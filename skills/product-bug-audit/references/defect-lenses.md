# Abstract Defect Lenses & Surface Routing

Load this file in Phase 3 before scanning the product. Run **only** the lenses enabled for the target's product shape; skip non-applicable dimensions rather than forcing irrelevant checks.

---

## Surface-Shape Lens Routing

| Product Shape | Enabled Pillar A Lenses | Enabled Pillar B Lenses | Notes |
|---|---|---|---|
| **Web / SaaS App** | All 3 (`verification-blind-spot`, `flow-dead-end`, `ergonomic-friction-defect`) | All 5 (`state-and-concurrency`, `data-ownership-and-cascade`, `trust-and-authz`, `boundary-resilience-and-bounds`, `invariants-and-runtime-readiness`) | Full surface audit across guests, authenticated paths, and admin/settings. |
| **Mobile App** | All 3 (plus interruption/offline & touch ergonomics) | All 5 | Inspect backgrounding/resume state, permission denial fallback, and offline cache staleness. |
| **CLI / Dev Tool** | All 3 adapted to CLI (`verification-blind-spot`, `flow-dead-end`, `ergonomic-friction-defect` for flags/prompts/exit codes) | Skip UI state matrix; check `state-and-concurrency`, `data-ownership-and-cascade`, `trust-and-authz` (if local secrets/paths), `boundary-resilience-and-bounds`, `invariants-and-runtime-readiness` | Pay close attention to clean-machine startup, idempotent re-runs, nonzero exit codes, and actionable stderr. |
| **API / SDK / Library** | `verification-blind-spot` (actionable error codes & caller signals), `flow-dead-end` (missing companion read/cancel/cleanup contract), `ergonomic-friction-defect` (unsafe defaults, ambiguous signatures) | `state-and-concurrency`, `data-ownership-and-cascade`, `trust-and-authz`, `boundary-resilience-and-bounds`, `invariants-and-runtime-readiness` | Focus on boundary validation, error taxonomy, pagination/bounds, compatibility, and idempotency. |
| **Backend / Worker / Internal Ops** | `verification-blind-spot` (health/outcome visibility), `flow-dead-end` (stuck jobs, unrecoverable failed states) | All 5 (skip visual UI items inside `state-and-concurrency`) | Focus on retries, dead-letter/partial writes, locks, timeouts, redaction, and cold-start config checks. |

---

## Pillar A — Broken First-Ring Product Closure Lenses

Reverse the "first-ring product closure" principle: look for places where a shipped feature stops short at a literal skeleton and breaks for a real user or operator.

### 1. `verification-blind-spot`
Where users or operators configure, enable, or trigger behavior and **cannot verify it actually works or understand why it failed**:
- Configuration, rule, or integration changes save silently with no direct feedback, dry-run/status signal, or observable proof of effect.
- Asynchronous, background, or multi-step triggers return a generic accepted/success state while errors are swallowed, overwritten, or hidden in unexposed logs.
- Failure messages omit actionable cause or recovery direction (or show raw internal codes/blank screens instead of clear failure semantics).

### 2. `flow-dead-end`
Where a real user journey breaks at an immediate upstream prerequisite or downstream follow-through step (strictly task-driven—never treat unrequested CRUD completeness as a bug):
- **Broken entry readiness**: missing prerequisite setup, empty datasets, or disabled states lead to broken controls, uncaught errors, or circular redirects with no path to resolve the prerequisite.
- **Stranded post-action states**: completing a primary action lands on a dead page, stale snapshot, or uninspectable output where the natural next step (view result, adjust, retry, pause/disable, cancel, or recover) is unreachable.
- **Irreversible traps**: operations that corrupt state or block subsequent steps when an expected cancel, rollback, or cleanup path fails partway through.

### 3. `ergonomic-friction-defect`
Where implemented interactions directly violate natural human or operator habits on that medium, causing accidental failures, lost work, or repeated mis-triggers:
- Missing double-submit / in-flight trigger locks on state-mutating actions, allowing duplicate requests or corrupted writes.
- Validation or server errors wipe already-entered user input instead of preserving form/draft state for quick correction.
- Disabled controls or rejected actions offer no explanation of what condition is unsatisfied.
- Destructive or high-impact actions execute immediately without proportional confirmation or safeguard, OR medium-standard submit/cancel/focus/CLI-flag conventions silently misfire (e.g., failing without clear exit status or prompting indefinitely in non-interactive shells).

---

## Pillar B — Structural Design & System-Integrity Lenses

Inspect the implementation for structural flaws that cause production failures, security leaks, data corruption, or broken deployments.

### 4. `state-and-concurrency`
- **Missing interactive states** *(when UI-facing)*: views implement only happy-path data and crash, freeze, or flash misleading content on empty, loading, error, or unauthorized states.
- **Illegal state transitions**: endpoints, handlers, or workers mutate entity status without validating allowed prior states, allowing out-of-order, stale, or post-terminal transitions.
- **Non-idempotent retries & races**: retried requests, duplicate callbacks, concurrent edits, or interrupted runs duplicate side effects, double-charge/double-write, or leave stuck intermediate states.

### 5. `data-ownership-and-cascade`
- **Split-brain SSOT**: the same business truth lives in two places (client cache vs server DB, duplicated columns, derived counters) without synchronized invalidation on every write path.
- **Orphan & broken cascades**: deleting, archiving, or deactivating a parent record leaves dangling foreign keys, broken reads, or still-running dependent jobs.
- **Incompatible schema evolution**: newly added constraints, non-null fields, or changed enum semantics break pre-existing persisted records without fallback or backfill.

### 6. `trust-and-authz`
- **AuthN without AuthZ (IDOR)**: routes check session authentication cleanly yet fail to verify per-resource ownership, role privilege, or tenant/workspace isolation on read or mutation queries.
- **UI-only gating**: privileged actions are hidden in frontend rendering while underlying API endpoints or server actions accept unauthorized requests directly.
- **Untrusted external inputs**: unverified webhook/callback signatures, unvalidated file upload types/sizes/paths (path traversal), open redirects, or unsanitized rich text / HTML rendering and unsafe deserialization.

### 7. `boundary-resilience-and-bounds`
- **Missing boundary timeouts & partial-failure handling**: external HTTP/RPC calls, subprocesses, or file IO run without timeouts; multi-step writes commit half the steps on mid-flight error without rollback or explicit partial-result recovery.
- **Unbounded collections & memory/query traps**: list queries, exports, or batch loops load unbounded datasets into memory, omit pagination/size caps, or execute per-item queries inside loops.
- **Unsafe error leakage**: internal stack traces, SQL/schema details, secrets, or tokens leak into HTTP responses, UI alerts, or logs.

### 8. `invariants-and-runtime-readiness`
- **Silent domain-invariant violations**: floating-point arithmetic used for exact financial/decimal quantities, implicit server-local timezone cutoffs instead of explicit/UTC handling, missing database-level uniqueness behind check-then-insert code, or non-deterministic pagination ordering.
- **Cold-start & configuration fragility**: fresh empty environments fail because required seed/default handling is missing, or absent/malformed config/env vars surface lazily mid-request instead of failing fast with diagnostic messages at startup.
