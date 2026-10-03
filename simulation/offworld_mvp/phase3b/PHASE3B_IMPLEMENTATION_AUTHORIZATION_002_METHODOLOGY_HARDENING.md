# Phase 3B Implementation Authorization 002 — Methodology Hardening

**Status:** AUTHORIZED / PRE-CONTRACT / SINGLE-AUTHORITY
**Authorization date:** 2026-10-04
**Authorizer:** project owner
**Scope:** Build 4-derived methodology hardening before autonomous-agent implementation

## Decision

Following the Build 4 freeze, implementation authority is granted to harden the Offworld MVP methodology and return to an updated Build 4-derived executable baseline.

This authorization extends Phase 3B Implementation Authorization 001 only for the work below. The full autonomous-agent engine remains gated.

## Authorized work

1. ODD-aligned executable model documentation and traceability.
2. Deterministic scheduler/time/coupling state and validation fixtures.
3. Verification, validation, calibration, sensitivity and uncertainty protocol scaffolding.
4. SYSTEM / AGGREGATE / AGENT / ENTITY_ASSET classification enforcement.
5. Deterministic AGGREGATE -> AGENT split/reconciliation fixtures and tests.
6. Explicit MVP accounting-boundary representation and validation.
7. Deterministic ensemble/parameter-sweep experiment infrastructure.
8. Replay manifests, run identities, event-order fingerprints and diagnostics needed to test the above.
9. FRD updates required to make these methodology requirements normative for the MVP.
10. Revalidation of the Build 4-derived kernel after the hardening work.

## Explicitly not authorized

This authorization does not permit:

- autonomous decision-policy implementation;
- LLM/runtime-agent authority;
- production forecasting claims;
- empirical calibration by invented values;
- historical backcast claims not supported by admitted data;
- promotion to Authority Contract v1;
- silent relaxation of Build 4 conservation, epistemic, locality or replay invariants.

Any behavioral policy used in testing remains a deterministic scripted validation driver.

## Exit condition

The methodology-hardening pass is complete when:

- the scheduler contract is executable and deterministic;
- resolution transitions reconcile conserved state;
- the accounting boundary is explicit and tested;
- ensemble runs preserve run identity and keyed replay;
- the ODD-aligned specification maps executable components and scheduling;
- the V&V protocol distinguishes verification from empirical validation;
- the complete regression suite passes from a fresh Git archive;
- a new validation record states what remains unvalidated.

This authorization does not close Phase 3B.
