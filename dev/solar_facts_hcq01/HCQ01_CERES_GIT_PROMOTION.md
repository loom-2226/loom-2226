# HCQ-01 CERES — Git Promotion Record

This record documents promotion of the already-frozen HCQ-01 qualification
specimen into repository authority. It does not change the scientific
specimen, the frozen v0.2 contract, or the candidate authority boundary.

## Frozen invariant

- Qualification case: `HCQ-01_CERES`
- Schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.2`
- Empirical cutoff: `2025-12-31T23:59:59Z`
- Result: `QUALIFIED WITH LIMITATIONS`
- SQLite SHA-256: `91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d`
- Scientific facts: `CANDIDATE` only
- `preferred_fact`: empty

The freeze marker and final qualification record preserve freeze-time history,
including that the specimen was uncommitted and unpushed when frozen. This
promotion record is the separate Git-authority record.

## Promotion contents

The promoted subtree contains:

- the frozen SQLite qualification specimen;
- the typed ingestion harness, SQLite implementation, and hostile tests;
- final qualification, findings, freeze, manifest, and Round-1 failure-history records;
- the reproducibility input records and acquired source/product artifacts;
- immutable raw-artifact audit manifests with SHA-256 and byte counts.

Python caches, bytecode, editor files, temporary SQLite journal/WAL files,
credentials, and unrelated machine-local files are excluded. HTML source
artifacts are intentionally force-added despite the repository-wide HTML
ignore rule because they are preserved raw evidence and provenance inputs.

## Authority boundary

This promotion does not promote candidate facts to production authority,
modify PostgreSQL, Solar Phase-4 authority, CIVPROP, resource potential,
habitation potential, transport judgments, or preferred facts. HCQ-01 is a
hostile qualification specimen, not an exhaustive Ceres corpus.
