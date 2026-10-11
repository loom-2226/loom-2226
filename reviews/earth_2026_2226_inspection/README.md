# LOOM Earth 2026–2226: read-only inspection map (incomplete)

**Review-only. No baseline promotion, runtime change, qualification or merge.**
Source: live repository main, inspected 2026-10-11. This is an evidence map, **not yet the complete requested inspection package**. Missing table rows, schema inventories, and hashes are deliberately not invented.

## Authority and consumer map

| Component | Source or version | Coverage | Evidence |
|---|---|---|---|
| Current economic pointer | `EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24` | modeled successor 2101–2226; WPP empirical demography through 2100 | [pointer](../../manifests/earth_long_run_economic_baseline/EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json) |
| Previous promoted economic baseline | `EARTH_LONG_RUN_ECONOMIC_BASELINE_v4_2026_09_24` | 80 economically qualified economies, annual 2026–2226; separate 237-area demographic envelope | [decision](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24/BASELINE_DECISION.md) |
| Earlier repaired baseline | `EARTH_LONG_RUN_ECONOMIC_BASELINE_v3_REPAIRED_2026_09_23` | long-run through 2226; exact per-table spans not verified in this inspection | [README](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/README.md) |
| Build 8 country-capital input | **Earth v4 external files, not the current successor pointer** | 2026–2035 initial reader; later experiments require separate verification | [Build 8 README](../../simulation/offworld_mvp/build8/README.md) |

**Build 8 exact source statement:** “Economic tests need external Earth v4 data.” See linked Build 8 README. Its historical first increment names `qualified_inputs/countries_2026_2031.ndjson` for 2026–2031 and `stage_2031_2060/countries_2031_2060.ndjson` for 2032–2035; 2031 overlap resolves to qualified inputs. The README explicitly distinguishes these historical increments from current experimental status.

## Source-document route (retain original wording)

- [v3 data dictionary](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/DATA_DICTIONARY.md)
- [v3 field semantics](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/FIELD_SEMANTICS.json)
- [v3 model specification](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/MODEL_SPEC.md)
- [v3 provenance](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/PROVENANCE.md)
- [v4 candidate model specification](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24/MODEL_SPEC.md)
- [v4 promotion decision](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24/BASELINE_DECISION.md)
- [current baseline overview](../../manifests/earth_long_run_economic_baseline/README.md)
- [Build 8 consumer README](../../simulation/offworld_mvp/build8/README.md)

These links are source documents, not rewritten descriptions. The original data dictionary and semantic JSON should be read directly for units, constant-dollar basis, missing-value semantics and field definitions.

## Staging and projection

The v4 candidate specification explicitly states the unchanged v3 forward-model stages as **2026–2031, 2031–2060 and 2060–2226**, with a changed qualifying 2026 sector seed. Growth equations, exact fallback rules, and their application by table: **not independently verified in this package**; consult linked source specifications. The selected successor has a separate modeled 2101–2226 segment.

## Table inventory and sample

**Not included yet:** actual table-level row counts, column types, file SHA-256, complete consumer mapping, and sampled CSV/NDJSON records. Large annual trajectories are retained externally on quantifactus and pinned by manifests; they cannot be reconstructed safely from Git metadata. No values were synthesized. The requested USA/CHN/DEU/IND/small/low-income country × seven-year sample and fallback rows require direct read-only access to those pinned files.

## Known review hazards

1. Current governed pointer **is not** the Build 8 Earth-v4 file input.
2. 80 modeled economies **does not mean** 237 qualified national economies.
3. The v4 candidate is distinct from promoted v4; rejected attempts are not baseline evidence.
4. Build 8 is experimental and non-canon, not a validated capital market or long-run forecast.
5. GitHub manifests do not substitute for inspecting external annual data files.
6. Documentation/data disagreement audit: **undocumented until external files are inspected**.

## Package scope

Included: this small navigation and evidence-gap README only. Excluded: all source-data copies, generated tables, code changes, secrets, credentials, large files, and speculative semantics. This branch changes no existing file. The review remains **incomplete** until an external read-only extraction is attached.
