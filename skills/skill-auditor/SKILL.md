---
name: "skill-auditor"
description: "Evaluate skill effectiveness through test runs, grading, benchmarking, and A/B comparison. Use this skill whenever someone wants to test a skill against real prompts, measure skill quality with quantitative metrics, compare two skill versions, benchmark skill performance, optimize a skill's description for better triggering, or run evals. Triggers on: 'test this skill', 'run evals', 'benchmark skill', 'compare skill versions', 'skill triggering', 'does this skill work', 'eval skill'."
---

# Skill Auditor

Evaluate whether a skill actually works by running it against real prompts, grading outputs, benchmarking performance, and comparing versions. This skill provides the runtime evaluation loop that complements skill-optimizer's static analysis.

The evaluation methodology comes from skill-creator's testing framework — this skill extracts and focuses the evaluation workflow into a standalone tool.

### When to Use
- "Test this skill", "run evals", "benchmark this skill"
- "Compare the old version with the new one"
- "Does this skill actually work?"
- "Optimize the skill's description for better triggering"
- After creating or modifying a skill, to verify it works
- Before publishing a skill, to measure quality

### `/skill-auditor` \<path-to-skill\> [mode]

Accepts a skill directory path or a direct path to a SKILL.md file.

**Modes:**
- `--eval` (default): Full evaluation loop — write test cases, run them, grade, benchmark, collect feedback
- `--compare`: Blind A/B comparison between two skill versions
- `--trigger`: Optimize the skill's description for better triggering accuracy
- `--grade-only`: Grade existing run outputs without re-running

---

## Phase 1: Test Case Design

### Step 1: Understand the skill

Read the target skill's SKILL.md and all bundled resources (references/, scripts/, assets/). Understand what the skill does, when it triggers, and what good output looks like.

### Step 2: Write test prompts

Create 2-3 realistic test prompts — the kind of thing a real user would actually say. Good test prompts are:

- **Concrete and detailed** — include file paths, personal context, specific data. Not "format this data" but "my boss sent me Q4_sales_final.xlsx and wants profit margins added to column E"
- **Diverse** — cover different use cases, phrasings (formal/casual), and edge cases
- **Substantive** — complex enough that Claude would benefit from consulting the skill, because simple one-step queries may not trigger skills regardless of quality

Share them with the user for review before running.

### Step 3: Save test cases

Save to `evals/evals.json` in the skill directory. Start with prompts only — assertions come later (Step 2 of Phase 2).

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/eval-schemas.md` for the full schema.

---

## Phase 2: Run and Evaluate

This is one continuous sequence — don't stop partway through.

### Workspace layout

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Organize by iteration (`iteration-1/`, `iteration-2/`) and within that, each test case gets a descriptive directory name.

### Step 1: Spawn all runs in parallel

For each test case, spawn **two** subagents in the same turn — one with the skill, one without. Launch everything at once so results arrive together.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about>
```

**Baseline run** (depends on context):
- **New skill**: Same prompt, no skill, save to `without_skill/outputs/`
- **Improving existing skill**: Snapshot the old version first (`cp -r`), run baseline against the snapshot, save to `old_skill/outputs/`

Write an `eval_metadata.json` for each test case with a descriptive name.

### Step 2: Draft assertions while runs are in progress

Don't wait — use this time to draft quantitative assertions and explain them to the user.

Good assertions:
- Are **objectively verifiable** (not "output looks nice")
- Have **descriptive names** that read clearly in the benchmark viewer
- Are **discriminating** — they pass when the skill succeeds and fail when it doesn't

Don't force assertions onto subjective outputs (writing style, design quality) — those are better evaluated qualitatively through the viewer.

Update `eval_metadata.json` and `evals/evals.json` with the drafted assertions.

### Step 3: Capture timing data

When each subagent completes, the notification contains `total_tokens` and `duration_ms`. Save immediately to `timing.json` — this data is not persisted elsewhere and cannot be recovered later.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade outputs

Read `agents/grader.md` from this skill's directory for the full grading protocol.

The grader evaluates each assertion against the actual outputs, producing `grading.json` with `text`, `passed`, and `evidence` fields (the viewer depends on these exact names).

For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and reusable across iterations.

### Step 5: Aggregate into benchmark

Run the aggregation script from the skill-creator directory:
```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens per configuration, including mean +/- stddev and the delta. See `references/eval-schemas.md` for the exact schema the viewer expects.

### Step 6: Analyst pass

Read the benchmark data and surface patterns the aggregate stats might hide. Read `agents/analyzer.md` for what to look for:
- Assertions that always pass regardless of skill (non-discriminating)
- High-variance evals (possibly flaky)
- Time/token tradeoffs
- Surprising results that contradict expectations

### Step 7: Launch the viewer

```bash
nohup python <skill-creator-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```

For iteration 2+, add `--previous-workspace <workspace>/iteration-<N-1>`.

**Headless/Cowork:** Use `--static <output_path>` for a standalone HTML file.

Tell the user: "I've opened the results in your browser. The 'Outputs' tab lets you review each test case and leave feedback. The 'Benchmark' tab shows quantitative comparison. Come back when you're done."

### Step 8: Collect feedback

When the user finishes, read `feedback.json`. Empty feedback means the user was satisfied. Focus improvements on test cases with specific complaints.

```bash
kill $VIEWER_PID 2>/dev/null
```

---

## Phase 3: Iterate

After collecting feedback, improve the skill and run again:

1. Apply improvements to the skill
2. Rerun all test cases into `iteration-<N+1>/`, including baseline runs
3. Launch the viewer with `--previous-workspace` pointing at the previous iteration
4. Wait for user review
5. Read feedback, improve, repeat

Keep going until:
- The user is happy
- All feedback is empty
- No meaningful progress is being made

---

## Mode: Blind Comparison (`--compare`)

For rigorous A/B comparison between two skill versions. Requires subagents.

### Step 1: Run both versions

For each test case, spawn two subagents — one with each skill version. Label outputs A and B without revealing which version produced which.

### Step 2: Blind evaluation

Spawn a comparator subagent (read `agents/comparator.md`) that judges output quality without knowing which skill produced which output. The comparator scores on content (correctness, completeness, accuracy) and structure (organization, formatting, usability).

### Step 3: Post-hoc analysis

After the blind comparison determines a winner, spawn an analyzer subagent (read `agents/analyzer.md`) that "unblinds" the results. It examines both skills and transcripts to understand:
- What made the winner better
- What instruction differences led to the outcome
- Actionable suggestions for improving the loser

### Step 4: Report

Present the comparison results: winner, scores, key differences, and improvement suggestions.

---

## Mode: Description Optimization (`--trigger`)

Optimize the skill's `description` field for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger (8-10) and should-not-trigger (8-10).

**Should-trigger queries**: Different phrasings of the same intent — formal, casual, implicit. Include cases where users don't name the skill but clearly need it.

**Should-not-trigger queries**: Near-misses that share keywords but need something different. These are the most valuable — naive keyword matching would trigger but shouldn't.

All queries must be realistic — concrete, detailed, with personal context. Not "format this data" but a real-sounding request with file names, column references, backstory.

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

### Step 2: Review with user

Present the eval set using the HTML template from skill-creator (`assets/eval_review.html`). The user can edit queries, toggle should-trigger, and export the final set.

### Step 3: Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

This automatically splits into 60% train / 40% test, evaluates the current description (3 runs per query for reliability), proposes improvements, and iterates up to 5 times. The best description is selected by test score to avoid overfitting.

### Step 4: Apply result

Take `best_description` from the output and update the skill's frontmatter. Show before/after with scores.

---

## Mode: Grade Only (`--grade-only`)

Grade existing outputs without re-running. Useful when outputs already exist from a previous run or manual testing.

Provide the workspace path. The grader reads transcripts and outputs from each run directory, evaluates against assertions in `eval_metadata.json`, and produces `grading.json`.

---

## Environment Adaptations

**Claude.ai** (no subagents):
- Run test cases sequentially, one at a time — read the skill, then follow its instructions yourself
- Skip baseline runs
- Present results inline instead of using the browser viewer
- Skip blind comparison and description optimization (requires `claude -p`)

**Cowork** (no browser):
- Use `--static <path>` for the viewer to generate standalone HTML
- Feedback downloads as `feedback.json` via the "Submit All Reviews" button

---

## Resource Reference

- `agents/grader.md` — How to evaluate assertions against outputs
- `agents/comparator.md` — How to do blind A/B comparison
- `agents/analyzer.md` — How to analyze benchmark results and why one version beat another
- `references/eval-schemas.md` — JSON schemas for evals.json, grading.json, benchmark.json, timing.json
