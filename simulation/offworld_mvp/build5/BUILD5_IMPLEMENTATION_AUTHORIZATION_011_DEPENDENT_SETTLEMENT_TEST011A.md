# Build 5 Implementation Authorization 011 — Dependent Settlement Formation Test 011A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Project-owner authorization:** “Go 1 - there is a research doc in case you're interested ;)”
**FRD mutation:** NOT AUTHORIZED FOR THIS TEST
**Parent:** Build 5 Test 010A surplus/return/reinvestment/distribution structural pass

## Purpose

Close the settlement component of the Offworld MVP success loop at the minimum causal resolution justified by the current FRD and parked research.

Authorized causal slice:

successful project -> local reinvestment -> installed settlement infrastructure -> derived EXTRACTION_ENCLAVE -> bounded public settlement-support decision -> conserved Earth-to-offworld migration -> external support -> derived DEPENDENT_SETTLEMENT.

A NULL/failure history shall not acquire settlement merely because a productive facility was commissioned earlier.

## Research intake standing

Advisory research inspected read-only from loom-2226/loom-research-lab at commit 0057937bdbf9732e235a7d8d718d2466898d8740:

- projects/offworld_population_labour_migration/RESEARCH_BRIEF_v0.1.md
- projects/offworld_settlement_infrastructure_operations/RESEARCH_BRIEF_v0.1.md

Classification: RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION.

Useful research principles admitted for Test 011A:

1. settlement remains an AGGREGATE, not a universal decision-making Agent;
2. population remains aggregate stock-flow state;
3. migration changes location, not total population;
4. early migration may remain a direct deterministic ledger transfer when transport is not yet the binding causal question;
5. installed settlement infrastructure creates capacity/opportunity but does not itself create population;
6. stage labels summarize achieved realized state and may not grant infrastructure, service, population or productive capability;
7. Level-A infrastructure-stock representation is acceptable when service reliability cannot change the bounded experiment;
8. explicit people/households/labour-market machinery is not required for this MVP closure.

No research proposal becomes runtime, FRD or empirical authority.

## Parked research

Test 011A does not authorize individual Human Agents, households, cohorts, fertility/mortality, skill pools, labour-market matching, rotational workforce, in-transit population, detailed passenger transport, power/life-support/water service networks, maintenance/reliability models, infrastructure-operator Agents, endogenous migration choice, detailed habitat engineering, DIVERSIFYING_SETTLEMENT, or HANDOFF_CANDIDATE mechanics.

## Existing local reinvestment is the capital source

Test 010A already makes a bounded sponsor decision to classify 10 MODEL_CURRENCY as local reinvestment in RICH and SPARSE.

Test 011A shall consume that already-realized local-reinvestment balance through a separately declared Test-only settlement-infrastructure plan.

The infrastructure SYSTEM does not re-decide the sponsor's reinvestment category.

NULL receives no Test 010A local reinvestment and therefore cannot execute the same infrastructure plan.

## Settlement infrastructure plan

Introduce an immutable SettlementInfrastructurePlan containing at minimum plan id, year, node id, source local-reinvestment account, local supplier account, infrastructure cost, habitat capacity in people-equivalent units, source/rationale reference, epistemic standing, and version.

Test-only fixture:

- infrastructure cost = 10 MODEL_CURRENCY;
- habitat capacity = 10 PEOPLE_EQUIVALENT;
- source = local_reinvest_funds;
- supplier = offworld local settlement supplier.

Cost and capacity are structural test fixtures only. They are not engineering estimates or empirical habitat costs.

## Infrastructure execution

A deterministic SYSTEM may execute the immutable plan only when source and supplier accounts are at the target offworld node, sufficient realized source balance exists, the plan has not already executed, and cost/capacity are valid.

Execution shall transfer the cost to the local supplier, increase realized colony infrastructure stock by the cost, increase realized habitat capacity by the declared people-equivalent capacity, record immutable realization and causal lineage, and leave resource remaining and population unchanged.

If funds are insufficient, no infrastructure may be created.

## Settlement remains an AGGREGATE

The colony/settlement does not become an Agent. The public institution remains the decision-bearing Agent for bounded migration support. Infrastructure realization and stage derivation remain SYSTEM mechanisms.

## Colony state extension

Test 011A may extend ColonyState with habitat_capacity.

This is realized aggregate state. It does not imply service reliability, occupancy quality, life-support engineering or permanent habitability outside the structural fixture.

## Derived colony stage rule

Introduce a versioned deterministic SettlementStageRule.

Earned stages in Test 011A:

- PROSPECTING: no commissioned productive capacity exists.
- EXTRACTION_ENCLAVE: commissioned productive capacity exists, but no resident population is present.
- DEPENDENT_SETTLEMENT: commissioned productive capacity > 0; resident population > 0; infrastructure stock > 0; habitat capacity >= resident population; explicit external subsidy/support > 0.

DIVERSIFYING_SETTLEMENT and HANDOFF_CANDIDATE are not earned.

The stage rule reads realized state only. It creates no capability, money, infrastructure or people.

## Colony productive-state synchronization

The settlement SYSTEM may derive aggregate productive state from already-realized kernel assets:

- productive_capital = current productive-asset book value at the node;
- production_capacity = current productive-asset capacity at the node.

This is aggregation, not capital creation.

## Public settlement-support Agent

The existing generic PUBLIC institutional Agent receives bounded settlement-support authority through the established AgentState -> DecisionSnapshot -> isolated policy -> immutable Decision -> scheduled SYSTEM consequence architecture.

Additional Test 011A public capabilities: MIGRATE and SETTLEMENT_SUPPORT.
Additional public objective: PUBLIC_SETTLEMENT.

No new public institution class is created.

## Public settlement-support request/decision

Introduce immutable SettlementSupportRequest and SettlementSupportDecision.

Required admitted facts:

- settlement.STAGE
- settlement.HABITAT_HEADROOM
- settlement.REQUESTED_RESIDENTS
- population.EARTH_AVAILABLE
- settlement.PUBLIC_SUPPORT_COST

Supported outcomes: AUTHORIZE, DEFER, BLOCKED_UNKNOWN.

## Bounded public policy

The policy contains no arbitrary probability threshold.

It may AUTHORIZE only when Agent kind is PUBLIC; objective includes PUBLIC_SETTLEMENT; capabilities include MIGRATE and SETTLEMENT_SUPPORT; current derived stage is EXTRACTION_ENCLAVE; requested residents > 0; habitat headroom >= requested residents; Earth population >= requested residents; and public support cost is nonnegative and affordable.

Otherwise it DEFERs or BLOCKED_UNKNOWN as appropriate.

## Public support and migration execution

For an authorized request, a later SYSTEM shall transfer declared public support from public_funds to an offworld settlement-support account, increase ColonyState.external_subsidy by the same amount, migrate exactly the authorized resident count from Earth to the offworld node, preserve total population exactly, and recompute settlement stage.

The decision itself mutates nothing.

## Structural migration fixture

Test-only request:

- requested residents = 10;
- public support = 10 MODEL_CURRENCY.

The resident request is bounded by habitat capacity 10. This is not a demographic forecast, optimal settlement size or implied transport capacity.

## Qualification

RICH and SPARSE receive 10 local-reinvestment cash from Test 010A and may execute the habitat plan. After infrastructure they derive EXTRACTION_ENCLAVE. With the same admitted public support state they may then authorize and migrate 10 residents, preserve total population, receive explicit external support and derive DEPENDENT_SETTLEMENT.

NULL has local reinvestment funds = 0 after Test 010A. It cannot create infrastructure without funds, habitat headroom remains zero, the public support policy DEFERs, no migration or subsidy occurs, and NULL may not reach DEPENDENT_SETTLEMENT. A commissioned but economically unsuccessful facility may remain descriptively EXTRACTION_ENCLAVE; that label does not imply economic viability or population.

## Conservation and falsification

Test 011A shall verify infrastructure cannot appear without realized funding; duplicate plan execution fails; invalid plan values and wrong-node linkages fail; infrastructure realization changes no population/resource stock; stage labels grant nothing; DEPENDENT_SETTLEMENT cannot occur with zero residents, inadequate habitat capacity or absent external support; policy evaluation mutates nothing; UNKNOWN headroom blocks before worker; missing capabilities, inadequate public funds, excessive requested migration and insufficient Earth population defer/reject; migration cannot exceed authorization; population totals reconcile; NULL cannot bootstrap settlement from absent cash; colony stage/habitat/population tampering is epoch-detectable; A1-A9 pass; deterministic replay is exact.

## Transport boundary

Test 011A deliberately does not implement the FRD transport relationship.

The direct migration ledger is retained only because transport capacity/time is not the discriminating causal question in this settlement-formation test. Minimal transport/technology gating remains a separate later MVP closure slice.

## FRD and epistemic standing

The FRD is not modified by this authorization.

Passing Test 011A establishes structural dependent-settlement formation only. It does not establish empirical habitat cost/capacity, demographic plausibility, labour sufficiency, infrastructure reliability, physical passenger transport, autonomous settlement economy, long-term survival or settlement-growth forecasts.
