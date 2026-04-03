# Structure Patterns Reference

Standards for organizing skill directories — reference files, agents, scripts, and assets. Load this file when the enhancement involves creating new files outside SKILL.md.

## Table of Contents
1. [Skill Directory Anatomy](#1-skill-directory-anatomy)
2. [Reference Files](#2-reference-files)
3. [Agent Files](#3-agent-files)
4. [Script Files](#4-script-files)
5. [Asset Files](#5-asset-files)
6. [Domain-Variant Pattern](#6-domain-variant-pattern)
7. [Naming Conventions](#7-naming-conventions)

---

## 1. Skill Directory Anatomy

The standard skill directory structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
├── references/    (optional) - Docs loaded into context as needed
├── agents/        (optional) - Subagent instruction files
├── scripts/       (optional) - Executable code for deterministic tasks
└── assets/        (optional) - Files used in output (templates, icons, fonts)
```

Only create directories that the skill actually needs. An empty `scripts/` directory with no scripts is clutter.

---

## 2. Reference Files

### Purpose
Reference files hold content the model needs on specific branches but not every invocation. They reduce SKILL.md's token cost for the common case while keeping detailed information available when needed.

### When to create a reference file
- Procedural detail (error tables, format specs, lookup tables) exceeding 15 lines
- Content gated by a condition ("if validation fails", "when dealing with framework X")
- Detailed rubrics or criteria that would bloat the main workflow
- Documentation that the model reads once during a specific phase, not continuously

### How to structure
- **Clear section headers** so the model can navigate to the relevant part without reading the entire file
- **Table of contents** if the file exceeds 300 lines — a list of anchor links near the top
- **Self-contained sections** — each section should make sense on its own, because the model may read just that section

### How to reference from SKILL.md
Include a conditional pointer that tells the model both *what* the file contains and *when* to load it:

```markdown
Read `references/error-recovery.md` when a validation error occurs in Step 3 —
it contains the error code table and recovery procedures for each error type.
```

A bare "see references/foo.md" without a condition wastes the model's decision-making — it doesn't know whether to load the file now or later.

### Avoiding duplication
Before creating a new reference file, check if the content belongs in an existing one. Merging related content into one file is better than creating many small files — each file load has overhead, and related content benefits from proximity.

If extracted content was already partially present in an existing reference file, consolidate rather than duplicate.

---

## 3. Agent Files

### Purpose
Agent files define the role, behavior, and evaluation criteria for specialized subagents. They live in `agents/` and are loaded only when the skill spawns that agent.

### Standard structure
Based on the patterns in existing agent files (grader.md, comparator.md, analyzer.md):

```markdown
# [Agent Name]

[1-2 sentence role description]

## Your Task
[What the agent does, step by step]

## Inputs
[What the agent receives — files, data, context]

## Output Format
[Exact structure of what the agent produces]

## Evaluation Criteria
[How to judge quality — what counts as good/bad output]

## Edge Cases
[How to handle ambiguous or unusual situations]
```

### Key principles
- **Self-contained** — the agent should be able to do its job without reading SKILL.md. Include all necessary context in the agent file.
- **Focused** — one agent, one clear responsibility. If an agent is doing two unrelated things, consider splitting it.
- **Output-oriented** — clearly define what the agent produces. Vague outputs lead to inconsistent results.

### How to reference from SKILL.md
```markdown
Spawn a grader subagent. Read `agents/grader.md` for the grading protocol
and pass it the outputs from Step 4.
```

---

## 4. Script Files

### Purpose
Scripts handle deterministic or repetitive operations — tasks that benefit from being written once and executed consistently rather than re-derived by the model each time.

### When to create a script
The clearest signal: if the model would independently write similar helper code across multiple test cases. Per skill-creator: "if all test cases resulted in the subagent writing a similar helper script, that's a strong signal the skill should bundle that script."

Also create scripts for:
- Data transformations with fixed logic
- File format conversions
- Aggregation and reporting
- Validation checks that can be automated

### Requirements
- **Shell scripts (.sh)**: Must have execute permission (`chmod +x`). Include a shebang line (`#!/bin/bash` or `#!/usr/bin/env bash`).
- **Python scripts (.py)**: Include a docstring explaining purpose and usage. If the directory uses module-style imports (`python -m scripts.foo`), ensure `__init__.py` exists.
- **Comment header**: Every script should start with a comment explaining what it does and how to invoke it.

### How to reference from SKILL.md
```markdown
Run the aggregation script to combine results:
\`\`\`bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
\`\`\`
```

Scripts can be invoked without loading their contents into context — the model just needs to know the command and arguments.

---

## 5. Asset Files

### Purpose
Assets are files used in the skill's output — HTML templates, icons, fonts, configuration templates. They're not loaded into the model's context; they're copied, transformed, or referenced during output generation.

### When to create an asset
- HTML/CSS templates that the skill fills with dynamic content
- Configuration file templates
- Image files used in generated output
- Any file that's used as-is or with minimal transformation

### How to reference from SKILL.md
Assets are typically referenced in script invocations or inline instructions:
```markdown
Read the template from `assets/eval_review.html` and replace the placeholders.
```

---

## 6. Domain-Variant Pattern

When a skill supports multiple frameworks, platforms, or domains and each variant has substantial content (>15 lines), organize as one reference file per variant:

```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

SKILL.md contains only the selection logic — how to determine which variant applies and a pointer to the relevant reference file. The model loads only the reference it needs, saving tokens on the others.

This pattern is appropriate when:
- Each variant has >15 lines of unique content
- The variants share a common workflow but differ in implementation details
- The number of variants may grow over time

It's overkill when:
- Variants are short (<15 lines each) — just keep them inline
- There are only 2 variants with small differences — a simple if/else in SKILL.md is clearer

---

## 7. Naming Conventions

### Files
- Use lowercase with hyphens: `error-recovery.md`, `grader.md`, `aggregate_benchmark.py`
- Reference files: descriptive names that hint at content — `audit-criteria.md`, `eval-schemas.md`
- Agent files: role-based names — `grader.md`, `comparator.md`, `analyzer.md`
- Script files: action-based names — `run_eval.py`, `package_skill.py`, `generate_report.py`

### Directories
- Standard names: `references/`, `agents/`, `scripts/`, `assets/`
- Don't invent new top-level directories unless there's a clear reason — stick to the standard four

### SKILL.md frontmatter
- `name` must match the skill's directory name (case-insensitive)
- `description` should be a complete sentence or paragraph, not a fragment
