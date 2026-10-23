# PR427 completed moon/giant rendezvous price merge: single full-clock run

TEST_ONLY / NON-CANON. 90 bodies, 20 sponsors, 2026–2226, rendezvous, high buyer budget, treasury appropriation share 1, material price multiplier x1, four sales per project. New files only; earlier reports unchanged.

## Merged price evidence

- Source: `PR427_COMPLETE_MOON_GIANT_RENDEZVOUS_REPORT_TEST_ONLY.json` and earlier `general_project_rule_kt_20261022/price_provenance_audit.json`.
- 900 exact body × mission × source-year audit records (90 bodies, 2 mission types, 5 available source years: 2026, 2027, 2035, 2036, 2226). The source does not supply independent quotes for every intervening year.
- New completed moon/giant rendezvous rows take precedence in 2026 and 2027. Other source-year rows retain their existing provenance and status.
- `merged_price_rows.csv` prints body, mission type, year, source, status and selected price. `merged_prices.json` preserves complete source quote fields.
- Merged file SHA-256: `3fcaeb7031bb4233431dadafb01d36e88162bd1f75ce85a4728a72730579e380`.

**Unpriced in 2026:** DACTYL and SELAM (`PARENT_GM_MISSING`), HYPERION (`NO_59_BODY_TABLE_QUOTE`). Source classifications are preserved; no values invented.

## Single run results

| Measure | Result |
|---|---:|
| Projects started | 63 |
| Sponsors ever started | 20 |
| Bodies ever started | 63 |
| Last start year | 2061 |
| Total committed | 42.1260476757984537490566252 |
| Total gross returned | 10.08000 |
| Total refilled into sponsor budgets | 8.82000 |
| Zero-balance sponsors in 2226 | 0 |

No new starts after 2066, 2100 or in 2226. The remaining 24 quote-eligible bodies are still pending, not unpriced.

## Funnel by body

| Stage reached | Distinct bodies |
|---|---:|
| Studied (at least one positive A1 review) | 90 |
| Positive A1 review | 90 |
| Priced for 2026 rendezvous | 87 |
| Candidate | 87 |
| Started | 63 |

All 90 body-specific stages are in `body_funnel.json`. Terminal stages: 3 unpriced, 24 candidate-not-started, 63 started.

## 24 previously pending outer-body candidates

The table reports the saved 2026 V2 rendezvous geometry and model-unit prices. These are the 24 candidate bodies that remained unstarted in the earlier sweep and remain unstarted here. The 1,400-day trajectory limit was not changed. A quoted flight at 1,400 days does not prove that longer flight alone would make a project affordable.

| Body | Price (model units) | Flight days | Arrival braking (km/s) |
|---|---:|---:|---:|
| ARROKOTH | 9.02e+09 | 1400.00 | 52.13 |
| ATLAS3I | 1.88e+07 | 1400.00 | 13.10 |
| BORISOV | 1.97e+18 | 1272.75 | 60.79 |
| CHARON | 3.83e+07 | 1400.00 | 42.46 |
| CHIRON | 18.671 | 1387.00 | 20.27 |
| COMET_HALLEY | 3.69e+07 | 1400.00 | 42.37 |
| ERIS | 6.03e+34 | 1357.00 | 121.58 |
| GONGGONG | 2.31e+31 | 1392.50 | 111.45 |
| HAUMEA | 2.57e+13 | 1398.00 | 60.79 |
| HYDRA | 4.1e+07 | 1400.00 | 42.55 |
| IXION | 6.27e+08 | 1400.00 | 45.18 |
| KERBEROS | 4.08e+07 | 1400.00 | 42.55 |
| MAKEMAKE | 7.77e+15 | 1400.00 | 64.55 |
| MS4 | 5.96e+12 | 1286.75 | 60.80 |
| NIX | 4.05e+07 | 1400.00 | 42.53 |
| ORCUS | 6.77e+12 | 1342.50 | 61.19 |
| OUMUAMUA | 1.67e+21 | 1292.00 | 70.93 |
| PLUTO | 4.47e+07 | 1400.00 | 42.67 |
| QUAOAR | 4.33e+09 | 1400.00 | 51.79 |
| SALACIA | 1.94e+13 | 1279.75 | 60.80 |
| SEDNA | 1.78e+28 | 1400.00 | 101.79 |
| STYX | 4.02e+07 | 1400.00 | 42.53 |
| SWIFTTUTTLE | 4.23e+11 | 1384.50 | 52.93 |
| VARUNA | 1.13e+11 | 1400.00 | 53.78 |

The price column is the 2026 `RENDEZVOUS_V2_PRICES_TEST_ONLY.csv` model-unit quote, the same `rendezvous_v2_90` source selected by the earlier audit for these 24 bodies. These are modeled placeholder costs, not real-world mission prices.

## Controls and identity

- Route 1 control hash: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` (PASS).
- Ceres equivalence: PASS.
- Selection firewall: PASS.
- Case scenario SHA-256: `db6e8ddeab115878e77d43d915e84a7f0444f2c9a7df72f77f74754e2f49fcc3`.
- Run identity SHA-256: `4fd10d7156561e22006c52e8aca00373ca2b516762b5a5371c036b1d568ca05b`.
- DB before: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- DB after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- No pre-existing source file modified.
