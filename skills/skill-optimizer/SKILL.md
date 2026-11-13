---
name: "skill-optimizer"
description: "Restructure and rewrite a skill that has grown too long, repetitive, or hard to follow: split content across SKILL.md and references/, convert MUST-style directives into instructions with rationale, rewrite the description for reliable triggering, fix reference and script health, and verify nothing was lost. Use this skill whenever someone wants to optimize, refactor, restructure, tighten, split, trim, clean up, modernize, or shorten a skill, or says a skill is bloated, messy, too long, or badly organized. Triggers on: 'optimize skill', 'refactor skill', 'restructure this skill', 'skill too long', 'trim this skill', 'split this skill', 'clean up this skill', 'modernize this skill'. It changes content that already exists; it does not add new capability, and it does not run an evaluation of the skill's behavior."
---

# Skill Optimizer

Rewrite one skill so it loads less, reads clearer, and triggers better — without losing what it knows.

The work is entirely on existing content: move it, cut it, rewrite it. Nothing new is invented here. If the author wants a section that does not exist yet, that is a different job and the plan should say so instead of quietly writing new material under the heading of "optimization".

### When to use

- The body has grown past the point where a model can hold it (approaching 500 lines)
- Sections that only matter on one branch are sitting in the main path
- Instructions are all-caps directives with no reason attached, or so specific they stop the model from generalizing
- The skill does not fire when it should, or fires on the wrong requests
- Reference files, scripts, or examples have drifted out of sync with the body

### Invocation

The user names a skill directory (or its SKILL.md) and says what bothers them. Both are natural language, not flags:

- "just diagnose it, don't change anything" → Phase 1 only, then stop
- "only fix the description" → run only the description group in Phase 2
- "split the body but leave my wording alone" → disclosure group only, no instruction rewrites

Record which groups the user authorized. Everything else is out of scope for this run.

---

## Phase 1 — Change list

Read the target's SKILL.md fully, plus every file under `references/`, `scripts/`, `assets/`, and `agents/`. Read `references/rewrite-playbook.md` — it holds the thresholds and the mechanics for every change type below.

Produce a change list, not an audit report. Each item is one intended change:

```markdown
| # | Problem | Location | Action | Reason |
|---|---------|----------|--------|--------|
| 1 | Error recovery is 67 lines in the main path but only matters when validation fails | SKILL.md L345-411 | extract → references/<topic>.md | move to on-demand loading |
| 2 | "ALWAYS name output report_final.docx" | SKILL.md L83 | rewrite | hardcoded filename, model cannot generalize |
| 3 | Description omits the "before publishing" scenario | frontmatter | rewrite | the body lists it, the metadata does not, so it will not fire |
```

Four actions only: `extract` (move to a bundled file), `rewrite` (same place, better text), `delete` (nothing depends on it), `fix` (objectively broken: path, permission, frontmatter, missing `__init__.py`).

Then show the budget math — current lines, expected delta per item, projected total. If the projection exceeds 500, the plan is incomplete.

Then stop and show the list. Do not begin editing until the author picks which items to apply. If the list is empty, say the skill is structurally sound and stop here; inventing work to justify the run wastes the author's review time.

---

## Phase 2 — Apply

Work through the authorized groups in this order. Each group loads its section of the playbook.

### Group 1 — Split by loading level

Decide per block whether the model needs it every time the skill triggers, or only on one branch:

- Every time → stays in the body
- One branch only, and the block is long → `references/<topic>.md`
- Deterministic and repeatable → `scripts/`, called from the body

Every extraction leaves a pointer that names the condition, not just the path: "Read `references/<topic>.md` when a validation error occurs in Step 3" beats "See references/ for details", because the second one is only followed by a model that already opened the file.

Merge into an existing reference file when the topic matches instead of creating a ninth file. A skill with nine thin references has the same problem as a 700-line body, relabeled.

### Group 2 — Rewrite instructions

For each `rewrite` item:

1. Replace bare directives with directive + reason, so the model can generalize instead of obeying literally: "Validate the output as JSON before returning, because the pipeline drops malformed payloads and the failure surfaces much later."
2. Replace hardcoded specifics with the principle behind them: "Name the output to match the input filename, because downstream tools expect consistency."
3. Delete guidance that changes nothing — restating default behavior, emphasis that repeats itself, edge cases too rare to pay for.
4. When two instructions contradict, decide which one the author actually meant and remove the other. Ask if it is genuinely unclear rather than picking the more recent one.

Show these as before → after pairs and let the author accept or reject each one. A rewrite can shift meaning, and the author's intent outranks the style rule.

### Group 3 — Rewrite the description

The description is the only part of the skill that is always in context, so it carries all the triggering work: what the skill does, when to use it, the words users actually type, and the near-miss cases that look similar but are not this skill. Keep it pushy enough to beat the model's habit of solving simple things without consulting anything.

Show current against proposed, with one line per change. Do not apply without confirmation — this field decides whether the skill fires at all.

### Group 4 — Health fixes

Objectively broken things, resolved without judgement calls:

- Body points at a path that does not exist → fix the path or create the file
- Missing required frontmatter → add it; align `name` with the directory
- `.sh` without execute bit → `chmod +x`
- Python package without `__init__.py` → add one
- Reference over 300 lines without a table of contents → add one
- Reference no one points at → ask: delete it, or wire in a pointer
- Destructive command with an unvalidated path → validate the path, or require confirmation
- Example over 30 lines demonstrating the obvious → trim to input/output

### Preview, then write

Before touching disk, show a diff of every file, grouped by the step that produced it, with each hunk labelled `insert`, `replace`, or `delete` and one line of rationale. Wait for the go-ahead. Then apply and summarize: files changed, added, removed; lines removed and added; instructions rewritten; description changed or not.

---

## Phase 3 — Verify

### Structure (always)

- **Completeness** — every line removed from the body exists in a bundled file
- **Pointer integrity** — every path named in the body exists; every bundled file is named from the body
- **No new duplication** — extracted content is not also still in the body
- **Standalone readability** — the body still reads as a workflow: what happens, in what order, when to branch. Only the how was deferred.
- **Budget** — the body is under 500 lines

### Behavior (only when it can actually be checked)

Structural checks prove the files agree with each other. They cannot prove the skill still works, and a refactor that removes half the body is exactly the change most likely to break behavior while passing every structural check.

So: if the target skill has `evals/evals.json`, rerun those prompts against the new version, compare with the pre-change run or a baseline, and report the delta. If it has no evals, the verdict must say **behavior unverified** in the verdict line itself — not in a footnote the author will skip.

Verdict is one of three, never blurred:

- **PASS** — structure holds and behavior was re-checked
- **STRUCTURAL PASS, BEHAVIOR UNVERIFIED** — structure holds, nothing was run
- **NEEDS WORK** — with the specific items

---

## Failure modes

- Adding content under the name of optimization: new sections, new capabilities, new examples the author never asked for
- Rewriting wording the author liked because the style rule prefers another phrasing — the rule serves the author
- Extracting so aggressively that the body becomes a table of contents with no instructions in it
- Splitting into many thin reference files instead of merging into the right one
- Reporting PASS from structural checks alone, which is the most expensive mistake here: the author ships, and the regression shows up in use
- Touching items that were not in the approved change list

---

## Resources

- `references/rewrite-playbook.md` — thresholds, split rules, instruction rewrite patterns, description construction, diff preview format, verification checklist. Load it in Phase 1 and keep it open through Phase 3.
