# HCQ-01 CERES — v0.3 Local Qualification

## Result

**QUALIFIED LOCALLY — LOSSLESS v0.2 → v0.3 MIGRATION**

This is a local schema-evolution qualification only. It does not promote
candidate facts, alter production authority, begin Phase-5 propagation, or
add Ceres science.

## Baseline

- Frozen v0.2: `LOOM_SOLAR_HCQ01_CERES.sqlite3`
- v0.2 SHA-256: `91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d`
- Inherited HCQ-01 status: `QUALIFIED WITH LIMITATIONS`
- v0.2 remained byte-identical after migration: **True**

## Migration

- Observation scale columns: six nullable fields added; existing values remain NULL.
- `fact_input`: typed fact/observation/model-product lineage with foreign keys,
  one-input-per-row constraints, body-consistency triggers, and UPDATE guards.
- `knowledge_event`: typed target foreign keys and event vocabulary
  `OBSERVED`, `PUBLISHED`, `RELEASED`, `REVISED`, `SUPERSEDED`, `RETRACTED`, `INGESTED`.
- `source_type`: `PREPRINT` added through a transactional source-table rebuild.
- Thermal source `arXiv:2003.11045` changed `OTHER → PREPRINT` as an
  authorized metadata-only correction; scientific values and citation identity
  are unchanged.
- Existing explicit observation start times produced 4
  `OBSERVED` events. Publication/release dates were not guessed into events.
- Two unambiguous `BULK_DENSITY` inputs were migrated: `MASS` and `MEAN_RADIUS`.
- Existing body/region and fact/observation guards were extended to UPDATEs.

## Preservation

Legacy table counts are preserved exactly. The field-level semantic comparison
reports `0` unexpected changes and one authorized
metadata change. Provenance fields and source assertions are unchanged.

| Table | v0.3 rows |
|---|---:|
| `activity_fact` | 2 |
| `body` | 1 |
| `body_model_product` | 9 |
| `body_region` | 5 |
| `derived_input` | 1 |
| `derived_quantity` | 1 |
| `fact` | 8 |
| `fact_input` | 2 |
| `fact_observation` | 2 |
| `gravity_model` | 1 |
| `knowledge_event` | 4 |
| `material_evidence` | 6 |
| `meta` | 10 |
| `observation` | 8 |
| `orientation_model` | 1 |
| `preferred_fact` | 0 |
| `property_definition` | 53 |
| `region_model_product` | 3 |
| `source` | 16 |
| `source_assertion` | 8 |

- Fact statuses: `{'CANDIDATE': 8}`
- Preferred facts: `0`
- Integrity: `ok`
- Foreign keys: `[]`
- Deterministic semantic rebuild: **True**
- Byte-identical independent rebuild: **True**

## Qualification tests

- Existing HCQ-01 tests: run separately; all preserved tests must pass.
- v0.3 migration/hostile tests: 9 tests pass.
- Covered: frozen SHA, lossless rows/values/provenance/statuses, NULL defaults,
  scale validation, typed lineage, invalid references, knowledge-event types,
  PREPRINT, legacy source types, cross-body INSERT and UPDATE guards, integrity,
  foreign keys, and deterministic rebuild.

## v0.3 artifact

- SQLite: `LOOM_SOLAR_HCQ01_CERES_v0_3.sqlite3`
- SHA-256: `310c35491e3768adcfc1607c4542603613d8d28ad00df883755537805037ed74`
- Schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3`
- DDL delta: `schema_v0_3.sql`
- Migration: `migration.py`
- Baseline manifest: `v0_3_baseline_manifest.json`
- Post-migration manifest: `v0_3_post_manifest.json`
- Semantic diff: `v0_3_semantic_diff.json`

## Findings

- **DDL DESIGN PROBLEM retained:** raw-artifact/audit linkage remains external to
  the frozen factual tables; this migration does not redesign it.
- **DDL DESIGN PROBLEM retained:** knowledge events add typed capability but do
  not model adoption, controversy resolution, or a complete event graph.
- **LEGITIMATE UNKNOWN:** observational-scale values were not invented for legacy
  observations; all six new fields remain NULL in migrated records.
- **LEGITIMATE UNKNOWN:** no model-parameter table was added; existing model
  products remain represented at their v0.2 metadata level.
- No new scientific observations, values, resource quantities, engineering
  judgments, economic judgments, CIVPROP state, preferred facts, or promotions
  were introduced.

## Explicit epistemic result

The migrated v0.3 database represents the same Ceres scientific knowledge as the
qualified v0.2 corpus, with improved observational-scale, structured-lineage,
knowledge-event, PREPRINT, and UPDATE-integrity capacity.
