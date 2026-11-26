---
name: "doc-sync"
description: "Perform a full synchronization of API documentation from OpenAPI specifications into the docs/ portal."
---

# Doc Sync

Synchronize generated reference pages from OpenAPI specs into the repository documentation portal.

## Mode: `full`

1. Read `openapi.yaml` and validate all operation IDs and response schemas.
2. Clean the target `docs/api/` directory so stale endpoints are removed.
3. Render Markdown pages for every tag and endpoint into `docs/api/`.
4. Rebuild `docs/api/index.md` with links to all generated pages.

## Verification

Check that every generated file exists and contains no broken relative links before finishing.
