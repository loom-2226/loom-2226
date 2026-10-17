# Solar Reach Executor-first: public body selection correction

**NONCANON / TEST_ONLY / in-memory. No physical mission, hidden WORLD, or DB.**

Authored cast SHA-256: `8c67e088fbd4eb3336d31c4dcdc97d28d548533cf8f69467851e5b00fa8674ee`.
Resolved public identity catalog: 110.
Study eligibility: determined by pinned Build 7 public eligibility and accessibility records, not constructed WORLD truth.
Each Sponsor scores every study-eligible identity every year of the authored full clock.
Economic value is explicitly synthetic, derived from authored seeded Sponsor subjective valuations; not sourced physical value.
Reach is a public accessibility status mapped to an authored penalty, not trajectory or cost data.
All initial actor values, service assumptions, income, outcomes, source pins, inherited values, and effective parameters appear in `solar_reach_cast.json` and fully in `SOLAR_REACH_EXECUTOR_SPIKE_REPORT.json`.

## Complete measured contracts

| Cast | Year | Body (CHOICE, not cast target) | Sponsor | Executor | TEST_ONLY outcome | Paid model currency |
|---|---:|---|---|---|---|---:|
| LONG | 2026 | VESTA | ESA | Thales Alenia Space | DELIVERED | 4.560000 |
| LONG | 2026 | STEINS | NASA | Northrop Grumman | FAILED | 5.700000 |
| LONG | 2027 | EROS | ESA | Thales Alenia Space | DELIVERED | 4.545455 |
| LONG | 2027 | CHARON | NASA | Airbus Defence and Space | DELIVERED | 5.928000 |
| LONG | 2028 | MARS | ESA | Thales Alenia Space | DELIVERED | 4.533333 |
| LONG | 2028 | NEREID | NASA | Airbus Defence and Space | DELIVERED | 5.909091 |
| LONG | 2029 | IAPETUS | ESA | Thales Alenia Space | DELIVERED | 4.523077 |
| SMALL | 2026 | STEINS | NASA | Thales Alenia Space | FAILED | 4.560000 |
| SMALL | 2027 | CHARON | NASA | Northrop Grumman | DELIVERED | 5.700000 |
| SMALL | 2028 | NEREID | NASA | Northrop Grumman | DELIVERED | 5.681818 |

## Identity, conservation and replay

| Cast | Run identity | Replay SHA256 | Evolving beliefs SHA256 | Number of exact replays | Opening/closing money |
|---|---|---|---|---:|---|
| LONG | `8cb06860354ff4dd89e1e87400d945b42673448f51a5919e18b6169fc3cce03b` | `68820a082e2757cb17226f9ec37874ef6103aebc5ed0615b7fb02c260642de32` | `f4de36ee34d3c1cf0781316e485425172edfa8c9887b16ab771ec8fd88ae6a78` | 2 | 74 / 74.000000 |
| SMALL | `0b303e2eff4b671712fa5d984d6a0d720a2107d8185ff541015f2a01b8c67240` | `843db4fa58663bdc5b28e3a0469e814814a6a2ebb299ce2a1095aff5791a0538` | `3dd0571106ec1b7fb67bdaa68385d7e39690fb560722a590ebf64196769b0901` | 2 | 36 / 36.000000 |

All available public identity rows remain visible even for ineligible identities.
All years are included; annual money is conserved. The synthetic outcomes are host-only until delivery and do not appear in the Executor bidding function.

## Body-choice controls

1. Suppress whichever body the Sponsor actually selected: a different source-eligible body is chosen, without deleting the identity from the visible catalog.
2. Change only its subjective value: a different body is chosen.
3. Change only its authored reach penalty: a different body is chosen.
4. Add a Sponsor from the longer cast with a different authored value seed: it targets a different body.
5. Vary executor capacity, margin, price belief, reliability prior or sponsor funding: all five materially change award/bid behavior, and the run identity and replay hash.
6. Change the host-only TEST_ONLY failure to success: the original bidder returns for a later bid rather than declining on reliability.

**8/8 focused tests PASS**, including full catalog-clock/replay and source-pin tamper checks.

## Limits

The public Build 7 eligibility list classifies analytical-study candidates, not genuine flight capability. The existing 110 public identities are not 110 valid study sites.
The seeded Sponsor valuations are explicit TEST_ONLY subjective assumptions, not measured scientific/economic values. No numerical travel prices by body/year are available from the selected sources.
No new activity is generated after the cast spends its budget. The complete clock still advances, but periods without demand correctly produce no contracts.
The removal test dynamically suppresses the *chosen body*. Since Ceres is no longer the initial winner, removing Ceres specifically is not a valid winner-switch test for this baseline.

Branch remains local and draft PR remains unopened. PRs #423 and #424 are untouched.
