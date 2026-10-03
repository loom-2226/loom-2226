# Phase 3B Financing and Recursive Fixed-Capital Formation — Finalized Design Candidate 0.1

**Status:** PHASE 3B DESIGN CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Branch:** offworld-mvp-phase3
**Implementation authority:** NOT YET GRANTED

## 1. Decision

Phase 3B adopts a location-neutral financing and fixed-capital-formation architecture. Financing is not fixed-capital formation. GFCF is not cash.

Economic recursion: economic state -> financing decision -> commitment -> disbursement -> expenditure -> fixed-capital formation / WIP -> productive asset -> production -> revenue/surplus -> return, retention or reinvestment -> subsequent financing decisions.

The same semantics must support Earth-to-offworld, offworld-to-Earth, local-to-local and offworld-to-offworld flows.

## 2. Generic fixed-capital-formation primitive

The simulation primitive is FixedCapitalFormationEvent, not an Earth-specific GFCF field. It records event/run/time, project, asset, owners, financing-origin nodes, supplier node, asset node, qualifying expenditure, asset class and lineage.

financing_origin, supplier_location, asset_location and owner_domicile are distinct dimensions. They may coincide, but no rule may assume that they do.

For node n and time t, FCF_realized(n,t) is the sum of qualifying fixed-capital-formation events whose asset node is n. Productive capital rolls forward from prior capital, depreciation, commissioned FCF and write-offs. WIP and exploration/knowledge assets remain separately accounted until their governing transitions occur.

## 3. GFCF semantics

LOOM Earth retains immutable reference capital-formation state under the Earth Reference Contract Candidate. Earth has FCF_reference, FCF_realized and an explicit delta. Existing Earth INVESTMENT_REAL_PROXY is a modeled productive-capital-formation flow in constant-2015-USD-scale proxy units, not liquid financing.

Offworld nodes begin with realized fixed-capital formation only. Formal national-accounts GFCF is not automatically created merely because assets exist there. A later governed accounting-boundary/residency contract is required. Until then the canonical generic concept is FIXED_CAPITAL_FORMATION.

## 4. Financing layer

A financing agent allocates claims on economic resources. Required stages remain distinct: FinancingDecision != Commitment != Disbursement != Expenditure != WIP != Capitalization != ProductiveAsset.

Earth-side financing may use FINANCING_AUTHORIZATION as an explicit MVP abstraction standing in for unmodeled savings, budgets, deposits, securities markets, credit creation and related institutions. It must never be described as money derived from GFCF. Offworld local financing funded by recorded balances or retained surplus does not require that Earth abstraction.

## 5. Earth resource/allocation proxy

Reference Earth GFCF does not empirically measure capital-goods supply capacity. For the MVP, an authored proxy constraint may use reference FCF/GFCF scale to bound otherwise unmodeled Earth claims for offworld capital formation.

QualifyingEarthSuppliedExpenditure(c,t) <= a_c * FCF_reference(c,t).

a_c is an authored parameter. This is an MVP scale/resource-allocation abstraction, not a measurement of saving, liquidity, fiscal capacity, banking capacity, industrial output, capital-goods production capacity or financing capacity. Future industrial/supply models may replace the proxy without changing the financing, transaction or FCF ontology.

## 6. Earth displacement

For the MVP, Delta_FCF_terr(c,t) = -lambda * QualifyingEarthSuppliedExpenditure(c,t), with lambda_MVP = 1.

lambda_MVP = 1 is a conservative displacement abstraction and authored parameter, not an economic identity. Future models may make displacement endogenous through saving, consumption, fiscal, credit, trade, price, idle-capacity, production and foreign-capital responses. The post-2060 LOOM Earth investment rule must not silently refill modeled displacement when two-way coupling is activated.

## 7. Transaction locality

Every account has an economic node. Transactions preserve source and destination accounts/locations and, where applicable, supplier and asset locations. This supports Earth -> offworld financing, offworld -> Earth returns, local -> local reinvestment, offworld A -> offworld B, and offworld financing -> Earth supplier -> offworld asset without schema change.

A fixed asset is counted at its asset location. Financing origin, supplier production and ownership do not clone the asset into another node's productive capital.

## 8. Recursive surplus disposition

Operating surplus has explicit disposition: RETURN_TO_EARTH, LOCAL_RETENTION, LOCAL_REINVESTMENT, OTHER_OFFWORLD_INVESTMENT, or RESERVE. No disposition is implied merely by ownership.

Local retained earnings and reinvestment may finance subsequent projects. Thus K_n -> Production_n -> Revenue/Surplus_n -> Financing_n -> Expenditure_n -> FCF_n -> K_n+1 is an endogenous recursion. Otherwise identical resource projects may generate divergent civilization trajectories because one exports surplus while another reinvests locally.

## 9. Economic maturity remains multidimensional

Report FinanceSelf, SupplySelf, ServiceSelf, OwnSelf, ExternalFinanceShare, EarthReturnShare and LocalReinvestmentShare without initially turning them into thresholds. A node may be locally financed but import capital goods, locally supplied but externally owned, or locally serviced while financially dependent. No single quantity is authorized as a colony/maturity threshold in Phase 3B.

## 10. Exploration

Exploration expenditure is not productive mining capital. Preserve ExplorationSpend -> EXPLORATION_WIP, resolving to a separately typed knowledge/exploration asset or write-off under the selected accounting abstraction. Accounts record cost, not hidden resource truth. Observations and beliefs remain in their epistemic planes. Successful-efforts versus full-cost treatment remains an explicit MVP accounting choice.

## 11. Many-agent requirement

All relationships are many-to-many from the beginning: multiple sponsors and financiers per project, one financier funding many projects, competing projects, syndication, heterogeneous beliefs/policies, Earth or offworld financier domicile, cross-node suppliers, ownership and returns. A tiny first fixture is permitted; singleton implementation assumptions are not.

## 12. Conservation and accounting requirements

At minimum: double-sided transaction conservation; account roll-forward; commitment/disbursement/lapse reconciliation; persistent project cash; qualifying expenditure rather than commitment/disbursement drives FCF/resource accounting; separate WIP/exploration/knowledge/productive-asset roll-forwards; every revenue has a payer; every productive asset has an explicit capitalization path; ownership reconciles; one physical asset cannot appear in productive capital at multiple locations; return/reinvestment lineage is preserved; Earth reference is immutable; realized Earth/offworld state remains separately queryable; hidden scenario truth cannot enter financing decisions except through admissible information; stochastic decisions remain replayable.

## 13. Required four-route trace test

Before Phase 3B closes, the same ontology must trace: (A) Earth-financed, Earth-supplied equipment installed offworld; (B) locally earned offworld surplus financing local capital; (C) offworld financing paying an Earth supplier for an offworld asset; and (D) offworld node A financing and/or supplying capital formation at offworld node B. Special-case schemas fail the test.

## 14. First recursive-economy falsification experiment

Use identical hidden universe, seed, starting agents, technology and physical parameters. Compare ENCLAVE policy, where surplus after reserves is predominantly returned externally, against SETTLEMENT policy, where eligible surplus may be reinvested in local productive/service/supply assets when projects clear the declared decision rule.

Run long enough to observe recursion, initially 50 years unless fixture design justifies otherwise. Compare productive capital, realized node FCF, local/external financing, local/imported supply, service self-sufficiency, ownership, Earth returns, stranded assets and population-supporting capacity where modeled. If trajectories fail to differ when reinvestment opportunities exist, the recursive mechanism has failed its intended test.

## 15. Classification firewall

Accounting/physical identities include balance roll-forwards, counterparty equality, ownership reconciliation and stock depletion. LOOM model mechanics include event ordering, capitalization, production/capacity rules, purchasing rules, agent decision interfaces and causal ledger. MVP abstractions include FINANCING_AUTHORIZATION, the GFCF-scaled Earth resource proxy, lambda displacement, simplified prices/markets and the selected exploration accounting convention. Authored parameters include allocation fractions, lambda, hurdle rates, depreciation, salvage, prices, capacities, service requirements, detection/noise parameters and policy overrides.

An abstraction may not silently acquire empirical status because repeated runs depend on it.

## 16. Supersession and integration

This candidate supersedes the earlier conceptual MVP_CAPITAL_ACCESS_v0 idea in which Earth investment risked being treated as an accessible financing pool.

Correct relation: Earth reference economic scale -> explicit financing/resource-allocation abstractions -> agent financing decisions -> actual expenditure -> location-specific fixed-capital formation -> productive capital -> production/surplus -> recursive financing.

The Phase 3B state model and abstraction register must be updated to reflect this architecture before Phase 3B closure.

## 17. Governance status

This document finalizes the financing/recursive-capital-formation design direction for Phase 3B but does not release Authority Contract v1 and does not grant production implementation authority. All new semantics remain PRE-CONTRACT / SINGLE-AUTHORITY. The participating Earth economy remains UNSELECTED. No legacy CIVPROP country actor receives default status.