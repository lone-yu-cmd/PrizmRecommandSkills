---
name: "report-builder"
description: "Audit project configuration files and output a diagnostic checklist report with error and warning severity levels."
---

# Report Builder

Inspect a target project configuration directory and produce a structured diagnostic checklist report.

## Step 1 — Collect inputs

Read all configuration files in the target directory (`*.yaml`, `*.json`, `*.toml`). Record missing required keys, deprecated options, and mismatched values.

## Step 2 — Evaluate rules

Classify each finding into one of two severities:
- `error`: breaks startup or causes invalid output
- `warning`: works today but risks drift or unexpected behavior

## Output Format

Use this exact markdown structure for the report:

```markdown
# Diagnostic Report

## Summary
- Files scanned: <N>
- Errors: <N>
- Warnings: <N>

## Findings
- [error] <location>: <problem description>
- [warning] <location>: <problem description>
```

## Step 3 — Deliver report

Present the generated report directly in the response without modifying any configuration files.
