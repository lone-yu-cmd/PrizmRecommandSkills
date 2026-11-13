---
name: "skill-reviewer"
description: "Static, read-only audit of a skill's SKILL.md and bundled files, producing a severity-ranked report without editing anything. Covers 17 dimensions: body size, progressive disclosure, conditional content, redundancy, instruction style, description triggering, reference/script health, safety, examples, and readability. Use this skill whenever someone asks to review, audit, lint, inspect, or diagnose a skill; asks whether a skill is well-written or follows best practices; or wants a documented quality report before publishing. Triggers on: 'review skill', 'audit skill', 'skill lint', 'skill health check', 'check skill quality', 'is this skill well-written', 'diagnose this skill'. This skill reports only — it never edits, restructures, or rewrites files."
---

# Skill Reviewer

Read-only audit of one skill directory. Reads the skill, judges it against 17 fixed dimensions, and returns a severity-ranked report.

Two things it deliberately does not do, because doing them silently is what makes audit reports untrustworthy: it never writes to the target skill, and it never claims a skill behaves well — only that its text is sound. Structure and behavior are different questions, and this skill answers one of them.

### When to use

- "Review this skill", "audit it", "is it well-written", "lint it"
- A check before publishing or handing a skill to someone else
- A check after a large edit, to see what the edit broke structurally
- Diagnosing why a skill triggers poorly or feels bloated

### Invocation

The user gives a skill directory or a path to a SKILL.md, and may optionally name the dimensions to run. Naming dimensions is natural language, not flags: "just check the description and the reference health" runs `description-triggering` and `reference-health` only. With no names, run all 17.

---

## Process

### Step 1 — Load the target

Resolve the path to its SKILL.md and read it fully. Then read every file under the target's `references/`, `scripts/`, `assets/`, and `agents/` directories if they exist — a body that looks clean can be an index pointing at four orphaned files, and you cannot see that from SKILL.md alone.

Record: total lines, bucket sizes, list of every file with line counts, and every path the body mentions.

### Step 2 — Load the rubrics

Read this skill's `references/audit-criteria.md`. It carries the per-dimension thresholds, detection methods, and false-positive guidance. The dimension list below says what to look at; the reference says when it counts as a finding.

### Step 3 — Audit the 17 dimensions

Use the slug, not a number, when you cite a dimension in the report — numbers shift the moment someone inserts a dimension, and an author reading "D7" has to go count headings.

1. `body-size` — line count against the 500-line budget
2. `progressive-disclosure` — is each block at the right loading level: flow control in the body, procedural detail in `references/`, deterministic work in `scripts/`
3. `conditional-content` — low-frequency content loading unconditionally; framework/platform branches that should be one reference file each
4. `redundancy` — the same concept in two sections, body repeating the description, body and reference overlapping
5. `instruction-style` — MUST/NEVER density without rationale, imperative form, over-specific rules that stop the model from generalizing, contradictions
6. `description-triggering` — does the description state what and when, is it pushy enough, does it cover the body's "when to use" scenarios and core domain terms
7. `reference-health` — files over 300 lines without a table of contents, orphans, paths in the body that do not exist
8. `examples` — realistic input/output pairs versus token-heavy demonstrations of the obvious
9. `frontmatter` — required fields present, YAML parses, `name` matches the directory
10. `script-health` — executability, orphaned scripts, Python packages missing `__init__.py`
11. `safety` — destructive commands, remote code execution, exfiltration patterns, unguarded writes
12. `diagram` — workflow rendered as ASCII trees where a numbered list would carry the same meaning
13. `visual-noise` — emoji, decorative bold, HTML, separator art that costs tokens without adding meaning
14. `referencing` — "see above" instead of "see §Phase 2 Step 3"
15. `heading-depth` — headings nested deeper than four levels
16. `chunking` — dense 100+ word paragraphs, tables wide enough that column alignment is lost
17. `pronoun-clarity` — "it" and "this" with more than one plausible referent

Severity ladder, applied consistently:

- **error** — the skill cannot work as written (broken path, mismatched name, contradicting instructions)
- **warning** — it works but degrades: wasted context, unreliable triggering, instructions the model will misread
- **info** — an improvement worth making but not worth blocking on
- **style** — subjective; the author decides

When `audit-criteria.md` says a case is a common false positive, drop the finding. A report full of noise teaches the author to ignore reports.

### Step 4 — Write the report

Read-only: no file is created or modified, including no report file. Deliver in conversation. Three data columns, not five — the rubric that flags wide tables applies to this template too.

```markdown
# Skill Review Report
Skill: <name> ・ Path: <absolute path> ・ Lines: N/500 ・ Files: N

## Findings

| Finding | Evidence | Severity |
|---------|----------|----------|
| Body is 413 lines with a 67-line error-recovery section inlined | SKILL.md L345-411 | warning |
| Description omits "before publishing" although §When to use lists it | SKILL.md frontmatter | warning |
| `name` is "my-skill", directory is "data-processor" | SKILL.md frontmatter | error |

## Resource Health
- references/planning-guide.md — 361 lines, no table of contents (warning)
- references/legacy-notes.md — never referenced from the body (warning: orphan)
- scripts/transform.sh — not executable (warning)

## Style Suggestions
Subjective rewording, kept out of the table so the author can ignore it wholesale.
- L47 "You MUST always validate" → "Validate before returning, because the pipeline drops malformed JSON and the user sees the failure much later."
- Description → add the trigger phrases the body already knows: "before publishing", "quality check".

## Summary
Errors N ・ Warnings N ・ Info N ・ Style N
Body could shrink by ~N lines by extracting L345-411 and L120-195.

## Not checked
Behavior. No prompt was run, no eval executed. If evals/ exists, it was not run.
```

Rules that keep the report usable:

- Every row carries a location. A finding without one cannot be verified and will be dismissed.
- Quote the offending text when the finding is about wording; the author should not have to grep for it.
- Estimate the line reduction for extraction findings — the author needs to know whether the work is worth it.
- Close with an honest coverage line: which dimensions ran, which were skipped and why, what stayed unread.
- If the skill is genuinely clean, say so in one line and stop. Inventing findings to look thorough is the failure mode of audit tools.

---

## Failure modes this skill exists to avoid

- Writing the report to a file, or "helpfully" applying a fix mid-audit — the author asked for a diagnosis, and a surprise edit destroys the diff they wanted to review.
- Reporting structure as if it were behavior: "PASS" on a skill whose instructions are subtly wrong. Static checks cannot see that; the report has to say so.
- Padding with false positives. Three real findings beat twenty, and the twenty teach the author to skim.
- Judging against personal taste and filing it as `error`. Taste belongs in Style Suggestions.
- Numbering dimensions in the output. Use the slug.

---

## Resources

- `references/audit-criteria.md` — per-dimension rubrics: thresholds, detection methods, false-positive guidance. Load it in Step 2; the 17-line list in the body is a table of contents, not the criteria.
