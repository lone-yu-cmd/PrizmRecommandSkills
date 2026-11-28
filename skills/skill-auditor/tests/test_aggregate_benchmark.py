#!/usr/bin/env python3
"""Unit and CLI tests for skills/skill-auditor/scripts/aggregate_benchmark.py."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import aggregate_benchmark


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class TestAggregateBenchmark(unittest.TestCase):
    """Tests for stats calculation, discovery, loading, aggregation, markdown, and CLI."""

    def test_calculate_stats(self):
        self.assertEqual(
            aggregate_benchmark.calculate_stats([]),
            {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0},
        )
        self.assertEqual(
            aggregate_benchmark.calculate_stats([0.75]),
            {"mean": 0.75, "stddev": 0.0, "min": 0.75, "max": 0.75},
        )
        # Sample stddev uses (n - 1): values [1.0, 2.0, 3.0] -> mean=2.0, stddev=1.0
        stats = aggregate_benchmark.calculate_stats([1.0, 2.0, 3.0])
        self.assertEqual(stats, {"mean": 2.0, "stddev": 1.0, "min": 1.0, "max": 3.0})
        rounded = aggregate_benchmark.calculate_stats([0.12345, 0.23456])
        self.assertEqual(rounded["mean"], 0.179)
        self.assertEqual(rounded["min"], 0.1235)
        self.assertEqual(rounded["max"], 0.2346)

    def test_discover_eval_dirs_prefers_eval_prefix_or_graded_subdirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "eval-1" / "with_skill" / "grading.json", {})
            write_json(root / "custom-case" / "with_skill" / "grading.json", {})
            (root / "unrelated").mkdir()
            (root / "notes.txt").write_text("hi", encoding="utf-8")

            # eval-* wins when present
            self.assertEqual(aggregate_benchmark.discover_eval_dirs(root), [root / "eval-1"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "case-single" / "with_skill" / "grading.json", {})
            (root / "case-multi" / "without_skill" / "run-1").mkdir(parents=True)
            (root / "empty-dir" / "outputs").mkdir(parents=True)

            discovered = aggregate_benchmark.discover_eval_dirs(root)
            self.assertEqual(discovered, [root / "case-multi", root / "case-single"])

    def test_load_run_results_layouts_and_fallbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench = Path(tmp)
            # Legacy runs/ layout with timing.json fallback, output_chars fallback, and notes
            write_json(
                bench / "runs" / "eval-2" / "with_skill" / "run-1" / "grading.json",
                {
                    "summary": {"pass_rate": 1.0, "passed": 2, "failed": 0, "total": 2},
                    "execution_metrics": {"total_tool_calls": 4, "output_chars": 500, "errors_encountered": 0},
                    "expectations": [{"text": "works", "passed": True, "evidence": "ok"}],
                    "user_notes_summary": {
                        "uncertainties": ["u1"],
                        "needs_review": ["r1"],
                        "workarounds": ["w1"],
                    },
                },
            )
            write_json(
                bench / "runs" / "eval-2" / "with_skill" / "run-1" / "timing.json",
                {"total_duration_seconds": 4.5, "total_tokens": 1200},
            )
            # Invalid JSON file in run-2 should be skipped cleanly
            bad_run = bench / "runs" / "eval-2" / "with_skill" / "run-2"
            bad_run.mkdir(parents=True)
            (bad_run / "grading.json").write_text("{bad", encoding="utf-8")

            # Missing grading.json in without_skill/run-1 should be skipped cleanly
            (bench / "runs" / "eval-2" / "without_skill" / "run-1").mkdir(parents=True)

            # Non-config directory (inputs) should be ignored
            (bench / "runs" / "eval-2" / "inputs").mkdir()

            results = aggregate_benchmark.load_run_results(bench)
            self.assertEqual(list(results.keys()), ["with_skill", "without_skill"])
            self.assertEqual(len(results["with_skill"]), 1)
            self.assertEqual(results["without_skill"], [])
            entry = results["with_skill"][0]
            self.assertEqual(entry["eval_id"], 2)
            self.assertEqual(entry["run_number"], 1)
            self.assertEqual(entry["time_seconds"], 4.5)
            self.assertEqual(entry["tokens"], 1200)
            self.assertEqual(entry["tool_calls"], 4)
            self.assertEqual(entry["notes"], ["u1", "r1", "w1"])

    def test_load_run_results_single_run_descriptive_and_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty"
            empty.mkdir()
            self.assertEqual(aggregate_benchmark.load_run_results(empty), {})

            bench = Path(tmp) / "bench"
            write_json(bench / "case-alpha" / "eval_metadata.json", {"eval_id": 7})
            write_json(
                bench / "case-alpha" / "new_skill" / "grading.json",
                {
                    "summary": {"pass_rate": 0.5, "passed": 1, "failed": 1, "total": 2},
                    "timing": {"total_duration_seconds": 2.0},
                    "execution_metrics": {"output_chars": 321},
                    "expectations": [{"text": "exp", "passed": True, "evidence": "e"}],
                },
            )
            # Descriptive case dir without eval_metadata.json (hyphenated fallback to eval_idx=1)
            write_json(
                bench / "case-beta" / "new_skill" / "grading.json",
                {"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1}},
            )

            results = aggregate_benchmark.load_run_results(bench)
            self.assertEqual([r["eval_id"] for r in results["new_skill"]], [7, 1])
            self.assertEqual(results["new_skill"][0]["run_number"], 1)
            self.assertEqual(results["new_skill"][0]["tokens"], 321)

    def test_aggregate_results_two_configs_one_config_and_empty(self):
        self.assertEqual(
            aggregate_benchmark.aggregate_results({}),
            {"delta": {"pass_rate": "+0.00", "time_seconds": "+0.0", "tokens": "+0"}},
        )

        two = aggregate_benchmark.aggregate_results({
            "with_skill": [
                {"pass_rate": 1.0, "time_seconds": 2.5, "tokens": 300},
                {"pass_rate": 0.5, "time_seconds": 3.5, "tokens": 500},
            ],
            "without_skill": [
                {"pass_rate": 0.5, "time_seconds": 4.5, "tokens": 300},
            ],
        })
        self.assertEqual(two["with_skill"]["pass_rate"]["mean"], 0.75)
        self.assertEqual(two["delta"], {"pass_rate": "+0.25", "time_seconds": "-1.5", "tokens": "+100"})

        empty_cfg = aggregate_benchmark.aggregate_results({"with_skill": []})
        self.assertEqual(empty_cfg["with_skill"]["tokens"]["mean"], 0)
        self.assertEqual(empty_cfg["delta"]["pass_rate"], "+0.00")

    def test_generate_benchmark_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench_dir = Path(tmp)
            write_json(
                bench_dir / "eval-10" / "with_skill" / "run-1" / "grading.json",
                {
                    "summary": {"pass_rate": 1.0, "passed": 2, "failed": 0, "total": 2},
                    "timing": {"total_duration_seconds": 3.0},
                    "execution_metrics": {"output_chars": 200},
                    "expectations": [],
                },
            )
            write_json(
                bench_dir / "eval-10" / "without_skill" / "run-1" / "grading.json",
                {
                    "summary": {"pass_rate": 0.5, "passed": 1, "failed": 1, "total": 2},
                    "timing": {"total_duration_seconds": 5.0},
                    "execution_metrics": {"output_chars": 100},
                    "expectations": [],
                },
            )
            benchmark = aggregate_benchmark.generate_benchmark(
                bench_dir, skill_name="demo-skill", skill_path="skills/demo"
            )
            self.assertEqual(benchmark["metadata"]["skill_name"], "demo-skill")
            self.assertEqual(benchmark["metadata"]["skill_path"], "skills/demo")
            self.assertEqual(benchmark["metadata"]["evals_run"], [10])
            self.assertEqual(len(benchmark["runs"]), 2)
            self.assertEqual(benchmark["run_summary"]["delta"]["pass_rate"], "+0.50")

            benchmark["notes"] = ["Observed faster run with skill."]
            md = aggregate_benchmark.generate_markdown(benchmark)
            self.assertIn("# Skill Benchmark: demo-skill", md)
            self.assertIn("| Metric | With Skill | Without Skill | Delta |", md)
            self.assertIn("| Pass Rate | 100% ± 0% | 50% ± 0% | +0.50 |", md)
            self.assertIn("## Notes\n\n- Observed faster run with skill.", md)

    def test_cli_valid_and_missing_dir(self):
        script = SCRIPTS_DIR / "aggregate_benchmark.py"
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope"
            res_missing = subprocess.run(
                [sys.executable, str(script), str(missing)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_missing.returncode, 1)
            self.assertIn("Directory not found", res_missing.stdout)

            bench = Path(tmp) / "bench"
            write_json(
                bench / "eval-1" / "with_skill" / "run-1" / "grading.json",
                {"summary": {"pass_rate": 1.0, "passed": 1, "failed": 0, "total": 1}},
            )
            out_json = Path(tmp) / "out" / "custom.json"
            out_json.parent.mkdir(parents=True)
            res_ok = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    str(bench),
                    "--skill-name",
                    "cli-skill",
                    "-o",
                    str(out_json),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_ok.returncode, 0, res_ok.stderr)
            self.assertTrue(out_json.is_file())
            self.assertTrue(out_json.with_suffix(".md").is_file())
            parsed = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(parsed["metadata"]["skill_name"], "cli-skill")


if __name__ == "__main__":
    unittest.main(verbosity=2)
