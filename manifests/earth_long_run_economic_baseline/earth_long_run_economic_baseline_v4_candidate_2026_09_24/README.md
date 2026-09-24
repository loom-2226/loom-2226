# Earth empirical baseline v4 candidate (2026-09-24)

**Class:** data. **Status:** candidate / non-canon / not promoted. **Base Git main:** `fbc3818648cd9cdf54629281f52b5eb928b4f877`. The governed current pointer remains v3. All monetary outputs are inherited constant-2015-USD-scale **model proxy units**, not physical capacity or literal 2226 purchasing-power USD.

This work tests a source-preserving 2026 production reconstruction and expands the Earth **identity and demographic** envelope. The 2026-2031 and 2031-2060 algorithms and the v3 2060-2226 numerical runner are reused by hash; candidate paths are injected without editing frozen v3. `CHANGE_IMPACT.md` gives the dependency and reuse decisions.

## Coverage and limits

The exact target identity rule is UN WPP 2024 Medium, year 2026, `LocTypeName=Country/Area`, nonempty ISO3, `TPopulation1Jan`. There are 237 unique areas and their Jan-1 population sums to the WPP World Jan-1 row. This is an **economy/area** universe, not a claim that all 237 are sovereign states. WPP's `Country/Area` field does not classify sovereignty or political status. HKG and TWN remain separate IDs because the source and existing economic model treat them separately. The 44 extra WDI envelope aggregate codes are excluded from the WPP area universe. No economy is excluded from the demographic envelope.

The inherited v3 economic model contains 80 IDs. The recovered WDI+WEO 2026 macro bridge covers 189 of the 237 WPP IDs on its own source basis; 48 lack that bridge. Among the 157 added areas, 109 have a bridged macro GDP, 145 have an ILOSTAT employment envelope, 105 appear in raw PWT 2019–2023, and 34 have each of seven relevant PWT fields somewhere in that interval. Raw presence is not joint economic qualification. All 157 lack **jointly qualified** ten-sector, four-asset, factor-share and bilateral-IO inputs for the inherited model. `COUNTRY_EVIDENCE.json` and `COVERAGE_REPORT.json` preserve each layer's evidence class and method. No fallback trade topology, sector split, capital stock or TFP is fabricated. Therefore `SUCCESSOR_FULL` economic propagation is **HOLD**. The 237-area demographic envelope is still available for later Atlas identity/demography work.

The WPP age source sums `PopTotal` percentages for age groups starting 15 through 60, giving ages 15-64. Population uses Jan 1, never July. The post-2100 central formula and its 40/30-year half-lives match v3 exactly. `FAST_DECAY` halves both half-lives and `SLOW_DECAY` doubles them as explicit sensitivity assumptions; neither changes the central input. `DEMOGRAPHIC_SENSITIVITY.json` carries 237-area 2226 populations, working-age shares, ranks and changes.

## Accounting repair and qualification

An active modeled sector qualifies only if signed current-price 2024 VA is nonpositive, current-price gross output is positive, PYP VA and gross output are positive, and 2026 modeled gross output and employment are positive while modeled VA is nonpositive. Across the original 80×10 modeled sector matrix, only TWN/ENERGY qualifies. The original signed −1,474.823 USD million observation stays in its immutable source. The 2026 modeled VA is reconstructed as `modeled_GO_2026 × (PYP_VA_2024 / PYP_GO_2024)`. Within-country sector VA, capital and investment are redistributed proportionally; existing asset-class capital proportions and country aggregates are preserved. Operative A is recalculated while the historical 2026 A source field is retained. `RECONSTRUCTION_TRACE.json` and `SEED_MANIFEST.json` pin the resulting isolated seed on quantifactus.

The repaired 2026–2031 bridge passes its inherited gate. The 2031–2060 stage keeps the node positive but remains **REVIEW**: its largest annual sector-investment-share move is 4.0282 percentage points, above the inherited 3-point gate. The original v3 2031–2060 stage already had the same review condition at 4.0094 points, recorded by its frozen 2060 manifest. No threshold has been loosened. The candidate 2061 forward smoke passes, but the upstream review gate remains visible. A completed 2226 forward run, if present, is a provisional diagnostic, not a promotion qualification.

## Reproduce without network

The compact reports and code are in this directory. Large candidate seed, annual rows and checkpoints are under `/home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24/` and will be hash-pinned. The commands below write only candidate paths; first generation requires an absent output root.

```bash
python3 build_coverage_demography.py
python3 build_2026_seed.py --output-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24
python3 run_pre2060.py --candidate-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24 --stage bridge
python3 run_pre2060.py --candidate-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24 --stage mid
python3 prepare_2060_candidate.py --candidate-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24
python3 run_successor_80.py --candidate-root /home/ubuntu/loom_earth_2026_2035/earth_empirical_baseline_v4_candidate_2026_09_24 --allow-review-input --end-year 2061
python3 -m unittest test_successor.py
```

The 2226 diagnostic uses `run_successor_80.py --end-year 2226 --output-name successor_80_2226` with the same root and review flag. `validate_candidate.py` and `analyze_candidate.py` independently audit it. The v3 pointer and files are never output targets.
