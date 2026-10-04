# Phase 3A Earth Reference Recovery - Pass 7

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Scope:** GLOBAL 2026-2226 REFERENCE PROJECTION AND EXCEPTION CENSUS  
**Branch:** `offworld-mvp-phase3`

## 1. Purpose

Pass 7 expands the verification harness from the 2060/2061 transition to the complete 80-economy, 2026-2226 PostgreSQL Earth economic reference.

The governing question is no longer whether a representative country can be replayed. It is whether every PostgreSQL country-year row can be traced to the correct promoted temporal regime and whether exceptional model branches can be enumerated rather than discovered accidentally.

## 2. PostgreSQL population

`loom_earth.earth_economic_year` contains:

- 80 economies;
- years 2026 through 2226 inclusive;
- 16,080 country-year rows.

The derivation census is:

| derivation_id | rows |
|---|---:|
| V4_2026_2030 | 400 |
| V4_2031_2059 | 2,320 |
| V4_2060_2100 | 3,280 |
| BIOSYNTHETIC_2101_2226 | 10,080 |

This establishes a critical point: the current PostgreSQL Earth reference is **not simply v4 through 2226**. At 2101 the selected reference changes to the biosynthetic coupled successor.

## 3. Correct composite reference lineage

The exact current country-economic projection is reconstructed from four temporal components:

1. promoted v4 bridge, 2026-2030;
2. promoted v4 structural stage, 2031-2059;
3. promoted v4 successor, 2060-2100;
4. selected `MED_CENTRAL__SYNTH_CENTRAL` biosynthetic detailed replay, 2101-2226.

The 2031 and 2060 overlaps between adjacent v4 artifacts are exact for value added, investment, capital, gross output and population across all 80 economies.

At the 2100 handoff, v4 and the selected biosynthetic replay are exact for value added, investment and capital across all 80 economies.

## 4. Full PostgreSQL equality

A composite 16,080-row reference was built using the correct temporal lineage above and compared mechanically with PostgreSQL.

Results across **all 80 economies and all 201 years**:

| Field | Maximum absolute difference | Rows differing > 1e-6 |
|---|---:|---:|
| value_added | 0 | 0 |
| investment | 0 | 0 |
| capital | 0 | 0 |
| population | 0 | 0 |

For biosynthetic years, PostgreSQL `population` maps to `biological_population`, not recognized-person population or biological-plus-synthetic population.

For 2026-2100, gross output also matches exactly across all 6,000 applicable v4 country-year rows.

The detailed biosynthetic country replay used for 2101-2226 does not carry country gross output, so gross-output equality for that interval is **not established by this artifact comparison**.

## 5. Important failed first hypothesis

The first full-range comparison incorrectly stitched v4 successor rows through 2226 and produced 10,080 PostgreSQL mismatches beginning in 2101.

That was not a database defect. It exposed the actual selected-reference handoff to `BIOSYNTHETIC_2101_2226`.

The failed comparison is retained conceptually because it demonstrates why temporal derivation identity is mandatory. A consumer selecting rows only by `iso3, year` could silently compare or consume the wrong reference trajectory.

## 6. Global investment-ratio identity

For every artifact row where `investment_output_ratio` is defined, the identity

`investment_output_ratio = investment / value_added`

holds exactly in the tested artifacts.

No tolerance was required for the stored ratio identity.

## 7. Exception census: factor-share fallback

The v4 bridge records factor-share fallback for eight economies:

- ARE
- BGD
- BRN
- COD
- KHM
- MMR
- PAK
- VNM

These are persistent boundary/source exceptions and must be carried as provenance rather than treated as ordinary direct-source factor shares.

## 8. Exception census: post-WEO TFP anchor fallback

Ten economies use the target-economy median PWT11 RTFPNA growth fallback instead of a direct economy-specific PWT11 historical TFP-growth anchor:

- ARE
- BGD
- BLR
- BRN
- COD
- KHM
- MMR
- PAK
- STP
- VNM

The fallback method is `TARGET_ECONOMY_MEDIAN_PWT11_RTFPNA_GROWTH`.

This branch is present in the structural/post-WEO lineage and remains visible in the successor boundary metadata.

## 9. Exception census: replacement underfunding

Replacement underfunding is not rare over the long horizon.

Observed rows with `replacement_coverage_ratio < 1`:

- 2026-2031 bridge: 62 rows across 17 economies;
- 2031-2060 structural stage: 78 rows across 10 economies;
- 2060-2226 v4 successor artifact: 6,473 rows across 60 economies.

For successor years 2061-2226 alone, 6,469 rows across 60 economies are underfunded.

This means replacement underfunding is a major exercised state of the long-run model, not an edge case.

It must therefore be part of the Earth Reference Contract semantics. A low replacement-coverage ratio means modeled national investment is insufficient to fund the calculated replacement requirement under the allocation rule; it must not be silently coerced to full replacement.

## 10. Representative replay strategy

The exception census changes how worked examples should be selected.

Minimum replay classes now include:

1. clean/direct-source, fully funded control;
2. 2026 investment-source fallback case;
3. factor-share fallback case;
4. post-WEO TFP-anchor fallback case;
5. replacement-underfunded case;
6. Taiwan negative-source-VA/reconstruction lineage;
7. 2100/2101 biosynthetic handoff.

A single economy may exercise multiple classes, but coverage must be demonstrated by branch, not by geography.

## 11. 2100/2101 boundary

The current PostgreSQL derivation changes from `V4_2060_2100` to `BIOSYNTHETIC_2101_2226`.

The selected biosynthetic detailed replay contains 10,160 rows covering 80 economies for 2100-2226.

At 2100, its value added, investment and capital match the v4 successor exactly for all 80 economies. At 2101, PostgreSQL matches the biosynthetic replay exactly for value added, investment, capital and biological population.

This establishes continuity of the tested macro boundary while preserving the fact that the labor/population ontology changes.

## 12. PostgreSQL semantic warning

The column name `population` is temporally overloaded:

- through the v4 regime it represents the v4 demographic population reference;
- in the biosynthetic regime it maps to `biological_population`.

It does **not** represent `recognized_person_population` once synthetic persons exist.

Therefore a future typed Earth interface must not expose `population` without a population concept/type. The raw PostgreSQL name is insufficient for governed semantic consumption.

## 13. Current status

Now ESTABLISHED:

- exact row-domain equality: 80 economies x 201 years = 16,080 rows;
- exact current temporal derivation partition;
- exact PostgreSQL equality for value added, investment, capital and the correctly mapped population across the full 2026-2226 range;
- exact v4 gross-output equality through 2100;
- exact v4 handoffs at 2031 and 2060 for tested fields;
- exact tested macro handoff into the selected biosynthetic trajectory at 2100/2101;
- explicit factor-share fallback census;
- explicit post-WEO TFP fallback census;
- long-horizon replacement-underfunding census.

NOT YET ESTABLISHED:

- biosynthetic gross-output provenance/equality for 2101-2226;
- full sector/asset equality across every year rather than transition samples;
- complete source/imputation/fallback census below country level;
- monetary/price-basis consistency statement sufficient for MVP financial coupling;
- exact semantics of every PostgreSQL field outside the narrow MVP subset;
- complete formula-level independent replay of every exceptional branch.

## 14. Contract consequence

The narrow Earth Reference Contract cannot be a wrapper around `earth_economic_year`.

It must make temporal derivation and concept identity explicit. At minimum:

`EarthReferenceAssertion = (baseline_or_trajectory_id, derivation_id, field_concept, iso3, year, value_state, value, unit_basis, provenance, exception_flags, replay_status)`

Population requires a typed concept, such as `BIOLOGICAL_POPULATION`, rather than an unqualified generic `population`.

Investment requires derivation and exception flags because direct-source, fallback, structural and successor values have materially different epistemic histories even when they share a numeric column.

## 15. Next pass

Pass 8 should finish the narrow MVP-readiness decision rather than continue archaeology indefinitely:

1. verify sector/asset aggregation over the full selected trajectory where artifacts exist;
2. locate/verify biosynthetic gross-output provenance or explicitly exclude it from MVP;
3. resolve the monetary/price-basis statement for `value_added`, `investment` and `capital`;
4. classify every remaining lien as BLOCKING or NON-MVP;
5. draft the **Earth Reference Contract Candidate** for the fields actually required by Offworld MVP.

That is the point at which recovery should become a contract instead of a hobby practiced by people who have developed unusually strong feelings about NDJSON.
