# LOOM Earth 2026–2226 | independent read-only inspection

**REVIEW / NON-CANON / NON-RUNTIME / NO BASELINE CHANGE.** Extracted from the existing immutable-looking source files on quantifactus, without executing model code. This is a review snapshot, not a new authority. Repository base: main at `9e4b8c3806413259b925754b70f914fdd13e8504`.

## 1. Map and actual consumers

| Source | Actual coverage / authority | Consumer |
|---|---|---|
| v3 repaired (2026-09-23) | historical long-run model; its local full annual 2060–2226 files are inventoried | historical/rollback, not current pointer |
| v4 promoted (2026-09-24) | 80 qualified national economies, annual 2026–2226; separate 237-area demographic envelope | **Build 8 reads v4**, not the current successor |
| v4 qualified inputs | 2026–2031 (480 country rows) | Build 8 2026–2031 |
| v4 stage 2026–2031 | 2026–2031 | long-run model |
| v4 stage 2031–2060 | 2031–2060 | Build 8 2032–2035; model beyond |
| v4 successor 80 | 2060–2226 | historical promoted v4 trajectory |
| current coupled successor | 2101–2226 modeled authority, WPP demography through 2100 | current economic pointer; **not Build 8's v4 input** |

Authoritative pointers and reading paths:
- [current economic pointer](../../manifests/earth_long_run_economic_baseline/EARTH_LONG_RUN_ECONOMIC_BASELINE_CURRENT.json)
- [Earth baseline index](../../manifests/earth_long_run_economic_baseline/README.md)
- [v4 promotion decision](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24/BASELINE_DECISION.md)
- [Build 8 consumer](../../simulation/offworld_mvp/build8/README.md)
- [Build 8 checkpoint](../../simulation/offworld_mvp/build8/BUILD8_CHECKPOINT.md)
- [v3 provenance](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/PROVENANCE.md)

**Direct source quotations:** Build 8 README: “Economic tests need external Earth v4 data.” v4 promotion decision: “No 237-economy economic result is claimed.” v3 provenance: “Large annual sector/asset output and the complete checkpoint remain on quantifactus and are hash-pinned, not stored in Git.”

Build 8 source reader specifically selects `qualified_inputs/countries_2026_2031.ndjson` for 2026–2031, and `stage_2031_2060/countries_2031_2060.ndjson` for 2032–2035; the 2031 qualified-input row takes precedence. This is an observed code-path claim documented by Build 8, not an assertion that Build 8 has an activated qualified economic runtime.

## 2. Semantics, units, assumptions, fallbacks

**Read original wording, not an invented glossary:**
- [v3 full data dictionary](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/DATA_DICTIONARY.md)
- [v3 machine-readable semantics](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/FIELD_SEMANTICS.json)
- [v3 model equations and growth assumptions](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v3_repaired_2026_09_23/MODEL_SPEC.md)
- [v4 candidate delta / qualifying seed rule](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24/MODEL_SPEC.md)
- [v4 candidate dictionary delta](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_candidate_2026_09_24/DATA_DICTIONARY.md)
- [v4 promotion scope](../../manifests/earth_long_run_economic_baseline/earth_long_run_economic_baseline_v4_2026_09_24/PROMOTION_SCOPE.json)

The v4 candidate specification states that the **2026–2031, 2031–2060 and 2060–2226** forward algorithms remain those of v3, with a qualified 2026 sector-seed change. The promoted coupled successor introduces its own post-2100 authority. **Constant-dollar bases and per-field meanings must be taken from the linked original dictionary/semantics**; an inventory column name or JSON type is not a unit. Any field lacking a definition there is **undocumented**, not inferred from its name.

The raw sample includes original provenance/fallback fields such as `factor_share_fallback`, `factor_share_method`, `post_weo_tfp_anchor_fallback`, `demography_source`, `depreciation_source` and `macro_envelope_source`. `FALLBACK_EXAMPLES.ndjson` contains actual rows selected by a mechanical heuristic; inclusion is **not** proof that the fallback was exercised (some examples have missing WEO growth at 2026).

## 3. Actual data inventory and representative rows

- `TABLE_INVENTORY.json`: **every NDJSON table in the local v3 and v4 permanent baseline roots**, including stage, smoke, annual, and endpoint outputs. Actual line/row count, observed field names and JSON types, year min/max, number of observed ISO3 codes, source byte size and **computed SHA-256 of the original source file**. No source file was modified.
- `SAMPLE.ndjson`: actual records selected for USA, CHN, DEU, IND, ISL (small economy) and AGO (lower-income comparator), at requested years 2026, 2035, 2060, 2100, 2150, 2200, 2226 **where the particular table has that year**. Up to two rows per country-year per table; sector/asset tables are intentionally not exhaustive.
- `FALLBACK_EXAMPLES.ndjson`: up to three original rows per table meeting a mechanical fallback/missingness filter.
- `SUMMARY.txt`: concise inventory.

The inventory's `consumer` field says `Build 8` only for the two explicitly documented input tables; other file-to-experiment mappings are `undocumented`, not guessed. JSON field type is the observed type, not a formal SQL schema.

## 4. Known issues / interpretation limits

1. **Current pointer ≠ Build 8 input.** Current points to the lean biosynthetic coupled successor, Build 8 experiments load promoted v4 external data.
2. 80 qualified economies ≠ 237 areas with economic states. The other 157 areas have identity/demographic coverage only.
3. The historical v4 candidate, rejected candidate attempts, promoted v4 and coupled successor are different artifacts.
4. Some stage boundaries overlap at 2031 and 2060. Do not sum overlapping stages as independent years.
5. Build 8 capital mobilization experiments are not a calibrated forecast or an activated national capital market.
6. Missing, interpolated, authored, fallback and uncertain values are not automatically invalid. Their exact provenance requires inspecting the linked source documentation and corresponding raw row.
7. **Documentation/data semantic discrepancies:** not fully adjudicated. This extraction tests presence, row counts, observed types and hashes, **not** the model's physical/economic validity or whether every documented field definition matches every numerical record.
8. The selected post-2100 coupled successor is mapped from repository authority, but its own external files are **not** included in this v3/v4 NDJSON extraction. Its schema and table counts here are **undocumented**.

## 5. Scope, exclusions and size

Included: source links, authority map, direct quotations, all 39 local v3/v4 NDJSON table inventories, sampled original rows and fallback examples. Excluded: full annual files (hundreds of MB), binary/database contents, raw WPP/OECD/PWT inputs, secrets, credentials, full coupled-successor data, and any changes to baseline/code/canon. Exact package bytes can be obtained with `wc -c` on these five files. **No merge requested.**
