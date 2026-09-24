# Earth lean biosynthetic coupled successor v0

**Designation:** `EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_CANDIDATE_2026_09_24`
**Status:** research candidate, non-canon, non-production, not promoted
**Authority boundary:** `loom-2226/loom-2226@817103d9d8640b6400047a1d02fd479633e8323d`

The bounded v0.1 sensitivity and allocation-repair successor is documented in
[`v0_1/README.md`](v0_1/README.md). The v0 files and results below remain frozen
as the named comparison case.

This candidate replaces the endpoint-only post-2100 bridge with a small causal
chain: WPP 2024 age/sex evidence at 2100, annual five-year biological cohorts,
medical-access mortality effects, health-sensitive biological labor, a separate
synthetic-person stock and labor path, separate non-person machine tasks, and the
existing qualified v4 economic machinery through 2226.

The result is an experiment. It does not change current Earth authority, canon,
the v4 economic files, or the selected 2226 demographic bridge.

## Result

The independently validated 2226 endpoint is:

- biological population: **6,991,125,306**;
- synthetic-person population: **9,791,858**;
- total recognized persons: **7,000,917,164**;
- approximate biological median age: **47.42**;
- biological effective labor: **1,448,652,898**;
- synthetic-person effective labor: **11,015,840**;
- non-person machine task capacity: **57,857,611**;
- total effective labor: **1,517,526,349**;
- qualified 80-economy value added proxy: **236.154 trillion**.

All three labor components are stored independently. Machine tasks never enter a
person count. Synthetic persons never enter biological cohorts.

## Scope and limits

Demography covers all 237 WPP Country/Area identities. Economics remains the
qualified v4 set of 80 economies. Global migration is zero after 2100 because no
qualified country migration model is available. The WPP open `100+` boundary is
placed in `100–104` at 2100; modeled survival subsequently populates older bins.

Mortality and medical adoption coefficients are transparent setting assumptions.
They are not fitted to the promoted 8.3125 billion endpoint. Synthetic stock and
machine-task coefficients are likewise exploratory and untuned. The strong
country concentration of synthetic labor and automation is surfaced in the
outlier report and requires sensitivity work before any promotion proposal.

## Reproduction

Commands and input paths are recorded in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).
Large annual trajectories remain in the local quantifactus package at
`/home/ubuntu/loom_earth_lean_biosynthetic_v0_20260924` and are individually
hash-pinned by `results/CANDIDATE_MANIFEST.json`. Compact annual summaries and
2226 endpoints are checked in under `results/`.

## Review files

- `MODEL_SPEC.md`: causal model and boundary handling.
- `MEDICAL_LONGEVITY_ASSUMPTIONS.md`: exact mortality and access assumptions.
- `SYNTHETIC_PERSON_ASSUMPTIONS.md`: stock and labor assumptions.
- `LABOR_COMPOSITION_REPORT.md`: labor interface and category separation.
- `CONSISTENCY_REPORT.md`: tests and hostile gates.
- `OUTLIER_REVIEW.md`: material findings and second-pass needs.
- `results/COMPARISON_CURRENT_V4_TO_CANDIDATE.json`: promoted versus candidate.
- `results/SOURCE_PROVENANCE.json`: sources and hashes.
- `results/CANDIDATE_MANIFEST.json`: generated artifact hashes.
