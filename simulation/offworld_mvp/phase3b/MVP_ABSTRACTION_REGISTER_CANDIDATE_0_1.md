# MVP Abstraction Register — Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN REGISTER
**Scope:** Offworld MVP Phase 3B
**Rule:** Simplify the subsystem, not the semantics.

This register names deliberate MVP abstractions and deferred subsystem stubs. It does not authorize numerical parameter values.

| ID | Category | Temporary role | Must preserve | Explicitly not | Revisit trigger |
|---|---|---|---|---|---|
| MVP_TRANSPORT_v0 | MVP abstraction | Return transport cost, time, energy, loss risk and capacity for an origin/destination/time/technology relation | distinct transport dimensions; route dependence; technology dependence where used; deterministic replay | detailed orbital logistics or mission planning | transport fidelity materially changes project choice, capacity, timing, or feasibility |
| EARTH_MARKET_v0 | deferred subsystem stub | External buyer/seller/clearing counterparty for exogenous MVP price/demand | double-sided accounting; demand constraint; counterparty identity | endogenous commodity market or unlimited magic buyer | multiple sellers/buyers, endogenous prices, market power, or Earth feedback required |
| MVP_COLONY_OPERATIONS_v0 | MVP abstraction | Transparent colony stock-flow operating rules | stocks/flows, operating needs, imports, subsidy, productive capacity, conservation | independent macroeconomy or Cobb-Douglas economy | settlement diversification/economic autonomy becomes causal |
| MVP_OBSERVATION_MODEL_v0 | MVP abstraction | Remote/surface prospecting observation channel | hidden-world firewall; noise; provenance; keyed randomness; agent-specific information | instrument-grade sensing physics | observation technology/instrument design becomes decision-critical |
| MVP_PROJECT_COST_v0 | MVP abstraction | Simplified exploration/development/extraction/energy cost rules | explicit cost components; technology/transport dependencies where relevant; accounting conservation | mine-engineering estimate or empirical forecast | engineering detail changes feasibility/ranking or physical constraints |
| MVP_PRICE_DEMAND_v0 | MVP abstraction | Exogenous authorized price/demand series consumed by EARTH_MARKET_v0 | versioning; units; demand ceiling; scenario/model lineage | prediction of future market prices | endogenous market behavior or feedback required |
| MVP_CAPITAL_ACCESS_v0 | deferred design boundary | Future governed bridge from Earth investment proxy scale to actor-accessible financing | source/counterparty, displacement/additionality, conservation, timing, lineage | treating Earth INVESTMENT_REAL_PROXY as cash | **owner decision required before any financing is instantiated** |

## Scenario truth is not registered here

NULL/SPARSE/RICH hidden resource quantities are scenario-world stipulations or later generator-derived scenario propositions. They are not placeholders and are not MVP abstractions.

## Unknown is not a placeholder

Missing or unknown evidence remains UNKNOWN/BLOCKED. This register cannot be used to fabricate a value merely because a downstream process wants one.

## Change rule

Replacing an abstraction does not authorize changing its public semantics. If replacement requires a semantic/interface change, Phase 3B/contract impact must be assessed explicitly.
