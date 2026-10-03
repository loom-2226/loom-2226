# Phase 3B.1 — Context and Identity Model Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN CANDIDATE

## 1. Purpose

Provide stable identity coordinates shared by evidence, scenario truth, agent state and realized simulation state without making storage identifiers carry epistemic meaning.

## 2. Identity rule

Entity identity, proposition identity, state-record identity and context identity are separate.

The same entity may appear in REAL, SCENARIO(id) and REALIZED(run_id) without those records becoming the same assertion or state.

## 3. Core identifiers

Minimum opaque stable identifiers:

- entity_id
- location_id
- actor_id
- account_id
- asset_id
- project_id
- infrastructure_id
- resource_state_id
- observation_id
- belief_state_id
- technology_id
- population_state_id
- colony_state_id
- transport_relation_id
- transaction_id
- event_id
- parameter_id
- abstraction_id
- scenario_id + scenario_version
- run_id
- lineage_id / dependency references

Identifiers must not encode mutable descriptive attributes.

## 4. World contexts

Closed for MVP execution semantics, not for all future LOOM ontology:

- REAL
- SCENARIO(scenario_id, scenario_version)
- REALIZED(run_id)

REAL contains evidence/reference-domain propositions. SCENARIO contains hidden/exogenous universe state. REALIZED contains state produced by simulation transitions.

Cross-context identity never authorizes value crossing.

## 5. Perspectives

Minimum perspectives:

- GOVERNANCE
- WORLD_SIM
- AGENT(actor_id)

Perspective is part of information/admissibility semantics, not merely a UI filter.

## 6. Time

Every time-varying state declares:

- time_basis;
- effective_time or interval;
- observation_time where different;
- simulation_time for realized events;
- source/as-of time where relevant.

MVP execution cadence is not fixed by this document. Calendar year may be used by Earth reference while projects/events later require finer simulation time. The identity model must not assume all subsystems share one time resolution.

## 7. Location

Location identity is hierarchical but not inferred from names.

Minimum kinds:

- EARTH_AREA
- CELESTIAL_BODY
- SITE
- FACILITY

Transport links locations; transport properties are not embedded as intrinsic location properties.

## 8. Scenario and run identity

A scenario version identifies immutable hidden/exogenous starting truth and scenario parameters.

Changing hidden truth after results are observed creates a new scenario version.

A run identifies execution against a pinned scenario version, reference/input snapshot, model/code version, parameter set and random master seed.

Runs do not mutate their parent scenario definition.

## 9. Agent identity

An institutional actor has persistent actor_id across a run. Its changing assets, beliefs, information, capabilities and accounts are time-indexed state associated with that actor, not changes to actor identity.

Public/private are actor types/roles, not identifiers.

## 10. Resource identity

Resource family identity, deposit/site identity, evidence assertion identity, hidden scenario quantity and realized remaining quantity are separate.

No identifier shall cause REAL evidence, SCENARIO truth and REALIZED stock to alias.

## 11. Earth reference identity

Earth reference assertions identify trajectory, derivation, concept, area and year according to the Earth Reference Contract candidate.

A realized Earth consequence references the relevant Earth reference assertion but receives separate realized/event identity.

## 12. Root identity

Primitive-root identity is extensible under Phase 2 Erratum 001. Storage must support root_type identifiers beyond EVIDENTIARY_ROOT and AUTHORIZATION_ROOT without schema replacement.

No additional primitive root is recognized by this representation.

## 13. MVP abstraction identity

An abstraction_id identifies a versioned simplified subsystem or deferred boundary from the MVP Abstraction Register.

Abstraction identity never substitutes for model/parameter/provenance lineage.

## 14. Referential invariants

1. IDs are stable within their governed scope.
2. Names/labels may change without changing identity.
3. Cross-context records never alias by convenience.
4. Scenario version is immutable after use.
5. Run state cannot mutate scenario definition.
6. Agent perspective requires a valid actor identity.
7. Every realized mutation references a run and event.
8. Every observation has producer/channel, subject and recipient perspective.
9. Every transaction identifies accounts/counterparties.
10. Every transport relation identifies origin and destination locations.
11. Every abstraction use identifies abstraction version.
12. UNKNOWN/missing does not create a synthetic entity/value merely to satisfy a foreign key.

## 15. Deferred decisions

This document deliberately does not choose UUID versus namespaced string serialization, database table layout, event time-step resolution, or external identity crosswalk format. Those are implementation/storage decisions unless they alter semantics.
