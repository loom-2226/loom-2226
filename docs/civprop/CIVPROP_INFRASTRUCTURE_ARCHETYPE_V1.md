# CIVPROP Infrastructure Archetype V1

Date: 2026-09-30
Class: class:engineering
Status: selected production-facing semantic contract; numeric production calibration incomplete

## Decision

The next CIVPROP production contract is the infrastructure archetype layer.

This layer answers:

> What generic kinds of capacity-bearing infrastructure can CIVPROP create?

It does not answer:

> Which named Atlas facilities must exist?

The V1 catalog therefore defines reusable infrastructure modules independently from
the old 2226 Ceres answer set.

## Why this contract comes first

CIVPROP already has a selected propagation architecture and substantial upstream
Earth, Solar and Timeline authority. The next causal bridge needed by the engine is
a stable description of what an investment can physically create.

Infrastructure archetypes sit between:

    opportunity / actor decision
             ->
       committed project
             ->
    commissioned physical capacity
             ->
      body / facility state
             ->
         Atlas output

This contract can remain stable while later cost, demand, transport and economic
parameterizations improve.

## Core rule: semantics are separate from parameterization

An archetype defines stable semantics:

- generic archetype identity;
- family;
- allowed spatial placement;
- required capability tags;
- capacity dimensions consumed;
- capacity dimensions produced.

It does not contain production cost or construction-time truth.

Numeric parameter sets are separately versioned and carry:

- parameter status;
- scope;
- capital cost and unit;
- construction lag;
- minimum input capacities;
- output capacities;
- provenance.

This prevents today's Method Lab fixture from quietly becoming tomorrow's economic
law.

## V1 archetypes

| Archetype | Family | Placement | Primary capacity role |
|---|---|---|---|
| SURFACE_PORT | TRANSPORT | surface | transport |
| LOGISTICS_NODE | TRANSPORT | orbital/free-space | transport, supporting power |
| POWER_PLANT | POWER | surface/orbital/free-space | power |
| HABITAT | HABITAT | surface/orbital/free-space | habitation |
| RESOURCE_PLANT | RESOURCE | surface | resource + industrial |
| INDUSTRIAL_WORKSHOP | MANUFACTURING | surface/orbital/free-space | industrial |
| SHIPYARD | SHIPYARD | orbital/free-space | shipyard + industrial |

PROSPECTING_SURVEY is intentionally excluded because it is a mission/action, not
infrastructure.

## Relationship to Atlas facilities

An archetype is a capacity-bearing module, not necessarily one final named Atlas
facility.

Several modules may be colocated and later materialized as one facility/site.

Examples using the existing Ceres vocabulary are illustrative only:

    SURFACE_INBODY_PORT
        ~= SURFACE_PORT + INDUSTRIAL_WORKSHOP (+ supporting POWER)

    SURFACE_RESOURCE_PORT
        ~= SURFACE_PORT + RESOURCE_PLANT (+ supporting POWER)

    ORBITAL_HABITAT_PORT
        ~= LOGISTICS_NODE + HABITAT

    ORBITAL_SHIPYARD
        ~= LOGISTICS_NODE + SHIPYARD (+ POWER / INDUSTRIAL support)

The current STRATEGIC_PORT label is not a primitive infrastructure archetype.
Strategic significance should be derived later from actual capability, traffic,
relationships, network position, technology and institutional role rather than
causing those things by label.

This prevents circular reasoning such as "the facility is strategically important
because its archetype was strategic."

## Historical Method Lab regression parameterization

The catalog still contains a parameter set named METHOD_LAB_SYNTHETIC_V1 for
historical Method Lab regression only. The default compiled CIVPROP path no longer
consumes it after GAP-005 closure.

It preserves, value-for-value, the existing Method Lab assumptions for:

- LOGISTICS_NODE;
- POWER_PLANT;
- HABITAT;
- RESOURCE_PLANT;
- INDUSTRIAL_WORKSHOP.

Those values remain:

- synthetic scenario credits;
- synthetic capacity units;
- synthetic construction lags;
- valid only for the frozen Method Lab scope.

They are not:

- empirical costs;
- calibrated 2026 costs;
- canon;
- technology forecasts;
- production CIVPROP economics;
- 2226 facility sizes.

SURFACE_PORT and SHIPYARD intentionally have no METHOD_LAB_SYNTHETIC_V1 numeric
parameterization.

The current default project parameter authority is instead:

    engineering/civprop/contracts/project_economics_v1.json
    EARTH_LUNA_PROJECT_ECONOMICS_V1_2026_2036

Project Economics V1 covers the full Earth-Orbit-Luna development project set,
including SURFACE_PORT and SHIPYARD, with explicit units, uncertainty ranges,
scale behavior, technology-year adjustments and provenance. Scenario-class values
remain visibly non-empirical.

The stable archetype semantics in this document remain independent from either the
historical Method Lab parameter set or the current Project Economics V1 values.

## Explicit V1 assumptions

1. Infrastructure is modular and capacity-bearing.
2. Final facility identity may aggregate multiple colocated modules.
3. Existing infrastructure remains spatially fixed unless an explicit event changes
   it; new investment creates new modules/expansions.
4. Placement classes are currently SURFACE, ORBITAL, and FREE_SPACE.
5. RESOURCE_PLANT remains a combined surface extraction/processing module for V1
   continuity. A later contract may split excavation, beneficiation and refining.
6. Capability tags are requirements to be resolved by Timeline/actor-capability
   adapters. A tag does not itself grant an actor capability.
7. Capacity dimensions are logical engine dimensions, not yet all Atlas display
   metrics.
8. Named Ceres facilities are not hard-coded into this catalog.

## What this unlocks

The Hybrid V1 engine can now move toward a production contract where an opportunity
means:

    actor
      + location
      + infrastructure archetype
      + parameter set
      + capability/access
      + demand/pressure
      + affordability

and a successful project produces a typed physical module whose capacities can feed
subsequent pressure, migration, production and Atlas materialization.

## What remains open

The following are deliberately not solved by this contract:

- production cost curves;
- scale economies;
- maintenance/depreciation;
- replacement value;
- detailed energy balances;
- resource mass/yield closure;
- facility aggregation/site formation;
- project financing;
- demand generation;
- freight/passenger throughput equations;
- ship/fleet production;
- surface coordinates and orbital element assignment;
- naming;
- institution relationships;
- strategic/economic/transport centrality.

Those belong to later parameter, opportunity, state or materialization layers rather
than being smuggled into archetype identity.

## Implementation

- engineering/civprop/contracts/infrastructure_v1.py
- engineering/civprop/contracts/infrastructure_archetypes_v1.json
- engineering/civprop/contracts/test_infrastructure_v1.py

The contract is independent of the Method Lab engine implementation. The synthetic
Method Lab parameter set exists solely to preserve current behavior and make later
adapter replacement explicit.
