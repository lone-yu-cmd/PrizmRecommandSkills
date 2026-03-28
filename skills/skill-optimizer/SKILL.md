---
name: "skill-optimizer"
description: "Audit and optimize SKILL.md files against skill-creator writing standards. Use this skill whenever someone wants to review skill quality, a skill feels too long or triggers poorly, before releasing a skill, or when restructuring skill content. Triggers on: 'optimize skill', 'audit skill', 'review skill quality', 'skill health check', 'skill too long'."
---

# Skill Optimizer

Audit any skill against skill-creator writing standards, then optimize it. Three phases: diagnose (read-only report), execute (restructure with user confirmation), review (verify nothing was lost).

The audit criteria come from skill-creator's own guidelines — this skill doesn't invent new rules, it enforces the existing ones.

### When to Use
- "Optimize this skill", "audit skill", "review skill quality"
- A skill feels too long or bloated
- Description doesn't trigger reliably
- Before publishing or sharing a skill
- After major edits to a skill, as a quality check

### `/skill-optimizer` \<path-to-skill-directory\> [--diagnose-only]

Accepts either a skill directory path or a direct path to a SKILL.md file.

`--diagnose-only`: Run Phase 1 only (read-only audit, no modifications).

Default mode: run all three phases with a confirmation gate before Phase 2.

---

## Phase 1: Diagnose

Read-only analysis. No files are modified.

#### Step 1: Locate and load target skill

Resolve the target path to find SKILL.md. Read it fully. Also read all files under the skill's `references/`, `assets/`, and `scripts/` directories (if they exist) to understand the full skill structure.

#### Step 2: Load audit criteria

Read `references/audit-criteria.md` from this skill's directory. This contains the detailed rubrics for each dimension.

#### Step 3: Run 8-dimension audit

Evaluate the target skill against these dimensions (detailed criteria in the reference file):

1. **Body size** — line count vs 500-line budget
2. **Progressive disclosure** — is content at the right loading level?
3. **Conditional content** — low-frequency content loading unconditionally
4. **Internal redundancy** — repeated content, description/body overlap
5. **Instruction style** — MUST/NEVER overuse vs explaining rationale
6. **Description triggering** — pushy enough? covers what + when-to-use?
7. **Reference file health** — oversized files, orphans, broken references
8. **Example effectiveness** — helpful vs token-consuming

For each finding, assign a severity:
- **error**: blocks the skill's effectiveness, should fix
- **warning**: degrades quality, recommend fixing
- **info**: minor improvement opportunity
- **style**: subjective suggestion, requires human judgment

#### Step 4: Generate diagnostic report

Output the report to conversation using the format in §Output Format below. Do NOT write to any file.

#### Step 5: Gate

If `--diagnose-only` was specified, stop here with a summary.

Otherwise, present the report and ask: "Ready to execute optimization? (yes to proceed / no to stop)"

---

## Phase 2: Execute Optimization

**Precondition**: User explicitly confirmed "yes" after reviewing the diagnostic report.

Apply fixes for error and warning findings:

#### Structural operations (auto-applied)
- **Extract**: Move reference-manual sections (procedural details, error tables, format specs) from SKILL.md to `references/` files. Replace with a concise pointer explaining when to load it.
- **Merge**: If content belongs in an existing reference file, append it there instead of creating a new file.
- **Deduplicate**: When the same concept appears twice, keep the better-located instance and remove the other.
- **Update pointers**: Add or update a Resource Loading section in SKILL.md to point to any new/modified reference files.
- **Compress**: Reduce verbose sections that restate what the description already covers.

#### Style suggestions (listed, not auto-applied)
Instruction rewrites (replacing bare MUST directives with rationale-based phrasing) and description improvements are subjective. List them as "Suggested manual edits" — the user decides whether to apply them. The reason: style rewrites can shift meaning, and the skill author's intent matters more than generic optimization.

#### Output
Print a change summary: files modified, files created, lines removed/added.

---

## Phase 3: Review

Verification pass after Phase 2 completes. Checks 5 dimensions:

1. **Completeness** — every piece of content removed from SKILL.md exists in a reference file, with a pointer from SKILL.md
2. **Pointer integrity** — every reference path mentioned in SKILL.md exists on disk; every reference file is pointed to from SKILL.md (no orphans)
3. **No new duplication** — content doesn't appear in both SKILL.md and a reference file
4. **Standalone readability** — SKILL.md is still interpretable as a workflow guide without reading reference files (the "what" and "when" are in SKILL.md; only "how" details are deferred)
5. **Line count** — SKILL.md is now within the 500-line budget

Output a verdict per check: PASS or FAIL with specifics.

Overall verdict: **PASS** or **NEEDS MANUAL FIXES** (with the specific issues listed).

---

## Output Format

The Phase 1 diagnostic report uses this structure:

```markdown
# Skill Optimizer Report
Skill: <name>
Path: <absolute-path>
Lines: N (budget: 500)

## Findings

| # | Dimension | Severity | Finding | Location |
|---|-----------|----------|---------|----------|
| 1 | Body size | warning | 413 lines — approaching 500-line budget | SKILL.md |
| 2 | Prog. disclosure | error | §Error Recovery (67 lines) is procedural detail, candidate for references/ | SKILL.md L345-411 |
| 3 | Redundancy | warning | Resume table appears in both §Error Recovery and §Resume Support | SKILL.md L398, L462 |
| ... | | | | |

## Reference File Health
- references/planning-guide.md — 361 lines, no TOC (warning: >300 lines)
- references/orphan-file.md — not referenced from SKILL.md (warning: orphan)

## Style Suggestions (manual review)
- S1: Line 47 — "You MUST always validate" → consider: "Always validate output because
  the pipeline rejects malformed JSON, which wastes a full retry cycle."
- S2: Description field — add trigger phrases: "Use when planning features, scoping work,
  preparing dev-pipeline input"

## Summary
Errors: N | Warnings: N | Info: N | Style: N
Estimated line reduction: ~N lines
```

---

## Resource Reference

Audit criteria details are in `references/audit-criteria.md`. Load it at the start of Phase 1 — it contains the per-dimension rubrics (thresholds, detection methods, false positive guidance) that this file intentionally does not repeat.
