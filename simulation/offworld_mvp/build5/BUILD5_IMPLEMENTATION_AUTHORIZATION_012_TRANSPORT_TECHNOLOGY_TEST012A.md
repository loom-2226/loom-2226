# Build 5 Implementation Authorization 012 — Minimal Transport Relationship + Exogenous Technology Gate Test 012A

**Status:** AUTHORIZED / BOUNDED IMPLEMENTATION / PRE-CONTRACT / SINGLE-AUTHORITY  
**Date:** 2026-10-04  
**Project-owner authorization:** “Go”  
**FRD mutation:** NOT AUTHORIZED FOR THIS TEST  
**Parent branch/head:** `offworld-mvp-build5-settlement` @ `768e25e2772e6f56ed4ae4be8d5d133d66c327d4`  
**Live FRD blob:** `1e4ebc11e2fde81f7dad87732bd6d563229ce935`

## Purpose

Close only the strict-MVP transport/technology gap left explicit by Test 011A.

Authorized causal slice:

`exogenous TechnologyCapabilityState -> typed TransportRelationship -> admitted transport opportunity -> bounded public settlement-support decision -> SYSTEM validation/payment -> deterministic passenger arrival -> conserved migration -> settlement-state update`.

Technology changes the opportunity set. The public Agent decides whether to use it. SYSTEM mechanics enforce what actually happens.

## Authority bootstrap

Live GitHub authority was verified before implementation.

- `loom-2226/loom-2226`: branch `offworld-mvp-build5-settlement` is identical to `768e25e2772e6f56ed4ae4be8d5d133d66c327d4`.
- `loom-2226/loom-research-lab`: `main` is identical to `572f174f8b329ca749fddaf3a3ce492ae97304bc`.

The guiding FRD was read live. Controlling requirements remain FRD §§10–13, especially:

`T(i,j,t) = {Cost, TravelTime, Energy, LossRisk, Capacity}`.

Transport is a relationship, not a deposit property. Technology is exogenous for MVP.

## Research intake standing

Read-only advisory inputs:

- `projects/offworld_transport_energy_logistics/RESEARCH_BRIEF_v0.1.md`, blob `b7b248f6cd1c15702b956e7874a708f7882cb9f1`;
- `projects/offworld_technology_research_innovation/RESEARCH_BRIEF_v0.1.md`, blob `8d2f6c87a88ff6c602c0b0c751f2c4adafefa875`.

Standing:

RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION / PARKED REFERENCE.

Admitted architecture principles only:

- physical feasibility is not transport service;
- transport service is not realized traffic;
- technology changes candidate capability/service characteristics but does not create traffic;
- one scalar technology level is prohibited;
- routine transport remains SYSTEM;
- no fleet, depot, backlog, endogenous R&D, adoption/diffusion or astrodynamics layer is earned.

## Technology Timeline disposition

Test 012A does not activate a named Technology Timeline row.

A Test-only exogenous capability fixture is authorized instead, so no calendar date is treated as an unlock and no Timeline scenario anchor is promoted into runtime authority.

## Technology capability state

Introduce immutable/versioned `TechnologyCapabilityState`.

Minimum fields:

- state id;
- effective period;
- explicit qualified capability identifiers;
- source/rationale reference;
- epistemic standing;
- version.

No `tech_level` scalar is authorized.

Capability-state creation mutates no population, finance, resource, project or settlement state.

## Transport relationship

Introduce immutable/versioned `TransportRelationship` representing one passenger service envelope between typed origin and destination nodes for a declared period.

Minimum fields:

- relationship id;
- origin node;
- destination node;
- effective period;
- required technology capability;
- Cost;
- TravelTime;
- Energy;
- LossRisk;
- Capacity;
- payload/passenger class;
- source/rationale reference;
- epistemic standing;
- version.

For this test, Cost is a per-passenger financial charge. The other four dimensions remain separately serialized and separately validated.

All numeric fixture values are `TEST_ONLY / NOT_CALIBRATED / NOT_POLICY_BASELINE`.

## Technology qualification

A deterministic SYSTEM may admit a transport relationship only when:

- the relationship is valid for the requested period;
- its required capability identifier is explicitly qualified in the supplied `TechnologyCapabilityState`;
- origin and destination match the requested direction;
- both nodes exist and have the required Earth/offworld kinds;
- all required transport inputs are known and valid.

Technology-state creation alone creates no service use, payment or movement.

Transport-relationship creation alone creates no payment or movement.

## Settlement decision integration

Test 012A extends the public settlement-support decision through a new transport-aware request/policy contract rather than reinterpreting the historical Test 011A contract.

The existing public Agent is reused. No carrier Agent, fleet Agent, technology Agent or settlement Agent is created.

Required transport-aware admitted facts include:

- existing Test 011A settlement facts;
- transport availability;
- transport relationship id;
- transport capacity;
- per-passenger transport cost;
- travel time;
- energy;
- loss risk.

UNKNOWN in any required transport fact produces `BLOCKED_UNKNOWN` before policy-worker execution.

The Agent may AUTHORIZE only when the existing settlement conditions remain satisfied and the requested resident count does not exceed admitted transport capacity and public funds cover both:

- settlement support cost; and
- transport cost = requested residents × per-passenger Cost.

Transport cost remains separate from settlement support cost.

The policy does not mutate world state.

## Capacity policy

Test 012A chooses an explicit all-or-defer rule for the first transport slice.

If requested residents exceed route capacity, the Agent DEFERs rather than silently truncating the request.

No partial passenger allocation policy is authorized.

## Travel time and movement

TravelTime must have executable meaning without orbital propagation.

For an authorized movement:

1. the SYSTEM revalidates current service qualification, direction, capacity and affordability;
2. settlement support and transport charges are ledgered separately;
3. a deterministic departure record is created;
4. the passenger arrival time is `departure_time + TravelTime`;
5. population movement occurs only at the governed arrival transition;
6. settlement stage is re-derived after arrival.

This test does not model trajectories, launch windows, individual ships or in-transit life support.

The minimal passenger batch remains an aggregate transport movement.

## Energy

Energy remains a separate declared service requirement in Test 012A.

No explicit energy inventory is authorized because energy stock is not yet the discriminating causal question.

Energy may not be silently folded into financial Cost.

## Loss risk

LossRisk remains a separate declared service characteristic.

The qualification fixture uses zero loss risk. This is a structural fixture, not an empirical safety claim.

Nonzero passenger-loss stochasticity is not authorized in this test.

## Financial mechanics

Introduce a transport-clearing/provider account solely as the financial counterparty for the passenger transport charge.

For successful transport:

- public settlement support is transferred separately under existing `PUBLIC_SUBSIDY` semantics;
- transport charge is transferred separately under an explicit transport-payment transaction purpose;
- no money is created or destroyed.

## NULL/SPARSE/RICH qualification

RICH and SPARSE may form the same dependent settlement when their admitted settlement state, technology state and transport relationship are equivalent.

NULL must remain unable to bootstrap settlement merely because transport exists. Its inherited lack of funded habitat/headroom continues to block migration.

Hidden resource truth may not affect the pre-arrival transport decision when admitted Agent-visible settlement/transport/technology state is identical.

## Required blocked cases

Test 012A shall structurally verify at least:

1. missing required technology capability blocks service/movement;
2. technology state alone creates no service use or movement;
3. missing transport relationship blocks movement;
4. wrong origin/destination linkage is rejected;
5. request above capacity cannot move excess population;
6. insufficient funds for transport plus support blocks movement;
7. transport relationship registration alone mutates no population/accounts;
8. technology improvement alone mutates no population/accounts;
9. decision evaluation alone mutates no world state;
10. travel direction cannot silently reverse;
11. Cost, TravelTime, Energy, LossRisk and Capacity remain separately serialized;
12. UNKNOWN required transport input propagates as `BLOCKED_UNKNOWN`;
13. duplicate departure/arrival execution cannot duplicate payment or population;
14. raw technology/transport/pending-arrival tampering is decision-epoch detectable;
15. population is exactly conserved at arrival;
16. A1–A9 remain green;
17. deterministic replay is exact;
18. all prior governed tests remain green.

## Technology-improvement case

A second Test-only capability/relationship fixture may change one or more transport dimensions, including lower Cost, shorter TravelTime, lower Energy or larger Capacity.

The changed opportunity set must not itself create a decision, payment or migration.

Same decision inputs plus unchanged Agent action remain required for world consequence.

## Historical Test 011A boundary

Test 011A's direct aggregate migration path remains historical structural machinery and is not re-described as physically transported movement.

Test 012A introduces the current transport-gated qualification path. Passing Test 012A does not retroactively convert Test 011A's direct migration fixture into a transport model.

## Not authorized

Do not implement:

- fleets or individual ships;
- launch windows;
- orbital propagation or SPICE;
- depots;
- propellant/remass inventories;
- local power grids;
- backlog/multi-commodity routing;
- maintenance/spares;
- carrier/operator Agents;
- dynamic transport pricing;
- endogenous technology or R&D;
- learning curves;
- automatic Timeline unlocks;
- multiple competing services;
- inter-colony trade.

## FRD / ODD / standing

The guiding FRD shall not be modified.

The executable ODD may be reconciled to new executable dataclasses/enums/unit contracts.

Passing Test 012A establishes structural transport relationship + exogenous technology gating only.

It does not establish empirical 2226 transport performance, passenger safety, freight economics, technology forecasts, adoption forecasts, logistics-network validity or settlement viability.
