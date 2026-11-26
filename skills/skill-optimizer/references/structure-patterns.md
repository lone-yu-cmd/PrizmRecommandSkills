# Structure Patterns Reference

Standards for organizing skill directories — reference files, agents, scripts, and assets. Load this file in Phase 1 or Phase 2 whenever adding or extracting files outside `SKILL.md` or splitting domain variants.

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

```text
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
├── references/    (optional) - Docs loaded into context on specific branches
├── agents/        (optional) - Subagent instruction files
├── scripts/       (optional) - Executable code for deterministic tasks
└── assets/        (optional) - Output templates, icons, fonts
```

Only create directories the skill actually uses; an empty `scripts/` directory is clutter.

---

## 2. Reference Files

### When to create
- Procedural details (error tables, format specs, lookup tables) exceeding 15 lines
- Content gated by a condition (`"if validation fails"`, `"when handling framework X"`)
- Detailed rubrics or criteria that would bloat the main workflow
- Phase-specific guidance read once rather than continuously

### How to structure
- **Clear section headers** so the model can jump straight to the needed section
- **Table of contents** near the top if the file exceeds 300 lines (anchor links to top-level sections)
- **Self-contained sections** that make sense on their own when read selectively

For conditional pointer wording and merging into existing files instead of creating thin files, follow `references/rewrite-playbook.md` §2.

---

## 3. Agent Files

Agent files define the role, workflow, and criteria for specialized subagents under `agents/` and are loaded only when spawning that agent.

### Standard structure

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
- **Self-contained** — the agent must be able to run without reading `SKILL.md`
- **Focused** — one agent, one clear responsibility; split unrelated duties
- **Output-oriented** — specify exact output structure to prevent drift

### Referencing from SKILL.md

```markdown
Spawn a grader subagent. Read `agents/grader.md` for the grading protocol
and pass it the outputs from Step 4.
```

---

## 4. Script Files

Scripts handle deterministic or repetitive tasks that are cheaper and more reliable to run than to re-derive in prose.

### When to create
Create a script when the model would otherwise write similar helper code across runs — fixed data transforms, format conversions, benchmark aggregation, or automated validation checks.

### Requirements
- **Shell scripts (`.sh`)**: Must have execute permission (`chmod +x`) and a shebang (`#!/bin/bash` or `#!/usr/bin/env bash`).
- **Python scripts (`.py`)**: Include a module docstring explaining purpose and usage; add `__init__.py` if invoked via module imports (`python -m scripts.foo`).
- **Comment header**: Start every script with a concise comment explaining what it does and how to invoke it.

### Referencing from SKILL.md

````markdown
```markdown
Run the aggregation script to combine results:
```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```
```
````

Scripts can execute without loading their source into context — `SKILL.md` only needs the command, arguments, and when to run it.

---

## 5. Asset Files

Assets (`assets/`) are files consumed by output generation — HTML/CSS templates, configuration templates, icons, fonts — copied or filled with minimal transformation rather than loaded as instructions.

### Referencing from SKILL.md

```markdown
Read the template from `assets/eval_review.html` and replace the placeholders.
```

---

## 6. Domain-Variant Pattern

When a skill supports multiple frameworks, clouds, or domains and each variant exceeds 15 lines of unique detail, organize one reference file per variant:

```text
cloud-deploy/
├── SKILL.md (workflow + variant selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Keep only the selection logic and conditional pointers in `SKILL.md` so the model loads just the active variant. Keep variants inline in `SKILL.md` when each is under 15 lines or when there are only two small variants.

---

## 7. Naming Conventions

### Files
- Lowercase with hyphens for docs/agents: `error-recovery.md`, `audit-criteria.md`, `grader.md`, `comparator.md`, `analyzer.md`
- Action-based names for scripts: `run_eval.py`, `package_skill.py`, `generate_report.py`

### Directories
- Stick to the standard four: `references/`, `agents/`, `scripts/`, `assets/`

### SKILL.md frontmatter
- `name` must match the skill's directory name (case-insensitive)
- `description` must read as complete sentences, not fragmented keywords
