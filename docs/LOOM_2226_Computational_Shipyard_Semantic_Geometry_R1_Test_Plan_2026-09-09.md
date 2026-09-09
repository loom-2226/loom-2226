# LOOM 2226 — Computational Shipyard Semantic Geometry R1 Test Plan

**Date:** 2026-09-09  
**Status:** ENGINEERING_RESEARCH / NON-CANON / NON-PRODUCTION

## Purpose

Validate that the R1 semantic-geometry sidecar adds machine-readable identity and downstream visual-mutability constraints without changing the existing governed Wayfarer geometry, escalating authority, guessing subsystem identity, or closing existing OPEN spatial evidence.

## Required checks

1. Every existing `GeometryPackage` primitive maps to exactly one semantic object in deterministic source order.
2. The semantic package records the source governed-package hash, source candidate hash and source geometry hash.
3. Admitted packaging envelopes remain identified as admitted spatial envelopes and require preservation of engineering envelope and position.
4. Structural members remain structural hypotheses with `NOT_STRUCTURALLY_QUALIFIED` status; semantic metadata may not create a structural PASS.
5. Source-node octahedra remain source-location proxies and may not silently imply volume.
6. Existing `NO_ADMITTED_VOLUME::*` OPEN items remain visible in semantic output.
7. R1 does not infer tank/reactor/habitat/etc. subsystem classifications from primitive names, shape or position. `system_id` remains explicitly OPEN in v0.1.
8. Semantic output is byte-deterministic for identical source input and does not mutate the governed synthesis package.
9. Authority escalation, ordering corruption and frozen-authority claims fail closed.
10. Existing governed synthesis regression tests remain passing.

## Acceptance

R1 may be called implemented only after the focused test set passes. It may be called regression-safe only after the repository unit regression suite passes.

No result from this test plan creates canon, production, flight-dynamics or structural-qualification authority.
