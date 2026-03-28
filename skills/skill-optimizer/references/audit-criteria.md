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

**Common false positives**: Section headers like "## Hard Rule" that use strong language for legitimate guardrails (scope boundaries, safety constraints) are acceptable. The issue is when MUST is used for stylistic preferences or minor operational details.

## 6. Description Triggering

**What to measure**: Whether the `description` frontmatter field effectively communicates both WHAT the skill does and WHEN to use it. Per skill-creator guidelines, descriptions should be slightly "pushy" to combat undertriggering.

**Warning threshold**: Description only describes capability ("Generates a report") without any trigger context ("Use when...", "Triggers on...").

**Error threshold**: Description is a single generic sentence with no specificity about use cases or trigger phrases.

**How to detect**: Parse the description field. Check for: (a) at least one verb describing output/capability, (b) at least one trigger phrase or usage context, (c) length — very short descriptions (< 20 words) are usually too vague. Also check if the description includes domain-specific keywords that users would naturally use.

**Common false positives**: Some skills are genuinely narrow in scope and a concise description is appropriate. Don't flag brevity alone — flag lack of trigger context.

## 7. Reference File Health

**What to measure**: Three sub-checks for the skill's `references/` directory.

**Sub-check A — Oversized files**: Reference files > 300 lines without a table of contents (TOC).
- Error threshold: > 300 lines, no heading that resembles a TOC.
- How to detect: Count lines; search for "Table of Contents", "TOC", or a list of `[anchor links]` near the top.

**Sub-check B — Orphan files**: Files in `references/` that are never mentioned in SKILL.md.
- Warning threshold: Any file not referenced.
- How to detect: List all files in `references/`. For each, search SKILL.md for the filename. If no match, it's an orphan.

**Sub-check C — Broken references**: SKILL.md mentions a reference file path that doesn't exist on disk.
- Error threshold: Any broken reference.
- How to detect: Extract all file paths from SKILL.md that point to `references/` (or equivalent relative paths). Check each exists.

**Common false positives**: Files in `assets/` or `scripts/` that are invoked by commands (not loaded as context) may not appear literally in SKILL.md — they might be referenced via a script argument. Only flag `references/` orphans, since those are meant to be read into context.

## 8. Example Effectiveness

**What to measure**: Whether examples in SKILL.md help the model understand usage patterns or just consume tokens.

**Warning threshold**: An example block > 30 lines. Or an example that restates the instructions without adding concrete input/output illustration.

**Info threshold**: A skill with multi-step workflow phases but no examples at all — adding 1-2 concise examples would help.

**How to detect**: Find fenced code blocks or sections labeled "Example". Measure their length. Assess whether they show realistic, non-trivial usage (concrete inputs/outputs) vs trivially obvious cases ("run command X" → "output: success"). Also check if examples are outdated (referencing features or formats that don't match the current instructions).

**Common false positives**: Output format templates (showing the exact report structure to generate) look like examples but are actually specifications. Don't flag those — they're necessary reference material.
