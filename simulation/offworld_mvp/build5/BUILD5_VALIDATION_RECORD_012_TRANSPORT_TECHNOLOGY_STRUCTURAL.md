# Build 5 Validation Record 012 — Minimal Transport Relationship + Exogenous Technology Gate Structural Qualification

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED  
**Date:** 2026-10-04  
**Authoritative repository:** `loom-2226/loom-2226`  
**Parent Build 5 branch:** `offworld-mvp-build5-settlement`  
**Parent head:** `768e25e2772e6f56ed4ae4be8d5d133d66c327d4`  
**Implementation branch:** `offworld-mvp-build5-transport-technology`  
**Authorization commit:** `0d8305519cb146bd5c9df019b1eeba70420d7bb9`  
**Candidate executable head:** `40ed51a8cc20ec55712f46b83a157530d3ab9ef5`  
**FRD mutation:** NONE  
**FRD diff from parent:** `0 lines`

## Qualification statement

Build 5 Test 012A structurally earns the minimum transport + exogenous-technology causal slice required by the current Offworld MVP FRD.

The implemented causal contract is:

`exogenous TechnologyCapabilityState -> capability-qualified TransportRelationship -> admitted transport opportunity -> bounded PUBLIC Agent decision -> SYSTEM departure/payment validation -> aggregate in-transit population -> deterministic arrival -> conserved offworld migration -> derived settlement state`.

This qualification does **not** establish empirical 2226 transport performance, technology timing, safety, economics, adoption, logistics-network behavior, or settlement viability.

## Live authority bootstrap

Before authorization or implementation, live GitHub authority was verified.

`loom-2226/loom-2226`:

- branch `offworld-mvp-build5-settlement` was identical to `768e25e2772e6f56ed4ae4be8d5d133d66c327d4`;
- live guiding FRD blob inspected: `1e4ebc11e2fde81f7dad87732bd6d563229ce935`;
- Test 011 validation record was read from live repository state.

`loom-2226/loom-research-lab`:

- `main` was identical to `572f174f8b329ca749fddaf3a3ce492ae97304bc`.

Research remained advisory only.

## Research intake

Read-only research inputs:

- `projects/offworld_transport_energy_logistics/RESEARCH_BRIEF_v0.1.md`;
- `projects/offworld_technology_research_innovation/RESEARCH_BRIEF_v0.1.md`.

Standing:

- RESEARCH;
- NON-CANON;
- NON-RUNTIME;
- NON-AUTHORITATIVE;
- NON-QUALIFICATION;
- PARKED REFERENCE.

The implementation admits only architectural distinctions compatible with the FRD:

- physical feasibility is not transport service;
- transport service is not fleet;
- service capacity is not realized traffic;
- technology capability changes the available service opportunity set;
- technology does not make the Agent act;
- routine transport mechanics remain SYSTEM;
- detailed logistics and endogenous R&D remain parked.

## Technology Timeline disposition

Test 012A does not activate a named Technology Timeline row and does not interpret a calendar date as an automatic unlock.

The test uses explicit Test-only capability identifiers.

Therefore:

`technology date/name != qualified capability != service use != Agent choice != movement != economic success`.

## Earned executable types

Test 012A adds immutable/versioned:

- `TechnologyCapabilityState`;
- `TransportRelationship`;
- `TransportQualificationRecord`;
- `TransportSettlementRequest`;
- `TransportSettlementDecision`;
- `PassengerTransportDepartureRecord`;
- `PassengerTransportArrivalRecord`.

The executable ODD schema registry is reconciled as:

`ODD_SCHEMA_REGISTRY_0_14`.

## Technology state

`TechnologyCapabilityState` declares:

- state identity;
- effective period;
- explicit qualified capability identifiers;
- source/rationale;
- epistemic standing;
- version.

No scalar `tech_level` exists.

Technology-state registration alone changes no population, account balance, resource, project, or settlement stock.

## Transport relationship

`TransportRelationship` is an origin/destination/time service envelope, not a deposit property.

It separately serializes and validates the five controlling FRD dimensions:

- Cost;
- TravelTime;
- Energy;
- LossRisk;
- Capacity.

The implementation additionally carries:

- required capability identifier;
- passenger class;
- source/rationale;
- epistemic standing;
- version.

For Test 012A, Cost is represented as a per-passenger financial charge.

Energy remains a separate declared service requirement and is not silently folded into Cost.

## Qualification gate

A relationship is available only when:

- the relationship exists;
- the technology state exists;
- both are applicable at the requested effective time;
- the relationship's explicit required capability is qualified;
- the registered direction is Earth -> offworld;
- referenced nodes exist and have the expected node kinds.

Technology qualification itself creates no traffic or financial consequence.

## Agent/system boundary

The existing PUBLIC institutional Agent remains the bounded decision-maker.

No new:

- transport Agent;
- carrier Agent;
- fleet Agent;
- technology Agent;
- settlement Agent

was created.

The PUBLIC Agent evaluates only admitted settlement, technology, and transport facts through the existing snapshot -> isolated policy -> immutable decision architecture.

SYSTEM code validates and executes authorized consequences.

## Transport-aware decision contract

Required admitted facts are:

- `settlement.STAGE`;
- `settlement.HABITAT_HEADROOM`;
- `settlement.REQUESTED_RESIDENTS`;
- `population.EARTH_AVAILABLE`;
- `settlement.PUBLIC_SUPPORT_COST`;
- `transport.AVAILABLE`;
- `transport.RELATIONSHIP_ID`;
- `technology.STATE_ID`;
- `transport.CAPACITY`;
- `transport.COST_PER_PASSENGER`;
- `transport.TRAVEL_TIME`;
- `transport.ENERGY_PER_PASSENGER`;
- `transport.LOSS_RISK`.

Any UNKNOWN required fact propagates to `BLOCKED_UNKNOWN` before policy-worker execution.

Current policy identity:

`PUBLIC_SETTLEMENT_TRANSPORT_V1:0.1:18e73a25d3e65dd99cc7e671795822c150b567359b592930103f3678debc71ef`.

Current contract SHA-256:

`cad5d6416f25aa19b473a2d2d589aa2a898d6043f6ad8ed80042662cf0790b66`.

## Capacity policy

The first MVP transport slice uses:

`ALL_OR_DEFER`.

If requested residents exceed admitted route capacity, no silent truncation occurs and no excess passenger movement occurs.

A future partial-allocation policy is not implied.

## Financial mechanics

Settlement support and transport payment remain distinct.

Successful departure may emit:

- `PUBLIC_SUBSIDY` from public funds to the offworld settlement-support account;
- `TRANSPORT_PAYMENT` from public funds to the Earth-side transport provider account.

The transport charge is:

`authorized passengers * Cost per passenger`.

Affordability is checked against:

`settlement support cost + transport charge`.

No transport payment is hidden inside settlement subsidy.

## Travel time and in-transit population

TravelTime has executable causal meaning.

At departure:

- Earth population decreases by the authorized passenger count;
- an aggregate passenger batch enters `PopulationLedger.in_transit`;
- offworld resident population does not yet increase;
- total population remains exactly conserved.

At deterministic arrival:

- the exact in-transit batch is removed;
- offworld and colony resident population increase by the same count;
- total population remains exactly conserved;
- settlement stage is re-derived from realized state.

This adds no ship, fleet, trajectory, launch-window, life-support, or orbital-propagation simulation.

## LossRisk boundary

LossRisk remains a separate service dimension.

The structural qualification fixture uses:

`LossRisk = 0`.

Nonzero loss risk is explicitly deferred with `LOSS_RISK_UNSUPPORTED`.

This is a Test-only structural boundary, not an empirical passenger-safety claim.

## Test-only baseline fixture

All numeric values below are:

`TEST_ONLY / NOT_CALIBRATED / NOT_POLICY_BASELINE`.

Baseline passenger capability:

`PASSENGER_TRANSFER_BASELINE_TEST012A`.

Baseline Earth -> `OFF:T1` relationship:

- Cost = 2 MODEL_CURRENCY per passenger;
- TravelTime = 1 SIM_TIME;
- Energy = 3 MODEL_ENERGY per passenger;
- LossRisk = 0;
- Capacity = 10 PEOPLE_EQUIVALENT.

Settlement request:

- requested residents = 10;
- settlement support = 10 MODEL_CURRENCY.

Successful baseline transport therefore separately charges:

- settlement support = 10;
- passenger transport = 20;
- combined public affordability requirement = 30.

These values are arithmetic fixtures only.

## Improved-technology structural case

A second explicit capability/service combination is tested with changed service characteristics.

Registration of improved technology/service state:

- changes the opportunity set;
- does not itself create a decision;
- does not move population;
- does not mutate account balances.

No endogenous R&D, maturation, learning, diffusion, or automatic Timeline unlock is introduced.

## RICH / SPARSE / NULL matrix

### RICH

With earned Test 010 local reinvestment and Test 011 habitat infrastructure:

- transport relationship qualifies;
- PUBLIC Agent authorizes 10 residents;
- 10 settlement support is separately paid;
- 20 transport cost is separately paid;
- 10 residents depart Earth into aggregate transit;
- no residents appear offworld before arrival;
- all 10 arrive at the deterministic arrival time;
- total population remains 1000;
- final offworld population is 10;
- final in-transit population is zero;
- settlement derives `DEPENDENT_SETTLEMENT`.

### SPARSE

With the same admitted settlement and transport opportunity state:

- the same bounded transport decision mechanics apply;
- the same authorized passenger/support/transport quantities result;
- hidden resource quantity does not alter the transport decision;
- arrival conserves population;
- settlement derives `DEPENDENT_SETTLEMENT`.

### NULL

Transport availability does not bootstrap settlement.

Inherited absence of realized local-reinvestment-funded habitat leaves habitat headroom at zero.

Therefore:

- PUBLIC policy defers on the settlement prerequisite;
- no departure occurs;
- no transport payment occurs;
- no settlement subsidy occurs;
- Earth population remains unchanged;
- offworld resident population remains zero;
- `DEPENDENT_SETTLEMENT` is not reached.

Thus:

`transport availability != settlement`.

## Hostile / falsification coverage

Test 012A verifies:

1. missing required technology capability blocks service use;
2. technology/service registration alone mutates no population or accounts;
3. missing transport relationship produces UNKNOWN required service dimensions rather than guessed values;
4. reverse Earth/offworld linkage is rejected;
5. requested passengers above capacity are all-or-defer;
6. inadequate combined support + transport funding defers;
7. nonzero loss risk is explicitly unsupported rather than silently simulated;
8. policy evaluation alone mutates no world state;
9. technology/service improvement alone mutates no world state;
10. Cost, TravelTime, Energy, LossRisk and Capacity remain separately admitted/serialized;
11. hidden resource truth cannot change a decision when admitted Agent/transport state is identical;
12. support and transport payments use separate transaction purposes;
13. departure preserves total population while creating explicit in-transit population;
14. arrival preserves total population while consuming the exact in-transit batch;
15. duplicate departure is rejected;
16. duplicate arrival is rejected;
17. raw technology-state tampering is decision-epoch detectable;
18. raw transport-relationship tampering is decision-epoch detectable;
19. raw pending in-transit population tampering is decision-epoch detectable;
20. RICH/SPARSE/NULL transport epochs preserve A1-A9;
21. deterministic replay is exact.

## Focused qualification

Command:

`python3 -m unittest tests.test_odd_schema_drift tests.test_build5_transport_technology`

Result:

- 23 tests executed;
- 23 passed;
- 0 failures;
- 0 errors.

## Full governed regression

Command:

`python3 -m unittest discover -s tests`

At candidate executable head:

`40ed51a8cc20ec55712f46b83a157530d3ab9ef5`

Result:

- 287 tests executed;
- 287 passed;
- 0 failures;
- 0 errors;
- runtime: 420.092 seconds.

This includes all pre-existing governed tests plus the new Test 012A coverage.

## Executable source-tree attestation

At candidate executable head:

`40ed51a8cc20ec55712f46b83a157530d3ab9ef5`

Filesystem executable source-tree SHA-256:

`2aa14a354635b200aef01a57510b6e2d326aae25398cd2edd56a9a99ebf02dfd`.

Git-object reconstructed executable source-tree SHA-256:

`2aa14a354635b200aef01a57510b6e2d326aae25398cd2edd56a9a99ebf02dfd`.

Standing:

`GIT_OBJECT_VERIFIED`.

## Historical Test 011 compatibility

Test 011A's direct aggregate migration remains historical structural machinery for the earlier settlement-only experiment.

Test 012A does not retroactively claim that Test 011A modeled physical transport.

Instead, Test 012A introduces the current transport-gated passenger path while preserving all prior tests.

## FRD standing

The guiding FRD was not modified.

Measured diff from the Test 011 parent:

`FRD_DIFF_LINES=0`.

The executable ODD alone was reconciled for newly executable schema and enum semantics.

## Explicitly not earned

Test 012A does not earn:

- detailed astrodynamics;
- SPICE propagation;
- fleets;
- individual ships;
- launch windows;
- depots;
- propellant/remass inventories;
- power infrastructure;
- maintenance/spares;
- backlog;
- multi-commodity transport flow;
- carrier/operator Agents;
- transport market competition;
- stochastic passenger casualty modeling;
- endogenous R&D;
- technology maturation;
- learning curves;
- diffusion/adoption;
- automatic Technology Timeline unlocks;
- inter-colony trade.

## Remaining strict-MVP gaps

After Test 012A, the principal strict-MVP gaps remain:

1. Earth-reference / shadow-impact integration;
2. repeated enterprise-cycle behavior, including partial/zero production and eventual failure/closure;
3. final integrated NULL/SPARSE/RICH qualification and governance reconciliation.

## Final standing

Test 012A passes structurally.

The earned distinction is:

**Technology constrains what service can exist.  
The Agent chooses whether to use the admitted opportunity.  
The SYSTEM validates affordability, capacity, direction and qualification.  
Population moves only through the governed departure/arrival transition.**

No empirical transport or technology forecast is claimed.
