# CIVPROP Engine V1 Executable Baseline

Date: 2026-10-01
Class: class:engineering
Status: locked executable baseline; compiled authority with explicit open-gap assumptions; non-canon; non-production

## Current baseline status

Runner V1.7.0 now defaults to the GAP-001 through GAP-007 compiled authority package
documented in docs/civprop/CIVPROP_INPUT_COMPILER_V1.md,
docs/civprop/CIVPROP_ACTOR_STATE_AND_BUDGETS_V1.md,
docs/civprop/CIVPROP_TRANSPORT_ACCESSIBILITY_V1.md,
docs/civprop/CIVPROP_DEMAND_PRESSURE_V1.md,
docs/civprop/CIVPROP_PROJECT_ECONOMICS_V1.md,
docs/civprop/CIVPROP_MISSIONS_AND_KNOWLEDGE_V1.md and
docs/civprop/CIVPROP_PRESSURE_OBSERVABILITY_V1.md.

The original V1.0 synthetic Method Lab baseline remains preserved as historical
regression evidence. It was not overwritten.

Current default input authority:

    COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

Current gap state begins:

    GAP-001 CLOSED
    GAP-002 CLOSED
    GAP-003 CLOSED
    GAP-004 CLOSED
    GAP-005 CLOSED
    GAP-006 CLOSED
    GAP-007 CLOSED
    GAP-008 through GAP-015 OPEN

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

With no path arguments, the runner uses the GAP-001 through GAP-007 compiled authority package and Infrastructure Archetype V1 catalog.

The runner may later be pointed at another compatible frozen input package with --input-dir and --infrastructure-catalog.

Changing input values is allowed. Changing input meaning is not allowed silently; semantic changes require a versioned input contract.

## Baseline identity

Machine-readable manifest:

    engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP7_BASELINE_MANIFEST.json

Golden output:

    engineering/civprop/baselines/CIVPROP_ENGINE_V1_GAP7_PRESSURE_OBSERVABILITY_SEED42.json

The current baseline contains real promoted authority plus explicit unresolved
synthetic assumptions. It proves execution, contracts, provenance and causal
bookkeeping. It is not yet a production forecast because GAP-008 onward remain open.

The prior V1.0 synthetic manifest/golden files remain preserved as historical
regression artifacts.

## Authority and epistemic status

The current default input authority is:

    COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

The compiled package contains frozen promoted Earth, Solar, Timeline, resource and
actor evidence. Demand/Pressure V1 uses explicit uncalibrated causal parameters,
Project Economics V1 carries versioned physical/economic ranges with scenario-class
components, and Mission/Knowledge V1 carries an uncalibrated binary observation
model. Later open mechanisms remain explicit rather than being silently invented.

The runner exists so those later gaps can be replaced without redesigning the engine
entrypoint.

# Input Contract

The current runtime input is the actor-visible compiled scenario:

    engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/scenario_v1.json

Its runtime SHA-256 is recorded in every output.

The compiled package also contains truth_v1.json. That file remains evaluator-only
synthetic compatibility state. Actor mission/project decisions cannot read hidden
truth. Mission/Knowledge V1 permits exactly one bounded use: when an admitted mission
executes, the observation runtime may read the scoped hidden physical realization to
produce a keyed noisy observation. Actors receive the observation, never the answer
key.

The runner therefore records separately:

    actor_visible_scenario_sha256
    runtime_input_sha256
    evaluator_truth_sha256
    evaluator_truth_consumed_by_engine

For the current seed-42 baseline the final value is false because no mission executes.

The first two hashes are currently identical because the actor-visible scenario is the actual runtime decision input.

## Top-level input fields

### format

Current value: CIVPROP_METHOD_LAB_SCENARIO_V1.

Meaning: schema/semantic identifier for the frozen scenario payload.

### fixture_id

Current value: EARTH_LUNA_COMPILED_AUTHORITY_V1_2026_2036.

Meaning: identity of the frozen input realization. It is not a world/canon ID.

### horizon

Fields: start_year, end_year, snapshot_interval_years.

Current baseline: 2026 through 2036, annual snapshots. The production engine target remains 2026 through 2226.
### classification and units

The current classification is COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1.

This distinguishes promoted/frozen authority from the explicit model assumptions
still owned by open gaps.

Project Economics V1 now uses USD_2026_billion for project capital and physical
capacity units: MW, person and tonnes/year. The legacy location-book-capital field
remains a compatibility value owned by later state/materialization work and is not
relabelled as project capital.

## Actors

The current compiled actor list contains identity/type only and is paired with
CIVPROP_ACTOR_STATE_V1.

For AUS, generic spendable allocation remains UNKNOWN. The observed AUD 42 million
Roo-ver commitment is preserved as a scoped committed fund and cannot finance
unrelated CIVPROP projects.

Ownership, operation, access/contracts, provider-service access, capability and
experience remain distinct actor-state surfaces. The default path does not use the
legacy Method Lab starting_capital or annual_capital_inflow fields.

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

Current development-slice locations are EARTH_SURFACE, EARTH_ORBIT, LUNA_SURFACE
and CISLUNAR_FREE_SPACE.

The Earth-Luna slice proves the mechanism. Full production coverage must broaden the
compiled Solar/location universe before POST-01.

## Technology frontier

Each row contains tech_id and frontier_year.

Meaning: the simulation may begin considering the technology frontier at or after the specified year.

It does not mean every actor owns, can buy or can operate that technology.
Actor capability/access is separate, preserving the Timeline rule DATE_DOES_NOT_UNLOCK.

## Actor capability

The default compiled path uses Actor State V1 rather than legacy generic
actor_capability rows.

Capability status remains distinct from provider access or timeline frontier dates.
A facility opportunity requiring a technology is admitted only when the actor's
versioned capability state resolves to USABLE.

## Accessibility

The default compiled path uses CIVPROP_ACCESSIBILITY_V1 rather than annual synthetic
accessibility profiles.

The service preserves:

    FEASIBLE
    INFEASIBLE
    UNKNOWN

and separates qualified Solar geometry, scoped provider/service access and
decomposed generalized cost. Body-center separation is context, not route length.
UNKNOWN does not become zero cost, impossibility or generic actor entitlement.

Historical Method Lab accessibility profiles remain supported only for regression
compatibility.
## Resource beliefs

Each current belief contains resource_id, location_id, evidence_status, prior_probability, observation_sensitivity and false_positive_probability.

Hybrid V1 uses actor-scoped knowledge where a resource-producing project is considered.

Mission/Knowledge V1 can execute admitted missions, generate keyed noisy observations,
apply deterministic Bayesian updates and hand the posterior to later project scoring.

Hidden truth remains prohibited from actor decisions. Only the observation runtime may
read evaluator-only physical realization when an admitted mission executes.

## Demand / Pressure V1

The default compiled path no longer contains annual demand_signals.

Instead it carries CIVPROP_DEMAND_PRESSURE_V1. Requirements are derived from current
off-world civilization state plus explicit scoped strategic requirements and pending
project prerequisites. Installed capacity satisfies those requirements; only unmet
demand adds pressure.

The current channels are HABITAT, TRANSPORT, INDUSTRIAL, RESOURCE and POWER. Each
channel declares its unit, state drivers, installed-capacity field, pressure gain and
decay. Current coefficients are UNCALIBRATED_CAUSAL_MODEL_PARAMETER_V1, not empirical
forecasts.

Historical Method Lab fixtures retain OFFWORLD_* and WATER_RESOURCE_DEMAND only for
regression compatibility; the default compiled authority path does not consume them.

## Runtime project archetypes

Each project row contains project_archetype_id, project_kind, allowed_placements,
required_tech and a start-year resolved view of cost, lag, output and prerequisite
capacity.

The default runner validates facility semantics against Infrastructure Archetype V1
and validates the numeric project layer against CIVPROP_PROJECT_ECONOMICS_V1. Project
economics are then resolved again at the actual opportunity year, so technology-year
adjustments are consumed rather than merely documented.

Historical Method Lab fixtures still validate against METHOD_LAB_SYNTHETIC_V1 for
regression only.

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

For each year on the default causal path Hybrid V1 performs, in order:

    YEAR_STARTED
    1. apply actor-budget events
    2. commission projects whose lag has completed
    3. derive state-driven requirements plus pending-project prerequisites
    4. subtract installed capacity to obtain unmet demand
    5. decay prior channel pressure and add current unmet demand
    6. generate currently feasible opportunities
    7. pressure-qualify projects against the capacity channels they would add
    8. actors rank qualified affordable opportunities
    9. actors COMMIT_PROJECT or WAIT
    10. emit annual location snapshots
    YEAR_COMPLETED

The historical Method Lab path retains its original exogenous-demand and pressure
logic only for regression compatibility.

At the end of the horizon the runner emits RUN_COMPLETED.

## Pressure semantics

Pressure represents remembered unmet requirement in a declared channel and therefore
carries that channel's unit.

For the causal path:

    pressure[t] = decay * pressure[t-1] + gain * unmet_demand[t]

Capacity relief removes new unmet demand; remembered pressure then decays. The current
gain/decay coefficients are versioned model parameters, not calibrated social laws.

A project is qualified by comparing channel pressure with the capacity that project
would add in the same channel. Pressure alone never creates infrastructure: actor
capability, accessibility, affordability and selection still apply.

Pressure Observability V1 now emits immutable annual pressure state, quantified
causal contributions and per-opportunity qualification traces. The audit lane mirrors
and verifies Hybrid arithmetic without feeding decisions or random draws.

## Actor decision semantics

A major project requires feasible placement, usable actor capability, feasible accessibility, local prerequisite capacity, sufficient actor budget, qualified structural pressure and actor selection.

Actor ranking uses explicit code and keyed stochasticity. There is no LLM/Codex/Sol runtime authority.
## Capital semantics

Current Method Lab accounting is:

    actor budget: debited at project commitment
    location capital: increased by project capital_cost at commissioning

Actor budget balances are currently internal and are not emitted.

Project commitments on the default path use USD_2026_billion from Project Economics V1. The separate legacy location-capital compatibility field is not a production currency or actor budget.

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
    mission_decisions
    missions
    observations
    knowledge_states
    events
    flows

Current format: CIVPROP_ENGINE_V1_OUTPUT.
Current contract version: 1.7.0.

## Metadata

metadata.runner records runner id and version. Current values are CIVPROP_ENGINE_V1_RUNNER and 1.7.0.

metadata.engine records engine id/version, deterministic run_id, seed and horizon. Current default engine is HYBRID_V1 / method-reference-v5.

metadata.inputs records fixture_id, scenario_format, Method Lab manifest/bundle hashes, actor-visible scenario hash, runtime input hash, evaluator-truth hash, observation-only access policy and whether evaluator truth was actually consumed in the run, plus input authority and provenance basis.

method_lab_bundle_sha256 identifies the complete evaluation package. runtime_input_sha256 identifies the actor-visible runtime scenario. They are intentionally separate.

metadata.infrastructure records catalog id/format/hash, parameter-set id/status and parameterized archetypes.
metadata.implementation pins SHA-256 values for the runner, hybrid engine, shared helpers, Method Lab contracts, infrastructure, actor-state, accessibility, demand/pressure, project-economics, mission/knowledge and pressure-observability contracts plus the mission and pressure-lane adapters.

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
    GAP-003 TRANSPORT_ACCESSIBILITY               CLOSED
    GAP-004 DEMAND_AND_PRESSURE_MODEL              CLOSED
    GAP-005 PROJECT_ECONOMICS                      CLOSED
    GAP-006 MISSIONS_AND_KNOWLEDGE_UPDATE          CLOSED
    GAP-007 PRESSURE_OBSERVABILITY                 CLOSED
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

The current GAP-007 pressure-observability seed-42 baseline produces:

    44 annual location-state rows
    11 annual actor-state rows
    0 commissioned facilities
    11 project decisions
    11 mission decisions
    1 actor-visible knowledge state
    0 missions
    0 observations
    0 actor transactions
    46 events
    0 migration flows
    165 pressure-state rows
    99 pressure-contribution rows
    0 pressure-qualification rows

All 11 project decisions are WAIT and all 11 mission decisions are WAIT. The current
AUS actor retains a private lunar-water prior at probability 0.45, but generic
spendable allocation is UNKNOWN, the mission path remains unresolved, and the
follow-on resource-project success value is explicitly UNKNOWN. No mission therefore
executes and evaluator truth is not consumed in the golden run.

Zero missions is thus a constraint result, not a dead mission subsystem. Hostile
fixtures separately prove the commit -> execute -> observe -> Bayes-update path.

All 165 default pressure states are causal channel pressure with zero synthetic
discharge. The current AUS path produces no pressure-qualification rows because no
ordinary project opportunity survives the already-closed actor/accessibility/
capability/budget boundaries to pressure screening. Bounded hostile fixtures prove
below-threshold and selected-decision qualification tracing.

All pre-existing GAP-006 behavioral arrays are byte-identical under GAP-007.

No significance should be attached to those numbers as a forecast.

The golden output asks only: did the same executable contract still produce the same
result from the same pinned inputs, implementation and seed?

# Baseline Metadata and Hashes

Authoritative current machine-readable values live in CIVPROP_ENGINE_V1_GAP7_BASELINE_MANIFEST.json. GAP-006, GAP-005, GAP-004, GAP-003, GAP-002, GAP-001 and earlier synthetic manifests remain historical evidence.

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
