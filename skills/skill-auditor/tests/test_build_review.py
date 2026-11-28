#!/usr/bin/env python3
"""Unit and CLI tests for skills/skill-auditor/scripts/build_review.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import build_review


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestLoaders(unittest.TestCase):
    """Tests for read_json, load_outputs, load_run, load_case, and load_iteration."""

    def test_read_json_handles_valid_missing_and_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = root / "valid.json"
            valid.write_text('{"a": 1}', encoding="utf-8")
            bad = root / "bad.json"
            bad.write_text("{not json", encoding="utf-8")

            self.assertEqual(build_review.read_json(valid), {"a": 1})
            self.assertEqual(build_review.read_json(root / "missing.json"), {})
            self.assertEqual(build_review.read_json(bad), {})

    def test_load_outputs_filters_binary_oversize_and_truncates(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "with_skill"
            cfg.mkdir()
            self.assertEqual(build_review.load_outputs(cfg), [])

            out = cfg / "outputs"
            (out / "sub").mkdir(parents=True)
            (out / "a_ok.md").write_text("# Title\nBody", encoding="utf-8")
            (out / "b_img.png").write_bytes(b"\x89PNG\r\n")
            (out / "c_huge.txt").write_bytes(b"x" * (build_review.MAX_INLINE_BYTES + 1))
            (out / "d_bin.json").write_bytes(b'{"a":\x00}')
            (out / "sub" / "e_long.txt").write_text("z" * (build_review.MAX_CHARS + 50), encoding="utf-8")

            loaded = build_review.load_outputs(cfg)
            self.assertEqual(len(loaded), 5)
            self.assertEqual(loaded[0], ("a_ok.md", "# Title\nBody", False))
            self.assertIn("not inlined", loaded[1][0])
            self.assertEqual(loaded[1][1:], ("", False))
            self.assertIn("not inlined", loaded[2][0])
            self.assertIn("binary", loaded[3][0])
            self.assertEqual(loaded[4][0], "sub/e_long.txt")
            self.assertEqual(len(loaded[4][1]), build_review.MAX_CHARS)
            self.assertTrue(loaded[4][2])

    def test_load_run_and_load_case_and_load_iteration(self):
        with tempfile.TemporaryDirectory() as tmp:
            iter_dir = Path(tmp) / "iteration-1"
            case1 = iter_dir / "case-1"
            write_json(
                case1 / "eval_metadata.json",
                {"eval_name": "Case One", "prompt": "Do X", "assertions": ["has Y"]},
            )
            (case1 / "without_skill" / "outputs").mkdir(parents=True)
            (case1 / "without_skill" / "outputs" / "note.txt").write_text("base", encoding="utf-8")
            write_json(
                case1 / "with_skill" / "run-1" / "grading.json",
                {
                    "expectations": [
                        {"text": "has Y", "passed": True, "evidence": "found"},
                        {"text": "no Z", "passed": False, "evidence": "missing"},
                    ],
                    "summary": {"pass_rate": 0.5},
                },
            )
            write_json(
                case1 / "with_skill" / "run-1" / "timing.json",
                {"total_tokens": 1500, "total_duration_seconds": 3.2},
            )
            (case1 / "with_skill" / "run-1" / "outputs").mkdir(parents=True)
            (case1 / "with_skill" / "run-1" / "outputs" / "res.md").write_text("ok", encoding="utf-8")
            (case1 / "ignored_dir").mkdir()

            # Empty case dir with no runs should be skipped by load_iteration
            (iter_dir / "case-empty").mkdir()

            cases = build_review.load_iteration(iter_dir)
            self.assertEqual(len(cases), 1)
            case = cases[0]
            self.assertEqual(case["name"], "Case One")
            self.assertEqual(case["prompt"], "Do X")
            self.assertEqual(case["assertions"], ["has Y"])
            # with_skill sorted before without_skill
            self.assertEqual([r["name"] for r in case["runs"]], ["with_skill/run-1", "without_skill"])
            r0 = case["runs"][0]
            self.assertTrue(r0["graded"])
            self.assertEqual((r0["passed"], r0["total"], r0["pass_rate"]), (1, 2, 0.5))
            self.assertEqual((r0["tokens"], r0["duration_s"]), (1500, 3.2))
            self.assertFalse(case["runs"][1]["graded"])

            self.assertEqual(build_review.load_iteration(None), [])
            self.assertEqual(build_review.load_iteration(Path(tmp) / "missing"), [])


class TestRenderingAndCLI(unittest.TestCase):
    """Tests for HTML rendering helpers and CLI entry points."""

    def test_esc(self):
        self.assertEqual(build_review.esc('<script>"&"'), "&lt;script&gt;&quot;&amp;&quot;")
        self.assertEqual(build_review.esc(None), "")
        self.assertEqual(build_review.esc(123), "123")

    def test_render_helpers_and_page(self):
        run = {
            "id": "case-1/with_skill",
            "name": "with_skill",
            "graded": True,
            "passed": 1,
            "total": 2,
            "pass_rate": 0.5,
            "tokens": 1200,
            "duration_s": 2.5,
            "expectations": [
                {"text": "pass check", "passed": True, "evidence": "ev1"},
                {"text": "fail <tag>", "passed": False, "evidence": "ev2"},
            ],
            "outputs": [("out.txt", "hello <world>", True), ("img.png (5 bytes, not inlined)", "", False)],
        }
        prev_run = {
            "name": "with_skill",
            "outputs": [("old.txt", "previous text", False)],
        }
        grades_html = build_review.render_grades(run)
        self.assertIn('<li class="pass"><b>PASS</b> pass check', grades_html)
        self.assertIn('<li class="fail"><b>FAIL</b> fail &lt;tag&gt;', grades_html)
        self.assertIn("No grading.json", build_review.render_grades({"graded": False}))

        outputs_html = build_review.render_outputs(run)
        self.assertIn("hello &lt;world&gt;", outputs_html)
        self.assertIn("(truncated for display)", outputs_html)
        self.assertIn("No output files.", build_review.render_outputs({"outputs": []}))

        run_html = build_review.render_run(run, prev_run)
        self.assertIn("1/2 assertions · pass rate 0.50 · 1,200 tokens · 2.5s", run_html)
        self.assertIn("Previous iteration output", run_html)
        self.assertIn('data-run-id="case-1/with_skill"', run_html)

        cases = [
            {
                "id": "case-1",
                "name": "Demo Case",
                "prompt": "Prompt <text>",
                "assertions": ["assert 1"],
                "runs": [run],
            }
        ]
        previous = [{"id": "case-1", "runs": [prev_run]}]
        page = build_review.render_page(cases, previous, "my<skill>", Path("/tmp/iter-2"))
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>my&lt;skill&gt; — review</title>", page)
        self.assertIn("1 case(s) · source: /tmp/iter-2", page)
        self.assertIn("Assertions under test", page)
        self.assertIn("Export feedback.json", page)

    def test_cli_errors_and_success(self):
        script = SCRIPTS_DIR / "build_review.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Nonexistent iteration directory -> exit 2
            res_missing = subprocess.run(
                [sys.executable, str(script), str(root / "missing")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_missing.returncode, 2)

            # Empty directory with no cases -> exit 2
            empty = root / "empty"
            empty.mkdir()
            res_empty = subprocess.run(
                [sys.executable, str(script), str(empty)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_empty.returncode, 2)

            # Valid iteration + empty previous iteration warning
            iter_dir = root / "my-skill" / "iteration-2"
            (iter_dir / "case-1" / "with_skill" / "outputs").mkdir(parents=True)
            (iter_dir / "case-1" / "with_skill" / "outputs" / "a.md").write_text("hi", encoding="utf-8")
            prev_empty = root / "prev-empty"
            prev_empty.mkdir()
            out_html = root / "out" / "review.html"

            res_ok = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(iter_dir),
                    "--skill-name",
                    "custom-skill",
                    "--previous-iteration",
                    str(prev_empty),
                    "-o",
                    str(out_html),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stderr)
            self.assertIn("warning:", res_ok.stderr)
            self.assertIn("(1 cases, 1 runs)", res_ok.stdout)
            self.assertTrue(out_html.is_file())
            self.assertIn("custom-skill — review", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
