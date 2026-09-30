# CIVPROP Engine V1 Executable Baseline

Date: 2026-09-30
Class: class:engineering
Status: locked executable baseline; compiled authority with explicit open-gap assumptions; non-canon; non-production

## Current baseline status

Runner V1.2.0 now defaults to the GAP-001/GAP-002 compiled authority package
documented in docs/civprop/CIVPROP_INPUT_COMPILER_V1.md and
docs/civprop/CIVPROP_ACTOR_STATE_AND_BUDGETS_V1.md.

The original V1.0 synthetic Method Lab baseline remains preserved as historical
regression evidence. It was not overwritten.

Current default input authority:

    COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

Current gap state begins:

    GAP-001 CLOSED
    GAP-002 CLOSED
    GAP-003 through GAP-015 OPEN

## Purpose

This document freezes one complete, tested Python path from declared inputs to declared outputs for the selected CIVPROP Engine V1 architecture.

The purpose is not to claim that every CIVPROP submodel is finished. The purpose is to stop moving the executable boundary while the missing scientific, economic and authority inputs are filled in behind it.

Locked entrypoint:

    engineering/civprop/run_civprop_v1.py

Conceptually:

    frozen input package
    + infrastructure semantic catalog
    + deterministic seed
            ->
    CIVPROP Engine V1 runner
            ->
    HYBRID_V1 propagation
            ->
    CIVPROP_ENGINE_V1_OUTPUT
The selected engine architecture remains:

    annual dynamic-recursive skeleton
            +
    decaying system-dynamics pressure
            +
    actor/event decisions for major commitments

## One command

From repository root:

    python3 engineering/civprop/run_civprop_v1.py       --seed 42       --output /tmp/civprop_v1.json

With no path arguments, the runner uses the GAP-001/GAP-002 compiled authority package and Infrastructure Archetype V1 catalog.

The runner may later be pointed at another compatible frozen input package with --input-dir and --infrastructure-catalog.

Changing input values is allowed. Changing input meaning is not allowed silently; semantic changes require a versioned input contract.

## Baseline identity

Machine-readable manifest:

    engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP2_BASELINE_MANIFEST.json

Golden output:

    engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP2_ACTOR_STATE_SEED42.json

The current baseline contains real promoted authority plus explicit unresolved
synthetic assumptions. It proves execution, contracts, provenance and causal
bookkeeping. It is not yet a production forecast because GAP-003 onward remain open.

The prior V1.0 synthetic manifest/golden files remain preserved as historical
regression artifacts.

## Authority and epistemic status

The current default input authority is:

    COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

The compiled package contains frozen promoted Earth, Solar, Timeline, resource and
actor evidence. It remains non-canon and non-production because budgets,
accessibility, demand, project economics and other downstream models remain explicit
placeholders.

The runner exists so those later gaps can be replaced without redesigning the engine
entrypoint.

# Input Contract

The current runtime input is the actor-visible compiled scenario:

    engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json

Its runtime SHA-256 is recorded in every output.

The compiled package also contains truth_v1.json. That file remains evaluator-only
synthetic compatibility state. HYBRID_V1 does not read hidden truth for decisions or
state transitions.

The runner therefore records separately:

    actor_visible_scenario_sha256
    runtime_input_sha256
    evaluator_truth_sha256
    evaluator_truth_consumed_by_engine = false

The first two hashes are currently identical because the actor-visible scenario is the actual runtime decision input.

## Top-level input fields

### format

Current value: CIVPROP_METHOD_LAB_SCENARIO_V1.

Meaning: schema/semantic identifier for the frozen scenario payload.

### fixture_id

Current value: EARTH_ORBIT_LUNA_SYNTHETIC_V1.

Meaning: identity of the frozen input realization. It is not a world/canon ID.

### horizon

Fields: start_year, end_year, snapshot_interval_years.

Current baseline: 2026 through 2036, annual snapshots. The production engine target remains 2026 through 2226.
### classification and units

The fixture classification is SYNTHETIC_METHOD_FIXTURE_NOT_CANON_NOT_EMPIRICAL.

This prevents fixture quantities from acquiring fake authority.

Units include synthetic values such as scenario_credit, scenario_capacity_unit and scenario_cost_index. These are not monetary or engineering units suitable for production use.

## Actors

Each actor input contains:

    actor_id
    actor_type
    starting_capital
    annual_capital_inflow

actor_id is stable within the run. actor_type is the bounded preference label used by Method Lab actor weighting. starting_capital and annual_capital_inflow are synthetic spendable run budgets.

Current actor capital is not GDP, national capital stock, government appropriation or observed corporate cash. Production CIVPROP still needs a qualified actor-state/budget bridge.

## Locations

Each location contains:

    location_id
    parent_body_id
    placement
    initial_state
Current placement enum:

    SURFACE
    ORBITAL
    FREE_SPACE

initial_state contains biological_population, transient_population, workforce, capital and capacities.

Current capacity dimensions:

    power
    resource
    industrial
    habitat
    shipyard
    transport

These are logical engine dimensions. Except where later explicitly calibrated, they are not automatically physical MW, tonnes/year, berths/year or equivalent real units.

Current fixture locations are EARTH_SURFACE, EARTH_ORBIT, LUNA_SURFACE and CISLUNAR_FREE_SPACE.

Production CIVPROP must replace these with a compiled Solar/location universe.

## Technology frontier

Each row contains tech_id and frontier_year.

Meaning: the simulation may begin considering the technology frontier at or after the specified year.

It does not mean every actor owns, can buy or can operate that technology.
Actor capability/access is separate, preserving the Timeline rule DATE_DOES_NOT_UNLOCK.

## Actor capability

Each row contains actor_id, tech_id, status, valid_from, valid_to and conditions.

Current status vocabulary:

    USABLE
    CONDITIONAL
    UNUSABLE
    UNKNOWN

The Hybrid V1 baseline admits a facility opportunity only when required capability resolves to USABLE.

## Accessibility

Each profile contains origin_location_id, destination_location_id and annual rows containing year, status and generalized_cost.

Current status vocabulary:

    FEASIBLE
    INFEASIBLE
    UNKNOWN

UNKNOWN is preserved and does not become zero-cost or impossible.

For the Method Lab, generalized cost is a synthetic scalar used for opportunity screening. It is not yet a production transport tariff, delta-v, time or risk metric.
## Resource beliefs

Each current belief contains resource_id, location_id, evidence_status, prior_probability, observation_sensitivity and false_positive_probability.

Hybrid V1 currently uses the actor-visible probability where a resource-producing project is considered.

The executable baseline does not yet execute prospecting missions or update this belief using CIVPROP-0 observation/Bayesian mechanics.

Hidden truth remains prohibited from actor decisions.

## Demand signals

Current fixture signals include OFFWORLD_TRANSPORT_DEMAND, OFFWORLD_INDUSTRIAL_DEMAND, OFFWORLD_HABITAT_INTEREST and WATER_RESOURCE_DEMAND.

Each contains signal_id, unit and annual year/value pairs.

These are deliberate Method Lab fixtures. They are not the production demand model.

Production CIVPROP must derive demand/pressure causally from state such as population, production, trade, scarcity, accessibility, infrastructure and strategic commitments.

## Runtime project archetypes

Each project row contains project_archetype_id, project_kind, allowed_placements, required_tech, capital_cost, construction_lag_years, output_capacities and minimum_input_capacities.
The runner validates every FACILITY row against Infrastructure Archetype V1 and the METHOD_LAB_SYNTHETIC_V1 parameter set before running.

This prevents semantic drift between the old Method Lab project rows and the infrastructure contract.

PROSPECTING_SURVEY is a MISSION, not infrastructure, and is intentionally outside the infrastructure catalog.

# Infrastructure Semantic Input

The second input surface is:

    engineering/civprop/contracts/infrastructure_archetypes_v1.json

Catalog identity:

    CIVPROP_INFRASTRUCTURE_ARCHETYPES_V1

Current semantic modules:

    SURFACE_PORT
    LOGISTICS_NODE
    POWER_PLANT
    HABITAT
    RESOURCE_PLANT
    INDUSTRIAL_WORKSHOP
    SHIPYARD

An archetype is a reusable capacity-bearing module, not a named Atlas facility.
Current numeric Method Lab parameterization exists only for LOGISTICS_NODE, POWER_PLANT, HABITAT, RESOURCE_PLANT and INDUSTRIAL_WORKSHOP.

SURFACE_PORT and SHIPYARD are deliberately unparameterized rather than assigned invented costs merely to make them executable.

# Seed Semantics

The --seed integer controls declared keyed stochastic choices.

Required reproducibility rule:

    same runtime input
    + same infrastructure catalog
    + same implementation
    + same seed
    = byte-equivalent logical output

Randomness is keyed so unrelated evaluation order should not silently redefine history.

# Engine Execution Semantics

For each year Hybrid V1 performs, in order:

    YEAR_STARTED
    1. replenish actor synthetic capital after the first year
    2. commission projects whose lag has completed
    3. decay prior structural pressure
    4. generate currently feasible opportunities
    5. add current structural signal to pressure
    6. pressure-qualify opportunities
    7. actors rank qualified affordable opportunities
    8. actors COMMIT_PROJECT or WAIT
    9. apply bounded source-debited migration
    10. emit annual location snapshots
    YEAR_COMPLETED

At the end of the horizon the runner emits RUN_COMPLETED.

## Pressure semantics

Pressure represents accumulated structural incentive/need for a location/project pair.

Current reference constants are implementation details, not calibrated social laws.

Important invariant: pressure decays. A weak positive signal cannot accumulate forever after the underlying condition disappears.

Pressure alone never creates infrastructure. It must qualify an opportunity, after which an eligible actor still decides whether to commit.

Pressure values are currently internal. Only qualification events are emitted.

## Actor decision semantics

A major project requires feasible placement, usable actor capability, feasible accessibility, local prerequisite capacity, sufficient actor budget, qualified structural pressure and actor selection.

Actor ranking uses explicit code and keyed stochasticity. There is no LLM/Codex/Sol runtime authority.
## Capital semantics

Current Method Lab accounting is:

    actor budget: debited at project commitment
    location capital: increased by project capital_cost at commissioning

Actor budget balances are currently internal and are not emitted.

The synthetic scenario_credit is not a production currency.

## Population semantics

Current executable baseline has no births/deaths. Population changes only by migration.

Migration is source-debited, habitat-constrained, job/capacity-constrained and accessibility-constrained. Total biological population is therefore conserved in the current fixture.

This is not yet cohort demography.

## Workforce semantics

Workforce behavior is the Method Lab placeholder rule. It is not the final labor-market, skills, remote-work, synthetic-labor or machine-task model.

## Facility semantics

A facility appears in facilities output only after commissioning.

A committed but unfinished project exists only in decisions/events and the internal pending-project queue.

Current facility capital is the synthetic project capital cost assigned when commissioned.

Infrastructure is generic module state, not final Atlas naming/materialization.
# Output Contract

Top-level output fields:

    format
    contract_version
    metadata
    semantics
    known_gaps
    annual_states
    facilities
    decisions
    events
    flows

Current format: CIVPROP_ENGINE_V1_OUTPUT.
Current contract version: 1.0.0.

## Metadata

metadata.runner records runner id and version. Current values are CIVPROP_ENGINE_V1_RUNNER and 1.0.0.

metadata.engine records engine id/version, deterministic run_id, seed and horizon. Current engine is HYBRID_V1 / method-reference-v1.

metadata.inputs records fixture_id, scenario_format, Method Lab manifest/bundle hashes, actor-visible scenario hash, runtime input hash, evaluator-truth hash and non-consumption flag, input authority and provenance basis.

method_lab_bundle_sha256 identifies the complete evaluation package. runtime_input_sha256 identifies the actor-visible runtime scenario. They are intentionally separate.

metadata.infrastructure records catalog id/format/hash, parameter-set id/status and parameterized archetypes.
metadata.implementation pins SHA-256 values for the runner, hybrid engine, shared helpers, Method Lab contracts and infrastructure contract.

The purpose is reproducibility independent of a vague statement such as "current main."

# Annual State Output

One row exists for every location and every annual snapshot.

Fields:

    year
    location_id
    biological_population
    transient_population
    workforce
    capital
    capacities

capacities contains power, resource, industrial, habitat, shipyard and transport.

Current snapshot timing is END_OF_YEAR_AFTER_DUE_COMMISSIONING_DECISIONS_AND_MIGRATION.

Annual state is engine state, not final Atlas display state.

# Facility Output

Each commissioned facility contains facility_id, project_archetype_id, location_id, owner_actor_id, committed_year, commissioned_year, status, capital and capacities.

facility_id is deterministic for the Method Lab engine path.

The facility is a generated infrastructure module instance. It is not yet a named settlement, final Atlas facility type, surface coordinate, orbital-element record or complete industrial balance sheet.
# Decision Output

Fields:

    decision_id
    year
    actor_id
    action
    target_location_id
    project_archetype_id
    status
    rationale_codes

Current actions are COMMIT_PROJECT and WAIT.

A decision expresses actor action, not hidden physical truth.

# Event Output

Fields:

    event_id
    year
    event_type
    actor_id
    location_id
    parent_event_ids

Current relevant events include RUN_STARTED, YEAR_STARTED, OPPORTUNITY_PRESSURE_QUALIFIED, DECISION_MADE, PROJECT_COMMITTED, FACILITY_COMMISSIONED, MIGRATION_APPLIED, YEAR_COMPLETED and RUN_COMPLETED.

Current Method Lab recorder creates an append-order parent chain using the previous event ID. This is replay scaffolding, not yet the final richer event DAG.

# Flow Output

Fields are flow_id, year, flow_type, origin_location_id, destination_location_id, amount, unit and actor_id.

Current executable baseline emits migration flows only.
Future material, freight, passenger, energy or financial flows are not part of the current locked semantics.

# Embedded Semantics and Gap Register

Every output carries a semantics object so a detached data file still declares important meaning: snapshot timing, engine architecture, no-LLM rule, hidden-truth firewall, timeline/capability separation, UNKNOWN handling, pressure decay, commitment semantics, capital accounting, population conservation, flow scope and Atlas boundary.

Every output also carries explicit known_gaps.

Current gap status:

    GAP-001 REAL_INPUT_COMPILER                    CLOSED
    GAP-002 ACTOR_STATE_AND_BUDGETS               CLOSED
    GAP-003 TRANSPORT_ACCESSIBILITY               OPEN
    GAP-004 DEMAND_AND_PRESSURE_MODEL              OPEN
    GAP-005 PROJECT_ECONOMICS                      OPEN
    GAP-006 MISSIONS_AND_KNOWLEDGE_UPDATE          OPEN
    GAP-007 PRESSURE_OBSERVABILITY                 OPEN
    GAP-008 RESOURCE_MASS_BALANCE                  OPEN
    GAP-009 PRODUCTION_AND_VALUE_ADDED             OPEN
    GAP-010 POWER_BALANCE                          OPEN
    GAP-011 TRAFFIC_AND_FLEET                      OPEN
    GAP-012 FACILITY_AND_SITE_MATERIALIZATION      OPEN
    GAP-013 MAINTENANCE_DEPRECIATION_RETIREMENT    OPEN
    GAP-014 DEMOGRAPHIC_DEPTH                      OPEN
    GAP-015 ATLAS_DERIVED_METRICS                  OPEN

The authoritative program register, detailed exit criteria and post-gap handoff are:

    engineering/civprop/gap_register_v1.json
    docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md

The gaps are part of output metadata so a future result cannot plausibly be mistaken
for a more complete simulation than it is.

# Golden Seed-42 Baseline

The current GAP-002 actor-state seed-42 baseline produces:

    44 annual location-state rows
    11 annual actor-state rows
    0 commissioned facilities
    11 actor decisions
    0 actor transactions
    45 events
    10 migration flows

All 11 current actor decisions are WAIT because generic AUS spendable allocation
remains UNKNOWN and generic Method Lab capability grants have been removed. This is
the intended consequence of closing GAP-002, not a forecast that Australia will
never develop off-world capability.

No significance should be attached to those numbers as a forecast.

The golden output asks only: did the same executable contract still produce the same
result from the same pinned inputs, implementation and seed?

# Baseline Metadata and Hashes

Authoritative current machine-readable values live in CIVPROP_ENGINE_V1_GAP2_BASELINE_MANIFEST.json. GAP-001 and earlier synthetic manifests remain historical evidence.

The manifest pins source-basis commit, runner and engine identities, output-contract version, runtime-input and evaluator-truth hashes, infrastructure catalog and parameter set, implementation source hashes, golden-output hashes/counts, and change-control rules.
# Change Control

A value-only input change gets a new frozen input hash and new golden result. The semantic contract may remain V1 if field meaning is unchanged.

An input semantic change requires a versioned input contract. Do not silently reuse the old field.

An engine algorithm change requires an engine-version bump, new implementation hashes and a new golden baseline.

An output semantic/envelope change requires a runner and/or output-contract version bump.

An infrastructure semantic change requires a versioned infrastructure catalog while preserving historical V1 meaning.

No silent rewrites: old inputs + old engine + old seed remain a reproducible historical simulation artifact.

# Relationship to the Future Atlas

The executable output is upstream of Atlas materialization.

The eventual materializer should derive or aggregate celestial-body state, surface and orbital sites, named facilities, settlements, owners/operators/institutions, biological/synthetic/transient population, workforce, capital, value added, power, habitat, resource production, cargo/passenger flows, ship calls, network centrality and strategic significance.

Strategic significance, economic centrality and transport centrality should be derived from actual generated state rather than fed back as primitive importance scores.

Infrastructure modules may be colocated and materialized into richer Atlas facility types. For example LOGISTICS_NODE + HABITAT may later materialize as an orbital habitat/port. The engine does not pre-author the named Ceres facility.

# What We Fill In Next

The executable boundary is now the thing to preserve.
From here, replace synthetic input components one at a time while keeping the runner and output envelope stable where semantics permit.

The real-input compiler is now closed as GAP-001.

The immediate continuation is GAP-002 ACTOR_STATE_AND_BUDGETS. The complete work
queue, exit criteria, dependency guidance and the seven post-gap gates are recorded
in:

    engineering/civprop/gap_register_v1.json
    docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md

A gap is complete only when its replacement has defined semantics, units where
applicable, authority/model provenance, tests and deterministic handoff to this
runner.

This remains the executable stake in the ground.
