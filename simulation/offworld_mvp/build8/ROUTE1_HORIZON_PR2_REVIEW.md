# Route 1 PR 2: Earth v4 annual horizon, 2026–2226

**class:research · EXPERIMENTAL · AUTHORED · TEST_ONLY · NON-CANON · opt-in / off by default.**

**Authority:** exact live main `79a10e1f70f4992ff83fdbd2e4768c707318839d`, PR #398 already merged. Build 8 only. No kernel, phase3b, Build 5, 6, 7, physical science, old fixture, Earth economic baseline, bank, credit or interest code touched. The 201-year continuation runs only when `run_cast_payments(end_year=2226)` is requested; original `run_cast_payments()` still ends in 2035 with its identical full kernel fingerprint. Plain Route 1 without the opt-in cast hook still refuses beyond 2035. No PR 3 body activities are added.

## Exact source ownership and 201-year validation

| Investment years in Route 1 | Exact Earth v4 source | Ownership / handoff |
|---|---|---|
| **2026–2031** (480 rows) | `qualified_inputs/countries_2026_2031.ndjson` | Qualified source owns **2031** |
| **2032–2060** (2,320 rows) | `stage_2031_2060/countries_2031_2060.ndjson` | Skip the stage-file 2031 overlap; it starts **2032** |
| **2061–2226** (13,280 rows) | `successor_80_2226/results/countries_2060_2226.ndjson` | Skip the successor-file 2060 overlap; successor starts **2061** |

Exact source SHA-256s, respectively:

- `8524ada09880514088d8293df84b0cd5c4eac30dcf8d694b72192c75096e9f7c`
- `449072d0c18ac09fc9346622d5917ef70efcb7913b5facbbd3517aa800e3e112`
- `ca9beba0ed8ed52b13c26691229eb5eee14f03065e60a528e614bc9a385daf15`

**80 modeled economies × 201 unique years = 16,080 selected country-year records**, exactly one numeric, finite, nonnegative modeled investment per (country, year), with an identical 80-country set. The reader fails closed for missing country-years, duplicates, invalid investments and malformed selected-year records, demonstrated by corrupting a disposable copy of the late successor file. No erroneous live source year or record was found. No extrapolation after 2226. **Investment capacity is not spendable cash**: the unchanged Build 8 mobilization and authored 25% share convert the capacity to the year's country allocation.

**Legacy compatibility correction:** An initial regression attempt exposed that the old Defense V2 trial imports the historical two-file `SOURCES` constant by name. Expanding that constant to three sources broke its pinned two-hash check. The final Build 8 reader preserves **the original two-file `SOURCES` export unchanged** and introduces a separate `SUCCESSOR_SOURCE` only for explicitly extended horizons. After that correction, **Defense V2 4/4 and new horizon 6/6 passed together**, without editing Defense V2 or the kernel. The uncorrected interrupted run is not counted as the final regression.

**2031/2032 handoff:** the stage input also contains 2031. In its shadow 2031 rows, 34 of 80 investment literals differ from the qualified 2031 value by tiny final-digit rounding amounts; all 80 qualified rows win. The actual aggregate modeled investment rises about **2.7069%** from qualified 2031 to stage 2032. No interpolation or averaging.

**2060/2061 handoff:** the successor file also includes 2060, exactly matching the stage 2060 investment for all 80 countries; stage owns 2060 and successor starts 2061. Aggregate modeled investment grows about **4.6686%** from 2060 to 2061, with notable individual modeled changes: **NGA −21.0011%**, **MMR −20.3983%**. These are source results, not input validation failures; no smoothing, inferred shocks or policy changes were introduced.

The 80-economy annual investment total peaks in **2071** (about **63.036 trillion** input currency units) and is about **47.989 trillion** in 2226. This is a model trajectory, not a validated future observation or spendable Route 1 bank balance.

## Four separate acceptance dimensions

| Dimension | Actual counted behavior |
|---|---|
| **Years** | **201 / 201** (2026–2226), continuously processed |
| **Sponsors** | **20 / 20 sponsor accounts** each year, **4,020 sponsor-year rows**; only the original twenty 2026 applications are financed in the default experiment |
| **Executors** | **16 / 16 eligible executor actors** listed for **each year**, **3,216 executor-year status rows**. Fifteen distinct vendors are paid in 2026 under the unchanged default quote table; one is eligible but not awarded. All sixteen were already demonstrated payable under the controlled PR #398 BUILD quote. |
| **Bodies** | **Not expanded**. Four existing 6C authored bodies stay isolated in their original tests. No 90-body campaigns or new study chains. |

**Idle years, plainly:** From **2027 through 2226 (200 years)** there are **zero new finance applications, disbursements, supplier contracts or execution outcomes** in this experimental path. Sponsors have already bought their one authored 2026 service; all later sponsor rows say `COMPLETE / NOT_EVALUATED / ALREADY_PURCHASED`. Every executor remains in the year's eligible cast but has `ELIGIBLE_NO_NEW_COMMISSION`, not fabricated paid work. This is precisely why PR 3 is needed to create body-linked activity demand. No bank or forced repeat sale masks this limitation.

**Country-envelope exception, unchanged from main:** the roster references 24 participating country codes, but only 23 are economically qualified in Earth v4. **QAT is not an 80-economy investment source**. Axiom continues to receive its existing allocations from the other participating modeled countries; the experiment does not invent a QAT cash account. There are **23 × 201 = 4,623** real Route 1 country-year origin accounts, all settled to zero.

## Protected original decade, side-by-side against actual main

A separate clean main-tree execution (same source tree as merge SHA `79a10e1`) produced and pinned the complete `ROUTE1_HORIZON_MAIN_79a10e1_BASELINE.json` fixture, including all 200 sponsor rows, all 20 delivery receipts, all 450 ledger transactions and the unchanged main-default kernel fingerprint.

| Comparison | `main 79a10e1` control | Extended 2226 run, restricted to ≤2035 | Result |
|---|---|---|---|
| Annual sponsor rows | **200** | **200** | **Exact object equality** |
| Row SHA-256 | `15fdc6b00df21d6b748a67a36fe9fbbca6d6fcb6156222ff1b5657eecca8b9cb` | Same | **MATCH** |
| Executor delivery receipts | **20** | **20** | **Exact object equality** |
| Receipt SHA-256 | `cbdbdb0810ba7fc1e020774b593aaad8f7ec42c2a7a902efa7c433d4a83d02f0` | Same | **MATCH** |
| Route 1 ledger transactions through 2035 | **450** | **450** | **Exact object equality**, including transaction IDs and parent references |
| Transaction SHA-256 | `f7e5ea74867d051e41bffab7f366bbfb5dd3e801fc4a9d324703eeed55fbea86` | Same | **MATCH** |

The old `run_cast_payments()` control is also rerun on the changed branch and retains its **full kernel fingerprint** `caff312f5b2dc4cea545788dedb0ca0d02b91265123d7ca5aa556b7c87a1876e`. The **extended** kernel has a different opening identity because it binds 191 additional years; comparing whole-kernel fingerprints across different horizons would be misleading. Compare decade rows, receipts and ledger, as above. The original NASA/CNSA pilot and 17 off-state golden snapshots are independently verified by the full inherited regression.

## 201 individual yearly money-conservation checks

For **each of 4,020 sponsor-year rows** in **each of all 201 years**, source transactions and actual closing cash are reconciled:

`closing(s,y) = previous_closing(s,y) + actual_country_allocations(s,y) − actual_disbursements(s,y)`

The equality is checked using `Decimal` with absolute tolerance `1e-24`, and the source transaction counts/amounts must agree with the annual row's opening, allocated, closing, funded status and quoted price. Every one of **4,623** actual country-year origin accounts ends at zero; unmodeled QAT contributes nothing. Within each year `sum(project disbursements) == sum(project-cash → executor CAPEX)`. All twenty project cash accounts end at zero; the final supplier balances equal all historical paid CAPEX. The kernel's own accounting invariants and replay also pass. No second money supply, bank or interest account is added.

| Calendar year | Actual financed work units | Total sponsor cash at year end, model currency |
|---|---:|---:|
| 2026 | 20 | 4.927514588513286705 |
| 2035 | 0 | 59.161346898903730875 |
| 2036 | 0 | 65.924666854300203083 |
| 2060 | 0 | 279.595069117807245271 |
| 2061 | 0 | 291.322642926940175884 |
| 2226 | 0 | 1662.403630540475413328 |

**An economically important limitation, not a conservation failure:** The last row retains ~**1,662.4 trial model-currency units** of unused sponsor cash, ~**28.1×** the 2035 ending balance. The reason is mechanical: positive modeled national allocations continue yearly while there are zero newly authored projects to spend them on. This is not a prediction of real-world hoarding or a reason to add loans. It will matter when deciding what PR 3 actually admits.

## Runtime and regression

One **isolated** `run_cast_payments(end_year=2226)` invocation on quantifactus with pinned Earth v4 present completed in **3.816908 seconds** (a separate run concurrent with regression took **6.698492 seconds**). These are observed local runtimes, not performance qualification. It produced **4,020 sponsor-year rows**, **3,216 executor-year rows**, **20 paid 2026 delivery receipts** and **8,281 Route 1 transactions**. A second independent 201-year replay yields identical annual rows, executor statuses, delivery receipts and kernel fingerprint. No kernel modification was required.

Exact **59-test combined command** from the repository root (53 inherited + six horizon tests):

```bash
PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python3 -m unittest -v simulation.offworld_mvp.build8.test_yearly_acceptance simulation.offworld_mvp.build8.test_screened_delivery simulation.offworld_mvp.build8.test_master_cast_snapshots tests.test_build6c_four_body_portfolio simulation.offworld_mvp.build8.test_route1_gate1 simulation.offworld_mvp.build8.test_route1_gate2 simulation.offworld_mvp.build8.test_capacity_options simulation.offworld_mvp.build8.test_route1_carry_cap simulation.offworld_mvp.build8.test_route1_carry_cap_extension simulation.offworld_mvp.build8.test_nasa_moon_a1 simulation.offworld_mvp.build8.test_nasa_moon_a2 simulation.offworld_mvp.build8.test_defense_v2_gate simulation.offworld_mvp.build8.test_followon_isolation simulation.offworld_mvp.build8.test_followon_trial simulation.offworld_mvp.build8.test_followon_four_body simulation.offworld_mvp.build8.test_route1_cast_payments simulation.offworld_mvp.build8.test_route1_horizon_pr2
```

The additional six tests cover completeness/hand-off sources, corrupt or missing successor records, 201×20 sponsor and 201×16 executor statuses, exact old-decade row/receipt/transaction/fingerprint equality, conservation in each 201 years and deterministic full replay. **VERIFIED after compatibility correction: 59/59 PASS, 0 failures, 0 skips, exit 0, 399.870 seconds, one sequential process. All 17 expected module counts matched exactly. The original 17 off-state golden snapshots and NASA/CNSA pilot tests passed unchanged.**

**Exact 17-module count audit from the corrected sequential log:**

| Module | Expected | Observed |
|---|---:|---:|
| `test_yearly_acceptance` | 1 | 1 |
| `test_screened_delivery` | 8 | 8 |
| `test_master_cast_snapshots` | 1 | 1 |
| `test_build6c_four_body_portfolio` | 8 | 8 |
| `test_route1_gate1` | 2 | 2 |
| `test_route1_gate2` | 1 | 1 |
| `test_capacity_options` | 3 | 3 |
| `test_route1_carry_cap` | 1 | 1 |
| `test_route1_carry_cap_extension` | 1 | 1 |
| `test_nasa_moon_a1` | 1 | 1 |
| `test_nasa_moon_a2` | 1 | 1 |
| `test_defense_v2_gate` | 4 | 4 |
| `test_followon_isolation` | 1 | 1 |
| `test_followon_trial` | 6 | 6 |
| `test_followon_four_body` | 8 | 8 |
| `test_route1_cast_payments` | 6 | 6 |
| `test_route1_horizon_pr2` | 6 | 6 |
| **Total** | **59** | **59** |

**GitHub CI limitation:** `loom-gate` and `LOOM Simulation Health (integrated)` do **NOT** execute this combined 59-test sequence or the new `test_route1_horizon_pr2.py`. Passing these workflows is not proof of 201 years, exact original-decade equality or every-year conservation. Those require the pinned external Earth v4 dataset on quantifactus.

**Out of scope and cut:** no 90-body generator, A2/A3 chain, 201-year vendor purchases, invented projects, physical delivery, trade, banking, loans, interest, pricing model, new country economy, future-year interpolation, scenario optimization, data promotion, persistence retrofit or kernel change. Existing off-state default behavior is unchanged. This PR is **DRAFT**; do not merge without separate user approval. Tell the user before changing anything after review.
