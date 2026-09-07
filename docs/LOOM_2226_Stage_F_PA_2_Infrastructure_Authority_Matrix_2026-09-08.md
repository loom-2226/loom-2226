# LOOM 2226 — Stage F-PA-2 Infrastructure Authority Matrix

Date: 2026-09-08  
Status: **Audit evidence — feature branch / NON-CANON until governed merge**

## Authority

This document records results produced from the exact GitHub PR checkout by the read-only audit in `src/loom/infrastructure_authority_audit.py` and `tests/test_infrastructure_authority_audit.py`.

GitHub documentary authority applies. Chat/model memory is not a source of record.

## Exact aggregate findings

The governed WORLD database contains **127 infrastructure nodes** and the row-level audit resolves one joined physical-authority record for every node.

### Facility class

- `ORBITAL`: 109
- `SURFACE`: 15
- `SOLAR`: 3

### Geometry kind

- `parent_centered_orbit`: 85
- `heliocentric_orbit`: 23
- `rotating_operational_region`: 10
- `halo_orbit`: 4
- `atmospheric_operational_region`: 2
- `relay_shell`: 2
- `surface_region`: 1

### Frame family

- `PARENT_CENTERED_INERTIAL`: 85
- `HELIOCENTRIC_INERTIAL`: 23
- `BODY_FIXED`: 10
- `CR3BP_ROTATING`: 4
- `ATMOSPHERIC_BODY_FIXED`: 2
- `LOCAL_ORBITAL`: 2
- `SURFACE_BODY_FIXED`: 1

### Position / epistemic authority

`entity_location_models.position_authority`:

- `CANON_DIRECT`: 39
- `DERIVED_QUALIFIED`: 88

`orbit_geometry_models.epistemic_status`:

- `CANON_DIRECT`: 39
- `DERIVED_QUALIFIED`: 88

`spatial_states.validity_status`:

- `CANON_DIRECT`: 39
- `DERIVED_QUALIFIED`: 88

### Precision class

- `HIGH`: 72
- `MEDIUM`: 48
- `LOW`: 7

### Orbit family

- `CIRCULAR_PARENT_CENTERED`: 85
- `HELIOCENTRIC_CIRCULAR`: 23
- `ROTATING_CYLINDER_REGION`: 10
- `CR3BP_HALO_APPROX`: 4
- `ATMOSPHERIC_OPERATIONAL_REGION`: 2
- `RELAY_ORBIT_SHELL`: 2
- `SURFACE_REFERENCE`: 1

### State completeness

- complete stored XYZ + VXYZ state: **127 / 127**
- complete classical Keplerian definition: **111 / 127**
- non-Keplerian / region / shell representation: **16 / 127**
- transport-hub extension rows: **12**

### Existing navigation-grade flags

The location, orbit and stored-state layers agree in aggregate:

- navigation-grade true: **104**
- navigation-grade false: **23**

The initial audit therefore classifies the stored 6D states as:

- `AUTHORITATIVE_NAVIGATION_GRADE`: 104
- `AUTHORITATIVE_NON_NAVIGATION_GRADE`: 23

and initial spatial derivability as:

- `DETERMINATE_FROM_EXISTING_AUTHORITY`: 104
- `CONSTRAINED_DESIGN_REQUIRED`: 23
- `UNDERDETERMINED`: 0

These labels describe the existing SQL flags and state completeness. They are **not yet the final simulator-usable qualification**.

## Critical qualification caveat — stored navigation grade is not yet runtime usability

`src/loom/spatial/frames.py` currently authorizes translation-only inertial frame transforms and explicitly rejects non-inertial / rotating / body-fixed transforms until an authoritative orientation model is promoted.

Therefore F-PA must not interpret all 104 stored `navigation_grade=1` infrastructure states as immediately usable navigation truth at arbitrary game epoch.

The following frame families require explicit runtime-method qualification before simulator promotion:

- `BODY_FIXED`: 10
- `ATMOSPHERIC_BODY_FIXED`: 2
- `SURFACE_BODY_FIXED`: 1
- `CR3BP_ROTATING`: 4
- `LOCAL_ORBITAL`: 2

The inertial families are structurally closer to current runtime support:

- `PARENT_CENTERED_INERTIAL`: 85
- `HELIOCENTRIC_INERTIAL`: 23

Even these must retain their existing source, model, validity, precision and navigation-grade metadata; no row is regraded merely because its frame family is supported.

## Surface-location result

The 15 `SURFACE` nodes do have stored physical-state/model records, but the exact SQL inventory contains no structured latitude/longitude/elevation field family.

Some surface entries are represented by body-fixed or rotating operational regions rather than a unique geodetic point. A complete stored 6D vector at one epoch therefore does **not** substitute for navigation-grade surface geography at arbitrary epoch.

Required future surface authority remains:

- body-fixed latitude / longitude;
- elevation or explicit reference-surface semantics;
- named body-fixed frame;
- authoritative body orientation / rotation model;
- epoch transform into inertial 3D state;
- local-level frame for landing / surface-relative operations;
- provenance and uncertainty / precision status.

No such values are to be inferred merely from the existing stored XYZ row.

## Docking / rendezvous result

The exact SQL inventory contains no structured docking, rendezvous, approach, keep-out or transition-point geometry family.

Therefore station position/orbit authority and docking/approach authority must remain separate. Existing station 6D state does not imply a rendezvous gate, approach corridor, hold point or docking-port state.

## F-PA-2 next qualification split

The next audit step is to classify every node into **runtime usability**, separate from the SQL `navigation_grade` flag:

- `RUNTIME_RESOLVABLE_NOW`
- `STORED_NAV_GRADE_FRAME_UNSUPPORTED`
- `SPECIAL_MODEL_QUALIFICATION_REQUIRED`
- `NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED`

The split must be determined from the exact row's frame family, geometry kind, source/derivation model, epoch semantics, validity status and current spatial-runtime capabilities.

Only after that split should F-PA consult frozen text canon for unresolved physical constraints or use NASA/JPL/NAIF/IDSS methodology to derive missing authority.

## No-promotion rule

This audit changes no WORLD/CIVSTATE values and promotes no coordinates/orbits. Existing SQL remains untouched. Any new surface geography, frame model, orbital re-derivation, station transition geometry or docking/landing authority requires a separate governed derivation and qualification step.