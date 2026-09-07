# LOOM 2226 — Stage F-PA-2 Infrastructure Authority Matrix

Date: 2026-09-08  
Status: **Audit evidence — feature branch / NON-CANON until governed merge**

## Authority

This document records results produced from the exact GitHub PR checkout by the read-only audit in `src/loom/infrastructure_authority_audit.py` and `tests/test_infrastructure_authority_audit.py`.

GitHub documentary authority applies. Chat/model memory is not a source of record.

Latest qualifying evidence for this revision is GitHub Actions run `34157614045` at feature-branch commit `d111c19859e97cd65e9c649dda9676f2b8440a55`. The unit regression suite completed **326 tests, PASS**.

## Correction to earlier F-PA-2 interpretation

An earlier version of this document incorrectly reported 104 infrastructure rows as navigation-grade and used frame-family labels that do not match the exact governed WORLD database. The exact row-level Git-backed audit supersedes those statements.

**Correct result: none of the 127 infrastructure spatial records are currently navigation-grade.**

The 127 stored XYZ+VXYZ records are engineering reference states. They are useful structured constraints and 3D reference geometry, but they are not yet authoritative flight-navigation states.

## Exact aggregate findings

### Core authority result

- infrastructure nodes: **127**
- complete stored XYZ + VXYZ states: **127 / 127**
- `entity_location_models.position_authority = ENGINEERING_REFERENCE`: **127 / 127**
- location `navigation_grade = false`: **127 / 127**
- orbit `navigation_grade = false`: **127 / 127**
- stored-state `navigation_grade = false`: **127 / 127**
- F-PA state authority: `AUTHORITATIVE_NON_NAVIGATION_GRADE`: **127 / 127**
- initial spatial derivability: `CONSTRAINED_DESIGN_REQUIRED`: **127 / 127**
- current simulator navigation readiness: `NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED`: **127 / 127**

No existing infrastructure vector may therefore be promoted into Navigator endpoint authority merely because it is present in `spatial_states`.

### Frame families

Exact WORLD values are:

- `PARENT_BODY_FIXED`: 53
- `PARENT_LOCAL_INERTIAL`: 32
- `HELIOCENTRIC_ECLIPJ2000`: 14
- `SYSTEM_BARYCENTRIC_INERTIAL`: 12
- `PARENT_EQUATORIAL_INERTIAL`: 6
- `EARTH_MOON_ROTATING`: 5
- `PARENT_POLAR_INERTIAL`: 2
- `SUN_EARTH_ROTATING`: 2
- `PLUTO_CHARON_ROTATING`: 1

These labels are the SQL authority vocabulary for this audit. No alternate remembered frame vocabulary is to be substituted.

### Geometry kinds

- `POINT`: 59
- `POINT_OR_REGION`: 48
- `POINT_OR_VOLUME`: 10
- `POINT_OR_ARC`: 7
- `REGION`: 3

### Precision classes

- `ROLE_CONSTRAINED`: 58
- `BODY_CONSTRAINED`: 50
- `MODEL_CONSTRAINED`: 10
- `REGION_CONSTRAINED`: 6
- `PARENT_CONSTRAINED`: 3

### Epistemic status

All 127 orbit/location models are explicitly engineering-derived:

- `ENGINEERING_DERIVED_CLASSIFICATION`: 56
- `ENGINEERING_DERIVED_FROM_CANON_ROLE`: 48
- `ENGINEERING_DERIVED_HELIOCENTRIC_REFERENCE`: 15
- `ENGINEERING_DERIVED_LINEARIZED_CR3BP_REFERENCE`: 7
- `ENGINEERING_DERIVED_BINARY_REFERENCE`: 1

This is consistent with the navigation-grade=false result and is a major F-PA finding: the existing layer is a disciplined reference/placement layer, not silently qualified operational navigation truth.

### Orbit/state completeness

- complete classical Keplerian definition: **64 / 127**
- incomplete/non-classical/regional definition: **63 / 127**
- `SURFACE_FIXED` orbit-family rows: **51**
- stored state validity `BODY_FIXED_PROVISIONAL`: **53**
- stored state validity `ORBIT_GEOMETRY_MODEL_3D`: **71**
- stored state validity `KUIPER_REGION_REFERENCE`: **3**

## Ground / surface infrastructure result

Ground infrastructure is included in the 127-row reference layer, but it is **not navigation-grade surface geography**.

The strongest direct evidence is:

- `PARENT_BODY_FIXED`: **53** rows;
- those rows remain non-navigation-grade;
- `BODY_FIXED_PROVISIONAL`: **53** stored-state rows;
- the exact WORLD/CIVSTATE schema scan finds **no structured latitude/longitude/elevation field family**.

Examples include Earth surface spaceports, Mars surface ports, lunar ports, Ceres surface/in-body facilities, Mercury surface facilities, and numerous moon/asteroid/KBO surface or in-body installations.

A provisional body-fixed XYZ reference at one epoch is not a substitute for a governed geodetic site definition. Navigation-grade surface authority still requires, where applicable:

- parent body;
- named body-fixed frame;
- latitude / longitude or body-shape equivalent;
- elevation / datum or explicit reference-surface semantics;
- authoritative body orientation/rotation model;
- body-fixed → inertial transform at arbitrary supported epoch;
- local-level frame for landing/surface operations;
- provenance, uncertainty and qualification metadata.

No missing geodetic values are to be reverse-engineered from provisional reference XYZ and silently promoted.

## Runtime frame-method result

`src/loom/spatial/frames.py` currently authorizes translation-only inertial transforms and rejects rotating/body-fixed transforms until authoritative orientation models are introduced.

F-PA therefore separates two questions:

1. **Is the stored infrastructure state navigation-grade?** Currently no, for all 127 rows.
2. **Could the declared frame family be handled by the current transform method if the state were later qualified?** This requires a separate frame-method compatibility classification using the exact SQL frame vocabulary.

The navigation-grade failure takes precedence today: all 127 require qualification/re-derivation before operational Navigator use regardless of frame family.

## Traffic-hub linkage caveat

The exact base schema contains `transport_hubs` with **12 rows**, but the current infrastructure matrix join on `transport_hubs.entity_id = infrastructure_nodes.entity_id` produced **0 matched extension rows**.

Therefore F-PA must audit the actual linkage semantics before claiming transport-hub traffic metadata applies directly to particular infrastructure nodes. The 12-row table remains real repository data; its relationship to the 127-node infrastructure registry is not yet demonstrated by this join.

## Docking / rendezvous result

The exact SQL inventory contains no structured docking, rendezvous, approach, keep-out or transition-point geometry family.

Station position/orbit authority and docking/approach authority therefore remain separate. Even after an infrastructure orbit is qualified, that alone will not create a rendezvous gate, approach corridor, hold point or docking-port state.

## SQL-first derivation consequence

For all 127 infrastructure nodes the next physical-authority path is:

```text
existing engineering reference SQL
        ↓
referenced derivation / placement model
        ↓
frozen Git canon constraints where needed
        ↓
NASA/JPL/NAIF/IDSS method where applicable
        ↓
candidate physical state / surface geography / orbit
        ↓
qualification
        ↓
governed SQL promotion
```

Existing engineering references are constraints and evidence, not discardable placeholders. But they also do not become navigation truth without qualification.

## No-promotion rule

This audit changes no WORLD/CIVSTATE values and promotes no coordinates/orbits. Any new surface geography, frame model, orbital re-derivation, station transition geometry, docking/landing authority or traffic regime requires a separate governed derivation and qualification step.