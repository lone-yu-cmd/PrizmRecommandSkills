# Addition Checklist Reference

Per-content-type pre-flight, content standards, and post-flight checklists for `add` actions. Load this file in Phase 2 (before drafting) and Phase 3 (post-flight verification) whenever the change list includes `add` items.

## Table of Contents

1. [Universal Checks](#1-universal-checks)
2. [Adding a Section to SKILL.md](#2-adding-a-section-to-skillmd)
3. [Adding a Reference File](#3-adding-a-reference-file)
4. [Adding an Agent File](#4-adding-an-agent-file)
5. [Adding a Script](#5-adding-a-script)
6. [Adding Examples](#6-adding-examples)
7. [Adding an Asset File](#7-adding-an-asset-file)

---

## 1. Universal Checks

Universal post-flight checks (reference integrity, no duplication, 500-line budget, scope adherence / `insert-only`, and behavior checks) live in `SKILL.md` Phase 3 and `references/rewrite-playbook.md` §7. For deciding whether an addition requires updating `description`, see `references/rewrite-playbook.md` §4.

---

## 2. Adding a Section to SKILL.md

### Pre-flight
- [ ] Determine where in the document the section belongs (after which existing section)
- [ ] Check whether an existing section partially covers the topic — extend it rather than creating a duplicate section
- [ ] Estimate line count — if >30 lines of procedural detail, split the details into `references/` and keep a routing summary in `SKILL.md`
- [ ] Check numbering scheme — match the existing pattern (`Phase N`, `Step N`, etc.)

### Content standards
- Section header matches existing heading levels (`##`, `###`, `####`)
- Opening paragraph explains what the section does and why it exists
- Steps use imperative form and numbered/lettered lists matching existing style
- Cross-references use explicit section names (`§Phase 2 Step 3`), not positional phrasing
- Conditional content (>15 lines, <30% trigger frequency) is flagged for extraction

### Post-flight
- [ ] New section integrates cleanly into top-to-bottom workflow reading
- [ ] No orphaned references (every mentioned file exists)
- [ ] No contradiction with existing sections (or conflicting lines were surfaced per Phase 1)
- [ ] Line budget verified after addition

---

## 3. Adding a Reference File

### Pre-flight
- [ ] Verify the content does not already belong in an existing file under `references/`
- [ ] Confirm the content is branch-specific rather than needed on every run
- [ ] Plan the `SKILL.md` pointer and its exact loading condition

### Content standards
- Clear, descriptive lowercase hyphenated filename
- Table of contents near the top if exceeding 300 lines
- Self-contained sections with clear headers, assuming the model may read starting from any section

### Post-flight
- [ ] `SKILL.md` contains a conditional pointer naming both path and loading condition
- [ ] Zero content duplication between the reference file and `SKILL.md`
- [ ] Reference file is readable on its own for its specific topic

---

## 4. Adding an Agent File

### Pre-flight
- [ ] Define the agent's single responsibility — split if it handles two unrelated jobs
- [ ] Check existing `agents/` files for overlap
- [ ] Identify exact inputs and expected outputs

### Content standards
Follow the 6-section template and principles in `references/structure-patterns.md` §3 (`Role`, `Your Task`, `Inputs`, `Output Format`, `Evaluation Criteria`, `Edge Cases`). Keep the file fully self-contained so the agent does not need to read `SKILL.md`.

### Post-flight
- [ ] `SKILL.md` names the agent and states when to spawn it
- [ ] Agent file defines a clear input/output contract matching what the parent skill expects
- [ ] No circular dependency requiring the subagent to read `SKILL.md`

---

## 5. Adding a Script

### Pre-flight
- [ ] Confirm the task is deterministic and benefits from scripting over model judgment
- [ ] Check existing scripts to extend rather than duplicate logic
- [ ] Choose direct execution vs module import (`python -m scripts.foo`)

### Content standards
Follow `references/structure-patterns.md` §4 for shebangs, execute bits, docstrings, comment headers, and `__init__.py`.

### Post-flight
- [ ] `SKILL.md` includes the invocation command and arguments
- [ ] Shell scripts have execute permission (`chmod +x`)
- [ ] Python scripts pass syntax compilation (`python3 -m py_compile`)
- [ ] `__init__.py` exists if module imports are used

---

## 6. Adding Examples

### Pre-flight
- [ ] Check existing examples so the addition does not repeat what is already shown
- [ ] Confirm a 2-line explanation would not be clearer and cheaper in tokens
- [ ] Identify the exact transformation or non-obvious rule being demonstrated

### Content standards
- Realistic, non-trivial pairs (never `"run command" → "success"`)
- Under 30 lines per example
- Uses `Input/Output` or `Before/After` framing unless the domain dictates otherwise
- Matches real usage complexity

### Post-flight
- [ ] Examples agree with existing instructions and defined output templates
- [ ] Token cost is justified — teaches something prose alone missed

---

## 7. Adding an Asset File

### Pre-flight
- [ ] Confirm the file is an output template or static resource (HTML/CSS/config template, icon, font) rather than model instructions
- [ ] Check existing `assets/` files for overlap or reusable templates
- [ ] Define the placeholder or consumption contract (who copies, fills, or reads it)

### Content standards
Follow `references/structure-patterns.md` §5: keep filenames clear and lowercase-hyphenated (or matching expected template naming), and use obvious, minimal placeholders.

### Post-flight
- [ ] `SKILL.md` or a bundled script references the exact `assets/` path
- [ ] File exists on disk at the referenced path
- [ ] Large static/binary assets are consumed by scripts or templates rather than loaded wholesale into prompt instructions
