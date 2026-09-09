# LOOM 2226 — Computational Shipyard Minimum Spatial Validation R2 v0.1

**Date:** 2026-09-09  
**Status:** ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION  
**Authority:** DERIVED_SPATIAL_VALIDATION_EVIDENCE_ONLY

## Purpose

R2 defines the smallest spatial-validation layer allowed between governed semantic geometry and downstream non-authoritative visual realization.

R2 is not a spacecraft qualification solver. It may detect geometric evidence, preserve OPEN states, and block visualization handoff. It may not invent missing clearance rules, deployment envelopes, plume geometry, docking corridors, structural qualification, flight authority, canon, production authority, or design-state changes.

## Inputs

R2 consumes:

1. the existing governed synthesis package;
2. the R1 semantic geometry sidecar.

Both inputs must validate before R2 executes. R2 binds its output to the governed package hash and R1 semantic package hash.

## Checks admitted in v0.1

### 1. Pairwise admitted-envelope overlap screen

R2 performs a deterministic conservative axis-aligned bounding-box screen over every pair of admitted packaging regions. Structural hypotheses and source-node proxies are excluded from this physical overlap check because they do not carry qualified spatial authority.

A pair separated on at least one axis receives `PASS_WITHIN_R2_SCOPE` for the narrow claim that no admitted-envelope overlap was detected by this screen.

A pair overlapping or contacting on all three axes receives `REVIEW_REQUIRED_OVERLAP_OR_CONTACT`. R2 does not infer that the condition is invalid: overlap may represent nesting, joining, interface contact, or an actual packaging conflict. That interpretation requires an admitted engineering rule.

### 2. Declared-clearance coverage

The current governed source contains no admitted inter-system clearance-rule contract. R2 therefore records `OPEN_MISSING_ADMITTED_RULE` and does not fabricate a minimum distance.

### 3. Deployment interference coverage

The current governed source contains no admitted swept-volume/deployment-state geometry. R2 records this domain OPEN.

### 4. Torch/plume exclusion coverage

The current governed source contains no admitted plume exclusion geometry or plume-rule contract. R2 records this domain OPEN.

### 5. Docking access coverage

The current governed source contains no admitted docking approach/access corridor envelope. R2 records this domain OPEN.

### 6. OPEN preservation

All R1 semantic OPEN items are carried forward exactly. R2 may not convert an OPEN item into geometry or a PASS claim.

## Handoff rule

`visual_realization_ready` is true only when no R2 check is OPEN or REVIEW_REQUIRED.

Because the current governed source lacks admitted clearance, deployment, plume and docking-access rules, the current Wayfarer R2 package is expected to remain:

`BLOCKED_FOR_VISUAL_REALIZATION_BY_OPEN_OR_REVIEW`

This is a successful R2 result. The validator exists to prevent downstream rendering from outrunning engineering authority.

## Explicit non-authority

R2 cannot claim or mutate:

- flight-dynamics authority;
- structural qualification;
- canon;
- production shipclasses;
- authoritative Design State;
- subsystem identity not supplied upstream;
- missing geometry, volume, clearance, plume, deployment, or docking rules.

`Geometry does not own the ship.` R2 validates only what the governed spatial evidence supports.
