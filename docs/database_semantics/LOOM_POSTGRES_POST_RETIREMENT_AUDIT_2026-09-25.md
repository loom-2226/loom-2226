# LOOM PostgreSQL post-retirement audit — 2026-09-25

**Class:** `class:data`  
**Status:** post-retirement verification record; no runtime/data mutation  
**Audit source main:** `ab9965ab59bbe929626023efd0c57a066ace8c85`  
**Primary database:** `loom_dev`

## Result

The Ceres PostgreSQL retirement remains successful and the retained authorities are healthy.

- Earth 2026→2226: **EXACT PASS** against the committed pre-retirement preservation contract.
- Timeline: **VALIDATED**, 43 milestones, full verifier PASS.
- Solar ephemeris runtime: **PASS**, pinned assets intact, 13/13 SPICE tests PASS.
- Solar PostgreSQL contract: **PASS**, 8/8 disposable integration tests PASS.
- Ceres Atlas operational data in `loom_dev`: **ABSENT**.
- Invalid PostgreSQL constraints in retained LOOM schemas: **0**.

The audit was read-only except for creation and removal of a disposable Solar migration test database.

## Earth authority

Snapshot `earth-v0-1-9934d0ac-20260925` remains `VALIDATED`.

- semantic SHA-256: `2d84b0b9137b3147e09723dff8cffe952e39e7d55f8062a73c0b13b62baee3a0`
- contract SHA-256: `78cbfde6d391ecdded2ae584fb1cd90b853d40eb8af25ed02d1a8be6bb9c3eb6`
- preservation overall SHA-256: `fedcc9b69e2e585663f821109be93338ca4711d4654097588f431cb991154ebc`
- schema fingerprint: `31c9887c619c4a7b68a08f57af3361f0d4d5ff4fcfe560fa08ffc24c1a510f1e`
- metadata fingerprint: `eb44a5ca63737c45f30dbc4fabacc91ffe567d8032e7ec13a9d5f4eb6caf4777`
- Narrator fingerprint: `94d61cc2ed30a4253bf30ab90703337c1f8147c478f93c6501e3a7ec5531c994`

Live `tools/earth_preservation.py` comparison against
`EARTH_AUTHORITY_PRESERVATION_PRE_CERES_RETIREMENT.json` returned `EXACT_PASS`.

Current row counts include 237 areas; 2,657,718 biological-cohort rows;
47,637 demographic rows; 7 derivations; 16,080 economic rows; 10,160
post-2100 labor-composition rows; 6,000 legacy-labor rows; 643,200 sector-asset
rows; and 160,800 sector rows.

Earth semantic/provenance controls remain intact: 16 snapshot-source links,
16 reachable source artifacts, 21 variable-semantic records, 15 model-context
records, 6 temporal-coverage records, 8 import batches, and 7 Earth derivations.
The referenced semantic-version set also matches the committed preservation
contract.

The existing Earth verifier passes with workforce invariant `80/80`,
2226 modeled value added `241453886085432.44`, and Ceres disposition
`RETIRED_FORENSIC_BASELINE`. Earth schema-separation qualification also
passes and reports the legacy CIV namespace as `RETIRED_EMPTY`.

Eight Earth Narrator views remain present, including the four current
Earth/country fact/year views plus snapshot, semantics, model-context and
temporal-coverage surfaces.

## Timeline authority

Snapshot `timeline-v0-1-0232bf23494f-20260925` remains `VALIDATED`.

The live verifier passed the full stored projection against current GitHub
sources: 19 canon-history IDs, 18 moderate scenario anchors, 5 fictional-
physics anchors, 1 social-scenario anchor, and 5 interpretation rules.

Timeline source hashes remain:

- CANON I: `98a83f50b68b68931ad24cfec97c347cc506901973d0e0787c09f2baa27cd3a6`
- Technology Timeline Register: `96c87881ca2f525b1de9fbfdb0aa3306c84dc0a76ae8c1c30ef4c972ae12f7eb`

## Solar ephemeris

The Phase-0→4 ephemeris foundation remains qualified.

Pinned local evidence/assets match GitHub:

- qualification evidence: `294890bc0ad5624d0bc2f0bf0ec850a7f19322093685adbb427c50c2dac9e56a`
- DE440: `a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5`
- Ceres supplementary SPK: `adb69cc0723550fad437b7466fedaf7480e2e36c489e9d2d727e783a78566137`

Using the governed Solar virtual environment with SpiceyPy 8.2.0, all 13
adapter/qualification tests passed. A fresh disposable PostgreSQL database
passed all 8 Solar migration/integration tests.

Important status distinction: live `loom_solar` contains the qualified
four-table schema but currently has zero rows in `body`, `body_identifier`,
`ephemeris_source`, and `ephemeris_coverage`. The qualified runtime path
therefore exists through pinned local SPICE assets and the governed adapter,
while PostgreSQL Solar identity/source/coverage persistence has not yet been
materialized. This is a persistence/materialization gap to close before
PostgreSQL is treated as the populated Solar metadata authority; it does not
invalidate the qualified ephemeris engine.

## Ceres retirement residual scan

In `loom_dev`:

- snapshot `ceres-v1-0231e5f7da744728ab5021268b6f239b`: absent;
- schemas `loom_ceres`, `loom_world`, `loom_civ`, `loom_media`: absent;
- all retained tables carrying a `snapshot_id` column: zero rows for the retired Ceres snapshot;
- Ceres-named retained relations: zero;
- Ceres-labelled retained `loom_control.source_artifact` records: zero.

Bare schemas `world`, `civstate`, and `media` still exist but contain zero
relations and zero routines. They are empty namespace archaeology, not Ceres
Atlas data.

Cluster-level auxiliary databases remain:

- `loom_solar_qualification`: contains empty Ceres-era schema/view structure,
  but zero underlying WORLD/CIV/MEDIA table rows and no retired Ceres snapshot;
- `loom_solar_official_centers_20260925`: only the default/public namespace,
  with no Ceres schema or objects.

These auxiliary databases are not the integrated `loom_dev` authority and
were not modified by this audit.

## GitHub consistency

PR #279 is merged. Its LOOM Gate workflow completed successfully. Migration
`011_retire_ceres_postgres` is present live with SHA-256
`36f36fbea8787f198677b20ef69bac8fdb4ab730ca0a3b7f7b7ea1080b347650`.

This audit also corrects two transcription errors in the retirement
qualification prose: CIV rows are 486 (not 484), and Earth biological-cohort
rows are 2,657,718 (not 2,657,315). The executable migration, committed Earth
preservation artifact, and live database already contained the correct values.

