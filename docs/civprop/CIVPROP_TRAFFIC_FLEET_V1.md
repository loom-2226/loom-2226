# CIVPROP Traffic/Fleet V1

Date: 2026-10-02
Class: class:engineering
Status: GAP-011 closure contract

## Purpose

Traffic/Fleet V1 converts explicitly assigned origin/destination transport demand into bounded annual service, fleet, voyage, call, backlog and node-incidence state.

It does not infer that installed local transport capacity is realized movement. It does not infer a generic route from geometry alone. It does not convert a named payload contract into generic freight service. Technology Timeline milestones do not create vehicle classes, fleet assets or traffic.

## Upstream authority

Traffic/Fleet V1 consumes:

- GAP-003 Accessibility V1 service paths;
- GAP-004 Demand/Pressure V1 TRANSPORT requirements in tonnes/year;
- runtime location transport handling capacity;
- explicit Traffic/Fleet V1 service bindings, vehicle classes, fleet assets and OD demand allocations;
- LOOM Technology Timeline entries only as capability context/provenance.

The default 2026-2036 package preserves the named AUS_ROOVER_CLPS_CT4_IM5 service with generic_demand_eligible=false.

## Core epistemic boundaries

Installed handling capacity is not traffic:

    local transport capacity != cargo moved

A technology milestone is not a fleet:

    TRN-MOD-HEAVY 2040 != vehicles appear in 2040
    TRN-MOD-NEP 2050 != NEP freighters appear in 2050

A named payload service is not generic logistics:

    Roo-ver / CLPS payload service != generic Earth-Luna freight lane

Unassigned demand remains explicit:

    local TRANSPORT requirement with no OD allocation -> UNASSIGNED_OD

It is not silently discarded and is not assigned to an arbitrary origin/service.

## Annual fleet capacity

For a vehicle with known mission duration, turnaround and availability:

    available_trips =
        floor(calendar_days * availability_fraction
              / (mission_duration_days + turnaround_days))

Cargo and passenger service ceilings derive from available trips times the vehicle-class payload/passenger capacities.

If required fleet parameters or service accessibility are UNKNOWN, realized movement remains UNKNOWN. UNKNOWN does not become zero or unconstrained capacity.

## Realized traffic

For a fully specified feasible service, realized cargo/passenger movement is bounded by:

- assigned demand plus opening backlog;
- active fleet trip capacity;
- vehicle cargo/passenger capacity;
- origin handling capacity;
- destination handling capacity.

Unserved demand becomes closing backlog and carries into the next year.

## Voyages and calls

Realized trips emit annual voyage records. Each modeled one-way voyage produces one origin departure call and one destination arrival call.

Cargo/passenger totals, voyage counts and node-incidence metrics reconcile with the route traffic state.

## Pressure handoff

Traffic/Fleet V1 may replace the old installed-capacity proxy in the GAP-004 TRANSPORT pressure observation only when OD assignment is complete and service capacity is known.

Partial or absent OD assignment does not rewrite pressure. Opening backlog is carried as an explicit transport requirement contribution.

## Production handoff

GAP-011 location transport_service_ratio feeds the GAP-009 TRANSPORT production constraint when the ratio is known.

If the service ratio cannot be established, the production constraint remains UNKNOWN.

Traffic/Fleet V1 does not attribute route throughput to a specific LOGISTICS_NODE facility without an explicit facility/service binding. That facility-output ownership question remains downstream.

## Atlas traffic projection

The runtime projects node-incidence metrics:

- cargo_throughput_tonnes_year
- passenger_movements_year
- ship_calls_year

with:

    metric_scope = MODELED_GENERIC_TRAFFIC_ONLY
    measurement_basis = ANNUAL_MODELED_NODE_TRAFFIC_INCIDENCE

A zero therefore means no modeled generic traffic in this boundary. It is not an empirical assertion that no spacecraft or payload activity existed.

## Default seed-42 consequence

The compiled default has zero vehicle classes, zero fleet assets and zero generic OD allocations. The named Roo-ver/CLPS binding remains non-generic.

Earth Orbit's 800 t/year local transport requirement remains:

    assigned cargo demand = 0
    unassigned cargo demand = 800
    assignment status = UNASSIGNED_OD

The default therefore emits no generic voyages, no generic route traffic and no traffic pressure override.

## Closure

GAP-011 is closed because the executable now has versioned, replayable and tested mechanisms for explicit OD demand assignment, scoped transport services, fleet assets and annual trip capacity, cargo/passenger service limits, voyages and ship calls, backlog, route utilization, origin/destination reconciliation, node-incidence traffic metrics, transport-pressure handoff and transport-service handoff to Production Accounting.

GAP-011 closure does not mean the production baseline contains a calibrated generic Earth-Luna fleet. The default correctly contains none.
