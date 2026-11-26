# Evidence Verification, Anti-Bloat Gates & Output Specification

Load this file in Phase 4 before finalizing any defect report. Every reported finding must pass all verification gates and follow the output schema below.

---

## 1. Evidence Verification Rules

Never report a suspected defect from filenames, grep matches, or client code alone:
- **Open the full execution chain**: if a route looks unauthenticated, inspect parent routers, framework middlewares, and shared decorators before calling it an auth bug. If a frontend component lacks validation, inspect the backend handler/schema before judging impact.
- **Verify test coverage if uncertain**: existing unit/integration tests sometimes clarify intended behavior vs genuine oversight.
- **Label every finding's evidence status**:
  - `fact` — directly observed in source lines, schema definitions, config, test failures, or a live walkthrough.
  - `inference` — logical failure mode deduced cleanly from verified source code when no live run executed (must state the exact source facts it rests on).

---

## 2. Four Hard False-Positive & Anti-Bloat Gates

Run every candidate finding through all four gates. Drop any item that fails Gates 1–3:

1. **Defect vs. Feature Wish Gate**:
   - *Real defect*: violates intended capability behavior, leaves an implemented flow blind/broken/stranded, exposes unsafe/unintuitive mechanics that cause errors, corrupts state/data, leaks privilege, or fails under normal edge conditions.
   - *Feature wish (DROP)*: introduces a new adjacent business domain, speculative future workflow, convenience shortcut, or optional enhancement unrelated to making existing behavior sound and complete.
2. **Guarded-Elsewhere Verification Gate**:
   - Check framework defaults, middleware chains, DB constraints, UI wrapper components, and shared error boundaries. If an existing layer already prevents the failure safely, **DROP** the finding.
3. **Anti-Mechanical-CRUD & Anti-Nitpick Gate**:
   - **DROP** complaints that merely ask for generic Create/Read/Update/Delete parity, bulk edit/export buttons, audit logs, or stylistic formatting/refactoring that causes no real user friction or system defect.
   - Zero findings in a clean module is a valid outcome—never manufacture noise to fill a table.
4. **Calibrated Severity Ladder** (attach a concrete indicator rationale to every kept finding; never collapse all items to `high`):

| Severity | Concrete Indicators (Require at Least One) |
|---|---|
| `critical` | Cross-tenant/authZ bypass, arbitrary access/RCE/secret leak, irreversible data loss/corruption, payment/financial miscalculation, or crash blocking all users on startup. |
| `high` | Core primary workflow breaks/dead-ends with no workaround, duplicate writes/illegal state corruption under normal retries, silent failure leaving users unable to confirm/recover core actions, or missing external timeout hanging primary requests. |
| `medium` | Significant ergonomic friction (input loss on validation error, missing double-submit guard mitigated partly by server checks), missing secondary empty/error recovery with an available workaround, or bounded degradation on edge inputs. |
| `low` | Minor localized polish or confusing diagnostic wording where flow succeeds and state remains safe (include only if directly tied to an audit lens; omit pure aesthetic taste). |

---

## 3. Entry A Deduplication Protocol

When the user provided known bugs, issues, or an existing backlog in Phase 1:
1. Normalize each known item by `(area / endpoint / component, failure mechanism)`. If the supplied bugs/issues/logs carry no IDs, assign deterministic sequential fallback IDs (`KNOWN-01`, `KNOWN-02`, ...) in the baseline before tagging.
2. Tag every verified finding:
   - `new` — distinct functional/design defect not covered by any supplied item.
   - `sibling-of:<known-id>` — distinct defect in a different path or component that shares the same root mistake or affected journey as `<known-id>` (or synthetic `KNOWN-NN`) — keep in `Findings`, noting the link.
   - `already-tracked:<known-id>` — duplicates a supplied bug with no material new root cause or severity impact; **omit from new `Findings`** and record only in `## Deduplicated Against Known Bugs`.

---

## 4. Deliverable Output Template

Use this exact structure so humans can triage directly and downstream planning tools can ingest entries verbatim:

```markdown
# Product & Design Defect Audit

## Audit Summary
- **Target**: <product/repo/module path>
- **Product Shape**: <Web/SaaS | CLI/Dev Tool | Mobile | API/SDK | Backend/Worker | Hybrid (<constituent shapes>)>
- **Entry Mode**: <Entry A — Incremental Deduplicated (N known items) | Entry B — Zero-Prerequisite Proactive Scan>
- **Execution Mode**: <Static source audit + live walkthrough (<URL/cmd>) | Static source audit only — no live walkthrough executed>
- **Verified Findings**: Critical N · High N · Medium N · Low N (Total: N) · Deduplicated duplicates skipped: N

## Findings

### AUDIT-001: <Concise Defect Title>
- **Lens**: <lens slug from defect-lenses.md>
- **Severity**: <critical | high | medium | low> — <concrete indicator rationale>
- **Status**: <new | sibling-of:<known-id>>
- **Location**: `<exact file:line>` (plus related caller/schema paths if relevant)
- **Actual vs Expected**:
  - *Actual*: <what the current implementation actually does, grounded in inspected code>
  - *Expected*: <exact observable behavior required to close the defect without scope creep>
- **Evidence**: `[fact]` <exact handler/component/schema facts>; `[inference]` <failure consequence if unexecuted live>
- **Verification Criteria**:
  1. Given <precondition>, When <action>, Then <observable outcome>.
  2. <Second verifiable condition covering negative/regression behavior if applicable>
- **Scope Guardrail**: <what adjacent refactor or speculative feature must stay out of scope during the fix>

## Deduplicated Against Known Bugs
<!-- Include only for Entry A; omit section in Entry B. -->
- `<known-id>`: matched/excluded as `already-tracked` because <evidence>, OR kept related finding `AUDIT-NNN` as `sibling-of:<known-id>` because <distinct surface/impact>.

## Coverage & Not Checked
- **Inspected surfaces & files**: <key routes, screens, handlers, models, middlewares inspected>
- **Lenses applied**: <active lens slugs> (Skipped as N/A for shape: <skipped slugs or none>)
- **Not checked / limits**: <uninspected modules if scoped, or runtime-only behavior unverified when no live instance existed>
```

---

## Worked Finding Example (Domain-Generic Format Reference)

```markdown
### AUDIT-001: Asynchronous Export Job Retries Duplicate Rows on Stale Status Transition
- **Lens**: state-and-concurrency
- **Severity**: high — allows duplicate side effects and corrupted export output under normal client retries with no idempotent workaround.
- **Status**: sibling-of:B-004
- **Location**: `src/jobs/export_runner.py:44-68`, `src/api/exports.py:91`
- **Actual vs Expected**:
  - *Actual*: `POST /api/exports/{id}/retry` resets status to `pending` unconditionally even while status is `running`, and `export_runner.py` appends rows without truncating partial writes from an interrupted attempt.
  - *Expected*: Reject retry transitions while `running` or `completed` (`409 Conflict`), and execute retries idempotently into a staging key before atomic swap.
- **Evidence**: `[fact]` `exports.py:91` issues `UPDATE exports SET status='pending' WHERE id=?` with no prior state predicate; `export_runner.py:52` opens output file in append mode; `[inference]` two concurrent worker runs corrupt output ordering.
- **Verification Criteria**:
  1. Given an export job in `running` state, When `POST /api/exports/{id}/retry` is called, Then the API returns `409` and leaves the running job untouched.
  2. Given a failed export retry after partial write, When re-executed, Then final output contains each matching record exactly once.
- **Scope Guardrail**: Fix transition guard and retry atomicity only; do not introduce distributed workflow queues or scheduled exports.
```
