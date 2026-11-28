#!/usr/bin/env python3
"""Unit tests for helper functions in check_loop.py."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_loop


class TestNormalizationAndIdentity(unittest.TestCase):
    """Tests for normalize, split_entry, claim_identity, settled_identity, and helpers."""

    def test_normalize_lowercases_and_collapses_whitespace(self):
        self.assertEqual(check_loop.normalize("  Null   Deref\tIn\nAuth  "), "null deref in auth")
        self.assertEqual(check_loop.normalize("   "), "")
        self.assertEqual(check_loop.normalize(""), "")
        self.assertEqual(check_loop.normalize("AlreadyNormal"), "alreadynormal")

    def test_split_entry_trims_parts(self):
        self.assertEqual(
            check_loop.split_entry(" src/a.py:10 | defect | null check "),
            ["src/a.py:10", "defect", "null check"],
        )
        self.assertEqual(
            check_loop.split_entry("a|b|c|reason"),
            ["a", "b", "c", "reason"],
        )
        self.assertEqual(check_loop.split_entry("a | | c"), ["a", "", "c"])
        self.assertEqual(check_loop.split_entry("single field"), ["single field"])

    def test_claim_identity_valid_and_malformed(self):
        id1 = check_loop.claim_identity("SRC/a.py:10 | Defect | Null   Deref")
        id2 = check_loop.claim_identity("src/a.py:10|defect|null deref")
        self.assertEqual(id1, "src/a.py:10 | defect | null deref")
        self.assertEqual(id1, id2)

        self.assertIsNone(check_loop.claim_identity("src/a.py:10 | defect"))
        self.assertIsNone(check_loop.claim_identity("single"))
        self.assertIsNone(check_loop.claim_identity("a | b | c | stray"))

    def test_settled_identity_valid_and_malformed(self):
        settled = check_loop.settled_identity(
            "SRC/a.py:10 | Defect | Null   Deref | disproved by guard on line 5"
        )
        claim = check_loop.claim_identity("src/a.py:10 | defect | null deref")
        self.assertEqual(settled, claim)

        self.assertIsNone(check_loop.settled_identity("src/a.py:10 | defect | null deref"))
        self.assertIsNone(check_loop.settled_identity("a | b"))
        self.assertIsNone(check_loop.settled_identity("a | b | c | d | e"))

    def test_settled_identities_collects_and_skips_malformed(self):
        entries = [
            "src/a.py:10 | Defect | Null check | fixed",
            "SRC/A.PY:10 | defect | null   check | duplicate with different reason",
            "malformed | only-two",
            "src/b.py:20 | security | SQLi | parametrized query",
        ]
        self.assertEqual(
            check_loop.settled_identities(entries),
            {
                "src/a.py:10 | defect | null check",
                "src/b.py:20 | security | sqli",
            },
        )

    def test_is_non_negative_int(self):
        self.assertTrue(check_loop.is_non_negative_int(0))
        self.assertTrue(check_loop.is_non_negative_int(42))
        self.assertFalse(check_loop.is_non_negative_int(-1))
        self.assertFalse(check_loop.is_non_negative_int(True))
        self.assertFalse(check_loop.is_non_negative_int(False))
        self.assertFalse(check_loop.is_non_negative_int(1.0))
        self.assertFalse(check_loop.is_non_negative_int("1"))

    def test_error_response_defaults_and_copies(self):
        counts = {"accepted_count": 1}
        history = [1]
        settled = ["a | b | c | d"]
        resp = check_loop.error_response(
            "Rejected: test",
            current_round=2,
            max_rounds=5,
            novelty_history=history,
            settled_claims=settled,
            independent=False,
            history_repaired=True,
            counts=counts,
        )
        counts["accepted_count"] = 99
        history.append(99)
        settled.append("other")
        self.assertEqual(resp["endLoop"], False)
        self.assertIsNone(resp["verdict"])
        self.assertIsNone(resp["exitReason"])
        self.assertEqual(resp["reason"], "Rejected: test")
        self.assertEqual(resp["round"], 2)
        self.assertEqual(resp["maxRounds"], 5)
        self.assertFalse(resp["independent"])
        self.assertTrue(resp["historyRepaired"])
        self.assertEqual(resp["dimensions"], check_loop.FULL_DIMENSIONS)
        self.assertEqual(resp["counts"], {"accepted_count": 1})
        self.assertEqual(resp["novelty_history"], [1])
        self.assertEqual(resp["settled_claims"], ["a | b | c | d"])


class TestCheckDivergence(unittest.TestCase):
    """Tests for check_divergence."""

    def test_short_or_decreasing_histories_do_not_diverge(self):
        for hist in ([], [0], [3], [3, 2], [2, 2], [5, 3, 1], [2, 1, 1], [1, 2, 1]):
            with self.subTest(hist=hist):
                self.assertFalse(check_loop.check_divergence(hist))

    def test_strict_delta_increase_diverges(self):
        for hist in ([0, 1], [1, 2], [4, 2, 3]):
            with self.subTest(hist=hist):
                self.assertTrue(check_loop.check_divergence(hist))

    def test_three_non_decreasing_nonzero_rounds_diverge(self):
        self.assertTrue(check_loop.check_divergence([1, 1, 1]))
        self.assertTrue(check_loop.check_divergence([3, 1, 1, 1]))
        self.assertTrue(check_loop.check_divergence([2, 2, 2]))

    def test_three_zeros_do_not_diverge(self):
        self.assertFalse(check_loop.check_divergence([0, 0, 0]))
        self.assertFalse(check_loop.check_divergence([3, 0, 0, 0]))


class TestStatePersistence(unittest.TestCase):
    """Tests for load_and_merge_state and persist_state."""

    def test_load_and_merge_state_none_or_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            data = {"round": 1}
            self.assertIsNone(check_loop.load_and_merge_state(data, None))
            self.assertIsNone(check_loop.load_and_merge_state(data, missing))
            self.assertEqual(data, {"round": 1})

    def test_load_and_merge_state_merges_only_missing_sync_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            stored = {
                "round": 3,
                "novelty_history": [2, 1],
                "settled_claims": ["a | b | c | d"],
                "max_rounds": 8,
                "reviewer_mode": "self",
                "verification": "passed",
                "dimensions": ["goal-alignment", "defect"],
                "extra_metadata": "keep-in-state-only",
            }
            state_path.write_text(json.dumps(stored), encoding="utf-8")

            data = {"round": 4, "verification": "failed"}
            loaded = check_loop.load_and_merge_state(data, state_path)
            self.assertEqual(loaded, stored)
            self.assertEqual(data["round"], 4)
            self.assertEqual(data["verification"], "failed")
            self.assertEqual(data["novelty_history"], [2, 1])
            self.assertEqual(data["settled_claims"], ["a | b | c | d"])
            self.assertEqual(data["max_rounds"], 8)
            self.assertEqual(data["reviewer_mode"], "self")
            self.assertNotIn("dimensions", data)
            self.assertNotIn("extra_metadata", data)

    def test_load_and_merge_state_invalid_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            non_dict = Path(tmp) / "list.json"
            non_dict.write_text("[1, 2, 3]", encoding="utf-8")
            with self.assertRaises(ValueError):
                check_loop.load_and_merge_state({}, non_dict)

            bad_json = Path(tmp) / "bad.json"
            bad_json.write_text("{broken", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                check_loop.load_and_merge_state({}, bad_json)

    def test_load_and_merge_state_with_non_dict_data_returns_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text(json.dumps({"round": 2}), encoding="utf-8")
            self.assertEqual(check_loop.load_and_merge_state(["not-a-dict"], state_path), {"round": 2})

    def test_persist_state_noop_when_missing_args_or_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            original = {"round": 1, "novelty_history": [], "verification": "not-run"}
            original_text = json.dumps(original)
            state_path.write_text(original_text, encoding="utf-8")

            # None path / None state_data
            check_loop.persist_state(None, original, {}, {"verdict": "PASS", "novelty_history": [0], "settled_claims": [], "dimensions": []})
            check_loop.persist_state(state_path, None, {}, {"verdict": "PASS", "novelty_history": [0], "settled_claims": [], "dimensions": []})
            self.assertEqual(state_path.read_text(encoding="utf-8"), original_text)

            # Rejected call (verdict is None and reason starts with "Rejected:")
            rejected_result = {
                "verdict": None,
                "reason": "Rejected: bad input",
                "novelty_history": [99],
                "settled_claims": ["x"],
                "dimensions": ["defect"],
            }
            check_loop.persist_state(state_path, original, {"verification": "passed"}, rejected_result)
            self.assertEqual(state_path.read_text(encoding="utf-8"), original_text)

    def test_persist_state_writes_continuing_and_terminal_calls_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_data = {"round": 2, "custom_note": "preserve-me", "verification": "passed"}
            continuing_result = {
                "verdict": None,
                "reason": "Round 2: 1 claim(s) accepted, 1 new; continuing to round 3",
                "novelty_history": [1, 1],
                "settled_claims": ["a | b | c | d"],
                "dimensions": ["goal-alignment", "defect"],
            }
            # No verification key in data -> falls back to state_data's "passed"
            check_loop.persist_state(state_path, state_data, {}, continuing_result)
            persisted = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["novelty_history"], [1, 1])
            self.assertEqual(persisted["settled_claims"], ["a | b | c | d"])
            self.assertEqual(persisted["dimensions"], ["goal-alignment", "defect"])
            self.assertEqual(persisted["verification"], "passed")
            self.assertEqual(persisted["custom_note"], "preserve-me")
            # No leftover temp files
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["state.json"])

            # Terminal PASS overrides verification from data and handles None/default fallback
            terminal_result = {
                "verdict": "PASS",
                "reason": "Round 3: Reviewer returned PASS and verification passed",
                "novelty_history": [1, 1, 0],
                "settled_claims": ["a | b | c | d"],
                "dimensions": check_loop.FULL_DIMENSIONS,
            }
            check_loop.persist_state(state_path, state_data, {"verification": "failed"}, terminal_result)
            persisted2 = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted2["verification"], "failed")
            self.assertEqual(persisted2["novelty_history"], [1, 1, 0])

    def test_persist_state_cleans_up_temp_file_when_replace_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text('{"round": 1}\n', encoding="utf-8")
            state_data = {"round": 1}
            result = {
                "verdict": "PASS",
                "reason": "ok",
                "novelty_history": [0],
                "settled_claims": [],
                "dimensions": check_loop.FULL_DIMENSIONS,
            }
            with mock.patch("check_loop.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    check_loop.persist_state(state_path, state_data, {}, result)

            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["state.json"])
            self.assertEqual(state_path.read_text(encoding="utf-8"), '{"round": 1}\n')


if __name__ == "__main__":
    unittest.main(verbosity=2)
