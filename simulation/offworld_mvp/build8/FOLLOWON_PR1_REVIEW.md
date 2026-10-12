# Follow-on funding PR 1: plain review pack

**class:research · EXPERIMENTAL · AUTHORED · TEST_ONLY · NON-CANON · Build 8 · opt-in · off by default.**

Base: main at 0ae8dfd17cc6986347c98f8ed1a7c74bd2c52dc8. No kernel, frozen 6C portfolio, or Build 7 changes. No merge authorized.

## What this tests

- Two actual 6C-authored result chains: NASA Moon A1 to A2 and CNSA Bennu A1 to A2.
- One shared Route 1 Earth ledger; distinct reconstructed execution kernels. Reconstruction is **not** live continuation or a second Earth balance.
- Follow-ons require actual admitted SUPPORTS_ADVANCE with ADVANCE review. Results permit requests; they **do not** price them.
- Existing ROUTE1_FINANCIER, neutral TEST_ONLY underwriting, 0.80 concentration, sponsor cash, per-request ceilings, cumulative limits, 2035 cutoff.
- At most one follow-on request per sponsor-year and one funded A2 per sponsor. Exclusivity of claims is enforced at actual funding.
- Only Scenario B / 25% / 2x next activity cost carry is enabled for PR 1. Scenario A, 10%, later A1 starts, six additional sponsors and four-body runs remain for PR 2.

## Fixed claim order

Recorded priority: **NASA, CNSA**, followed by unassigned sponsors in normal name order. First sponsor *actually funded* wins a body chain. Reversing priority in the real pilot changes no semantic outcomes because NASA and CNSA request different bodies.

Reversed real-pilot outcomes changed: **FALSE**.
A synthetic competition gives both sponsors the Bennu A1 activity at the identical authored 0.150 price: order NASA/CNSA funds NASA and blocks CNSA; reversing it funds CNSA and blocks NASA. The loser receives WAIT_CLAIMED_BY_OTHER, not a fictitious financier rejection. This synthetic fixture is non-canon.

## Authored assignment table

All amounts are Route 1 MODEL_CURRENCY. Conversion: 100 6C native units = 1 MODEL_CURRENCY; authored/test-only.

| Sponsor | Body | A1 price / outcome | A2 price / outcome | Existing per-request ceiling | Trial-wide cumulative limit |
|---|---|---|---|---:|---:|
| NASA | MOON | 0.35 / SUPPORTS_ADVANCE | 0.3 / INSUFFICIENT | .350 | 0.650 |
| CNSA | BENNU | 0.15 / SUPPORTS_ADVANCE | 0.25 / INSUFFICIENT | .300 | 0.400 |

All assignments, assumptions and limits AUTHORED / TEST_ONLY / NON-CANON. Prices and results are read from the pinned 6C authored scenario, not inferred from scientific truth.

## Observed pilot outcomes

| Sponsor | A1 funding | A2 funding | A2 review time | Stop reason |
|---|---|---|---|---|
| NASA | MOON-A1-SURFACE / 2026 | MOON-A2-ASSESS / 2029 | 2030.62 | RESULT_INSUFFICIENT |
| CNSA | BENNU-A1-RESOURCE / 2026 | BENNU-A2-CONCEPT / 2027 | 2028.12 | RESULT_INSUFFICIENT |

## Per-sponsor, per-year report

A REQUEST includes a financier decision. NO_REQUEST never means a new decision. BUILT_IN means authored activity price > assigned per-request ceiling. EMERGENT means balance, concentration, cumulative spending history, claim or window. Original financier codes are separate from simulator wait reasons.

| Year | Sponsor | Stage | Event | Requested | Financier / reason | Status | Failure class | Disbursement | Stop |
|---:|---|---|---|---:|---|---|---|---|---|
| 2026 | NASA | A1 | REQUEST | 0.35 | APPROVE / APPROVED_POLICY_RULE | FUNDED_PENDING_EXECUTOR | — | tx-000043 | — |
| 2026 | CNSA | A1 | REQUEST | 0.15 | APPROVE / APPROVED_POLICY_RULE | FUNDED_PENDING_EXECUTOR | — | tx-000045 | — |
| 2027 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / WAIT_RESULT | WAIT_RESULT | — | — | — |
| 2027 | CNSA | A2 | REQUEST | 0.25 | APPROVE / APPROVED_POLICY_RULE | FUNDED_PENDING_EXECUTOR | — | tx-000102 | — |
| 2028 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / WAIT_RESULT | WAIT_RESULT | — | — | — |
| 2028 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2029 | NASA | A2 | REQUEST | 0.3 | APPROVE / APPROVED_POLICY_RULE | FUNDED_PENDING_EXECUTOR | — | tx-000212 | — |
| 2029 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2030 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2030 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2031 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2031 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2032 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2032 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2033 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2033 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2034 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2034 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2035 | NASA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |
| 2035 | CNSA | A2 | NO_REQUEST | — | NOT_EVALUATED / ALREADY_PURCHASED | COMPLETE | — | — | RESULT_INSUFFICIENT |

## Off-state isolation against unchanged main

Captured **17 golden snapshots** directly on main at 0ae8dfd17cc6986347c98f8ed1a7c74bd2c52dc8. They include Gate 1 A/B at 10%/25%, Gate 2 at both shares and unlimited/0/1/2 carry caps, 2035 carry extension at both shares, NASA A1, and NASA A2 with unlimited and 1x carry.

Each snapshot pins SHA-256 of the canonical serialized full rows and the exact relevant kernel fingerprints. A1 result entries, A2 decision/evidence and both A2 stage fingerprints are additionally checked. The opt-off test compares the changed branch against those independent main results, not against itself.

## Scope / limitations

- Future PR 2: six more sponsors; ESA/ISRO ceiling overrides in test-only trial; all four bodies and Scenario A/B x 10%/25%; Scenario B 25% control with those overrides off.
- Future PR 2 must handle late initial funding and dynamic result dates. PR 1 explicitly refuses the pilot if either A1 was not funded in 2026.
- No cross-kernel atomic funding, lender-owned cash treasury, A3 invention, or empirically validated underwriting. A funded 6C activity is a reconstructed cost, paired to exactly one Route 1 transaction.
- When the chain is complete it never requests another stage. The 2035 financing cutoff is absolute.
- GitHub LOOM Gate checks PR governance and Integrated Simulation Health checks pre-existing simulation modules. Neither invokes these new two tests; neither proves the Earth v4-dependent isolation. Local result is reported separately.

## Full sequential regression command

Run from repository root on quantifactus with external Earth v4 available.

~~~bash
PYTHONPATH=.:src:simulation/offworld_mvp/phase3b/kernel python3 -m unittest -v simulation.offworld_mvp.build8.test_yearly_acceptance simulation.offworld_mvp.build8.test_screened_delivery simulation.offworld_mvp.build8.test_master_cast_snapshots tests.test_build6c_four_body_portfolio simulation.offworld_mvp.build8.test_route1_gate1 simulation.offworld_mvp.build8.test_route1_gate2 simulation.offworld_mvp.build8.test_capacity_options simulation.offworld_mvp.build8.test_route1_carry_cap simulation.offworld_mvp.build8.test_route1_carry_cap_extension simulation.offworld_mvp.build8.test_nasa_moon_a1 simulation.offworld_mvp.build8.test_nasa_moon_a2 simulation.offworld_mvp.build8.test_defense_v2_gate simulation.offworld_mvp.build8.test_followon_isolation simulation.offworld_mvp.build8.test_followon_trial
~~~

**Verified on this PR 1 checkout: 39/39 PASS, 0 failures, 0 skips, exit 0, 296.836 seconds (2026-10-12).** Historical 32 + 1 off-isolation + 6 focused tests, one sequential process. The external Earth v4 baseline was available on quantifactus.
