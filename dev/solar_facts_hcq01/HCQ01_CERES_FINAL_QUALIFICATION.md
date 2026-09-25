# HCQ-01 CERES — Final Qualification / Freeze

## Result

**QUALIFIED WITH LIMITATIONS**

Qualification case: `HCQ-01 CERES`
Schema: `LOOM_SOLAR_FACTUAL_ENRICHMENT_DDL_v0.2`
Empirical cutoff: `2025-12-31T23:59:59Z`

This freezes the HCQ-01 qualification specimen only. It does not promote Ceres facts, select preferred facts, change production authority, or claim exhaustive Ceres coverage.

## Qualification history

`ROUND 1 — FAILED / NOT QUALIFIED` → Round-2 remediation → `ROUND 2 — QUALIFIED WITH LIMITATIONS` → independent direct review → thermal-source closeout → `HCQ-01 CERES — FROZEN`.

The Round-1 database/report are preserved in `round1_qualification_artifact/`.

## Thermal-source closeout

Before: the preserved `arXiv:2003.11045` artifact was classified `PEER_REVIEWED`.
After: it is classified `OTHER`.

Why: the preserved file is an arXiv preprint. Bibliographic evidence identifies a later Astronomical Journal publication, but that journal artifact is not the artifact preserved in this HCQ corpus. `OTHER` is the least misleading existing v0.2 source type. A future vocabulary may add `PREPRINT`.

Scientific values changed: **No**.
Source/provenance classification changed: **Yes**.
Downstream derivations changed: **No**.

## Final database

Database: `LOOM_SOLAR_HCQ01_CERES.sqlite3`
SHA-256: `91137126f635cd35e7ccde20cc41ed342dbd23dec7e7af304d9220318f1da26d`

`PRAGMA integrity_check`: `ok`
`PRAGMA foreign_key_check`: `[]`

## Row counts

| Table | Rows |
|---|---:|
| body | 1 |
| source | 16 |
| observation | 8 |
| body_region | 5 |
| fact | 8 |
| source_assertion | 8 |
| material_evidence | 6 |
| activity_fact | 2 |
| body_model_product | 9 |
| region_model_product | 3 |
| gravity_model | 1 |
| orientation_model | 1 |
| derived_quantity | 1 |
| derived_input | 1 |
| preferred_fact | 0 |

Sources represented: A=6, B=1, C=1, D=1, E=2, F=1, G=2, H=2.

## Verification

- 14 hostile/regression tests: **PASS**
- Corpus load: 16 PASS, 0 REVIEW, 0 REJECT
- Current run audit manifests: 16/16 complete
- Raw SHA-256 and byte-count verification: PASS
- Publication cutoff violations: 0
- Preferred facts: 0
- Scientific fact statuses: all `CANDIDATE`
- Evidence classes are frozen-v0.2 values only
- Confidence classes are frozen-v0.2 values only
- Assertion roles are frozen-v0.2 values only
- Regional cross-body violations: 0
- Model/region relationships: 3
- Provenance gaps: 0
- PSR area stored as water-ice extent: 0 rows
- Phase-4 ephemeris contamination: none
- CIVPROP/resource/habitation/transport contamination: none

Historical snapshots use publication/release as an earliest-public-availability lower bound, not as observation time: 2010 has 0 facts, 2016 has 1, and 2025 has 8. Retrieval in 2026 does not leak evidence into earlier snapshots.

The equivalent-spherical `VOLUME` retains structured lineage through `derived_input` to `MEAN_RADIUS`. Quarantining that input invalidates dependent derivation authority.

## Findings

- **DDL DESIGN PROBLEM:** no native raw-artifact/audit relation; external immutable artifacts and manifests are retained.
- **DDL DESIGN PROBLEM / REPRESENTATIONAL LIMITATION:** no complete knowledge-event timeline for observation, analysis, publication, adoption, revision, or controversy.
- **DDL DESIGN PROBLEM:** ordinary `DERIVED` fact lineage is prose-only, unlike `derived_quantity`/`derived_input`.
- **DDL DESIGN PROBLEM:** orientation uncertainty is held in source artifacts/notes rather than structured parameter fields.
- **DDL DESIGN PROBLEM / HARDENING REQUIREMENT:** semantic integrity protection is INSERT-safe; UPDATE-safe database-native protection remains future hardening.
- **VOCABULARY PROBLEM:** v0.2 has no `PREPRINT`; the preserved thermal preprint is represented as `OTHER`.
- **LEGITIMATE UNKNOWN:** unsupported abundances, complete coefficient/raster flattening, gravity reference epoch, and unsupported geotechnical scalars remain unknown.

All Round-1, Round-2, independent-review, and thermal closeout findings are preserved in `HCQ_FINDINGS.md`.

## Candidate v0.3 improvements

Artifact-manifest relation; knowledge-event/provenance-time model; structured derived-fact lineage; structured orientation uncertainty; explicit `PREPRINT` source type; UPDATE-safe semantic constraints.

## Boundaries

`preferred_fact = 0`; no Phase-4 authority contamination; no CIVPROP/resource/habitation/transport judgments; all loaded facts remain `CANDIDATE`. Nothing was committed or pushed.
