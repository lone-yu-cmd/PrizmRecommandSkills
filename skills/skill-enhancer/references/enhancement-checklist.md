# Enhancement Checklist Reference

Per-content-type checklists for verifying enhancements. Load this file for every enhancement — it contains the pre-flight and post-flight checks that ensure new content integrates cleanly.

## Table of Contents
1. [Universal Checks](#1-universal-checks)
2. [Adding a Section to SKILL.md](#2-adding-a-section-to-skillmd)
3. [Adding a Reference File](#3-adding-a-reference-file)
4. [Adding an Agent File](#4-adding-an-agent-file)
5. [Adding a Script](#5-adding-a-script)
6. [Adding Examples](#6-adding-examples)
7. [Description Update Decision](#7-description-update-decision)

---

## 1. Universal Checks

Universal pre-flight and post-flight checks are defined in SKILL.md Phase 4 (Verify). This file focuses on **type-specific** checklists that supplement those universal checks.

---

## 2. Adding a Section to SKILL.md

### Pre-flight
- [ ] Determine where in the document the section belongs (after which existing section?)
- [ ] Check if any existing section partially covers this topic — if so, extend it rather than creating a new one
- [ ] Estimate line count — if >30 lines of procedural content, consider splitting to references/
- [ ] Check numbering scheme — match existing pattern (Phase N, Step N, etc.)

### Content standards
- Section header follows existing heading level conventions (##, ###, ####)
- First paragraph explains what this section does and why it exists
- Steps use imperative form and numbered/lettered lists matching existing style
- Cross-references to other sections use consistent linking style
- Any conditional content (>15 lines, <30% invocation frequency) flags for extraction

### Post-flight
- [ ] New section integrates into the document flow — reading the document top-to-bottom still makes sense
- [ ] No orphaned references (the section mentions files that exist)
- [ ] No contradiction with existing sections
- [ ] Line budget check (current total after addition)

---

## 3. Adding a Reference File

### Pre-flight
- [ ] Verify this content doesn't belong in an existing reference file — check all files in references/
- [ ] Determine if the content is truly branch-specific (only needed sometimes) or always needed
- [ ] Plan the SKILL.md pointer: what condition triggers loading this file?

### Content standards
- Clear, descriptive filename (lowercase, hyphenated)
- Table of contents if file exceeds 300 lines
- Self-contained sections with clear headers
- No assumptions about SKILL.md context — the model may read this file starting from any section

### Post-flight
- [ ] SKILL.md contains a conditional pointer to the new file
- [ ] The pointer includes both the path AND the loading condition
- [ ] No content duplication between the reference file and SKILL.md
- [ ] The reference file is self-contained — readable without SKILL.md for its specific topic

---

## 4. Adding an Agent File

### Pre-flight
- [ ] Define the agent's single responsibility — if it does two things, consider two agents
- [ ] Check existing agents for overlap — can an existing agent handle this?
- [ ] Identify what inputs the agent needs and what outputs it produces

### Content standards
Follow the standard agent structure in `structure-patterns.md` §3 (Agent Files). The agent file must be self-contained — the agent should not need to read SKILL.md to do its job.

### Post-flight
- [ ] SKILL.md references the agent with context on when to spawn it
- [ ] Agent file defines clear input/output contract
- [ ] Output format matches what the parent skill expects to receive
- [ ] No circular dependencies (agent doesn't need to read SKILL.md)

---

## 5. Adding a Script

### Pre-flight
- [ ] Verify the operation is deterministic and benefits from being scripted (vs model judgment)
- [ ] Check if similar logic already exists in another script — extend rather than duplicate
- [ ] Determine invocation pattern: direct execution or module import?

### Content standards
Follow the requirements in `structure-patterns.md` §4 (Script Files) for shebangs, permissions, docstrings, and module structure.

### Post-flight
- [ ] SKILL.md contains the invocation command with arguments
- [ ] Shell scripts have execute permission (`chmod +x`)
- [ ] Python scripts compile without syntax errors
- [ ] If scripts/ uses module imports, `__init__.py` exists

---

## 6. Adding Examples

### Pre-flight
- [ ] Check if existing examples already cover this case — extend rather than add redundant examples
- [ ] Determine whether an example is the right tool — would a 2-line explanation suffice?
- [ ] Identify the transformation or pattern the example illustrates

### Content standards
- Realistic, non-trivial input/output pairs (not "run command" → "success")
- Under 30 lines per individual example
- Uses Input/Output or Before/After framing (unless the skill's domain suggests otherwise)
- Matches the complexity level of actual usage — not too simple, not an edge case

### Post-flight
- [ ] Examples don't contradict existing instructions
- [ ] Examples are consistent with the output format defined elsewhere in the skill
- [ ] Token cost is justified — the example teaches something the instructions alone don't convey

---

## 7. Description Update Decision

After any enhancement, evaluate whether the `description` frontmatter field needs updating.

### Update needed when:
- The enhancement adds a new capability or mode the skill didn't have before
- The enhancement adds a new trigger scenario (a new "when to use" case)
- The enhancement adds support for a new domain or framework
- New keywords introduced in the content should appear in the description for triggering

### Update NOT needed when:
- The enhancement deepens existing capability without changing scope
- The enhancement adds internal structure (reference files, agents) that don't change what the skill does from the user's perspective
- The enhancement adds examples that illustrate existing behavior

### How to update
If an update is needed:
1. Show the current description
2. Highlight what's changed (new capability, new trigger, new keywords)
3. Propose a revised description that incorporates the changes
4. Let the user decide — description changes affect triggering across all future invocations

Do not auto-modify the description. Always present the change for user confirmation.
