# LOOM 2226 — Portable Ship Qualification — Phase 3 Prototype Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 3 IN PROGRESS — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-2 contract:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_v0.2.md`

## 1. Current Phase-3 artifacts

- `qualification/phase3/LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql`
- `qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql`
- `qualification/phase3/shipclasses_resolver.py`
- `qualification/phase3/test_phase3_wayfarer.py`

These are prototype qualification artifacts only. They do not replace the current Wayfarer geometry seed/compiler or any production/campaign SQLite authority.

## 2. Live authority used

The seed was mapped from live GitHub authority/current engineering sources including:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`
- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`
- `engineering/current/LOOM_2226_Wayfarer_Project_State_and_Pixel_Handoff_v0.2.md`

No chat-memory Wayfarer number was promoted into the prototype without a live GitHub source.

## 3. Compatibility results

The prototype reproduces the current Wayfarer reference mass/CoM compatibility model for the two presently modeled launch states.

Reference values:

| State | Dry mass | Wet mass | Dry CoM B [m] | Wet CoM B [m] |
|---|---:|---:|---|---|
| DOCKED | 858,500 kg | 1,158,500 kg | [27.990564938846827, 0, 0.19988351776354105] | [26.676650841605525, 0, 0.14812257229175657] |
| ABSENT | 825,500 kg | 1,125,500 kg | [28.238037552998183, 0, 0] | [26.819635717458908, 0, 0] |

The 300 t working-fluid/water family is represented as exactly 300,000 kg of physical store mass at reference state: 250,000 kg normal remass-capable inventory plus 50,000 kg protected water. Operational labels do not create additional mass.

## 4. Local regression evidence before Python commit

Before committing the resolver/test Python artifacts, a local unit/functional run executed seven tests and reported:

```text
Ran 7 tests in 0.008s
OK
```

Covered behavior:

1. docked wet mass/CoM compatibility;
2. launch-absent wet mass/CoM compatibility;
3. protected-water minimum fails closed;
4. dry reference ledger compatibility;
5. no double-counting of the 300 t inventory;
6. illegal configuration state fails closed;
7. direct DOCKED→ABSENT transition is rejected while DOCKED→EXTRACTING is admitted.

This is development evidence, not the mandatory Pixel acceptance gate.

## 5. Important limitations still OPEN

Phase 3 is **not closed**.

The current prototype deliberately does not invent:

- exact Wayfarer RCS nozzle count/placement/directions;
- final radiator geometry or sweep envelopes;
- detailed tank fill geometry/inertia behavior;
- complete component-level inertia tensors;
- final docking collar dimensions;
- detailed torch application/gimbal geometry beyond currently governed sources;
- production metric hardware serialization beyond already governed machine/configuration facts.

The current resolver therefore proves class/configuration/store/mass/CoM semantics only. Full inertia/effectors/geometry qualification remains ahead.

## 6. Next controlled sequence

1. extend the Wayfarer prototype using only current governed geometry/component data;
2. preserve OPEN status for unresolved RCS/radiator/docking details;
3. add deterministic prototype database construction and machine-readable verification;
4. qualify component/configuration geometry from the same authority used by mass properties;
5. then proceed toward Phase 4 Wayfarer compatibility + minimal-3D sniff qualification.

**Navigator/GIS/HUD physics-dependent implementation remains hard frozen.**

**No merge is authorized by this status record.**
