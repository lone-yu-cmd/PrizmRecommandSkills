# Rewrite Playbook

Mechanics for every change type in the optimizer's four groups: thresholds, decision rules, patterns, and the preview format. Load in Phase 1 and keep open through Phase 3.

## Table of contents

1. [Thresholds](#1-thresholds)
2. [Split rules: body vs references vs scripts](#2-split-rules-body-vs-references-vs-scripts)
3. [Instruction rewrite patterns](#3-instruction-rewrite-patterns)
4. [Description construction](#4-description-construction)
5. [Health fixes](#5-health-fixes)
6. [Diff preview format](#6-diff-preview-format)
7. [Verification checklist](#7-verification-checklist)

---

## 1. Thresholds

Numbers exist to make a judgement repeatable, not to overrule it. A 520-line body that reads well beats a 300-line body that no longer explains itself.

| Measurement | Watch | Act |
|---|---|---|
| SKILL.md length | 400 lines | 500 lines: split |
| One purely procedural section | 15 lines | 30 lines: extract to `references/` |
| One conditional branch (per framework/platform) | 10 lines | 15 lines: one reference file per variant |
| Reference file | 200 lines | 300 lines: add a table of contents |
| Example | 20 lines | 30 lines: trim to input/output |
| Directive density | 3 capitals per 100 lines | 5 per 100 lines without a reason attached |
| Heading depth | 3 levels | 5 levels: flatten to bold labels |
| Table width | 4 columns | 6 columns: definition list or split |
| Paragraph | 80 words | 100 words: break up |

Measure the thing the author cares about. A body at 450 lines with 100 blank lines is not the same risk as 450 lines of dense rules, and saying so is more useful than quoting the number.

---

## 2. Split rules: body vs references vs scripts

Ask one question per block: **does the model need this every time the skill fires, or only on one branch?**

| Block | Belongs in | Why |
|---|---|---|
| Phase order, decision points, gates, routing | body | Needed to know what to do next, every run |
| Stop conditions, confirmation points, output shape | body | Flow control |
| Error tables, format specs, field lists | `references/` | Only needed on the failing or formatting branch |
| A sub-procedure over 15 lines used on one branch | `references/` | Rarely needed, expensive to carry |
| Platform/framework variants, each substantial | one file per variant | Only one variant is ever relevant |
| Deterministic transforms, aggregation, schema validation | `scripts/` | Cheaper to run than to describe |
| Long worked example | `references/` | Useful once, costly always |

Two rules that keep extraction from degrading the skill:

- **The body stays a workflow.** After extraction it should still say what happens, in what order, and when to branch. If the body becomes pointers with no instructions, the extraction went too far.
- **The pointer names the condition.** "Read `references/error-recovery.md` when a validation error occurs in Step 3" is followed. "See references/ for details" is not, because a model that does not already know the file matters will not open it.

Merge, do not proliferate. If a block's topic matches an existing reference file, append it there. A skill with nine 20-line references has the same loading problem as a 700-line body, with more paths to keep in sync.

---

## 3. Instruction rewrite patterns

### Directive without reason → directive with reason

The model generalizes from the reason; it only obeys the directive. Reasons are what let a skill work on the input the author never imagined.

```text
Before: ALWAYS validate the JSON before returning.
After:  Validate the output as JSON before returning, because the downstream
        pipeline silently drops malformed payloads and the user sees the
        failure much later, on a different screen.
```

### Over-specific → principle

Hardcoded filenames, column names, and single scenarios make a skill brittle: the model follows the example instead of the intent.

```text
Before: ALWAYS name the output report_final.docx.
After:  Name the output to match the user's input filename, because downstream
        tools expect the two to correspond.
```

### Redundant → deleted

Delete when removing the line changes nothing the executor does:

- Restating behavior the model already has by default ("be helpful", "think carefully")
- The same rule in two sections
- Emphasis on top of emphasis ("**MUST always**")
- Edge cases so rare the token cost outweighs the coverage

### Contradiction → one survivor

Two instructions that cannot both be satisfied is an error, not a style issue. Determine which one reflects the author's intent, remove the other, and say which one was dropped and why. If the intent is genuinely ambiguous, ask — do not pick the more recently written one.

### Prose → numbered steps

When a paragraph encodes a sequence, a numbered list carries the order in fewer tokens and cannot be misread as parallel options.

### Positional → named

"See above" assumes spatial memory a model does not have. "See §Phase 2 Step 3" resolves by name.

---

## 4. Description construction

The description is the only always-loaded part of a skill, so it does all the triggering work. Build it in four parts:

1. **What** — verb-led capability statement: "Restructure and rewrite a skill that has grown too long…"
2. **When** — the contexts that should fire it, including the ones the body lists but the description forgot. Missing a scenario the body knows about is the most common triggering bug.
3. **Keywords** — terms users actually type for this job. If the body says "benchmark", "eval", and "grading" and the description says none of them, users of those words never trigger the skill.
4. **Near-miss negatives** — the nearby requests that look similar but are a different job, so the description does not claim them. One clause is enough; a description that claims everything triggers on everything.

Write it slightly pushy: models undertrigger, solving a simple request themselves rather than consulting a description that matches. Pushiness has a limit — a description that oversells will fire on the wrong work, and the misfire costs more than the missed trigger.

Check before proposing:

- Does it read as a sentence a person would say, or as a keyword dump?
- Is every phrase in it a phrase a user would actually type?
- Does it promise anything the body cannot deliver?

---

## 5. Health fixes

| Problem | Fix | Note |
|---|---|---|
| Body names a path that does not exist | Fix the path, or create the file | Check every `references/`, `scripts/`, `assets/`, `agents/` mention |
| Missing `name` or `description` | Add it | `name` must match the directory name |
| YAML does not parse | Repair quoting/indentation | Unquoted colons inside a description are the usual cause |
| `.sh` not executable | `chmod +x` | A script that cannot run is a dead pointer |
| Python package without `__init__.py` | Add it | Needed for `python -m` style imports |
| Reference over 300 lines, no TOC | Add one | Top-level sections only |
| Reference nobody points at | Delete, or wire a pointer | Ask which; do not guess |
| Destructive command, unvalidated path | Validate, or require confirmation | `rm -rf $VAR` with an empty `$VAR` is the classic disaster |
| Example demonstrating the obvious | Trim, or replace | Examples should show a non-obvious input/output pair |

---

## 6. Diff preview format

One block per file, in the order the change list presented them. Every hunk gets a label and a reason, because the author is approving meaning, not characters.

```text
SKILL.md
  [extract] L345-411 §Error Recovery → references/error-recovery.md
    why: 67 lines that only matter on the validation-failure branch
    pointer added at §Phase 2 Step 3

  [rewrite] L83
    - ALWAYS name output report_final.docx
    + Name the output to match the user's input filename, because downstream
      tools expect the two to correspond
    why: hardcoded name, model cannot generalize to other inputs

  [delete] L120-124
    - "Be thorough and careful."
    why: default behavior, changes nothing
references/error-recovery.md
  [insert] 67 lines moved from SKILL.md, headings preserved
```

Close the preview with the totals — files touched, lines removed, lines added, projected body length — then wait.

---

## 7. Verification checklist

Run after applying, and report each item as PASS or FAIL with the specific evidence, not as a single overall "looks good".

**Structure**

1. Completeness — each removed block exists in a bundled file, byte-comparable content
2. Pointer integrity — every path in the body exists; every bundled file is named from the body
3. No new duplication — nothing lives in both places
4. Standalone readability — read the body alone; can you still execute the workflow?
5. Budget — bodies under 500 lines, references over 300 with a TOC
6. Frontmatter — parses, `name` matches directory

**Behavior**

7. If `evals/evals.json` exists: rerun the prompts, grade as before, report the pass-rate delta and any per-case regressions
8. If it does not: state "behavior unverified" in the verdict line

A structural pass is not a quality pass. The refactor most likely to break a skill is the one that removes the most text, and it passes every structural check by construction.
