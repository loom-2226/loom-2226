# HCQ-01 CERES — v0.3-R1 Repository Freeze Record

## Qualified state

- Qualification case: `HCQ-01_CERES`
- Current candidate schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.3-R1`
- Status: **QUALIFIED LOCALLY WITH LIMITATIONS**
- Independent hostile review: **PASS**
- Empirical cutoff: `2025-12-31T23:59:59Z`
- R1 SQLite SHA-256: `0bbbfd5ae2ab287900ff4e356f9571d21aff4593cc78e0cd69bf1610def9adc6`

## Preserved lineage

The repository preserves the actual qualification history:

1. HCQ-01 v0.2 — qualified with limitations.
2. v0.3 — lossless local migration.
3. Independent hostile review — found R1-A and R1-B.
4. v0.3-R1 — repaired endpoint/node semantic integrity and temporal syntax.
5. Independent hostile review — R1-A closed, R1-B closed, scientific preservation pass.

The v0.2 and v0.3 SQLite files remain separate immutable qualification
artifacts. R1 does not rewrite either earlier specimen.

## R1 qualification invariants

- `PRAGMA integrity_check = ok`.
- `PRAGMA foreign_key_check = []`.
- 8 facts, all `CANDIDATE`.
- `preferred_fact = 0`.
- Observation-scale populated count = 0.
- `fact_input = 2` and `knowledge_event = 4`.
- Thermal source `arXiv:2003.11045` remains `PREPRINT`.
- No scientific values, provenance, source classifications or Ceres observations changed.
- No Phase-4 authority, CIVPROP, resource, habitation, transport or preferred-fact state entered.

## Deferred limitations

The inherited raw-artifact relational linkage, complete knowledge/adoption
ontology, orientation uncertainty structure, and richer model-parameter
representation remain documented future limitations. Observational-scale
fields are intentionally unpopulated in this migration. These limitations do
not authorize new science or a schema redesign in this freeze.

This record establishes repository qualification status for the candidate
specimen. It does not promote Ceres facts to production `CURRENT` authority
and does not start the next empirical-enrichment phase.

Change class: `class:research`.
