# Loop Exit Gate Contract

Read this when you first call the gate, when a call comes back `Rejected:`, or when Python is unavailable and the gate must be applied by hand.

`$SKILL_DIR` is the directory containing this skill's SKILL.md. Always invoke with an absolute path — the current working directory is the user's project, not the skill:

```bash
python3 "$SKILL_DIR/scripts/check_loop.py"
```

After any change to the gate or to this contract, run `python3 "$SKILL_DIR/scripts/test_check_loop.py"`: it exercises every verdict path, the rejection paths, novelty computation, and history continuity.

## Input

| Field | Type | Required | Meaning |
|---|---|---|---|
| `reviewer_result` | `"PASS"` \| `"NEEDS_FIXES"` | yes | Reviewer verdict. |
| `round` | int | yes | 1-based current round. `0` is rejected — no review has run. |
| `claim_keys` | `[str]` | yes | This round's distinct claims as `<location> \| <dimension> \| <short problem>`. Empty only for `PASS`. |
| `accepted_count` | int | yes | Claims to fix now. |
| `rejected_count` | int | yes | Claims disproved with evidence. |
| `waived_count` | int | yes | Claims accepted but deliberately not fixed. |
| `backlog_count` | int | yes | Claims parked outside the loop. |
| `verification` | `"passed"` \| `"failed"` \| `"not-run"` | no | Outcome of the last `verify_cmd` run — on round 1 that is the pre-loop baseline. Default `not-run`. |
| `novelty_history` | `[int]` | yes | New-claim count per completed round. Start `[]`, pass back what the gate returned. |
| `settled_claims` | `[str]` | no | Settled entries: `<location> \| <dimension> \| <problem> \| <evidence or reason>`. Start `[]`. |
| `max_rounds` | int | no | Review-round ceiling. Default `10`. |
| `reviewer_mode` | `"isolated"` \| `"self"` | no | Default `isolated`; `self` yields `independent: false`. |

The four counts must sum to `len(claim_keys)`. The gate rejects the call otherwise — a claim with no status is an unadjudicated claim.

## Output

| Field | Meaning |
|---|---|
| `endLoop` | The only exit authority. |
| `verdict` | `PASS` \| `PASS_UNVERIFIED` \| `VERIFICATION_FAILED` \| `ALL_REJECTED` \| `NEEDS_FIXES` \| `null`. Render verbatim. |
| `exitReason` | `reviewer-pass` \| `reviewer-pass-unverified` \| `verification-failed` \| `no-accepted-claims` \| `max-rounds` \| `null`. |
| `reason` | Human-readable explanation, including counts. |
| `independent` | `false` when the main agent reviewed its own work. |
| `divergenceWarning` | New-claim counts rose across the last three rounds. |
| `dimensions` | The review dimensions for the next round: all five, or `goal-alignment` + `defect` once diverging. |
| `newClaimCount` | Claims this round that were not already settled. |
| `counts` | Echo of the four adjudication counts. |
| `historyRepaired` | Stale entries beyond `round - 1` were dropped. |
| `novelty_history` | Carry into the next call unchanged. |
| `settled_claims` | Carry into the next call unchanged, and into the next Reviewer prompt. |

## Verdict order

A `Rejected:` call is bad input, not a verdict: fix the fields and call again.

1. Invalid or inconsistent input → `endLoop: false`, `verdict: null`.
2. `PASS` + `verification: "failed"` → `VERIFICATION_FAILED`. A failing check outranks a reviewer verdict; the loop ends and the failure is the headline.
3. `PASS` + `verification: "not-run"` → `PASS_UNVERIFIED`. No check exists, so the review is labelled unverified rather than proven.
4. `PASS` + `verification: "passed"` → `PASS`.
5. `accepted_count == 0` → `ALL_REJECTED`. Nothing will be fixed: the claims were rejected, waived, or backlogged. Not a clean pass.
6. `round >= max_rounds` → `NEEDS_FIXES`, with the accepted-but-unfixed count.
7. Otherwise → continue.

`PASS` requires empty `claim_keys` and all four counts at zero.

## Continuity and novelty

`novelty_history` must hold exactly `round - 1` entries. Fewer is rejected — claiming round 3 requires the history that rounds 1 and 2 produced. More is truncated and flagged `historyRepaired`.

Novelty is computed, not reported: the gate compares each claim identity against the first three fields of every `settled_claims` entry, ignoring case and whitespace. A settled claim that comes back does not count as new.

Divergence fires when the last three novelty counts are strictly increasing — that means the Reviewer keeps finding genuinely fresh problems, so the loop is expanding rather than converging. The gate then pins `dimensions` to `goal-alignment` and `defect`: style and consistency hunting stops before the round budget is spent.

## Worked example

Round 1: five claims, two accepted, one rejected, two backlogged, no verification yet.

```bash
echo '{"reviewer_result":"NEEDS_FIXES","round":1,
"claim_keys":["src/a.ts:10 | defect | null deref","src/a.ts:22 | defect | unchecked error",
"src/b.ts:5 | consistency | mixed naming","src/c.ts:9 | completeness | missing test",
"src/d.ts:1 | consistency | unused import"],
"accepted_count":2,"rejected_count":1,"waived_count":0,"backlog_count":2,
"verification":"not-run","novelty_history":[],"settled_claims":[],
"max_rounds":10,"reviewer_mode":"isolated"}' | python3 "$SKILL_DIR/scripts/check_loop.py"
# {"endLoop": false, "newClaimCount": 5, "novelty_history": [5], "dimensions": [...five...]}
```

Round 2: the fixes were applied and `verify_cmd` passed; the Reviewer raised two claims, one accepted, one rejected with evidence.

```bash
echo '{"reviewer_result":"NEEDS_FIXES","round":2,
"claim_keys":["src/a.ts:10 | defect | null deref","src/e.ts:3 | consistency | route naming"],
"accepted_count":1,"rejected_count":1,"waived_count":0,"backlog_count":0,
"verification":"passed","novelty_history":[5],
"settled_claims":["src/e.ts:3 | consistency | route naming | existing router uses this form; see src/routes/index.ts:12"],
"max_rounds":10,"reviewer_mode":"isolated"}' | python3 "$SKILL_DIR/scripts/check_loop.py"
# {"endLoop": false, "newClaimCount": 1, "novelty_history": [5, 1], ...}
```

Round 3: clean review, verification passed.

```bash
echo '{"reviewer_result":"PASS","round":3,"claim_keys":[],
"accepted_count":0,"rejected_count":0,"waived_count":0,"backlog_count":0,
"verification":"passed","novelty_history":[5,1],
"settled_claims":["src/e.ts:3 | consistency | route naming | existing router uses this form; see src/routes/index.ts:12"],
"max_rounds":10,"reviewer_mode":"isolated"}' | python3 "$SKILL_DIR/scripts/check_loop.py"
# {"endLoop": true, "verdict": "PASS", "exitReason": "reviewer-pass", "newClaimCount": 0}
```

## Text mode (no Python)

Apply the same rules by hand and state the verdict in the transcript:

1. Reject calls with `round < 1`, an unknown enum, non-integer counts, counts that do not sum to the claim count, a malformed claim or waiver entry, `PASS` with claims, `NEEDS_FIXES` without claims, or a novelty history whose length is not `round - 1`.
2. Verdict in this order: `VERIFICATION_FAILED` (PASS + failed), `PASS_UNVERIFIED` (PASS + not-run), `PASS`, `ALL_REJECTED` (nothing accepted), `NEEDS_FIXES` (round limit), otherwise continue.
3. Compute novelty against the first three fields of each settled entry; append exactly one entry per round.
4. When the last three novelty counts rise, reduce the review dimensions to goal-alignment and defect.

Declaring a verdict without running a round is invalid in text mode exactly as it is in script mode.
