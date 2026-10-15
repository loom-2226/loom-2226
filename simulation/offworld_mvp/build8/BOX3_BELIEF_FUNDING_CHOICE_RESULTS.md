# Build 8 PR C: Belief-Driven Funding Choice (opt-in evidence)

**RESEARCH / NON-CANON / IN-MEMORY ONLY.** Exact starting main SHA: `170a0084e92705b7d1666d93532994d815405af6` (#415 merged). Nothing in this report authorizes a canon or World Authority join. One sponsor and two existing-form *real kernel* Offworld projects per independent scenario; one common Earth-side sponsor capital pool, 100 MODEL_CURRENCY, and commitments of 60 each. One objective: expected monetary value, no nonfinancial preference. Frozen `SPONSOR_PORTFOLIO_V1` and kernel unmodified.

## Mechanism and authored inputs

**Expected net value = admitted Bayesian posterior × sponsor-assigned success value − project commitment.** The assigned success value is an experimental monetary outcome *conditional on success*, not an observed commodity price or guaranteed realization. A sponsor's minimum expected net return is a visible hurdle. A candidate qualifies if and only if expected net value **>= hurdle**; below-hurdle activities are excluded from the policy request, not from the recorded decision evidence. All projects retain PROPOSED status until the existing kernel advances the one actually funded. Eligible candidates get integer priorities 1, 2 in descending expected net value with deterministic ties by `project_id, activity_id`. Those priorities are supplied to the **unchanged** portfolio policy. The policy itself remains responsible for its normal affordability decision. No extra limit or preference is added.

Fixed experimental likelihoods: prior 0.5 per project; detection 0.8; false-positive 0.2; existing `update_agent_belief_from_observation`. Posterior 0.2 uses one admitted NEGATIVE; 0.8 uses one admitted POSITIVE; **0.5 is derived** through sequential POSITIVE then NEGATIVE (not inserted as a belief). Both projects have independent, explicitly admitted, synthetic `BodyRemoteObservation` records. B is always fixed at 0.5. All tests start from fresh independent kernel instances. No fabricated hidden geological truth exists.

## Complete decision matrix

All currency columns are MODEL_CURRENCY. A/B cost **60 / 60 in every row**, and pool **100** in every row. Values and hurdles were declared before execution and not adjusted against outcomes. In `Offered`, the order reflects computed priority; a dash means **no call to portfolio policy**.

| Case | Sponsor | p(A) | p(B) | Value A | Value B | Cost A | Cost B | Hurdle | EV A | EV B | Offered | Result | Cash left |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| A20 | SPN | 0.2 | 0.5 | 200 | 130 | 60 | 60 | 0 | -20 | 5 | B | B | 40 |
| A50 | SPN | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 0 | 40 | 5 | A>B | A | 40 |
| A80 | SPN | 0.8 | 0.5 | 200 | 130 | 60 | 60 | 0 | 100 | 5 | A>B | A | 40 |
| ValuesFlip | SPN | 0.5 | 0.5 | 100 | 200 | 60 | 60 | 0 | -10 | 40 | B | B | 40 |
| Low0 | SPN | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 0 | 40 | 5 | A>B | A | 40 |
| Medium20 | SPN | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 20 | 40 | 5 | A | A | 40 |
| High150 | SPN | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 150 | 40 | 5 | — | DECLINED | 100 |
| SponsorLow | SPN_LOW | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 0 | 40 | 5 | A>B | A | 40 |
| SponsorHigh | SPN_HIGH | 0.5 | 0.5 | 200 | 130 | 60 | 60 | 150 | 40 | 5 | — | DECLINED | 100 |
| Tie | SPN | 0.5 | 0.5 | 200 | 200 | 60 | 60 | 0 | 40 | 40 | A>B | A | 40 |

### Choice-change and no-change observations

- **A belief grid (B fixed 50%, values 200/130, hurdle 0):** A 20% -> B funds (EV A -20, EV B 5); A 50% -> A funds (40 vs 5); A 80% -> A still funds (100 vs 5). The decision **changes at 20 to 50**, **does not change at 50 to 80**. There was no belief tuning after these observations.
- **Different authored monetary values, same 50% beliefs and hurdle 0:** A=200/B=130 -> A; A=100/B=200 -> B. A project succeeds in attracting funding based on expected money, not arbitrary original priority.
- **Hurdles 0, 20, 150 at identical beliefs and values:** hurdle 0 offers both and funds A; hurdle 20 offers only A and funds A (**unchanged funding choice, changed eligibility**); hurdle 150 offers neither, explicitly **DECLINED** and transfers 0.
- **One above and one below:** hurdle 20 has EV A=40 above and EV B=5 below. B stays PROPOSED, ACT-B stays PROPOSED, with recorded `BELOW_HURDLE`.
- **Both above, insufficient funds for both:** hurdle 0 offers A then B, both commitment 60, aggregate 120 vs pool 100; A receives 60, remaining sponsor cash 40, unchanged policy explicitly returns `DEFER / INSUFFICIENT_AVAILABLE_CAPITAL` for B. B remains PROPOSED, **not abandoned**.
- **Two separately modeled sponsors:** SPN_LOW (hurdle 0) funds A; SPN_HIGH (hurdle 150) declines; both have exactly the same admitted beliefs, values, projects and initial pool in independent runs. No simultaneous/multi-sponsor ownership is modeled.
- **Tied EV control:** p=.5 for both, values A/B=200/200, hurdle 0 -> both EV 40; deterministic project/activity-ID tie selects A.

A full decline produces a sponsor causal **DECLINED** event containing `ALL_EXPECTED_NET_VALUES_BELOW_HURDLE`, the numerical hurdle, and each candidate's EV. Separate below-hurdle causal events leave both project and activity states PROPOSED. Where one is funded, a real ledger `OTHER_INVESTMENT` Earth (`<sponsor>:POOL`) -> Offworld (`cash:A` or `cash:B`) transaction transfers 60 with decision/activity parent lineage; the funded project advances to DEVELOPMENT. These are actual kernel transitions and transfers, not a new financial policy.

## Earth capital gauge and yearly identities

For **each** row in the matrix, this is the capital ledger split at EARTH:X. All columns are numeric, including genuine zeros. `New + recycled = total draw`; `A + B + unattributed = total draw` were both asserted **for every year of every scenario**. Recycling is zero because there are no proven returns; a project allocation is a breakdown of the kernel's Earth shadow draw, not an additional draw.

| Case | Year | A | B | Unattributed | New | Recycled | Total draw | Check 1 | Check 2 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| A20 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| A20 | 2 | 0 | 60 | 0 | 60 | 0 | 60 | PASS | PASS |
| A20 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| A50 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| A50 | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| A50 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| A80 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| A80 | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| A80 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| ValuesFlip | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| ValuesFlip | 2 | 0 | 60 | 0 | 60 | 0 | 60 | PASS | PASS |
| ValuesFlip | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Low0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Low0 | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| Low0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Medium20 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Medium20 | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| Medium20 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| High150 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| High150 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| High150 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| SponsorLow | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| SponsorLow | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| SponsorLow | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| SponsorHigh | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| SponsorHigh | 2 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| SponsorHigh | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Tie | 1 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |
| Tie | 2 | 60 | 0 | 0 | 60 | 0 | 60 | PASS | PASS |
| Tie | 3 | 0 | 0 | 0 | 0 | 0 | 0 | PASS | PASS |

Additional existing `_gauge` fields: returns to Earth **0**, study spend **0**, Offworld purchases from Earth **0**, Earth-side transport spending **0**, for **each year of every scenario**, not blanks. These zeros reflect absent transactions, not an assumption that such flows are economically impossible. A/B balances after funding are 60/0 (A-selected), 0/60 (B-selected), or 0/0 (declined); sponsor balance is 40 or 100 accordingly. Actual 100 opening money is neither destroyed nor double counted.

## Information boundary, determinism and unchanged authority

- The fixture does **not instantiate a WORLD generator, source-truth resource or hidden geologic state**: `kernel.resources` is empty and no `hidden_world` exists; the synthetic observation records are directly added to the sponsor's information, then processed by the kernel's **existing** Bayesian update rule. Both actor-visible snapshots export only admitted evidence refs, posteriors/priors, actor-visible authored values, hurdle, computed EV/priority, and existing policy facts. New tests check every produced snapshot for excluded hidden-state keys and permitted fact provenance.
- Policy input is only `offered_to_policy`, never a below-hurdle candidate. No such policy call occurs on complete decline. The remaining candidate of a both-above case is separately evaluated by the unchanged policy after a genuine transfer.
- **Full deterministic replay:** local test re-creates independent runs with equal parameters and checks **exact equality of complete reports and sorted JSON**, including decisions, snapshots, ledger gauges, causal references and state fingerprints, across grid, different values, hurdles and sponsors. This is not a World Authority reopen test.
- **Modification boundary:** only three *new* opt-in files under `simulation/offworld_mvp/build8/`: `box3_belief_funding_choice.py`, `test_box3_belief_funding_choice.py`, and this report. No existing tracked files were changed, therefore frozen kernel, portfolio policy, frozen paths, existing pins, baselines and placeholders retain precisely the main-base content.

## Tests and CI scope

- **Local added PR C tests:** 12/12, including evidence-derived 20/50/80 beliefs, changed and unchanged choices, alternative monetary values, low/medium/high hurdles, all-decline untouched capital, one-above, both-above affordability, sponsors, deterministic tie break, real transfer, every-year identities, forbidden hidden state, and replay.
- **Local prior #415 tests:** 6/6 unchanged.
- **Local Build 6A temporal multiproject:** 8/8 unchanged.
- **Local combined above:** 26/26 passing.
- **Local exact CI-equivalent selection:** 10/10 PASS, zero failures, errors or skips, using the workflow's exact class/module selectors and Earth-v4-absent sentinel.
- **Existing Build 8 Fast Tests workflow:** selects exactly 8 Build 6C + 2 `test_capacity_options` (10 total). PR C's twelve tests are **local-only**, not included in the existing CI selection. This is disclosed, not misrepresented as CI coverage. The Build 8 workflow itself was not edited. GitHub PR CI status must be checked at the PR head separately.

## Not verified / deliberate omissions

No geological learning or hidden physical truth, expected-value calibration, actual monetary success realization, market pricing, bank lending, contracts, recurring attempts, any motive beyond monetary expected value, multi-sponsor ownership, external persistence, or independent Earth data coupling is proven. The funds here are genuine **in-memory ledger** transfers but not real-world financial flows.

The later governed World Authority join must explicitly admit and carry **receipts for computed priorities**, linking every priority to admitted observation IDs and Bayesian update records, authored project success values and costs, sponsor hurdle and the deterministic EV/rank derivation. Today's in-memory snapshot has visible source labels **but not governed admission receipts** for the computed ranks. This experiment does not create a receipt system or bypass that future requirement.

**Stopping point:** PR C only; do not merge without kT approval; no follow-on edits after opening without first asking kT.
