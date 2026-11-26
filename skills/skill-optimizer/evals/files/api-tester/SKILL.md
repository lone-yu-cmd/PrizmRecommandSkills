---
name: "api-tester"
description: "Run HTTP endpoint checks."
---

# API Tester

Execute structured smoke and regression checks against REST and GraphQL endpoints, verify status codes and JSON schemas, and report failures clearly.

## Step 1 — Prepare auth headers

Read `references/auth.md` for token exchange, OAuth refresh, and HMAC signing rules before sending requests.

## Step 2 — Run endpoint suite

Execute each request in the collection against the target base URL, asserting HTTP status codes, response latency bounds, and required response body fields.

## Step 3 — Report results

Summarize passed, failed, and skipped endpoints with status code diffs and response snippets for any failing case.
