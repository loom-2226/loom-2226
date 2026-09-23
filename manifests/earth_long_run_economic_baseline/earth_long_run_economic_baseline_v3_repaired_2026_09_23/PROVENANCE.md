# Source and artifact provenance

`RUN_MANIFEST.json` is the machine-readable authority for the **actual absolute path, byte size and SHA-256** of every frozen 2060 input, OECD source reducer, 2026 activity input, WPP/PWT/WDI input, runtime source file, complete annual trajectory, 2226 endpoint, checkpoint and validation log. Its permanent local path is `/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v3_repaired_2026_09_23/RUN_MANIFEST.json`. The small Git copies of code, the 2226 country endpoint, Taiwan repair record and trajectory summary are byte-identical to the pinned local files. Large annual sector/asset output and the complete checkpoint remain on quantifactus and are hash-pinned, not stored in Git.

`runner_executed.py` preserves the **exact runner bytes used for the numerical run**: its SHA-256 is `3ed3b926c36cca51165a42aa81739806aefb66ae58cb8eb3b1ea887e5c466a44`, identical to `runner_sha256` inside the completed 2226 checkpoint. After the run, only the inaccurate TFP descriptor string was changed in `runner.py` and the experimental NDJSON outputs. `runner_executed.py` was recovered by reversing that known single string substitution on the preserved source bytes and was accepted only after its hash matched the checkpoint. `long_run_repair.py` and all numerical code were unchanged. `RUN_MANIFEST.json` pins both runner variants and the corrected output bytes.

## Taiwan ENERGY causal chain and repair

The qualified 2024 OECD current-price observations for TWN / ENERGY are signed value added **−1,474.8229150813295 USD million** and gross output **65,382.8595 USD million**. Previous-year-price (PYP) value added is **4,792.9530 USD million** and PYP gross output is **52,908.1834 USD million**. The qualified 2026 model seed shows positive gross output **70,172,805,548.05833 proxy units** and positive employment **70,578.711**. Negative current-price accounting VA does not imply no production.

The old source-seed rule clamped the negative VA to zero, causing **zero VA → zero assigned capital → Cobb–Douglas A = 0 → permanent zero production**. The signed OECD source observation is retained unchanged. The repaired rule applies universally to a node only when current-price source VA is non-positive, current-price source gross output is positive, PYP VA and output are positive, the 2026 sector has positive gross output and employment, and the frozen 2060 sector has non-positive modeled VA. Across the complete 80 × 10 matrix, **TWN / ENERGY was the only qualifying node**.

For a qualifying node the implemented 2060 boundary rule is:

```text
VA_candidate_2026 = GO_sector_2026 * (PYP_VA_sector_2024 / PYP_GO_sector_2024)
VA_sector_2060 = VA_candidate_2026 * (country_VA_2060 / country_VA_2026)
GO_sector_2060 = VA_sector_2060 * (PYP_GO_sector_2024 / PYP_VA_sector_2024)
K_sector_2060 = VA_sector_2060 * (country_K_2060 / country_VA_2060)
employment_sector_2060 = (employment_sector_2026 / employment_country_2026)
                         * employment_country_2060
investment_sector_2060 = (VA_sector_2060 / VA_country_2060) * investment_country_2060
```

The other sectors surrender proportional shares of each aggregate, preserving the **qualified 2060 country VA, gross output, capital, employment and investment totals**. Existing asset composition proportions distribute the reconstructed sector capital/investment. Operative A is then calculated from the reconstructed modeled VA, capital, employment, country TFP and 2060 alpha. This is an explicit modeled reconstruction, not a corrected OECD VA observation, a Taiwan-specific magic number or a physical capacity estimate.

| State | VA | Gross output | Capital | Employment | Operative A |
|---|---:|---:|---:|---:|---:|
| Reconstructed 2060 | 8.737 B proxy | 96.442 B proxy | 34.050 B proxy | 38,738 | 1,078.538 |
| Modeled 2226 | 7.151 B proxy | 78.941 B proxy | 18.957 B proxy | 21,802 | 1,341.060 |

**ACCOUNTING STATE != PHYSICAL CAPACITY STATE.** None of these fields is an observed Taiwan energy-production capacity, GW, generation, fuel throughput or physical infrastructure measurement. The pre-2060 zero-production rows remain historical model artifacts and were not repaired in this promotion.

## Version lineage

The previous current designation, `EARTH_LONG_RUN_ECONOMIC_BASELINE_v2_2026_09_23`, remains at `/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v2_2026_09_23/`. Its manifest and outputs are untouched and hash-pinned by the new baseline manifest as rollback history. The earlier Nigeria 30.704% OECD-ICIO investment fallback defect was corrected to WDI national GFCF/GDP **before** v2; this v3 addresses later long-horizon structural extrapolation.
