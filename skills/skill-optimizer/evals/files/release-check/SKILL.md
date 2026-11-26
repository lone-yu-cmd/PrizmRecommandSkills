---
name: "release-check"
description: "Verify repository readiness, changelog completeness, dependency audit, and tag hygiene prior to cutting a release."
---

# Release Check

Run pre-release verification across code quality, versioning, security checks, and artifact integrity.

## Phase 1 — Version & Branch Hygiene

1. Confirm current branch is `main` or a dedicated `release/*` branch.
2. Confirm working tree is clean with zero untracked build artifacts.
3. Verify semantic version bump in `package.json` or `pyproject.toml` matches release scope.
4. Confirm `CHANGELOG.md` contains a dated heading for the target version.
5. Verify no snapshot or pre-release dependency pins remain in lockfiles.
6. Check that all cherry-picked hotfixes from previous release branches are merged.
7. Confirm tag name `vX.Y.Z` does not already exist locally or on `origin`.
8. Validate commit signatures on release head commits.

## Phase 2 — Automated Quality Gates

1. Run full unit and integration test suites with zero skipped critical tests.
2. Run static type checking and linter with zero errors.
3. Run dependency vulnerability scan (`npm audit` / `pip-audit`).
4. Verify reproducible production build completes cleanly.
5. Compare bundle size against the previous release threshold.
6. Confirm database migration scripts pass dry-run forward check.
7. Verify API schema backward compatibility against prior release spec.
8. Check environment config templates for newly added required variables.
9. Verify container image scans report zero critical CVEs.
10. Confirm license headers and `NOTICE` attributions are up to date.

## Phase 3 — Sign-off & Tagging

1. Assemble the release readiness summary from Phase 1 and Phase 2.
2. Attach benchmark comparisons and migration notes to the release ticket.
3. Verify on-call rotation and release window availability.
4. Confirm rollback contacts are listed in the release checklist.
5. Verify artifact checksums (`SHA256SUMS`) match CI build outputs.
6. Validate release notes links and documentation anchor targets.
7. Prepare signed annotated git tag command without pushing yet.
8. Confirm staging soak tests passed for at least 30 minutes.
9. Review open P0/P1 issues targeting the milestone.
NEVER skip manual sign-off before tagging a release.

## Phase 4 — Detailed Verification Matrix

### Matrix Item 1: Release Verification Check 1
1. Inspect subsystem 1 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 1 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 1 in the release log.

### Matrix Item 2: Release Verification Check 2
1. Inspect subsystem 2 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 2 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 2 in the release log.

### Matrix Item 3: Release Verification Check 3
1. Inspect subsystem 3 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 3 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 3 in the release log.

### Matrix Item 4: Release Verification Check 4
1. Inspect subsystem 4 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 4 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 4 in the release log.

### Matrix Item 5: Release Verification Check 5
1. Inspect subsystem 5 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 5 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 5 in the release log.

### Matrix Item 6: Release Verification Check 6
1. Inspect subsystem 6 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 6 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 6 in the release log.

### Matrix Item 7: Release Verification Check 7
1. Inspect subsystem 7 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 7 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 7 in the release log.

### Matrix Item 8: Release Verification Check 8
1. Inspect subsystem 8 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 8 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 8 in the release log.

### Matrix Item 9: Release Verification Check 9
1. Inspect subsystem 9 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 9 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 9 in the release log.

### Matrix Item 10: Release Verification Check 10
1. Inspect subsystem 10 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 10 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 10 in the release log.

### Matrix Item 11: Release Verification Check 11
1. Inspect subsystem 11 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 11 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 11 in the release log.

### Matrix Item 12: Release Verification Check 12
1. Inspect subsystem 12 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 12 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 12 in the release log.

### Matrix Item 13: Release Verification Check 13
1. Inspect subsystem 13 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 13 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 13 in the release log.

### Matrix Item 14: Release Verification Check 14
1. Inspect subsystem 14 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 14 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 14 in the release log.

### Matrix Item 15: Release Verification Check 15
1. Inspect subsystem 15 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 15 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 15 in the release log.

### Matrix Item 16: Release Verification Check 16
1. Inspect subsystem 16 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 16 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 16 in the release log.

### Matrix Item 17: Release Verification Check 17
1. Inspect subsystem 17 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 17 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 17 in the release log.

### Matrix Item 18: Release Verification Check 18
1. Inspect subsystem 18 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 18 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 18 in the release log.

### Matrix Item 19: Release Verification Check 19
1. Inspect subsystem 19 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 19 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 19 in the release log.

### Matrix Item 20: Release Verification Check 20
1. Inspect subsystem 20 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 20 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 20 in the release log.

### Matrix Item 21: Release Verification Check 21
1. Inspect subsystem 21 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 21 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 21 in the release log.

### Matrix Item 22: Release Verification Check 22
1. Inspect subsystem 22 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 22 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 22 in the release log.

### Matrix Item 23: Release Verification Check 23
1. Inspect subsystem 23 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 23 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 23 in the release log.

### Matrix Item 24: Release Verification Check 24
1. Inspect subsystem 24 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 24 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 24 in the release log.

### Matrix Item 25: Release Verification Check 25
1. Inspect subsystem 25 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 25 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 25 in the release log.

### Matrix Item 26: Release Verification Check 26
1. Inspect subsystem 26 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 26 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 26 in the release log.

### Matrix Item 27: Release Verification Check 27
1. Inspect subsystem 27 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 27 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 27 in the release log.

### Matrix Item 28: Release Verification Check 28
1. Inspect subsystem 28 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 28 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 28 in the release log.

### Matrix Item 29: Release Verification Check 29
1. Inspect subsystem 29 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 29 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 29 in the release log.

### Matrix Item 30: Release Verification Check 30
1. Inspect subsystem 30 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 30 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 30 in the release log.

### Matrix Item 31: Release Verification Check 31
1. Inspect subsystem 31 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 31 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 31 in the release log.

### Matrix Item 32: Release Verification Check 32
1. Inspect subsystem 32 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 32 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 32 in the release log.

### Matrix Item 33: Release Verification Check 33
1. Inspect subsystem 33 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 33 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 33 in the release log.

### Matrix Item 34: Release Verification Check 34
1. Inspect subsystem 34 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 34 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 34 in the release log.

### Matrix Item 35: Release Verification Check 35
1. Inspect subsystem 35 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 35 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 35 in the release log.

### Matrix Item 36: Release Verification Check 36
1. Inspect subsystem 36 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 36 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 36 in the release log.

### Matrix Item 37: Release Verification Check 37
1. Inspect subsystem 37 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 37 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 37 in the release log.

### Matrix Item 38: Release Verification Check 38
1. Inspect subsystem 38 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 38 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 38 in the release log.

### Matrix Item 39: Release Verification Check 39
1. Inspect subsystem 39 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 39 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 39 in the release log.

### Matrix Item 40: Release Verification Check 40
1. Inspect subsystem 40 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 40 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 40 in the release log.

### Matrix Item 41: Release Verification Check 41
1. Inspect subsystem 41 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 41 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 41 in the release log.

### Matrix Item 42: Release Verification Check 42
1. Inspect subsystem 42 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 42 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 42 in the release log.

### Matrix Item 43: Release Verification Check 43
1. Inspect subsystem 43 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 43 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 43 in the release log.

### Matrix Item 44: Release Verification Check 44
1. Inspect subsystem 44 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 44 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 44 in the release log.

### Matrix Item 45: Release Verification Check 45
1. Inspect subsystem 45 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 45 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 45 in the release log.

### Matrix Item 46: Release Verification Check 46
1. Inspect subsystem 46 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 46 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 46 in the release log.

### Matrix Item 47: Release Verification Check 47
1. Inspect subsystem 47 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 47 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 47 in the release log.

### Matrix Item 48: Release Verification Check 48
1. Inspect subsystem 48 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 48 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 48 in the release log.

### Matrix Item 49: Release Verification Check 49
1. Inspect subsystem 49 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 49 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 49 in the release log.

### Matrix Item 50: Release Verification Check 50
1. Inspect subsystem 50 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 50 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 50 in the release log.

### Matrix Item 51: Release Verification Check 51
1. Inspect subsystem 51 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 51 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 51 in the release log.

### Matrix Item 52: Release Verification Check 52
1. Inspect subsystem 52 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 52 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 52 in the release log.

### Matrix Item 53: Release Verification Check 53
1. Inspect subsystem 53 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 53 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 53 in the release log.

### Matrix Item 54: Release Verification Check 54
1. Inspect subsystem 54 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 54 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 54 in the release log.

### Matrix Item 55: Release Verification Check 55
1. Inspect subsystem 55 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 55 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 55 in the release log.

### Matrix Item 56: Release Verification Check 56
1. Inspect subsystem 56 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 56 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 56 in the release log.

### Matrix Item 57: Release Verification Check 57
1. Inspect subsystem 57 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 57 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 57 in the release log.

### Matrix Item 58: Release Verification Check 58
1. Inspect subsystem 58 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 58 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 58 in the release log.

### Matrix Item 59: Release Verification Check 59
1. Inspect subsystem 59 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 59 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 59 in the release log.

### Matrix Item 60: Release Verification Check 60
1. Inspect subsystem 60 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 60 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 60 in the release log.

### Matrix Item 61: Release Verification Check 61
1. Inspect subsystem 61 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 61 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 61 in the release log.

### Matrix Item 62: Release Verification Check 62
1. Inspect subsystem 62 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 62 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 62 in the release log.

### Matrix Item 63: Release Verification Check 63
1. Inspect subsystem 63 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 63 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 63 in the release log.

### Matrix Item 64: Release Verification Check 64
1. Inspect subsystem 64 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 64 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 64 in the release log.

### Matrix Item 65: Release Verification Check 65
1. Inspect subsystem 65 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 65 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 65 in the release log.

### Matrix Item 66: Release Verification Check 66
1. Inspect subsystem 66 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 66 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 66 in the release log.

### Matrix Item 67: Release Verification Check 67
1. Inspect subsystem 67 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 67 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 67 in the release log.

### Matrix Item 68: Release Verification Check 68
1. Inspect subsystem 68 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 68 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 68 in the release log.

### Matrix Item 69: Release Verification Check 69
1. Inspect subsystem 69 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 69 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 69 in the release log.

### Matrix Item 70: Release Verification Check 70
1. Inspect subsystem 70 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 70 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 70 in the release log.

### Matrix Item 71: Release Verification Check 71
1. Inspect subsystem 71 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 71 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 71 in the release log.

### Matrix Item 72: Release Verification Check 72
1. Inspect subsystem 72 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 72 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 72 in the release log.

### Matrix Item 73: Release Verification Check 73
1. Inspect subsystem 73 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 73 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 73 in the release log.

### Matrix Item 74: Release Verification Check 74
1. Inspect subsystem 74 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 74 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 74 in the release log.

### Matrix Item 75: Release Verification Check 75
1. Inspect subsystem 75 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 75 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 75 in the release log.

### Matrix Item 76: Release Verification Check 76
1. Inspect subsystem 76 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 76 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 76 in the release log.

### Matrix Item 77: Release Verification Check 77
1. Inspect subsystem 77 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 77 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 77 in the release log.

### Matrix Item 78: Release Verification Check 78
1. Inspect subsystem 78 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 78 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 78 in the release log.

### Matrix Item 79: Release Verification Check 79
1. Inspect subsystem 79 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 79 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 79 in the release log.

### Matrix Item 80: Release Verification Check 80
1. Inspect subsystem 80 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 80 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 80 in the release log.

### Matrix Item 81: Release Verification Check 81
1. Inspect subsystem 81 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 81 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 81 in the release log.

### Matrix Item 82: Release Verification Check 82
1. Inspect subsystem 82 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 82 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 82 in the release log.

### Matrix Item 83: Release Verification Check 83
1. Inspect subsystem 83 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 83 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 83 in the release log.

### Matrix Item 84: Release Verification Check 84
1. Inspect subsystem 84 telemetry, error rate, and SLA compliance before approval.
2. Verify configuration checksum 84 matches the staged release manifest.
3. Record operator verification timestamp for subsystem 84 in the release log.

End of release verification checklist.
