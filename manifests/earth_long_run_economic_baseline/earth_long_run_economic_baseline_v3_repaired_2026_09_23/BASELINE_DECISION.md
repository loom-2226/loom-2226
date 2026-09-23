# Earth long-run economic baseline v3 — repaired, 2026-09-23

**Decision:** designate `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23` as the current local Earth economic reference. **Class:** data / economic-model baseline promotion. **Status:** numerically qualified exploratory scenario, not a validated forecast, canon fact, or physical-capacity dataset.

The permanent quantifactus record is `/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23/`. Its `RUN_MANIFEST.json` pins the complete annual output and checkpoint outside Git. The Git record contains the actual model source, 2226 country endpoint, validation evidence, and `TRAJECTORY_SUMMARY.json` with every top-20 share at 2060, 2090, 2120, 2165, 2180, 2205 and 2226. The previous v2 designation and all its files remain unchanged as rollback history. Promotion did not rerun or tune the model.

## Why this model exists

V2 used corrected **WDI national GFCF/GDP** investment-rate provenance, yet held those national investment/VA rates effectively fixed through 2226 and retained high country-specific capital elasticities, capped at 0.60. Those structural long-horizon assumptions produced 2226 VA **581.741290 T**, capital **3,287.021024 T**, annual investment **155.436039 T/year** in inherited constant-2015-USD-scale model proxy units, and Nigeria at **17.5614%** of 80-economy VA. The earlier Nigeria **30.704% OECD ICIO fallback** was a distinct source-rate provenance defect; it had already been replaced by the WDI national GFCF/GDP architecture before v2. This v3 addresses the later structural extrapolation. Nigeria's share was a diagnostic result, never a calibration target.

The repaired run starts at the qualified 2060 country state, transitions operative factor shares toward 1/3, and transitions investment toward a 3.4 capital/VA equilibrium rule. It retains the qualified PWT-derived frontier-growth and decaying-catch-up TFP mechanism. It also reconstructs an active 2060 boundary for the one economically active sector whose non-positive accounting VA had become permanent zero production: TWN / ENERGY. Exact mechanics and limits are in `MODEL_SPEC.md` and `PROVENANCE.md`.

## 2226 result

The 80-economy result is **328.649393 T VA**, **1,124.064437 T productive capital**, **47.988427 T/year annual investment**, and **3.4203 capital/VA**. All monetary figures are model proxy units, not literal 2226 purchasing-power dollars.

| Rank | ISO3 | VA share | Rank | ISO3 | VA share |
|---:|:---:|---:|---:|:---:|---:|
| 1 | USA | 20.1906% | 11 | GBR | 1.7834% |
| 2 | IND | 15.2111% | 12 | EGY | 1.5040% |
| 3 | CHN | 14.3278% | 13 | DEU | 1.4929% |
| 4 | NGA | 7.5780% | 14 | KAZ | 1.4119% |
| 5 | IDN | 3.5969% | 15 | PHL | 1.3983% |
| 6 | PAK | 2.7778% | 16 | CAN | 1.3515% |
| 7 | RUS | 2.5235% | 17 | JPN | 1.2995% |
| 8 | AGO | 2.4963% | 18 | ISR | 1.2762% |
| 9 | AUS | 2.3552% | 19 | FRA | 1.0706% |
| 10 | ARE | 2.3155% | 20 | MYS | 1.0435% |

The complete top-20 trajectory is stored as numeric shares in `TRAJECTORY_SUMMARY.json` and displayed in `VALIDATION.md`.

The old pre-2060 Taiwan ENERGY model rows still contain the zero-production artifact. V3 reconstructs the **2060 boundary for forward simulation**; those earlier zeros are historical model artifacts, not observations. This promotion does not repair or replace that earlier history.
