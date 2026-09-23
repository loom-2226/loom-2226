# Validation and frozen result

The actual original `full_2226` run completed through **2226** in **528.6 seconds** as reported by its runner console and recorded in `RUN_MANIFEST.json`. Its `trajectory_report.json` says `QUALIFIED_CAUSAL_TECH_BLIND_EARTH_2060_2226_PROVISIONAL`, `passed: true`, and `annual_gate_failures: []`. This is a numerical qualification of the implemented scenario, not empirical validation of the 2226 future.

The preserved `focused_tests.log` shows **3 tests passed**. The preserved `independent_validation.log` checks **13,360 country rows**, **133,600 sector rows** and **534,400 asset rows** and reports PASS for country–sector reconciliation, sector–asset reconciliation, every annual asset stock-flow identity, the operative production equation, alpha plus effective labor exponent equal to one, historical 2026 A immutability, and positive TWN / ENERGY VA, gross output, capital and operative A in every 2060–2226 year. No listed test failed. The raw TFP descriptor was corrected to `FRONTIER_GROWTH_TRANSITION_DECAYING_CATCHUP` after the run by a string-only replacement; **no numerical TFP value or model output was changed**.

All monetary results below are **inherited constant-2015-USD-scale model proxy units**. They are not literal 2226 purchasing-power dollars or physical-capacity observations.

| 2226 aggregate | Repaired v3 | Previous v2 |
|---|---:|---:|
| 80-economy VA | 328.649393 T | 581.741290 T |
| Productive capital | 1,124.064437 T | 3,287.021024 T |
| Annual investment | 47.988427 T/year | 155.436039 T/year |
| Capital / VA | 3.4203 | — |

The changes reflect the universal factor-share and investment transitions together with the active-sector boundary repair. This run contains no Nigeria-specific treatment, country outcome cap, ranking target or 2226 Atlas calibration. It does not isolate a numerical contribution for each change.

## Four-country VA-share paths

| ISO3 | 2060 | 2090 | 2120 | 2165 | 2180 | 2205 | 2226 |
|:---:|---:|---:|---:|---:|---:|---:|---:|
| NGA | 1.7380% | 4.1681% | 5.7546% | 6.9204% | 7.1491% | 7.4222% | 7.5780% |
| CHN | 27.2419% | 25.0251% | 20.7054% | 16.4230% | 15.6307% | 14.7668% | 14.3278% |
| IND | 10.2004% | 14.3961% | 14.9010% | 15.0447% | 15.0857% | 15.1549% | 15.2111% |
| USA | 19.8740% | 18.0788% | 18.9976% | 20.0335% | 20.1530% | 20.2112% | 20.1906% |

## Complete top-20 VA-share trajectory

The table below is generated from the preserved `TRAJECTORY_SUMMARY.json`, which was independently calculated from all 80 country rows at each year. Rows retain 2226 rank order.

| 2226 rank | ISO3 | 2060 | 2090 | 2120 | 2165 | 2180 | 2205 | 2226 |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | USA | 19.8740% | 18.0788% | 18.9976% | 20.0335% | 20.1530% | 20.2112% | 20.1906% |
| 2 | IND | 10.2004% | 14.3961% | 14.9010% | 15.0447% | 15.0857% | 15.1549% | 15.2111% |
| 3 | CHN | 27.2419% | 25.0251% | 20.7054% | 16.4230% | 15.6307% | 14.7668% | 14.3278% |
| 4 | NGA | 1.7380% | 4.1681% | 5.7546% | 6.9204% | 7.1491% | 7.4222% | 7.5780% |
| 5 | IDN | 2.6757% | 3.5099% | 3.5851% | 3.5720% | 3.5747% | 3.5856% | 3.5969% |
| 6 | PAK | 0.7652% | 1.4783% | 2.0403% | 2.5497% | 2.6395% | 2.7333% | 2.7778% |
| 7 | RUS | 1.4708% | 1.8270% | 2.1322% | 2.3924% | 2.4404% | 2.4945% | 2.5235% |
| 8 | AGO | 0.1731% | 0.6219% | 1.1872% | 1.9250% | 2.1104% | 2.3505% | 2.4963% |
| 9 | AUS | 1.7100% | 1.7845% | 2.0000% | 2.2331% | 2.2783% | 2.3290% | 2.3552% |
| 10 | ARE | 0.8527% | 1.1502% | 1.5799% | 2.0418% | 2.1375% | 2.2513% | 2.3155% |
| 11 | GBR | 2.4501% | 1.9495% | 1.8670% | 1.8304% | 1.8179% | 1.7980% | 1.7834% |
| 12 | EGY | 0.8337% | 1.1833% | 1.3844% | 1.4956% | 1.5052% | 1.5078% | 1.5040% |
| 13 | DEU | 2.2911% | 1.7104% | 1.5992% | 1.5407% | 1.5263% | 1.5063% | 1.4929% |
| 14 | KAZ | 0.4673% | 0.8542% | 1.1059% | 1.3151% | 1.3521% | 1.3919% | 1.4119% |
| 15 | PHL | 1.1466% | 1.5064% | 1.4934% | 1.4373% | 1.4243% | 1.4079% | 1.3983% |
| 16 | CAN | 1.4445% | 1.2004% | 1.2412% | 1.3155% | 1.3296% | 1.3445% | 1.3515% |
| 17 | JPN | 2.4792% | 1.6841% | 1.4901% | 1.3594% | 1.3366% | 1.3121% | 1.2995% |
| 18 | ISR | 0.6086% | 0.8061% | 0.9984% | 1.1822% | 1.2171% | 1.2560% | 1.2762% |
| 19 | FRA | 1.7474% | 1.2587% | 1.1642% | 1.1091% | 1.0971% | 1.0812% | 1.0706% |
| 20 | MYS | 0.7039% | 0.8701% | 0.9639% | 1.0276% | 1.0358% | 1.0420% | 1.0435% |
