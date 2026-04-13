---
name: "skill-optimizer"
description: "Audit and optimize SKILL.md files against skill-creator writing standards. Use this skill whenever someone wants to review skill quality, a skill feels too long or triggers poorly, before releasing a skill, or when restructuring skill content. Triggers on: 'optimize skill', 'audit skill', 'review skill quality', 'skill health check', 'skill too long'."
---

# Skill Optimizer

Audit any skill against skill-creator writing standards, then optimize it. Three phases: diagnose (read-only audit report), optimize (apply targeted fixes per diagnostic findings, with user confirmation), review (verify nothing was lost).

The audit criteria come from skill-creator's own guidelines — this skill doesn't invent new rules, it enforces the existing ones.

### When to Use
- "Optimize this skill", "audit skill", "review skill quality"
- A skill feels too long or bloated
- Description doesn't trigger reliably
- Before publishing or sharing a skill
- After major edits to a skill, as a quality check

### `/skill-optimizer` \<path-to-skill-directory\> [options]

Accepts either a skill directory path or a direct path to a SKILL.md file.

Supported options (free-text, not parsed as CLI flags):

- `--diagnose-only`: Run Phase 1 only (read-only audit, no modifications).
- `--dimensions N,N,...`: Run only the specified dimensions (comma-separated numbers, e.g., `--dimensions 5,6,9`). Useful for targeted checks after editing a specific aspect. Default: all dimensions.

Default mode: run all three phases with a confirmation gate before Phase 2.

---

## Phase 1: Diagnose

Read-only analysis. No files are modified.

#### Step 1: Locate and load target skill

Resolve the target path to find SKILL.md. Read it fully. Also read all files under the skill's `references/`, `assets/`, and `scripts/` directories (if they exist) to understand the full skill structure.

#### Step 2: Load audit criteria

Read `references/audit-criteria.md` from this skill's directory. This contains the detailed rubrics for each dimension.

#### Step 3: Run 17-dimension audit

Evaluate the target skill against these dimensions (detailed criteria in the reference file):

1. **Body size** — line count vs 500-line budget
2. **Progressive disclosure** — is content at the right loading level?
3. **Conditional content** — low-frequency content loading unconditionally; domain-variant branches that should be separate reference files
4. **Internal redundancy** — repeated content, description/body overlap
5. **Instruction style** — MUST/NEVER overuse vs explaining rationale; over-specificity/overfitting of instructions
6. **Description triggering** — pushy enough? covers what + when-to-use? consistent with body's "When to Use" section? keyword coverage of core domain terms?
7. **Reference file health** — oversized files, orphans, broken references (including scripts/ and assets/ paths)
8. **Example effectiveness** — helpful vs token-consuming
9. **Frontmatter completeness** — required fields present (name, description), YAML well-formed, name matches directory
10. **Script & asset health** — executability, orphan detection, Python package structure
11. **Safety patterns** — destructive commands, remote code execution, data exfiltration patterns
12. **Diagram effectiveness** — workflow descriptions using ASCII tree format instead of LLM-friendly numbered lists
13. **Visual noise** — decorative markdown, emoji, and HTML styling that wastes tokens without adding semantic value
14. **Semantic referencing** — positional references ("see above") instead of named anchors ("see §Phase 2 Step 3")
15. **Heading hierarchy** — heading nesting deeper than 4 levels, increasing LLM context tracking burden
16. **Information chunking** — dense paragraphs (100+ words) and wide tables (5+ columns) that hinder token-level parsing
17. **Pronoun clarity** — ambiguous pronouns ("it", "this") with unclear referents that LLMs may misresolve

If `--dimensions` was specified, run only the listed dimensions.

For each finding, assign a severity:
- **error**: blocks the skill's effectiveness, should fix
- **warning**: degrades quality, recommend fixing
- **info**: minor improvement opportunity
- **style**: subjective suggestion, requires human judgment

#### Step 4: Generate diagnostic report

Output the report to conversation using the format in §Output Format below. Do NOT write to any file.

#### Step 5: Gate

If `--diagnose-only` was specified, stop here with a summary.

Otherwise, present the report and ask: "Ready to proceed with optimization? (yes to proceed / no to stop)"

---

## Phase 2: Optimize

**Precondition**: User explicitly confirmed "yes" after reviewing the diagnostic report.

Apply targeted fixes for diagnostic findings. Each step addresses a specific category — only the parts flagged in Phase 1 are touched, unflagged content stays as-is.

Steps 1–4 are planning steps: prepare all proposed changes without writing any files. Step 5 previews them for user confirmation. Step 6 applies.

#### Step 1: Structure optimization — Progressive Disclosure

Reorganize flagged content across skill-creator's three loading levels. Only move content that was flagged in Phase 1 (D2/D3 findings) — don't reorganize sections that passed audit.

- **Level 1 (Metadata)**: Ensure `name` and `description` frontmatter are complete. Fix D9 findings. Align `name` with directory name.
- **Level 2 (SKILL.md body)**: Retain only flow-control logic — decisions, routing, gates, phase structure, and the "what/when" of each step. Target < 500 lines.
- **Level 3 (Bundled resources)**:
  - **→ references/**: Extract procedural details the model needs only on specific branches (error tables, format specs, sub-procedures > 15 lines).
  - **→ scripts/**: Identify deterministic or repetitive operations described in prose. If the instructions describe a multi-step procedure that could be a script, write it once in `scripts/` and reference it. Per skill-creator: "if all test cases resulted in the subagent writing a similar helper script, that's a strong signal the skill should bundle that script."
  - **Domain-variant pattern**: When multiple conditional branches exist for different frameworks/platforms and each exceeds 15 lines, split into one reference file per variant. SKILL.md keeps only the selection logic.
  - **Merge, don't proliferate**: If extracted content belongs in an existing reference file, append it there instead of creating a new file.

For each extraction, replace removed content with a pointer that states *when* to load it — not just a path, but the condition: "Read `references/error-recovery.md` when a validation error occurs in Step 3."

#### Step 2: Instruction improvement — Explain the Why

Improve flagged instructions following skill-creator's core writing principle: "explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general."

For each D5 finding:

1. **Improve directives with rationale** — Transform `MUST/ALWAYS/NEVER` into: imperative verb + action + reason. Example: `"ALWAYS validate JSON"` → `"Validate the output as JSON before returning, because the downstream pipeline silently drops malformed payloads and the user won't see an error until much later."`

2. **Generalize over-specific instructions** — Replace hardcoded filenames, formats, or single-scenario assumptions with the general principle. Example: `"ALWAYS name output report_final.docx"` → `"Name the output to match the user's input filename — downstream tools expect filename consistency."` The model is smart enough to adapt when it understands *why*.

3. **Prune dead weight** — Read through the full instruction set and identify guidance that is unlikely to influence model behavior: restating what the model would do by default, redundant emphasis, edge cases so rare they don't justify the token cost. Per skill-creator: "remove things that aren't pulling their weight." Delete them.

4. **Resolve contradictions** — If two instructions conflict (D5 error findings), determine which reflects the skill author's actual intent and remove the other.

Present all instruction improvements and deletions as a numbered list of **before → after** pairs. The user confirms or rejects each individually — rewrites can shift meaning, and the skill author's intent takes precedence over generic optimization.

#### Step 3: Description optimization — Combat Undertriggering

Generate an improved `description` field following skill-creator's triggering standard.

The description is the primary mechanism Claude uses to decide whether to invoke a skill. Per skill-creator: "make the skill descriptions a little bit pushy" to combat undertriggering.

Construct the new description with these components:

1. **WHAT** — Clear capability statement (verb-led: "Audit and optimize...", "Generate and validate...")
2. **WHEN** — Specific trigger contexts. Merge in all scenarios from the body's "When to Use" section that are missing from the current description (D6 consistency findings). Include "Use this skill whenever..." or "Triggers on:..." phrasing.
3. **Keywords** — Domain-specific terms that users would naturally say (D6 keyword coverage findings). If the body repeatedly mentions "benchmark", "eval", "grading" but the description doesn't, users who say those words won't trigger the skill.
4. **Near-miss coverage** — Think about what adjacent requests the skill should also handle. Per skill-creator example: "even if they don't explicitly ask for a 'dashboard'."

Present current vs proposed description side by side. The user picks one or edits further.

#### Step 4: Structure & health fixes

Objective fixes applied directly (no subjective judgment):

- **Broken references** → update paths or create missing files (D7-C)
- **Frontmatter** → add missing required fields (D9)
- **Script permissions** → add execute bit to `.sh` files (D10-A)
- **Python packages** → add `__init__.py` for module-style imports (D10-C)
- **Reference TOC** → add table of contents to files > 300 lines (D7-A)
- **Orphaned references** → for each orphan, ask user: delete it or add a pointer from SKILL.md? (D7-B)
- **Safety patterns** → add path validation to destructive commands, add user-confirmation gates to remote execution (D11)
- **Example quality** → trim examples > 30 lines to focus on input/output pairs; add 1-2 concise examples to multi-step skills that have none (D8)

#### Step 5: Diff preview and confirmation

After preparing all changes (Steps 1–4), generate a unified preview before writing any files:

For each file to be modified or created, show:
- Unified-diff style view of removals and additions
- Grouped by the step that produced them (Structure / Instruction / Description / Health)
- A brief rationale for each change

Present to the user: "Apply these changes? (yes to apply all / partial to select which changes / no to cancel)"

#### Step 6: Apply and summarize

Write all confirmed changes. Print a change summary:
- Files modified, files created, files deleted
- Lines removed / added
- Instructions improved (count)
- Description: changed or unchanged

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
| 3 | Cond. content | warning | 3 domain branches (React/Vue/Angular) each >20 lines — candidate for domain-variant pattern | SKILL.md L120-195 |
| 4 | Redundancy | warning | Resume table appears in both §Error Recovery and §Resume Support | SKILL.md L398, L462 |
| 5 | Instr. style | warning | "ALWAYS use report_final.docx" — over-specific, should generalize to match user's input | SKILL.md L47 |
| 6 | Desc. triggering | warning | "When to Use" lists "before publishing" but description doesn't mention publishing | SKILL.md frontmatter |
| 7 | Ref. health | error | references/planning-guide.md — 361 lines, no TOC | references/ |
| 8 | Examples | info | No examples for multi-step workflow — consider adding 1-2 concise examples | SKILL.md |
| 9 | Frontmatter | error | `name` field is "my-skill" but directory is "data-processor" | SKILL.md frontmatter |
| 10 | Script health | warning | scripts/transform.sh lacks execute permission | scripts/ |
| 11 | Safety | warning | `rm -rf $OUTPUT_DIR` without path validation | scripts/cleanup.sh L12 |
| ... | | | | |

## Reference / Script / Asset Health
- references/planning-guide.md — 361 lines, no TOC (warning: >300 lines)
- references/orphan-file.md — not referenced from SKILL.md (warning: orphan)
- scripts/transform.sh — missing execute permission (warning)

## Style Suggestions (manual review)
- S1: Line 47 — "You MUST always validate" → consider: "Always validate output because
  the pipeline rejects malformed JSON, which wastes a full retry cycle."
- S2: Line 83 — "ALWAYS name output `report_final.docx`" → consider: "Name the output
  to match the user's input filename, because downstream tools expect consistency."
- S3: Description field — add trigger phrases from "When to Use" section:
  "before publishing", "quality check"

## Summary
Errors: N | Warnings: N | Info: N | Style: N
Estimated line reduction: ~N lines
```

---

## Resource Reference

Audit criteria details are in `references/audit-criteria.md`. Load it at the start of Phase 1 — it contains the per-dimension rubrics (thresholds, detection methods, false positive guidance) that this file intentionally does not repeat.
