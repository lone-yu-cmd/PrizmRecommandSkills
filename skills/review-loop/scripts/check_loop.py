#!/usr/bin/env python3
"""
Loop Exit Gatekeeper for review-loop skill.

Reads loop state from stdin (JSON) and determines whether the review loop can exit.

Usage:
    echo '{"reviewer_result": "PASS", "accepted_count": 0}' | python scripts/check_loop.py

Input JSON schema:
    {
        "reviewer_result": "PASS" | "NEEDS_FIXES",
        "accepted_count": int  # number of findings accepted by main agent
    }

Output JSON schema:
    {
        "endLoop": bool,
        "reason": str  # human-readable explanation
    }

Exit conditions (endLoop=true):
    - Reviewer returned PASS (no findings)
    - Reviewer returned NEEDS_FIXES but accepted_count == 0 (all findings rejected)
"""

import json
import sys


def check_exit_condition(data):
    reviewer_result = data.get("reviewer_result")
    accepted_count = data.get("accepted_count", 0)

    if reviewer_result == "PASS":
        result = {"endLoop": True, "reason": "Reviewer returned PASS"}
    elif accepted_count == 0:
        result = {"endLoop": True, "reason": "All findings rejected by main agent"}
    else:
        result = {
            "endLoop": False,
            "reason": f"{accepted_count} findings accepted, continuing loop",
        }

    return result


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"endLoop": False, "reason": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    result = check_exit_condition(data)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
