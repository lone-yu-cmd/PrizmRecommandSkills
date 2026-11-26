# Rewrite & Enhancement Playbook

Mechanics for every change type across all five optimizer actions: thresholds, loading-level placement, evidence-first diagnosis, writing and rewrite patterns, description & trigger checks, health fixes, preview format, and verification. Load in Phase 1 and keep open through Phase 3.

## Table of contents

1. [Thresholds & line budget](#1-thresholds--line-budget)
2. [Progressive disclosure & split/placement rules](#2-progressive-disclosure--splitplacement-rules)
3. [Evidence-first diagnosis, writing & rewrite standards](#3-evidence-first-diagnosis-writing--rewrite-standards)
4. [Description construction, update decision & trigger sanity check](#4-description-construction-update-decision--trigger-sanity-check)
5. [Health fixes](#5-health-fixes)
6. [Unified diff preview format](#6-unified-diff-preview-format)
7. [Verification checklist](#7-verification-checklist)

---

## 1. Thresholds & line budget

Numbers make judgment repeatable without overruling readability or inviting cosmetic churn. A well-structured 520-line body beats a 300-line body that no longer explains itself; 450 lines with 100 blank lines carries less risk than 450 lines of dense rules.

| Measurement | Watch | Act |
|---|---|---|
| SKILL.md length | 400 lines | 500 lines: split |
| One purely procedural section | 15 lines | 30 lines: extract to `references/` |
| One conditional branch (per framework/platform) | 10 lines | 15 lines: one reference file per variant |
| Reference file | 200 lines | 300 lines: add a table of contents |
| Example | 20 lines | 30 lines: trim to input/output |
| Directive density | 3 capitals per 100 lines | 5 per 100 lines without a reason attached |

### Line budget math & over-budget handling

Count total lines including frontmatter and blank lines. Always show the arithmetic in Phase 1:

`current + estimated adds - estimated extracts/deletes = projected total / 500`

If an addition or existing bloat pushes `SKILL.md` past 500 lines, identify branch-specific procedural sections (>15 lines), extract them to `references/` with conditional pointers, and keep only the flow-control summary in `SKILL.md` (e.g., `"Place ~80 lines of new procedural detail in references/ with a 20-line routing summary in SKILL.md, net +20; or extract an existing 80-line block leaving a 20-line summary, net -60"`).

---

## 2. Progressive disclosure & split/placement rules

Skills use a three-level loading system:

- **Level 1 — Metadata (`name` + `description`)**: Always in context (~100 words). Carries all triggering context.
- **Level 2 — `SKILL.md` body (<500 lines ideal)**: Loaded whenever the skill triggers. Holds flow-control logic (decisions, routing, gates, phase order) so the model can run the workflow from `SKILL.md` alone.
- **Level 3 — Bundled resources (unlimited)**: Loaded or executed only when needed.

Ask one question per block: **does the model need this every time the skill fires, or only on a specific branch?**

| Content type | Belongs in | Why |
|---|---|---|
| Phase order, decision points, gates, routing | `SKILL.md` body | Needed every run to know what happens next |
| Stop conditions, confirmation points, output shape | `SKILL.md` body | Core flow control |
| Error tables, format specs, field lists, rubrics | `references/` | Only needed on the failing, formatting, or branch path |
| Branch-specific sub-procedure (>15 lines) | `references/` | Rarely needed, expensive to carry on every run |
| Substantial domain/platform variants (>15 lines each) | `references/<variant>.md` | Only one variant applies per run |
| Deterministic transforms, aggregation, repeated helper logic | `scripts/` | Cheaper and more reliable to execute than describe or rewrite each run |
| Subagent protocols (grader, comparator, validator) | `agents/` | Loaded only when spawning that subagent |
| Output templates, icons, fonts | `assets/` | Copied or filled without loading into prompt context |
| Long worked example | `references/` | Useful once, costly every trigger |

Four rules keep splitting and additions healthy:

- **The body stays a workflow.** After extraction or addition, `SKILL.md` must still state what happens, in what order, and when to branch — never reduce it to a bare table of pointers.
- **Conditional pointers name *when* to load.** `"Read references/error-recovery.md when a validation error occurs in Step 3"` is followed; `"See references/error-recovery.md for details"` is ignored because a model that has not opened the file does not know when it matters.
- **Merge instead of proliferating.** Before creating a new reference file, check existing `references/` files and append when the topic matches. Nine 20-line references recreate the loading problem with more paths to keep in sync.
- **Promote repeated helpers to `scripts/`.** When execution transcripts or failure reports show the model repeatedly writing similar parsing, cleanup, or validation helper scripts across runs, bundle that script in `scripts/` and point `SKILL.md` to its command instead of adding more prose.

---

## 3. Evidence-first diagnosis, writing & rewrite standards

### Evidence-first & anti-overfitting

- **Trace root causes before touching structure.** When a user shares a bad output, transcript, or failing test, map each edit directly to why the model skipped a step, misread a rule, burned tokens in a loop, or hit a missing dependency.
- **Generalize incident fixes.** Never hardcode a single filename, column name, or dataset from one failure into the skill; abstract the underlying invariant (e.g., `"Detect encoding and parse quoted fields with a standard CSV parser"` rather than `"Use UTF-8 and handle commas in sales_q4.csv"`).
- **Cut token-wasting instructions.** If transcripts show an instruction triggers unnecessary detours without improving output quality, delete or narrow it instead of layering on counter-rules.

### Rewrite patterns (for existing text)

- **Directive without reason → directive with reason**: The model generalizes from reasons and obeys bare commands mechanically.
  ```text
  Before: ALWAYS validate the JSON before returning.
  After:  Validate the output as JSON before returning, because the downstream
          pipeline silently drops malformed payloads and the failure surfaces much later.
  ```
- **Over-specific → principle**: Hardcoded filenames, column names, or single scenarios prevent generalization.
  ```text
  Before: ALWAYS name the output report_final.docx.
  After:  Name the output to match the user's input filename, because downstream
          tools expect the two to correspond.
  ```
- **Redundant → deleted**: Remove lines that change nothing — restatements of default model behavior ("be thorough and careful"), the same rule repeated in two sections, stacked emphasis ("**MUST always**"), or rare edge cases whose token cost exceeds their value.
- **Contradiction → one survivor**: Two incompatible instructions are a bug. Keep the one reflecting the author's intent, remove the other, and state why; ask if genuinely ambiguous rather than picking the newer line.
- **Prose → numbered steps**: Encode sequential actions as numbered lists so steps cannot be misread as parallel options.
- **Positional → named**: Replace `"see above"` with explicit targets like `"see §Phase 2 Group 3"`.

### Authoring standards (for new or rewritten text)

- **When `MUST`/`ALWAYS` is justified**: Apply the damage test — if deviating causes real harm (safety constraint, scope boundary, irreversible data loss), a strong directive is justified; for style or minor preferences, explain the rationale instead.
- **Imperative form**: Start steps with action verbs (`"Read the file"`, `"Check each assertion"`), not passive voice (`"The file should be read"`).
- **Tone & numbering consistency**: Match the target skill's tone (conversational vs technical) and its existing heading/numbering scheme (`Phase N` / `Step N`).
- **Domain-first organization**: For multi-framework/platform skills, organize references by domain (`react.md`, `vue.md`) rather than function so only one file loads per run.
- **Example writing**: Add examples only when an output format or transformation is non-obvious. Keep each example under 30 lines, use realistic `Input/Output` or `Before/After` pairs, and avoid 50-line examples where a 2-line rule suffices.
- **Output format definitions**: Mark required report structures, JSON schemas, or templates explicitly as fixed specifications (`"Use this template:"`), not variable examples.

---

## 4. Description construction, update decision & trigger sanity check

The `description` frontmatter field is the only part always in context and carries all triggering work. Construct it with four parts:

1. **What** — verb-led capability summary
2. **When** — trigger contexts, including scenarios listed in the body that metadata omitted
3. **Keywords** — exact terms and bilingual phrases users naturally type
4. **Near-miss negatives** — neighboring jobs that look similar so the skill does not misfire

Write slightly pushy to counter model undertriggering without claiming unrelated tasks. Before proposing, check: does it read naturally rather than like a keyword dump, reflect real user phrasing, and promise only what the body delivers?

### When an addition warrants a description update

- **Update needed when**: the addition introduces a new capability or mode, a new trigger scenario, a new supported domain/framework, or new user-facing keywords.
- **Update NOT needed when**: the addition deepens existing behavior without changing scope, adds internal structure (`references/`, `agents/`) invisible to users, or adds illustrative examples.
- **Confirmation rule**: Show `current`, highlight what changed, propose the revised `description`, and wait for user approval — never auto-modify `description`.

### Trigger boundary dry-run

Whenever proposing a new or revised `description`, attach **4–6 realistic sanity queries** in the preview so the author can spot misfires immediately:
- **2–3 should-trigger queries**: realistic user prompts, including at least one implicit phrasing that does not name the skill explicitly.
- **2–3 should-not-trigger queries**: tricky near-miss requests sharing keywords with the skill that belong to a neighboring task.

---

## 5. Health fixes

| Problem | Fix | Note |
|---|---|---|
| Body names a path that does not exist | Fix the path, or create the file | Check every `references/`, `scripts/`, `assets/`, `agents/` mention |
| Missing `name` or `description` | Add it | `name` must match the directory name |
| YAML does not parse | Repair quoting/indentation | Unquoted colons inside `description` are the usual cause |
| `.sh` not executable | `chmod +x` | A script that cannot run is a dead pointer |
| Python package without `__init__.py` | Add it | Needed for `python -m` style imports |
| Reference over 300 lines, no TOC | Add one | Top-level sections only |
| Reference nobody points at | Delete, or wire a pointer | Flag in Phase 1 for the author to choose; do not guess |
| Destructive command, unvalidated path | Validate, or require confirmation | `rm -rf $VAR` with an empty `$VAR` is the classic disaster |
| Example demonstrating the obvious | Trim, or replace | Show a non-obvious input/output pair |

---

## 6. Unified diff preview format

Group changes by file in change-list order (for small targeted edits, combine this preview with the Phase 1 change list into one single confirmation gate). Label every hunk in existing files and explain *why*; show new files in full with the standard they follow:

```text
SKILL.md
  [add] after §Output Format (~22 lines)
    why: requested Fix Suggestions section; follows addition-checklist.md §2
    + ## Fix Suggestions ...

  [extract] L345-411 §Error Recovery → references/error-recovery.md
    why: 67 lines only needed on the validation-failure branch
    pointer added at §Phase 2 Step 3

  [rewrite] L83
    - ALWAYS name output report_final.docx
    + Name the output to match the user's input filename, because downstream
      tools expect the two to correspond.
    why: hardcoded name prevents generalization

  [delete] L120-124
    - "Be thorough and careful."
    why: restates default model behavior

references/error-recovery.md (new file, follows structure-patterns.md §2)
  [insert] full content (67 lines moved from SKILL.md, headings preserved)
```

Close with totals — files touched, lines added, lines removed, projected `SKILL.md` length — then wait for confirmation.

---

## 7. Verification checklist

Report every item individually as `PASS` or `FAIL` with evidence.

**Structure**
1. **Lossless completeness** — every block extracted from `SKILL.md` exists in a bundled file with matching content.
2. **Pointer integrity** — every path mentioned in `SKILL.md` exists on disk; every bundled file is named from `SKILL.md` with a loading condition (or, for `assets/` consumed by a bundled script, referenced by that script whose pointer is in `SKILL.md`).
3. **No new duplication** — neither extracted nor newly added content is duplicated between `SKILL.md` and `references/`.
4. **Standalone readability** — reading `SKILL.md` alone still executes the workflow end to end.
5. **Budget & TOC** — `SKILL.md` is under 500 lines; any reference >300 lines has a TOC.
6. **Frontmatter** — valid YAML; `name` matches directory; verify `description` matches capabilities (if missed in Phase 2 Group 4, flag suggestion without auto-editing).
7. **Scope adherence & addition post-flight** — zero edits outside approved items (and `insert-only` verified if `add-only` was requested); any `add` items pass `references/addition-checklist.md`.

**Behavior (self-contained)**
8. If `evals/evals.json` exists: rerun prompts in an isolated workspace outside the target skill directory against both the updated skill and the pre-edit snapshot (parallel subagents when available, or serial runs noting that limitation), and report pass-rate delta and any per-case regressions.
9. If no `evals/evals.json` exists and core workflow logic or `description` changed: propose 2 realistic smoke-test prompts (plus 4–6 trigger boundary queries if `description` changed and not already verified) and offer to run a before/after check against the pre-edit snapshot; if the user skips behavioral testing (or edits were purely mechanical health fixes), state `"behavior unverified"` directly in the verdict line.
