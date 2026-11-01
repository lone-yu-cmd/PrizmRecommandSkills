#!/usr/bin/env python3
"""
Contract tests for check_loop.py.

Run after touching the gate or its contract:
    python3 "$SKILL_DIR/scripts/test_check_loop.py"

Exits 0 when every case matches, 1 otherwise. No external dependencies.
"""

import json
import subprocess
import sys
from pathlib import Path

GATE = Path(__file__).with_name("check_loop.py")


def call(payload):
    result = subprocess.run(
        [sys.executable, str(GATE)], input=json.dumps(payload), capture_output=True, text=True
    )
    return result.returncode, (json.loads(result.stdout) if result.stdout.strip() else None)


def claims(*keys, accepted=0, rejected=0, waived=0, backlog=0, **overrides):
    payload = {
        "reviewer_result": "NEEDS_FIXES",
        "round": 1,
        "claim_keys": list(keys),
        "accepted_count": accepted,
        "rejected_count": rejected,
        "waived_count": waived,
        "backlog_count": backlog,
        "verification": "not-run",
        "novelty_history": [],
        "settled_claims": [],
        "max_rounds": 10,
        "reviewer_mode": "isolated",
    }
    payload.update(overrides)
    return payload


PASS = {"reviewer_result": "PASS", "claim_keys": [], "accepted_count": 0}

CASES = [
    (
        "PASS with a passing verification",
        claims(**PASS, verification="passed"),
        lambda o: o["endLoop"] and o["verdict"] == "PASS" and len(o["dimensions"]) == 5,
    ),
    (
        "PASS without a verification run is labelled unverified",
        claims(**PASS, verification="not-run"),
        lambda o: o["verdict"] == "PASS_UNVERIFIED",
    ),
    (
        "failed verification outranks a PASS",
        claims(**PASS, verification="failed"),
        lambda o: o["endLoop"] and o["verdict"] == "VERIFICATION_FAILED",
    ),
    (
        "accepted work continues",
        claims("src/a.ts:10 | defect | null deref", accepted=1),
        lambda o: not o["endLoop"] and o["newClaimCount"] == 1 and o["novelty_history"] == [1],
    ),
    (
        "waived claims end as ALL_REJECTED",
        claims("src/a.ts:10 | defect | null deref", waived=1, verification="passed"),
        lambda o: o["verdict"] == "ALL_REJECTED",
    ),
    (
        "backlogged claims end as ALL_REJECTED",
        claims("src/a.ts:10 | defect | null deref", backlog=1),
        lambda o: o["verdict"] == "ALL_REJECTED",
    ),
    (
        "round limit yields NEEDS_FIXES",
        claims("src/a.ts:10 | defect | x", accepted=1, round=3, max_rounds=3, novelty_history=[2, 1]),
        lambda o: o["verdict"] == "NEEDS_FIXES" and "not yet fixed" in o["reason"],
    ),
    (
        "a settled claim is not novelty",
        claims(
            "src/a.ts:10 | Defect | null   deref",
            rejected=1,
            round=2,
            novelty_history=[1],
            settled_claims=["src/a.ts:10 | defect | null deref | impossible state, see src/a.ts:20"],
        ),
        lambda o: o["newClaimCount"] == 0 and o["novelty_history"] == [1, 0],
    ),
    (
        "rising novelty narrows the dimensions",
        claims(
            "a | defect | a",
            "b | defect | b",
            "c | defect | c",
            "d | defect | d",
            accepted=4,
            round=4,
            novelty_history=[1, 2, 3],
        ),
        lambda o: o["divergenceWarning"] and o["dimensions"] == ["goal-alignment", "defect"],
    ),
    (
        "a short novelty history is rejected",
        claims("a | defect | a", accepted=1, round=3),
        lambda o: o["verdict"] is None and "requires 2" in o["reason"],
    ),
    (
        "stale novelty history is repaired",
        claims("a | defect | a", accepted=1, round=2, novelty_history=[1, 9, 9]),
        lambda o: o["historyRepaired"] and o["novelty_history"] == [1, 1],
    ),
    (
        "counts must sum to the claim count",
        claims("a | defect | a"),
        lambda o: o["verdict"] is None and "must equal the number of claim keys" in o["reason"],
    ),
    (
        "PASS cannot carry claims",
        claims("a | defect | a", accepted=1, reviewer_result="PASS"),
        lambda o: o["verdict"] is None and "PASS must have no claim keys" in o["reason"],
    ),
    (
        "NEEDS_FIXES cannot be empty",
        claims(accepted=0),
        lambda o: o["verdict"] is None and "no claim keys is inconsistent" in o["reason"],
    ),
    (
        "verification must be a known state",
        claims("a | defect | a", accepted=1, verification="maybe"),
        lambda o: o["verdict"] is None and "verification must be" in o["reason"],
    ),
    (
        "claim identity needs three fields",
        claims("src/a.ts:10 | defect"),
        lambda o: o["verdict"] is None and "claim key needs" in o["reason"],
    ),
    (
        "settled entries need four fields of content",
        claims("a | defect | a", accepted=1, settled_claims=["src/a.ts:10 | defect"]),
        lambda o: o["verdict"] is None and "settled_claims entry needs" in o["reason"],
    ),
    (
        "a claim key with a stray pipe is rejected",
        claims("src/a.ts:10 | defect | null deref | stray note", accepted=1),
        lambda o: o["verdict"] is None and "exactly three fields" in o["reason"],
    ),
    (
        "booleans are not counts",
        claims("a | defect | a", accepted=True),
        lambda o: o["verdict"] is None and "accepted_count" in o["reason"],
    ),
    (
        "self review is not independent",
        claims("a | defect | a", accepted=1, reviewer_mode="self"),
        lambda o: o["independent"] is False,
    ),
    (
        "counts are echoed for the summary",
        claims("a | defect | x", "b | defect | y", "c | consistency | z", accepted=2, backlog=1),
        lambda o: not o["endLoop"] and o["counts"]["accepted_count"] == 2 and o["newClaimCount"] == 3,
    ),
]


def main():
    failures = 0
    for name, payload, check in CASES:
        _, output = call(payload)
        ok = output is not None and check(output)
        print(("PASS" if ok else "FAIL"), name, "" if ok else output)
        failures += 0 if ok else 1

    result = subprocess.run(
        [sys.executable, str(GATE)], input="{not json", capture_output=True, text=True
    )
    output = json.loads(result.stdout)
    ok = result.returncode == 1 and output["endLoop"] is False and output["verdict"] is None
    print(("PASS" if ok else "FAIL"), "invalid JSON exits non-zero without a verdict")
    failures += 0 if ok else 1

    print(f"{len(CASES) + 1} cases, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
