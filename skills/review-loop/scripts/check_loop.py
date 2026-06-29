#!/usr/bin/env python3
"""
Loop Exit Gatekeeper for the review-loop skill.

Stateless design: all loop state is passed via stdin and returned via stdout.
The caller tracks `findings_history`, `round`, and `max_rounds` between calls.
No runtime files are created — the script is a pure function over JSON.

The model supplies the current round in each call. The gate records exactly one
findings count per round by updating the entry at index `round - 1`; repeated
calls for the same round update that entry instead of appending duplicates.

Usage:
    echo '{"reviewer_result":"NEEDS_FIXES","accepted_count":2,"findings_count":5,"round":1,"findings_history":[],"max_rounds":3}' | python3 check_loop.py

Input JSON schema:
    {
        "reviewer_result": "PASS" | "NEEDS_FIXES",
        "accepted_count": int,
        "findings_count": int,
        "round": int,
        "findings_history": [int, ...],
        "max_rounds": int
    }

Output JSON schema:
    {
        "endLoop": bool,
        "reason": str,
        "verdict": "PASS" | "NEEDS_FIXES" | null,
        "round": int,
        "maxRounds": int,
        "divergenceWarning": bool,
        "findings_history": [int, ...]
    }

Exit conditions (checked in order):
    1. Invalid or inconsistent input        → endLoop=false
    2. Reviewer returned PASS               → endLoop=true, verdict=PASS
    3. All findings rejected (accepted=0)   → endLoop=true, verdict=PASS
    4. Max rounds reached (round >= limit)  → endLoop=true, verdict=NEEDS_FIXES
    5. Otherwise                            → endLoop=false

Divergence detection:
    If findings_count strictly increases for 3 consecutive rounds, set divergenceWarning=true.
    This is a warning only — it does not force loop exit.
"""

import json
import sys

DEFAULT_MAX_ROUNDS = 10
ALLOWED_REVIEWER_RESULTS = {"PASS", "NEEDS_FIXES"}


def is_non_negative_int(value):
    """Return True for non-bool integers greater than or equal to zero."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def error_response(reason, current_round=0, max_rounds=DEFAULT_MAX_ROUNDS, findings_history=None):
    """Build a standard non-exiting rejection response."""
    return {
        "endLoop": False,
        "reason": reason,
        "verdict": None,
        "round": current_round,
        "maxRounds": max_rounds,
        "divergenceWarning": False,
        "findings_history": findings_history or [],
    }


def record_round_findings(findings_history, findings_count, current_round):
    """Record one findings count per 1-based round."""
    if current_round < 1:
        return findings_history

    round_index = current_round - 1
    if len(findings_history) <= round_index:
        findings_history.extend([0] * (round_index - len(findings_history)))
        findings_history.append(findings_count)
    else:
        findings_history[round_index] = findings_count

    return findings_history


def check_divergence(findings_history):
    """Return True if the last 3 entries in findings_history are strictly increasing."""
    if len(findings_history) < 3:
        return False
    last_three = findings_history[-3:]
    return last_three[0] < last_three[1] < last_three[2]


def check_exit_condition(data):
    """Determine whether the loop should exit. Pure function — no side effects."""
    if not isinstance(data, dict):
        return error_response("Rejected: input must be a JSON object.")

    raw_history = data.get("findings_history", [])
    if not isinstance(raw_history, list) or not all(is_non_negative_int(item) for item in raw_history):
        return error_response("Rejected: findings_history must be a list of non-negative integers.")
    findings_history = list(raw_history)

    max_rounds = data.get("max_rounds", DEFAULT_MAX_ROUNDS)
    if not is_non_negative_int(max_rounds) or max_rounds < 1:
        return error_response(
            "Rejected: max_rounds must be a positive integer.",
            findings_history=findings_history,
        )

    current_round = data.get("round", 0)
    if not is_non_negative_int(current_round) or current_round < 1:
        return error_response(
            "Rejected: cannot declare a verdict without spawning a Reviewer. Round must be >= 1.",
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    accepted_count = data.get("accepted_count", 0)
    findings_count = data.get("findings_count", 0)
    if not is_non_negative_int(accepted_count):
        return error_response(
            "Rejected: accepted_count must be a non-negative integer.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )
    if not is_non_negative_int(findings_count):
        return error_response(
            "Rejected: findings_count must be a non-negative integer.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    reviewer_result = data.get("reviewer_result")
    if reviewer_result not in ALLOWED_REVIEWER_RESULTS:
        return error_response(
            "Rejected: reviewer_result must be PASS or NEEDS_FIXES.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    if reviewer_result == "PASS" and (accepted_count != 0 or findings_count != 0):
        return error_response(
            "Rejected: PASS must have accepted_count=0 and findings_count=0.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    if reviewer_result == "NEEDS_FIXES" and findings_count == 0:
        return error_response(
            "Rejected: NEEDS_FIXES with 0 findings is inconsistent. Reviewer must report actual findings count.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    if accepted_count > findings_count:
        return error_response(
            "Rejected: accepted_count cannot exceed findings_count.",
            current_round=current_round,
            max_rounds=max_rounds,
            findings_history=findings_history,
        )

    findings_history = record_round_findings(findings_history, findings_count, current_round)
    divergence_warning = check_divergence(findings_history)

    # Condition 1: Reviewer returned PASS
    if reviewer_result == "PASS":
        return {
            "endLoop": True,
            "reason": f"Round {current_round}: Reviewer returned PASS",
            "verdict": "PASS",
            "round": current_round,
            "maxRounds": max_rounds,
            "divergenceWarning": False,
            "findings_history": findings_history,
        }

    # Condition 2: All findings rejected
    if accepted_count == 0:
        return {
            "endLoop": True,
            "reason": f"Round {current_round}: all findings rejected by main agent",
            "verdict": "PASS",
            "round": current_round,
            "maxRounds": max_rounds,
            "divergenceWarning": False,
            "findings_history": findings_history,
        }

    # Condition 3: Max rounds reached
    if current_round >= max_rounds:
        return {
            "endLoop": True,
            "reason": f"Hard limit: max {max_rounds} rounds reached",
            "verdict": "NEEDS_FIXES",
            "round": current_round,
            "maxRounds": max_rounds,
            "divergenceWarning": divergence_warning,
            "findings_history": findings_history,
        }

    # Condition 4: Continue loop
    next_round = current_round + 1
    return {
        "endLoop": False,
        "reason": f"Round {current_round}: {accepted_count} findings accepted, continuing to round {next_round}",
        "verdict": None,
        "round": current_round,
        "maxRounds": max_rounds,
        "divergenceWarning": divergence_warning,
        "findings_history": findings_history,
    }


def main():
    # Read input from stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(
            json.dumps(
                {
                    "endLoop": False,
                    "reason": f"Invalid JSON input: {e}",
                    "verdict": None,
                    "round": 0,
                    "maxRounds": DEFAULT_MAX_ROUNDS,
                    "divergenceWarning": False,
                    "findings_history": [],
                }
            )
        )
        sys.exit(1)

    result = check_exit_condition(data)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
