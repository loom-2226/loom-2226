# LOOM Solar Phase 1 — Minimum Identity and Ephemeris Contract v0.1

**Status:** proposed implementation contract; documentation only  
**Primary class:** `class:engineering`  
**Date:** 2026-09-25  
**Parent plan:** `LOOM_SOLAR_SPATIAL_FOUNDATION_WORKPLAN_v1.0.md`

## 1. Decision

Phase 1 creates an isolated, additive Solar persistence domain. It does not clean, migrate, normalize, reconcile or depend on Ceres, `loom_world`, Earth, CIVSTATE or legacy SQLite data.

The physical PostgreSQL namespace for new Solar persistence is:

`loom_solar`

Existing qualified code contracts, especially `HybridCelestialStateService` and canonical `J2000/ECLIPTIC` state semantics, remain reusable interfaces. Reuse of an interface does not transfer database ownership.

## 2. Bounded purpose

The Phase 1 schema exists only to support the first qualified local DE440 path:

`LOOM body identity -> external NAIF identity -> pinned ephemeris source -> declared source coverage -> governed resolver`

No other Solar enrichment is required before DE440 qualification.

## 3. Minimum tables

### `loom_solar.body`

Stable LOOM identity for an astronomical/dynamical object.

Minimum fields:

- `body_id` — immutable LOOM-owned identifier; primary key.
- `canonical_name` — human-readable canonical name.
- `body_class` — controlled object class sufficient for the current body.
- `parent_body_id` — nullable self-reference where a parent relationship is required.
- `status` — lifecycle/catalog status; must not encode ephemeris quality.
- `created_at` — insertion timestamp.

Rules:

- external provider identifiers are never the primary key;
- catalog membership does not imply ephemeris availability;
- Phase 1 seeds only bodies required by qualification cases.

### `loom_solar.body_identifier`

Crosswalk from LOOM identity to external authorities.

Minimum fields:

- `body_id` — FK to `loom_solar.body`.
- `authority` — e.g. `NAIF`, `JPL_HORIZONS`, `IAU`.
- `identifier_type` — e.g. `NAIF_ID`, `HORIZONS_COMMAND`, `DESIGNATION`.
- `identifier_value` — provider identifier exactly as governed.
- `status` — active/retired/alias state as required.

Key rule:

`UNIQUE(authority, identifier_type, identifier_value)`

Multiple aliases may resolve to one LOOM `body_id`.

### `loom_solar.ephemeris_source`

Identity and integrity record for a locally evaluated ephemeris asset/product.

Minimum fields:

- `ephemeris_source_id` — immutable LOOM-owned source identifier; primary key.
- `provider` — authoritative provider, initially JPL/NAIF.
- `product_name` — initially DE440 where applicable.
- `product_version` — explicit provider/version label.
- `asset_filename` — governed local asset filename.
- `sha256` — cryptographic content hash.
- `byte_count` — exact asset size.
- `source_url` — acquisition source.
- `acquired_at` — acquisition timestamp.
- `status` — candidate/qualified/retired; qualification is explicit.

The DE440 binary remains a file, not a PostgreSQL blob.

### `loom_solar.ephemeris_coverage`

Declares what a source can authoritatively resolve.

Minimum fields:

- `ephemeris_source_id` — FK to source.
- `body_id` — nullable when coverage applies to the product generally; explicit body rows may be added when required.
- `valid_from` — lower time boundary.
- `valid_until` — upper time boundary.
- `reference_frame` — governed frame contract.
- `units` — governed state-vector units.
- `coverage_class` — product/body/derived coverage classification.
- `status` — candidate/qualified/retired.

Coverage is source metadata. It is not a universal LOOM time boundary.

## 4. Deliberately absent from Phase 1

Do not create Phase 1 tables for:

- atmospheres;
- resources/composition;
- gravity harmonics;
- exploration history;
- settlements/facilities;
- civilization state;
- transport/Lambert results;
- broad small-body catalog;
- monthly/materialized state vectors;
- generic property bags;
- presentation/GIS state.

Do not add a persistent state-cache table until measured resolver/integration needs justify one.

## 5. Authority and epistemic rules

Phase 1 `loom_solar` persistence is empirical infrastructure only.

A record is not empirical merely because it is dated before 2026, and is not fictional merely because it is dated after 2026. Source authority and provenance determine epistemic class.

Fictional settlements, future extraction, future population, polities and infrastructure do not belong in these Phase 1 tables.

Ceres/legacy rows may be used as comparison evidence but may not be copied into `loom_solar` without independent source qualification.

## 6. State interface boundary

PostgreSQL does not evaluate DE440.

The intended runtime path is:

`loom_solar identity/source metadata -> governed local SPICE adapter -> HybridCelestialStateService-compatible typed state`

The adapter must return the existing canonical state contract:

- explicit `entity_id/body_id`;
- explicit UTC request epoch with governed SPICE time conversion internally;
- `J2000/ECLIPTIC` canonical LOOM frame unless a separately reviewed contract changes it;
- position in km;
- velocity in km/s;
- provenance identifying the exact source/kernel;
- navigation-grade/qualification state;
- uncertainty/quality metadata where applicable.

No consumer calls SPICE directly.

## 7. Initial qualification seed

Phase 1 does not ingest a catalog. Seed only the minimum bodies needed for Phase 2–4 qualification, expected initially to include:

- Sun;
- Earth;
- Mars;
- Ceres.

Exact external identifiers must be verified against the acquired authoritative NAIF/JPL assets before insertion; this contract does not guess or hard-code them.

## 8. Migration discipline

Implementation must be one additive migration creating `loom_solar` and only the minimum tables above.

It must not:

- ALTER or DROP Ceres/`loom_world`/Earth/CIVSTATE tables;
- migrate legacy SQLite rows;
- rename existing schemas;
- change existing snapshots;
- require a legacy cleanup migration;
- create speculative future-enrichment columns merely for convenience.

Rollback for the unpopulated/candidate Phase 1 migration is removal of the newly introduced Solar namespace under normal migration/recovery controls; once qualified data exists, recovery follows governed backup/migration policy rather than destructive ad-hoc rollback.

## 9. Phase 1 exit gate

Phase 1 passes when:

1. the four-table minimum contract is reviewed;
2. its migration can be applied to a disposable/test database without touching non-Solar domains;
3. constraints reject duplicate external identifiers and orphan references;
4. a seed identity can resolve from LOOM `body_id` to a governed external identifier;
5. no Ceres/legacy cleanup is required.

Only then proceed to DE440 acquisition and local SPICE proof.
