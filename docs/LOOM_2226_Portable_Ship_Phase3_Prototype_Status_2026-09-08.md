# LOOM 2226 — Portable Ship Qualification — Phase 3 Prototype Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 3 PASSED — PIXEL ONLINE + OFFLINE DETERMINISM GATE CLOSED — FEATURE BRANCH — NOT CANON  
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

These remain prototype qualification artifacts only. They do not replace the current Wayfarer geometry seed/compiler or any production/campaign SQLite authority.

## 2. Live authority used

The seed was mapped from live GitHub authority/current engineering sources including:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`
- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`
- `engineering/current/LOOM_2226_Wayfarer_Project_State_and_Pixel_Handoff_v0.2.md`

No chat-memory Wayfarer number was promoted into the prototype without a live GitHub source.

## 3. Qualified compatibility targets

| State | Dry mass | Wet mass | Dry CoM B [m] | Wet CoM B [m] |
|---|---:|---:|---|---|
| DOCKED | 858,500 kg | 1,158,500 kg | [27.990564938846827, 0, 0.19988351776354105] | [26.676650841605525, 0, 0.14812257229175657] |
| ABSENT | 825,500 kg | 1,125,500 kg | [28.238037552998183, 0, 0] | [26.819635717458908, 0, 0] |

The 300 t working-fluid/water family is represented as exactly 300,000 kg physical store mass at reference state: 250,000 kg normal remass-capable inventory plus 50,000 kg protected water. Operational labels do not create additional mass.

## 4. Same-authority geometry coupling

The planetary launch is the initial qualified same-source case:

```text
component_transform
      ├──> physical mass centroid
      └──> low-detail geometry pose
```

The geometry-coupling overlay moves launch placement into `component_transform`, resets the launch mass element centroid to component-local zero, and binds low-detail geometry to that same transform. The mass and geometry resolvers both consume the same governed transform chain.

## 5. First Pixel verifier execution — FAIL retained as evidence

The first real Pixel/Termux execution of `verify_all.py` correctly returned:

```text
LOOM_PHASE3_VERIFY: FAIL
```

Eight checks passed and `docked_mass_com` failed. Observed DOCKED mass remained exactly 1,158,500 kg, but CoM resolved incorrectly to `[26.05567544238239, 0, 0]`, with max error `0.6209753992231342 m`.

Root cause: after the geometry overlay moved launch placement into `component_transform`, the original mass resolver still treated `mass_element.cx/cy/cz` as already body-frame. The 33 t launch therefore contributed at body origin while geometry correctly resolved to `[21.8, 0, 5.2]`.

Repair:

- `shipclasses_resolver.py` now resolves mass-element body centroids through the governed component-transform chain;
- `test_phase3_overlay_mass_integration.py` guards integrated DOCKED and ABSENT mass/CoM after schema + seed + geometry overlay are all applied.

The initial FAIL remains part of the qualification record and is not rewritten as a PASS.

## 6. Pixel repaired online PASS

After installing the repaired resolver and new integration test, the Pixel verifier returned:

```text
LOOM_PHASE3_VERIFY: PASS
```

Environment:

```text
machine:  aarch64
platform: Android-17-aarch64-64bit-ELF
python:   3.13.13
```

All checks were true:

- `absent_mass_com`
- `docked_mass_com`
- `foreign_keys`
- `launch_pose_reference`
- `required_files`
- `same_authority_geometry_mass`
- `sqlite_integrity`
- `unit_suite`
- `working_fluid_no_double_count`

Unit suite:

```text
tests_run: 11
errors:    0
failures:  0
PASS
```

All reported numerical errors were exactly `0.0`.

Qualified numerics:

```text
DOCKED wet mass = 1158500.0 kg
DOCKED wet CoM  = [26.676650841605525, 0.0, 0.14812257229175657]
ABSENT wet mass = 1125500.0 kg
ABSENT wet CoM  = [26.819635717458908, 0.0, 0.0]
launch mass pose     = [21.8, 0.0, 5.2]
launch geometry pose = [21.8, 0.0, 5.2]
store mass           = 300000.0 kg
```

Online result hashes:

```text
phase3_verification_result.json
dff47b726b464c7a2a47c4b68f902a4205c61b07aa01db27f15ed9a8489721f8

canonical_db_snapshot
b32644422c8ae9593602a74ccf66987704b771f566300b574d599b3efb5184cb

database_sha256
858a5779712e321c27feccbc3cb82edabcc929f106b7258598d2eb38aaf9578f
```

## 7. Mandatory Pixel offline repeat — PASS / deterministic

With Wi-Fi and mobile data disabled, the same local command was executed again:

```text
python verify_all.py
```

The offline execution again returned:

```text
LOOM_PHASE3_VERIFY: PASS
```

The full numerical payload matched the repaired online PASS. The result JSON hash and canonical database snapshot hash were byte-identical:

```text
phase3_verification_result.json
dff47b726b464c7a2a47c4b68f902a4205c61b07aa01db27f15ed9a8489721f8

canonical_db_snapshot
b32644422c8ae9593602a74ccf66987704b771f566300b574d599b3efb5184cb
```

Therefore the Phase-3 verifier is demonstrated to execute locally on the Pixel, without network access, with deterministic code-judged PASS/FAIL and byte-identical qualification outputs across the repaired online and offline runs.

## 8. Phase-3 disposition

**PHASE 3: PASSED.**

The following gate claims are now supported:

1. Wayfarer can be instantiated non-destructively in the accepted generic ship physical contract;
2. current mass/configuration/store semantics reproduce governed Wayfarer reference behavior;
3. 300 t working-fluid/water accounting does not double count protected water;
4. illegal configuration state/transition behavior fails closed;
5. mass and low-detail geometry can consume one shared component-transform authority;
6. the integrated repository verifier catches cross-layer semantic defects that isolated unit suites can miss;
7. the repaired verifier passes on Android/Termux;
8. the same verifier passes offline;
9. online and offline qualification outputs are deterministic and byte-identical for the recorded result JSON and canonical database snapshot.

Phase 3 authorizes progression to Phase 4 minimal-3D / same-authority Wayfarer qualification only. It does **not** authorize production SHIPCLASSES promotion, production database replacement, or Navigator/GIS/HUD physics resumption.

## 9. Remaining OPEN engineering facts

Phase-3 PASS does not fabricate or close:

- exact Wayfarer RCS nozzle count/placement/directions;
- final radiator geometry or sweep envelopes;
- detailed tank fill geometry/inertia behavior;
- complete component-level inertia tensors;
- final docking collar dimensions;
- detailed torch application/gimbal geometry beyond currently governed sources;
- production metric hardware serialization beyond already governed machine/configuration facts.

These remain explicit OPEN inputs to later qualification phases.

**Navigator/GIS/HUD physics-dependent implementation remains hard frozen.**

**No merge is authorized by this status record.**
