# Scenario Checklists

Load only the section for the primary scenario. Each section gives:

- **Done** — what "complete" means for this scenario.
- **Check** — dimensions that materially change the conclusion.
- **Common misses** — what reviewers usually overlook.
- **Evidence** — what to read before judging.
- **Ask** — at most two decision-impact questions.

---

## Layered docs (L0/L1/L2)

**Done:** each layer has one job; upper/lower pointers are mutual; no duplication or contradiction; docs match source; every document is within its capacity and format rules.

**Check:**

- **Ownership** — each fact lives at its lowest owning level; a parent index does not copy child detail.
- **Pointer integrity** — every upper pointer resolves; every child is reachable; no dead links or orphans.
- **Coverage** — every real module or stable behavior has an owning document; no missing child for a module that exists.
- **Duplication and abstraction** — the same fact is not repeated across layers; sibling documents have consistent granularity.
- **Source alignment** — docs match code, contracts, and generated/installed copies; no stale claims.
- **Capacity and format** — byte limits, required sections, terminology, and validation rules.
- **Navigability** — an agent can go root → relevant L1 → L2 without loading the whole tree.

**Common misses:** reviewing L1 in isolation; treating an index as a detail document; missing orphan L2 files; missing a pointer for a newly added module; reporting a capacity warning as a hard failure; forgetting the installed or bundled copy.

**Evidence:** root document, all L1 documents, linked L2 documents, source tree, validator output, recent changes, install/bundle state.

**Ask:** Which criterion matters most — format compliance, design soundness, source alignment, or navigability? Audit only, or also fix?

---

## Design review

**Done:** goal → mechanism → failure path → verification all hold, and the approach is necessary.

**Check:**

- **Goal fit** — every mechanism maps to a confirmed goal; non-goals are explicit.
- **Assumptions** — what must be true for the design to work? Which are unverified?
- **Alternatives and necessity** — is there a materially simpler or safer path? Why was it rejected?
- **Boundaries and failure** — invalid input, partial success, concurrency, permission, rollback.
- **Coupling and cohesion** — ownership boundaries, dependency direction, single responsibility.
- **Observability** — can we tell whether it works and where it fails?
- **Evolution** — compatibility, migration, deprecation, generated/installed copies.
- **Cost and reversibility** — effort, blast radius, cost of being wrong.

**Common misses:** validating internal consistency without questioning the approach; no non-goals; no failure path; no rollback; no owner; no observability.

**Evidence:** design document, constraints, similar systems, tests, incident history, consumer expectations.

**Ask:** What decision does this design enable? What would make you reject it?

---

## Logic closure

**Done:** every path has a terminal state; state, error, retry, and rollback behavior are coherent.

**Check:**

- **Entry and exit** — every entry has a defined exit; no path hangs.
- **Branch totality** — every condition has a handler; no silent fallthrough.
- **State machine** — all states reachable and terminal states defined; no illegal transitions.
- **Error taxonomy** — retryable vs terminal vs user-actionable errors are distinct.
- **Idempotency and concurrency** — duplicate execution, parallel writers, stale reads.
- **Timeouts** — every wait has a bound and a cleanup path.
- **Recovery and rollback** — partial failure leaves a defined state.
- **Invariants** — what must always hold, and where is it enforced?

**Common misses:** happy path only; undefined error state; retry without idempotency; partial success; concurrent duplicate; timeout without cleanup; rollback never tested.

**Evidence:** flow or state diagrams, code paths, tests, logs, failure incidents.

**Ask:** What is the terminal state for each branch? What happens on duplicate execution?

---

## Requirements/spec

**Done:** testable, unambiguous, scoped, with observable acceptance criteria.

**Check:**

- **Goal and non-goals** — what is in, what is explicitly out.
- **Ambiguity** — words that can be read two ways.
- **Acceptance** — observable criteria, not implementation descriptions.
- **Priority** — what must ship first; what can be deferred.
- **Dependencies and assumptions** — external contracts, data, permissions.
- **Testability** — can each goal be verified without reading the implementation?

**Common misses:** a solution disguised as a requirement; no non-goals; acceptance not observable; hidden dependency; no priority; assumed context.

**Evidence:** spec, original request, existing contracts, stakeholder constraints, prior decisions.

**Ask:** What decision does this unblock? What is explicitly out of scope?

---

## Implementation/change

**Done:** behavior matches intent, is verified, and the blast radius is controlled.

**Check:**

- **Requirement mapping** — each change maps to a goal or confirmed constraint.
- **Impact surface** — call sites, consumers, generated artifacts, installed copies.
- **Compatibility** — public contracts, data formats, versioning.
- **Tests** — positive, negative, boundary, regression.
- **Rollback** — can the change be reverted safely?
- **Docs and generated outputs** — canonical source updated, derived outputs rebuilt and verified.

**Common misses:** change without a test; hidden callers; generated artifacts not rebuilt; installed copy not updated; docs stale; rollback impossible.

**Evidence:** diff, call sites, tests, build/install pipeline, version and release state.

**Ask:** What behavior must not change? How will we know it worked?

---

## Debug/root cause

**Done:** the root cause is reproducible and falsifiable; the fix does not hide it.

**Check:**

- **Reproduction** — smallest reliable repro.
- **Evidence chain** — logs, traces, recent changes, environment.
- **Alternative hypotheses** — at least two, with a way to distinguish them.
- **Impact** — who and what else is affected?
- **Regression** — a test that fails before and passes after.
- **Observability** — how to detect recurrence.

**Common misses:** fixing a symptom; a single hypothesis; no repro; not checking other callers; no regression test; noisy logs mistaken for evidence.

**Evidence:** logs, traces, repro steps, recent commits, tests, environment differences.

**Ask:** What is the smallest repro? What would falsify this root cause?

---

## Test adequacy

**Done:** risk → case → assertion → repeatable.

**Check:**

- **Risk coverage** — the highest-impact failures have tests.
- **Boundaries and negative paths** — empty, extreme, invalid, partial.
- **Isolation** — no shared state or ordering dependency.
- **Flakiness** — time, network, randomness, concurrency.
- **Diagnosability** — a failure tells you what broke and where.
- **Regression** — the test would have caught the bug it claims to cover.

**Common misses:** only the happy path; asserting implementation instead of behavior; shared state; time/network flakiness; unreadable failures.

**Evidence:** test list, coverage, CI history, failure logs, incident history.

**Ask:** Which risk is untested? What would make this test flaky?

---

## Contract/interface change

**Done:** producer and consumers are synchronized and compatible.

**Check:**

- **Fields and semantics** — names, types, meaning, nullability.
- **Versioning** — how the change is identified and negotiated.
- **Defaults** — missing fields, backward compatibility.
- **Error codes** — stable meanings and mappings.
- **Consumers** — every caller updated or protected.
- **Migration** — compatibility window and removal plan.

**Common misses:** changing semantics without a version bump; optional field becoming required; missing consumer update; error-code drift; no migration window.

**Evidence:** OpenAPI/schema, call sites, version history, contract tests, generated clients.

**Ask:** Who consumes this? What is the compatibility window?

---

## Migration/release

**Done:** reversible, verifiable, staged.

**Check:**

- **Data** — backup, transformation, validation, rollback.
- **Compatibility window** — old and new versions coexist.
- **Rollout** — staged or gated by observable signals.
- **Rollback** — tested path to the previous state.
- **Monitoring** — success and failure signals.
- **Installed/generated copies** — source fix is delivered to the installed runtime.

**Common misses:** no rollback; no backup; big-bang release; monitoring missing; installed copy not updated; docs not updated.

**Evidence:** migration scripts, release plan, monitoring dashboards, version pins, install verification.

**Ask:** How do we roll back? How do we know it worked in production?

---

## Decision/tradeoff

**Done:** options, criteria, evidence, and reversibility are explicit.

**Check:**

- **Objective function** — what are we optimizing for?
- **Constraints** — hard vs soft.
- **Alternatives** — genuinely different viable paths.
- **Worst case** — what happens if we are wrong?
- **Reversibility** — cost to undo.
- **Opportunity cost** — what are we not doing?

**Common misses:** false binary; criteria chosen after the fact; ignoring opportunity cost; no worst case; irreversible choice without confirmation.

**Evidence:** options, constraints, cost estimates, precedents, user preferences.

**Ask:** What are we optimizing for? What is the cost of being wrong?

---

## Explanation/writing

**Done:** the reader can act without misreading.

**Check:**

- **Audience** — expertise, context, decision power.
- **Answer-first** — the conclusion before the background.
- **Terminology** — defined once, used consistently.
- **Examples** — one concrete case.
- **Boundaries** — when the advice does not apply.
- **Common misconceptions** — what a reasonable reader might wrongly infer.

**Common misses:** burying the answer; undefined terms; no example; no boundary; assuming expertise.

**Evidence:** reader's context, existing docs, prior feedback.

**Ask:** Who is the reader? What should they do after reading?

---

## AI asset review (skill/prompt/agent)

**Done:** the trigger is precise; instructions do not conflict; context is bounded; terminal states are deterministic; behavior is evaluable.

**Check:**

- **Trigger precision** — what should and should not activate it; false positives and misses.
- **Instruction hierarchy and conflicts** — safety, user intent, project rules, examples.
- **Context budget** — what loads always vs on demand; no whole-repo reads.
- **Terminal and failure paths** — every outcome is defined; no silent success.
- **Platform neutrality** — no platform-specific names used as protocol identifiers.
- **Eval coverage** — positive, negative, ambiguous, injection, headless.
- **Deterministic artifacts** — owned paths, complete templates, no placeholders in output.

**Common misses:** description too broad or too narrow; conflicting instructions; context bloat; no failure terminal; platform-specific identifiers; no evals; non-deterministic generated artifacts.

**Evidence:** SKILL.md, description, references, evals, install output, runtime tests.

**Ask:** When should this trigger, and when must it not? What are the terminal outcomes?
