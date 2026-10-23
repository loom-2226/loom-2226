# PR427 moon/giant price-unit correction: authoritative replacement experiment

**INVALID PREVIOUS RESULT:** The earlier `moon_price_merge_kt_20261023` 63-project result is invalid. The 21 completed moon/giant quotes were stored in `model_units` but read as USD, then divided by 1,000,000,000 again at `PortfolioCampaign._positive_a1_candidates` in `run_multi_project.py`. This understated their mission costs by exactly 1e9 and admitted projects on false commitments. Do not use the earlier 63-project count or its economic totals.

## Exactly which quotes were double-converted

- **42 rows**, 21 bodies × two source years (2026 and 2027), all rendezvous, from `PR427_COMPLETE_MOON_GIANT_RENDEZVOUS_REPORT_TEST_ONLY.json`.
- Bodies: ARIEL, CALLISTO, DIONE, ENCELADUS, EUROPA, GANYMEDE, IAPETUS, IO, MIMAS, MIRANDA, MOON, NEREID, OBERON, PHOEBE, PROTEUS, RHEA, TETHYS, TITAN, TITANIA, TRITON, UMBRIEL.
- Source field: `price_fields.model_units`, unit **model currency units** (1 model unit = USD 1,000,000,000).
- Erroneous second conversion: `PortfolioCampaign.__init__` extracted `model_units` into `main_quotes` as if it were USD; `PortfolioCampaign._positive_a1_candidates` divided that value by `scenario.price_inputs.usd_per_model_currency`.
- Correction: convert those 42 source values to the `lowest_price_usd` field with explicit `unit=USD`, retaining original model units in `original_price_model_units`; campaign then converts USD to model units exactly once.
- `double_conversion_rows.json` prints all 42 rows with body, source, field, units, conversion site and corrected USD.

## Mandatory mission-cost floor

- Authored fixed mission cost: USD 700,000,000 = 0.7 model units. No tolerance.
- Floor applied to **all priced rows in the saved 900-row matrix**, including flyby and other saved source years, not just the 2026 rendezvous case.
- Original merged file: **FAIL**, 249 of 667 priced rows below floor.
- Corrected merged file: **PASS**, 0 of 667 priced rows below floor.
- The 249 below-floor quotes were raised to 0.7 model units, and their original price fields preserved as `original_price_fields_before_floor`. This is an authored lower bound, not a new trajectory computation. See `floor_adjustments.json`.
- The floor check executes before any campaign state transition; violations raise `AssertionError`.

## Full-clock case

Treasury share 100%, material price x1, 4-sale cap, high buyer budget, rendezvous, 2026–2226, all 90 bodies and all sponsors.

| Measure | Corrected result |
|---|---:|
| Projects started | 57 |
| Sponsors ever started | 20 |
| Bodies ever started | 57 |
| Last start year | 2140 |
| Committed, min/project | 0.780 |
| Committed, median/project | 0.9463963262098969872 |
| Committed, max/project | 36.671951863741646 |
| Committed, sum | 124.2581766338780427472 |
| Gross returned | 9.12000 |
| Treasury refilled | 7.98000 |
| Sponsor budgets at zero | 0 |

`started_project_commitments.csv` lists all 57 starts and their actual commitment.

## Funnel by body

| Stage | Bodies |
|---|---:|
| Studied | 90 |
| Positive | 90 |
| Priced | 87 |
| Candidate | 87 |
| Started | 57 |

All 90 named body outcomes are in `body_funnel.json`; 30 priced candidates remain unstarted and 3 are unpriced (DACTYL, SELAM, HYPERION).

## Identity and controls

- Corrected merged price SHA-256: `fa17b1faa3c798eddd05c8c9fdb36990f0893af601d837c1d9c7279ff0534681`.
- Authored scenario SHA-256: `ffc3cb6517d77a810574191d4729e41e099ddcb12a3a7bd1afb77f2dfe2b96f5`.
- Run identity SHA-256: `c880a30965e76fcb4bf9d2300256487ec184081d35b5d7f1f91d01f819d6fc4f`.
- Route 1 control hash: `4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430` **PASS**.
- Ceres equivalence: **PASS**.
- Selector firewall: PASS.
- Database SHA-256 before: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- Database SHA-256 after: `e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde`.
- No edits to existing files. Draft PR #427 only.
