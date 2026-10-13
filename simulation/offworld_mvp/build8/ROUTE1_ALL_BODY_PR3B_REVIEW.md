# PR 3B — All 90 eligible bodies in one conserved 201-year Route 1 world

**EXPERIMENTAL / TEST_ONLY / NON-CANON / OPT-IN; OFF BY DEFAULT.** DRAFT review, not a claim about physical missions, recovered materials, 2226 propulsion, or empirical resource probabilities.

**Exact baseline:** GitHub main `cff4ad2f8a9bf70cbe81a995a88ea116db5423c5`, the merged PR #400 head. No Build 5, 6, 6C, 6E, 7, kernel, phase3b, protocol, SQLite, frozen inputs, bank, interest, loan, or main-branch edits.

## Acceptance: the 45-body checkpoint first, then all 90

| Observable | 45-body checkpoint | Full 90-body run |
|---|---:|---:|
| Eligible bodies | **45/45** (includes four authored) | **90/90** |
| Body/year states | **9,045/9,045** | **18,090/18,090** |
| Sponsor/year rows | **4,020** (20 × 201) | **4,020** |
| Executor/year roster statuses | **3,216** (16 × 201) | **3,216** |
| Years | **201/201** | **201/201** |
| New supplier-paid TEST_ONLY study stages | **119** | **249** |
| New paid A1 attempts | **74** | **159** |
| Funded A2s | **45** | **90** |
| Body claims at end of run | **45** | **90** |
| Recorded financing blockers | **0** | **0** |
| Actual elapsed entire Route 1 run | **9.690447 s** | **16.001066 s** |

The 45 checkpoint includes all four previously authored bodies plus the first 41 other eligible body IDs in sorted table order. It is an explicit test scenario, **not** a 45-body global cap in the full 90-body campaign.

All 90 eventually receive A1 and A2 services at the current abstract TEST_ONLY unit prices. The original 86 non-historical bodies retain seeded A1 first draws. The 39 initial insufficient generated bodies reopen and **69 additional paid A1 attempts** eventually produce admitted positive synthetic reviews. Zero blocks means the measured sponsor money and current study quotations permit all 249 attempts. It does **not** establish physical spacecraft fundability or realistic costs.

**Actual participation:** all **20/20** sponsors receive at least one new paid study (9–16 paid study stages each). All **16/16** executor identities remain eligible and visible for each of 201 years, while **15 of 16** receive new TEST_ONLY study payments; **Isar Aerospace** receives none. There is no artificial requirement to pay every vendor. The final new stage is funded in **2042**; from 2043 through 2226, the run still records every yearly body and economic state but has no newly authored stage after A2. Accumulating cash later is expected with the real-mission-cost lane parked.

## Four authored bodies: standing, provenance and timing

**These four use the existing Build 6C authored TEST_ONLY result standings; they do not use a generated SHA256 draw.** A1 is paid in 2036, A1 review becomes effective in 2037, A2 is separately paid in 2037, and the authored A2 result/review enters in 2038.

| Body | 2037 A1 review | 2038 A2 result | A1/A2 source |
|---|---|---|---|
| Bennu | SUPPORTS_ADVANCE | INSUFFICIENT | BENNU-A1-RESOURCE / BENNU-A2-CONCEPT |
| Ceres | SUPPORTS_ADVANCE | SUPPORTS_ADVANCE | CERES-A1-SURFACE / CERES-A2-ASSESS |
| Mars | SUPPORTS_ADVANCE | INSUFFICIENT | MARS-A1-REMOTE / MARS-A2-SURFACE |
| Moon | SUPPORTS_ADVANCE | INSUFFICIENT | MOON-A1-SURFACE / MOON-A2-ASSESS |

Original Build 6C studies were authored for specific 2026–2041 timing, costs, maturity and windows. **They are not physically executed or replayed in 2036.** Only their *authored TEST_ONLY result standings and stage identities* inform new Build 8 abstract analytical services. Old histories remain separate provenance and retain their exact old fingerprints, pilot tests and frozen bytes. No retroactive financing is inserted in 2026–2035.

Source authority: `simulation/offworld_mvp/build6/inputs/BUILD6C_2026_2041_PORTFOLIO_SCENARIO_V0_1.json`, read only. An authored outcome here does **not** demonstrate empirical material abundance or a spacecraft trip.

## Body admission and seven missing trajectories

Eligible population is derived from pinned `simulation/offworld_mvp/build6e/inputs/SOLAR_HIDDEN_WORLD_WATER_PRIOR_TABLE_v0.1.csv` using existing `load_inputs()` and only its `material_model_applicability` metadata (not generated hidden WORLD deposit truth).

| Input class | Count | Treatment |
|---|---:|---|
| SOLID | 87 | eligible |
| SOLID_WITH_ATMOSPHERE | 3 | eligible |
| HOMEWORLD_REFERENCE | 1 | exclude Earth |
| NO_SOLID_SURFACE | 4 | exclude four giant planets |
| **Total** | **95** | **90 admitted** |

Read-only Build 7 accessibility reference provides 83 `DERIVABLE` and seven `UNKNOWN` statuses. The seven bodies **DACTYL, HYDRA, KERBEROS, NIX, PROTEUS, SELAM, STYX** participate in all 201 years and can receive abstract studies; each of their 201 annual state rows retains **ACCESS_UNKNOWN**. No trajectory, mission cost, transfer or surface landing is fabricated. DERIVABLE is not itself route qualification.

**201-year body states:** each eligible body receives one annual status in every year 2026–2226, including a `HISTORICAL_BASELINE_UNCHANGED` placeholder for pre-2036 years. From 2036, statuses identify available/unfunded, funded-awaiting-review, reopened, A2-ready, A2-awaiting-review and completed. This is body participation, not 90 physical missions.

## Reopening, payment identity and limit register

Existing PR 3A single-stage body key was insufficient to preserve repeated A1 histories. PR 3B keeps the shared Route 1 accounts and financier process, adds paid attempt numbers to the audit and report, and records separate observations, results, actual disbursements, project-cash supplier payments and unique parent transaction references. A previous insufficient or failed A1 never disappears from history.

| Named effective setting | Effective PR 3B value |
|---|---|
| `CAMPAIGN_START_YEAR` / `CAMPAIGN_END_YEAR` | 2036 / 2226 |
| `BODY_SELECTION_ORDER` | Sorted eligible Build 6E IDs (90) |
| `SPONSOR_CLAIM_ORDER` | Original 20 cast-actor IDs |
| `SPONSOR_ALLOCATION_ORDER` | REPEATED_CAST_ID_ROUNDS |
| `MAX_NEW_STAGES_PER_SPONSOR_YEAR` | **None / DISABLED**, Sol's previous artificial cap removed |
| `MAX_ACTIVE_CLAIMANTS_PER_BODY` | 1 |
| `A1_REOPEN_ON` | INSUFFICIENT, NO_RESULT |
| `A1_REOPEN_AT` | Next yearly decision after review |
| `A1_RETRY_LIMIT` | None |
| `A1_RETRY_DRAW_KEY` | Named seed + body + A1 + paid attempt number |
| `A1_POSITIVE_REVIEW_FRACTION` | 0.50 TEST_ONLY (generated bodies only) |
| `A1_RESULT_SOURCE` | Authored 6C standings OR generated seeded result, separately recorded |
| `STUDY_DURATION_YEARS` | 1 TEST_ONLY |
| `A1_SERVICE_CATEGORY/PRICE` | RUN, 0.015 TEST_ONLY |
| `A2_SERVICE_CATEGORY/PRICE` | BUILD, 0.015 TEST_ONLY |
| `MAX_AUTHORED_STAGE` | A2; no A3 |
| `SPONSOR_REQUEST_CEILINGS_ENABLED` | True; existing per-sponsor nominal ceilings preserved |
| `GLOBAL_PROJECT_CAP` / `EXECUTOR_CAPACITY_CAP` | None / None |
| `LIFETIME_SPENDING_CAP` / `CARRY_CAP` | None / None |
| `ACCESS_UNKNOWN_TREATMENT` | Abstract studies allowed; no trajectory authority |
| `CHECKPOINT_BODY_COUNT` | 45 test variant only, full run uses 90 |

Existing financier policy/hurdle/concentration, original TEST_ONLY resource belief and prior, comparable executor quote availability, real sponsor cash, and disclosed sponsor-held evidence remain in the `campaign.limits` register. No hidden sponsor or executor throttles were added. Sponsor-specific existing ceiling values are inherited without modification. The 16 executor capabilities are all represented in every year; payment is awarded only to the eligible supplier selected by the existing quote mechanism, not forced to every executor.

**Blocker accounting:** every attempted non-funded request has one ordered primary named blocker and preserved original financier reason, and every calendar reporting period satisfies `attempted = funded + named primary blockers`. Full 90-body run: **249 = 249 + 0**. A separate focused negative case removes comparable RUN quotes for one requested study and proves **1 = 0 + 1 COMPARABLE_EXECUTOR_QUOTE**, with zero money disbursed. `NO_CANDIDATE` is not counted as a rejected request. Existing PR 3A named historic caps remain visible only in its untouched original scenario.

### Full per-limit primary-blocker matrix (all 20 financing periods)

These are **measured zeros**, not missing data. The opt-in run finances all 249 actual requests. The isolated negative-quote test demonstrates one nonzero named block without spending money. There is **no attempted A2** on a weak A1: the body is explicitly reopened for a separately paid A1 retry.

| Period | `MAX_CLAIMANTS_PER_BODY_CAMPAIGN` | `A1_REVIEW_NOT_READY` | `A1_REVIEW_INSUFFICIENT` | `COMPARABLE_EXECUTOR_QUOTE` | `EXECUTOR_CAPABILITY` | `SPONSOR_REQUEST_CEILINGS` | `ACTUAL_SPONSOR_CASH` | `FINANCIER_CONCENTRATION` | `FINANCIER_INFORMATION` | `FINANCIER_RETURN` | `FINANCIER_OTHER` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2036-2045 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2046-2055 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2056-2065 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2066-2075 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2076-2085 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2086-2095 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2096-2105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2106-2115 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2116-2125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2126-2135 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2136-2145 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2146-2155 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2156-2165 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2166-2175 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2176-2185 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2186-2195 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2196-2205 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2206-2215 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2216-2225 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2226-2226 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

## Actual financing, supplier payments and historical protection

The full 90-body execution produces **8,779 actual money-ledger transactions**. Every 2026–2226 year is checked against actual transfers:

`closing = previous sponsor cash + originating country investment allocations − sponsor disbursements`.

Actual annual `DISBURSE` equals supplier `CAPEX`. The corresponding new supplier payment has the real disbursement as its parent and each project-cash account is emptied after payment. All 23 country-source accounts settle to zero each year (**4,623 origin/year accounts**); kernel invariants pass. No bank, interest, loan, fictitious receipt of returned capital or printed funds.

- Original 2026 Build 8 service spending: **0.350 model currency** (unchanged).
- 249 newly purchased, TEST_ONLY abstract body-stage services: **249 × 0.015 = 3.735 model currency**.
- Combined paid services: **4.085 model currency**.
- Full 2226 aggregate sponsor cash: **1658.668630540475413328499999** model currency, 3.735 less than the base PR 2 horizon without new body work.

**Protected first decade:** exact equality against pinned main for 2026–2035 **200 sponsor-year rows, 20 original supplier receipts and 450 transaction objects including parent lineage**. These are checked in the PR 3B acceptance test in addition to all inherited PR 3A assertions. **17 off-state protected snapshots, NASA/CNSA pilot, frozen 6C four-body history and default kernel fingerprints** must all pass the exact full sequential suite.

**Receipt re-scan eliminated in PR 3B:** Sponsor/year study expenditure is incrementally recorded from actual paid receipts for that year, not computed by re-scanning the full historical receipt list each year. This is the only performance refinement required for the observed workload.

## Wall-clock performance against approximately four-second PR 3A baseline

**Isolated 201-year run:** 45 bodies **9.690447 s**, all 90 bodies **16.001066 s** (~4× PR 3A two-body baseline, not 16 seconds per decade). Measured on quantifactus; TEST_ONLY workload.

Annual durations below come from instrumented Build 8 yearly callbacks and include Route 1 work within that yearly interval. Their sum is less than the full wall time because the total also includes common input setup, pre-loop preparation and result assembly. Neither measurement is a guarantee of future speed.

| Time period | Measured 90-body elapsed seconds |
|---|---:|
| 2026-2035 | 2.899234 |
| 2036-2045 | 11.970549 |
| 2046-2055 | 0.031939 |
| 2056-2065 | 0.032619 |
| 2066-2075 | 0.034478 |
| 2076-2085 | 0.039625 |
| 2086-2095 | 0.037066 |
| 2096-2105 | 0.040776 |
| 2106-2115 | 0.047177 |
| 2116-2125 | 0.042098 |
| 2126-2135 | 0.044231 |
| 2136-2145 | 0.075169 |
| 2146-2155 | 0.045075 |
| 2156-2165 | 0.042932 |
| 2166-2175 | 0.040620 |
| 2176-2185 | 0.044502 |
| 2186-2195 | 0.039362 |
| 2196-2205 | 0.040179 |
| 2206-2215 | 0.041478 |
| 2216-2225 | 0.048259 |
| 2226-2226 | 0.004286 |

The concentrated high-cost interval is **2036–2045: 11.970549 seconds**; after the A1 retry and A2 work is finished, later periods remain below ~0.08 seconds each in this run. No arbitrary runtime cutoff has been introduced.

### Actual request counts per financing decade

One bucket begins each ten years from 2036, with a single-year 2226 final bucket. Every blocker family not displayed in the table is explicitly **zero** in this full run; the structured `campaign.decades` output stores the named counts.

| Financing period | Attempted | Funded | Named blockers |
|---|---:|---:|---:|
| 2036-2045 | 249 | 249 | 0 |
| 2046-2055 | 0 | 0 | 0 |
| 2056-2065 | 0 | 0 | 0 |
| 2066-2075 | 0 | 0 | 0 |
| 2076-2085 | 0 | 0 | 0 |
| 2086-2095 | 0 | 0 | 0 |
| 2096-2105 | 0 | 0 | 0 |
| 2106-2115 | 0 | 0 | 0 |
| 2116-2125 | 0 | 0 | 0 |
| 2126-2135 | 0 | 0 | 0 |
| 2136-2145 | 0 | 0 | 0 |
| 2146-2155 | 0 | 0 | 0 |
| 2156-2165 | 0 | 0 | 0 |
| 2166-2175 | 0 | 0 | 0 |
| 2176-2185 | 0 | 0 | 0 |
| 2186-2195 | 0 | 0 | 0 |
| 2196-2205 | 0 | 0 | 0 |
| 2206-2215 | 0 | 0 | 0 |
| 2216-2225 | 0 | 0 | 0 |
| 2226-2226 | 0 | 0 | 0 |

## Exact sequential regression and module counts

All **19 modules** execute in **one** sequential Python unittest process. The 67 inherited Build 8/6C qualification tests remain intact; PR 3B adds **10** acceptance tests. The full command:

```bash
PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python3 -m unittest -v \
  simulation.offworld_mvp.build8.test_yearly_acceptance \
  simulation.offworld_mvp.build8.test_screened_delivery \
  simulation.offworld_mvp.build8.test_master_cast_snapshots \
  tests.test_build6c_four_body_portfolio \
  simulation.offworld_mvp.build8.test_route1_gate1 \
  simulation.offworld_mvp.build8.test_route1_gate2 \
  simulation.offworld_mvp.build8.test_capacity_options \
  simulation.offworld_mvp.build8.test_route1_carry_cap \
  simulation.offworld_mvp.build8.test_route1_carry_cap_extension \
  simulation.offworld_mvp.build8.test_nasa_moon_a1 \
  simulation.offworld_mvp.build8.test_nasa_moon_a2 \
  simulation.offworld_mvp.build8.test_defense_v2_gate \
  simulation.offworld_mvp.build8.test_followon_isolation \
  simulation.offworld_mvp.build8.test_followon_trial \
  simulation.offworld_mvp.build8.test_followon_four_body \
  simulation.offworld_mvp.build8.test_route1_cast_payments \
  simulation.offworld_mvp.build8.test_route1_horizon_pr2 \
  simulation.offworld_mvp.build8.test_route1_body_campaign_pr3a \
  simulation.offworld_mvp.build8.test_route1_all_body_campaign_pr3b
```

| Module | Expected tests | Observed |
|---|---:|---:|
| `simulation.offworld_mvp.build8.test_yearly_acceptance` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_screened_delivery` | 8 | 8 |
| `simulation.offworld_mvp.build8.test_master_cast_snapshots` | 1 | 1 |
| `tests.test_build6c_four_body_portfolio` | 8 | 8 |
| `simulation.offworld_mvp.build8.test_route1_gate1` | 2 | 2 |
| `simulation.offworld_mvp.build8.test_route1_gate2` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_capacity_options` | 3 | 3 |
| `simulation.offworld_mvp.build8.test_route1_carry_cap` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_route1_carry_cap_extension` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_nasa_moon_a1` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_nasa_moon_a2` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_defense_v2_gate` | 4 | 4 |
| `simulation.offworld_mvp.build8.test_followon_isolation` | 1 | 1 |
| `simulation.offworld_mvp.build8.test_followon_trial` | 6 | 6 |
| `simulation.offworld_mvp.build8.test_followon_four_body` | 8 | 8 |
| `simulation.offworld_mvp.build8.test_route1_cast_payments` | 6 | 6 |
| `simulation.offworld_mvp.build8.test_route1_horizon_pr2` | 6 | 6 |
| `simulation.offworld_mvp.build8.test_route1_body_campaign_pr3a` | 8 | 8 |
| `simulation.offworld_mvp.build8.test_route1_all_body_campaign_pr3b` | 10 | 10 |
| **TOTAL** | **77** | **77** |

**PASS: 77/77 tests across 19/19 exact module counts in 503.286 seconds, 0 failures, 0 skips.** A green Gate or Integrated Health workflow does not substitute for this manual command or the separately measured 45/90 checkpoints.

**CI limitations:** GitHub LOOM Gate and Integrated Simulation Health do not run `test_route1_all_body_campaign_pr3b.py`, the exact 77-test sequence, the isolated 45/90 benchmarks, 18,090 body-year state check, seeded retry-history audit, per-decade runtime, complete 201-year budget/23-origin reconciliation, or external pinned Earth v4 input verification. CI may check narrower repository invariants only.

**Actual omissions:** no genuine transport, no new trajectories for seven unknown bodies, no real mission costing, no sponsor target preferences, no investment bank, no wealth interest, no A3, no activation of further stage types after A2, no hidden topology coupling, no kernel or frozen path changes, and no claim that all 16 eligible executors must receive contracts. The 2036+ four-body standings are authored scenario values, **not executed native 6C activities**.

**DRAFT ONLY.** Wait for explicit kT approval before merge. Tell the user before editing this reviewed draft, and do not start a later PR without approval.
