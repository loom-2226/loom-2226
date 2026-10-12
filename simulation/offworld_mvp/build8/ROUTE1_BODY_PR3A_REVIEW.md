# PR 3A: Connected two-body Route 1 campaign — DRAFT review pack

**Authority:** live `main` at `eb7d33ce940e0ccfd0c59f3b89db5d93ff17ee0c`. **EXPERIMENTAL / TEST_ONLY / NON-CANON / opt-in; OFF by default.**

## What is and is not simulated

The opt-in `run_body_campaign()` runs **201/201 years (2026–2226)** with the existing **20 sponsors** and **16 eligible executors** in the same Route 1 money ledger: **4,020 sponsor-year rows**, **3,216 executor-year eligibility/status rows**, and **8,287 financial transactions**. Two bodies are newly authored: **EUROPA** and **PHOBOS**. All other bodies, including the four previously authored Moon/Mars/Ceres/Bennu activity histories, are untouched. **No second generated activity chain exists for Moon, Mars, Ceres or Bennu.** No PR 3B activation, no new bank/loans/interest, no kernel, phase3b, Build 5, Build 6, Build 7 or frozen-file changes.

| Year | Sponsor | Body | Work and paid executor | TEST_ONLY cost | Result |
|---|---|---|---|---:|---|
| 2036 | Australian Space Agency | Europa | A1 RUN, Toyota | .015 | DELIVERED |
| 2036 | Axiom | Phobos | A1 RUN, Thales Alenia Space | .015 | DELIVERED |
| 2037 | Axiom | Phobos | A2 BUILD, Thales Alenia Space | .015 | DELIVERED |

Study duration is **one TEST_ONLY year**. In 2037, Europa A1 produces **INSUFFICIENT / HOLD**, and Phobos A1 produces **SUPPORTS_ADVANCE / ADVANCE**. The A1 study result and separate review are explicit kernel audit events; a delivered A1 also creates a sponsor-held **TEST_ONLY** observation. It is not empirical evidence or a hidden-truth revelation. A paid supplier failure produces **NO_RESULT / HOLD** and no observation. These payments purchase abstract RUN and BUILD study services, **not physical spacecraft missions, navigated trajectories, or physical landing/return capabilities**.

An approved A2 requires a prior positive A1 result and review. No A3 exists. After the 2037 follow-on, there is no new two-body study demand: **189 campaign years have zero attempted requests**, even while national capital allocations continue.

**Measured single isolated `run_body_campaign()` wall time:** approximately 4–5 seconds on quantifactus; not a performance qualification. **The exact 67-test suite is separately measured below.**

## Named effective limit register

Every potentially limiting number for this campaign is a named TEST_ONLY setting, or an already-named existing financier-policy parameter exposed here; no hidden additional governor.

| Name | Exact effective value | Effect / standing |
|---|---|---|
| `CAMPAIGN_START_YEAR` | 2036 | TEST_ONLY; protects all 2026–2035 history |
| `CAMPAIGN_END_YEAR` | 2226 | Matched to qualified Earth v4 |
| `MAX_NEW_STAGES_PER_SPONSOR_YEAR` | 1 | **SOL-PROPOSED TEST_ONLY**, not requested or justified by kT |
| `MAX_CLAIMANTS_PER_BODY_CAMPAIGN` | 1 | Avoids duplicate funded body study claims |
| `MAX_AUTHORED_STAGE` | A2 | No A3 |
| `BODY_SELECTION_ORDER` | EUROPA, PHOBOS | Stable body identity order |
| `SPONSOR_CLAIM_ORDER` | Australian Space Agency, Axiom, Blue Origin, CNES, CNSA, CSA, DLR, ESA, Interlune, Isar Aerospace, ispace, ISRO, JAXA, KASA, LandSpace, NASA, Roscosmos, SpaceX, Starlab, UAE Space Agency | Stable existing cast actor-ID order, not a fictional priority score |
| `PARTICIPATING_SPONSORS` | All 20 above in normal run | Controlled single-sponsor test variant proves repeated projects; default excludes nobody |
| `A1_POSITIVE_REVIEW_FRACTION` | 0.50 | TEST_ONLY synthetic outcome fraction, **not scientific probability** |
| `A1_REVIEW_SEED` | ROUTE1_BODY_PR3A_V1 | Explicit deterministic seed |
| `STUDY_DURATION_YEARS` | 1 | TEST_ONLY |
| `A1_SERVICE_CATEGORY` / `A1_SERVICE_PRICE` | RUN / .015 | Reused TEST_ONLY work-unit price |
| `A2_SERVICE_CATEGORY` / `A2_SERVICE_PRICE` | BUILD / .015 | Reused TEST_ONLY work-unit price |
| `COUNTRY_ALLOCATION_SHARE` | 0.25 | Existing PR 2 B25 Route 1 share |
| `FINANCIER_RESOURCE_BELIEF` / `FINANCIER_RESOURCE_PRIOR` | 0.5 / 0.5 | Existing uniform TEST_ONLY financier state |
| `A1_DISCLOSED_EVIDENCE_SOURCE` | AUTHORED:UNIFORM_NEUTRAL_ROUTE1_2026 | Existing sponsor-held neutral synthetic observation |
| `SPONSOR_REQUEST_CEILINGS_ENABLED` | True | Only toggle changed in the separate counterfactual |
| `LIFETIME_SPENDING_CAP` | None | **Not enabled**, legacy four-body limit does not constrain this campaign |
| `CARRY_CAP` | None | **Not enabled**, no two-times-price cash lapse |
| `GLOBAL_PROJECT_CAP` / `EXECUTOR_CAPACITY_CAP` | None / None | **Not invented** |

### Every existing per-request sponsor ceiling, TEST_ONLY model currency

| Sponsor | Ceiling | Sponsor | Ceiling |
|---|---:|---|---:|
| NASA | .350 | CNSA | .300 |
| ISRO | .120 | JAXA | .180 |
| ESA | .200 | CNES | .100 |
| DLR | .100 | Australian Space Agency | .050 |
| UAE Space Agency | .025 | ispace | .100 |
| Interlune | .025 | Roscosmos | .100 |
| CSA | .100 | KASA | .100 |
| SpaceX | .200 | Blue Origin | .200 |
| Axiom | .100 | Isar Aerospace | .100 |
| Starlab | .100 | LandSpace | .100 |

### Inherited existing TEST_ONLY financier parameters (not duplicated or altered)

| Parameter | Effective value |
|---|---:|
| `max_concentration_fraction` | .80 |
| `hurdle_rate` | .20 |
| `horizon_years` | 10 |
| `normalized_throughput` | 10 |
| `agent_detection_rate` | .80 |
| `agent_false_positive_rate` | .20 |

The underwriting inputs are explicitly named in `FINANCIER_UNDERWRITING_FACTS`: `PRICE=1`, `EXPLORATION_CAPEX=.125`, `DEVELOPMENT_CAPEX=.125`, `OPERATING_COST=.5`, `LEAD_TIME=1`. The existing financier requires actually available sponsor cash and disclosed sponsor-held information. The original 16-executor capabilities also gate selection: 7 eligible RUN providers, 14 BUILD providers. The quote winner is lowest comparable price, then authored preferred relationship, then existing stable actor ID. Nobody is paid merely to achieve a 16/16 supplier statistic.

## Single primary blocker, not a grab bag

For each considered and rejected/deferred stage request, record **exactly one** `primary_blocker`, its compared actual cash, sponsor ceiling, TEST_ONLY stage price, year/body/stage/sponsor and original financier reason if reached. Checks are ordered as follows; the first applicable named gate wins:

`MAX_NEW_STAGES_PER_SPONSOR_YEAR` → `MAX_CLAIMANTS_PER_BODY_CAMPAIGN` → `A1_REVIEW_NOT_READY` → `A1_REVIEW_INSUFFICIENT` → `COMPARABLE_EXECUTOR_QUOTE` → `EXECUTOR_CAPABILITY` → `SPONSOR_REQUEST_CEILINGS` → `ACTUAL_SPONSOR_CASH` → `FINANCIER_CONCENTRATION` → `FINANCIER_INFORMATION` → `FINANCIER_RETURN` → `FINANCIER_OTHER`.

No available new candidate means **NO_CANDIDATE**, not an attempted rejection. The completed result contains five attempted requests:

| Year | Sponsor | Body | Stage | Outcome | Primary blocker |
|---|---|---|---|---|---|
| 2036 | Australian Space Agency | Europa | A1 | FUNDED | NONE |
| 2036 | Australian Space Agency | Phobos | A1 | BLOCKED | MAX_NEW_STAGES_PER_SPONSOR_YEAR |
| 2036 | Axiom | Phobos | A1 | FUNDED | NONE |
| 2037 | Australian Space Agency | Europa | A2 | BLOCKED | A1_REVIEW_INSUFFICIENT |
| 2037 | Axiom | Phobos | A2 | FUNDED | NONE |

### Per-decade primary-blocker counts for every named rule

All unused blocker columns are shown as zero; there is no averaging or omission of the idle decades.

| Period | Attempted | Funded | `MAX_NEW_STAGES_PER_SPONSOR_YEAR` | `MAX_CLAIMANTS_PER_BODY_CAMPAIGN` | `A1_REVIEW_NOT_READY` | `A1_REVIEW_INSUFFICIENT` | `COMPARABLE_EXECUTOR_QUOTE` | `EXECUTOR_CAPABILITY` | `SPONSOR_REQUEST_CEILINGS` | `ACTUAL_SPONSOR_CASH` | `FINANCIER_CONCENTRATION` | `FINANCIER_INFORMATION` | `FINANCIER_RETURN` | `FINANCIER_OTHER` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2036–2045 | 5 | 3 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2046–2055 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2056–2065 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2066–2075 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2076–2085 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2086–2095 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2096–2105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2106–2115 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2116–2125 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2126–2135 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2136–2145 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2146–2155 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2156–2165 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2166–2175 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2176–2185 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2186–2195 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2196–2205 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2206–2215 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2216–2225 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2226–2226 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Reconciliation:** **5 attempted = 3 funded + 2 single-primary-blocker results**. In each of the 20 calendar-decade reporting buckets, attempted = funded + sum(named blockers). The last bucket covers year 2226 alone. Source is the recorded `campaign.attempts`/`campaign.decades` outputs and the eight new tests.

## Synthetic evidence/review, deterministic and separated from hidden WORLD

`a1_draw(body) = int_from_bytes(SHA256("ROUTE1_BODY_PR3A_V1" + "|" + body + "|A1")) / 2^256`, in Decimal precision. Draw below TEST_ONLY 0.50 means a synthetic `SUPPORTS_ADVANCE` / `ADVANCE` outcome; otherwise `INSUFFICIENT` / `HOLD`.

- **Europa**: draw `0.6110510016917168358468180901`, so HOLD and one explicitly blocked A2.
- **Phobos**: draw `0.3592648676293149899316784012`, so ADVANCE and a funded 2037 A2.

The draw knows only seed/body/stage, **not private WORLD material presence, public geological evidence, or ephemeris truth**. The A1 observation/review is a Build 8 TEST_ONLY journaled research transition, **not** a claimed execution of the frozen 6C physical/study engine. If a supplier fails, the result is NO_RESULT/HOLD with no observation. These limitations are deliberate and explicit.

## One-stage-per-sponsor-year limit: what it actually filters

This **was Sol's proposed TEST_ONLY limit, not kT's**. It causes exactly **one** 2036 otherwise-affordable Phobos A1 request to be recorded as blocked for the Australian Space Agency. Because Axiom subsequently claims and funds Phobos, the number of funded body campaigns remains **2**. Raising only the named stage limit from 1 to 2 lets the Australian Space Agency finance both bodies. The total is still three funded stages: it changes claimant distribution and causes an avoidable blocked request, not a physical capability improvement. It is retained in this draft only to measure the explicit approved trial setting and should not be promoted into an enduring governor without evidence.

A separate CONTROL with only NASA participating in new study bids proves repeat sponsor/body projects: NASA finances **Europa A1 in 2036**, **Phobos A1 in 2037**, and **Phobos A2 in 2038**. The underlying same 20-sponsor Earth funding ledger remains intact. No sponsor lifetime spending cap is added.

## Existing original decade: exact unchanged baseline

The independently pinned former `main 79a10e1` baseline was established in merged PR #399 as identical to `eb7d33ce` over 2026–2035. The PR 3A extended run exactly matches the same golden objects:

| Check | Original first decade | PR 3A first decade |
|---|---:|---:|
| Sponsor-year rows | 200 | **200, exact object equality** |
| Original paid executor receipts | 20 | **20, exact object equality** |
| Ledger transactions (IDs, parent lineage, amounts) | 450 | **450, exact object equality** |
| Sponsor row SHA-256 | `15fdc6b00df21d6b748a67a36fe9fbbca6d6fcb6156222ff1b5657eecca8b9cb` | MATCH |
| Transaction SHA-256 | `f7e5ea74867d051e41bffab7f366bbfb5dd3e801fc4a9d324703eeed55fbea86` | MATCH |

The original default `run_cast_payments()` still produces the exact old full kernel fingerprint. Inherited tests establish **17/17 unchanged off-state snapshots**, exact NASA/CNSA pilot and unchanged four-body follow-on tests.

## Money conservation in every year

For **every sponsor in every year from 2026 through 2226**, verify using actual ledger transactions:

`closing(s,y) = previous_closing(s,y) + country_origin_allocations(s,y) - all_actual_disbursements(s,y)` (Decimal tolerance 1e−24).

All 23 qualified country-origin accounts settle to zero **each year**, or **4,623 country-year origins**. Each annual disbursement sum equals the same year's supplier CAPEX. All new per-body project-cash accounts return to zero after the supplier payment, with payment transaction parent IDs pointing at actual disbursements. The unchanged kernel accounting invariants and full deterministic replay pass. No bank, interest, loan or additional modeled money source.

- Original paid 2026 service tokens: **0.350** model currency.
- Additional three 2036/2037 TEST_ONLY body-study units: **0.045** model currency.
- Cumulative supplier payments 2026–2226: **0.395** model currency.
- Original PR 2 unspent sponsor cash at 2226: approximately **1,662.403631**; PR 3A: approximately **1,662.358631**. Accumulation persists because no additional work is authored beyond the two new bodies.

## Regression command: exact 67 tests, one sequential run

```bash
PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python3 -m unittest -v simulation.offworld_mvp.build8.test_yearly_acceptance simulation.offworld_mvp.build8.test_screened_delivery simulation.offworld_mvp.build8.test_master_cast_snapshots tests.test_build6c_four_body_portfolio simulation.offworld_mvp.build8.test_route1_gate1 simulation.offworld_mvp.build8.test_route1_gate2 simulation.offworld_mvp.build8.test_capacity_options simulation.offworld_mvp.build8.test_route1_carry_cap simulation.offworld_mvp.build8.test_route1_carry_cap_extension simulation.offworld_mvp.build8.test_nasa_moon_a1 simulation.offworld_mvp.build8.test_nasa_moon_a2 simulation.offworld_mvp.build8.test_defense_v2_gate simulation.offworld_mvp.build8.test_followon_isolation simulation.offworld_mvp.build8.test_followon_trial simulation.offworld_mvp.build8.test_followon_four_body simulation.offworld_mvp.build8.test_route1_cast_payments simulation.offworld_mvp.build8.test_route1_horizon_pr2 simulation.offworld_mvp.build8.test_route1_body_campaign_pr3a
```

| Module | Expected | Verified |
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
| `test_route1_body_campaign_pr3a` | 8 | 8 |
| **TOTAL** | **67** | **67** |

**PASS: 67/67**, **443.221 seconds**, **0 failures**, **0 skips**, **18/18 expected test module counts matched exactly**. Fifty-nine inherited tests plus eight PR 3A tests. Nothing was split into parallel module runs.

## CI limitations and deliberate omissions

GitHub **LOOM Gate** and **Integrated Simulation Health** do **not** run the new `test_route1_body_campaign_pr3a.py` or the full sequential **67-test** sequence on external pinned Earth v4 inputs. Green CI alone does not establish complete first-decade identity, 201 annual money reconciliations, 17 off-state protected snapshots, synthetic review gating, or blocker counts. The tests were run sequentially on quantifactus with the existing local Earth v4 baseline.

**Deliberately absent:** physical mission purchase/trajectory model, 90-body campaign, A3, repeat missions after candidate exhaustion, global active-project cap, issuer bank/loans/interest, issuer money top-up, sponsor lifetime cap, cash carry-lapse, executor capacity quota, new project schema, kernel/phase3b edit, Build 5/6/7 edit or any frozen path edit. Scientific observation from actual hidden WORLD remains out of scope. Numerical work packages and synthetic review fraction are all **TEST_ONLY**.

**DRAFT ONLY:** Do not merge without explicit approval. Notify the user before changing this reviewed PR.
