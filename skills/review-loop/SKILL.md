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

#### Gate Mode Detection

The loop exit conditions are enforced by a gatekeeper. Check Python availability first:

```bash
python3 --version 2>/dev/null && echo "SCRIPT_MODE" || echo "TEXT_MODE"
```

- **Script mode** (Python available): Use `skills/review-loop/scripts/check_loop.py` to enforce exit conditions with round tracking, findings history, and anti-spoofing — the script rejects self-declared PASS without a real review cycle.
- **Text mode** (no Python): Follow §Text Fallback Constraints — identical behavior enforced manually.

#### Step 0: Initialize Loop State

The script is stateless — no `--reset` or runtime files. Initialize these values before starting:

**Script mode** — `findings_history = []`, `max_rounds = 10`, `round = 1`.
**Text mode** — track manually: `round = 1`, `findings_history = []`.

#### Loop Flow

```
1. Spawn Reviewer Agent (read-only, NO worktree) → findings or PASS
2. Verify workspace root unchanged (no worktree created) → if changed: abort & clean up
3. If Reviewer returns PASS → call Loop Exit Gate → if endLoop: exit
4. If Reviewer returns NEEDS_FIXES → Main Agent filters findings
5. Call Loop Exit Gate with accepted_count → if endLoop: exit
6. Spawn Dev Agent (read-write, NO worktree) or apply fixes directly
7. Verify workspace root unchanged → increment round → back to Step 1
```

**Divergence detection**: If findings count increases for 3 consecutive rounds, the gate sets `divergenceWarning=true`. Warn the user the loop may not be converging and ask whether to continue.

#### No Worktree (Mandatory)

**All agents in this loop MUST operate directly in the current workspace — NEVER create or switch to a git worktree.**

Worktrees cause the Reviewer to inspect a stale or empty tree (missing the user's uncommitted changes), the Dev Agent to write fixes into an isolated directory the user can't see, and the Main Agent to lose track of where changes actually landed. This breaks the entire loop.

When spawning any subagent (Reviewer or Dev), you MUST:

1. **Do NOT pass any worktree flag or parameter** to the Task/subagent invocation. Do not set `cwd`, `workdir`, or any directory option that points outside the current workspace.
2. **Explicitly instruct the subagent in its prompt** (see the prompt templates below) that it is forbidden from running `git worktree add`, `git worktree`, or any command that creates/enters a separate working tree.
3. **Verify workspace integrity after each agent returns**: run `git rev-parse --show-toplevel` and confirm it points at the original workspace root. If a worktree was created, abort, remove it with `git worktree remove --force <path>`, and re-run that step in-place.

If the host environment auto-spawns subagents in a worktree by default, override that behavior by setting the subagent's working directory to the current workspace root before it starts.

---

#### Loop Exit Gate (Mandatory)

Call the gate only when the data needed for a valid decision is available:

- After Step 2 only if the Reviewer returned `PASS`.
- After Step 3 if the Reviewer returned `NEEDS_FIXES`, because `accepted_count` is known only after filtering.

Only exit the loop when `endLoop` is `true` — the gate is the sole authority on exit decisions.

**Script mode invocation:**
```bash
echo '{"reviewer_result":"PASS","accepted_count":0,"findings_count":0,"round":1,"findings_history":[],"max_rounds":10}' | python3 skills/review-loop/scripts/check_loop.py
```

| Input field | Type | Description |
|-------------|------|-------------|
| `reviewer_result` | `"PASS"` or `"NEEDS_FIXES"` | Reviewer's verdict. Any other value is invalid. |
| `accepted_count` | int | Findings accepted by Main Agent. Use `0` for `PASS` or when all findings were rejected. |
| `findings_count` | int | Total findings returned by Reviewer this round. Must be `0` for `PASS` and `> 0` for `NEEDS_FIXES`. |
| `round` | int | Current round number, starting at `1`. The gate rejects round `0` because no Reviewer cycle has happened yet. |
| `findings_history` | `[int, ...]` | Findings count per round, used for divergence detection. Initialize as `[]` and pass back the value from the previous gate output. |
| `max_rounds` | int | Maximum review rounds before forced exit. Default `10`. |

Output: `{"endLoop": bool, "reason": str, "verdict": "PASS"|"NEEDS_FIXES"|null, "round": int, "maxRounds": int, "divergenceWarning": bool, "findings_history": [int, ...]}`

**Anti-spoofing**: The script rejects any gate call with `round < 1` — you cannot declare a verdict without actually spawning a Reviewer and completing at least one review round.

**Text mode** — enforce §Text Fallback Constraints manually with identical logic. In text mode, self-declaring a verdict without spawning a Reviewer is equally invalid.

#### Text Fallback Constraints

When Python is unavailable, apply these rules exactly — they match the script's logic:

1. **Input validation**: `reviewer_result` must be `PASS` or `NEEDS_FIXES`; counts must be non-negative integers; `round` must be >= 1.
2. **PASS exit**: Reviewer returns `PASS` with `findings_count == 0` and `accepted_count == 0` → exit loop, verdict PASS.
3. **All-rejected exit**: Reviewer returns `NEEDS_FIXES` and all findings are rejected after filtering → exit loop, verdict PASS.
4. **Divergence**: If findings count strictly increases for 3 consecutive rounds, warn user.
5. **Counter**: Increment `round` after each complete cycle. Track exactly one `findings_history` entry per round.

### Step 1: Spawn Reviewer Agent

Spawn an available **read-only review/exploration agent** with the following prompt structure. In CodeBuddy, prefer `code-explorer`; in Claude-style environments, this may be `Explore`. If no read-only subagent is available, perform the review yourself without editing files.

> ⚠️ **No worktree**: Do not pass any worktree/cwd override to the Task invocation. The subagent must run in the current workspace so it sees the user's actual diff. The prompt below includes a hard prohibition on `git worktree` — do not remove it.

```
You are a code reviewer. Your job is to review workspace changes against the user's goals and identify issues.

## CRITICAL: No Worktree
You MUST review changes in the current workspace directly. Do NOT run `git worktree add`, `git worktree`, or any command that creates or switches to a separate working tree. Do NOT change the working directory. All `git diff` / `git status` commands must run against the workspace you were spawned in — that is where the user's uncommitted changes live.

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
- If `Result: PASS` → call the **Loop Exit Gate** with `{"reviewer_result": "PASS", "accepted_count": 0, "findings_count": 0, "round": <current_round>}`. If `endLoop=true`, proceed to Phase 3.
- If `Result: NEEDS_FIXES` → extract findings, count them, and continue to Step 3.

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

If all findings are rejected → call the **Loop Exit Gate** with `{"reviewer_result": "NEEDS_FIXES", "accepted_count": 0, "findings_count": <total findings this round>, "round": <current_round>}`. If `endLoop=true`, proceed to Phase 3.

### Step 4: Spawn Dev Agent

Spawn an available **read-write development agent** with the following prompt structure. If the host environment has no separate write-capable agent, the Main Agent applies the accepted fixes directly while preserving the same output format.

> ⚠️ **No worktree**: Do not pass any worktree/cwd override to the Task invocation. The Dev Agent must write fixes into the current workspace so the next Reviewer round can verify them. The prompt below includes a hard prohibition on `git worktree` — do not remove it.

```
You are a developer fixing code review findings. Apply each fix carefully, ensuring you don't break existing functionality.

## CRITICAL: No Worktree
You MUST apply fixes directly in the current workspace. Do NOT run `git worktree add`, `git worktree`, or any command that creates or switches to a separate working tree. Do NOT change the working directory. The Reviewer found issues in this workspace's changes — your fixes must land here so the next review round can see them.

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
- Increment `round` by 1, then return to Step 1 for the next review round.

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
