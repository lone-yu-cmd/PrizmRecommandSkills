---
name: "skill-reviewer"
description: "Static audit of SKILL.md files against skill-creator writing standards. Use this skill whenever someone wants to review skill quality, check a skill's health, audit a skill before publishing, verify a skill follows best practices, or diagnose issues with a skill's structure, description, or instructions. Triggers on: 'review skill', 'audit skill', 'check skill quality', 'skill health check', 'diagnose skill', 'is this skill well-written', 'skill lint'."
---

# Skill Reviewer

Read-only static audit of any skill against skill-creator writing standards. Evaluates 17 dimensions — body size, progressive disclosure, redundancy, instruction style, description triggering, reference health, safety patterns, and more — and produces a diagnostic report without modifying any files.

The audit criteria come from skill-creator's own guidelines — this skill doesn't invent new rules, it enforces the existing ones.

### When to Use
- "Review this skill", "audit skill quality", "skill health check"
- Check if a skill follows skill-creator best practices
- Before publishing or sharing a skill
- After major edits to a skill, as a quality gate
- Diagnosing why a skill triggers poorly or feels bloated
- Feeding results into skill-optimizer for automated refactoring

### `/skill-reviewer` \<path-to-skill-directory\> [--dimensions N,N,...]

Accepts either a skill directory path or a direct path to a SKILL.md file.

`--dimensions`: Run only the specified dimensions (comma-separated numbers, e.g., `--dimensions 5,6,9`). Useful for targeted checks after editing a specific aspect. Default: all 17 dimensions.

---

## Audit Process

#### Step 1: Locate and load target skill

Resolve the target path to find SKILL.md. Read it fully. Also read all files under the skill's `references/`, `assets/`, and `scripts/` directories (if they exist) to understand the full skill structure.

#### Step 2: Load audit criteria

Read `references/audit-criteria.md` from this skill's directory (skill-reviewer's own references, not the target skill's). This contains the detailed rubrics for each dimension — thresholds, detection methods, false positive guidance.

#### Step 3: Run 17-dimension audit

Evaluate the target skill against these dimensions (detailed criteria in the reference file):

1. **Body size** — line count vs 500-line budget
2. **Progressive disclosure** — is content at the right loading level? Flow-control logic belongs in SKILL.md body; procedural details (error tables, format specs, sub-procedures > 15 lines) belong in references/; deterministic operations belong in scripts/
3. **Conditional content** — low-frequency content loading unconditionally; domain-variant branches that should be separate reference files
4. **Internal redundancy** — repeated content across sections, description/body overlap, content duplicated between SKILL.md and reference files
5. **Instruction style** — MUST/NEVER overuse vs explaining rationale; over-specificity/overfitting of instructions to narrow examples
6. **Description triggering** — pushy enough? covers what + when-to-use? consistent with body's "When to Use" section? keyword coverage of core domain terms?
7. **Reference file health** — oversized files without TOC, orphan files, broken references (including scripts/ and assets/ paths)
8. **Example effectiveness** — helpful vs token-consuming; realistic input/output pairs vs trivially obvious cases
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

Output the report to conversation using the format in **Output Format** below. This is a read-only operation — do NOT write to any file or modify the target skill.

---

## Output Format

```markdown
# Skill Review Report
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

### Report Guidelines

- **Be specific**: cite line numbers, section names, and quote the problematic text
- **Be actionable**: each finding should make it clear what to fix and why
- **Avoid false positives**: use the false positive guidance in audit-criteria.md before flagging
- **Style suggestions are separate**: put subjective rewording suggestions in the Style Suggestions section, not in the main findings table — the skill author decides whether to adopt them
- **Estimate line reduction**: sum up the lines of content flagged for extraction to references/ — this gives the author a sense of how much the body could shrink

---

## Pipeline Integration

skill-reviewer is designed to feed into skill-optimizer. The typical workflow:

1. Run `skill-reviewer` to get the diagnostic report
2. Review findings and decide which to address
3. Run `skill-optimizer` to refactor (it will run its own diagnosis as part of Phase 1, but having reviewed the report upfront helps the author make informed decisions about which refactorings to approve)

skill-reviewer can also be used standalone as a quality gate — run it before publishing a skill, after major edits, or as part of a review checklist.

---

## Resource Reference

Audit criteria details are in `references/audit-criteria.md`. Load it at the start of the audit process — it contains the per-dimension rubrics (thresholds, detection methods, false positive guidance) that this file intentionally does not repeat.
