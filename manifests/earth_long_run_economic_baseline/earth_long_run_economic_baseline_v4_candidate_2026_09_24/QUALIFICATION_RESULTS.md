# Candidate qualification results

Decision: **HOLD**. The current pointer remains the immutable v3 baseline. This record describes the diagnostic v4 candidate and does not authorize promotion.

## Controlled arms

| 2226 measure | V3_CONTROL | SUCCESSOR_80 | A → B |
| --- | ---: | ---: | ---: |
| Population, original 80 | 6,572,523,389.641 | 6,572,523,389.641 | 0 |
| Value added, proxy units | 328,649,393,161,949.3 | 328,650,274,209,051.56 | +881,047,102.25 (+0.000268%) |
| Capital, proxy units | 1,124,064,437,105,335.4 | 1,124,067,440,593,771.9 | +3,003,488,436.5 |
| Investment, proxy units | 47,988,427,255,531.33 | 47,988,618,657,732.17 | +191,402,200.84 |
| Capital / VA | 3.420254108 | 3.420254078 | −0.000000030 |

The A → B difference isolates the 2026 accounting repair and its inherited-model propagation in the exact original 80-economy universe. `SUCCESSOR_FULL` economic propagation was not run because the 157 added WPP areas have no jointly qualified sector, asset, factor and trade/network model state. B → C and A → C are therefore unavailable, not zero. The 237-area identity and demographic envelope is separately complete. See `CONTROLLED_COMPARISON.json` for all four boundaries, country effects, ranks, concentration, sector and asset shares.

## Reconstruction and gates

Exactly one signed-accounting anomaly qualifies: TWN / ENERGY. Its negative OECD current-price VA remains a source observation. The modeled 2026 production state uses positive source PYP VA/GO proportions against positive modeled gross output, within-country redistribution, and source-backed asset proportions. Country VA, capital, investment, gross output and employment reconcile. `RECONSTRUCTION_TRACE.json` and `REDISTRIBUTION_PROVENANCE.json` identify the target, nine donor sectors and 40 affected asset cells. TWN / ENERGY remains positive across the 2026–2061 repair boundary and through 2226.

The 2026–2031 bridge and 2060–2226 forward annual qualification gates pass. The inherited 2031–2060 stage remains REVIEW: maximum annual sector-investment-share movement is 0.040093550275 (4.009355 percentage points), above its 3-point threshold. Its original v3 stage had the same approximately 4.0094-point issue. The threshold was not weakened. Independent candidate validation passes 480/4,800/19,200 country/sector/asset rows for 2026–2031, 2,400/24,000/96,000 for 2031–2060, and 13,360/133,600/534,400 for 2060–2226. It checks unique identity, demographics and labor bounds, nonnegative finite state, reconciliation, annual stock-flow, factor exponents, production equations, fallback method provenance and the repaired node.

## Tests and immutable authority

- Candidate focused tests: `python3 -m unittest -v manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24/test_successor.py` — 13 PASS.
- Current-baseline resolver tests, run from `manifests/earth_long_run_economic_baseline/earth_baseline_integration_2026_09_23`: `python3 -m unittest -v test_earth_baseline_resolver.py` — 5 PASS.
- V3 semantic tests: `python3 -m unittest -v manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/test_field_semantics.py` — 4 PASS.
- V3 mechanics tests, run from `manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23`: `python3 -m unittest -v test_long_run_repair.py` — 2 PASS, 1 preexisting optional smoke skip.
- Independent read-only candidate validator: `python3 manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24/validate_candidate.py --candidate-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24` — PASS.
- The active designation is `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23`. Its baseline manifest SHA-256 is `f8954955671c59bda3d4ce51b734589d77395a70ae556d9df277ae209f580fdb`. The pointer, 34 directly enumerated artifact records, the run manifest and 45 recursively enumerated run records passed byte-size and SHA-256 verification after the candidate run.

Fast/slow economic sensitivity awaits a qualified central successor. Demographic-only sensitivity and the full 2226 descriptive and outlier reports are complete. No active pointer or v3 artifact changed.
