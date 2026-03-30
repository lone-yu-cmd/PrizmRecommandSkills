# Evaluation Schemas Reference

JSON schemas used by skill-auditor. Load this file when you need to create or validate evaluation data structures.

## Table of Contents
1. [evals.json](#evalsjson)
2. [eval_metadata.json](#eval_metadatajson)
3. [timing.json](#timingjson)
4. [grading.json](#gradingjson)
5. [benchmark.json](#benchmarkjson)
6. [comparison.json](#comparisonjson)
7. [analysis.json](#analysisjson)
8. [feedback.json](#feedbackjson)

---

## evals.json

Defines test cases for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter
- `evals[].id`: Unique integer identifier
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable assertion statements

---

## eval_metadata.json

Per-test-case metadata. Located at `<workspace>/iteration-<N>/eval-<ID>/eval_metadata.json`.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": [
    "Output is a valid PDF",
    "All form fields are populated"
  ]
}
```

Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too.

---

## timing.json

Wall clock timing for a run. Located at `<run-dir>/timing.json`.

**How to capture:** When a subagent task completes, the notification includes `total_tokens` and `duration_ms`. Save immediately — this data is not persisted elsewhere.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## grading.json

Output from the grader agent. Located at `<run-dir>/grading.json`.

**Critical:** The `expectations` array must use the fields `text`, `passed`, and `evidence` — the viewer depends on these exact field names. Do not use `name`/`met`/`details` or other variants.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": { "Read": 5, "Write": 2, "Bash": 8 },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**Fields:**
- `expectations[]`: Graded assertions with evidence
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size (from executor's metrics.json)
- `timing`: Wall clock timing (from timing.json)
- `claims`: Extracted and verified claims from the output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: Optional improvement suggestions for the evals themselves

---

## benchmark.json

Aggregated benchmark results. Located at `<workspace>/iteration-<N>/benchmark.json`.

**Important:** The viewer reads these field names exactly. Using `config` instead of `configuration`, or putting `pass_rate` at the top level instead of nested under `result`, will cause the viewer to show empty/zero values.

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05},
      "time_seconds": {"mean": 45.0, "stddev": 12.0},
      "tokens": {"mean": 3800, "stddev": 400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08},
      "time_seconds": {"mean": 32.0, "stddev": 8.0},
      "tokens": {"mean": 2100, "stddev": 300}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": [
    "Assertion 'Output is a PDF' passes 100% in both configurations - non-discriminating",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**Fields:**
- `metadata`: Benchmark run context
- `runs[]`: Individual run results — `configuration` must be `"with_skill"` or `"without_skill"` (viewer uses this for grouping). Put each with_skill version before its baseline counterpart.
- `run_summary`: Statistical aggregates with `mean` and `stddev` per configuration
- `notes`: Freeform analyst observations

---

## comparison.json

Output from blind comparator. Located at `<grading-dir>/comparison.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A provides complete solution with proper formatting. Output B is missing the date field.",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5, "accuracy": 4},
      "structure": {"organization": 4, "formatting": 5, "usability": 4},
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2, "accuracy": 3},
      "structure": {"organization": 3, "formatting": 2, "usability": 3},
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {"score": 9, "strengths": ["..."], "weaknesses": ["..."]},
    "B": {"score": 5, "strengths": ["..."], "weaknesses": ["..."]}
  }
}
```

---

## analysis.json

Output from post-hoc analyzer. Located at `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary"
  },
  "winner_strengths": ["Clear step-by-step instructions", "Validation script"],
  "loser_weaknesses": ["Vague instructions", "No validation"],
  "instruction_following": {
    "winner": {"score": 9, "issues": ["Minor: skipped optional step"]},
    "loser": {"score": 6, "issues": ["Did not use formatting template"]}
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace vague instruction with explicit steps",
      "expected_impact": "Would eliminate ambiguity"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5 steps -> Validated -> Output",
    "loser_execution_pattern": "Read skill -> Unclear -> Tried 3 methods -> Errors"
  }
}
```

**Suggestion categories:** `instructions`, `tools`, `examples`, `error_handling`, `structure`, `references`

**Priority levels:** `high` (would change the outcome), `medium` (quality improvement), `low` (marginal)

---

## feedback.json

User feedback from the viewer. Located at `<workspace>/iteration-<N>/feedback.json`.

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user was satisfied with that test case.
