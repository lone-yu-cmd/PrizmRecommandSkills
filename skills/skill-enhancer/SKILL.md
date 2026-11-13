---
name: "skill-enhancer"
description: "Supplement an existing skill with new content: sections, references, agents, scripts, examples, error handling. Additive only — it inserts what is missing and never rewrites or deletes what is already there. Use this skill whenever someone wants to add a section to a skill, supplement a skill with reference docs, agents, or scripts, expand a skill's capabilities, add examples or error handling, enrich a skill, or fill in a gap someone else flagged. Triggers on: 'enhance skill', 'add to skill', 'supplement skill', 'expand skill', 'skill needs more', 'enrich skill content', 'add section to skill', 'add examples to this skill', 'complete this skill'."
---

# Skill Enhancer

Supplement an existing skill with content it does not have yet — sections, references, agents, scripts, examples. The user says what to add; this skill works out where the content belongs and what shape it should take, then writes it after confirmation.

This skill is strictly additive. It inserts content that is missing; it does not refactor, remove, reorganize, or rewrite what is already there, and it does not diagnose problems. Whether a gap is worth filling is the user's call, or the call of whoever flagged it — this skill's job starts once the answer is "add this".

### When to Use
- "Add error handling to this skill", "supplement the evaluation section"
- "This skill needs a grader agent", "add reference docs"
- "Expand the examples", "add a scripts/ directory"
- "The skill is missing X, can you add it?"
- Filling a gap someone else identified
- When extending a skill's capabilities with new content

### `/skill-enhancer` \<path-to-skill\> \<what to add\>

Accepts a skill directory path or a direct path to a SKILL.md file, plus a description of what the user wants to add.

**Examples:**
```
/skill-enhancer skills/report-builder "add a Fix Suggestions section after Output Format"
/skill-enhancer skills/data-validator "add an agents/schema-checker.md"
/skill-enhancer skills/changelog-writer "supplement 2-3 before/after examples in the rewrite step"
```

---

## Phase 1: Understand Intent and Context

### Step 1: Load the target skill

Read the target skill's SKILL.md fully. Also read all files under the skill's `references/`, `agents/`, `scripts/`, and `assets/` directories (if they exist). Build a mental model of what the skill currently does, how it's structured, and where the user's requested content would fit.

### Step 2: Load relevant writing standards

Read the reference files from this skill's directory based on what the user wants to add:

- **Adding a section to SKILL.md** → read `references/writing-standards.md`
- **Adding reference files, agents, or scripts** → read `references/structure-patterns.md`
- **Any enhancement** → read `references/enhancement-checklist.md` (always load this)

These references hold the standards that decide where new content goes and how it is written — loading level, line budget, wording, file structure. Every recommendation this skill makes traces back to a specific rule in one of them, so the author can see why the shape was chosen instead of taking it on trust.

### Step 3: Classify the enhancement type

Determine what category of content the user wants to add:

| Type | Examples | Primary reference |
|------|----------|-------------------|
| **Section** | New phase, error handling, workflow step | writing-standards.md |
| **Reference** | Format spec, lookup table, detailed procedure | structure-patterns.md |
| **Agent** | Grader, comparator, specialized subagent | structure-patterns.md |
| **Script** | Automation, deterministic operation, helper tool | structure-patterns.md |
| **Example** | Input/output pairs, usage demonstrations | writing-standards.md |
| **Mixed** | Combination of the above | both references |

---

## Phase 2: Plan the Enhancement

### Step 1: Determine where the content belongs

Place new content at the appropriate level using the progressive disclosure principle. Read `references/writing-standards.md` §1 (Progressive Disclosure) for the decision rule and examples — it covers which content belongs in SKILL.md body vs `references/` vs `scripts/` vs `agents/`.

When the user asks to "add a section" but the content is procedural and would push SKILL.md over its line budget, recommend splitting: a brief routing pointer in SKILL.md, with details in a reference file.

### Step 2: Check the line budget

Read `references/writing-standards.md` §2 (Line Budget) for the 500-line target and splitting strategy. Count the current SKILL.md line count, estimate the addition, and show the math in the plan.

### Step 3: Draft the enhancement plan

Generate a plan that shows exactly what will change. The plan has four parts:

**User Intent** — Restate what the user asked for to confirm understanding.

**Standards Reference** — Which standard from which reference file applies, and what it says. This makes the reasoning transparent — the user can see why you're recommending a particular structure.

**Change Plan** — A table of file-level changes:

```markdown
| # | Change Type | File Path | Description |
|---|------------|-----------|-------------|
| 1 | Modify | SKILL.md | Add "Error Recovery" section after Phase 2 |
| 2 | Create | references/<topic>.md | Detailed error table and recovery procedures |
| 3 | Create | agents/validator.md | Validation subagent instructions |
```

**Content Outline** — For each change, a brief outline of what the content will cover. Enough detail that the user can judge whether it matches their intent, but not the full content yet.

**Progressive Disclosure Check** — Current line count, estimated post-enhancement line count, and whether any splitting is needed.

### Step 4: Present and confirm

Show the plan to the user. Wait for confirmation before writing any files. If the user wants adjustments, revise the plan and present again.

---

## Phase 3: Generate Content

### Step 1: Write the content

Generate all new content according to the confirmed plan. Follow the writing standards from the reference files:

**For SKILL.md sections:**
- Follow the writing standards in `references/writing-standards.md` §3 (Writing Style) — explain the why behind important instructions rather than using rigid MUST/NEVER directives
- Use imperative form ("Read the file", not "The file should be read")
- Keep the section focused on flow-control: what to do, when to do it, what decisions to make
- Defer procedural details (lookup tables, format specs, multi-step sub-procedures) to reference files when they exceed 15 lines

**For reference files:**
- Include a table of contents if the file exceeds 300 lines
- Write clear section headers so the model can navigate to the relevant part
- Reference the file from SKILL.md with guidance on *when* to load it — not just a path, but the condition: "Read `references/<topic>.md` when a validation error occurs in Step 3"

**For agent files:**
- Read `references/structure-patterns.md` §3 (Agent Files) for the standard structure and self-containment requirements
- Follow the pattern used by existing agents in the project (e.g., grader.md, comparator.md in sibling skills)

**For script files:**
- Read `references/structure-patterns.md` §4 (Script Files) for requirements on shebangs, permissions, and module structure

**For examples:**
- Show realistic, non-trivial input/output pairs under 30 lines each
- If the target skill has no existing examples, use the Input/Output or Before/After pattern from `references/writing-standards.md` §5

### Step 2: Check consistency with existing content

Before showing the diff, verify:
- New sections don't contradict existing instructions
- New reference files don't duplicate content already in SKILL.md or other references
- New pointers from SKILL.md correctly name the files being created
- Writing style matches the rest of the skill (if the skill uses a conversational tone, don't add a section in formal academic style)

### Step 3: Preview and confirm

Show a unified diff preview of all changes, grouped by file:
- For modified files: show the additions in context (a few surrounding lines)
- For new files: show the full content
- For each change, note which standard it follows

Present to the user: "Apply these changes? (yes / no / adjust)"

### Step 4: Apply

Write all confirmed changes. For new script files, set appropriate permissions.

---

## Phase 4: Verify

Two passes. The first checks that the files agree with each other; the second checks whether the skill still does its job. They answer different questions, and the first one passing says nothing about the second.

### Structural pass

1. **Reference integrity** — Every file path mentioned in SKILL.md exists on disk. Every new reference/agent/script file is pointed to from SKILL.md with a "when to load" condition.
2. **No new duplication** — The added content doesn't repeat information already present in SKILL.md or other reference files.
3. **Line budget** — SKILL.md total line count is within the 500-line budget.
4. **Writing style** — New content uses imperative form, explains rationale for important guidance, and avoids excessive MUST/NEVER directives.
5. **Insert-only** — The diff contains no modified or deleted pre-existing lines. If it does, the author's approval did not cover them.
6. **Description update** — If the enhancement changes the skill's capabilities (adding a new mode, new output type, new trigger scenario), the description field may need updating. Read `references/enhancement-checklist.md` §7 (Description Update Decision) for the decision criteria. Show the current description and suggest additions — but don't modify it without user confirmation, because description changes affect triggering behavior.

### Behavior pass

A pass covering files and line counts cannot tell you whether the new section actually helps, because nothing ran. So:

- If the target skill has `evals/evals.json`, run those prompts against the enhanced skill and report pass rate per case — before and after if a baseline exists.
- If it has none, the verdict line says **behavior unverified**. Do not let six PASS rows imply the addition works; they only say the files are consistent.

```markdown
# Enhancement Verification
- Reference integrity: PASS/FAIL — details if FAIL
- No new duplication: PASS/FAIL — details if FAIL
- Line budget: N/500 PASS/FAIL
- Writing style: PASS/FAIL — details if FAIL
- Insert-only: PASS/FAIL — list any modified or deleted lines
- Description update: needed / not needed — suggestion if needed
- Behavior: pass rate N/N (before N/N) — or "behavior unverified, no evals/ found"
```

If any check fails, note what needs fixing and offer to fix it.

---

## Additive boundary, and what to do when it breaks

This skill inserts. It does not rewrite, restructure, delete, or relocate existing content — even when the insertion makes an existing line wrong, which is the case that actually happens.

When the requested addition cannot land without editing an existing line (a new rule contradicting an old one, a new section that makes an old section redundant, a naming change that invalidates a pointer):

1. Stop before writing.
2. Name the conflicting line and quote it.
3. Offer the two real options: keep the existing line and weaken the addition, or replace the existing line.
4. Let the author choose, and record the choice in the plan.

Silently editing the conflicting line is the failure mode: the author asked for an addition, reviews a diff expecting inserts, and approves a deletion without noticing. When a request is mostly rewriting rather than adding, say so in one line and stop — the deliverable would not be an enhancement.

Writing standards and structural patterns are in the `references/` directory. Load them during Phase 1 based on what the user wants to add — they back every recommendation this skill makes.

- `references/writing-standards.md` — How to write skill content: progressive disclosure, line budgets, writing style, examples
- `references/structure-patterns.md` — How to organize skill directories: reference files, agents, scripts, assets
- `references/enhancement-checklist.md` — Per-content-type checklists for what to verify before and after enhancement
