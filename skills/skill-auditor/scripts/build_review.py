#!/usr/bin/env python3
"""Build one static review page from an iteration directory.

Reads the layout produced by the eval workflow:

    iteration-N/
    ├── case-name/
    │   ├── eval_metadata.json        (optional: prompt, eval_name, assertions)
    │   ├── with_skill/
    │   │   ├── outputs/              (files to show)
    │   │   ├── grading.json          (optional: expectations[], summary{})
    │   │   └── timing.json           (optional: total_tokens, duration_ms)
    │   └── without_skill/            (same shape, any config name works)

Writes a single self-contained HTML file: every case with its prompt, outputs,
grades, and a feedback box. The feedback box exports feedback.json, which the
next iteration reads.

Usage:
    python build_review.py <iteration-dir> [--skill-name NAME]
                           [--previous-iteration DIR] [-o OUT]

No network, no server, no dependencies beyond the standard library.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_INLINE_BYTES = 200_000
MAX_CHARS = 20_000
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".py", ".js", ".ts",
    ".html", ".css", ".sh", ".toml", ".ini", ".log", ".sql", ".xml", ".rs",
    ".go", ".java", ".rb", ".tsx", ".jsx",
}


# ---------------------------------------------------------------- loading


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_outputs(config_dir: Path) -> list[tuple[str, str, bool]]:
    """Return [(relative path, content, truncated)] for readable files."""
    out_dir = config_dir / "outputs"
    if not out_dir.is_dir():
        return []
    files = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(out_dir).as_posix()
        raw = path.read_bytes()
        if path.suffix.lower() not in TEXT_SUFFIXES or len(raw) > MAX_INLINE_BYTES:
            files.append((f"{rel}  ({len(raw)} bytes, not inlined)", "", False))
            continue
        if b"\x00" in raw[:4096]:
            files.append((f"{rel}  ({len(raw)} bytes, binary)", "", False))
            continue
        text = raw.decode("utf-8", errors="replace")
        truncated = len(text) > MAX_CHARS
        files.append((rel, text[:MAX_CHARS], truncated))
    return files


def load_run(config_dir: Path, name: str | None = None) -> dict:
    grading = read_json(config_dir / "grading.json")
    timing = read_json(config_dir / "timing.json")
    expectations = grading.get("expectations") or []
    passed = sum(1 for e in expectations if e.get("passed"))
    return {
        "name": name or config_dir.name,
        "outputs": load_outputs(config_dir),
        "expectations": expectations,
        "graded": bool(expectations),
        "passed": passed,
        "total": len(expectations),
        "pass_rate": grading.get("summary", {}).get("pass_rate"),
        "tokens": timing.get("total_tokens"),
        "duration_s": timing.get("total_duration_seconds"),
    }


def load_case(case_dir: Path) -> dict:
    meta = read_json(case_dir / "eval_metadata.json")
    runs = []
    for sub in sorted(p for p in case_dir.iterdir() if p.is_dir()):
        repeats = sorted(r for r in sub.glob("run-*") if r.is_dir())
        if repeats:
            # multi-run layout: with_skill/run-1, with_skill/run-2, ...
            for repeat in repeats:
                runs.append(load_run(repeat, name=f"{sub.name}/{repeat.name}"))
        elif (sub / "outputs").is_dir() or (sub / "grading.json").is_file():
            runs.append(load_run(sub))
    # with_skill first, then the baseline — the comparison reads in that order.
    runs.sort(key=lambda r: (not r["name"].startswith("with"), r["name"]))
    return {
        "id": case_dir.name,
        "name": meta.get("eval_name") or case_dir.name,
        "prompt": meta.get("prompt", ""),
        "assertions": meta.get("assertions") or [],
        "runs": runs,
    }


def load_iteration(root: Path) -> list[dict]:
    if root is None or not root.is_dir():
        return []
    cases = []
    for sub in sorted(p for p in root.iterdir() if p.is_dir()):
        case = load_case(sub)
        if case["runs"]:
            cases.append(case)
    return cases


# ---------------------------------------------------------------- rendering


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def render_grades(run: dict) -> str:
    if not run["graded"]:
        return '<p class="muted">No grading.json — not graded.</p>'
    rows = []
    for item in run["expectations"]:
        ok = item.get("passed")
        mark = "PASS" if ok else "FAIL"
        cls = "pass" if ok else "fail"
        rows.append(
            f'<li class="{cls}"><b>{mark}</b> {esc(item.get("text", ""))}'
            f'<div class="evidence">{esc(item.get("evidence", ""))}</div></li>'
        )
    return f'<ul class="grades">{"".join(rows)}</ul>'


def render_outputs(run: dict) -> str:
    if not run["outputs"]:
        return '<p class="muted">No output files.</p>'
    blocks = []
    for name, content, truncated in run["outputs"]:
        note = '<p class="muted">(truncated for display)</p>' if truncated else ""
        body = f"<pre>{esc(content)}</pre>" if content else ""
        blocks.append(f'<details open><summary>{esc(name)}</summary>{body}{note}</details>')
    return "".join(blocks)


def render_run(run: dict, previous: dict | None) -> str:
    stats = []
    if run["graded"]:
        stats.append(f'{run["passed"]}/{run["total"]} assertions')
    if run["pass_rate"] is not None:
        stats.append(f'pass rate {run["pass_rate"]:.2f}')
    if run["tokens"]:
        stats.append(f'{run["tokens"]:,} tokens')
    if run["duration_s"] is not None:
        stats.append(f'{run["duration_s"]:.1f}s')
    prev_html = ""
    if previous is not None and previous["outputs"]:
        prev_html = (
            '<details class="prev"><summary>Previous iteration output</summary>'
            f"{render_outputs(previous)}</details>"
        )
    return f"""
    <section class="run">
      <header>
        <h3>{esc(run["name"])}</h3>
        <span class="stats">{esc(" · ".join(stats) or "ungraded")}</span>
      </header>
      {render_grades(run)}
      <h4>Outputs</h4>
      {render_outputs(run)}
      {prev_html}
      <label>Feedback for {esc(run["name"])}
        <textarea data-run-id="{esc(run["id"])}" rows="3"
          placeholder="What is wrong with this output? Empty means it looked fine."></textarea>
      </label>
    </section>"""


def render_case(case: dict, prev_case: dict | None) -> str:
    prev_by_name = {r["name"]: r for r in (prev_case or {}).get("runs", [])}
    for run in case["runs"]:
        run["id"] = f'{case["id"]}/{run["name"]}'
    runs = "".join(render_run(run, prev_by_name.get(run["name"])) for run in case["runs"])
    assertions = ""
    if case["assertions"]:
        items = "".join(f"<li>{esc(a)}</li>" for a in case["assertions"])
        assertions = f'<details><summary>Assertions under test</summary><ul>{items}</ul></details>'
    return f"""
  <article class="case">
    <h2>{esc(case["name"])}</h2>
    <p class="prompt">{esc(case["prompt"]) or '<span class="muted">(no eval_metadata.json)</span>'}</p>
    {assertions}
    <div class="runs">{runs}</div>
  </article>"""


def render_page(cases: list[dict], previous: list[dict], skill_name: str, source: Path) -> str:
    prev_by_id = {c["id"]: c for c in previous}
    body = "".join(render_case(case, prev_by_id.get(case["id"])) for case in cases)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(skill_name)} — review</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font: 15px/1.55 -apple-system, "Segoe UI", system-ui, sans-serif;
         max-width: 1080px; margin: 0 auto; padding: 2rem 1.25rem 6rem; }}
  h1 {{ font-size: 1.5rem; margin-bottom: .25rem; }}
  h2 {{ font-size: 1.15rem; margin: 2.5rem 0 .5rem; }}
  h3 {{ font-size: 1rem; margin: 0; }}
  h4 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .04em;
        opacity: .6; margin: 1rem 0 .35rem; }}
  .meta {{ opacity: .6; font-size: .85rem; }}
  .case {{ border-top: 1px solid rgba(128,128,128,.35); padding-top: 1rem; }}
  .prompt {{ background: rgba(128,128,128,.12); padding: .7rem .9rem;
             border-radius: 6px; white-space: pre-wrap; }}
  .run {{ border: 1px solid rgba(128,128,128,.35); border-radius: 8px;
          padding: .9rem 1rem; margin: .9rem 0; }}
  .run header {{ display: flex; justify-content: space-between; align-items: baseline;
                 gap: 1rem; flex-wrap: wrap; }}
  .stats {{ font-size: .82rem; opacity: .7; }}
  pre {{ background: rgba(128,128,128,.12); padding: .7rem .9rem; border-radius: 6px;
         overflow-x: auto; font-size: .84rem; max-height: 26rem; }}
  details {{ margin: .35rem 0; }}
  summary {{ cursor: pointer; font-size: .88rem; }}
  ul.grades {{ list-style: none; padding: 0; margin: .4rem 0; font-size: .9rem; }}
  ul.grades li {{ padding: .15rem 0; }}
  .pass b {{ color: #1a7f37; }}
  .fail b {{ color: #b42318; }}
  .evidence {{ opacity: .65; font-size: .84rem; padding-left: 3.2rem; }}
  .muted {{ opacity: .6; font-size: .88rem; }}
  label {{ display: block; font-size: .85rem; margin-top: 1rem; }}
  textarea {{ width: 100%; font: inherit; font-size: .9rem; padding: .55rem;
              border-radius: 6px; border: 1px solid rgba(128,128,128,.5);
              background: transparent; color: inherit; resize: vertical; }}
  .bar {{ position: fixed; inset: auto 0 0 0; display: flex; gap: .75rem;
          justify-content: flex-end; align-items: center; padding: .8rem 1.5rem;
          border-top: 1px solid rgba(128,128,128,.35); background: Canvas; }}
  button {{ font: inherit; padding: .45rem 1rem; border-radius: 6px;
            border: 1px solid rgba(128,128,128,.6); background: transparent;
            color: inherit; cursor: pointer; }}
  button.primary {{ background: #1a7f37; border-color: #1a7f37; color: #fff; }}
</style>
</head>
<body>
<h1>{esc(skill_name)} — review</h1>
<p class="meta">{len(cases)} case(s) · source: {esc(source)} · generated {generated}</p>
{body}
<div class="bar">
  <span class="muted" id="count">0 notes</span>
  <button id="export" class="primary">Export feedback.json</button>
</div>
<script>
const boxes = [...document.querySelectorAll('textarea[data-run-id]')];
const count = document.getElementById('count');
function refresh() {{
  const n = boxes.filter(b => b.value.trim()).length;
  count.textContent = n + (n === 1 ? ' note' : ' notes');
}}
boxes.forEach(b => b.addEventListener('input', refresh));
document.getElementById('export').addEventListener('click', () => {{
  const reviews = boxes
    .filter(b => b.value.trim())
    .map(b => ({{
      run_id: b.dataset.runId,
      feedback: b.value.trim(),
      timestamp: new Date().toISOString()
    }}));
  const payload = {{ reviews, status: 'complete' }};
  const blob = new Blob([JSON.stringify(payload, null, 2)], {{ type: 'application/json' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'feedback.json';
  a.click();
  URL.revokeObjectURL(a.href);
}});
refresh();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- main


def main() -> int:
    parser = argparse.ArgumentParser(description="Iteration directory → static review page")
    parser.add_argument("iteration", type=Path, help="Directory holding one iteration's eval cases")
    parser.add_argument("--skill-name", default=None, help="Name shown in the page title")
    parser.add_argument("--previous-iteration", type=Path, default=None,
                        help="Earlier iteration to show as 'previous output'")
    parser.add_argument("--output", "-o", type=Path, default=None,
                        help="Output HTML path (default: <iteration>/review.html)")
    args = parser.parse_args()

    if not args.iteration.is_dir():
        print(f"error: {args.iteration} is not a directory", file=sys.stderr)
        return 2

    cases = load_iteration(args.iteration)
    if not cases:
        print(f"error: no eval cases found under {args.iteration}", file=sys.stderr)
        return 2

    previous = load_iteration(args.previous_iteration) if args.previous_iteration else []
    if args.previous_iteration and not previous:
        print(f"warning: {args.previous_iteration} had no readable cases", file=sys.stderr)

    skill_name = args.skill_name or args.iteration.resolve().parent.name
    output = args.output or (args.iteration / "review.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_page(cases, previous, skill_name, args.iteration), encoding="utf-8")

    print(f"wrote {output}  ({len(cases)} cases, {sum(len(c['runs']) for c in cases)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
