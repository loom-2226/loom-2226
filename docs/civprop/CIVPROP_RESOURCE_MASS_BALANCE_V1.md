# CIVPROP Resource Mass Balance V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-008 closure contract

## Purpose

Resource Mass Balance V1 replaces abstract resource-production semantics with an
explicit physical stock-flow chain:

    in-situ stock
        -> extracted feed
        -> contained resource
        -> recovered product
        -> product inventory
        -> consumption / outbound flow

The governing epistemic separation is:

    resource evidence
        !=
    actor resource knowledge
        !=
    evaluator physical realization
        !=
    economic value

GAP-008 owns physical conservation. GAP-006 owns actor-visible knowledge. GAP-009
owns production/value-added economics.

## Authority boundary

Promoted lunar-water evidence currently establishes:

    resource_id      MOON_POLAR_WATER
    body             MOON
    region           MOON_POLAR_PSR
    material family  VOLATILES
    abundance        PRESENT_UNQUANTIFIED
    scope            POLAR_AND_SELECTED_SURFACE_FOOTPRINTS

The admitted evidence does not establish:

- a site inventory in tonnes;
- ore/feed grade;
- extraction throughput;
- recovery efficiency;
- an opening product inventory;
- a global lunar-water inventory.

Therefore the default evaluator physical realization is:

    realization_status      UNKNOWN
    stock_status            UNKNOWN
    opening_stock_tonnes    null
    grade_status            UNKNOWN
    grade_mass_fraction     null
    inventory_status        UNKNOWN
    opening_inventory       null

UNKNOWN is not zero.

Presence evidence is not a numeric inventory.

## Legacy compatibility truth

The older Method Lab evaluator file contains:

    present = true
    grade_index = 0.65

Those fields remain Mission/Knowledge compatibility truth.

They are not Resource Mass Balance stock or grade.

In particular:

    grade_index = 0.65
        !=
    grade_mass_fraction = 0.65

The compiler explicitly creates a separate physical-realization boundary rather than
copying the compatibility index into the mass-balance model.

## Contract

Implementation:

    engineering/civprop/contracts/resource_mass_balance_v1.py

Parameter boundary:

    engineering/civprop/contracts/resource_mass_balance_v1.json

Hybrid adapter:

    engineering/civprop/method_lab/resource_lane_v1.py

Identity:

    CIVPROP_RESOURCE_MASS_BALANCE_V1
    contract_version = 1.0.0

Physical realization:

    CIVPROP_RESOURCE_PHYSICAL_REALIZATION_V1
    contract_version = 1.0.0

Units:

    mass       tonne
    throughput tonnes/year

## First process model

The first admitted process is:

    LUNAR_WATER_RESOURCE_PLANT_V1

It maps:

    RESOURCE_PLANT
        ->
    MOON_POLAR_WATER at LUNA_SURFACE

The existing facility resource-capacity field is interpreted as recovered-product
processing capacity in tonnes/year.

A separate extraction-feed capacity is required because feed throughput and recovered
product throughput are not physically interchangeable.

Current production-facing values remain:

    extraction feed capacity per facility = UNKNOWN
    recovery fraction                     = UNKNOWN

The timeline establishes relevant ISRU knowledge/demonstration context, not a
qualified generic lunar mining rate or recovery fraction.

## Stock-flow equations

For known physical/process parameters in year t:

    S_open
        = opening in-situ feed stock

    E
        = extracted feed

    G
        = contained-resource mass fraction

    C
        = contained resource

    R
        = recovery fraction

    P
        = recovered product

Then:

    C = E * G

    P = C * R

    unrecovered_contained = C - P

    process_tailings = E - P

    S_close = S_open - E

The process-tailings definition closes total feed mass. It therefore includes both
unrecovered contained resource and non-target feed material.

## Capacity constraints

Extraction is bounded by:

    E <= remaining stock

    E <= extraction-feed capacity

Recovered product is bounded by:

    P <= processing-product capacity

For nonzero grade and recovery, the processing limit can be transformed back to a
maximum feed rate:

    E_process_limit
        =
    product_capacity / (G * R)

The annual extracted feed is therefore:

    E
      =
    min(
        opening stock,
        extraction capacity,
        processing-derived feed limit
    )

No active RESOURCE_PLANT means:

    E = 0
    P = 0

That zero is causal: there is no active process capacity.

It does not imply zero resource stock.

## Inventory

Recovered product enters a separate inventory:

    I_close
      =
    I_open
      + P
      - consumption
      - outbound

The current GAP-008 Hybrid lane supplies no economic consumption/export demand.

Those sinks therefore default to zero only when inventory is numerically known.

The contract already supports explicit consumption and outbound quantities so later
GAP-009 / traffic work can use the same conservation boundary.

Inventory sinks may not exceed:

    I_open + P

An overdraw fails closed.

## UNKNOWN propagation

If an active facility exists but physical stock/grade is unresolved:

    production_status = PHYSICAL_STATE_UNKNOWN

and the numeric production chain remains null.

If physical state is known but extraction/recovery process parameters are unresolved:

    production_status = PROCESS_MODEL_UNKNOWN

and the numeric production chain remains null.

The engine does not emit:

    extraction = 0

merely because the required quantity is unknown.

Once unresolved active extraction could have occurred, later stock/inventory cannot
honestly remain numerically known; the physical runtime therefore propagates UNKNOWN.

## Evaluator versus actor state

ResourceStateV1 is:

    authority_class = EVALUATOR_PHYSICAL_STATE
    actor_visible   = false

The Resource Mass Balance runtime has no actor-belief or posterior input.

Actor-visible resource probability continues to come from GAP-006 Mission/Knowledge
V1.

Changing an actor belief therefore does not directly rewrite physical stock.

Changing physical stock does not directly rewrite actor knowledge.

Observation remains the governed bridge between hidden realization and actor belief.

## Annual resource state

Each resource/location/year emits one ResourceStateV1 containing:

    year
    location
    resource
    material family
    region

    production status

    opening stock
    grade

    active process-facility count
    extraction-feed capacity
    product-processing capacity

    extracted feed
    contained resource
    recovered product
    unrecovered contained material
    process tailings

    opening inventory
    consumption
    outbound
    closing inventory

    closing stock

All physical quantities are nullable where unresolved.

## Resource flows

Known physical production can emit:

    EXTRACTED_FEED
    RECOVERED_PRODUCT
    PROCESS_TAILINGS
    INVENTORY_CONSUMPTION
    INVENTORY_OUTBOUND

Each ResourceFlowV1 carries:

    stable resource-flow ID
    resource-state ID
    year
    location
    resource
    flow type
    tonnes
    contributing facility IDs

Resource flows are separate from the existing migration flow surface.

GAP-008 does not silently redefine migration/transport records as material flows.

## Validation

The runtime and common result validator enforce:

1. stock conservation

       S_open = E + S_close

2. grade conversion

       contained = extracted feed * grade

3. recovery conservation

       contained
         =
       recovered product
         + unrecovered contained

4. total feed/tailings closure

       tailings
         =
       extracted feed - recovered product

5. inventory closure

       I_open + P
         =
       consumption + outbound + I_close

6. extraction throughput limit;

7. processing-product throughput limit;

8. nonnegative mass and throughput;

9. grade/recovery fractions in [0,1];

10. year-to-year stock continuity;

11. year-to-year inventory continuity;

12. facility-count and facility-capacity consistency;

13. flow-to-state reconciliation;

14. flow-to-facility referential integrity.

## Hostile fixtures

Bounded synthetic tests provide known stock/grade/recovery values only for contract
qualification.

They verify:

- UNKNOWN abundance remains null, not zero;
- no active plant produces zero extraction without changing stock;
- extraction cannot exceed stock;
- extraction cannot exceed feed throughput;
- recovered product cannot exceed processing capacity;
- recovery above 100 percent fails;
- grade above 100 percent fails;
- stock/recovery/tailings equations close;
- inventory sinks close and cannot overdraw;
- depletion constrains later production;
- evidence presence alone does not create inventory.

Synthetic test parameters are not promoted lunar-resource facts.

## Default seed-42 consequence

The current promoted Earth-Luna development baseline has:

    0 commissioned facilities

Therefore the expected GAP-008 default output is:

    11 annual MOON_POLAR_WATER resource states
    0 resource flows

Each state retains:

    opening stock = null
    grade         = null
    closing stock = null
    inventory     = null

while:

    extracted feed    = 0
    recovered product = 0

because no active process facility exists.

This is intentionally different from saying the Moon contains zero water.

## Observer-effect requirement

Adding GAP-008 must not alter any GAP-007 behavioral surface:

    actor states
    actor transactions/events
    annual location states
    facilities
    project decisions
    mission decisions
    missions
    observations
    actor knowledge
    pressure states/contributions/qualifications
    events
    migration flows

Only the version/fingerprint envelope, compiled resource boundary and new resource
state/flow surfaces may change.

## GAP-008 closure

GAP-008 is closed when the production-facing path provides:

1. explicit separation of evidence/belief from evaluator physical realization;
2. stock/grade/extraction/recovery/tailings/inventory/depletion contracts;
3. UNKNOWN-not-zero abundance semantics;
4. facility-constrained extraction and processing;
5. mass-conservation validation;
6. annual resource state and material flow outputs;
7. regression proof that the new physical accounting does not leak into actor
   knowledge or silently change prior behavior.

Closure does not mean lunar stock, grade, mining rate or recovery have been measured.

## Immediate frontier

GAP-009 PRODUCTION_AND_VALUE_ADDED is now CLOSED through Production Accounting V1.

The immediate engineering frontier is:

    GAP-010 POWER_BALANCE

Production Accounting V1 may value physically possible resource output when valuation
parameters are known, but it preserves UNKNOWN monetary valuation where they are not.
Resource Mass Balance V1 remains authoritative for the underlying physical flow.
