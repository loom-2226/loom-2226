# LOOM Solar Spatial Foundation v1.0 — Architecture and Work Plan

**Status:** proposed engineering architecture/work plan; documentation only.
**Primary class:** `class:engineering`
**Date:** 2026-09-25
**Repository:** `loom-2226/loom-2226`
**Promotion target:** protected `main`

## 1. Purpose

Establish a qualified, time-addressable Solar System foundation shared by Navigator, Solar GIS/HUD, transportation modeling, and 2026→2226 civilization propagation.

This plan extends rather than replaces the current LOOM spatial-state authority. Existing `HybridCelestialStateService`, canonical `J2000/ECLIPTIC` state semantics, provenance/uncertainty handling and Navigator authority boundaries remain implementation inputs. Existing Ceres/legacy PostgreSQL and SQLite structures may be inspected for proven patterns, but they are not Solar data authority and are not prerequisites to be cleaned, reconciled, migrated or reorganized.

The governing architectural invariant is:

> **One identity system; separate empirical and fictional authorities; explicit lineage for every derived product that crosses those authorities.**

The second invariant is:

> **No presentation surface owns world truth. GIS/HUD renders; Navigator consumes physical state and owns navigation-domain outputs; persistence stores governed state; source adapters preserve external scientific provenance.**
## 2. Scope and non-scope

This work plan covers:

- celestial identity and external-identifier crosswalks;
- DE440-backed local ephemeris authority;
- a governed SPICE/SpiceyPy adapter and resolver;
- a broad empirical Solar System catalog including planets, satellites, asteroids, comets, TNOs, NEOs and interstellar objects such as 1I/ʻOumuamua;
- empirical physical/environmental enrichment with provenance and uncertainty;
- integration seams for GIS/HUD, Navigator and transportation/accessibility;
- the later interface to civilization propagation.

This planning PR does **not** install SpiceyPy, download kernels, change schemas, migrate data, alter runtime behavior, modify current Navigator/GIS/HUD code, change canon, change CIVSTATE, or authorize production deployment.

DE440 is the selected primary planetary ephemeris for this program. Its coverage boundary must be represented as source coverage, not hard-coded as a universal LOOM time limit.

## 3. Authority separation

LOOM must logically separate shared identity from evidentiary authority.
Proposed logical domains:

- **`solar_core`** — immutable LOOM celestial identity, aliases, hierarchy, frames and source identity.
- **`solar_empirical`** — externally sourced observations/reference data: ephemerides, mass/GM, radii/shape, rotation, atmosphere, composition, resources and exploration history.
- **`solar_world`** — LOOM fictional/world state: settlements, facilities, population, polities, economies, future infrastructure, extraction and fictional events.
- **`solar_derived`** — reproducible calculations whose lineage identifies empirical/world inputs and algorithms.

Derived records must declare at least one derivation class:

- `EMPIRICAL_DERIVED`
- `WORLD_DERIVED`
- `MIXED_DERIVED`

A date is not an epistemic classification. A fictional pre-2026 assertion remains fictional; a future empirical observation remains empirical when later ingested. Authority and provenance determine classification.

### Solar isolation and anti-rabbit-hole boundary

Solar work is a new, additive domain. Ceres and the existing `loom_world` implementation are out of scope except as read-only reference examples for proven structural patterns such as keys, snapshots, provenance, lineage, migrations, qualification and recovery.

The implementation must:

- leave existing Ceres, `loom_world`, Earth and CIVSTATE schemas/data intact unless a separately authorized work item explicitly changes them;
- create no cleanup, normalization, migration or reconciliation prerequisite against Ceres or legacy SQLite;
- avoid importing legacy celestial/entity rows wholesale merely because they already exist;
- use a dedicated Solar persistence namespace, presently `loom_solar`, for new empirical Solar-System persistence;
- keep Solar schema changes additive;
- reuse qualified code/interface behavior where appropriate without inheriting Ceres database ownership;
- add only data structures required by the current bounded Solar phase.

`loom_control` may be reused for genuinely shared governance/provenance machinery where its existing contract fits without modification. Reusing shared control infrastructure does not make Ceres or `loom_world` an upstream Solar data dependency.

**Anti-rabbit-hole rule:** no legacy PostgreSQL/SQLite cleanup is required to begin or qualify the Solar foundation. If Solar implementation exposes a legacy defect, record it separately and continue Solar work unless that defect directly blocks the qualified Solar interface.

The earlier logical names `solar_core`, `solar_empirical`, `solar_world` and `solar_derived` describe authority concepts, not required physical PostgreSQL schemas. The initial physical persistence target is one isolated `loom_solar` namespace; additional schemas require demonstrated need and separate review.

## 4. Celestial identity model

LOOM owns identity. NASA/JPL/NAIF/IAU identifiers are aliases, not primary identity.

Minimum conceptual entities:
- `celestial_body`: immutable LOOM `body_id`, canonical name, class, parent/system relationships.
- `body_identifier`: authority, identifier type, identifier value, validity/status.
- `source_artifact`: provider, dataset/product, version, retrieval/acquisition record, hash and coverage.
- temporal/provenanced property records rather than one mutable “current facts” row.

Catalog membership, ephemeris availability and physical-property completeness are independent states.

The registry must support ordinary bodies and unusual classes without special hacks: comets, dwarf planets, NEOs, Centaurs, TNOs, interstellar objects, spacecraft and dynamical points can share identity infrastructure while retaining distinct classifications.

## 5. Ephemeris architecture

Target flow:

```text
authoritative scientific assets
        |
        v
DE440 + qualified companion kernels
        |
        v
governed SPICE adapter
        |
        v
ephemeris resolver
        |
        v
typed celestial state authority
        |
        +---- Navigator
        +---- GIS / HUD
        +---- transportation/accessibility
        +---- derived simulation inputs
```
DE440 binary assets remain immutable files on the quantifactus development VM or later governed runtime storage. PostgreSQL stores metadata, identity, provenance, coverage, cached/derived results and world state; it is not the DE440 evaluator.

No LOOM consumer may call an external Horizons/API endpoint as a runtime requirement for ordinary DE440 state queries.

The resolver contract is conceptually:

`state(entity_id, epoch, frame) -> qualified state + provenance + coverage/quality`

and:

`relative_state(a, b, epoch, frame)`

with distance and frame-transform helpers derived from typed state.

Implementation must reconcile this interface with the already-promoted `HybridCelestialStateService.resolve(entity_id, epoch_utc)`; do not create a competing state authority.

## 6. Catalog and materialization strategy

LOOM should maintain a broad authoritative object inventory while avoiding millions of permanently materialized trajectories.

Three operational levels:

1. **Catalog level** — authoritative identities/designations/classes for the broad known Solar System.
2. **Operational spatial level** — locally supported high-value ephemeris/state coverage for planets, major satellites, dwarf planets, civilization-relevant asteroids/TNOs/NEOs, important comets and known interstellar objects.
3. **On-demand level** — long-tail objects retain identity locally; higher-cost ephemeris products are acquired/materialized only when needed under provenance controls.
The catalog must include comets and known interstellar visitors, including 1I/ʻOumuamua, as ordinary first-class objects.

DE440 is the planetary backbone, not the object catalog. Separate qualified satellite and small-body kernels/solutions may be composed through the resolver without pretending they are contained in DE440.

## 7. GIS / Navigator / HUD convergence

The existing convergence rule remains: GIS/HUD is the visual application surface; Navigator/domain services retain navigation and physics authority.

The Solar Spatial Foundation strengthens that rule by separating:

- **physical coordinates** — authoritative state in canonical frames;
- **presentation coordinates** — schematic, compressed, logarithmic or otherwise transformed geometry for usable displays.

GIS/HUD may transform physical state for display but must preserve traceability to the physical source state and must never promote presentation geometry into navigation authority.

A selected celestial entity should eventually expose coherent tabs/views for empirical physical state, navigation/accessibility, LOOM world state, infrastructure, resources, relationships and history without merging their authority classes.

## 8. Transportation and civilization seam

After ephemeris qualification, build a time-dependent transportation layer rather than a static distance table.

Initial transportation baseline may use Lambert solutions to derive departure/arrival geometry, time of flight and Δv opportunities. Lambert is a baseline accessibility model, not the final propulsion model.
Later propulsion-specific solvers may include low-thrust, gravity-assist, torch and metric-domain methods while consuming the same celestial-state authority.

Conceptually:

`ephemeris -> geometry -> accessibility -> transport -> infrastructure -> civilization`

Civilization propagation consumes accessibility; it does not invent instantaneous interplanetary connectivity.

## 9. Phased work plan

### Phase 0 — Bootstrap and dependency reconciliation

- create implementation work from current protected `main` in a clean quantifactus worktree;
- inspect current spatial-state authority, SQLite provider, Navigator/GIS contracts, PostgreSQL schemas and dependency manifests read-only;
- identify superseded/active seams before mutation;
- classify Ceres/legacy database structures as reference-only unless a Solar requirement independently justifies reuse;
- classify downstream components and required revalidation.

**Exit:** implementation scope references exact current Git authorities and does not duplicate an existing service.

### Phase 1 — Celestial identity and epistemic contracts

- define immutable LOOM body identity and external-ID crosswalk;
- define object taxonomy and hierarchy;
- define empirical/world/derived authority classes and lineage;
- define the minimum additive `loom_solar` persistence contract required for identity and ephemeris;
- explicitly prohibit Ceres/`loom_world` cleanup or migration as a Phase 1 dependency.

**Exit:** identity and authority contracts reviewed before schema/code implementation.
### Phase 2 — DE440 local authority

- acquire DE440 and required NAIF support kernels from authoritative sources;
- record source URL/product identity, byte count and cryptographic hashes;
- freeze controlled meta-kernel/configuration;
- pin SpiceyPy/toolchain versions;
- establish canonical time, frame, unit and aberration/state policy consistent with existing LOOM state authority.

**Exit:** reproducible local kernel environment with no runtime network dependency.

### Phase 3 — Governed ephemeris adapter

- implement one typed adapter/resolver behind the existing celestial-state authority;
- expose arbitrary-time state and relative-state operations;
- fail closed on missing identity, frame, source or coverage;
- carry source, provenance, uncertainty/quality and navigation-grade semantics.

**Exit:** stable typed interface; no consumer directly calls SPICE.

### Phase 4 — Qualification and 2250 ephemeris completion

The representative `EPHEMERIS_FOUNDATION_V1` qualification remains necessary but
is no longer sufficient to exit Phase 4.

Phase 4 now MUST also complete
`docs/architecture/LOOM_SOLAR_PHASE4_2250_COMPLETION_WORKPLAN_v1.0.md`.

Required rules:

- physical bodies resolve to physical centers; system barycenters remain separate
  first-class dynamical points and may not silently stand in for bodies;
- "through 2250" means uninterrupted state capability through
  `2250-12-31T23:59:59Z`, requiring source/model coverage through at least
  `2251-01-01T00:00:00Z`;
- promote the already-earned DE440/Ceres/official-planet-center authority into
  `loom_solar` before new catalog expansion;
- close Ceres, Saturn, Jupiter and Pluto physical-center horizon holes;
- qualify the major/strategic moons and the strategic resource/object priority set;
- establish a broad empirical catalog with explicit per-object state-capability
  status and governed offline position capability through 2250;
- preserve source-specific uncertainty and distinguish direct SPICE/Horizons
  authority from non-navigation-grade empirical propagation;
- test time conversion, frames, units, source/object coverage boundaries, identity,
  center-vs-barycenter semantics, deterministic replay and failure modes;
- run relevant unit, functional, PostgreSQL and backup/restore regression.

Catalog presence is not ephemeris qualification. Kernel target presence is not
object-level promotion.

**Exit:** `EPHEMERIS_FOUNDATION_V1 = PASS` **and** the Phase-4 2250 completion gate
passes with zero unresolved operational targets. Phase 5 is blocked until that
machine-readable completion is recorded.

### Phase 5 — Post-baseline empirical catalog expansion

Phase 5 begins only after the Phase-4 2250 completion gate has frozen the baseline
empirical catalog and state-capability matrix.

- ingest newly discovered or newly prioritized objects beyond the frozen baseline;
- refresh authoritative inventory/crosswalk snapshots through versioned successor
  manifests rather than mutating historical provenance;
- extend aliases, designations, classifications, discovery/source metadata and
  completeness status;
- preserve the Phase-4 rule that an object may not become operational merely because
  it is cataloged; operational promotion requires governed state capability for the
  required horizon and quality class.

**Exit:** versioned post-baseline catalog expansion with no regression of the frozen
Phase-4 2250 state foundation.

### Phase 6 — Post-baseline resolver/provider expansion

The baseline multi-provider resolver for planets, moons, strategic small bodies and
the Phase-4 empirical catalog is already required by the Phase-4 completion gate.

Phase 6 may add later provider classes, higher-fidelity models, spacecraft,
dynamical points or successor scientific products without changing consumer
contracts.

- compose additional qualified providers behind the existing resolver;
- preserve provider/coverage selection, source-specific uncertainty and validity;
- never downgrade an already-qualified Phase-4 target to a weaker implicit fallback.

**Exit:** successor provider capability integrates without regressing the frozen
Phase-4 state authority.

### Phase 7 — Empirical scientific enrichment

Add separately sourced, temporal/provenanced records for:

- mass/GM, shape/radii, density and rotation;
- gravity models;
- atmosphere/environment;
- composition and resource observations/estimates;
- exploration and observation history.

Resource records must preserve measurement method, spatial scope, uncertainty/confidence and observation epoch. Estimates must not become hard mining inventories.

**Exit:** empirical enrichment is queryable without contamination from `solar_world`.
### Phase 8 — GIS/HUD integration

- bind Solar GIS/HUD to the shared celestial-state and identity contracts;
- implement epoch-driven views and object-class filtering;
- preserve physical versus presentation-coordinate separation;
- avoid rendering the full catalog simultaneously; use level-of-detail/filtering.

**Exit:** GIS/HUD can inspect supported epochs and object classes without owning orbital truth.

### Phase 9 — Navigator integration

- ensure Navigator uses the same state resolver and identities;
- remove or deprecate duplicate ephemeris paths only after compatibility tests;
- preserve route/execution authority and existing metric-domain seams.

**Exit:** one qualified celestial-state authority serves Navigator and GIS/HUD.

### Phase 10 — Solar Transportation Accessibility v1

- implement baseline transfer-window/Lambert capability;
- produce time-dependent accessibility edges with explicit vehicle/assumption lineage;
- persist derived results as cache/products, not primary astronomical truth.

**Exit:** interplanetary accessibility is geometry-aware and reproducible.

### Phase 11 — Civilization propagation interface

- feed qualified accessibility into the 2026→2226 propagation model;
- let settlements, infrastructure, capital and industrial capacity create new origin nodes;
- retain fictional future state in world authority only.

**Exit:** propagation cannot silently spatial-teleport between bodies.
### Phase 12 — Freeze and promotion

- run required regression/qualification;
- publish provenance, hashes, compatibility classification and rollback path;
- update dependency/compatibility records as required;
- pass `loom-gate`;
- promote only through protected `main`.

**Exit:** `SOLAR_SPATIAL_FOUNDATION_V1` baseline is reproducible and governed.

## 10. Explicit prohibitions

Do not:

- store DE440 binary content as ordinary PostgreSQL domain rows;
- materialize monthly states for the entire small-body catalog by default;
- make Horizons/API availability an operational dependency;
- allow GIS/HUD to calculate or certify navigation truth;
- create a second celestial-state authority beside the existing typed service;
- infer source quality from object popularity;
- treat catalog presence as ephemeris availability;
- mix empirical resource observations with fictional 2226 reserves/extraction;
- use a date boundary such as 2026 as a substitute for provenance;
- overwrite historical source/version records in place;
- refactor, clean, migrate or normalize Ceres/`loom_world`/legacy SQLite as a prerequisite to Solar work;
- make Solar persistence depend on Ceres data ownership merely because Ceres contains earlier celestial rows;
- pre-design Solar tables for future enrichment before a bounded phase actually requires them.

## 11. Testing and promotion class

This planning PR is documentation-only and requires no functional test. Each implementation phase must declare its own primary change class and tests under current governance.
Expected implementation classes include `class:engineering`, `class:runtime` and `class:data`; mixed-class PRs should be avoided where clean seams exist.

Any future production promotion requires relevant unit/functional regression, dependency classification, rollback evidence and current `loom-gate`. No research or fictional/canon claim is promoted by this plan.

## 12. Recovery

The planning document is additive and can be reverted by reverting its commit.

Implementation must preserve:

- immutable source kernel copies/hashes;
- prior validated state-provider behavior until replacement qualification passes;
- prior database snapshots/migrations under existing recovery policy;
- explicit consumer bindings so a failed integration can return to the previous qualified provider.

## 13. First implementation campaign

The first bounded campaign is **Phases 0–4 only**. Database work in this campaign is additive and limited to the minimum `loom_solar` identity/ephemeris persistence required to qualify the local DE440 path; it does not include legacy cleanup:

`dependency reconciliation -> identity/authority contracts -> DE440 local assets -> governed adapter -> qualification`

Do not begin catalog-wide ingestion, Lambert work, HUD changes or civilization propagation until this campaign earns its PASS.

This keeps the architectural destination broad while the active lane remains small.
