# CIVPROP Project Economics V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-005 closure contract

## Purpose

Project Economics V1 replaces the default Method Lab project costs, lags and
capacity values with a versioned hybrid parameter boundary.

The governing separation is:

    qualified physical reference
        !=
    scenario parameter
        !=
    derived runtime project economics

A scenario range is allowed to drive the simulation when empirical calibration does
not exist, but it must remain visibly scenario-class rather than acquiring fake
authority through repetition.

## Contract

Implementation:

    engineering/civprop/contracts/project_economics_v1.py

Parameter set:

    engineering/civprop/contracts/project_economics_v1.json

Identity:

    CIVPROP_PROJECT_ECONOMICS_V1
    contract_version = 1.0.0
    parameter_set_id = EARTH_LUNA_PROJECT_ECONOMICS_V1_2026_2036

Scope:

    EARTH_ORBIT_LUNA_CISLUNAR_2026_2036

Capital unit:

    USD_2026_billion

Capacity units:

    power       MW
    habitat     person
    transport   tonnes/year
    industrial  tonnes/year
    resource    tonnes/year
    shipyard    tonnes/year

The old scenario_credit and scenario_capacity_unit are not used by the default
Project Economics V1 boundary.

## Parameter status

Each quantitative range is one of:

    QUALIFIED_REFERENCE
    SCENARIO_ASSUMPTION

A whole project parameterization is one of:

    SCENARIO_ASSUMPTION
    HYBRID_SCENARIO_WITH_QUALIFIED_COMPONENT

All quantities carry low / nominal / high values, units and provenance.

The runtime currently resolves the nominal value. The low/high values remain in the
output boundary for uncertainty analysis and later ensemble work.

## Qualified component currently used

The POWER_PLANT base output uses the existing LOOM technology-timeline reference to
NASA Fission Surface Power:

    40-kW-class lunar demonstration objective
        =
    0.04 MW base module reference

Provenance:

    docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md#R03

This qualifies only the base power-output reference.

It does not qualify:

- project capital cost;
- construction lag;
- transport prerequisite;
- learning rate;
- commercialization;
- fleet availability;
- a claim that 0.04 MW is an operational 2026 lunar plant.

Those remain scenario assumptions.

## First parameter set

Nominal 2026 module values are:

| Project | Capital, USD_2026 bn | Lag, years | Nominal output |
|---|---:|---:|---|
| PROSPECTING_SURVEY | 0.25 | 2 | mission; no installed output |
| LOGISTICS_NODE | 2.0 | 4 | 1,000 t/yr transport + 0.10 MW |
| POWER_PLANT | 0.40 | 4 | 0.04 MW |
| HABITAT | 2.0 | 5 | 4 persons |
| RESOURCE_PLANT | 3.0 | 5 | 100 t/yr resource + 25 t/yr industrial |
| INDUSTRIAL_WORKSHOP | 1.5 | 4 | 100 t/yr industrial |
| SURFACE_PORT | 1.5 | 4 | 1,000 t/yr transport |
| SHIPYARD | 8.0 | 7 | 100 t/yr shipyard + 50 t/yr industrial |

These are not point forecasts.

The JSON parameter set carries deliberately wide low/high scenario ranges around the
unqualified components.

## Prerequisite capacities

Prerequisites use the same physical capacity dimensions as installed state.

Examples:

- HABITAT requires nominal 0.10 MW and 250 t/yr transport capacity;
- RESOURCE_PLANT requires nominal 0.50 MW and 500 t/yr transport;
- INDUSTRIAL_WORKSHOP requires nominal 0.50 MW and 300 t/yr transport;
- SHIPYARD requires power, industrial and transport support.

These values are scenario assumptions and remain clearly marked as such.

## Scale behavior

Every project defines:

    reference_scale
    capital_exponent
    output_exponent
    lag_exponent

For current facilities:

    capital_exponent = 0.90
    output_exponent  = 1.00
    lag_exponent     = 0.15

Therefore a scale-2 facility currently resolves approximately as:

    capital ~ 2^0.90
    capacity ~ 2^1.00
    lag      ~ 2^0.15

relative to a scale-1 module.

This makes scale behavior explicit and versionable rather than hidden inside a
future spreadsheet.

Hybrid V1 currently requests scale = 1.0. The resolver already supports other scales
for later opportunity/actor work.

## Technology-year dependence

The current scenario epoch schedule is:

| Year | Cost multiplier | Capacity multiplier | Lag multiplier |
|---|---:|---:|---:|
| 2026 | 1.00 | 1.00 | 1.00 |
| 2031 | 0.92 | 1.10 | 0.90 |
| 2036 | 0.84 | 1.25 | 0.80 |

Intermediate years are linearly interpolated.

These multipliers are scenario assumptions, not empirical technology forecasts.

The purpose is to make technology-year dependence explicit and testable now, so
future calibrated curves can replace the scenario schedule without changing the
runtime contract.

## Hybrid V1 integration

For the compiled production-facing path, Hybrid resolves project economics at the
year the opportunity is evaluated.

Therefore a 2034 project can have different:

- capital cost;
- installed capacity;
- prerequisite capacity;
- construction lag;

from an otherwise identical 2026 project.

A committed project retains the resolved values that existed when it was scheduled.

Runner-level actor-budget replay resolves the same year-specific project economics,
so finance replay cannot silently fall back to the 2026 nominal.

Historical Method Lab inputs do not carry Project Economics V1 and preserve their
original static economics for regression.

## Capacity-unit migration

GAP-005 also removes the default scenario_capacity_unit interpretation from the
capacity dimensions used by causal demand/project output.

The current adapter maps the old off-world compatibility state into explicit units:

    transport   x100 -> tonnes/year
    industrial  x100 -> tonnes/year
    resource    x100 -> tonnes/year
    shipyard    x100 -> tonnes/year
    power       x1   -> MW
    habitat     x1   -> person

This does not make the inherited initial-state values empirical.

Those initial off-world values remain owned by GAP-012
FACILITY_AND_SITE_MATERIALIZATION and are explicitly registered as compatibility
assumptions. GAP-005 changes their unit representation so the project/demand
interfaces are dimensionally coherent.

Location book-capital is not relabeled as USD. It remains the later-gap compatibility
capital field.

Project capital has its own explicit unit:

    project_capital = USD_2026_billion

That separation prevents scenario_credit from being laundered into dollars.

## Dorrington-Olsen boundary

Existing LOOM assessment:

    dev/resource_economics/dorrington_olsen/m2/
      DORRINGTON_OLSEN_CIVPROP_INPUT_CONTRACT.json

    reports/solar_civprop/
      DORRINGTON_OLSEN_M2_CIVPROP_ASSESSMENT.md

The assessment classifies Dorrington-Olsen as an asteroid-mining
mission/architecture/economic kernel.

It is not a lunar-facility cost database or a lunar mining-rate model.

Project Economics V1 therefore records:

    DORRINGTON_OLSEN_M2
    use_status =
    NOT_APPLIED_TO_EARTH_LUNA_FACILITY_COSTS

No Dorrington-Olsen asteroid economic value is copied into HABITAT, POWER_PLANT,
RESOURCE_PLANT or other Earth-Luna facility parameters.

This satisfies the rule that a qualified domain model may be used only inside its
qualified scope.

## GAP-005 closure

GAP-005 is closed because the default production-facing path now has:

1. versioned project parameter sets with economic/physical units and provenance;
2. no METHOD_LAB_SYNTHETIC_V1 project parameterization in runtime use;
3. low/nominal/high uncertainty ranges;
4. explicit construction-lag ranges;
5. explicit scale behavior;
6. explicit technology-year dependence;
7. physical output and prerequisite capacity units;
8. disciplined domain-model scoping.

Closure does not mean the scenario assumptions are calibrated forecasts.

## Current seed-42 consequence

The outward seed-42 history remains:

    44 annual location states
    11 annual actor states
    11 actor decisions
    35 events
    0 facilities
    0 actor transactions
    0 actor-state events
    0 migration flows

All current actor decisions remain WAIT.

This is expected. Project Economics V1 can now tell the engine what a project would
cost and create, but it does not invent Australian generic spendable allocation,
capability or transport entitlement.

    need != project economics != ability to act

## Mission handoff after GAP-006

GAP-006 MISSIONS_AND_KNOWLEDGE_UPDATE is now closed.

Project Economics V1 continues to parameterize PROSPECTING_SURVEY cost and duration,
but Mission/Knowledge V1 owns its action identity, decision, execution, observation
and knowledge update. The default follow-on resource-project success value remains
UNKNOWN rather than being invented by the economics contract.

The immediate engineering frontier is GAP-007 PRESSURE_OBSERVABILITY.
