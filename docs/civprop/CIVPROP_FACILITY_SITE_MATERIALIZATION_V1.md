# CIVPROP Facility/Site Materialization V1

Date: 2026-10-02
Class: class:engineering
Status: GAP-012 closure contract

## Purpose

Facility/Site Materialization V1 is a deterministic post-engine projection from commissioned CIVPROP infrastructure modules into stable sites, materialized facilities, orbital/site projections, habitat settlement candidates and Atlas-facing facility classifications.

It does not alter propagation, decisions, capacity, economics, traffic, pressure, knowledge or RNG.

## Governing boundary

Materialization occurs only after the Hybrid result has validated.

    CIVPROP propagation
        -> validated commissioned modules
        -> deterministic materialization
        -> Atlas-facing site/facility projection

Materialized presentation state is therefore downstream of causal simulation state.

## Colocation

V1 colocation policy is:

    EXPLICIT_ONLY

Modules sharing the same broad runtime location, owner, year or capability are not automatically colocated.

Without an explicit site binding, every commissioned module receives its own stable materialized site identity.

An explicit binding may aggregate multiple module facility IDs only when they share the same runtime location.

This prevents broad location classes such as LUNA_SURFACE from becoming one enormous accidental base.

## Stable identity

Site and materialized-facility IDs are deterministic hashes of causal identity inputs.

Display names are excluded from identity construction.

Changing:

    Lunar Base Alpha

to:

    Kevin's Extremely Serious Moon Warehouse

cannot alter the site ID, facility ID, module composition, ownership, capacities or simulation state.

Naming policy is:

    PRESENTATION_ONLY

## Spatial authority

A materialized site always has stable location-class identity.

Precise surface coordinates or orbital elements exist only when explicit admitted spatial authority supplies them.

Supported spatial states are:

- LOCATION_CLASS_ONLY
- EXACT_SURFACE_COORDINATES
- EXACT_ORBITAL_ELEMENTS

LOCATION_CLASS_ONLY carries no invented latitude, longitude or orbital elements.

Exact surface authority requires latitude/longitude and SURFACE placement.

Exact orbital authority requires semimajor axis, eccentricity and inclination and ORBITAL placement.

## Ownership and operation

Module owner identity is preserved from the generated facility record.

Site/materialized-facility owners are the unique owners of member modules.

Operator identity is never inferred from ownership.

Operators appear only through explicit site binding authority.

Therefore:

    OWNER != OPERATOR

unless a separate admitted relationship says otherwise.

## Lifecycle and composition

Every materialized module preserves:

- original facility ID;
- project archetype;
- location;
- owner;
- commitment year;
- commissioning year;
- lifecycle status;
- capital;
- capacity vector.

Sites and materialized facilities preserve the complete member-module list and archetype composition.

GAP-012 does not invent depreciation, failure, maintenance, retirement or abandonment. Those belong to GAP-013.

## Atlas facility type derivation

Legacy Ceres facility-type vocabulary is used only as a qualified vocabulary reference. Legacy Ceres facility identities, names, coordinates and facility rows are not copied as generated answers.

V1 derives four Atlas-facing types from generated composition:

    SURFACE_PORT + RESOURCE_PLANT
        -> SURFACE_RESOURCE_PORT

    SURFACE_PORT + INDUSTRIAL_WORKSHOP
        -> SURFACE_INBODY_PORT

    LOGISTICS_NODE + HABITAT
        -> ORBITAL_HABITAT_PORT

    LOGISTICS_NODE + SHIPYARD
        -> ORBITAL_SHIPYARD

Unsupported compositions remain:

    facility_type_status = UNKNOWN

rather than being forced into a legacy label.

STRATEGIC_PORT is explicitly excluded from materialization. Strategic significance belongs to GAP-015 derived metrics.

## Habitat and settlements

A site containing a HABITAT module may emit:

    settlement_status = HABITAT_INFRASTRUCTURE_CANDIDATE
    demographic_status = DEFERRED_GAP_014

This is not a claim that a viable or occupied settlement exists.

Population cohorts, births/deaths, biological viability and long-run settlement status remain GAP-014 concerns.

## Inherited initial-state compatibility boundary

The pre-existing Earth-orbit/Luna/cislunar starting state contains inherited compatibility values from the original Method Lab envelope.

These values are not a qualified empirical 2026 infrastructure inventory.

GAP-012 makes that status explicit through:

    status = UNQUALIFIED_COMPATIBILITY

and:

    materialization_policy =
        NEVER_MATERIALIZE_WITHOUT_MODULE_PROVENANCE

The current scoped locations are:

- EARTH_ORBIT
- LUNA_SURFACE
- CISLUNAR_FREE_SPACE

Those state values remain available to the locked causal regression envelope, but they do not create modules, sites, facilities, orbitals or Atlas facility identities.

This replaces the old ASSUME-GAP012-OFFWORLD-INITIAL-STATE open-gap placeholder with a versioned closed-boundary policy. It does not convert the inherited values into empirical authority.

## Production-accounting handoff

Production Accounting advances to contract version 1.2.0 under GAP-012 bookkeeping.

LOGISTICS_NODE physical/economic output remains DEFERRED because GAP-011 route traffic is not automatically attributable to a particular logistics facility and GAP-012 refuses to invent that relationship.

The unresolved facility-level attribution now points to GAP-015, where Atlas-derived facility/network metrics can use explicit materialized identities and relationships.

## Default seed-42 consequence

The default run commissions no facilities.

Therefore GAP-012 emits:

- 3 materialization compatibility-state rows;
- 0 materialized modules;
- 0 generated sites;
- 0 materialized facilities;
- 0 orbitals;
- 0 settlement candidates;
- 0 Atlas facilities.

This is a valid materialization result, not a missing implementation.

## Closure

GAP-012 is closed because the executable now has a deterministic, versioned and tested mechanism for:

- stable materialized identity;
- explicit-only colocation;
- authority-bounded surface/orbital placement;
- module composition preservation;
- lifecycle-field preservation;
- owner/operator separation;
- presentation-only naming;
- habitat settlement candidacy;
- composition-derived Atlas facility types;
- explicit handling of inherited compatibility state without false facility creation; and
- a strict no-copy boundary against the legacy Ceres answer set.

Closure does not claim that the default 2026-2036 package contains a qualified off-world infrastructure inventory. It correctly does not.
