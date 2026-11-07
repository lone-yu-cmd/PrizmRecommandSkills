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
  seen-snapshot       # stash-create id of the state the reviewer last read
  round-N.patch       # patch since the previous snapshot, sent to the reviewer
  backlog.md          # medium/low claims parked outside the loop
  round-1.reviewer.md # raw Reviewer output, append-only
  round-1.fix.md      # the main agent's fix record for the round
  round-2.reviewer.md
  ...
```

The Reviewer writes nothing here; it returns text, and the main agent files that text plus its own fix record.

## state.json

Start every loop from this skeleton — `rounds` empty, and both verification fields carrying the pre-loop result:

```json
{
  "goal": "one-line goal statement",
  "verify_cmd": "npm test -- --runInBand",
  "baseline_verification": "passed",
  "verification": "passed",
  "reviewer_mode": "isolated",
  "reviewer_agent_id": "",
  "reviewer_context_broken": false,
  "frozen_themes": [],
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
  "reviewer_agent_id": "agent-7f3c",
  "frozen_themes": [
    {
      "theme": "queue_timeout_end_tip column type",
      "identity": "db/migrations/0042.sql:10 | defect | end_tip column type too narrow",
      "constraints": ["omitted-column INSERT must succeed", "MySQL 5.7 row size must hold"],
      "reopen_used": false
    }
  ],
  "novelty_history": [5],
  "settled_claims": [
    "db/migrations/0042.sql:10 | defect | end_tip column type too narrow | waived: theme frozen; constraints: omitted-column INSERT must succeed, MySQL 5.7 row size must hold",
    "src/auth.ts:12 | consistency | two naming schemes | backlog: housekeeping, medium"
  ],
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

The gate compares exact identities. Object-level folding happens in the main agent before the gate call: when a claim is about an object in `frozen_themes`, the main agent rewrites the claim's identity to the theme's recorded identity, so the gate sees a settled claim. The gate itself never guesses that two identities mean the same object — do not weaken its match to a fuzzy one.

If the Reviewer re-raises a settled claim with different wording, restore the settled wording before counting it. Do not let phrasing drift manufacture novelty.

## Frozen themes

A theme is the object a decision is about — `queue_timeout_end_tip column type`, not the sentence, the line, or the file. Freeze it when a claim is accepted, so later rounds cannot spend rounds re-deciding the same object.

Each entry:

```json
{
  "theme": "queue_timeout_end_tip column type",
  "identity": "db/migrations/0042.sql:10 | defect | end_tip column type too narrow",
  "constraints": ["omitted-column INSERT must succeed", "MySQL 5.7 row size must hold"],
  "reopen_used": false
}
```

- `identity` is the accepted claim's three-field identity and is what later same-object claims are rewritten to.
- `constraints` are the hard conditions the chosen scheme must satisfy, each checkable by reading the patch or a schema. They are what makes the freeze falsifiable rather than a preference.
- `theme` and every constraint contain no `|`; `identity` uses the gate's three-field pipe-delimited shape and must keep it, because it is passed straight into `claim_keys`.
- `reopen_used` records the one allowed reopen.

On acceptance, append the theme and, **after the gate call**, add `<identity> | waived: theme frozen; constraints: <...>` to `settled_claims`. Adding it before the call would suppress this round's novelty count for a claim that was genuinely new this round; adding it after keeps the current round honest and makes every later round see an old identity.

## Reopening a theme once

A freeze is not absolute. When a patch proves a hard condition that was never written into `constraints`, the theme may reopen once:

1. The claim must name the missing constraint — a condition that is checkable and was not listed, such as a row-size limit discovered only when the schema is read.
2. Keep the claim's own identity, so the fix is allowed; append the constraint to `constraints`; set `reopen_used: true`.
3. From then on, a third scheme — or merely a preference for another implementation — is folded back into the theme and does not reopen again.

Without this exit, a scheme that cannot survive deployment would be protected by the freeze itself.

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

`settled_claims` holds every rejected, waived, and backlogged entry, with its evidence or reason prefixed `rejected:`, `waived:`, or `backlog:`. Frozen themes add a `waived: theme frozen; constraints: ...` entry carrying the theme's identity, which is how the gate recognises a re-worded same-object claim as old. The gate uses the first three fields to compute novelty, so a re-raised settled claim — parked or not — does not look like progress.

Un-setting an entry is a deliberate act: remove it from `settled_claims` only when the Reviewer supplies evidence that did not exist when it was settled, and say so to the user. Never silently drop a waiver to make the loop look converged.
