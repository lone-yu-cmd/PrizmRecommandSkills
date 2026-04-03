# Skill Enhancer Design Spec

**Date:** 2026-04-03
**Status:** Draft

---

## 1. Overview

**skill-enhancer** is a new skill that helps users supplement existing skills with additional content, following the best practices defined in skill-creator's implementation standards.

### Core Positioning

Users tell the skill what they want to add. The skill plans the best way to do it according to established norms, then executes after user confirmation.

### Strict Boundaries with Existing Skills

| Skill | Responsibility | Does NOT do |
|-------|---------------|-------------|
| `skill-reviewer` | Read-only diagnostic audit | Modify any content |
| `skill-optimizer` | Refactor/optimize existing content quality | Add new content |
| `skill-enhancer` (new) | Supplement missing/insufficient content per standards | Refactor existing content |
| `skill-auditor` | Runtime testing and evaluation | Modify skills |

**Key distinction:** skill-optimizer improves what's already there; skill-enhancer adds what's missing. They do not overlap.

---

## 2. Trigger Conditions

**Trigger phrases:** "enhance skill", "supplement skill", "add content to skill", "skill needs more", "expand skill section", "enrich skill"

**Command format:**
```
/skill-enhancer <path-to-skill> <user intent description>
```

**Examples:**
```
/skill-enhancer skills/skill-reviewer "add a grader agent for scoring"
/skill-enhancer skills/skill-auditor "add detailed examples to the evaluation flow"
/skill-enhancer skills/skill-optimizer "supplement error handling section"
```

---

## 3. Workflow (4 Phases)

### Phase 1 — Understand Intent & Context

1. Read the target skill's complete directory (SKILL.md + references/agents/scripts)
2. Load relevant sections from local reference files (see Section 4)
3. Identify what type of content the user wants to add (section / reference / agent / script / example)

### Phase 2 — Plan Enhancement

1. Based on writing standards and structure patterns, determine best practices for this type of content
2. Considering the target skill's existing structure, decide where and how to organize the new content
3. Generate an enhancement plan:

```markdown
# Enhancement Plan

## User Intent
<what the user wants to add>

## Standards Reference
<which reference file, which standard applies>

## Change Plan
| # | Change Type | File Path | Description |
|---|------------|-----------|-------------|
| 1 | Modify | SKILL.md | Add "Error Handling" section after Phase 2 |
| 2 | Create | agents/grader.md | Scoring agent definition |

## Content Outline
### 1. Error Handling Section
- Scenarios covered: ...
- Handling strategies: ...

## Progressive Disclosure Check
- Current SKILL.md lines: 135 -> Estimated after enhancement: 178 (within 500-line budget)
```

4. Present plan to user, wait for confirmation before proceeding

### Phase 3 — Generate Content per Standards

1. Generate/modify files according to the confirmed plan
2. Ensure compliance with skill-creator writing principles:
   - Progressive disclosure: content at the correct loading level
   - 500-line budget: split to references if SKILL.md would exceed
   - Writing style: explain the why, avoid MUST/NEVER overuse
   - Reference health: new references/agents correctly linked
3. Show unified diff preview, apply after user confirmation

### Phase 4 — Verify

Quick verification pass:
```markdown
# Enhancement Verification
- Content consistency: new content does not conflict with existing content
- Reference integrity: all new reference paths are valid
- Line budget: N/500
- Writing style: compliant with standards
- Description update: [needed/not needed] based on whether skill capabilities changed
```

---

## 4. Reference Files

The skill loads its own local reference files (extracted from skill-creator standards) rather than reading skill-creator's SKILL.md at runtime. This follows the progressive disclosure principle.

### `references/writing-standards.md` — Writing Standards

Content extracted from skill-creator:
- **Progressive Disclosure** three-level model (metadata -> body -> resources)
- **500-line budget** rule and splitting strategy
- **Writing style**: explain the why, avoid MUST/NEVER overload, imperative form
- **Section organization**: domain-first, not alphabetical
- **Example writing**: token cost vs. usefulness balance

### `references/structure-patterns.md` — Structure Patterns

- SKILL.md standard structure (frontmatter -> description -> body sections)
- Reference files: when to use, how to organize
- Agent files: role definition standards
- Script files: executability, permissions, purpose documentation
- Asset management principles

### `references/enhancement-checklist.md` — Enhancement Checklist

- Per-content-type enhancement standards (section / reference / agent / script / example)
- Pre/post consistency checks
- Reference integrity verification
- Description update decision criteria

---

## 5. Output Scope Decision Logic

The skill automatically determines which files need to change:

- If the enhancement only affects SKILL.md body content -> modify SKILL.md only
- If the enhancement requires supporting files (agent definitions, reference docs, scripts) -> create them alongside SKILL.md changes
- If adding content would push SKILL.md over 500 lines -> split into reference files
- If the enhancement changes the skill's capability scope -> flag that description may need updating

---

## 6. Design Principles

1. **User-driven, standard-guided**: Users decide what to add; the skill decides how to do it well
2. **Show the plan before acting**: Never modify files without user confirmation
3. **Reference-backed decisions**: Every suggestion traces back to a specific standard in the reference files
4. **Additive only**: This skill adds content. It does not refactor, remove, or reorganize existing content (that's skill-optimizer's job)
5. **Progressive disclosure aware**: New content lands at the right level in the skill's architecture
6. **Budget conscious**: Always check line counts before and after enhancement
