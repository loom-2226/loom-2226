# CIVPROP Pressure Observability V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-007 closure contract

## Purpose

Pressure Observability V1 makes the existing Hybrid pressure mechanism inspectable
without turning the audit layer into a second decision engine.

The causal chain is now externally reconstructable:

    civilization state
        -> requirement components
        -> installed capacity
        -> unmet demand
        -> annual pressure transition
        -> per-project qualification ratios
        -> actor decision

The observability lane is read-only.

It may compare its reconstructed pressure and qualification arithmetic with Hybrid's
internal values and fail closed on divergence. It does not write pressure, choose an
opportunity, alter a budget, alter a random draw, or change a decision.

## Contract

Implementation:

    engineering/civprop/contracts/pressure_observability_v1.py

Configuration:

    engineering/civprop/contracts/pressure_observability_v1.json

Adapter:

    engineering/civprop/method_lab/pressure_lane_v1.py

Identity:

    CIVPROP_PRESSURE_OBSERVABILITY_V1
    contract_version = 1.0.0

The default package enables:

    emit_contributions = true
    emit_all_qualifications = true
    record_legacy_discharge = true

## Output surfaces

Pressure Observability V1 adds three immutable output surfaces.

### PressureStateV1

One causal state exists for each admitted:

    year
    location
    demand-pressure channel

The record exposes:

    opening_pressure
    decay
    decayed_pressure
    required
    available
    unmet_demand
    gain
    added_pressure
    prequalification_pressure
    discharge
    closing_pressure
    unit
    stable pressure_state_id

For the causal Demand/Pressure V1 path:

    decayed_pressure
      = opening_pressure * decay

    added_pressure
      = unmet_demand * gain

    prequalification_pressure
      = decayed_pressure + added_pressure

    discharge
      = 0

    closing_pressure
      = prequalification_pressure

There is no arbitrary project-commitment pressure discharge in the causal path.

Capacity relief acts through later changes to unmet demand. Remembered pressure then
decays according to the channel decay parameter.

### PressureContributionV1

Quantified contributions retain the components that produced a demand/pressure state.

Current causal component types include:

    STATE_DRIVER
    STRATEGIC_REQUIREMENT
    PENDING_PROJECT_REQUIREMENT
    INSTALLED_CAPACITY

Requirement contributions have sign +1.

Installed capacity is recorded with sign -1.

Each contribution records:

    contribution_id
    pressure_state_id
    year
    location
    component_type
    source_id
    quantity
    unit
    sign
    pressure semantics
    channel identity

Demand/Pressure V1 remains the authority for deriving the requirement. The
observability layer consumes its quantified components rather than reimplementing
the demand equation independently.

### PressureQualificationV1

Every project opportunity reaching the pressure-screening stage can record:

    qualification_id
    year
    actor
    location
    project archetype
    qualification threshold
    pressure-qualified true/false
    controlling ratio
    controlling channel
    all channel ratios
    optional linked decision_id
    selected true/false

For each project output channel c:

    channel_ratio(c)
      = pressure(c) / project_output_capacity(c)

The controlling ratio is:

    max(channel_ratio)

The current Hybrid threshold remains:

    0.55

A project is pressure-qualified when:

    controlling_ratio >= 0.55

For a multi-output project, all applicable channel ratios are retained, not merely
the winner.

A channel outside the current pressure scope may appear with zero pressure and no
pressure_state_id. This does not fabricate a pressure state that never existed.

## Decision provenance

When an actor commits a project, the selected decision is linked back to the exact
PressureQualificationV1 record through:

    decision_id

The validator requires:

- the qualification to be above threshold;
- actor, year, location and project identity to match the decision;
- the decision to be COMMIT_PROJECT / COMMITTED;
- one selected pressure qualification per committed project;
- no selected qualification without a real decision.

This yields a direct machine-readable trace:

    pressure state(s)
        -> qualification record
        -> committed decision

The real seed-42 AUS baseline contains no pressure-qualification records because no
ordinary project opportunity survives the already-closed actor/access/capability
constraints far enough to be pressure-screened.

Hostile bounded fixtures exercise both below-threshold qualification and successful
qualification linked to a committed project.

## Causal pressure semantics

Current production-facing semantics are:

    CAUSAL_DEMAND_CHANNEL_PRESSURE

The unit is the unit of the underlying channel:

    HABITAT      person
    TRANSPORT    tonnes/year
    INDUSTRIAL   tonnes/year
    RESOURCE     tonnes/year
    POWER        MW

The ledger validates the exact arithmetic independently against Hybrid's internal
pressure result.

Any difference greater than the deterministic comparison tolerance fails the run.

## Historical Method Lab semantics

Historical Method Lab uses a different pressure mechanism:

    LEGACY_PROJECT_PRESSURE

It operates on project-specific synthetic structural signals and historically used:

    pressure
      = decay * opening_pressure
      + gain * structural_signal

followed, after a project commitment, by:

    pressure
      = max(
          0,
          pressure
          - project_capital_cost * pressure_discharge
        )

with the historical:

    pressure_discharge = 0.85

Pressure Observability V1 does not normalize this into the causal model.

When explicitly enabled on a historical Method Lab fixture, it records:

- LEGACY_PROJECT_PRESSURE semantics;
- the legacy structural signal;
- the legacy pressure transition;
- the exact historical discharge;
- the resulting closing pressure.

This preserves the difference between the historical regression mechanism and the
current causal Demand/Pressure V1 mechanism.

## Stable identity

Pressure states, contributions and qualifications receive stable content/scoped IDs.

The IDs are derived from their semantic identity, year and relevant scope rather
than from insertion order.

Observability therefore does not consume random numbers and does not perturb keyed
stochasticity.

## Validation

The common result validator requires, where Pressure Observability V1 is enabled:

- unique pressure-state IDs;
- exact pressure arithmetic reconstruction;
- valid year/location/channel/project scope;
- causal channel-unit agreement;
- causal discharge equal to zero;
- legacy discharge explicitly represented;
- contribution-to-state referential integrity;
- qualification-to-pressure-state referential integrity;
- controlling ratio consistency;
- threshold consistency;
- exact selected decision provenance;
- every committed project to have one selected pressure trace.

Historical runs without the observability package retain their previous canonical
result hashes.

## Observer-effect regression

GAP-007 contains explicit hostile tests that run otherwise-identical simulations
with and without Pressure Observability V1.

The following behavioral surfaces must remain identical:

    annual_states
    facilities
    decisions
    events
    flows
    missions
    observations
    knowledge_states
    mission_decisions

For the current authoritative seed-42 baseline, GAP-007 additionally compares the
complete pre-existing behavioral arrays against the locked GAP-006 golden.

They are byte-identical.

The only intentional changes are:

- engine/runner/output version envelope;
- implementation fingerprints;
- compiled input hash because the observability package is now part of the governed
  scenario boundary;
- pressure observability configuration and ledger surfaces.

## Current seed-42 ledger

The Earth-Luna 2026-2036 seed-42 baseline emits:

    165 pressure states
    99 quantified pressure contributions
    0 pressure qualifications

All 165 pressure states use:

    CAUSAL_DEMAND_CHANNEL_PRESSURE

All have:

    discharge = 0

The absence of pressure qualifications is not an observability failure.

The current AUS actor has no ordinary project opportunity surviving the closed
actor/accessibility/capability/budget boundaries to the pressure-screening stage.

The bounded hostile fixtures prove the qualification and decision-provenance lane.

### Example: Earth orbit habitat, 2026

The ledger records:

    required            200 person
    available            50 person
    unmet               150 person

    opening pressure       0 person
    decay                  0.60
    decayed pressure       0 person

    gain                   0.24
    added pressure        36 person

    closing pressure      36 person

Contributions identify:

    state:transient_population   +200 person
    state:habitat                 -50 person

### Earth orbit habitat, 2027

The next state reconstructs directly:

    opening pressure       36 person
    decayed pressure       21.6 person
    added pressure         36 person
    closing pressure       57.6 person

The 2026 closing state is therefore visibly the 2027 opening state.

## GAP-007 closure

GAP-007 is closed because the default production-facing path now provides:

1. immutable annual pressure state;
2. quantified causal contributions;
3. inspectable decay, accumulation, gain and discharge semantics;
4. per-opportunity qualification arithmetic and threshold result;
5. exact provenance from a committed project decision to its qualifying pressure
   record;
6. explicit separation of causal and historical legacy pressure semantics;
7. regression proof that observability does not change decisions or random draws.

## What remains open

GAP-007 does not solve:

- physical resource stock, grade, recovery, throughput, inventory or depletion;
- production/value-added accounting;
- power-system closure;
- traffic/fleet utilization;
- site/facility materialization;
- lifecycle/depreciation;
- deeper demography;
- final Atlas-derived metrics.

GAP-008 RESOURCE_MASS_BALANCE is now CLOSED.

The immediate engineering frontier is:

    GAP-009 PRODUCTION_AND_VALUE_ADDED

Pressure observability must remain an audit surface while later mechanisms are
added. It must not become an alternate source of decisions.
