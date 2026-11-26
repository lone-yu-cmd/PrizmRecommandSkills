---
name: "data-validator"
description: "Validate incoming ETL payloads across schema, type, and freshness checks before downstream loading."
---

# Data Validator

Validate structured JSON and CSV data batches prior to warehouse ingestion.

## Phase 1 — Structural check

1. Read the input payload header and sample the first 100 rows.
2. Check that required top-level columns exist and no column names contain trailing whitespace.
3. Log any missing columns before moving on.

## Phase 2 — Type & range check

1. Verify numeric fields parse cleanly as integers or floats without `NaN` strings.
2. Verify ISO-8601 timestamps are valid and not in the future.
3. Verify enum columns only contain documented values.

## Phase 3 — Finalize validation

1. Combine findings from Phase 1 and Phase 2 into one summary table.
2. Double-check output keys match the target schema manually before returning `PASS` or `FAIL`.
3. Stop immediately if any `FAIL` condition is present.
