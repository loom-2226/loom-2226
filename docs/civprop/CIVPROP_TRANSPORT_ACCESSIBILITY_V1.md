# CIVPROP Transport Accessibility V1

Date: 2026-09-30
Class: class:engineering
Status: GAP-003 closure contract

## Purpose

Accessibility V1 replaces the default Method Lab accessibility curves with a
versioned physics + scoped-service boundary used by Hybrid V1.

The governing separation is:

    qualified Solar geometry
            !=
    route / trajectory
            !=
    provider service
            !=
    actor entitlement
            !=
    generalized cost

The contract is implemented in:

    engineering/civprop/contracts/accessibility_v1.py

and compiled into the default runtime package by:

    engineering/civprop/compile_inputs_v1.py

## Query contract

The service accepts an AccessibilityRequest containing:

- actor identity;
- origin location;
- destination location;
- UTC epoch;
- mission class;
- service class;
- optional subject/payload identity;
- optional explicitly requested service identity.

Evaluation also receives Actor State V1 and an explicit technology-state mapping.

The result preserves exactly three accessibility states:

    FEASIBLE
    INFEASIBLE
    UNKNOWN

UNKNOWN is not converted to zero cost, infeasibility, or feasibility.

Every assessment can carry:

- matched service identity;
- qualified geometry context when available;
- decomposed cost components;
- generalized cost state/value/unit/uncertainty;
- limiting constraints;
- provenance references.

## Physics layer

The current compiled Earth-Luna development slice admits one frozen qualified
Solar geometry sample from the promoted Roo-ver transport screen:

    epoch: 2030-07-01T00:00:00Z
    origin body: EARTH
    destination body: MOON
    reference frame: J2000/ECLIPTIC
    ephemeris: DE440
    state source: qualified LOCAL_SPICE
    navigation grade: true
    Earth-Moon body-center separation: 401540.02139136905 km
    relative body speed: 0.9836733938012038 km/s

The compiler revalidates the frozen Earth/Moon state vectors against the captured
DE440 asset hash and recomputes separation and relative speed before admitting the
sample.

The distance semantic is explicitly:

    BODY_CENTER_STRAIGHT_LINE_CONTEXT_NOT_ROUTE_LENGTH

Therefore the sample is not:

- a trajectory;
- path length;
- delta-v;
- transfer duration;
- launch window;
- payload allocation;
- proof of service availability.

An epoch without a qualified frozen geometry sample remains without geometry
context. CIVPROP does not synthesize a state vector merely because DE440 coverage
exists.

## Service layer

The default compiled package currently contains one scoped service path:

    service_id: AUS_ROOVER_CLPS_CT4_IM5
    actor_id: AUS
    subject_id: ROO_VER_WITH_NASA_MNP
    provider_id: INTUITIVE_MACHINES
    origin: EARTH_SURFACE
    destination: LUNA_SURFACE
    mission_class: NAMED_PAYLOAD_DELIVERY
    service_class: CLPS_LUNAR_DELIVERY
    target year: 2030
    end-to-end status: UNKNOWN

This path is admitted from the existing Roo-ver / NASA CLPS CT-4 / Intuitive
Machines IM-5 evidence already preserved by CIVPROP-0.

Actor use of a service requires matching scoped provider-service access in Actor
State V1. A private-company service relationship, a national partnership, or a
named payload contract does not become generic transport capability.

A request that explicitly names a service but falls outside that service's scope
may be INFEASIBLE for that named path. That does not imply every other possible
transport path is infeasible.

## Cost layer

Generalized cost is no longer an unexplained Method Lab scalar in the default
compiled input.

The contract represents physical/service quantities separately, with units and
uncertainty fields. The current Roo-ver service path preserves these unresolved
components as UNKNOWN:

    route length          km
    transfer duration     s
    delta-v               km/s
    service price         currency/service-unit

Qualified geometry can additionally expose:

    body-center separation    km
    relative body speed       km/s

Those geometry quantities are context and are not silently inserted as route
length or delta-v.

A generalized-cost scalar may be KNOWN only when the contract explicitly carries
a value and unit. UNKNOWN generalized cost may not carry an invented scalar.

## Hybrid V1 integration

Hybrid V1's orchestration is unchanged.

For historical Method Lab fixtures without Accessibility V1, the legacy
accessibility-profile behavior remains intact for regression comparison.

For the default compiled authority package, Hybrid queries Accessibility V1 when
generating project opportunities. Generic project deployment requests use generic
project/service classes and therefore do not match the narrowly scoped Roo-ver
service.

Consequently Roo-ver access does not unlock generic lunar construction,
prospecting, migration, or logistics.

This is intentional.

## What GAP-003 closure removes

The default compiled scenario no longer contains the Method Lab
`accessibility` profile table or its synthetic annual generalized-cost curves.

The explicit assumption:

    ASSUME-GAP003-ACCESSIBILITY

is removed.

The compiler manifest marks GAP-003 CLOSED.

## What GAP-003 closure does not claim

GAP-003 closure does not provide:

- a general Lambert solver;
- arbitrary trajectory optimization;
- launch-provider market clearing;
- fleet inventories or utilization;
- cargo/passenger manifests;
- service prices where none are qualified;
- technology performance curves;
- arbitrary annual SPICE state generation inside the runtime;
- generic Australian access derived from Roo-ver;
- proof that IM-5 will fly or succeed;
- a forecast of lunar development.

Fleet/traffic mechanics remain owned by later gaps, including GAP-011.

Demand remains GAP-004. Project economics remain GAP-005.

## Seed-42 regression consequence

With GAP-002 and GAP-003 both closed, the current default seed-42 regression
produces:

    44 annual location states
    11 annual actor states
    11 actor decisions
    35 events
    0 facilities
    0 actor transactions
    0 actor-state events
    0 migration flows

All eleven actor decisions are WAIT.

The loss of the previous ten migration flows is expected. Those flows depended on
the synthetic accessibility curves that GAP-003 removed. It is not a forecast
that migration cannot occur.

## Closure criteria trace

GAP-003 required:

1. versioned service accepting origin, destination, epoch, mission/service class,
   and actor/technology state;
2. FEASIBLE / INFEASIBLE / UNKNOWN preservation with provenance and limiting
   constraints;
3. decomposable physical/service cost quantities with units and uncertainty;
4. qualified Solar geometry without treating straight-line separation as route
   length;
5. removal of synthetic Method Lab accessibility profiles from the default
   compiled input.

Accessibility V1, the compiler integration, Hybrid adapter, tests and GAP-003
baseline satisfy those criteria for the current Engine V1 development boundary.

## Change control

Changes to Accessibility V1 semantics require an explicit contract/version
decision and a new golden baseline.

Changes to qualified Solar geometry evidence require a new frozen evidence hash
and recompiled input package.

New provider-service evidence must remain actor-, subject-, route-, time- and
service-scoped. It may not be generalized into capability or entitlement without
separate authority.

Historical Method Lab and GAP-001/GAP-002 baseline artifacts remain immutable.
