# Phase 3A Earth Reference Recovery - Pass 6

**Status:** PRE-CONTRACT / RECOVERY EVIDENCE / NO REPAIR  
**Scope:** GLOBAL 80-ECONOMY 2060->2061 TRANSITION  
**Branch:** `offworld-mvp-phase3`

## 1. Correction of verification strategy

Passes 3-5 used Australia as a clean worked specimen. Pass 6 changes the verification unit from one country to the complete economically qualified population.

The model claims an 80-economy economic reference. Qualification evidence therefore needs population-wide mechanical tests plus explicit exception census, not repeated proof that Australia continues to exist.

## 2. Promoted v4 artifacts tested

The promoted v4 local artifact set contains:

- `stage_2031_2060/countries_2060.ndjson`
- `stage_2031_2060/country_sectors_2060.ndjson`
- `stage_2031_2060/country_sector_assets_2060.ndjson`
- `smoke_2061/results/countries_2060_2061.ndjson`
- corresponding smoke sector/asset files
- `successor_80_2226/results/countries_2060_2226.ndjson`
- corresponding successor sector/asset files

The current PostgreSQL projection contains exactly 80 distinct economies and 160 country-year rows for 2060 and 2061.

## 3. Smoke versus selected successor

For all 80 economies in both 2060 and 2061, the v4 smoke output and the selected successor output were compared for:

- value added
- investment
- capital
- gross output
- population
- employment
- labor force
- demographic working-age population
- labor-market working-age population

Result:

**0 discrepancies. Maximum absolute difference = 0 for every tested field.**

Thus the 2061 smoke transition is exactly reproduced by the selected successor trajectory at the country level for the tested fields.

## 4. Selected successor versus PostgreSQL

All 160 country-year rows for 2060/2061 in the selected successor were compared with `loom_earth.earth_economic_year`.

Key sets are identical: 160 artifact rows = 160 PostgreSQL rows.

For every economy/year:

| Field | Maximum absolute difference | Rows differing > 1e-6 |
|---|---:|---:|
| value_added | 0 | 0 |
| investment | 0 | 0 |
| capital | 0 | 0 |
| gross_output | 0 | 0 |
| population | 0 | 0 |

Therefore the PostgreSQL country-economic projection is an exact projection of the selected v4 successor for the tested 2060/2061 fields.

## 5. Population-wide identities

For every one of the 80 economies at 2061:

`investment_output_ratio = investment / value_added`

Maximum absolute residual: **0**.

For every one of the 80 economies:

`real_value_added_growth = value_added_2061 / value_added_2060 - 1`

Maximum absolute residual: **0**.

These are exact stored identities for this transition.

## 6. Sector and asset reconciliation

The selected successor contains, for 2060 and 2061:

- 160 country rows
- 1,600 country-sector rows = 10 sectors per economy-year
- 6,400 country-sector-asset rows = 40 sector-assets per economy-year

Population-wide aggregation tests:

| Reconciliation | Maximum relative residual | Failures > 1e-10 |
|---|---:|---:|
| sector VA -> country VA | 2.88e-16 | 0 |
| sector investment -> country investment | 2.79e-16 | 0 |
| sector capital -> country capital | 3.22e-16 | 0 |
| asset investment -> country investment | 5.34e-16 | 0 |
| asset capital -> country capital | 8.89e-16 | 0 |

The tiny absolute residuals are floating-point summation effects. No reconciliation failure exists at the 1e-10 relative threshold.

## 7. Exception census: replacement underfunding

The global pass exposed an important branch that an Australia-only replay would miss.

At 2061, **6 of 80 economies** have `replacement_coverage_ratio < 1`:

| ISO3 | replacement coverage | I/Y |
|---|---:|---:|
| BGR | 0.9825468437044963 | 0.1997525132027305 |
| BRA | 0.9777818346664598 | 0.16693707926546236 |
| ITA | 0.9263323120005618 | 0.21265123010285283 |
| MMR | 0.9419903563227181 | 0.22442312343997445 |
| SAU | 0.8582073537739409 | 0.29504781047023954 |
| TWN | 0.937764888171671 | 0.22299828700627974 |

This means national investment is insufficient to fund modeled asset replacement fully in those six cases under the successor's allocation rules.

This is not automatically a defect. It is a distinct model branch requiring explicit semantic documentation and targeted replay.

It also validates the move away from Australia-only verification: Australia follows the fully funded branch and therefore cannot test this behavior.

## 8. Cross-sectional investment-rate range

At 2061 the modeled investment/output ratios span at least:

- low: STP = 0.09253892951395808
- AGO = 0.11315893003112991
- EGY = 0.12125514498518504
- high: KHM = 0.30667100981693607
- IND = 0.31682926839263986
- CHN = 0.3918494401956739

The successor is therefore materially heterogeneous across economies. A single-country replay cannot establish global behavior.

## 9. Global transition status

The following are now **ESTABLISHED for all 80 economies at 2060/2061**:

1. selected successor country rows match the v4 smoke transition exactly for tested fields;
2. PostgreSQL matches the selected successor exactly for the country-economic fields it projects;
3. I/Y stored identity holds exactly;
4. year-over-year VA-growth identity holds exactly;
5. sector VA, investment and capital aggregate to country totals within floating-point tolerance;
6. asset investment and capital aggregate to country totals within floating-point tolerance;
7. replacement underfunding is an exercised branch in six economies, not a theoretical code path.

## 10. What is not yet established

This pass does **not** claim an independent recomputation of every 2061 primitive from source observations.

Still open:

- exact formula-level replay of the successor's national investment-rate transition for all 80;
- exact TFP/frontier/catch-up replay for all 80;
- targeted replay of the six replacement-underfunded economies;
- fallback/exception census across all temporal regimes, not only 2061;
- full 2026-2226 PostgreSQL/artifact equality, rather than the 2060/2061 transition;
- long-run monetary/price-basis contract.

## 11. Revised qualification strategy

Phase 3A shall use three layers:

### A. Population-wide mechanical verification

Run invariant, aggregation, projection and boundary checks across all applicable economies and years.

### B. Exception census

Enumerate every economy/year invoking fallback, imputation, reconstruction, underfunding, stale-source treatment, or exceptional branch.

### C. Targeted worked replays

Use representative rows selected because they exercise distinct model branches:

- clean/direct-source control;
- historical investment fallback;
- negative-VA/reconstruction case;
- replacement-underfunded case;
- other branches as discovered.

Country selection is evidentiary, not geographic.

## 12. Next pass

Expand the mechanical harness across the full promoted 2026-2226 Earth economic trajectory and produce:

1. full PostgreSQL-to-promoted-artifact equality report;
2. transition-boundary checks at 2026/27, 2031/32, 2060/61 and 2100/01;
3. global fallback/exception census;
4. candidate list of the minimum representative worked replays needed for the Earth Reference Contract.

That is the appropriate evidence base for freezing a global reference interface.
