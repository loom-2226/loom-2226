# Build 8 Experiment A: what changes relative to Build 7 (2026)

Status: research/experimental result, non-qualified. Inputs: promoted Earth v4 80-country 2026 investment capacities, existing Build 7 `ProspectingScenario`, unchanged `derive_mobilization` and 2-unit prospecting required capital. Zero strategic pressure. The activated counterfactual uses commercial opportunity `1` for every country; the negative control uses opportunity `0` and yields zero mobilization for every country. Values below are MODEL_CURRENCY, not national budgets or free Sponsor cash.

| Country | Activated mobilization |
|---|---:|
| CHN | 7.692996779240421 |
| USA | 4.958025335469291 |
| JPN | 1.325135751324722 |
| IND | 1.1702166812795935 |
| DEU | 0.7486920318216503 |
| GBR | 0.6353770659068336 |
| FRA | 0.604042274190448 |
| KOR | 0.5486383629459968 |
| ITA | 0.4465911635391386 |
| CAN | 0.43325254053696594 |

All 80 total: `25.10396510558080532339`. Top-five share: `0.6331695615527318328003093787`; USA share: `0.1974996903723023291090529133`. **Only CHN and USA have individually mobilized at least 2** (the unchanged Build 7 prospecting project capital requirement). This is an *affordability counterfactual*, not an actual country investment or financing decision.

## Causal comparison and stop point

Build 7 already provides real Sponsor decisions, project initiation, commitments, disbursements, finite capital, and persistent replay. Build 8 has so far added 80 country-specific capital inputs and 2026 persisted country mobilization, **but has not changed Sponsor project outcomes**. The Build 8 country pools are not currently sources of Sponsor spendable financing. The existing Build 7 Sponsor continues to read its own funds. The observation that only two country pools independently exceed the project-cost threshold is new, but cannot be interpreted as a country investment choice.

**Do not implement another Sponsor/finance subsystem or repeat Build 7 qualification.** The next worthwhile experiment must test one explicit country-to-existing-Sponsor allocation assumption (or an existing supported allocation path), and compare actual project choices and resulting balances with the Build 7 control. If the allocation assumption is arbitrary, report the scenario dependence rather than claiming emergent behavior. The purpose is a changed simulated-world outcome, not plumbing for its own sake.
