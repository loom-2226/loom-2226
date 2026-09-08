# LOOM 2226 — Portable Ship Qualification — Phase 4 3D Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 4 IN PROGRESS — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-3 closure parent:** commit `56053a90a989e59c1153693f8dd2ab1bebcfad93`

## 1. Scope

Phase 4 is the Wayfarer compatibility + minimal-3D sniff qualification gate.

It must demonstrate that the generic ship-class authority can reproduce the current Wayfarer physical baseline and generate a deterministic crude 3D artifact without renderer-only numerical geometry becoming a second authority.

## 2. Live authority re-fetched before work

Current work was based on live GitHub copies of:

- `geometry/wayfarer_geometry_seed.sql`;
- `src/wayfarer_geometry.py`;
- `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`;
- the Phase-3 generic ship-class prototype and resolver artifacts.

The Phase-4 mapping preserves source/status labels rather than promoting lower-authority values.

## 3. New Phase-4 artifacts

- `qualification/phase4/LOOM_2226_SHIPCLASSES_WAYFARER_PHASE4_GEOMETRY_v0.1.sql`
- `qualification/phase4/minimal_3d.py`
- `qualification/phase4/test_phase4_wayfarer_3d.py`
- `qualification/phase4/verify_all.py`

The generator emits deterministic:

- `wayfarer_minimal3d.json` — structured scene with primitive, transform, status and provenance;
- `wayfarer_minimal3d.obj` — crude portable OBJ generated only from primitives marked `RENDER`.

## 4. Authority discipline

The overlay maps currently governed/current-engineering geometry including:

- 57 m canonical overall length reference;
- 9 m canonical nominal main-body diameter reference;
- forward pressure hull;
- four major tanks;
- four longerons;
- technical core;
- integrated +Z launch-bay envelope and planetary launch;
- relational-plant region;
- shadow-shield region;
- reactor/torch region;
- magnetic-nozzle envelope;
- four radiator root markers;
- -Z docking-side marker.

Radiator physical panel geometry remains `OPEN` and is deliberately **not rendered**. Only the governed four-root count/root region is represented. The existing current compiler's 8 m × 5 m radiator placeholder is not promoted into the Phase-4 physical model.

Docking collar dimensions also remain `OPEN`; only the governed docking station / -Z side semantic marker is carried.

The 57 m × 9 m canonical reference envelope is stored as a non-rendered `REFERENCE_ENVELOPE`, so it remains testable without falsely turning a nominal envelope into literal hull geometry.

## 5. Critical coupled test

The Phase-4 test mutates the governed `planetary_launch` component transform from z=5.2 m to z=6.25 m.

The same database row must drive both:

1. the generated launch geometry pose; and
2. the physical mass centroid used by the Phase-3 mass resolver.

The expected center-of-mass shift is evaluated numerically as:

`33000 kg * (6.25 - 5.2) m / 1158500 kg`.

Any disagreement fails the gate.

## 6. Development regression evidence

Before the new Python artifacts were committed, local development checks completed:

- Python compilation of `minimal_3d.py`, the Phase-4 test module and verifier: PASS;
- deterministic synthetic-schema unit/functional exercise: PASS;
- scene rendered x-bounds: exactly 0.0 m to 57.0 m;
- canonical 57 m × 9 m reference envelope retained as non-rendered CANON metadata;
- four radiator roots retained as OPEN non-rendered status markers;
- launch DOCKED/ABSENT visibility semantics exercised;
- one transform mutation moved the generated launch geometry consistently.

These are development results only. Phase 4 remains OPEN until the repository verifier passes on the Pixel and repeats offline.

## 7. Pixel acceptance target

Run:

```text
python qualification/phase4/verify_all.py
```

The verifier checks:

- required Phase-3/Phase-4 artifacts;
- Phase-4 unit suite;
- SQLite integrity and foreign keys;
- exact 57 m rendered longitudinal extent;
- canonical 57 m × 9 m reference envelope;
- Phase-3 docked mass/CoM compatibility;
- +Z launch and -Z docking semantics;
- radiator OPEN/non-rendered discipline;
- critical same-source geometry/mass transform coupling;
- deterministic scene JSON and OBJ hashes.

A second run with Wi-Fi and mobile data disabled is mandatory.

## 8. Gate state

**PHASE 4: OPEN — PIXEL QUALIFICATION REQUIRED.**

No merge is authorized.

Production SHIPCLASSES remains untouched.

Navigator/GIS/HUD physics-dependent implementation remains hard frozen.
