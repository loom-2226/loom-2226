# M4-B Solar Resource Population Qualification

**Verdict: `M4_B_PASS_WITH_LIENS`**

This campaign populated a candidate empirical material-evidence layer and dispositioned all **380** required lanes across **95 eligible bodies**. It does not claim complete resource knowledge: **343 lanes remain `UNKNOWN_AFTER_SEARCH`**. Unknown, taxonomy, detection, measurement, sample-scale abundance, and modelled evidence remain distinct. No economic, accessibility, mining, or habitation judgment is present.

## Coverage and evidence

- 110 existing identity objects; 95 eligible natural/material bodies; 4 resource families per body. No new identity authority was created.
- 37 lanes are supported: 31 `SUPPORTED_PRESENT_UNQUANTIFIED`, 2 `SUPPORTED_QUANTIFIED`, and 4 `SUPPORTED_INFERRED_OR_MODELLED`; 343 are `UNKNOWN_AFTER_SEARCH`. No lane was `SOURCE_NOT_FOUND` or `NOT_APPLICABLE`.
- 43 candidate material rows comprise 7 inherited qualified rows and 36 campaign additions; 33 distinct recorded evidence lineages. Four inference/model lanes occur on bodies that also have direct evidence elsewhere, so there are zero bodies supported only by inference.
- The two numeric abundance assertions are approximate, sample-scoped modal mineral proportions; no global inventory, bounded abundance, recoverability, or economic value is inferred.
- 14 bodies have at least one direct material-evidence assertion. 81 bodies have all four lanes unknown; 83 have at least three unknown lanes.
- Physical inventory: 10 bodies have candidate mass; 39 have candidate size/shape plus bulk-density inputs; 46 remain without either route.

## Source and provenance

The campaign reviewed 25 source records, acquired 24, and recorded one failed publisher request (HTTP 403). It froze 25 artifacts totaling 8,113,565 bytes. Source families include NASA/NTRS and mission archives, JAXA/DARTS sample products, NASA-hosted primary analyses, and mission/planetary agency records. Assertions link to source, observation, region, explicit scope, epistemic class, and lineage; all 25 acquired artifacts have `source_artifact` provenance rows in the candidate. Acquired artifact URL, retrieval time, size and SHA-256 are in `M4B_RAW_ARTIFACT_MANIFEST.json`.

**Temporal and provenance liens:** some institutional mission-summary pages lack explicit publication/version dates; their linked empirical observations/products predate the cutoff, but artifact-page temporal metadata is incomplete. Source redistribution terms were not verified uniformly. Only the Bennu PNAS article reprint with CC BY 4.0 is retained in the repository; other acquired source bytes remain in the local research worktree and are not required for offline replay. Deterministic replay starts from the frozen extraction/crosswalk JSON and verified qualified databases.

## Validation and non-interference

- Hostile validator rejected unknown-to-zero, taxonomy-to-quantity, invalid range, missing quantified or bounded units, percent-over-100, economic-field, duplicate-key, and out-of-catalog identity fixtures. Structural audit verified body/observation/region coherence and no foreign-key or SQLite integrity errors.
- Surface, coma, sample, regional, drill-site, and spectral scopes remain attached to evidence. Nondetection was not synthesized from absent rows. No preferred fact was selected (total **0**).
- The inherited SF-PROMOTE-03 rows are an exact row subset of the candidate. Ceres, 67P and Europa body semantic digests are unchanged.
- Clean offline rebuilds are byte-identical; reversing source, assertion, region and observation insertion order preserves canonical source/region/observation/material semantics. Build time: 0.213s.
- Existing M4-A resource-contract tests and 8 M4-B tests pass.

## Candidate

`dev/solar_civprop_m4b/LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3`
SHA-256: `3e32c58703fc01ac5090ce36a06e24081fca9e30542bfb579344adeb244a1e60`
Whole semantic digest: `1b47133a1a5d6e58d3557e4efcfc5f678d5a1b7a343260709ca66b9776a8480e`

## Liens and integration readiness

The principal scientific limit is sparse empirical coverage, not an unaccounted lane. 46 eligible bodies also lack candidate mass/size-density support. A downstream integration prototype can consume this candidate only if it preserves unknown and sample/regional/model scope; the current evidence is **not** a complete physical/resource inventory for all 95 bodies.

Machine-readable verdict and checks: `M4B_QUALIFICATION_RESULT.json`, `M4B_HOSTILE_VALIDATION.json`, and `M4B_REPLAY_DETERMINISM.json`.
