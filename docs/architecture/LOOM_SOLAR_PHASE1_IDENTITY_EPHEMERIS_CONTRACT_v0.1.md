# LOOM Solar Phase 1 — Identity and Ephemeris Persistence Contract v0.1

**Class:** `class:engineering`
**Scope:** Phase 1 contract only; no database mutation, kernel acquisition, runtime integration, Ceres cleanup, Earth changes, or CIVSTATE changes.

## Decision

Solar persistence is a new additive PostgreSQL domain: `loom_solar`.

Ceres, `loom_world`, legacy SQLite, Earth, and CIVSTATE are not Solar data authorities and are not migration or cleanup prerequisites. Existing structures may be inspected only for proven patterns.

The initial contract deliberately contains four tables only:

1. `loom_solar.body` — immutable LOOM celestial identity.
2. `loom_solar.body_identifier` — external identifiers/aliases such as NAIF/JPL/IAU designations.
3. `loom_solar.ephemeris_source` — immutable acquired ephemeris/support artifact identity and provenance.
4. `loom_solar.ephemeris_coverage` — declared provider coverage for a body/source combination.

No state-vector table is required for Phase 1. DE440 remains a local immutable file and the future SPICE adapter evaluates arbitrary epochs. Persisted states, if later justified, are derived cache/products rather than astronomical authority.

## Identity rules

- `body_id` is LOOM-owned and stable. External IDs never become primary keys.
- Canonical names are labels, not identity.
- Parent relationships are optional because barycenters, dynamical points and unusual objects do not always fit a simple parent tree.
- Catalog membership does not imply ephemeris availability.
- Ephemeris availability does not imply physical-property completeness.
- The model must support planets, satellites, dwarf planets, asteroids, comets, TNOs, NEOs and interstellar objects without special-case identity hacks.

## Epistemic boundary

All four Phase 1 tables are empirical infrastructure. Fictional settlements, future extraction, future political state, future population and similar LOOM world assertions do not belong in `loom_solar`.

Derived calculations must preserve their empirical/world lineage outside this minimum Phase 1 persistence contract.

## Minimum schema semantics

### body

- `body_id text PRIMARY KEY`
- `canonical_name text NOT NULL`
- `body_class text NOT NULL`
- `parent_body_id text NULL REFERENCES loom_solar.body(body_id)`
- `status text NOT NULL DEFAULT 'ACTIVE'`
- `created_at timestamptz NOT NULL DEFAULT now()`

No physical facts such as mass, radius, atmosphere or resources are stored here.

### body_identifier

- `body_id text NOT NULL REFERENCES loom_solar.body(body_id)`
- `authority text NOT NULL`
- `identifier_type text NOT NULL`
- `identifier_value text NOT NULL`
- `status text NOT NULL DEFAULT 'ACTIVE'`
- `valid_from timestamptz NULL`
- `valid_until timestamptz NULL`
- primary key: `(authority, identifier_type, identifier_value)`
- uniqueness: `(body_id, authority, identifier_type, identifier_value)`

This permits, for example, one LOOM Earth identity to map to NAIF 399 while retaining other authoritative aliases.

### ephemeris_source

- `source_id text PRIMARY KEY`
- `provider text NOT NULL`
- `product_name text NOT NULL`
- `product_version text NULL`
- `artifact_filename text NOT NULL`
- `sha256 text NOT NULL UNIQUE`
- `byte_count bigint NOT NULL CHECK (byte_count > 0)`
- `source_url text NOT NULL`
- `acquired_at timestamptz NOT NULL`
- `source_class text NOT NULL`
- `status text NOT NULL DEFAULT 'ACQUIRED'`

The database records the artifact; it does not contain the DE440 binary.

### ephemeris_coverage

- `source_id text NOT NULL REFERENCES loom_solar.ephemeris_source(source_id)`
- `body_id text NOT NULL REFERENCES loom_solar.body(body_id)`
- `provider_target_id text NOT NULL`
- `center_id text NULL`
- `frame text NOT NULL`
- `valid_from timestamptz NOT NULL`
- `valid_until timestamptz NOT NULL`
- `quality_class text NOT NULL`
- primary key: `(source_id, body_id, provider_target_id, frame)`
- check: `valid_until > valid_from`

Coverage is explicit and source-specific. DE440 coverage is not treated as a universal LOOM time limit.

## Interface boundary

The future SPICE provider must sit behind the existing typed celestial-state authority rather than create a competing consumer API.

Canonical LOOM state semantics remain `J2000/ECLIPTIC`, km, km/s, explicit UTC request epoch with governed SPICE time conversion, geometric state unless separately qualified, and source provenance attached to every returned state.

No GIS/HUD consumer may call SPICE directly.

## Explicitly deferred

Not Phase 1:

- physical properties;
- atmospheres;
- resources/composition;
- exploration history;
- persisted state-vector cache;
- full JPL small-body catalog ingestion;
- Lambert/accessibility;
- GIS/HUD changes;
- Navigator behavior changes;
- civilization propagation;
- legacy Ceres/SQLite cleanup.

These are added only when a bounded later phase requires them.

## Phase 1 exit gate

Phase 1 passes when:

1. this identity/authority contract is reviewed;
2. the four-table schema can be created independently in an empty PostgreSQL database;
3. representative identities Earth, Mars, Ceres and 1I/ʻOumuamua can be represented without schema exceptions;
4. DE440 can be represented as a source artifact without storing binary content in PostgreSQL;
5. no Ceres, `loom_world`, Earth or CIVSTATE table is required to satisfy the schema;
6. no runtime behavior changes.

Only after this gate should Phase 2 acquire and freeze DE440/support kernels.
