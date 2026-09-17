# LOOM 2226 — Ceres-only Inspector data visualization work plan

**Date:** 2026-09-18. **Primary class:** `class:asset-media` (planning/documentation only). **Status:** proposed implementation plan; not evidence that the production SQL has been exhaustively audited. **Target:** existing `docs/inspector/` Media + Canon Inspector only. **GIS:** visual-design reference, not a second application or implementation target. **Later:** institutions and other destinations are explicitly deferred.

## Goal and boundary

Make Ceres and its related fly-to objects intelligible at a glance while preserving traceability to production SQL, declared source authority and media provenance. The current Inspector exports only 182 approved/current media assets and a 21-field media/spatial record; its JSON panel is **not** a complete object characterization. Build a reviewed, explicitly allowlisted **derived public object profile** rather than exporting arbitrary SQLite rows, whole databases, CIVSTATE, private data, or unreviewed canon. No canon, WORLD, media database or frozen scientific-object mutation is authorized by this plan. Public disclosure of new fields requires separate review.

**Initial scope:** Ceres itself (`dwarf planet`/body; confirm the exact production class), its parent/orbital context, and the five already pictured facilities `CER-P01` Occator Industrial Lift & Surface Port, `CER-P02` Ceres Polar Volatiles Terminal, `CER-P03` Ceres Belt Exchange, `CER-P04` Ceres Shipyard Arc, `CER-P05` Ceres Metric & Loom Anchorage. Distinguish surface facilities (`CER-P01`, `CER-P02`) from orbital facilities (`CER-P03`, `CER-P04`); classify `CER-P05` from authoritative spatial data rather than guessing its physical placement. Ceres has no moon in this five-facility pilot: do not invent one. A generic moon design may be specified after this pilot, not populated with fabricated Ceres data. Existing Ceres gallery: `docs/ceres/index.html`; retain it during Pages deployment.

## Phase 0 — source inventory and completeness audit (first task)

1. Bootstrap live `main` governance and check relevant open PRs, current WORLD database/release provenance, schema/data dictionaries, existing SQL views and adapters, GIS visual examples and current Inspector exporter/UI. Inventory actual SQL tables, columns, keys, relationships, units, timestamps, provenance and source authority **before** promising any specific values. Read source SQLite in `mode=ro`; inspect PRAGMA schema, views and actual Ceres/`CER-P01`–`CER-P05` records. Where CIVSTATE or a separate database contains a relevant value, record the boundary and public-release approval requirement; do not quietly join or publish it.
2. Produce a **field-by-field completeness matrix** for Ceres and each of the five facilities: concept, SQL database/table/column or view, join path, object IDs, observed value/null/absence, units, epoch, authority/provenance, freshness, cardinality, public eligibility, candidate graphic and confidence. Distinguish `SOURCE_PRESENT`, `SOURCE_NULL`, `NO_SOURCE_FIELD`, `JOIN_UNRESOLVED`, `CONFLICT`, `DERIVED`, `WITHHELD` and `NOT_APPLICABLE`; never display a missing value as zero. Reconcile spatial entity IDs, knowledge noun IDs, media asset IDs and any economic/demographic IDs with explicit typed adapters, not name matching.
3. Compare every source-backed attribute that characterizes the object against what the current 21-field Inspector actually shows. Audit identities/aliases, hierarchy, location/coordinates and orbit, physical environment, infrastructure type/placement, capacity/throughput/utilization, population/workforce, power/resources, economic/transport measures, operational status, relationships, chronology, source/provenance and image metadata **only where the actual production model supports them**. Record unsupported concepts as gaps, not canon inventions. Include a machine-checkable coverage report: eligible fields, displayed fields, withheld fields, unresolved joins, nulls, mismatches and source snapshot hashes. Human review resolves which values are appropriate to publish.
4. Deliverables: `CERES_INSPECTOR_SQL_FIELD_AUDIT` (source-cited matrix and explicit missingness), join/ID diagram, disclosure allowlist proposal, sample approved Ceres and facility profile JSON, and a test fixture against the pinned source snapshot. **Exit:** all six scoped objects reconciled or explicitly marked unresolved; no claim of complete SQL coverage without actual schema/row inspection.

## Phase 1 — presentation concepts to compare in the Inspector

Design three alternatives against the same verified field matrix and show screenshots/thumbnails for each, including Pixel landscape/portrait and desktop. Reuse prior GIS's orbital hierarchy, spatial emphasis and legible numeric presentation **as references**, without embedding or modifying GIS.

| Option | Inspector interaction | Strength | Trade-off |
| --- | --- | --- | --- |
| A — illustrated dossier | Existing HERO thumbnail/image, concise identity + breadcrumb, compact key-metric tiles, themed sections, provenance disclosure | Fast object recognition and readable detail | Weak spatial comparison unless location module is added |
| B — spatial-first object card | HERO thumbnail + small schematic parent/orbit/surface-or-orbital locator, contextual neighbors, metrics below | Shows where an object sits relative to Ceres | Locator must be source-derived; no invented coordinates or fake orbital precision |
| C — comparative facility dashboard | Ceres overview with five image thumbnails, shared metric rows/small bars and facility drill-down | Exposes similarities, differences and data gaps | Requires compatible units/epochs and explicit null/denominator handling |

**Proposed sequencing, subject to prototype review:** build A as the common object profile; add B's verified locator where spatial data permits; add C only for genuinely comparable facility measures. These are design candidates, not approved UI behavior.

## Field-to-visualization decision matrix

Each element below is a **candidate**, not a claim that the SQL contains it. Phase 0 must resolve source, units, availability and public eligibility per object before implementation.

| Data element | Ceres/body presentation | Surface/orbital facility presentation | Alternative / guardrail |
| --- | --- | --- | --- |
| Identity, class, aliases, IDs | Title, type badge, inspectable identifiers | Facility title, type badge, typed IDs | IDs in provenance drawer; never use display names as join keys |
| Parent and ancestry | Breadcrumb + mini hierarchy | Facility → Ceres → parent chain | Source-backed links; unknown parent visibly unknown |
| HERO/reference media | Image + thumbnail gallery | Existing five facility thumbnails and originals | Preserve media approval, image provenance and asset-role labels |
| Spatial position / placement | Orbit schematic only if orbit fields exist | Surface/orbital locator only with actual placement | Schematic labeled non-scale; never imply verified lat/long when absent |
| Orbital / physical parameters | Unit-labeled compact fact grid and optional orbit diagram | Only applicable local/host parameters | Epoch/reference frame mandatory for dynamic coordinates; N/A ≠ missing |
| Environment/resources | Small facts or sourced composition bars | Relevant local constraints if recorded | No speculative resource grades or invented percentages |
| Facility role and systems | Facility-type mix if sourced | Role, services and systems chips | Taxonomy must follow real SQL values |
| Population / residents / transients | Breakdown with definitions and scope | Occupancy/served population only when directly supported | No CIVSTATE publication by default; prevent double counting |
| Workforce | Count/sector chart with definitions | Workforce and staffing only if source-backed | Distinguish headcount, FTE and modeled workforce |
| Capacity, throughput, utilization | Summary with denominators and time basis | Gauge/bars/sparklines only if denominator and time basis valid | Never show utilization without capacity/measurement basis |
| Power / resource flow | Power balance or labeled figures | Average/peak power and relevant flows | MW vs MWh; peak vs average; no invented network edges |
| Economy / capital | Labeled metrics and source period | Value added, capital, replacement cost if supported | Currency, price year and aggregation scope required |
| Cargo, passengers, ship calls | Modal/flow summary | Throughput cards and comparison bars | t/year, passengers/year, calls/time period; avoid mixed units |
| Ownership, governance, relations | Link list only after source/approval review | Operator/owner relationships only if verified | Institutions phase deferred; do not infer owners from names |
| Timeline / operational state | Epoch/status badge and sourced history | Commissioning/status/history where present | No fabricated chronology or conflation of canon vs runtime |
| Completeness and provenance | Coverage badges + source drawer | Per-field missingness, source, last verified, derivation | `SOURCE_NULL`/`WITHHELD`/`NO_SOURCE_FIELD` distinct; no generic 0 |

## Phase 2 — governed implementation slices

**Slice 1: typed profile contract.** Introduce a versioned, allowlisted `object_profiles` output alongside the existing media catalogue (or a separate JSON file if safer). Define stable object IDs, object kind, schema version, source snapshot, field-level `value/unit/epoch/source/status`, and media asset references. Explicitly define missingness, null and non-applicability. No generic `SELECT *`, browser SQL access or direct SQLite publication. Require publication approval for every new field; keep current 182-media invariant unchanged unless separately reviewed.

**Slice 2: Ceres dossier.** Add Ceres object navigation, source-backed identity/hierarchy, verified data tiles, thumbnail/HERO and provenance/missingness drawer. Do not break the existing 182-image gallery, search, filters, Inspect JSON or Ceres Pages gallery. Provide a visible distinction between a media record and an object profile.

**Slice 3: five facility dossiers.** Reuse one schema-driven facility component with surface/orbital/unknown placement variants. Include image thumbnails, verified contextual locator and only supported metrics. Do not hard-code five separate field-name templates or assume every facility has the same schema.

**Slice 4: optional Ceres comparison.** Only after comparable measures pass unit, epoch, definition and denominator checks, show five-facility comparisons with explicit missing-value labels and drill-down. No institutions view yet.

**Slice 5: publication.** Preview branch artifact; verify JSON allowlist, asset references, no database/CIVSTATE leakage, source hashes, browser behavior and Ceres preservation. Require `loom-gate` at current head, merge protected `main`, then run the existing **manual** Inspector Pages publication workflow with explicit `confirm_publication` and verify both `/inspector/` and `/ceres/` live. Follow `docs/MEDIA_INSPECTOR_PUBLISHING_RUNBOOK.md` once merged; until then its PR #243 is not main authority.

## Tests, review gates and recovery

- Audit: schema introspection, row-level six-object joins, coverage counts and provenance checks against pinned source files; failures and ambiguity recorded, not silently patched.
- Export: unit tests for typed adapters, allowlist, null semantics, unique IDs, units/epochs, deterministic output and disclosure; functional tests on the actual approved WORLD + media release; no CIVSTATE or arbitrary SQL export.
- UI: test Ceres + each facility, images, hierarchy, filters, mobile/desktop, accessible labels, zero/null/withheld states, comparison unit compatibility and failure behavior. Preview artifacts are not live publication.
- Production: full end-to-end regression immediately before final promotion, live smoke checks after manual Pages deployment, release hash and source commit recorded.
- Recovery: revert Inspector-only code through governed PR and republish from known-good `main` and matching release; retain existing Ceres gallery and immutable source databases.

## Immediate next action

Perform Phase 0 read-only source inventory and Ceres six-object SQL audit; bring back the verified field matrix and three thumbnail-backed Inspector mockups for a design decision **before** adding public data fields or modifying production UI. This plan alone does not authorize a data release or imply the completeness audit has passed.
