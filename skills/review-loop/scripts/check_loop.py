#!/usr/bin/env python3
"""
Loop exit gate for the review-loop skill (claim-level contract).

Design goals:
- The gate decides the exit, not the model. Every branch returns a verdict or an
  explicit rejection; there is no "self-declared pass" path.
- Findings are claims with stable keys, so novelty is computed mechanically
  instead of trusting a self-reported count.
- Convergence is measured on *new* claims, not on volume: re-raising a settled
  claim must not look like progress.
- A PASS cannot outrank a failed verification, and a PASS without a verification
  run is labelled honestly instead of being reported as assurance.

State is still not stored here: the caller persists the ledger (see
references/claim-ledger.md) and passes `novelty_history` / `settled_claims`
back on every call.

Usage:
    echo '{"reviewer_result":"PASS","round":1,"claim_keys":[],"accepted_count":0,
           "rejected_count":0,"waived_count":0,"backlog_count":0,
           "verification":"passed","novelty_history":[],"settled_claims":[],
           "max_rounds":10,"reviewer_mode":"isolated"}' \
      | python3 "$SKILL_DIR/scripts/check_loop.py"

Input:
    reviewer_result  "PASS" | "NEEDS_FIXES"
    round            int >= 1, current 1-based review round
    claim_keys       [str] this round's distinct claims, each
                     "<location> | <dimension> | <short problem>"
    accepted_count   int, claims to fix now
    rejected_count   int, claims disproved with evidence
    waived_count     int, claims accepted but deliberately not fixed
    backlog_count    int, medium/low claims parked outside the loop
    verification     "passed" | "failed" | "not-run" (last verify_cmd run)
    novelty_history  [int] new-claim count per completed round
    settled_claims  [str] settled entries
                     "<location> | <dimension> | <problem> | <evidence or reason>"
    max_rounds       int, default 10
    reviewer_mode    "isolated" | "self"

Output:
    endLoop, verdict, exitReason, reason, round, maxRounds, independent,
    divergenceWarning, dimensions, historyRepaired, newClaimCount,
    counts, novelty_history, settled_claims

Verdicts: PASS | PASS_UNVERIFIED | VERIFICATION_FAILED | ALL_REJECTED |
          NEEDS_FIXES | null (input rejected or loop continues)

Exit order:
    1. invalid input                         → endLoop=false
    2. PASS with failed verification         → VERIFICATION_FAILED
    3. PASS without a verification run       → PASS_UNVERIFIED
    4. PASS                                  → PASS
    5. nothing accepted (rejected/waived/backlog) → ALL_REJECTED
    6. round >= max_rounds with accepted work     → NEEDS_FIXES
    7. otherwise                                  → continue

Divergence: new-claim counts strictly increasing across the last three rounds
(two consecutive rises). It sets a warning and pins `dimensions` to
goal-alignment + defect so the next round stops hunting style nits.
"""

import argparse
import json
from pathlib import Path
import sys

DEFAULT_MAX_ROUNDS = 10
ALLOWED_REVIEWER_RESULTS = {"PASS", "NEEDS_FIXES"}
ALLOWED_REVIEWER_MODES = {"isolated", "self"}
ALLOWED_VERIFICATION = {"passed", "failed", "not-run"}
COUNT_FIELDS = ("accepted_count", "rejected_count", "waived_count", "backlog_count")
FULL_DIMENSIONS = ["goal-alignment", "defect", "completeness", "consistency", "security"]
REDUCED_DIMENSIONS = ["goal-alignment", "defect"]


def is_non_negative_int(value):
    """Return True for non-bool integers greater than or equal to zero."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def normalize(text):
    """Normalize a claim component so whitespace and case do not defeat matching."""
    return " ".join(text.lower().split())


def split_entry(entry):
    """Split a pipe-delimited claim or waiver entry into its parts."""
    return [part.strip() for part in entry.split("|")]


def claim_identity(entry):
    """Return the 3-field identity used for dedupe and novelty, or None if malformed."""
    parts = split_entry(entry)
    if len(parts) != 3:
        return None
    return normalize(" | ".join(parts))


def settled_identity(entry):
    """Return the 3-field identity of a settled entry, or None if it lacks a reason."""
    parts = split_entry(entry)
    if len(parts) != 4:
        return None
    return normalize(" | ".join(parts[:3]))


def settled_identities(settled_claims):
    """Collect the identities of every already-settled entry."""
    settled = set()
    for entry in settled_claims:
        identity = settled_identity(entry)
        if identity:
            settled.add(identity)
    return settled


def error_response(
    reason,
    current_round=0,
    max_rounds=DEFAULT_MAX_ROUNDS,
    novelty_history=None,
    settled_claims=None,
    independent=True,
    history_repaired=False,
    counts=None,
):
    """Build a standard non-exiting rejection response."""
    return {
        "endLoop": False,
        "verdict": None,
        "exitReason": None,
        "reason": reason,
        "round": current_round,
        "maxRounds": max_rounds,
        "independent": independent,
        "divergenceWarning": False,
        "dimensions": list(FULL_DIMENSIONS),
        "historyRepaired": history_repaired,
        "newClaimCount": 0,
        "counts": dict(counts or {}),
        "novelty_history": list(novelty_history or []),
        "settled_claims": list(settled_claims or []),
    }


def check_divergence(novelty_history):
    """True when a delta round produces strictly more new claims than the prior round, or three rounds fail to decrease."""
    if len(novelty_history) >= 2 and novelty_history[-1] > novelty_history[-2]:
        return True
    if (
        len(novelty_history) >= 3
        and novelty_history[-1] > 0
        and novelty_history[-3] <= novelty_history[-2] <= novelty_history[-1]
    ):
        return True
    return False


def check_exit_condition(data):
    """Determine whether the loop should exit. Pure function, no side effects."""
    if not isinstance(data, dict):
        return error_response("Rejected: input must be a JSON object.")

    reviewer_mode = data.get("reviewer_mode", "isolated")
    if reviewer_mode not in ALLOWED_REVIEWER_MODES:
        return error_response("Rejected: reviewer_mode must be isolated or self.")
    independent = reviewer_mode == "isolated"

    max_rounds = data.get("max_rounds", DEFAULT_MAX_ROUNDS)
    if not is_non_negative_int(max_rounds) or max_rounds < 1:
        return error_response(
            "Rejected: max_rounds must be a positive integer.", independent=independent
        )

    current_round = data.get("round", 0)
    if not is_non_negative_int(current_round) or current_round < 1:
        return error_response(
            "Rejected: cannot declare a verdict without running a review round. Round must be >= 1.",
            max_rounds=max_rounds,
            independent=independent,
        )

    raw_settled = data.get("settled_claims", [])
    if not isinstance(raw_settled, list) or not all(isinstance(item, str) for item in raw_settled):
        return error_response(
            "Rejected: settled_claims must be a list of strings.",
            current_round=current_round,
            max_rounds=max_rounds,
            independent=independent,
        )
    if any(settled_identity(entry) is None for entry in raw_settled):
        return error_response(
            "Rejected: every settled_claims entry needs exactly four fields: "
            "'<location> | <dimension> | <problem> | <evidence or reason>' — do not use '|' inside a field.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
        )

    raw_keys = data.get("claim_keys", [])
    if not isinstance(raw_keys, list) or not all(isinstance(item, str) for item in raw_keys):
        return error_response(
            "Rejected: claim_keys must be a list of strings.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
        )
    if any(claim_identity(entry) is None for entry in raw_keys):
        return error_response(
            "Rejected: every claim key needs exactly three fields: "
            "'<location> | <dimension> | <short problem>' — do not use '|' inside a field.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
        )

    counts = {}
    for field in COUNT_FIELDS:
        value = data.get(field, 0)
        if not is_non_negative_int(value):
            return error_response(
                f"Rejected: {field} must be a non-negative integer.",
                current_round=current_round,
                max_rounds=max_rounds,
                settled_claims=raw_settled,
                independent=independent,
            )
        counts[field] = value

    if sum(counts.values()) != len(raw_keys):
        return error_response(
            "Rejected: accepted + rejected + waived + backlog must equal the number of claim keys "
            f"({sum(counts.values())} != {len(raw_keys)}).",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )

    raw_history = data.get("novelty_history", [])
    if not isinstance(raw_history, list) or not all(is_non_negative_int(item) for item in raw_history):
        return error_response(
            "Rejected: novelty_history must be a list of non-negative integers.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )
    novelty_history = list(raw_history)

    reviewer_result = data.get("reviewer_result")
    if reviewer_result not in ALLOWED_REVIEWER_RESULTS:
        return error_response(
            "Rejected: reviewer_result must be PASS or NEEDS_FIXES.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )

    verification = data.get("verification", "not-run")
    if verification not in ALLOWED_VERIFICATION:
        return error_response(
            "Rejected: verification must be passed, failed, or not-run.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )

    if reviewer_result == "PASS" and (raw_keys or any(counts.values())):
        return error_response(
            "Rejected: PASS must have no claim keys and zero counts.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )

    if reviewer_result == "NEEDS_FIXES" and not raw_keys:
        return error_response(
            "Rejected: NEEDS_FIXES with no claim keys is inconsistent. Report the real claims.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )

    # History continuity: exactly one novelty entry per completed round.
    expected_history_len = current_round - 1
    if len(novelty_history) < expected_history_len:
        return error_response(
            f"Rejected: novelty_history has {len(novelty_history)} entries but round {current_round} "
            f"requires {expected_history_len}. Pass back the novelty_history from the previous gate call.",
            current_round=current_round,
            max_rounds=max_rounds,
            settled_claims=raw_settled,
            independent=independent,
            counts=counts,
        )
    history_repaired = len(novelty_history) > expected_history_len
    if history_repaired:
        novelty_history = novelty_history[:expected_history_len]

    settled = settled_identities(raw_settled)
    new_claim_count = len(
        {claim_identity(entry) for entry in raw_keys if claim_identity(entry) not in settled}
    )
    novelty_history.append(new_claim_count)
    divergence_warning = check_divergence(novelty_history)
    dimensions = list(REDUCED_DIMENSIONS) if divergence_warning else list(FULL_DIMENSIONS)

    common = {
        "endLoop": True,
        "round": current_round,
        "maxRounds": max_rounds,
        "independent": independent,
        "divergenceWarning": divergence_warning,
        "dimensions": dimensions,
        "historyRepaired": history_repaired,
        "newClaimCount": new_claim_count,
        "counts": counts,
        "novelty_history": novelty_history,
        "settled_claims": raw_settled,
    }

    if reviewer_result == "PASS":
        if verification == "failed":
            return {
                **common,
                "verdict": "VERIFICATION_FAILED",
                "exitReason": "verification-failed",
                "reason": (
                    f"Round {current_round}: Reviewer returned PASS but the last verification run failed. "
                    "A failed check outranks a reviewer verdict."
                ),
            }
        if verification == "not-run":
            return {
                **common,
                "verdict": "PASS_UNVERIFIED",
                "exitReason": "reviewer-pass-unverified",
                "reason": (
                    f"Round {current_round}: Reviewer returned PASS with no verification run. "
                    "The review is unverified, not proven."
                ),
            }
        return {
            **common,
            "verdict": "PASS",
            "exitReason": "reviewer-pass",
            "reason": f"Round {current_round}: Reviewer returned PASS and verification passed",
        }

    if counts["accepted_count"] == 0:
        if verification == "failed":
            return {
                **common,
                "verdict": "VERIFICATION_FAILED",
                "exitReason": "verification-failed",
                "reason": (
                    f"Round {current_round}: no claim was accepted to fix, and the last verification run failed. "
                    "A failed check outranks a no-accepted-claims exit."
                ),
            }
        if (
            counts["rejected_count"] == 0
            and counts["waived_count"] == 0
            and counts["backlog_count"] > 0
        ):
            if verification == "not-run":
                return {
                    **common,
                    "verdict": "PASS_UNVERIFIED",
                    "exitReason": "backlog-only-unverified",
                    "reason": (
                        f"Round {current_round}: all {counts['backlog_count']} claim(s) were non-blocking backlog items "
                        "with no verification run."
                    ),
                }
            return {
                **common,
                "verdict": "PASS",
                "exitReason": "backlog-only-pass",
                "reason": (
                    f"Round {current_round}: all {counts['backlog_count']} claim(s) were non-blocking backlog items "
                    "and verification passed"
                ),
            }
        return {
            **common,
            "verdict": "ALL_REJECTED",
            "exitReason": "no-accepted-claims",
            "reason": (
                f"Round {current_round}: no claim was accepted "
                f"({counts['rejected_count']} rejected, {counts['waived_count']} waived, "
                f"{counts['backlog_count']} backlogged)"
            ),
        }

    if current_round >= max_rounds:
        return {
            **common,
            "verdict": "NEEDS_FIXES",
            "exitReason": "max-rounds",
            "reason": (
                f"Hard limit: max {max_rounds} rounds reached with {counts['accepted_count']} "
                "accepted claim(s) not yet fixed"
            ),
        }

    return {
        **common,
        "endLoop": False,
        "verdict": None,
        "exitReason": None,
        "reason": (
            f"Round {current_round}: {counts['accepted_count']} claim(s) accepted, "
            f"{new_claim_count} new; continuing to round {current_round + 1}"
        ),
    }


STATE_SYNC_KEYS = (
    "round",
    "novelty_history",
    "settled_claims",
    "max_rounds",
    "reviewer_mode",
    "verification",
)


def load_and_merge_state(data, state_path):
    """Merge missing caller-state fields from state_path into data."""
    if not state_path or not state_path.exists():
        return None
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state_data, dict):
        raise ValueError("state file must contain a JSON object")
    if isinstance(data, dict):
        for key in STATE_SYNC_KEYS:
            if key not in data and key in state_data:
                data[key] = state_data[key]
    return state_data


def persist_state(state_path, state_data, data, result):
    """Write updated gate fields back to state_path when the call succeeded."""
    if state_path is None or state_data is None:
        return
    reason = str(result.get("reason", ""))
    if result.get("verdict") is None and reason.startswith("Rejected:"):
        return
    state_data["novelty_history"] = result["novelty_history"]
    state_data["settled_claims"] = result["settled_claims"]
    state_data["dimensions"] = result["dimensions"]
    state_data["verification"] = data.get(
        "verification", state_data.get("verification", "not-run")
    )
    state_path.write_text(json.dumps(state_data, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state-file",
        type=Path,
        default=None,
        help="Optional state.json path to read missing loop fields from and update in place.",
    )
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(
            json.dumps(
                {
                    "endLoop": False,
                    "verdict": None,
                    "exitReason": None,
                    "reason": f"Invalid JSON input: {e}",
                    "round": 0,
                    "maxRounds": DEFAULT_MAX_ROUNDS,
                    "independent": True,
                    "divergenceWarning": False,
                    "dimensions": list(FULL_DIMENSIONS),
                    "historyRepaired": False,
                    "newClaimCount": 0,
                    "counts": {},
                    "novelty_history": [],
                    "settled_claims": [],
                }
            )
        )
        sys.exit(1)

    state_data = None
    if args.state_file is not None:
        try:
            state_data = load_and_merge_state(data, args.state_file)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            print(json.dumps(error_response(f"Invalid state file: {e}")))
            sys.exit(1)

    result = check_exit_condition(data)
    persist_state(args.state_file, state_data, data, result)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
