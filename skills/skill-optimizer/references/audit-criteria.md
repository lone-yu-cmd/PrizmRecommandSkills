# Audit Criteria Reference

Detailed rubrics for each audit dimension. Load this file at the start of Phase 1 diagnosis.

## Table of Contents
1. [Body Size](#1-body-size)
2. [Progressive Disclosure](#2-progressive-disclosure)
3. [Conditional Content](#3-conditional-content)
4. [Internal Redundancy](#4-internal-redundancy)
5. [Instruction Style](#5-instruction-style)
6. [Description Triggering](#6-description-triggering)
7. [Reference File Health](#7-reference-file-health)
8. [Example Effectiveness](#8-example-effectiveness)
9. [Frontmatter Completeness](#9-frontmatter-completeness)
10. [Script & Asset Health](#10-script--asset-health)
11. [Safety Patterns](#11-safety-patterns)

---

## 1. Body Size

**What to measure**: Total line count of SKILL.md (including blank lines and frontmatter).

**Error threshold**: > 500 lines.

**Warning threshold**: > 400 lines. Skills approaching the limit tend to cross it after a few iterations of feature additions.

**How to detect**: Count lines with `wc -l`. Separately count structural lines (blank lines, headers, frontmatter) vs content lines for context — a file with 450 lines but 100 blank lines is less concerning.

**Common false positives**: Skills with large fenced code blocks (output templates, examples) may appear long but the fenced content is dense reference material. Judge by whether the non-fenced content alone approaches the limit.

## 2. Progressive Disclosure

**What to measure**: Whether content is placed at the correct loading level. Flow-control logic (decisions, routing, gates) belongs in SKILL.md. Procedural details (error tables, format specs, step-by-step sub-procedures) belong in `references/`. Deterministic or repetitive operations belong in `scripts/`.

**Error threshold**: A section longer than 30 lines that is purely procedural (lookup tables, decision trees with fixed outcomes, format specifications) sitting in SKILL.md body.

**Warning threshold**: A section of 15-30 procedural lines in the body, or a section that mixes flow-control and procedural detail that could be cleanly separated.

**How to detect**: For each section in SKILL.md, ask: "Does the model need this content every time the skill triggers, or only when a specific branch is taken?" If the answer is "specific branch only" and the section exceeds 15 lines, it's a candidate for extraction.

**Common false positives**: Checkpoint tables and phase lists look procedural but are flow-control — the model references them every session to know what to do next. These should stay in the body.

## 3. Conditional Content

**What to measure**: Content gated by conditions ("if X happens", "when dealing with Y", "most sessions will NOT need this") that loads unconditionally into context.

**Error threshold**: > 30 lines of content that applies to < 30% of invocations, sitting in the SKILL.md body.

**Warning threshold**: 15-30 lines of low-frequency content in the body.

**How to detect**: Scan for phrases like "if validation fails", "when errors occur", "most sessions will NOT", "this is conditional", "only when", "optional". Estimate the invocation frequency of the gated content. If the gate condition triggers in a minority of sessions and the gated block is substantial, flag it.

**Sub-check: Domain organization** — When SKILL.md contains multiple conditional branches for different frameworks/platforms/domains (e.g., `if framework == React`, `if platform == AWS`) and each branch exceeds 15 lines, flag as a candidate for the domain-variant pattern: one reference file per variant, with SKILL.md containing only the selection logic. This is a warning, not an error — small branches are fine inline.

**Common false positives**: Short conditional blocks (< 10 lines) are fine in the body — the overhead of a pointer + file load exceeds the token savings. Also, "if the user says X, do Y" routing logic is flow-control, not conditional content.

## 4. Internal Redundancy

**What to measure**: (a) The same concept explained in two different sections of SKILL.md. (b) Content in the SKILL.md body that substantially repeats the `description` frontmatter field. (c) Content duplicated between SKILL.md and a reference file.

**Error threshold**: Two passages that share 60%+ of their key terms and convey the same instruction.

**Warning threshold**: A paragraph in the body that restates the description field with minor rewording.

**How to detect**: (a) Compare section summaries pairwise — if two sections answer the same question ("when does X happen?"), they may be redundant. (b) Compare the description field against any "When to Use" or introductory section. (c) After extraction, check if any extracted content was already partially present in an existing reference file.

**Common false positives**: A brief "When to Use" section that echoes the description in bullet form is acceptable — it serves as a quick-reference for the model. Only flag if it's a full paragraph reproduction.

## 5. Instruction Style

**What to measure**: Ratio of directive commands (MUST, ALWAYS, NEVER, in capitals) to explanatory instructions. Whether instructions use imperative form.

**Warning threshold**: > 5 capitalized directives per 100 lines without an adjacent rationale ("because", "so that", "this prevents", "the reason is").

**Error threshold**: A MUST directive that contradicts another instruction elsewhere in the same file.

**How to detect**: Count occurrences of MUST, ALWAYS, NEVER, CRITICAL (case-sensitive for capitals). For each occurrence, check if the surrounding 2 lines contain a rationale clause. Also check that instructions start with verbs ("Read...", "Scan...", "Generate...") rather than noun phrases ("The reading of...", "A scan should be...").

**Sub-check: Over-specificity / overfitting** — Instructions that hardcode specific file names, specific user scenarios, particular format strings, or narrow examples as if they were the only use case. Overly specific instructions cause the model to follow them rigidly instead of generalizing to the user's actual context.

- Warning threshold: > 3 instructions that reference concrete filenames, specific column names, exact version numbers, or single-scenario examples where the skill is meant to handle a general class of inputs.
- How to detect: Scan for patterns like quoted file paths (`"report.xlsx"`), hardcoded identifiers, or instructions that read like "the user will provide X in format Y" when the skill should handle multiple formats. Also look for chains of narrow `if/then` rules that could be replaced by a general principle with an explanation of *why*.
- The fix is usually to replace the specific instruction with the general principle + rationale, so the model can adapt: instead of "ALWAYS name output `report_final.docx`", write "Name the output to match the user's input filename, because downstream tools expect filename consistency."

**Common false positives**: Section headers like "## Hard Rule" that use strong language for legitimate guardrails (scope boundaries, safety constraints) are acceptable. The issue is when MUST is used for stylistic preferences or minor operational details. Output format templates that use specific field names as a specification (not an example) are also acceptable.

## 6. Description Triggering

**What to measure**: Whether the `description` frontmatter field effectively communicates both WHAT the skill does and WHEN to use it. Per skill-creator guidelines, descriptions should be slightly "pushy" to combat undertriggering.

**Warning threshold**: Description only describes capability ("Generates a report") without any trigger context ("Use when...", "Triggers on...").

**Error threshold**: Description is a single generic sentence with no specificity about use cases or trigger phrases.

**How to detect**: Parse the description field. Check for: (a) at least one verb describing output/capability, (b) at least one trigger phrase or usage context, (c) length — very short descriptions (< 20 words) are usually too vague. Also check if the description includes domain-specific keywords that users would naturally use.

**Sub-check: "When to Use" consistency** — If SKILL.md body contains a "When to Use" section (or similar: "Usage", "Triggers on"), compare its trigger scenarios against the `description` field. Any scenario listed in "When to Use" but absent from `description` is a triggering gap — the skill body knows when it should fire, but the metadata that Claude uses for routing doesn't reflect it.

- Warning threshold: ≥ 1 trigger scenario in the body's "When to Use" that has no corresponding keyword or phrase in the description.
- How to detect: Extract bullet points or phrases from the "When to Use" section. For each, check if the description contains the same keyword, a synonym, or a semantically equivalent trigger phrase. Flag gaps.
- The fix: add the missing trigger context to the description field so Claude can match on it during routing.

**Sub-check: Keyword coverage** — Scan the SKILL.md body for recurring domain-specific terms (nouns and verbs that appear 3+ times and are not common English words). If a core term is absent from the description, the skill may not trigger when users mention that term.

- Info threshold: ≥ 1 core domain term missing from the description.
- How to detect: Extract content terms from SKILL.md (excluding stop words, markdown syntax, and structural words like "step", "section", "file"). Rank by frequency. Check the top 5-10 terms against the description.

**Common false positives**: Some skills are genuinely narrow in scope and a concise description is appropriate. Don't flag brevity alone — flag lack of trigger context.

## 7. Reference File Health

**What to measure**: Three sub-checks for the skill's `references/` directory.

**Sub-check A — Oversized files**: Reference files > 300 lines without a table of contents (TOC).
- Error threshold: > 300 lines, no heading that resembles a TOC.
- How to detect: Count lines; search for "Table of Contents", "TOC", or a list of `[anchor links]` near the top.

**Sub-check B — Orphan files**: Files in `references/` that are never mentioned in SKILL.md.
- Warning threshold: Any file not referenced.
- How to detect: List all files in `references/`. For each, search SKILL.md for the filename. If no match, it's an orphan.

**Sub-check C — Broken references**: SKILL.md mentions a file path (in `references/`, `scripts/`, or `assets/`) that doesn't exist on disk.
- Error threshold: Any broken reference, regardless of directory.
- How to detect: Extract all file paths from SKILL.md that point to `references/`, `scripts/`, or `assets/` (or equivalent relative paths). Check each exists. A broken pointer to a script is just as much a bug as a broken pointer to a reference doc.

**Common false positives**: Files in `assets/` or `scripts/` that are invoked by commands (not loaded as context) may not appear literally in SKILL.md — they might be referenced via a script argument. For orphan detection, only flag `references/` orphans, since those are meant to be read into context. But for broken reference detection, check all directories — a path that SKILL.md tells the model to use must exist.

## 8. Example Effectiveness

**What to measure**: Whether examples in SKILL.md help the model understand usage patterns or just consume tokens.

**Warning threshold**: An example block > 30 lines. Or an example that restates the instructions without adding concrete input/output illustration.

**Info threshold**: A skill with multi-step workflow phases but no examples at all — adding 1-2 concise examples would help.

**How to detect**: Find fenced code blocks or sections labeled "Example". Measure their length. Assess whether they show realistic, non-trivial usage (concrete inputs/outputs) vs trivially obvious cases ("run command X" → "output: success"). Also check if examples are outdated (referencing features or formats that don't match the current instructions).

**Common false positives**: Output format templates (showing the exact report structure to generate) look like examples but are actually specifications. Don't flag those — they're necessary reference material.

## 9. Frontmatter Completeness

**What to measure**: Whether the YAML frontmatter is well-formed and contains all required fields per skill-creator standards.

**Error threshold**: Missing `name` or `description` field — these are required for the skill to be recognized and triggered.

**Warning threshold**: Any of the following:
- `name` does not match the skill's directory name (causes confusion when installing/referencing)
- `description` is present but empty or contains only whitespace
- YAML frontmatter is malformed (not enclosed in `---` delimiters, invalid YAML syntax)

**How to detect**: Parse the file's first lines for `---` delimiters. Extract the YAML block between them. Validate:
1. `---` appears on line 1
2. A closing `---` appears before the markdown body
3. `name` key exists and is a non-empty string
4. `description` key exists and is a non-empty string
5. `name` value matches the parent directory name (case-insensitive comparison)

**Common false positives**: Some skills use additional frontmatter fields (e.g., `compatibility`, `version`) — these are optional and should not be flagged as unexpected. Only check required fields.

## 10. Script & Asset Health

**What to measure**: Health of the `scripts/` and `assets/` directories, complementing D7's focus on `references/`.

**Sub-check A — Script executability**: Scripts in `scripts/` that are referenced by SKILL.md but lack execute permissions or have syntax issues.
- Warning threshold: A `.sh` file without execute permission. A `.py` file with a syntax error detectable by `python -m py_compile`.
- How to detect: For shell scripts, check `ls -l` for the `x` bit. For Python scripts, run `python -m py_compile` (non-destructive, read-only). Don't run scripts — just check they could run.

**Sub-check B — Orphan scripts/assets**: Files in `scripts/` or `assets/` that are never referenced from SKILL.md or from other reference files.
- Info threshold: Any unreferenced file. This is info, not warning, because scripts/assets may be invoked indirectly (via another script, or by the model at runtime based on judgment).
- How to detect: List all files in `scripts/` and `assets/`. For each, search SKILL.md and all `references/*.md` files for the filename. If no match, flag as potentially orphaned.

**Sub-check C — Python package structure**: If `scripts/` contains Python files imported as modules (e.g., SKILL.md says `python -m scripts.foo`), check that `__init__.py` exists.
- Warning threshold: Module-style invocation without `__init__.py`.
- How to detect: Search SKILL.md for `python -m scripts` patterns. If found, check for `scripts/__init__.py`.

**Common false positives**: Assets like icons, fonts, or template files may be used by generated output rather than loaded by the model — they won't appear in SKILL.md. Flag at info level only, and note "may be used indirectly" in the finding.

## 11. Safety Patterns

**What to measure**: Lightweight scan for patterns that violate skill-creator's "Principle of Lack of Surprise" — a skill's contents should not surprise the user in their intent.

**Warning threshold**: Any of the following patterns appearing in SKILL.md, reference files, or scripts:
- Destructive shell commands: `rm -rf`, `mkfs`, `dd if=`, `> /dev/sd`
- Remote code execution: `curl ... | sh`, `wget ... | bash`, `eval()` on user input
- Credential/data exfiltration: `curl -X POST` with file contents, piping env vars or secrets to external URLs
- Privilege escalation: `chmod 777`, `sudo` without clear context

**Error threshold**: A pattern that is clearly destructive or exfiltrating with no adjacent explanation of why it's safe or necessary.

**How to detect**: Scan all files under the skill directory (SKILL.md, references/, scripts/, assets/) for the patterns listed above using regex matching. For each match, check if the surrounding 3 lines contain an explanation or safety context (e.g., "this is safe because...", "only runs in sandbox", "user must confirm first").

**Common false positives**:
- Documentation or examples that show dangerous commands in fenced code blocks as "what NOT to do" — check if the block is inside a warning/caution section.
- Build scripts that legitimately use `rm -rf` on a temp directory with a well-scoped path (e.g., `rm -rf /tmp/skill-build-*`) — the concern is unscoped `rm -rf /` or `rm -rf $VAR` without validation.
- Skills that are explicitly about security testing or system administration may legitimately contain these patterns. If the skill's description indicates a security/admin domain, reduce severity to info.
