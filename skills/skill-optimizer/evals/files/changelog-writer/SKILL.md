---
name: "changelog-writer"
description: "Convert raw git commit logs into release notes grouped by feature, fix, and breaking change."
---

# Changelog Writer

Turn commit history between two tags into clean, user-facing release notes.

## Step 1 — Gather commits

Run `git log <prev-tag>..HEAD --oneline` and filter out merge commits and CI-only chores.

## Step 2 — Rewrite entries

Rewrite each raw commit message so end users understand the impact:
- ALWAYS start every bullet with a clear past-tense verb.
- NEVER copy internal Jira ticket IDs or branch names into the release notes.
- ALWAYS group entries under `Added`, `Fixed`, and `Breaking Changes`.
- NEVER leave vague entries like "misc fixes" without checking the diff.

## Step 3 — Output release notes

Emit the grouped markdown changelog ready to paste into the GitHub Release body.
