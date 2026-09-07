# LOOM 2226 — Stage F-PA Physical Authority Audit

Date: 2026-09-08
Status: **Stage F-PA audit — feature branch / NON-CANON until governed merge**
Parent authority: `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`

## 0. Documentary authority

All findings in this audit must be supported by live GitHub repository artifacts. Chat history and model memory may identify a source but are not documentary authority. If GitHub and chat differ, GitHub wins.

This stage is audit/classification first. It does not invent or promote physical constants, surface coordinates, station orbits, traffic rules, transition geometry, or campaign authority.

### 0.1 SQL-first physical derivation authority

```text
1. EXISTING WORLD / CIVSTATE SQL
        ↓
2. GOVERNED MODEL / DERIVED DATA REFERENCED BY SQL
        ↓
3. FROZEN TEXT CANON FROM LIVE GITHUB — only to constrain unresolved SQL gaps
        ↓
4. NASA / JPL / NAIF / IDSS methods and standards — methodology, not setting authority
        ↓
5. CANDIDATE DERIVED PHYSICAL STATE
        ↓
6. QUALIFICATION / REVIEW
        ↓
7. GOVERNED PROMOTION BACK INTO STRUCTURED SQL AUTHORITY
```

Rules:

- Existing SQL is the first structured source for physical class, parent, location/orbit model, spatial state, provenance, traffic relationships and engineering metadata.
- Follow any governed referenced model before consulting prose canon.
- Frozen text canon constrains unresolved SQL gaps; it does not silently override populated SQL.
- NASA/JPL/NAIF/IDSS define derivation/representation methods; they do not choose fictional LOOM coordinates or orbital elements.
- SQL↔canon conflicts stop the pipeline until explicitly reconciled.
- Underdetermined geometry remains design-required/underdetermined rather than fabricated.
- Simulator-facing promoted results should be structured SQL or a governed referenced physical model.

Infrastructure-node derivation tracking must include `PRIMARY_STRUCTURED_SOURCE`, `REFERENCED_MODEL_SOURCE`, `TEXT_CANON_CONSTRAINT`, `SOURCE_CONFLICT_STATUS`, `SPATIAL_DERIVABILITY`, `DERIVATION_STANDARD_OR_METHOD`, `QUALIFICATION_STATUS`, and `PROMOTION_TARGET`.

`SPATIAL_DERIVABILITY` values are `DETERMINATE_FROM_EXISTING_AUTHORITY`, `CONSTRAINED_DESIGN_REQUIRED`, and `UNDERDETERMINED`.

## 1. Audit classification

- `AUTHORITATIVE_NAVIGATION_GRADE`
- `AUTHORITATIVE_NON_NAVIGATION_GRADE`
- `DERIVED_QUALIFIED`
- `APPROXIMATE_PRESENTATION_ONLY`
- `SEMANTIC_LOCATION_ONLY`
- `MISSING`
- `DEPRECATED_OR_SHADOW`

## 2. GitHub-authoritative findings

### 2.1 Exact WORLD / CIVSTATE inventory

Exact Git-backed audit of the governed databases established:

- WORLD SHA-256: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`
- WORLD size: `4,882,432` bytes
- WORLD tables: `42`
- CIVSTATE SHA-256: `9ef530bdc1b8d867fe217a8c6d3a05e3926b0b09b0d66a91ce090b3e52fae560`
- CIVSTATE size: `8,093,696` bytes
- CIVSTATE tables: `53`

Key WORLD rows:

- `infrastructure_nodes`: 127
- `entity_location_models`: 127
- `orbit_geometry_models`: 127
- `spatial_states`: 127
- `ephemeris_states`: 48
- `celestial_dynamics`: 48
- `orbit_snapshots`: 20
- `placement_models`: 28
- `transport_hubs`: 12

### 2.2 Shared spatial state boundary

`src/loom/spatial/sqlite_source.py` opens WORLD read-only/query-only and preserves reference frame, XYZ, velocity, provenance, navigation grade, model ID and validity status when promoting stored state into the shared `SpatialState` contract.

The presence of a complete stored vector does not by itself establish operational navigation authority.

### 2.3 Infrastructure physical-authority correction and exact result

Row-level audit in `src/loom/infrastructure_authority_audit.py`, qualified by GitHub Actions run `34157867196` after exact-vocabulary correction, establishes:

- complete stored XYZ + VXYZ reference state: **127 / 127**;
- `position_authority = ENGINEERING_REFERENCE`: **127 / 127**;
- location `navigation_grade = false`: **127 / 127**;
- orbit `navigation_grade = false`: **127 / 127**;
- stored-state `navigation_grade = false`: **127 / 127**;
- F-PA classification `AUTHORITATIVE_NON_NAVIGATION_GRADE`: **127 / 127**;
- initial derivability `CONSTRAINED_DESIGN_REQUIRED`: **127 / 127**;
- simulator navigation readiness `NON_NAVIGATION_GRADE_REDERIVATION_REQUIRED`: **127 / 127**.

An earlier F-PA-2 interpretation reporting 104 navigation-grade infrastructure rows was wrong and is superseded by this exact Git-backed row-level result.

The existing infrastructure layer is therefore a useful engineering reference/constraint layer, **not operational Navigator endpoint authority**.

### 2.4 Exact infrastructure frame vocabulary

The governed SQL contains:

- `PARENT_BODY_FIXED`: 53
- `PARENT_LOCAL_INERTIAL`: 32
- `HELIOCENTRIC_ECLIPJ2000`: 14
- `SYSTEM_BARYCENTRIC_INERTIAL`: 12
- `PARENT_EQUATORIAL_INERTIAL`: 6
- `EARTH_MOON_ROTATING`: 5
- `PARENT_POLAR_INERTIAL`: 2
- `SUN_EARTH_ROTATING`: 2
- `PLUTO_CHARON_ROTATING`: 1

The audit now separates frame-method compatibility from navigation qualification:

- current translation-only inertial method compatible: **66**;
- rotating/body-fixed method unsupported by current runtime: **61**.

This compatibility split does not regrade any infrastructure state. All 127 remain non-navigation-grade.

### 2.5 Ground / surface authority

Ground and surface infrastructure is included in the 127-row engineering reference layer. The exact data contains **53 `PARENT_BODY_FIXED`** rows and **53 `BODY_FIXED_PROVISIONAL`** stored states.

However, the exact WORLD/CIVSTATE schema scan found **no structured latitude/longitude/elevation field family**. The current runtime also lacks an authoritative rotating/body-fixed orientation transform.

Therefore present surface/reference vectors must not be treated as navigation-grade geography. Future surface promotion requires, as applicable: parent body, named body-fixed frame, latitude/longitude or body-shape equivalent, elevation/datum semantics, body orientation/rotation, epoch transform, local-level frame, provenance and uncertainty/qualification.

### 2.6 Infrastructure orbit/reference models

`orbit_geometry_models` contains a full 127-row engineering-reference layer. Exact row-level findings include:

- complete classical Keplerian definition: **64 / 127**;
- incomplete/non-classical/regional definition: **63 / 127**;
- `SURFACE_FIXED` orbit family: **51**;
- engineering-derived epistemic statuses on all 127 rows.

These models constrain later derivation but are not themselves navigation-grade.

### 2.7 Celestial ephemeris and propagation

`src/loom/spatial/sqlite_celestial_catalog.py` permits genuine navigation-grade J2000/ECLIPTIC states directly. Where direct moon coverage is absent, it may derive a parent-centric two-body osculating model only from a genuine navigation-grade anchor and parent GM; propagated output retains lesser qualification and explicit unmodeled-perturbation metadata. Display-only circular fallback is prohibited from physics authority.

Classification:

- genuine direct navigation-grade celestial state: `AUTHORITATIVE_NAVIGATION_GRADE`;
- qualified two-body propagation from such an anchor: `DERIVED_QUALIFIED`;
- display fallback: `APPROXIMATE_PRESENTATION_ONLY`.

### 2.8 Reference frames

`src/loom/spatial/frames.py` currently supports translation-only inertial transforms and explicitly rejects rotating/body-fixed transforms until an authoritative orientation model is introduced.

This blocks navigation-grade surface geography, rotating-body local scenes, landing geometry and surface-relative telemetry until the missing orientation/frame authority is supplied and qualified.

### 2.9 Gravity

`src/loom/spatial/gravity.py` provides deterministic Newtonian point-mass acceleration from explicit state inputs and GM. It does not own ephemeris generation, trajectory integration or collision geometry and does not regrade source states.

Point-mass gravity is `DERIVED_QUALIFIED` within that contract. Higher harmonics, non-spherical gravity, atmosphere/drag, SRP and terrain/collision require separate inventory/authority.

### 2.10 Traffic authority linkage

WORLD has traffic-related structures and `transport_hubs` contains 12 rows. However, the current row-level infrastructure join on `entity_id` produced **0 direct matches**. F-PA must determine the actual linkage semantics before claiming those 12 rows map directly to specific infrastructure nodes.

No current evidence yet demonstrates a complete body-specific authorized-orbit / approach-corridor / clearance-law model.

### 2.11 Docking / rendezvous gap

The exact schema scan found no structured docking, rendezvous, approach, keep-out or transition-point geometry family in WORLD or CIVSTATE. Existing station reference state does not imply rendezvous gates, approach corridors, hold points or docking-port states.

### 2.12 Campaign persistence

`src/loom/campaign/shadow_ledger.py` declares JSON state plus RC6.1 history ledger canonical. `LOOM_CAMPAIGN_DEV.sqlite3` remains a non-authoritative diagnostic/reconciliation shadow.

Canonical richer simulator-state SQL persistence remains a future governed promotion rather than current authority.

## 3. Confirmed simulator gaps

1. qualified rotating/body-fixed orientation/frame model;
2. structured navigation-grade surface geography;
3. qualification/re-derivation of all 127 infrastructure reference placements before Navigator use;
4. body-specific authorized orbit and traffic-law model;
5. station rendezvous/transition/docking geometry;
6. surface deorbit/entry/terminal/landing transition geometry;
7. complete vehicle true-state dynamics loop;
8. sensor models and estimated-navigation state/covariance;
9. guidance/control/actuator loop;
10. telemetry derived from true/measured/estimated state rather than presentation values;
11. richer canonical campaign persistence after formal promotion.

## 4. Remaining F-PA work

### F-PA-1 — Exact WORLD/CIVSTATE inventory

**BASE INVENTORY COMPLETE.** Continue targeted row/relationship audits only where needed.

### F-PA-2 — Infrastructure physical-authority matrix

**CORE ROW-LEVEL AUTHORITY CLASSIFICATION COMPLETE.** All 127 are currently non-navigation-grade engineering references. Remaining work is derivation-source/canon-conflict/provenance classification and targeted relationship audits, including transport-hub linkage.

### F-PA-3 — CIVSTATE boundary audit

Determine which traffic, ownership, authority, port, commercial and institutional state belongs to civil context versus numerical physical navigation authority. CIVSTATE must not become an accidental trajectory-physics database.

### F-PA-4 — Campaign true-state audit

Inventory exact persisted mutable state versus missing translational/attitude state, mass/remass, thermal, power, propulsion, docking/landing/local state, navigation estimate, faults, traffic clearance and guidance state.

### F-PA-5 — Navigator/trajectory authority audit

Map current trajectory packet fields to simulator needs, especially ordinary XYZ/velocity coverage on both sides of metric transit, acceleration semantics, propulsion state, remass, thermal, target range/delta-v and provenance/qualification.

### F-PA-6 — Engineering authority audit

Map Wayfarer/vehicle engineering authority to runtime dynamics requirements: mass properties, thrust/acceleration envelopes, remass flow, power, thermal, attitude/RCS, structural limits and sensor/communications capability. Missing fields remain missing.

## 5. F-PA exit gate

F-PA is complete only when repository evidence supports:

1. exact WORLD/CIVSTATE inventory;
2. infrastructure-by-infrastructure physical-authority/derivability matrix;
3. campaign mutable-state gap matrix;
4. Navigator/trajectory telemetry coverage matrix;
5. engineering/dynamics coverage matrix;
6. explicit list of models/fields requiring new governed authority;
7. proposed schema/service changes separated from audit facts;
8. no display/reference approximation silently promoted to physics;
9. no new canon values invented merely for visual completeness;
10. SQL-first provenance for every future promoted spatial result;
11. all SQL↔text-canon conflicts explicitly reconciled before promotion.

Only after this gate should schema migration or bulk physical-data enrichment be proposed.