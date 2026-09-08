# LOOM 2226 — Portable Ship Qualification — Phase 3 Prototype Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 3 IN PROGRESS — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-2 contract:** `docs/LOOM_2226_Generic_Ship_Physical_Contract_v0.2.md`

## 1. Current Phase-3 artifacts

- `qualification/phase3/LOOM_2226_SHIPCLASSES_PROTOTYPE_SCHEMA_v0.1.sql`
- `qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql`
- `qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql`
- `qualification/phase3/shipclasses_resolver.py`
- `qualification/phase3/shipclasses_geometry_resolver.py`
- `qualification/phase3/test_phase3_wayfarer.py`
- `qualification/phase3/test_phase3_geometry_coupling.py`
- `qualification/phase3/test_phase3_overlay_mass_integration.py`
- `qualification/phase3/verify_all.py`

These are prototype qualification artifacts only. They do not replace the current Wayfarer geometry seed/compiler or any production/campaign SQLite authority.

## 2. Live authority used

The seed was mapped from live GitHub authority/current engineering sources including:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`
- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`
- `engineering/current/LOOM_2226_Wayfarer_Project_State_and_Pixel_Handoff_v0.2.md`

No chat-memory Wayfarer number was promoted into the prototype without a live GitHub source.

## 3. Compatibility targets

Reference values remain:

| State | Dry mass | Wet mass | Dry CoM B [m] | Wet CoM B [m] |
|---|---:|---:|---|---|
| DOCKED | 858,500 kg | 1,158,500 kg | [27.990564938846827, 0, 0.19988351776354105] | [26.676650841605525, 0, 0.14812257229175657] |
| ABSENT | 825,500 kg | 1,125,500 kg | [28.238037552998183, 0, 0] | [26.819635717458908, 0, 0] |

The 300 t working-fluid/water family is represented as exactly 300,000 kg of physical store mass at reference state: 250,000 kg normal remass-capable inventory plus 50,000 kg protected water. Operational labels do not create additional mass.

## 4. Development regression evidence

Earlier development runs passed the original seven mass/configuration tests and four focused transform tests.

After the first Pixel verifier failure described below, a targeted unit + functional regression was run before the resolver repair was committed. It verified both representations of the launch placement:

1. pre-overlay form: component transform identity + launch centroid stored in component-local fields;
2. overlay form: launch centroid local zero + placement stored in `component_transform`.

Both forms reproduced exactly:

- DOCKED wet mass `1,158,500 kg`;
- DOCKED wet CoM `[26.676650841605525, 0, 0.14812257229175657]`;
- ABSENT wet mass `1,125,500 kg`;
- ABSENT wet CoM `[26.819635717458908, 0, 0]`.

The repair changes the generic mass resolver so mass-element centroids are resolved through the governed component-transform chain rather than being treated as already body-frame after the geometry-coupling overlay.

## 5. Same-authority geometry coupling increment

The planetary launch remains the initial controlled same-source case:

```text
component_transform
      ├──> physical mass centroid
      └──> low-detail geometry pose
```

The geometry-coupling overlay moves the launch placement into `component_transform`, resets the launch mass element centroid to component-local zero, and binds the low-detail geometry primitive to that same transform.

## 6. First Pixel verifier execution — FAIL, useful integration finding

The first real Pixel/Termux execution of `verify_all.py` ran on:

```text
Android-17-aarch64-64bit-ELF
Python 3.13.13
aarch64
```

The executable correctly returned:

```text
LOOM_PHASE3_VERIFY: FAIL
```

Eight checks passed and one failed:

```text
absent_mass_com                 PASS
foreign_keys                    PASS
launch_pose_reference           PASS
required_files                  PASS
same_authority_geometry_mass    PASS
sqlite_integrity                PASS
unit_suite                      PASS
working_fluid_no_double_count   PASS
docked_mass_com                 FAIL
```

Observed DOCKED result:

```text
mass = 1,158,500 kg                         correct
CoM  = [26.05567544238239, 0, 0]           incorrect
expected [26.676650841605525, 0, 0.14812257229175657]
max error = 0.6209753992231342 m
```

The failure was deterministic and diagnostic. The repository unit suites each passed in isolation, but the integrated verifier applied the geometry overlay and then called the original mass resolver. That resolver still interpreted `mass_element.cx/cy/cz` as already body-frame. The overlay had intentionally moved the launch placement into `component_transform` and reset its local centroid to zero. Therefore the integrated mass solution placed the 33 t launch at body origin while the geometry resolver correctly placed it at `[21.8, 0, 5.2]`.

This was an integration bug in LOOM's prototype resolver semantics, not a Pixel numerical failure and not a canon-data discrepancy.

Repair:

- `shipclasses_resolver.py` now obtains mass-element body centroids through `resolve_mass_centroids_B()`;
- `test_phase3_overlay_mass_integration.py` explicitly guards DOCKED and ABSENT mass/CoM after schema + seed + geometry overlay are all applied together.

The first Pixel FAIL remains retained as qualification evidence. It is not rewritten as a PASS.

## 7. Important limitations still OPEN

Phase 3 is **not closed**. The prototype still deliberately does not invent:

- exact Wayfarer RCS nozzle count/placement/directions;
- final radiator geometry or sweep envelopes;
- detailed tank fill geometry/inertia behavior;
- complete component-level inertia tensors;
- final docking collar dimensions;
- detailed torch application/gimbal geometry beyond currently governed sources;
- production metric hardware serialization beyond already governed machine/configuration facts.

## 8. Next controlled sequence

1. install the repaired `shipclasses_resolver.py` and new integration test from the current feature-branch commit on Pixel;
2. rerun `python verify_all.py` online-installed;
3. if PASS, disable Wi-Fi and mobile data and rerun exactly the same verifier;
4. compare result JSON/database snapshot hashes and numerical outputs;
5. only after two Pixel PASS runs, close the Phase-3 portable prototype gate and proceed toward Phase 4 minimal-3D qualification.

**Navigator/GIS/HUD physics-dependent implementation remains hard frozen.**

**No merge is authorized by this status record.**
