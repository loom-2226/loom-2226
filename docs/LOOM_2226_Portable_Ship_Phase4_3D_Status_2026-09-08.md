# LOOM 2226 — Portable Ship Qualification — Phase 4 3D Status

**Date:** 2026-09-08  
**Status:** ENGINEERING / QUALIFICATION — PHASE 4 PASSED — FEATURE BRANCH — NOT CANON  
**Parent authority:** `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`  
**Phase-3 closure parent:** commit `56053a90a989e59c1153693f8dd2ab1bebcfad93`

## 1. Scope

Phase 4 is the Wayfarer compatibility + minimal-3D sniff qualification gate. It demonstrates that the generic ship-class authority can reproduce the current Wayfarer physical baseline and generate a deterministic crude 3D artifact without renderer-only numerical geometry becoming a second authority.

## 2. Live authority used

Work was based on live GitHub copies of:

- `geometry/wayfarer_geometry_seed.sql`;
- `src/wayfarer_geometry.py`;
- `docs/LOOM_2226_Portable_Ship_Simulation_Qualification_Work_Plan_2026-09-08.md`;
- the Phase-3 generic ship-class prototype and resolver artifacts.

The Phase-4 mapping preserves source/status labels rather than promoting lower-authority values.

## 3. Qualified artifacts

- `qualification/phase4/LOOM_2226_SHIPCLASSES_WAYFARER_PHASE4_GEOMETRY_v0.1.sql`
- `qualification/phase4/minimal_3d.py`
- `qualification/phase4/test_phase4_wayfarer_3d.py`
- `qualification/phase4/verify_all.py`

The generator emits deterministic:

- `wayfarer_minimal3d.json` — structured scene with primitive, transform, status and provenance;
- `wayfarer_minimal3d.obj` — crude portable OBJ generated only from primitives marked `RENDER`.

## 4. Authority discipline retained

The qualified mapping carries the current governed/current-engineering geometry needed for the sniff test, including the canonical 57 m overall length reference, 9 m nominal main-body diameter reference, major tank/longeron placement, +Z launch-bay/launch semantics, propulsion/relational regions, radiator roots, and -Z docking-side semantics.

Radiator physical panel geometry remains `OPEN` and is deliberately not rendered. The older 8 m × 5 m panel placeholder was not promoted into physical authority. Docking collar dimensions likewise remain `OPEN`.

The 57 m × 9 m reference envelope remains a non-rendered `REFERENCE_ENVELOPE`; it is testable metadata, not literal hull geometry.

## 5. Critical same-source coupled test

The verifier mutates the governed `planetary_launch` component transform from z=5.2 m to z=6.25 m. The same source row must move both:

1. generated launch geometry; and
2. physical launch mass centroid used by the mass resolver.

The expected wet center-of-mass shift is evaluated numerically as:

`33000 kg * (6.25 - 5.2) m / 1158500 kg`.

Observed:

- mutated launch z: `6.25 m`;
- mutated wet CoM delta z: `0.02990936555891241 m`;
- coupling numerical error: `2.7755575615628914e-17 m`.

This passes the critical same-authority requirement.

## 6. Pixel acceptance evidence

The Phase-4 verifier executed on Pixel / Termux under:

```text
Android-17-aarch64-64bit-ELF
Python 3.13.13
aarch64
```

### Online-installed run

Result:

```text
LOOM_PHASE4_VERIFY: PASS
```

All ten checks passed:

- `critical_same_source_coupling`
- `docked_mass_com`
- `foreign_keys`
- `main_body_reference`
- `overall_length`
- `radiators_open`
- `required_files`
- `side_semantics`
- `sqlite_integrity`
- `unit_suite`

Unit suite: `6` tests, no errors/failures/skips.

Reference numerics:

- DOCKED wet mass: `1,158,500 kg`;
- DOCKED wet CoM: `[26.676650841605525, 0.0, 0.14812257229175657] m`;
- scene bounds min: `[0.0, -4.3, -4.3] m`;
- scene bounds max: `[57.0, 4.3, 7.1] m`.

Artifact hashes:

```text
phase4_verification_result.json
38792e824e095e96d0d53bcb1001d4f65757bee603ce984f2d761bce3fb05b2e

wayfarer_minimal3d.json
2bbb05fdbdcaae873eec00091843cf1b72d2826e42b05658306da798b0a2f896

wayfarer_minimal3d.obj
68a9521bf3041e7355d628aa07b4f1f9b52ca6f058c6d582b3767b5b478b8ac8
```

### Mandatory offline repeat

With Wi-Fi and mobile data disabled, the same command was executed again.

Result:

```text
LOOM_PHASE4_VERIFY: PASS
```

The result JSON, scene JSON, OBJ hashes, environment fields and numerical outputs matched the online-installed run exactly.

This satisfies the mandatory offline and deterministic Pixel requirement for Phase 4.

## 7. Gate disposition

**PHASE 4: PASSED — WAYFARER COMPATIBILITY + MINIMAL-3D / SAME-AUTHORITY COUPLING GATE CLOSED.**

This authorizes progression to Phase 5 standalone flight-dynamics qualification only.

It does **not** authorize:

- production SHIPCLASSES promotion;
- destructive migration of current Wayfarer authority;
- Navigator/GIS/HUD physics-dependent implementation;
- invention of OPEN radiator, docking, RCS or inertia detail;
- merge without explicit authorization.

Navigator/GIS/HUD physics-dependent implementation remains hard frozen pending the full exit gate.
