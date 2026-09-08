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
- `qualification/phase3/shipclasses_geometry_resolver.py`
- `qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql`
- `qualification/phase3/test_phase3_geometry_coupling.py`

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

## 4. Development regression evidence

Before committing the original resolver/test Python artifacts, a local unit/functional run executed seven tests and reported:

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

Before committing the transform-coupling resolver, a second local unit run executed four focused transform tests and reported:

```text
Ran 4 tests in 0.002s
OK
```

Covered behavior:

1. one component transform moves both a mass centroid and a geometry primitive;
2. parent/child transform composition correctly rotates and translates child placement;
3. center-of-mass calculation uses transformed mass centroids;
4. transform cycles fail closed.

These are development regression results. The repository-level Wayfarer geometry-coupling tests have now been authored against the real prototype schema/seed/overlay, but mandatory Pixel acceptance has not yet been run for this Phase-3 increment.

## 5. Same-authority geometry coupling increment

Phase 3 now contains the first explicit same-source coupling seam required by the governing work plan.

The planetary launch is used as the initial controlled case because its carried-state mass, conservative working centroid, and working low-detail envelope are already present in live Wayfarer engineering authority.

The geometry-coupling overlay moves the launch placement into `component_transform`, resets the launch mass element centroid to component-local zero, and binds a low-detail `geometry_primitive` to that same component transform. The transform resolver composes parent/child translation and quaternion orientation into body-datum placement.

Required coupled behavior is therefore explicit:

```text
component_transform
      ├──> physical mass centroid
      └──> low-detail geometry pose
```

The accompanying repository test intentionally mutates the one launch transform and requires both mass and geometry placement to move together. This is the narrow precursor to the Phase-4 coupled test; it does not yet constitute full Wayfarer 3D qualification.

## 6. Important limitations still OPEN

Phase 3 is **not closed**.

The current prototype deliberately does not invent:

- exact Wayfarer RCS nozzle count/placement/directions;
- final radiator geometry or sweep envelopes;
- detailed tank fill geometry/inertia behavior;
- complete component-level inertia tensors;
- final docking collar dimensions;
- detailed torch application/gimbal geometry beyond currently governed sources;
- production metric hardware serialization beyond already governed machine/configuration facts.

The original resolver proves class/configuration/store/mass/CoM semantics. The new transform resolver proves the generic same-authority placement mechanism. Full inertia/effectors/geometry qualification remains ahead.

## 7. Next controlled sequence

1. execute the real repository Phase-3 mass/configuration and geometry-coupling tests together;
2. build deterministic prototype database construction and machine-readable verification around the accepted schema + seed + coupling overlay;
3. extend low-detail governed geometry only where current authority supports it;
4. preserve OPEN status for unresolved RCS/radiator/docking details;
5. run the resulting Phase-3 verifier on the Pixel, including an offline repeat;
6. only after that gate, proceed into Phase 4 Wayfarer compatibility + minimal-3D sniff qualification.

**Navigator/GIS/HUD physics-dependent implementation remains hard frozen.**

**No merge is authorized by this status record.**
