# LOOM 2226 — Stage F-PB Wayfarer Physical Baseline

**Status:** IMPLEMENTATION / NON-CANON / STACKED ON F-PA  
**Date:** 2026-09-08

## Purpose

Use the existing Wayfarer dimensional/3D geometry work as the first concrete vehicle baseline for simulator-state contracts instead of inventing a dimensionless generic spacecraft.

## Live Git authority used

- `engineering/current/LOOM_2226_Wayfarer_Canon_Candidate_Specification_v0.1.md`
- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`

The geometry compiler is the dimensional source. Its generated `geometry/wayfarer_geometry.json` remains derived/regenerable output, not hand-authored authority.

## Authority preservation

The source material distinguishes CANON, DESIGN_BASELINE/CANDIDATE, DERIVED, LEGACY_COMPATIBLE, VISUAL_REFERENCE and OPEN values. The F-PB bridge preserves those labels. It does not promote candidate or open dimensions merely because they exist in the 3D model.

Examples:

- ship length and nominal main-body diameter remain CANON-backed geometry parameters;
- launch-bay placement remains DESIGN_BASELINE;
- docking-collar detailed geometry remains OPEN;
- radiator placeholder geometry remains OPEN and is not simulator authority.

## Body-frame baseline

The existing geometry coordinate convention is reused unchanged:

- x: forward-to-aft, bow datum x=0 m, aftmost permanent structure x=57 m;
- y: transverse;
- z: transverse, +Z launch-bay side, -Z docking side.

F-PB names this vehicle-local frame `WAYFARER_BODY`. This is a contract label for the existing dimensional convention, not a new orientation solution relative to inertial space.

## Configuration-dependent mass state

The existing geometry compiler already computes configuration-dependent mass and centre of mass for launch DOCKED versus ABSENT. F-PB exposes those generated mass states directly instead of recreating a second mass ledger.

This matters for later 6DOF and thrust-vector work: configuration changes may shift centre of mass and therefore cannot be represented by a single immutable point-mass location.

## Shared configuration vocabulary

F-PB reuses the existing geometry vocabularies:

- launch: DOCKED / EXTRACTING / ABSENT
- radiators: STOWED / DEPLOYING / DEPLOYED
- docking: FREE / APPROACH / SOFT_CAPTURE / HARD_DOCKED
- torch: OFF / SAFE / ACTIVE

No duplicate runtime vocabulary is introduced here.

## What this slice does not claim

It does not yet provide:

- an inertia tensor;
- centre-of-mass evolution during continuous remass flow;
- certified RCS thruster geometry;
- certified thrust-vector/gimbal envelope;
- docking capture geometry;
- final radiator geometry;
- inertial attitude or angular rate;
- full 6DOF vehicle dynamics.

Those remain later physical-authority tasks.

## Implementation

`src/loom/wayfarer_physical_baseline.py`

Contract version:

`LOOM_F_PB_WAYFARER_PHYSICAL_BASELINE_V1`

The adapter accepts the existing `LOOM.Wayfarer.Geometry` v0.1 compiler payload and fails closed if the schema or body-frame convention drifts.

## Qualification

`tests/test_wayfarer_physical_baseline.py` compiles the actual checked-in Wayfarer geometry seed and verifies that the simulator bridge preserves the body frame, authority statuses, mass/configuration dependence and existing state vocabulary.

No canon, geometry seed, campaign authority, Navigator trajectory mathematics or world database is modified by this slice.
