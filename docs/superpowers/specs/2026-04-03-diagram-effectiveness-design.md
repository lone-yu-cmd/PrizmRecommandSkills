# Diagram Effectiveness Audit Dimension Design Spec

**Date:** 2026-04-03
**Status:** Draft

---

## 1. Overview

Add a 12th audit dimension — **Diagram Effectiveness** — to the shared `audit-criteria.md` used by skill-reviewer and skill-optimizer. This dimension detects workflow descriptions rendered as ASCII tree diagrams and recommends converting them to numbered lists for better LLM comprehension.

### Why This Matters

Skill files (SKILL.md and references) are primarily consumed by LLMs, not humans. LLMs process text as token sequences — they don't perceive spatial relationships from `│├└─` characters the way a human eye does. ASCII tree characters used in workflow descriptions are noise tokens that consume context budget without conveying information the model can use. Numbered lists communicate the same sequential/hierarchical information more directly and with fewer tokens.

### Scope Boundary

This dimension targets **workflow/process diagrams only** — sequences of steps, phases, or actions rendered as tree structures. It explicitly excludes:
- **Directory structure diagrams** (e.g., `skill-name/├── SKILL.md`) — these are a well-established convention that LLMs have extensive training exposure to and parse reliably
- **Markdown tables** — already an efficient format
- **Graphviz/dot notation** — structured data format, not visual art

---

## 2. Audit Criteria Specification

### Dimension 12: Diagram Effectiveness

**What to measure**: Whether workflow/process descriptions use ASCII tree-drawing characters (`│├└─→` combined with indentation) when a numbered list or prose would be more LLM-friendly.

**Warning threshold**: A fenced or inline block that (a) contains 2+ tree-drawing characters (`│`, `├`, `└`, `─`) AND (b) the content describes actions, phases, steps, or workflows (not file paths).

**How to detect**:
1. Scan for blocks containing tree-drawing characters: `│`, `├`, `└`, `─`, `┌`, `┐`, `┘`, `┤`, `┬`, `┴`, `┼`
2. For each match, classify the content:
   - **Directory structure**: Lines contain file extensions (`.md`, `.py`, `.json`, `.sh`), path separators (`/`), or common directory names (`scripts/`, `references/`, `assets/`, `src/`, `dist/`). → Skip, not a finding.
   - **Workflow diagram**: Lines contain action verbs, phase numbers, step descriptions, arrow operators (`→`, `->`, `=>`), or process nouns ("brainstorm", "plan", "launch", "monitor", "evaluate", "generate"). → Flag as warning.
3. If the block is ambiguous (mixed file paths and action descriptions), flag at **info** level with a note for manual review.

**Severity**: warning

**Finding format**:
```
Workflow diagram uses ASCII tree format — LLMs process tokens sequentially and don't 
perceive the spatial relationships these characters convey. Consider converting to a 
numbered list for clearer sequential/hierarchical communication.
```

**Suggested fix**: Convert to numbered list. Show before/after in the finding.

**Before (warning)**:
```
feature-workflow <idea>
   │
   ├── Phase 1: Brainstorm → deep Q&A
   │
   ├── Phase 2: Plan → planner → output.json
   │
   └── Phase 3: Launch → pipeline execution
```

**After (recommended)**:
```
1. Brainstorm — deep interactive Q&A until requirements are clear
2. Plan — run feature-planner, output feature-list.json
3. Launch — run pipeline-launcher, execute pipeline
```

**False positive guidance**:
- Directory tree diagrams (`skill-name/├── SKILL.md└── references/`) are NOT workflow diagrams. Skip them.
- A tree diagram inside a `## Output Format` section may be a specification for user-facing output (what the user sees), not instructions for the LLM. In that context, the diagram serves a formatting purpose and may be appropriate. Flag at info level rather than warning.
- Very short trees (2-3 items, single level) have minimal token overhead. Flag at info level if under 5 lines.

---

## 3. Files to Modify

| File | Change |
|------|--------|
| `skills/skill-reviewer/references/audit-criteria.md` | Add §12 Diagram Effectiveness |
| `skills/skill-optimizer/references/audit-criteria.md` | Identical addition (these are duplicate files) |
| `skills/skill-reviewer/SKILL.md` | Update "11-dimension" references to "12-dimension" |
| `skills/skill-optimizer/SKILL.md` | Same update |

### SKILL.md Changes (Both Files)

In the dimension list (both skill-reviewer and skill-optimizer have the same list), add:
```
12. **Diagram effectiveness** — workflow descriptions using ASCII tree format instead of LLM-friendly numbered lists
```

Update summary text: "Evaluates 11 dimensions" → "Evaluates 12 dimensions" (appears in description and intro).

---

## 4. Design Principles

1. **Targeted, not dogmatic** — only flag workflow diagrams, not all ASCII art
2. **Warning, not error** — respect skill author's choice while surfacing the optimization opportunity
3. **Show the alternative** — every finding includes a before/after conversion
4. **Explain the why** — the finding explains the token-efficiency reasoning so the author can make an informed decision
