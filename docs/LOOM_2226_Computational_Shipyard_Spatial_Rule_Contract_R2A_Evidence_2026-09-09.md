# LOOM 2226 — Computational Shipyard Spatial Rule Contract R2A Evidence

**Date:** 2026-09-09  
**Status:** IMPLEMENTED / CI PASS  
**Classification:** ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION

## Scope

R2A adds a governed spatial-rule contract above the existing R2 minimum spatial-validation layer. R2 remains unchanged.

The contract registers seven explicit spatial-rule domains:

- clearance;
- deployment;
- plume exclusion;
- docking access;
- service access;
- robot access;
- Loom domain.

Current Wayfarer evidence admits none of these rule domains. The R2A Wayfarer contract therefore records all seven as `OPEN_NOT_ADMITTED` and carries no fabricated geometry or thresholds.

## Typed rule capability

R2A currently supports two conservative rule forms when future governed evidence admits them:

- pairwise minimum clearance between admitted packaging-envelope semantic objects;
- axis-aligned exclusion envelopes for deployment, plume, docking, service, robot or Loom-domain screening.

These are deliberately minimum viable spatial contracts. More faithful shape families may be added only when engineering need justifies them.

An `ADMITTED_COMPLETE` domain must contain explicit governed rules. An OPEN domain may not silently contain admitted rules.

## Evaluation behavior

R2A binds to the governed synthesis package hash, R1 semantic package hash, R2 package hash and spatial-rule contract hash.

A rule can close only its own admitted domain to PASS or REVIEW. It does not close unrelated OPEN domains.

Synthetic regression tests demonstrate that:

- a governed clearance threshold below an existing admitted-envelope separation produces PASS for the clearance domain;
- a threshold exceeding that separation produces REVIEW, not a fabricated PASS;
- declaring a domain complete without explicit rules fails closed;
- authority/hash tampering fails closed.

Synthetic test rules are test fixtures only and are not Wayfarer engineering admissions.

## Wayfarer result

Current Wayfarer remains blocked for downstream visual-realization readiness because all seven governed spatial-rule domains remain OPEN and any existing R2 pairwise review evidence remains independently relevant.

This is a successful fail-closed result, not a spacecraft qualification failure.

## CI evidence

Initial implementation head `babdbc9876d320c6f0228ba55ff3deb16f99db69` passed:

- `LOOM Shipyard Spatial Rule Contract R2A`;
- inherited `LOOM Shipyard Minimum Spatial Validation R2`;
- full `LOOM Python Regression`.

Documentation head `03ff664d534d055b5bac306bdfb19cce0f506484` also passed all three workflows. The full repository unit-regression suite completed successfully after the dedicated R2A and inherited R2 workflows had already passed.

## Authority

```text
ENGINEERING_RESEARCH
NON_CANON
NON_PRODUCTION
NO_FLIGHT_DYNAMICS_AUTHORITY
NO_STRUCTURAL_QUALIFICATION
NO_DESIGN_STATE_MUTATION
NO_AI_BACKPROPAGATION
```
