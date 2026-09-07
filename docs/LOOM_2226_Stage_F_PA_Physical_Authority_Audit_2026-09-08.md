# LOOM 2226 — Stage F-PA Physical Authority Audit

Date: 2026-09-08
Status: **Stage F-PA audit — feature branch / NON-CANON until governed merge**
Parent authority: `docs/LOOM_2226_Simulation_Physical_Authority_Work_Plan_Amendment_2026-09-08.md`

## 0. Documentary authority

All findings in this audit must be supported by live GitHub repository artifacts. Chat history and model memory may locate a source but are not documentary authority. If GitHub and chat differ, GitHub wins.

This stage is audit/classification first. It does not invent or promote physical constants, surface coordinates, station orbits, traffic rules, transition geometry, or campaign authority.

### 0.1 SQL-first physical derivation authority

For spatial-authority work, the source chain is explicitly:

```text
1. EXISTING WORLD / CIVSTATE SQL
        ↓
2. GOVERNED MODEL / DERIVED DATA REFERENCED BY SQL
        ↓
3. FROZEN TEXT CANON FROM LIVE GITHUB — only to constrain unresolved SQL gaps
        ↓
4. NASA / JPL / NAIF / IDSS methods and standards — derivation methodology, not setting authority
        ↓
5. CANDIDATE DERIVED PHYSICAL STATE
        ↓
6. QUALIFICATION / REVIEW
        ↓
7. GOVERNED PROMOTION BACK INTO STRUCTURED SQL AUTHORITY
```

Rules:

- Existing SQL is the first structured source for an entity's physical class, parent, location model, orbit/placement model, spatial state, provenance, traffic/authority relationships and engineering metadata.
- If SQL references another governed model or dataset, follow that chain before consulting prose canon.
- Frozen text canon is a secondary constraint source for fields that SQL does not determine. Text canon does not override a populated SQL physical value silently.
- NASA/JPL/NAIF/IDSS standards define how a physically valid state, frame, orbit, rendezvous condition, docking geometry or surface frame is represented/derived; they do not independently choose fictional 2226 coordinates or orbital elements.
- Derived physical values remain candidate/derived authority until qualified and promoted through governed repository change.
- The simulator-facing authoritative result should be structured in SQL or a governed referenced physical model, not left only in prose.
- If SQL and frozen text canon conflict, **stop and reconcile the conflict explicitly**. Do not silently prefer SQL, prose, or whichever value produces a cleaner simulation.
- If neither SQL nor canon constrains a unique physical result, classify the missing geometry as design-required or underdetermined rather than fabricating it.

Each infrastructure-node audit must therefore include:

- `PRIMARY_STRUCTURED_SOURCE`
- `REFERENCED_MODEL_SOURCE`
- `TEXT_CANON_CONSTRAINT`
- `SOURCE_CONFLICT_STATUS`
- `SPATIAL_DERIVABILITY`
- `DERIVATION_STANDARD_OR_METHOD`
- `QUALIFICATION_STATUS`
- `PROMOTION_TARGET`

`SPATIAL_DERIVABILITY` uses:

- `DETERMINATE_FROM_EXISTING_AUTHORITY`
- `CONSTRAINED_DESIGN_REQUIRED`
- `UNDERDETERMINED`

## 1. Audit classification

Every relevant source/table/model is to be classified as one of:

- `AUTHORITATIVE_NAVIGATION_GRADE`
- `AUTHORITATIVE_NON_NAVIGATION_GRADE`
- `DERIVED_QUALIFIED`
- `APPROXIMATE_PRESENTATION_ONLY`
- `SEMANTIC_LOCATION_ONLY`
- `MISSING`
- `DEPRECATED_OR_SHADOW`

## 2. GitHub-authoritative initial findings

### 2.1 WORLD data artifacts

The governed repository contains `data/LOOM_2226.sqlite3` and `data/LOOM_2226_CIVSTATE.sqlite3`. Binary SQLite content cannot be promoted by inference from filenames; schema/content findings require either repository code that explicitly queries the tables or a reproducible audit of the exact Git blob.

### 2.2 Shared spatial state

`src/loom/spatial/sqlite_source.py` opens the WORLD SQLite read-only/query-only and promotes stored states into the canonical `SpatialState` contract. It distinguishes legacy `states` from first-class `spatial_states`, preserves reference frame, velocity, provenance, `navigation_grade`, model ID and validity status. This is a strong existing physical-authority boundary.

Initial classification:

- exact stored state with `navigation_grade=1`: `AUTHORITATIVE_NAVIGATION_GRADE` subject to source/epoch/frame validity;
- stored state with navigation grade false/absent: `AUTHORITATIVE_NON_NAVIGATION_GRADE` or lower according to provenance;
- renderer/display placement is not navigation authority merely because it has XYZ.

### 2.3 Celestial ephemeris and propagated states

`src/loom/spatial/sqlite_celestial_catalog.py` explicitly permits exact J2000/ECLIPTIC navigation-grade states directly. Where direct moon coverage is absent, it may derive a parent-centric two-body osculating model only from a genuine navigation-grade ephemeris anchor and parent GM. The propagated result explicitly carries `unmodeled_perturbations=True` and `navigation_qualification=PROPAGATED_NOT_DIRECT`. Display-only circular-period fallbacks are explicitly prohibited from physics authority.

Classification:

- exact navigation-grade J2000/ECLIPTIC state: `AUTHORITATIVE_NAVIGATION_GRADE`;
- two-body state propagated from genuine anchor: `DERIVED_QUALIFIED`, not equivalent to direct navigation-grade telemetry;
- display circular fallback: `APPROXIMATE_PRESENTATION_ONLY` and prohibited from physical promotion.

### 2.4 Reference frames

`src/loom/spatial/frames.py` currently authorizes translation-only inertial transforms. It explicitly rejects rotating/body-fixed transforms until an authoritative orientation model is introduced.

Classification:

- existing inertial translation frame transforms: `DERIVED_QUALIFIED` within their declared contract;
- body-fixed rotation/orientation transforms: `MISSING` for the simulator target.

This is a direct blocker for navigation-grade surface infrastructure, lat/lon/elevation resolution, landing corridors, rotating-body local scenes and surface-relative telemetry.

### 2.5 Gravity

`src/loom/spatial/gravity.py` computes deterministic Newtonian point-mass acceleration from explicit celestial `SpatialState` inputs and supplied GM. It explicitly does not own ephemeris generation, trajectory integration or collision geometry and does not promote source states to navigation grade.

Classification:

- Newtonian point-mass gravity primitive: `DERIVED_QUALIFIED`;
- body harmonics/non-spherical gravity: `MISSING` in this primitive;
- atmosphere/drag/SRP/terrain collision: outside this primitive and must be separately inventoried.

### 2.6 Campaign persistence

`src/loom/campaign/shadow_ledger.py` explicitly declares JSON state and RC6.1 history ledger canonical. `LOOM_CAMPAIGN_DEV.sqlite3` is a non-authoritative best-effort mirror used for diagnostics/reconciliation/later migration.

Classification:

- current JSON + history transition authority: authoritative campaign persistence under the current governed architecture;
- `LOOM_CAMPAIGN_DEV.sqlite3`: `DEPRECATED_OR_SHADOW` for authority purposes (active diagnostic shadow, not deprecated code);
- canonical campaign SQLite simulator state: `MISSING` pending governed promotion.

## 3. Confirmed simulator gaps from code authority

The following are already confirmed gaps without inventing database content:

1. authoritative rotating/body-fixed frame model;
2. navigation-grade surface coordinate resolution from body-fixed geography to inertial 6D state;
3. body-specific standard/authorized orbit regime and traffic-law model;
4. station transition/rendezvous gates and docking approach geometry;
5. surface entry/deorbit/terminal approach transition geometry;
6. complete vehicle true-state dynamics loop;
7. sensor measurement models and estimated-navigation state/covariance;
8. guidance/control/actuator state loop;
9. telemetry generated from true/estimated subsystem state rather than presentation values;
10. canonical campaign persistence capable of retaining the richer mutable simulator state after formal promotion.

## 4. Audit work still required before schema design

### F-PA-1 — Exact WORLD SQLite inventory

Audit the exact Git blob for:

- schema version and all tables/views;
- row counts;
- `entities` and celestial hierarchy;
- `states`, `ephemeris_states`, `spatial_states`;
- `celestial_properties`, `celestial_dynamics`;
- `entity_location_models`, `placement_models`, `orbit_geometry_models`, `orbit_snapshots`;
- infrastructure tables and engineering/physical profiles;
- provenance/source/authority tables;
- any existing surface coordinate, orientation, atmosphere, shape, terrain, orbit-law, traffic or docking fields.

### F-PA-2 — Infrastructure physical-authority matrix

For every infrastructure node classify:

- physical class: surface/orbital/Lagrange/free-space/semantic-only/other;
- parent body/system;
- time-resolvable 6D state available?;
- surface lat/lon/elevation available?;
- orbit/state model available?;
- reference frame explicit?;
- provenance/source?;
- navigation grade?;
- docking/landing metadata?;
- traffic authority/regime?;
- `PRIMARY_STRUCTURED_SOURCE`;
- `REFERENCED_MODEL_SOURCE`;
- `TEXT_CANON_CONSTRAINT`;
- `SOURCE_CONFLICT_STATUS`;
- `SPATIAL_DERIVABILITY`;
- `DERIVATION_STANDARD_OR_METHOD`;
- `QUALIFICATION_STATUS`;
- `PROMOTION_TARGET`;
- resulting F-PA classification.

No missing coordinates or orbital elements may be fabricated to complete the matrix.

### F-PA-3 — CIVSTATE boundary audit

Determine which traffic, ownership, authority, port, commercial and institutional data belongs to civil context versus physical navigation authority. CIVSTATE must not become an accidental trajectory-physics database.

### F-PA-4 — Campaign true-state audit

Inventory exact current JSON/history fields and determine which mutable simulator state is already persisted versus missing: translational/attitude state, mass/remass, thermal, power, propulsion, docking/landing/local state, navigation estimate, faults, traffic clearance and active guidance state.

### F-PA-5 — Navigator/trajectory authority audit

Map current trajectory packet fields to simulator needs, especially ordinary XYZ/velocity coverage before and after metric transit, acceleration semantics, propulsion state, remass, thermal, target range/delta-v and qualification/provenance.

### F-PA-6 — Engineering authority audit

Map Wayfarer/vehicle engineering authority to runtime dynamics requirements: mass properties, thrust/acceleration envelopes, remass flow, power, thermal, attitude/RCS, structural limits and sensor/communications capability. Missing fields remain missing; no canon engineering values are inferred.

## 5. F-PA exit gate

Stage F-PA is complete only when repository evidence supports:

1. exact WORLD and CIVSTATE schema/content inventory;
2. infrastructure-by-infrastructure physical-authority matrix;
3. campaign mutable-state gap matrix;
4. Navigator/trajectory telemetry coverage matrix;
5. engineering/dynamics coverage matrix;
6. explicit list of fields/models requiring new governed authority;
7. proposed schema/service changes separated from audit facts;
8. no display approximation silently promoted to physics;
9. no new canon values invented merely to make the simulator visually complete;
10. SQL-first derivation provenance captured for every promoted spatial result;
11. all SQL↔text-canon conflicts explicitly reconciled before promotion.

Only after this gate should a schema migration or bulk physical-data enrichment be proposed.