# CIVPROP Power Balance V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-010 closure contract

## Purpose

Power Balance V1 replaces abstract installed-power capacity with an explicit
location/year electrical accounting boundary.

It separates:

    installed generation capacity (MW)
        !=
    average generation (MW)
        !=
    firm generation capacity (MW)
        !=
    peak electrical load (MW)
        !=
    average electrical load (MW)
        !=
    annual electrical energy (MWh)

The model is intentionally conservative where LOOM does not yet have qualified
operating parameters. UNKNOWN is not converted into zero, full utilization, or
calendar-driven capability.

## Technology Timeline authority

Primary technology context:

    docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md

Two entries matter directly.

### R03

R03 records a NASA 40-kW-class lunar fission surface-power demonstration objective
in the early 2030s.

For CIVPROP this qualifies the existing 0.04 MW POWER_PLANT reference output
component already used by Project Economics V1.

It does not qualify:

- a generic lunar capacity factor;
- firm-capacity fraction;
- operating lifetime;
- MW-scale industrial electricity;
- storage;
- distribution;
- actor ownership/access;
- automatic commercialization.

### ENE-MOD-INDUSTRIAL

The Timeline's moderate industrial-energy scenario threshold is 2040 and describes
reliable MW-scale delivered electrical power to an off-world industrial facility.

It remains a conditional author-scenario milestone.

The Timeline's own interpretation rule applies:

    DATE DOES NOT UNLOCK CAPABILITY

Therefore:

    threshold year reached
        !=
    generator installed
        !=
    generator operational
        !=
    actor has access
        !=
    location has MW-scale delivered electricity

Power Balance V1 records:

    auto_unlock = false

A year can never create generation by itself.

## Scope

Current production-facing scope:

    NON_EARTH_SURFACE

Excluded:

    EARTH_SURFACE

The current Earth-surface CIVPROP power value is a compatibility state, not an
empirical model of terrestrial generation. GAP-010 does not reinterpret that value
as the Earth's grid.

Current modeled locations are:

    EARTH_ORBIT
    LUNA_SURFACE
    CISLUNAR_FREE_SPACE

## Contract

Implementation:

    engineering/civprop/contracts/power_balance_v1.py

Configuration:

    engineering/civprop/contracts/power_balance_v1.json

Runtime adapter:

    engineering/civprop/method_lab/power_lane_v1.py

Identity:

    CIVPROP_POWER_BALANCE_V1
    contract_version = 1.0.0

Hybrid version with GAP-010 enabled:

    method-reference-v8

## Population load

Power Balance V1 reuses the POWER state-driver coefficients from Demand/Pressure V1.

Current uncalibrated coefficients are:

    biological_population   0.025 MW/person
    transient_population    0.025 MW/person

Within GAP-010 these are interpreted as population peak-load drivers.

Thus:

    population_peak_load
        =
    Σ population_driver_value * driver_coefficient

This reuse does not make the coefficient empirically calibrated.

It also does not convert pending-project prerequisite MW into operating electrical
consumption. Project prerequisites remain commissioning/feasibility requirements,
not annual load measurements.

## Average population load

A separate average-to-peak factor is required:

    population_average_load
        =
    population_peak_load
        * population_average_to_peak_factor

The default factor is:

    UNKNOWN

Therefore a known peak demand does not imply known average demand or annual MWh.

## Facility load

Every current facility archetype has an explicit FacilityLoadModel:

    LOGISTICS_NODE
    POWER_PLANT
    HABITAT
    RESOURCE_PLANT
    INDUSTRIAL_WORKSHOP

For each facility the contract provides separate parameters for:

    peak load MW/facility
    average-to-peak factor

The production-facing defaults are UNKNOWN.

No facility's project capital, installed output capacity, or minimum power
prerequisite is silently reinterpreted as its operating electrical load.

When a required facility-load value is unknown, the corresponding aggregate
average/peak demand remains unknown as appropriate.

## Generation

Installed generation capacity comes from location power capacity and commissioned
power-producing facility capacity.

Current facility archetypes with positive installed power output are:

    LOGISTICS_NODE
    POWER_PLANT

Each generator model has separate:

    availability factor
    firm-capacity fraction

Average generation:

    G_avg
        =
    installed_capacity * availability_factor

Firm capacity:

    G_firm
        =
    installed_capacity * firm_capacity_fraction

Both factors remain UNKNOWN in the production-facing default.

Therefore:

    installed MW
        !=
    average generated MW

and:

    installed MW
        !=
    annual generated MWh

The inherited off-world initial power capacity is governed by GAP-012 Facility/Site Materialization V1 as UNQUALIFIED_COMPATIBILITY and is never materialized into a facility without module provenance. Its availability and firmness remain UNKNOWN.

## Time and energy

Annual energy uses actual Gregorian calendar-year duration:

    8760 hours
or
    8784 hours in leap years

When average generation is known:

    generated_energy_MWh
        =
    average_generation_MW * interval_hours

When average demand is known:

    demanded_energy_MWh
        =
    average_demand_MW * interval_hours

## Energy closure

For a known annual balance:

    served_energy
        =
    min(demanded_energy, generated_energy)

    unserved_energy
        =
    max(0, demanded_energy - generated_energy)

    curtailed_energy
        =
    max(0, generated_energy - demanded_energy)

The two conservation identities are:

    generated
        =
    served + curtailed

    demand
        =
    served + unserved

The runtime records an energy-closure residual and requires it to be within
deterministic tolerance.

If required average-load or availability values are unresolved:

    energy_balance_status = UNKNOWN

No MWh values are fabricated.

## Peak adequacy and reserve

Peak service ratio is based on firm capacity:

    peak_service_ratio
        =
    min(1, firm_generation_capacity / peak_demand)

when both are known.

A reserve-margin parameter may define:

    required_firm_capacity
        =
    peak_demand * (1 + reserve_margin)

and a reserve-adequacy ratio.

The production-facing reserve margin is UNKNOWN.

An unknown reserve assumption does not mean zero reserve is required.

## Power service ratio

When annual-energy and peak-service ratios are both known:

    power_service_ratio
        =
    min(
        energy_service_ratio,
        peak_service_ratio
    )

This ratio is the governed handoff to Production Accounting V1 for facilities whose
production model requires POWER.

If the power service ratio is unknown:

    production POWER constraint = UNKNOWN

not:

    production POWER constraint = 1.0

## Storage

Current storage model status:

    NOT_MODELED_V1

with modeled capacities:

    storage power  = 0 MW
    storage energy = 0 MWh

This means the current GAP-010 model contains no storage asset or dispatch mechanism.

It does not mean real future off-world systems cannot contain batteries, thermal
storage, regenerative fuel cells, flywheels, or other storage.

Storage semantics may be versioned later without redefining current GAP-010 results.

## Power flows

When annual energy quantities are known, PowerFlowV1 can emit:

    GENERATION
    SERVED_LOAD
    UNSERVED_LOAD
    CURTAILMENT

All amounts use MWh.

Unknown annual energy produces no invented numerical flow.

## Atlas power metrics

Legacy Atlas/CIVSTATE exposes:

    power_average_mw
    power_peak_mw

Their previous qualification explicitly lacked:

- demand versus supply semantics;
- time interval;
- inclusion boundary.

GAP-010 defines the runtime projection as electrical LOAD DEMAND:

    power_average_mw
        =
    PowerState.average_demand_mw

    power_peak_mw
        =
    PowerState.peak_demand_mw

Measurement basis:

    ANNUAL_AVERAGE_AND_PEAK_ELECTRICAL_LOAD_DEMAND

These are direct projections from PowerState.

They are not:

- installed generation capacity;
- arbitrary capacity indexes;
- average generation;
- historical Ceres answer-sheet values.

If average demand is unresolved, Atlas average power remains null while peak power
may still be known.

## Production Accounting V1 handoff

GAP-009 originally deferred POWER_PLANT physical output to GAP-010.

GAP-010 closes that handoff by versioning Production Accounting V1 to:

    contract_version = 1.1.0

POWER_PLANT now uses:

    output_source = POWER_GENERATION
    output_unit   = MWh/year

Its physical output derives from the exact GAP-010 FACILITY_GENERATOR component:

    facility annual generation
        =
    facility average generation MW
        * interval hours

If generator availability is UNKNOWN, physical electrical production remains
UNKNOWN.

Monetary valuation remains independently UNKNOWN unless qualified prices,
intermediate-consumption coefficients and operating-cost coefficients exist.

## Default seed-42 behavior

The current 2026-2036 development slice emits:

    33 PowerStateV1 rows
    0 PowerFlowV1 rows
    33 Atlas power metric rows

Earth surface is excluded.

### Earth orbit 2026

The inherited location state contains:

    installed generation capacity = 5 MW
    transient population          = 200 people

Population peak load therefore evaluates to:

    200 * 0.025 MW/person = 5 MW

The runtime records:

    installed generation capacity = 5 MW
    population peak load          = 5 MW
    peak demand                   = 5 MW

but:

    average generation = UNKNOWN
    firm generation    = UNKNOWN
    average demand     = UNKNOWN
    annual generation  = UNKNOWN
    annual consumption = UNKNOWN
    power service      = UNKNOWN

because availability, firm-capacity fraction and average-load factor are not
qualified.

Atlas projection:

    power_peak_mw    = 5
    power_average_mw = null

### Luna and cislunar free space 2026

Current state contains no population, facility load, or installed generation.

The zero/zero balance is therefore numerically closed:

    installed capacity = 0
    peak demand         = 0
    average generation  = 0
    average demand      = 0
    generated energy    = 0
    consumed energy     = 0
    power service ratio = 1

These zeroes arise from explicit zero modeled state, not UNKNOWN coercion.

## Hostile fixtures

Bounded tests separately prove:

- installed capacity is not average generation;
- unknown availability does not create MWh;
- population peak load uses Demand/Pressure POWER drivers;
- facility loads are explicit;
- known surplus closes with curtailment;
- known shortfall closes with unserved energy;
- power service ratio reflects energy and peak constraints;
- Power Plant capacity becomes a generator component only when an actual facility
  exists;
- Timeline thresholds do not auto-create capacity;
- zero/zero systems close without inventing energy;
- Earth surface remains out of the off-world boundary;
- Production Accounting consumes the exact GAP-010 generator result.

Synthetic hostile parameters are test fixtures, not promoted technology forecasts.

## GAP-010 closure

GAP-010 is closed because the default production path now has:

1. explicit installed-capacity versus generation/load/energy semantics;
2. explicit population and facility load models;
3. versioned availability, firmness, reserve and storage assumptions;
4. deterministic MWh conservation when required quantities are known;
5. UNKNOWN propagation when they are not;
6. runtime-derived Atlas average/peak power metrics;
7. a governed POWER service handoff to Production Accounting;
8. no Technology Timeline auto-unlock.

## Immediate frontier

The next implementation target is:

    GAP-011 TRAFFIC_AND_FLEET

Power state must remain an upstream physical/service constraint. GAP-011 may consume
power where appropriate, but it must not infer vehicle movement merely because
electrical capacity exists.
