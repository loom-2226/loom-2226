# CIVPROP Production Accounting V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-009 closure contract

## Purpose

Production Accounting V1 converts commissioned generated facilities into an
auditable annual production/accounting surface without confusing physical capacity,
physical output, market valuation, operating cost, investment, or capital stock.

The governing chain is:

    commissioned facility
        -> physical output basis
        -> required operating constraints
        -> realized utilization
        -> realized physical output
        -> monetary valuation
        -> gross output / intermediate consumption / operating cost / value added
        -> commissioning investment / gross productive capital

The governing separation is:

    PHYSICAL OUTPUT
        !=
    MONETARY VALUATION
        !=
    OPERATING COST
        !=
    INVESTMENT
        !=
    PRODUCTIVE CAPITAL

GAP-009 owns this accounting boundary.

GAP-010 owns power balance.
GAP-011 owns traffic/fleet realization.
GAP-013 owns depreciation, replacement and retirement.
GAP-014 owns deeper labor/demographic state.

## Earth accounting authority

The promoted Earth temporal schema contains:

    earth_economic_year
    earth_sector_year
    earth_sector_asset_year

Relevant transferable field semantics include:

    gross_output
    value_added
    investment
    capital
    employment / effective_labor
    depreciation_rate / replacement fields

Authority:

    data/postgres/migrations/004_earth_temporal_authority.sql

GAP-009 transfers the accounting vocabulary and aggregation structure only.

It does not copy:

- Australian sector output/value-added ratios;
- Earth prices;
- Earth utilization;
- Earth operating costs;
- Earth productivity;
- Earth capital/output ratios;

into off-world production.

The authority capture records this explicitly as:

    FIELD_NAMES_AND_ACCOUNTING_IDENTITIES_ONLY_
    NO_OFFWORLD_PRICE_PRODUCTIVITY_OR_UTILIZATION_COPY

## Core accounting identity

Where valuation is known:

    value_added
        =
    gross_output
        -
    intermediate_consumption

or:

    VA = GO - IC

Operating cost is a separate analytical field.

Therefore:

    VA != GO - operating_cost

unless a separate model happens to produce equality for a specific case.

This prevents accounting value added from being silently turned into profit.

## Monetary units

Productive capital stock:

    USD_2026_billion

Annual monetary flows:

    USD_2026_billion/year

This matches the Project Economics V1 project-capital basis.

It does not relabel the legacy location book-capital compatibility field.

## Gross productive capital

For a generated facility, commissioning creates gross productive capital.

On its commissioning year:

    opening_gross_productive_capital = 0

    commissioned_investment
        =
    resolved commissioned project capital

    closing_gross_productive_capital
        =
    opening capital + commissioned investment

After commissioning, before lifecycle/depreciation is implemented:

    commissioned_investment = 0

    closing_gross_productive_capital
        =
    opening_gross_productive_capital

No depreciation is applied by GAP-009.

That belongs to:

    GAP-013 MAINTENANCE_DEPRECIATION_RETIREMENT

Project capital is not:

- an output price;
- annual operating cost;
- intermediate consumption;
- an actor's remaining budget;
- the legacy location capital compatibility field.

## Production constraints

Production Accounting V1 recognizes the following operating constraints:

    POWER
    LABOR_AUTOMATION
    MATERIALS
    TRANSPORT

Each required constraint is:

    KNOWN
    UNKNOWN
    NOT_APPLICABLE

A KNOWN constraint carries a utilization ratio in:

    [0,1]

Where all required constraints are resolved, realized utilization is bounded by the
most restrictive known constraint:

    U
      =
    min(U_power,
        U_labor,
        U_materials,
        U_transport)

using only constraints that are applicable to that facility model.

Missing required constraint evidence is emitted as:

    UNKNOWN

and therefore:

    UNKNOWN != 0
    UNKNOWN != 1

An unresolved required constraint makes realized utilization and realized physical
output UNKNOWN.

It does not become zero output.
It does not become full utilization.

## Current downstream constraint boundary

GAP-010 POWER_BALANCE is CLOSED. Production Accounting V1 is now version 1.1.0; POWER_PLANT physical output derives from GAP-010 facility generation in MWh/year. Installed MW is still not treated as annual energy availability.

GAP-011 TRAFFIC_AND_FLEET remains open.

Therefore installed transport capacity is not treated as realized freight service.

GAP-014 DEMOGRAPHIC_DEPTH remains open.

Therefore the current generic workforce field is not treated as a qualified
facility-specific labor/automation service.

Production Accounting V1 is already designed to consume those future constraint
observations without changing the accounting identities.

## Current facility production models

The current compiled Earth-Luna scenario contains five facility archetypes.

### LOGISTICS_NODE

Sector:

    TRANSPORT

Physical output source:

    DEFERRED

Owning downstream gap:

    GAP-011 TRAFFIC_AND_FLEET

Installed transport capacity is not itself realized cargo service.

### POWER_PLANT

Sector:

    ENERGY

Physical output source:

    POWER_GENERATION

Output unit:

    MWh/year

The source is the exact GAP-010 FACILITY_GENERATOR component. Unknown generator availability preserves UNKNOWN annual production.

### HABITAT

Sector:

    HABITAT_SERVICES

Physical output source:

    DEFERRED

Owning downstream gap:

    GAP-014 DEMOGRAPHIC_DEPTH

Person-capacity is not automatically market-valued habitat/service output.

### RESOURCE_PLANT

Sector:

    RESOURCE

Physical output basis:

    GAP-008 RESOURCE_RECOVERED_PRODUCT

Output unit:

    tonnes/year

The admitted output ceiling cannot exceed:

- facility resource-processing capacity; or
- the facility's deterministic share of GAP-008 recovered physical product.

When multiple peer RESOURCE_PLANT facilities operate at one resource/location, the
aggregate GAP-008 recovered product is allocated in proportion to each peer's
installed resource-processing capacity. The sum of facility physical-output ceilings
therefore cannot exceed the aggregate recovered product.

Required GAP-009 service constraints are:

    POWER
    LABOR_AUTOMATION
    TRANSPORT

GAP-008 remains authoritative for stock, grade, extraction, recovery, tailings,
inventory and depletion.

### INDUSTRIAL_WORKSHOP

Sector:

    INDUSTRY

Physical output basis:

    installed industrial capacity

Output unit:

    tonnes/year

Required constraints are:

    POWER
    LABOR_AUTOMATION
    MATERIALS
    TRANSPORT

Installed capacity is only an output ceiling.

It is not annual realized production.

## Valuation parameters

Each facility model exposes separately:

    unit_output_value
    intermediate_consumption_per_output
    operating_cost_per_output

Each parameter is:

    KNOWN
    UNKNOWN

The current production-facing Earth-Luna parameter set leaves all three UNKNOWN for
all five facility archetypes.

This is intentional.

There is currently no qualified off-world price/cost model that justifies copying
Earth values, project cost, or asteroid economics into these fields.

Therefore known physical output can coexist with:

    gross_output             UNKNOWN
    intermediate_consumption UNKNOWN
    operating_cost           UNKNOWN
    value_added              UNKNOWN

Physical production does not require a fabricated price.

## FacilityProductionStateV1

Each active generated facility/year can emit:

    production_state_id
    year
    facility_id
    project_archetype_id
    production_model_id
    sector_id
    location_id
    owner_actor_id

    output_source
    physical_output_unit
    installed_output_capacity
    physical_output_ceiling

    constraint_observations
    utilization_status
    realized_utilization
    controlling_constraint_id

    physical_output_status
    physical_output_quantity

    valuation_status
    unit_output_value
    gross_output
    intermediate_consumption
    operating_cost
    value_added

    opening_gross_productive_capital
    commissioned_investment
    closing_gross_productive_capital

Physical output and monetary fields are nullable when unresolved.

## Aggregate surfaces

Facility rows aggregate deterministically into:

    SectorProductionStateV1
    LocationProductionStateV1
    BodyProductionStateV1

Sector aggregation preserves physical output only where member facilities share one
output unit and all member physical outputs are known.

Location/body aggregation does not add heterogeneous physical units together.

Economic flows and productive capital can aggregate because they share governed
monetary units.

The validator independently rebuilds every aggregate from facility rows and rejects
any difference.

## Replay and validation

Where Production Accounting V1 is enabled, the common result validator requires:

- every active generated facility to have one production row for every year from
  commissioning through the end of the horizon;
- every facility row to replay exactly from the facility record, its explicit
  constraint observations, and GAP-008 resource state;
- physical output not to exceed its admitted ceiling;
- utilization to remain within [0,1];
- value-added identity to close exactly where valuation is known;
- gross productive-capital identity to close;
- sector aggregates to reproduce exactly from facility rows;
- location aggregates to reproduce exactly from sector rows;
- body aggregates to reproduce exactly from location rows.

Historical runs without Production Accounting V1 retain their previous canonical
result hashes.

## Hostile qualification fixtures

Synthetic test fixtures are allowed to provide known prices, costs and constraints
only for mechanism qualification.

They prove:

- UNKNOWN required constraint propagates UNKNOWN rather than zero;
- the minimum known constraint controls utilization;
- realized output cannot exceed installed capacity;
- Resource Plant output cannot exceed GAP-008 recovered product;
- known physical output may coexist with UNKNOWN monetary valuation;
- known valuation obeys VA = GO - IC;
- operating cost remains distinct from intermediate consumption/value added;
- zero physical output produces zero monetary flows when valuation coefficients are
  known;
- utilization above 1 fails closed;
- commissioning creates investment and gross productive capital;
- no depreciation occurs before GAP-013;
- facility, sector, location and body aggregates reconcile.

Synthetic fixture prices/costs are not promoted off-world economic facts.

## Default seed-42 consequence

The current Earth-Luna seed-42 baseline contains:

    0 commissioned generated facilities

Therefore GAP-009 emits:

    0 facility production states
    0 sector production states
    0 location production states
    0 body production states

This is a causal result of the current generated-facility state.

It does not mean:

- Earth orbit has no real-world economic activity;
- Luna has no external economic activity outside the generated model;
- inherited pre-GAP-012 compatibility capacities are materialized operating firms.

The output scope is the generated CIVPROP facility economy.

## Observer-effect requirement

Adding Production Accounting V1 must not alter GAP-008 behavioral state:

    actor state
    actor transactions/events
    annual location state
    facilities
    project decisions
    mission decisions
    missions
    observations
    knowledge
    pressure
    resource state/flows
    events
    migration flows

GAP-009 is currently an accounting/output lane.

Later gaps may feed production constraints back into feasibility only through
explicitly versioned interfaces.

## GAP-009 closure

GAP-009 is closed when the production-facing path provides:

1. explicit physical-output bases and constraint observations;
2. UNKNOWN-safe utilization;
3. independent monetary valuation;
4. documented GO / IC / VA identities;
5. separate operating-cost accounting;
6. commissioning investment and gross productive-capital accounting;
7. deterministic facility -> sector -> location -> body reconciliation;
8. versioned outputs and hostile tests;
9. proof that existing GAP-008 behavior is unchanged.

Closure does not mean off-world prices, operating costs, utilization, power service,
transport service or labor availability are empirically calibrated.

## Immediate frontier

GAP-010 POWER_BALANCE is CLOSED and supplies the governed power-service/generation boundary.

The immediate engineering frontier is:

    GAP-011 TRAFFIC_AND_FLEET

## GAP-012 materialization handoff

Production Accounting V1.2 moves LOGISTICS_NODE facility-output attribution from GAP-012 to GAP-015. GAP-011 produces route/node traffic, while GAP-012 materializes stable facility/site identity; neither contract proves which specific logistics facility owns a route-throughput flow. The default remains DEFERRED rather than smearing route traffic across colocated nodes.
