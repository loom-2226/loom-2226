# Solar Reach Executor-first spike: measured outcomes

CLASS: BUILD8 NONCANON TEST_ONLY IN-MEMORY / NOT WORLD TRUTH / NOT GOVERNED QUALIFICATION
BASE: 19377b854c529e74afc61202d9eb2e780c5b4884

Canonical authored cast: solar_reach_cast.json (FULL raw content also reproduced in SOLAR_REACH_EXECUTOR_SPIKE_REPORT.json).
Cast SHA-256: 3d7552398891438cb5d6c1171ebce61c19e203408740b401d72e16b6ca30ef8b
Pinned kernel source tree SHA-256: 549a8bf07adf14bab56fb825aa95d07f7279fa878a750ebd8b506314cb020627
Source pins and all inherited parameter values: see the complete resolved report JSON.

## Two full-catalog, full-clock runs with independent replays

| Cast | Source catalog | Clock | Body-years | Awards | Real kernel transfers | Opening = closing currency | Two replays |
|---|---:|---:|---:|---:|---:|---|---|
| LONG | 110 | 201 | 22110 | 4 | 8 | 74 = 74.00000000000000000000000000 (numeric) | 2 identical SHA256 |

Cast LONG run identity: 0fb7e3eb65aba69c7c4fddcb0013074e11f40f06cddce32d86994c8579a96103
Cast LONG replay SHA-256: e0680645ca636181e96d7c908bc42ed5815d3daab2d4657bdfe3e4b3a1a2c71f
All replay hashes: e0680645ca636181e96d7c908bc42ed5815d3daab2d4657bdfe3e4b3a1a2c71f, e0680645ca636181e96d7c908bc42ed5815d3daab2d4657bdfe3e4b3a1a2c71f, e0680645ca636181e96d7c908bc42ed5815d3daab2d4657bdfe3e4b3a1a2c71f
Annual conservation: True
Years with awards: [2026, 2027, 2029, 2032]

| SMALL | 110 | 201 | 22110 | 2 | 4 | 36 = 36.000 (numeric) | 2 identical SHA256 |

Cast SMALL run identity: 557ccd63bc0788a7d52493c4148a94f45eef311ec3a4e51f608263dd83d581d7
Cast SMALL replay SHA-256: b4770975dc295cd944f87481ef5e90a3718c8fde63586ec63cb8cf806a86fc97
All replay hashes: b4770975dc295cd944f87481ef5e90a3718c8fde63586ec63cb8cf806a86fc97, b4770975dc295cd944f87481ef5e90a3718c8fde63586ec63cb8cf806a86fc97, b4770975dc295cd944f87481ef5e90a3718c8fde63586ec63cb8cf806a86fc97
Annual conservation: True
Years with awards: [2026, 2029]

## Measured small-cast contested contract

| Want | Award | TEST_ONLY delivery outcome |
|---|---|---|
| NASA:CERES:INITIAL | Thales Alenia Space | FAILED |
| NASA:CERES:FOLLOWUP | Northrop Grumman | DELIVERED |

The initial Thales failure increments its own failure count, drops its Beta reliability estimate below its authored hurdle, and Thales DECLINES on the later NASA request. Northrop is subsequently awarded. Both Executors independently BID on the initial request.

## Authored knob mutations with actual decision/ledger effects

| Knob | Original → alternative | New first award | Preferred Executor initial action | Changed replay? |
|---|---|---|---|---|
| capacity | 1 → 0 | Northrop Grumman | DECLINE | True |
| funding | 20 → 3 | NO AWARD | BID | True |
| margin | 0.10 → 0.85 | Northrop Grumman | BID | True |
| price_belief | 10 → 4 | Northrop Grumman | DECLINE | True |
| reliability_prior | 9 → 1 | Northrop Grumman | DECLINE | True |

Margin changes the winning quote even though the higher-priced Executor still BIDs. Funding prevents the award but does not stop eligible Executors from submitting offers. All other sampled knob mutations cause the previously preferred Executor to DECLINE. Every mutation has its own full authored-data digest and run identity.

## Explicit outcome-causality control

Holding the initial Executor-visible snapshot constant and switching the host TEST_ONLY result changes the later winner from Northrop Grumman to Thales Alenia Space. Initial bids are byte-identical under the outcome switch. No real hidden WORLD values are read.

## Long-horizon observation

After 2032 there are no new awards in either cast, through 2226. There are still annual body-year state and conserved account records, but no new demand. This spike does not magically create Box 4, habitation, or continuing economic demand.

## Constraints / not claimed

- No code-defined cap on sponsor, Executor, body or year population. Cast controls actor membership; source identity catalog controls full body population; authored clock is 2026–2226. Full coverage is not permission to claim physical reach.
- Executors are independently deciding Build8-local actors, NOT typed as frozen kernel AgentKind.EXECUTOR (enum absent). Their money/cost are kernel-owned accounts, and their beliefs are Build8-local evolving state included in the initial run identity and all replay hashes.
- Contract payment uses unchanged transfer twice: sponsor cash to Executor supplier account, then Executor account to cost account. Failure receives full up-front payment under explicitly authored TEST_ONLY terms. The cost account remains part of total money conservation.
- No isolated policy worker or governed authorization claimed; this is an in-memory noncanon behavioral spike.
- No separate ledger, database, WORLD state, observations or population. Source pins are checked before each ordinary run. No frozen or WALTER changes.
