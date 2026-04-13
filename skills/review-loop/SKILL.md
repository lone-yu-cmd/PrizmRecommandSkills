---
name: "review-loop"
description: "Iterative review-fix loop with three agents. Spawns a read-only Reviewer agent to analyze workspace diff against user goals, main agent filters findings for reasonableness, then a Dev agent applies fixes. Loops until the Reviewer finds no issues. Use this skill after completing code changes that need quality assurance. Trigger on: 'review loop', 'review and fix', 'review-fix cycle', 'iterative review', 'help me review and fix'. (project)"
---

# Review Loop

An iterative review-fix loop that uses three agents with separated concerns to improve code quality:

- **Reviewer Agent** (read-only): analyzes workspace diff against user goals, produces structured findings
- **Main Agent** (orchestrator): filters Reviewer findings for reasonableness, coordinates the loop
- **Dev Agent** (read-write): applies fixes for findings the Main Agent deems reasonable

The loop repeats until the Reviewer Agent finds no issues, meaning all changes meet the user's goals and have no defects.

### When to Use
- After completing code modifications that need quality assurance
- When the user wants an independent review-fix cycle on their workspace changes
- When code changes are complex enough to benefit from a fresh-eyes review
- User says "review loop", "review and fix", "iterative review", "help me review and fix"

### When NOT to Use
- No changes in the workspace (nothing to review)
- Trivial one-line changes that don't warrant a review cycle

## Execution Steps

### Phase 1: Goal Inference

Before starting the review loop, establish what the user is trying to accomplish. The Reviewer Agent needs this context to judge whether changes are correct and complete.

1. **Scan conversation history** for the user's original task description, requirements, or instructions.
2. **Synthesize a goal statement**: a concise summary of what the workspace changes should achieve.
3. **If the goal is unclear** (e.g., the conversation lacks enough context), ask the user directly:
   - "I'm about to start the review-fix loop. Can you briefly describe what these changes are supposed to accomplish?"
   - Collect all unclear points in a single question — don't ask multiple rounds.
4. **Capture workspace state**: run `git diff` (unstaged) + `git diff --cached` (staged) + `git status` to understand the full scope of changes.
   - If no changes are detected, inform the user and stop.

### Phase 2: Review-Fix Loop

```
┌─── Loop ──────────────────────────────────────────────┐
│                                                        │
│  Step 1: Spawn Reviewer Agent (read-only)              │
│    → Input: git diff + goal statement + round number   │
│    → Output: structured findings or PASS               │
│                                                        │
│  Step 2: Check result                                  │
│    → If PASS (no findings): exit loop                  │
│                                                        │
│  Step 3: Main Agent filters findings                   │
│    → For each finding: accept (reasonable) or reject   │
│    → If all rejected: exit loop                        │
│                                                        │
│  Step 4: Spawn Dev Agent (read-write)                  │
│    → Input: accepted findings + goal statement         │
│    → Output: fix report                                │
│                                                        │
│  Step 5: Back to Step 1                                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

The loop terminates when:
- The Reviewer Agent returns PASS (no findings), or
- The Main Agent rejects all findings as unreasonable

**Divergence detection**: If findings count increases for 3 consecutive rounds, warn the user that the loop may not be converging and ask whether to continue.

---

### Step 1: Spawn Reviewer Agent

Spawn a **read-only** agent (subagent_type: `Explore`) with the following prompt structure:

```
You are a code reviewer. Your job is to review workspace changes against the user's goals and identify issues.

## User Goal
{goal_statement}

## Review Round
Round {N}. {round_context}

## What to Review
Run these commands to see the current workspace changes:
- `git diff` (unstaged changes)
- `git diff --cached` (staged changes)  
- `git status` (new/deleted files)

For new files shown in git status, read their full content.
For modified files, read enough surrounding context to understand the change.

## Review Dimensions
Evaluate the changes across these dimensions (focus on what's relevant — not every dimension applies to every change):

1. **Goal alignment**: Do the changes accomplish what the user intended? Is anything missing or off-target?
2. **Defects**: Logic bugs, missing error handling, boundary condition issues, incorrect behavior.
3. **Completeness**: Are there files that should have been changed but weren't? Missing tests, types, imports, exports?
4. **Consistency**: Do the changes follow the project's existing patterns, naming conventions, and code style?
5. **Security**: Hardcoded secrets, injection vulnerabilities, unsafe operations.

## Output Format
Respond with EXACTLY this format:

### Result: PASS | NEEDS_FIXES

### Findings
(If PASS, write "No issues found.")

#### Finding N
- **Severity**: high | medium | low
- **Dimension**: goal-alignment | defect | completeness | consistency | security
- **Location**: filepath:line (or "project-level")
- **Problem**: What is wrong and why it matters
- **Suggestion**: Recommended fix direction (describe the approach, not exact code)
- **Verification**: How to confirm the fix is correct

### Summary
One to two sentences about the overall state of the changes.
```

**Round context** varies by round:
- Round 1: "This is the first review. Examine all changes comprehensively."
- Round 2+: "Previous round found issues that were fixed. Focus on: (1) whether previous fixes are correct, (2) whether fixes introduced new problems, (3) any remaining issues in unchanged code. Do not re-report issues that have already been fixed."

### Step 2: Check Result

Parse the Reviewer Agent's output:
- If `Result: PASS` → the loop is done. Proceed to Phase 3.
- If `Result: NEEDS_FIXES` → extract findings and continue to Step 3.

### Step 3: Main Agent Filters Findings

The Main Agent reviews each finding and decides whether it's reasonable. This is a critical quality gate — it prevents the Dev Agent from making unnecessary or harmful changes.

**For each finding, evaluate:**
- Is this finding relevant to the current changes? (Reject findings about code that wasn't modified and isn't related to the goal.)
- Is this a real problem or a subjective style preference? (Reject pure style preferences unless they violate clear project conventions.)
- Would fixing this improve the code without introducing risk? (Reject fixes that would require large, risky refactors outside the original scope.)

**Output per finding:**
- **Accepted**: The finding is reasonable — include it in the Dev Agent's task.
- **Rejected** (with reason): Brief explanation of why the finding was dismissed (e.g., "Out of scope — this code wasn't changed", "Style preference, not a defect").

Display the filtering results to the user before spawning the Dev Agent, so the user has visibility into the decisions.

If all findings are rejected → the loop is done. Proceed to Phase 3.

### Step 4: Spawn Dev Agent

Spawn a **general-purpose** agent (has read-write access) with the following prompt structure:

```
You are a developer fixing code review findings. Apply each fix carefully, ensuring you don't break existing functionality.

## User Goal
{goal_statement}

## Findings to Fix
{accepted_findings_list — each with Severity, Location, Problem, Suggestion, Verification}

## Instructions
1. Read each finding carefully.
2. For each finding:
   a. Read the relevant code and understand the context.
   b. Implement the fix based on the suggestion.  
   c. If a suggestion is not feasible (would break other functionality, is technically impossible, etc.), explain why instead of forcing a bad fix.
3. After all fixes are applied, report what you did.

## Output Format
For each finding, report:
- **Finding N**: [fixed | unable-to-fix]
- **What was done**: Brief description of the change
- **Files modified**: List of changed files
(If unable-to-fix, explain why)
```

After the Dev Agent returns:
- Record which findings were fixed and which were not.
- If any findings were reported as "unable-to-fix", show these to the user with the Dev Agent's explanation. The user can decide to skip them or provide guidance.
- Return to Step 1 for the next review round.

---

### Phase 3: Completion Summary

When the loop ends, display a summary:

```
## Review Loop Complete

- **Rounds**: {N}
- **Total findings**: {total across all rounds}
- **Fixed**: {count}
- **Rejected by main agent**: {count} (with reasons)
- **Unable to fix**: {count} (if any)
- **Final status**: PASS
```

This is a terminal skill — no automatic handoff. The user decides what to do next (commit, run tests, continue working, etc.).
