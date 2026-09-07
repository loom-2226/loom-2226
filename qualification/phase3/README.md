# LOOM 2226 — Phase 3 Wayfarer Ship-Class Prototype

Status: ENGINEERING / QUALIFICATION — PROTOTYPE — NOT CANON — NOT PRODUCTION.

This directory contains the non-destructive Wayfarer-only prototype implementing the accepted Generic Ship Physical Contract v0.2.

The prototype must not replace or mutate the existing Wayfarer geometry seed/compiler pipeline until compatibility is demonstrated.

Current first artifact:

- `LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql`

Next required work:

1. seed only live-authority Wayfarer data with provenance/status preserved;
2. implement deterministic resolvers for active components, transforms, mass, CoM, inertia, stores, effectors, attachments, torch capability and metric eligibility;
3. add unit tests against current Wayfarer reference mass/CoM/configuration behavior;
4. keep OPEN RCS/radiator details unfilled rather than fabricating them;
5. do not promote to production SQLite until later qualification gates pass.
