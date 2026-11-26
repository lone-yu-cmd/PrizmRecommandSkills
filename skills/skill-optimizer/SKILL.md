---
name: "skill-optimizer"
description: "Improve, expand, refactor, and fix an existing skill—diagnosing real failure outputs or bloated structure, adding missing sections, reference docs, subagents, helper scripts, assets, or examples, splitting long bodies for progressive disclosure, rewriting unclear or overfitted instructions, repairing broken resources, and tuning description triggering. Use whenever someone asks to optimize, enhance, debug, expand, trim, split, clean up, modernize, fix triggering, or add content/capabilities to an existing skill, or says 「优化/重构/精简/拆分这个 skill」「这个 skill 跑出来效果不对」「给 skill 加个章节/示例/脚本」「补充错误处理」「完善这个 skill」「太长了」「触发不准」, even without saying 'optimizer' or 'enhance'. Do not use to create a brand-new skill from scratch, perform a read-only audit with no edits, or run standalone multi-iteration benchmark suites."
---

# Skill Optimizer

Improve one existing skill from real execution evidence or structural/capability requests — making it work reliably, load less, read clearer, and trigger accurately without inventing unrequested features or editing outside approved scope.

Handle additions, extractions, rewrites, deletions, and resource fixes through one unified change list (`add`, `extract`, `rewrite`, `delete`, `fix`) and a self-contained verification loop with zero external skill dependencies.

### Invocation & Authorized Scope

The user names a skill directory (or its `SKILL.md`) and describes what failed, what is missing, or what to change. Map natural-language constraints to an authorized scope before proposing edits (scopes can also be combined, e.g., `description-only + fix`):

- `"just diagnose it, don't change anything"` → `diagnose-only` (Phase 1 only, then stop)
- `"don't modify existing text"` / `"only add X"` → `add-only` (lock to `add` actions and enforce `insert-only` check)
- `"refactor/trim without adding new features"` → `refactor-only` (`extract`, `rewrite`, `delete`, `fix`; no `add`)
- `"only fix the description"` → `description-only` (Group 4 only)
- `"split the body but leave my wording alone"` → `disclosure-only` (Group 2 only, no instruction rewrites)
- Default → `all actions` (combine `add`, `extract`, `rewrite`, `delete`, `fix` as needed)
- Explicit pre-authorization (e.g., `"无需二次确认，直接执行并验证"`): still output the Phase 1 change list and line-budget math for traceability, then proceed through Phase 2 and Phase 3 without pausing (still never auto-modifying `description` unless explicitly authorized).

**Examples:**
```text
/skill-optimizer skills/my-skill "这次跑出来跳过了校验还绕了远路，帮我修一下"
/skill-optimizer skills/report-builder "add a Fix Suggestions section after Output Format"
/skill-optimizer skills/data-validator "别动现有的东西，只加一个 agents/schema-checker.md"
/skill-optimizer skills/my-skill "只修 description 和断链，别改正文"
```

Record the authorized scope first; everything outside it is out of scope for the run.

---

## Phase 1 — Diagnose & Change list

Read the target's `SKILL.md` fully, plus every file under `references/`, `agents/`, `scripts/`, and `assets/` if present. Always load `references/rewrite-playbook.md`; load `references/structure-patterns.md` when adding or extracting files outside `SKILL.md` or splitting domain variants; load `references/addition-checklist.md` when any `add` action is planned.

Diagnose on two tracks, prioritizing real execution evidence whenever available:

1. **Evidence-first diagnosis**: If the user reports a real failure, shares bad outputs or transcripts, or the target has failing `evals/evals.json` cases, trace root causes first — skipped steps, misleading rules, token-wasting loops, or repeated ad-hoc helper code that belongs in `scripts/`. Bind each proposed edit to the observed failure and run an **anti-overfitting check** so one-off incident fixes generalize into reusable principles rather than brittle single-case patches.
2. **Structure & expansion diagnosis**: For explicit additions, bloated bodies (>500 lines), broken resources, or triggering gaps, classify edits into five atomic actions: `add` (tag type: `section` / `reference` / `agent` / `script` / `asset` / `example`), `extract` (move to a bundled file), `rewrite` (same place, better text), `delete` (redundant or token-wasting), `fix` (objectively broken path, permission, frontmatter, TOC, or missing `__init__.py`).

```markdown
**Authorized scope:** <all actions | add-only | refactor-only | description-only | disclosure-only | diagnose-only>

| # | Action | Target / Type | Location | Summary & Rationale |
|---|--------|---------------|----------|---------------------|
| 1 | add | section | SKILL.md (after Output Format) | Add Fix Suggestions for error-level findings; requested by user |
| 2 | extract | reference | SKILL.md L345-411 → references/<topic>.md | 67 lines only needed on validation failure; move to on-demand loading |
| 3 | rewrite | instruction | SKILL.md L83 | Generalize hardcoded manifest rule to input-matching principle |
| 4 | delete | redundant text | SKILL.md L120-124 | Restates default behavior, adds no behavioral signal |
| 5 | fix | script health | scripts/check.sh | Missing execute bit (`chmod +x`) |
```

**Conflict & orphan handling:** If a requested `add` contradicts or invalidates an existing line, pair the `add` with an explicit `rewrite` or `delete` item explaining the causal link. When scope is locked to `add-only`, stop before drafting, quote the conflicting line, and offer the two real options — keep the existing line and weaken the addition, or replace the existing line — so the author chooses explicitly. Also list any orphan file discovered under `references/`, `agents/`, `scripts/`, or `assets/` in the Phase 1 table (`delete` vs `wire a conditional pointer`) so the author resolves it before Phase 2.

**New-content outlines** *(include only when the list contains `add` items)*: Outline what each addition covers and cite the reference standard justifying its placement and shape.

**Line budget math:** Show `current + estimated adds - estimated extracts/deletes = projected total / 500`. If projected total exceeds 500, include a split plan right here (routing pointer in `SKILL.md` + details in `references/`).

**Adaptive confirmation gate:** If the list is empty, report that the skill is sound and stop without inventing work. For **small, targeted edits** (1–2 files, no conflicting deletions, no new agents/scripts or cross-file splits — e.g., fixing a broken path, tuning `description`, adding one short section or a few examples), draft the changes and combine Phase 1 with the Phase 2 unified preview into **one single confirmation gate**. For **larger or higher-risk edits** (cross-file splits, new agents/scripts, rule conflicts, or multi-group refactors), stop after Phase 1 for plan approval before drafting, then confirm once more at the unified preview.

---

## Phase 2 — Apply

Draft all authorized groups in order, collecting Group 3 `before → after` pairs and Group 4 `current vs proposed` diffs into the single **Preview, then write** gate rather than pausing multiple times mid-Phase 2.

### Group 1 — Add new content (`add`)

1. Classify each addition (`section`, `reference`, `agent`, `script`, `asset`, or `example`) and place it at the right loading level per `references/rewrite-playbook.md` §2.
2. Follow `references/addition-checklist.md` (Pre-flight and Content standards) for the content type, and `references/structure-patterns.md` when creating files under `references/`, `agents/`, `scripts/`, or `assets/`.
3. Match the target skill's tone, heading levels, and Phase/Step numbering; verify new content neither duplicates nor contradicts existing instructions.

### Group 2 — Split by loading level (`extract`)

Decide per block whether the model needs it every run or only on one branch:
- Every run → keep in `SKILL.md` body
- One branch only (>15 procedural lines, or substantial per-domain variant) → `references/<topic>.md`
- Deterministic or repeatedly written helper logic across runs → `scripts/`, invoked from `SKILL.md`

Leave a conditional pointer naming *when* to load the file ("Read `references/<topic>.md` when a validation error occurs in Step 3", not "See references/ for details"). Merge into an existing reference file when the topic matches instead of proliferating thin files.

### Group 3 — Rewrite instructions (`rewrite`)

For each `rewrite` item:
1. Replace bare directives with directive + reason so the model can generalize. Reserve `MUST`/`ALWAYS`/`NEVER` for genuine safety or scope guardrails where deviation causes real damage.
2. Generalize hardcoded specifics and one-off incident patches into reusable principles; use imperative form.
3. Delete guidance that changes nothing or wastes tokens without improving output (default model behavior, repeated emphasis, negligible edge cases).
4. Resolve contradictions — keep the one reflecting author intent and drop the other, or ask when genuinely ambiguous.
5. Treat output format definitions as fixed specifications, not variable examples.

Include `before → after` pairs in the Preview gate so the author can accept or reject each rewrite; author intent outranks style rules.

### Group 4 — Update or rewrite description (`rewrite` frontmatter)

Build `description` in four parts: what the skill does, when to use it (including body scenarios missing from metadata), natural user keywords, and near-miss negatives. Keep it slightly pushy to counter undertriggering without overselling onto unrelated tasks.

When an `add` introduces a new capability, mode, trigger scenario, or domain, consult `references/rewrite-playbook.md` §4 and include a proposed description update in the Preview gate. Always show `current` vs `proposed` (line by line) alongside **4–6 trigger boundary sanity queries** (2–3 realistic should-trigger + 2–3 tricky near-miss negatives) and wait for confirmation — never auto-modify `description`.

### Group 5 — Health fixes (`fix` / `delete`)

Resolve objectively broken items per `references/rewrite-playbook.md` §5:
- Broken path in body → fix path or create target; missing/invalid frontmatter → repair and align `name` with directory
- `.sh` without execute bit → `chmod +x`; Python package missing `__init__.py` → add it
- Reference >300 lines without TOC → add TOC; orphan reference → apply the Phase 1 choice (delete or wire a conditional pointer)
- Destructive command with unvalidated path → validate or require confirmation; obvious >30-line example → trim to concise input/output

### Preview, then write

Before touching disk, display a unified preview grouped by file using `references/rewrite-playbook.md` §6 (existing files with labeled hunks + Group 3 `before → after` and Group 4 `current vs proposed` + trigger sanity queries; new files in full + applied standard; totals).

Wait for go-ahead (merged with Phase 1 for small targeted edits, or skipped when explicitly pre-authorized). Before writing, if the target skill has `evals/evals.json` OR core workflow logic or `description` will change, snapshot the unmodified target directory into an isolated temp workspace outside the skill directory so Phase 3 has a clean baseline. Apply approved edits (setting `+x` on new `.sh` scripts) and summarize files changed, added, removed, line deltas, and whether `description` changed.

---

## Phase 3 — Verify

### Structure (always)

Verify every item and report PASS or FAIL with concrete evidence:
- **Lossless completeness** (`extract`) — every line removed from the body exists in a bundled file
- **Pointer integrity** — every path named in the body exists; every bundled file (including newly created ones) is pointed to from the body with a loading condition (or, for `assets/` consumed by a bundled script, referenced by that script whose pointer is in `SKILL.md`)
- **No new duplication** — added or extracted content does not duplicate body or other references
- **Standalone readability** — `SKILL.md` still reads top-to-bottom as a complete workflow
- **Line budget & frontmatter** — `SKILL.md` under 500 lines, references >300 lines have a TOC, YAML frontmatter parses and `name` matches directory
- **Type-specific post-flight** (`add`) — check each addition against `references/addition-checklist.md` (writing style, agent self-containment & I/O contract, script `chmod +x`/syntax/`__init__.py`, asset references, example <30 lines & non-trivial); confirm any capability-changing addition had a description update proposed in Phase 2 Group 4 (if skipped or out of scope, flag a suggestion here without auto-editing)
- **Scope adherence** — zero edits outside the approved change list; if `add-only` was authorized, confirm `insert-only` diff with zero modified or deleted pre-existing lines

### Behavior (self-contained)

Structural checks prove files agree; they cannot prove the skill works better after editing:
- **If `evals/evals.json` exists**: rerun those prompts in an isolated workspace outside the target skill directory against both the updated skill and the pre-edit snapshot (in parallel via subagents when available, or serially while noting that limitation when subagents are unavailable), and report the pass-rate delta and any per-case regressions.
- **If no `evals/evals.json` exists**: whenever core workflow logic or `description` changed, propose **2 realistic smoke-test prompts** (plus **4–6 trigger boundary queries** if `description` changed and they were not already validated in Preview) and offer to run a quick before/after check against the pre-edit snapshot. Only if the user skips behavioral testing (or edits were purely mechanical health fixes), state **behavior unverified** directly in the verdict line.

Verdict is strictly one of three:
- **PASS** — structure holds and behavior was re-checked (via evals or smoke/trigger checks)
- **STRUCTURAL PASS, BEHAVIOR UNVERIFIED** — structure holds, behavioral checks were skipped or not run
- **NEEDS WORK** — list the specific failing items and offer to fix them

---

## Failure modes

- Overfitting a one-off failure into a brittle, case-specific rule instead of a reusable principle
- Chasing cosmetic formatting tweaks (paragraph word counts, minor table widths) that do not improve execution
- Adding unrequested sections, capabilities, or examples during a refactoring run
- Silently editing or deleting conflicting pre-existing lines under `add-only` scope instead of quoting the line and asking the author to choose
- Extracting so aggressively that `SKILL.md` becomes a hollow table of contents, or splitting into many thin reference files
- Auto-modifying `description` without user confirmation
- Reporting `PASS` from structural checks alone without running behavioral checks
- Touching items outside the approved change list

---

## Resources

- `references/rewrite-playbook.md` — thresholds, budget math, progressive disclosure, evidence-first & anti-overfitting standards, description construction & trigger dry-run, health fixes, preview format, verification checklist. Load in Phase 1 and keep open through Phase 3.
- `references/structure-patterns.md` — directory anatomy, reference/agent/script/asset templates, domain-variant pattern, naming conventions. Load in Phase 1 or Phase 2 whenever adding or extracting files outside `SKILL.md` or splitting domain variants.
- `references/addition-checklist.md` — pre-flight, content standards, and post-flight checklists per addition type (`section`, `reference`, `agent`, `script`, `asset`, `example`). Load in Phase 2 before writing and Phase 3 during verification whenever the change list includes `add` items.
