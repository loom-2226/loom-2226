# PR 2: Four-body result-triggered follow-on funding

**class:research · EXPERIMENTAL · AUTHORED · TEST_ONLY · NON-CANON · Build 8 only · opt-in and off by default.**

Base: `main` at `698aec2c16d90faeb8bf574797cc85e13f3619fc`. Draft only, no merge, no frozen 6C or kernel edits.

## Mechanism

One Earth Route 1 ledger per run. The existing TEST_ONLY financier considers annual requests. An actual funded A1 schedules an authored 6C execution; only its admitted `SUPPORTS_ADVANCE` result plus `ADVANCE` review permits A2. A2 must independently pass the financier, per-request ceiling, cumulative sponsor limit, body claim, cash and concentration. The study starts at the later of financing, review, earliest start and opportunity open. No backdating. After the 2035 financing cutoff a funded study may still finish. The frozen 6C outcome is not a generated scientific truth.

**Fixed claim order:** NASA → CNSA → ESA → ISRO → JAXA → CNES → DLR → ispace. One claimant per body-chain, first actually funded wins. At most one A2 request per sponsor-year, two funded stages per sponsor, 2× next authored activity price carry cap (trial only), no A3. All values and relationships are AUTHORED / TEST_ONLY / NON-CANON.

## Authored sponsor table

100 native 6C study units = 1 Route 1 MODEL_CURRENCY (authored conversion). Prices and study standings come from the pinned 6C scenario; identities, bounds and two ceiling overrides are newly authored trial selections.

| Sponsor | Body | A1, price, result | A2, price, potential result | Existing ceiling | Trial ceiling | Lifetime total |
|---|---|---|---|---:|---:|---:|
| NASA | MOON | MOON-A1-SURFACE / 0.35 / SUPPORTS_ADVANCE | MOON-A2-ASSESS / 0.3 / INSUFFICIENT | .350 | .350 | 0.650 |
| CNSA | BENNU | BENNU-A1-RESOURCE / 0.15 / SUPPORTS_ADVANCE | BENNU-A2-CONCEPT / 0.25 / INSUFFICIENT | .300 | .300 | 0.400 |
| ESA | CERES | CERES-A1-SURFACE / 0.7 / SUPPORTS_ADVANCE | CERES-A2-ASSESS / 0.25 / SUPPORTS_ADVANCE | .200 | 0.700 | 0.950 |
| ISRO | MARS | MARS-A1-REMOTE / 0.2 / SUPPORTS_ADVANCE | MARS-A2-SURFACE / 0.6 / INSUFFICIENT | .120 | 0.200 | 0.200 |
| JAXA | BENNU | BENNU-A1-RESOURCE / 0.15 / SUPPORTS_ADVANCE | BENNU-A2-CONCEPT / 0.25 / INSUFFICIENT | .180 | .180 | 0.180 |
| CNES | CERES | CERES-A1-SURFACE / 0.7 / SUPPORTS_ADVANCE | CERES-A2-ASSESS / 0.25 / SUPPORTS_ADVANCE | .100 | .100 | 0.100 |
| DLR | MOON | MOON-A1-SURFACE / 0.35 / SUPPORTS_ADVANCE | MOON-A2-ASSESS / 0.3 / INSUFFICIENT | .100 | .100 | 0.100 |
| ispace | MARS | MARS-A1-REMOTE / 0.2 / SUPPORTS_ADVANCE | MARS-A2-SURFACE / 0.6 / INSUFFICIENT | .100 | .100 | 0.100 |

**Override scope:** ESA `.200 → .700` and ISRO `.120 → .200` are trial-only, AUTHOR-SELECTED / TEST_ONLY; `CEILINGS` in the default Gate 1 is not changed. B25_NO_OVERRIDES switches both off.

## Five actual counterfactual runs

| Run | Scenario | Share | Overrides | Funded activities | Claimed bodies | Finding |
|---|---|---:|---|---:|---:|---|
| A10 | A | .10 | ON | 0 | 0 | No funded study; the neutral observation is absent |
| A25 | A | .25 | ON | 0 | 0 | More cash does not cure missing evidence |
| B10 | B | .10 | ON | 7 | 4 | Same seven stages as B25, but late Moon/Mars/Ceres first finance |
| B25 | B | .25 | ON | 7 | 4 | Seven stages, four claims; Mars A2 cannot fund |
| B25_NO_OVERRIDES | B | .25 | OFF | 4 | 2 | Four stages; only Moon/Bennu claimants |

## Four-body chains in each run

Only executed studies have actual results. Mars A2 is unfunded: its authored `INSUFFICIENT` is NOT an observed result.

| Run | Body | Claimant | A1 funded / result | A2 funded / result | Stop reason |
|---|---|---|---|---|---|
| A10 | MOON | — | — | — | WINDOW_EXPIRED |
| A10 | MARS | — | — | — | UNFUNDED_BY_2035 |
| A10 | CERES | — | — | — | WINDOW_EXPIRED |
| A10 | BENNU | — | — | — | UNFUNDED_BY_2035 |
| A25 | MOON | — | — | — | WINDOW_EXPIRED |
| A25 | MARS | — | — | — | UNFUNDED_BY_2035 |
| A25 | CERES | — | — | — | WINDOW_EXPIRED |
| A25 | BENNU | — | — | — | UNFUNDED_BY_2035 |
| B10 | MOON | NASA | 2028 / SUPPORTS_ADVANCE | 2029 / INSUFFICIENT | RESULT_INSUFFICIENT |
| B10 | MARS | ISRO | 2028 / SUPPORTS_ADVANCE | — | FOLLOWON_BUILT_IN_CEILING |
| B10 | CERES | ESA | 2029 / SUPPORTS_ADVANCE | 2035 / SUPPORTS_ADVANCE | NO_NEXT_AUTHORED_ACTIVITY |
| B10 | BENNU | CNSA | 2026 / SUPPORTS_ADVANCE | 2027 / INSUFFICIENT | RESULT_INSUFFICIENT |
| B25 | MOON | NASA | 2026 / SUPPORTS_ADVANCE | 2029 / INSUFFICIENT | RESULT_INSUFFICIENT |
| B25 | MARS | ISRO | 2026 / SUPPORTS_ADVANCE | — | FOLLOWON_BUILT_IN_CEILING |
| B25 | CERES | ESA | 2027 / SUPPORTS_ADVANCE | 2034 / SUPPORTS_ADVANCE | NO_NEXT_AUTHORED_ACTIVITY |
| B25 | BENNU | CNSA | 2026 / SUPPORTS_ADVANCE | 2027 / INSUFFICIENT | RESULT_INSUFFICIENT |
| B25_NO_OVERRIDES | MOON | NASA | 2026 / SUPPORTS_ADVANCE | 2029 / INSUFFICIENT | RESULT_INSUFFICIENT |
| B25_NO_OVERRIDES | MARS | — | — | — | BUILT_IN_CEILING |
| B25_NO_OVERRIDES | CERES | — | — | — | BUILT_IN_CEILING |
| B25_NO_OVERRIDES | BENNU | CNSA | 2026 / SUPPORTS_ADVANCE | 2027 / INSUFFICIENT | RESULT_INSUFFICIENT |

## Authored versus emergent outcomes

**Authored:** sponsor-to-body choices, all eight A1/A2 study costs/results, opportunity windows, financier neutral underwriting, the absence of a Scenario A neutral observation, scenario shares, the conversion, fixed priority, ceiling overrides, cumulative limits, carry-cap and 2035 last financing year.

**Emergent under these inputs:** claim winners, policy decisions, whether cash/concentration/claims deny a request, the year money becomes available, whether a window closes first, retimed study start/review dates, and which scripted result is actually reached. A positive Ceres result does not create an A3.

**Unexpected or notable:** B10 still funds seven stages (like B25), but Ceres A1 is funded in 2029 instead of 2027; Ceres A2 finances in 2035 and completes in 2036.02. The financing cutoff is respected. Reversing the eight-sponsor priority changes **CNES in 2027**: normal order skips its request because ESA already claimed Ceres; reversed order lets CNES request first and get `REJECT / CEILING`, before ESA claims it. No funded activity or body owner changes. A forced same-body eligible collision does reverse the winner.

**BUILT_IN** means assigned activity price exceeds its sponsor ceiling, even if a later window expires. **EMERGENT** means cash/concentration/epistemic admissibility, claim, window or cumulatively exhausted real spending. Reports keep original financier `reason` separate from the Build 8 `status`; no invented financier codes.

## Pilot and default isolation

The original NASA+CNSA PR 1 pilot is rerun and checked against `FOLLOWON_PR2_PILOT_BASELINE_698aec2c.json`, independently captured from unmodified `698aec2c` main: exact entire annual rows digest, funding records, Earth and A1/A2 fingerprints. The original 17 off-state main fingerprints/complete row digests in `test_followon_isolation.py` also remain unchanged. In expanded B25, NASA and CNSA **fund the same stages in the same years and obtain the same authored results**. Later transaction IDs and whole-Earth fingerprints differ because six more sponsors participate; those are not presented as byte-identical.

## Machine-readable timeline and annual reports

Every run has **80 annual sponsor rows** from 2026–2035: 400 total in [annual CSV](FOLLOWON_PR2_ANNUAL.csv). Complete five visualizable Year/Time/Sponsor/Event/Body/Activity tables are in [timeline tables](FOLLOWON_PR2_TIMELINES.md) and [timeline CSV](FOLLOWON_PR2_TIMELINES.csv). See [body summary CSV](FOLLOWON_PR2_BODIES.csv). The timeline contains every no-request year and the later actual result/admission/review events, including any 2036 completion. No Earth financing takes place past 2035.

## Accounting boundary

Financier uses the existing sponsor-budget cash/concentration proxy, **not a separately conserved lender treasury**. The execution kernel is a referenced, cost-reconciled reconstruction following an approved Earth disbursement; no live two-ledger cash injection, no physical shared state, no new mineral inventory or new mine, no kernel or frozen changes.

## Test command and CI limits

From repository root on quantifactus, with pinned external Earth v4 available:

```bash
PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python3 -m unittest -v simulation.offworld_mvp.build8.test_yearly_acceptance simulation.offworld_mvp.build8.test_screened_delivery simulation.offworld_mvp.build8.test_master_cast_snapshots tests.test_build6c_four_body_portfolio simulation.offworld_mvp.build8.test_route1_gate1 simulation.offworld_mvp.build8.test_route1_gate2 simulation.offworld_mvp.build8.test_capacity_options simulation.offworld_mvp.build8.test_route1_carry_cap simulation.offworld_mvp.build8.test_route1_carry_cap_extension simulation.offworld_mvp.build8.test_nasa_moon_a1 simulation.offworld_mvp.build8.test_nasa_moon_a2 simulation.offworld_mvp.build8.test_defense_v2_gate simulation.offworld_mvp.build8.test_followon_isolation simulation.offworld_mvp.build8.test_followon_trial simulation.offworld_mvp.build8.test_followon_four_body
```

**Verified after scaling review: 47/47 PASS, 0 failures, 0 skips, exit 0, 391.727 seconds (quantifactus).** Exactly 32 historical + 7 PR1 + 8 PR2 tests, one sequential process. The external pinned Earth v4 baseline was available.

GitHub LOOM Gate checks PR governance; Integrated Simulation Health runs existing integrated tests. **Neither runs the new PR2 `test_followon_four_body.py`, the PR1 follow-on/isolation tests, nor the complete 46-test sequence including Defense V2.** External pinned Earth v4 is required locally. A green GitHub CI status is not evidence of a complete PR2 regression.

## Scaling and money-handoff review (PR #397 follow-up)

**Row-only synthetic scaling test:** `test_ninth_sponsor_fifth_body_from_synthetic_rows_only` appends a ninth test-only sponsor (`TEST_ONLY_SYNTHETIC_SPONSOR`, participating through the existing AUS country envelope), a fifth test-only body, an evidence row, and authored A1/A2 activity rows. No synthetic row enters the canonical 6C scenario, the standing sponsor network, or runtime authority. All synthetic rows exist in the test only, with a distinct `TEST_ONLY_NON_CANON` in-memory portfolio identity. The 6C loader's frozen four-body validation is unchanged.

The normal `run_four_body()` logic now derives its body set, assigned sponsors, activities, prices, ceilings and fixed claim order from authored table rows rather than embedded body names. The scaling test verifies **90 annual sponsor-year rows, five body summaries, the fifth claimant, A1 funded in 2026, result/review, A2 funded in 2027, terminal INSUFFICIENT, and timeline events**. This is a synthetic behavior test, not a fifth canonical physical object.

**Single finance-to-execution handoff:** `route1_funding_handoff()` in `followon_execution.py` is the only entry through which the PR 1 pilot and eight-/nine-sponsor runner represent a recorded Route 1 disbursement as 6C execution opening money. It checks sponsor identity, a populated Route 1 funding transaction reference, and the funding year; `execute_stage()` enforces the authored price conversion and 6C expenditure conservation. The reconstructed execution balance is never added to the Route 1 ledger. This remains **reconstruction, not live continuation**.

**Regression:** the original 17 off-state snapshots remain identical; PR 1's independently pinned NASA/CNSA pilot rows and fingerprints remain identical to `698aec2c`; existing B25 eight-sponsor run semantics are unchanged. The exact unittest command above is unchanged in module selection; `test_followon_four_body.py` now contains eight tests rather than seven, so it runs **47** in total. GitHub CI does not run this suite.

**PR description update pending user permission.** The PR branch and this review pack can be updated, but its GitHub description must not be edited without the requested prior notice and reply.
