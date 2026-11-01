# Claim Ledger and Loop State

The loop's truth lives in files, not in the orchestrator's context. Read this file when you start a loop, when a claim's status is unclear, or when the user asks what was parked.

## Why files

An instruction to "keep a summary" is not enforcement. If the round reports stay in the conversation, every later round pays for them, and the goal drifts as the transcript grows. Keeping state in a file makes the digest the only thing that survives: the orchestrator reads one JSON file plus the current round's report, and history is referenced by path when it is actually needed.

The state directory must live **outside the reviewed workspace** — otherwise the state files show up in `git status` and become part of the diff the Reviewer inspects. Use the baseline directory created in Phase 1 (`/tmp/review-loop-<timestamp>/`).

## Layout

```
$REVIEW_LOOP_DIR/
  state.json          # the ledger; written by the main agent after each gate call
  changes.patch       # pre-loop `git diff HEAD`
  status.txt          # pre-loop `git status --porcelain`
  backlog.md          # medium/low claims parked outside the loop
  round-1.reviewer.md # raw Reviewer output, append-only
  round-1.dev.md      # raw Dev output
  round-2.reviewer.md
  ...
```

The Reviewer and the Dev write nothing here. They return text; the main agent files it.

## state.json

Start every loop from this skeleton — `rounds` empty, and both verification fields carrying the pre-loop result:

```json
{
  "goal": "one-line goal statement",
  "verify_cmd": "npm test -- --runInBand",
  "baseline_verification": "passed",
  "verification": "passed",
  "reviewer_mode": "isolated",
  "round": 1,
  "max_rounds": 10,
  "novelty_history": [],
  "settled_claims": [],
  "dimensions": ["goal-alignment", "defect", "completeness", "consistency", "security"],
  "rounds": []
}
```

After round 1 has been adjudicated and verified, the same file looks like this. It is illustrative — never copy it as a starting state, because it already records a finished round:

```json
{
  "...": "the fields above, with:",
  "round": 2,
  "verification": "passed",
  "novelty_history": [5],
  "settled_claims": ["src/auth.ts:12 | consistency | two naming schemes | backlog: housekeeping, medium"],
  "rounds": [
    { "round": 1, "claims": 5, "new": 5, "accepted": 2, "rejected": 1,
      "waived": 0, "backlog": 2, "fixed": 2, "unable_to_fix": 0,
      "verification": "passed", "verdict": null }
  ]
}
```

Write it back after every gate call: `round`, `verification`, `novelty_history`, `settled_claims` come from the loop; `rounds[]` is the human-readable ledger. `baseline_verification` never changes after Phase 1 — it is the only record of what was already broken before the loop touched anything.

## Claim identity

Every claim has exactly one identity:

```
<location> | <dimension> | <short problem>
```

Examples: `src/auth.ts:42 | defect | null deref on missing session` or `project-level | consistency | two naming schemes for the same route`.

Matching rules:

- Case and runs of whitespace are ignored when comparing (`src/A.ts:42 | Defect | null  deref` matches `src/a.ts:42 | defect | null deref`).
- Location is the file path plus the line that best anchors the claim. A claim that moves after a fix keeps its old identity only if the location is unchanged; otherwise it is a new claim, which is correct — the code changed.
- The fourth field is not part of the identity. It exists only on settled entries: `<location> | <dimension> | <problem> | <evidence or reason>`.
- A field never contains `|`. The gate splits on it and rejects anything that is not exactly three fields (claim) or exactly four (settled), so a stray pipe fails loudly instead of silently truncating an identity.

If the Reviewer re-raises a settled claim with different wording, restore the settled wording before counting it. Do not let phrasing drift manufacture novelty.

## Statuses

Every claim ends a round in exactly one status. The four counts must sum to the number of claim keys.

- **accepted** — in scope, evidenced, and will be fixed now.
- **rejected** — disproved. Requires evidence: `file:line` that shows the behaviour is intended, a project convention document, a contract/schema, a passing test, or an explicit exclusion in the spec/plan/user request. If the claim cites a rule and the rejection cannot cite anything, accept it.
- **waived** — accepted as true but deliberately not fixed: user decision, infeasible in this context, or the fix needs a refactor beyond the goal. Always carries the reason.
- **backlog** — parked outside the loop: medium severity by default, low always. Written to `backlog.md` with its identity so a later session can pick it up. The state directory lives under `/tmp` and does not survive a reboot, so Phase 3 asks once whether to keep a non-empty backlog somewhere durable.

## Severity budget

The loop spends rounds on blocking work only:

- **critical** — adjudicate; accepted critical claims keep the loop alive regardless of other counts.
- **high** — adjudicate; accept unless evidence disproves it.
- **medium** — backlog, unless it is a correctness or security issue, in which case treat it as high.
- **low** — backlog, always. A low-severity claim may be rejected outright instead of parked when it is pure style.

This is what keeps a ten-round fuse from being consumed by nitpicking: the loop cannot substitute volume for severity.

## Settled claims

`settled_claims` holds every rejected, waived, and backlogged entry, with its evidence or reason prefixed `rejected:`, `waived:`, or `backlog:`. The gate uses the first three fields to compute novelty, so a re-raised settled claim — parked or not — does not look like progress.

Un-setting an entry is a deliberate act: remove it from `settled_claims` only when the Reviewer supplies evidence that did not exist when it was settled, and say so to the user. Never silently drop a waiver to make the loop look converged.
