# Writing Standards Reference

Standards for writing skill content, extracted from skill-creator's guidelines. Load this file when the enhancement involves adding or expanding SKILL.md sections or examples.

## Table of Contents
1. [Progressive Disclosure](#1-progressive-disclosure)
2. [Line Budget](#2-line-budget)
3. [Writing Style](#3-writing-style)
4. [Section Organization](#4-section-organization)
5. [Example Writing](#5-example-writing)
6. [Output Format Definitions](#6-output-format-definitions)
7. [Description Field](#7-description-field)

---

## 1. Progressive Disclosure

Skills use a three-level loading system. Understanding where content belongs is the most important structural decision.

### Level 1: Metadata (name + description)
- Always in context, roughly 100 words
- The `description` field is the primary triggering mechanism — Claude decides whether to invoke a skill based on this
- Include both WHAT the skill does AND WHEN to use it
- All trigger context goes here, not in the body

### Level 2: SKILL.md body (<500 lines ideal)
- Loaded whenever the skill triggers
- Contains flow-control logic: decisions, routing, gates, phase structure
- Contains the "what" and "when" of each step
- The model should be able to follow the skill's workflow by reading only SKILL.md

### Level 3: Bundled resources (unlimited)
- **references/**: Docs loaded into context on specific branches. For procedural details the model needs only sometimes — error tables, format specs, detailed sub-procedures.
- **scripts/**: Executable code for deterministic or repetitive tasks. Scripts can run without being loaded into context.
- **agents/**: Instructions for specialized subagents, loaded only when spawning that agent.
- **assets/**: Files used in output (templates, icons, fonts). Not loaded into context.

### Decision rule
For each piece of content, ask: "Does the model need this every time the skill triggers, or only when a specific branch is taken?"

- Every time → SKILL.md body (Level 2)
- Specific branch only → references/ (Level 3)
- Can be executed mechanically → scripts/ (Level 3)
- Needed for subagent work → agents/ (Level 3)

### Conditional pointer pattern
When content is placed at Level 3, SKILL.md must contain a conditional pointer that states *when* to load it — not just a path, but the condition:

Good: "Read `references/error-recovery.md` when a validation error occurs in Step 3."
Bad: "See `references/error-recovery.md` for details."

The condition helps the model know when to load the file, saving tokens in sessions where that branch isn't taken.

---

## 2. Line Budget

### The 500-line target
SKILL.md body should stay under 500 lines. This is a guideline, not a hard wall — going slightly over for good reason is fine. But skills approaching this limit tend to cross it after a few iterations of additions.

### What counts
Total line count including blank lines and frontmatter. But context matters: a file with 450 lines and 100 blank lines is less concerning than 450 lines of dense instruction.

### When approaching the limit
If adding content would push SKILL.md past 500 lines:
1. Identify procedural sections (>15 lines) that only apply to specific branches
2. Extract them to reference files with conditional pointers
3. Keep the flow-control summary in SKILL.md

### Show the math
When proposing changes, always show: current lines + estimated addition = total. If splitting is needed, show how: "Extract ~80 lines to references/, keeping a 20-line summary, net +20 in SKILL.md."

---

## 3. Writing Style

### Explain the why
The most important writing principle. Today's LLMs are smart — they have good theory of mind and respond better to well-reasoned guidance than to rigid commands. When writing instructions:

- **Prefer**: "Validate the output as JSON before returning, because the downstream pipeline silently drops malformed payloads and the user won't see an error until much later."
- **Avoid**: "ALWAYS validate JSON output."

The first version gives the model enough context to make good decisions even in edge cases the instruction didn't anticipate. The second version is a brittle rule that the model follows mechanically.

### When MUST/ALWAYS is appropriate
Strong directives are appropriate for genuine guardrails — safety constraints, scope boundaries, hard requirements where deviation causes real damage. They're a yellow flag when used for stylistic preferences or minor operational details.

The test: if the model deviates from this instruction, does something actually break? If yes, a strong directive is justified. If no, explain the preference and let the model exercise judgment.

### Imperative form
Start instructions with verbs: "Read the file", "Generate the report", "Check each assertion". Not: "The file should be read", "A report is to be generated."

### Generalize, don't overfit
Instructions should describe the general principle, not a single scenario. When you find yourself writing a specific filename, column name, or format string, step back and ask: is the skill meant to handle only this one case?

- **Overfit**: "ALWAYS name output `report_final.docx`"
- **General**: "Name the output to match the user's input filename — downstream tools expect filename consistency."

### Tone matching
New content should match the existing skill's tone. If the skill uses a conversational, friendly style, don't add a section in formal academic prose. If it uses precise technical language, don't add casual commentary.

---

## 4. Section Organization

### Domain-first, not alphabetical
When a skill supports multiple domains or frameworks, organize by domain variant rather than by function:

```
skill-name/
├── SKILL.md (workflow + domain selection logic)
└── references/
    ├── react.md
    ├── vue.md
    └── angular.md
```

The model reads only the relevant domain's reference file, saving tokens on the others.

### Phase/step structure
Skills with multi-step workflows typically organize as numbered phases with lettered or numbered steps within each phase. New sections should follow the existing numbering pattern — don't introduce a different scheme.

### Section sizing
A section in SKILL.md that exceeds 30 lines of procedural content is a candidate for extraction. Sections of 15-30 procedural lines are borderline — extract if the content is only needed on a specific branch.

Flow-control content (decision trees, phase descriptions, routing logic) can be longer without extraction because the model references it every session.

---

## 5. Example Writing

### When to add examples
Examples help when the skill has a non-obvious output format or a multi-step transformation where the model might get confused. They're less useful for straightforward operations.

### Effective examples
- Show realistic, non-trivial input/output pairs
- Keep individual examples under 30 lines
- Focus on the transformation — what the input looks like, what the output should look like, and why
- Use the `Input/Output` or `Before/After` pattern unless the skill's domain suggests a different framing

### Formatting
```markdown
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

Or for more complex examples with context:
```markdown
**Example: Handling a multi-file skill**
Given a skill directory with:
- SKILL.md (420 lines)
- references/api-spec.md (150 lines)

The enhancement adds a "Validation" section...
```

### Token awareness
Examples consume tokens every time the skill triggers. A 50-line example block that only clarifies one edge case is an expensive way to handle that edge case. Consider whether a 2-line explanation would be just as effective.

---

## 6. Output Format Definitions

When a skill defines a specific output format (report structure, JSON schema, markdown template), treat it as a specification, not an example:

```markdown
## Report structure
Use this template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

This is not an example to be varied — it's a format to be followed. When adding output format definitions, mark them clearly as templates or required structures.

---

## 7. Description Field

### Structure
A good description has three components:
1. **WHAT** — Verb-led capability statement: "Audit and refactor...", "Generate and validate..."
2. **WHEN** — Specific trigger contexts: "Use this skill whenever...", "Triggers on:..."
3. **Keywords** — Domain-specific terms users would naturally say

### Combat undertriggering
Per skill-creator: descriptions should be slightly "pushy." Claude tends to undertrigger skills — not using them when they'd be useful. Include trigger phrases that cover near-miss scenarios:

"Use this skill whenever someone wants to add content to a skill, even if they just say 'this skill needs more' or describe a specific section they want without using the word 'enhance'."

### When to update
If an enhancement changes the skill's capabilities — adding a new mode, new output type, or new domain — the description may need updating. Flag this during verification but don't auto-modify, because description changes affect triggering behavior across all future invocations.
