---
name: "skill-auditor"
description: "Measure whether a skill actually works: write realistic test prompts, run them with and without the skill, grade the outputs, benchmark pass rate, time and tokens, and compare versions. Use this skill whenever someone wants to test a skill, run evals, benchmark performance, check whether a skill triggers when it should, compare an old and new version, or find out if an edit made a skill better or worse. Triggers on: 'test this skill', 'run evals', 'eval skill', 'benchmark skill', 'compare skill versions', 'does this skill work', 'skill triggering', 'measure skill quality'. Runs the skill and measures outcomes; it does not audit text and does not edit the skill."
---

# Skill Auditor

Answer one question with evidence: does this skill work better than not having it?

Everything here is behavioral. A skill can be beautifully written and still produce worse output than a bare model; the only way to know is to run both and compare. That makes the baseline non-negotiable — a run with no baseline measures how hard the task is, not how good the skill is.

### When to use

- After writing or changing a skill, to see whether the change helped
- "Does this skill actually work?" / "Is it worth shipping?"
- "Which of these two versions is better?"
- "The skill never fires when I want it to" (trigger measurement)
- Before publishing, to have numbers instead of impressions

### Invocation

The user names a skill path and says what they want. Modes in plain words:

- default — design tests, run with and without, grade, benchmark, review, iterate
- "compare these two versions" — blind A/B comparison
- "just measure triggering" — description trigger measurement
- "grade what we already ran" — grade existing outputs, no new runs

The two bundled scripts are referenced from this skill's own `scripts/` directory. Resolve them relative to this skill, not to the user's project — a run from the wrong cwd is the most common way this workflow breaks.

---

## Phase 1 — Design the tests

Read the target's SKILL.md and every bundled file. You need to know what good output looks like before writing a prompt that produces it.

Write 2-3 prompts a real user would type. Concrete beats abstract: file paths, column names, backstory, the messy phrasing people actually use. "Add profit margin to column E of the Q4 xlsx my boss sent" tests something; "process data" tests nothing.

Two constraints that decide whether the results mean anything:

- **Substantive.** A one-step request may not trigger any skill, so it measures nothing about this one. Complex, multi-step, specialized requests are what actually load a skill.
- **Diverse.** Different phrasings of the same intent, one edge case, one case where the user never names the skill. Three variations of the same prompt produce one data point three times.

Show the prompts to the user before running. Bad prompts cost a full iteration to discover.

Save to `evals/evals.json` in the skill directory — prompts and expected output first, assertions come in Phase 2 while the runs are in flight.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "What a good result looks like",
      "files": []
    }
  ]
}
```

Full schema: `references/eval-schemas.md`.

---

## Phase 2 — Run, grade, benchmark

One continuous sequence. Stopping halfway leaves a folder of transcripts and no answer.

### Workspace

`<skill-name>-workspace/iteration-<N>/`, as a sibling of the skill directory. Each test case gets its own directory with a descriptive name, not `eval-0`:

```text
skill-name-workspace/iteration-1/
├── error-recovery-flow/
│   ├── with_skill/outputs/
│   └── without_skill/outputs/
└── multi-file-refactor/
    ├── with_skill/outputs/
    └── without_skill/outputs/
```

### Step 1 — Launch every run in one turn

For each test case, two subagents at once — with the skill, and the baseline. Launching them together keeps the environment comparable and finishes them together; running the skill cases first and baselines an hour later produces a comparison of two different machines.

```text
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files, or "none">
- Save outputs to: <workspace>/iteration-<N>/<case>/with_skill/outputs/
- Outputs to save: <what the user cares about — the file, the table, the report>
```

The baseline depends on what is being tested:

- **New skill** — no skill at all, saved to `without_skill/outputs/`. This answers "is the skill better than nothing".
- **Improvement to an existing skill** — snapshot the pre-change version with `cp -r` before editing anything, run the baseline from the snapshot, save to `old_skill/outputs/`. This answers "did the edit help", which is usually the real question.

Write `eval_metadata.json` per case, assertions empty for now:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name",
  "prompt": "The task prompt",
  "assertions": []
}
```

### Step 2 — Write assertions while the runs execute

Idle time is free, and assertions written before seeing the outputs are harder to fudge toward whatever the skill happened to produce.

Good assertions are objectively checkable, named so a stranger understands them at a glance in the report ("chart has axis labels", not "output is good"), and **discriminating** — they fail when the skill is absent and pass when it works. An assertion that passes in both configurations carried no information and should be dropped, which is worth noticing here rather than after the benchmark.

Subjective quality — tone, design taste, whether the prose lands — is not assertion material. Grade it by reading the outputs.

Write the assertions into `eval_metadata.json` and `evals/evals.json`, and tell the user what they will see.

### Step 3 — Capture timing as each run lands

The completion notification carries `total_tokens` and `duration_ms`, and nothing else records them. Write `timing.json` immediately, per run; batching at the end loses the data.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4 — Grade

Read `agents/grader.md`, then grade each run, writing `grading.json` beside its outputs. The `expectations` array must use the field names `text`, `passed`, `evidence` — the aggregation script and the review page both read those exact keys.

For anything checkable mechanically, write a script and run it instead of reading the output and judging. A script is faster, reproducible, and reusable next iteration; eyeballing 30 assertions is where grading quietly becomes unreliable.

### Step 5 — Aggregate

```bash
python <this-skill>/scripts/aggregate_benchmark.py <workspace>/iteration-<N> --skill-name <name>
```

Produces `benchmark.json` and `benchmark.md`: pass rate, time, and tokens per configuration, mean ± stddev, and the delta with_skill vs baseline. If you build the JSON by hand, follow `references/eval-schemas.md` — the review page depends on those field names. List every with-skill case before its baseline counterpart so the comparison reads straight.

### Step 6 — Analyst pass

Read the numbers as a skeptic before showing them:

- Assertions that pass in every configuration — non-discriminating, they inflate the pass rate without measuring anything
- Cases whose results swing wildly across runs — flaky, not a skill effect
- A pass-rate gain bought with a large token or time increase — a real trade-off, not a free win
- Any result that contradicts what the transcripts look like

`agents/analyzer.md` has the detail. Fold the observations into what you report; a bare table invites the user to over-read it.

### Step 7 — Build the review page

```bash
python <this-skill>/scripts/build_review.py <workspace>/iteration-<N> \
  --skill-name <name> \
  --previous-iteration <workspace>/iteration-<N-1> \
  -o <workspace>/iteration-<N>/review.html
```

A single static HTML file: every case with its prompt, outputs, grading, and a feedback box. No server, no network, opens anywhere. The feedback box exports `feedback.json` when the user is done; save it into the iteration directory.

Get this in front of the human before you start revising on your own judgement. The person who knows the task will spot the wrong-shaped output in ten seconds, and every round you rewrite without their read is a round spent guessing.

### Step 8 — Read the feedback

```json
{
  "reviews": [
    {"run_id": "error-recovery-flow/with_skill", "feedback": "the table is missing a header row", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means that case looked fine. Weight the specific complaints — a complaint names something the metrics could not see, which is exactly why the human pass exists.

---

## Phase 3 — Iterate

1. Apply the changes the feedback points at
2. Rerun everything into `iteration-<N+1>/`, baselines included
3. Build the review page with `--previous-iteration` so the user can compare
4. Wait for review, read feedback, repeat

Stop when the user is satisfied, when feedback comes back empty, or when two rounds move nothing. A loop that keeps producing edits with no measurable gain is overfitting to the visible cases — check whether the next change would hold on a prompt you have not written yet.

---

## Mode — Blind comparison

To compare two versions properly, hide the labels:

1. Run both versions on the same cases, into `A/` and `B/` directories, without recording which is which anywhere the comparator can read.
2. Spawn a comparator subagent (`agents/comparator.md`) that scores content and structure on output quality alone.
3. Once it commits to a winner, spawn an analyzer (`agents/analyzer.md`) to unblind and explain why: which instruction differences produced the difference in output.
4. Report the winner, the scores, the reasoning, and the concrete edits suggested for the loser.

Blinding matters most when the two versions are your own work, which is the usual case.

---

## Mode — Trigger measurement

Answers "would this skill fire on the requests I care about". Uses judgement instead of an API loop, so it needs no CLI beyond the agent itself.

1. **Write 20 queries.** 8-10 should trigger, 8-10 should not. Realistic, with paths, columns, company names, casual phrasing, typos — the way people actually type.
2. **Make the negatives near-misses.** "Write a fibonacci function" against a PDF skill tests nothing; a request that shares the keywords but needs a different tool tests everything. A negative set of obviously irrelevant queries produces a meaningless 100%.
3. **Split 60/40** into train and held-out test. Choose the best description by test score, not train — picking by train score is how a description gets tuned to the examples and fires on nothing in production.
4. **Evaluate each query 3 times**, deciding from the description alone: given this request and this list of available skills, would you consult this one? Reading the skill body while judging gives a false positive, because the real router only sees the description.
5. **Propose one improved description**, using the failures: missing scenario, missing keyword users would type, or too broad and stealing a near-miss.
6. **Report the rates** — train and test, before and after — and the proposed description. Applying it changes what the skill fires on, so it needs explicit confirmation.

`references/eval-schemas.md` has the query file shape.

---

## Mode — Grade only

When outputs already exist from a previous run or manual testing: point at the workspace, grade against the assertions in each `eval_metadata.json`, write `grading.json`, aggregate, build the page. Same grading rules as Phase 2 Step 4 — script over eyeball wherever possible.

---

## Environment adaptations

Work with what is available rather than stopping:

- **No subagents** — run the cases yourself, one at a time, following the skill's own instructions. Less rigorous, since the author running their own skill has every bit of context, but it still catches the cases where the skill wastes half the run. Skip baselines; without independence they compare nothing.
- **No browser** — `build_review.py` already writes a static file. Show the path, or paste the per-case summary into the conversation.
- **No eval history** — start at iteration-1 with a baseline, and treat the first run as the reference point everything later is measured against.

---

## Failure modes

- Running without a baseline, then reporting a pass rate that measures task difficulty
- Assertions that pass either way, reported as coverage
- Grading by reading instead of by script, then trusting the number
- Prompts so simple the skill never loads, so the eval measures the bare model
- Choosing a description by train score
- Rewriting the skill from your own reading of the outputs before the human has looked
- Reporting a benchmark table with no note that two of the four assertions were non-discriminating

---

## Resources

- `scripts/aggregate_benchmark.py` — grading.json → benchmark.json/md with mean, stddev, delta
- `scripts/build_review.py` — iteration directory → one static review page with feedback export
- `agents/grader.md` — evaluate assertions against outputs, and criticize weak assertions
- `agents/comparator.md` — blind A/B scoring
- `agents/analyzer.md` — why the winner won, and what to change in the loser
- `references/eval-schemas.md` — JSON shapes for evals, grading, benchmark, timing, trigger queries
