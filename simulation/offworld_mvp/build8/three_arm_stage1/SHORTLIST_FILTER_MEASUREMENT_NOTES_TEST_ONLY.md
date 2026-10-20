# Shortlist and cheap-cost filter: controlled Arm A measurement

**TEST_ONLY / NON-CANON / NON-RUNTIME.** This is a measurement of a *counterfactual* cheap-cost filter applied to Arm A. The original Arm A has no such filter. No original code or inputs changed. No B, C, D runs performed.

## Source and interpretation

`run.py:95-105` computes radial distance `abs(|r_body|-|r_earth|)` at `year-01-01` and selects eight for `C_CHEAP_COST`; `B_VALUE_FIRST` instead ranks maximum sponsor evaluation score, eight. `A_EXHAUSTIVE` includes all eligible bodies. `run.py:108-116` only prices the selected arm members, so dropped candidates are **never priced within that arm**. `experiment.json` supplies `cheap_cost_count=8`, `shortlist_count=8` and the `cheap_cost_rule`. Radial proximity is not a mission price.

## Measurement contract

New-file runner `SHORTLIST_FILTER_MEASUREMENT_TEST_ONLY.py` reads the original 25-body validated table path, original 50-body-year checkpoint and original 100-pair CSV. It recomputes table geometry at every recorded departure, verifies its SHA against the original checkpoint, then reevaluates the two mission types. Mode 1 is original Arm A with filter OFF; mode 2 explicitly turns ON the C-style radial top-eight prefilter. The runner prints the complete authored toggle input, hashes it and incorporates source, table and reference hashes in the run identity. Both modes run sequentially in one process: peak RSS is process-resident and not an isolated cold-start memory benchmark. No simulations of B, C or D were executed.

**Note on machine-readable column naming:** the `filter_off` field in the new CSV/report is the *counterfactual FILTER_ON_CHEAP_COST_8 result*, as established by `interpretation`, `runs` and the runner; the name is an unfortunate label, not a third mode.

## Hashes

- Authored toggle SHA-256: `8d7cd1c4b7a04f9523dde5dcf7a622a0f12e101a9cab34a7714eef61599fadc7`

- Run identity SHA-256: `2d60edcb4b2a60bba6f9ca84b2cca82196fe8edea14485842a24f910528f33b9`

- Table manifest SHA-256: `848f0f9d3e75517448d6071c0397922e4ca0cfa410ffc75d7416853c84cba74a`

- Difference CSV SHA-256: `4a915337ea75aeb813363b9c7c35ec6c35299442cc4b0ea49870341de012e1e2`

- Every original table geometry hash was checked against the pinned original checkpoint, 1,537 in exhaustive mode and 656 in counterfactual filtered mode. Original 100-row pair CSV regression: **zero differences**.

## Measured time and memory

- `AS_AUTHORED_ARM_A`: 256.311174 seconds; peak RSS 291942400 bytes (278.42 MiB); 1537 geometry hashes; 50 body-years evaluated.

- `FILTER_ON_CHEAP_COST_8`: 99.155015 seconds; peak RSS 291942400 bytes (278.42 MiB); 656 geometry hashes; 16 body-years evaluated.

## Selected cheap-cost top eight

- 2026: BENNU, RYUGU, AMUN, EROS, VENUS, ITOKAWA, MARS, MERCURY

- 2027: DIDYMOS, ITOKAWA, AMUN, VENUS, BENNU, RYUGU, MERCURY, MARS

## Every changed body-year/mission

The CSV contains all **170 field-level differences**, including status, price, departure date and flight days, across **68** body-year/mission pairs. For the **34 priced pairs dropped**, the new price is *undefined*, not higher or lower: there is no defensible numeric price delta. The remaining **34** changed pairs were originally infeasible and become `NOT_EVALUATED_FILTERED`. **All retained pairs are identical in all four fields**. No filter-on priced candidate became cheaper or more expensive.

| Year | Body | Flyby originally | Rendezvous originally | Filtered result |

|---|---|---|---|---|

| 2026 | ASTEROID_6178 | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | CERES | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | CHIRON | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | COMET_67P | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | COMET_HALLEY | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | DIDYMOS | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | ERIS | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | EURYBATES | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | HAUMEA | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | HYGIEA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | KLEOPATRA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | MAKEMAKE | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | PALLAS | PRICED_TEST_ONLY | INFEASIBLE | Not evaluated |

| 2026 | PATROCLUS | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | PLUTO | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2026 | PSYCHE | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2026 | VESTA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | ASTEROID_6178 | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | CERES | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | CHIRON | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | COMET_67P | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | COMET_HALLEY | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | ERIS | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | EROS | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | EURYBATES | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | HAUMEA | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | HYGIEA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | KLEOPATRA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | MAKEMAKE | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | PALLAS | PRICED_TEST_ONLY | INFEASIBLE | Not evaluated |

| 2027 | PATROCLUS | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | PLUTO | INFEASIBLE | INFEASIBLE | Not evaluated |

| 2027 | PSYCHE | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

| 2027 | VESTA | PRICED_TEST_ONLY | PRICED_TEST_ONLY | Not evaluated |

## Conclusion

The filter reduces work by excluding 34 of 50 body-years, including 34 otherwise priced body-year/mission opportunities. It does **not** change the prices or best routes of the retained bodies. It is a search-effort governor, not a travel-cost model. All numerical values used were existing authored inputs; the only new experiment input is the explicit filter mode, printed and hashed.
