# MVP Abstraction Register — Candidate 0.2

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
| FINANCING_AUTHORIZATION_v0 | MVP abstraction | Earth-side institutional authorization of financing claims without pretending that GFCF is cash | commitment/disbursement/expenditure separation; explicit accounts/counterparties; lineage; many-agent compatibility | savings model, bank balance sheet, deposits, credit creation, fiscal capacity, or cash derived from GFCF | explicit macro-financial subsystem is introduced |
| EARTH_FCF_RESOURCE_PROXY_v0 | MVP abstraction | Bound otherwise-unmodeled Earth claims for offworld capital formation using an authored fraction of reference fixed-capital-formation scale | supplier/resource constraint remains separate from financing constraint and displacement; parameter lineage | empirical capital-goods supply capacity, industrial-output measure, financing capacity, saving or liquidity | industrial/supply capacity model becomes available or materially changes outcomes |
| EARTH_FCF_DISPLACEMENT_v0 | MVP abstraction | Apply conservative Earth realized-capital-formation displacement from qualifying Earth-supplied offworld expenditure | reference/realized separation; explicit lambda; no silent post-2060 refill | economic identity or empirical estimate of displacement | saving/consumption/fiscal/credit/trade/price/idle-capacity responses are modeled |
| MVP_EXPLORATION_ACCOUNTING_v0 | MVP abstraction | Preserve exploration spend as exploration WIP and resolve separately from productive mining capital | cost separate from hidden truth; observations/beliefs separate; write-off path | assertion that selected successful-efforts/full-cost convention is universal national-accounting truth | formal accounting boundary or intangible-asset fidelity becomes material |

## Superseded entry

MVP_CAPITAL_ACCESS_v0 is superseded by FINANCING_AUTHORIZATION_v0 plus EARTH_FCF_RESOURCE_PROXY_v0 and EARTH_FCF_DISPLACEMENT_v0.

Earth INVESTMENT_REAL_PROXY / reference FCF is not actor cash and is not a standing financing pool.

## Generic capital-formation rule

The canonical simulation primitive is location-neutral FIXED_CAPITAL_FORMATION. Formal offworld GFCF is deferred until a governed accounting-boundary/residency contract exists.

Financing origin, supplier location, asset location and owner domicile are separate dimensions.

## Scenario truth is not registered here

NULL/SPARSE/RICH hidden resource quantities are scenario-world stipulations or later generator-derived scenario propositions. They are not placeholders and are not MVP abstractions.

## Unknown is not a placeholder

Missing or unknown evidence remains UNKNOWN/BLOCKED. This register cannot be used to fabricate a value merely because a downstream process wants one.

## Change rule

Replacing an abstraction does not authorize changing its public semantics. If replacement requires a semantic/interface change, Phase 3B/contract impact must be assessed explicitly.
