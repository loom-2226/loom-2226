# CIVPROP Demand / Pressure V1

Date: 2026-09-30
Class: class:engineering
Status: GAP-004 closure contract

## Purpose

Demand / Pressure V1 replaces the default Method Lab annual demand curves with a
causal stock-flow mechanism driven by current civilization state and explicit scoped
requirements.

The governing chain is:

    civilization state
        -> requirement
        -> installed capacity
        -> unmet demand
        -> decaying pressure
        -> opportunity qualification
        -> actor decision

Demand does not grant capability, accessibility, money or project economics.

## Contract

Implementation:

    engineering/civprop/contracts/demand_pressure_v1.py

Format:

    CIVPROP_DEMAND_PRESSURE_V1
    contract_version = 1.0.0

Parameter status:

    UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1

The current coefficients close the causal mechanism. They are explicit model
parameters, not empirical forecasts or calibrated social laws.

## Equations

For location l, channel c and year t:

    requirement(l,c,t)
      = state-driven requirement
      + scoped strategic requirement
      + pending-project prerequisite requirement

    unmet(l,c,t)
      = max(0, requirement(l,c,t) - installed_capacity(l,c,t))

    pressure(l,c,t)
      = decay(c) * pressure(l,c,t-1)
      + gain(c) * unmet(l,c,t)

Pressure therefore has the same unit as unmet demand for that channel.

When unmet demand disappears, no new pressure is added and remembered pressure
decays. Capacity additions can therefore relieve pressure without an arbitrary
"pressure discharge" transaction.

## Current channels

The default Earth-Luna development slice defines:

| Channel | Unit | Available state |
|---|---|---|
| HABITAT | person | habitat |
| TRANSPORT | scenario_capacity_unit | transport |
| INDUSTRIAL | scenario_capacity_unit | industrial |
| RESOURCE | scenario_capacity_unit | resource |
| POWER | MW_equivalent | power |

All current channels use:

    decay = 0.60
    gain = 0.24

These are versioned, uncalibrated model parameters.

Current state drivers are:

- HABITAT: biological population + transient population;
- TRANSPORT: transient population at 0.04 capacity-unit/person;
- INDUSTRIAL: workforce at 0.04 capacity-unit/person;
- RESOURCE: biological + transient population at 0.01 capacity-unit/person;
- POWER: biological + transient population at 0.025 MW-equivalent/person.

EARTH_SURFACE is excluded from this off-world demand boundary.

## Strategic requirements

The contract supports explicit actor/location/channel requirements with:

- stable requirement identity;
- actor;
- location;
- channel;
- amount and unit;
- validity interval;
- provenance references.

The default compiled package currently contains no numeric strategic requirement.

Roo-ver is a real scoped commitment, but the admitted evidence does not establish a
generic numeric transport, power, industrial, resource or habitat requirement.
GAP-004 therefore does not invent one.

Strategic commitment exists != quantified generic infrastructure demand.

## Pending projects

A committed project that has not yet commissioned contributes its declared minimum
input capacities as additional requirements.

This gives construction commitments a causal way to create pressure for prerequisite
capacity without importing project profitability or market valuation.

Those minimum-input capacity values remain METHOD_LAB_SYNTHETIC_V1 under GAP-005.
GAP-004 consumes their declared semantics but does not claim they are calibrated.

## Opportunity qualification

For the causal path, a project is pressure-qualified using pressure in the same
capacity channel as the capacity the project would add.

Conceptually:

    qualification ratio
      = max(channel pressure / project output capacity)

The current Hybrid qualification threshold remains:

    0.55

This removes project capital cost from pressure qualification.

Capital cost still affects affordability and actor ranking under the existing
project-economics placeholder. That belongs to GAP-005.

Need != affordability.
Pressure != willingness to pay.
Demand != project profitability.

## Legacy Method Lab

The historical Method Lab scenario still carries:

    OFFWORLD_TRANSPORT_DEMAND
    OFFWORLD_INDUSTRIAL_DEMAND
    OFFWORLD_HABITAT_INTEREST
    WATER_RESOURCE_DEMAND

Those fixtures remain supported only so historical Method Lab regressions reproduce.

The default compiled authority package does not contain demand_signals and does not
consume those annual curves.

The compiler assumption:

    ASSUME-GAP004-DEMAND

is removed.

## Migration

Demand / Pressure V1 does not infer migration desire from spare habitat, scarcity or
pressure.

The causal runtime therefore disables the old Method Lab migration-interest rule,
which depended on OFFWORLD_HABITAT_INTEREST.

A production relocation/demography mechanism remains later work, principally
GAP-014.

## Pressure observability

Dynamic pressure reservoirs remain internal to Hybrid V1.

The runner exposes the versioned Demand / Pressure V1 configuration boundary, but
does not emit annual pressure trajectories.

That is intentional. GAP-007 PRESSURE_OBSERVABILITY remains OPEN and owns the
versioned pressure-state output and decision trace surface.

Closing GAP-004 does not steal GAP-007 by quietly emitting a half-designed pressure
ledger.

## Hostile cases

Tests cover:

- zero state requirement -> zero demand and zero pressure;
- habitat shortage -> state-derived unmet demand;
- installed-capacity relief -> no new demand and old pressure decays;
- balanced local state -> no fake congestion;
- explicit strategic requirement -> demand without population;
- expired strategic requirement -> demand disappears;
- strategic requirement unit mismatch -> fail closed;
- Earth surface exclusion;
- Hybrid no-demand case -> no pressure-qualified project;
- Hybrid habitat shortage -> habitat can qualify;
- Hybrid strategic transport requirement -> logistics can qualify.

## Current default behavior

The 2026 compiled state produces, internally:

    EARTH_ORBIT HABITAT
      required = 200 person
      available = 50 person
      unmet = 150 person
      pressure = 36 person

    EARTH_ORBIT RESOURCE
      required = 2 scenario_capacity_unit
      available = 0
      unmet = 2
      pressure = 0.48 scenario_capacity_unit

The default seed-42 output nevertheless remains:

    44 annual location states
    11 annual actor states
    11 actor decisions
    35 events
    0 facilities
    0 actor transactions
    0 actor-state events
    0 migration flows

All eleven actor decisions remain WAIT.

That does not mean no demand exists. It means current scoped actor state,
accessibility, capability and budget constraints still prevent generic project
commitment.

## GAP-004 closure

GAP-004 is closed because the default production-facing path now:

1. derives demand from explicit civilization state rather than annual authored
   demand curves;
2. permits only versioned causal state and scoped requirement inputs;
3. documents channel components and units;
4. decays pressure when unmet demand disappears and relieves it through capacity;
5. removes OFFWORLD_* and WATER_RESOURCE_DEMAND series from the default compiled
   input.

## What remains open

GAP-004 does not solve:

- calibrated project costs, lags or capacities: GAP-005;
- missions and knowledge evolution: GAP-006;
- emitted/reconstructable annual pressure state: GAP-007;
- resource mass balance: GAP-008;
- production/value added: GAP-009;
- power-system balance: GAP-010;
- traffic and fleet utilization: GAP-011;
- full demography and migration: GAP-014.

The immediate engineering frontier is GAP-005 PROJECT_ECONOMICS.
