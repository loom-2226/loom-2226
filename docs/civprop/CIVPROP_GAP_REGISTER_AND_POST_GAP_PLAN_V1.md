# CIVPROP Gap Register and Post-Gap Plan V1

Date: 2026-09-30
Class: class:engineering
Status: current program register and post-gap handoff plan

## Authority boundary

This document records the CIVPROP program state through GAP-004 closure.

Authoritative repository basis at creation:

    53cca0679f6e2bdd8aa8b3be22b387136bfe1bc3

Machine-readable register:

    engineering/civprop/gap_register_v1.json

The machine-readable register is the canonical inventory of gap IDs, names,
meanings, current status, exit criteria, evidence, next action, affected contracts,
and the ordered post-gap gates.

The executable remains:

    engineering/civprop/run_civprop_v1.py

Current default runtime package:

    engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/

Current runner/output contract:

    CIVPROP_ENGINE_V1_RUNNER 1.4.0
    CIVPROP_ENGINE_V1_OUTPUT 1.4.0

Current engine:

    HYBRID_V1 method-reference-v2

Current input authority:

    COMPILED_AUTHORITY_WITH_EXPLICIT_OPEN_GAP_ASSUMPTIONS_V1

## Where we stand now

The architecture question is closed for Engine V1.

The selected propagation method is:

    annual dynamic-recursive skeleton
            +
    decaying system-dynamics pressure
            +
    actor/event decisions for major commitments

The engine has one tested executable path from frozen inputs to complete output.

GAP-001 is CLOSED: promoted Earth, Solar, Timeline, resource and actor evidence can
now be captured read-only, frozen with provenance, and deterministically compiled
into the locked runner envelope.

GAP-002 is also CLOSED. Actor State V1 now separates scoped rights/contracts,
capability, experience, committed funds and generic spendable allocation. The old
AUS scenario-credit and generic-capability placeholders are gone; unsupported
generic spendable allocation remains explicitly UNKNOWN.

GAP-003 is CLOSED. Accessibility V1 now separates qualified Solar geometry,
scoped provider/service access and decomposed generalized cost while preserving
FEASIBLE/INFEASIBLE/UNKNOWN. The synthetic default accessibility curves are gone.

GAP-004 is CLOSED. Demand/Pressure V1 derives off-world requirements from current
civilization state and explicit scoped commitments, subtracts installed capacity and
carries unmet demand into decaying unit-preserving pressure. The default annual
OFFWORLD_* and WATER_RESOURCE_DEMAND curves are gone.

The current baseline is still not a forecast because GAP-005 through GAP-015 remain
open. The demand coefficients are uncalibrated causal model parameters, project
economics remain synthetic, and later mechanisms materially affect the result. The
default seed-42 baseline remains an engineering regression/reference artifact, not a
2036 prediction or 2226 canon.

## Closure semantics

CLOSED means:

> A tested, versioned mechanism exists that is adequate for the current CIVPROP
> development boundary.

CLOSED does not mean:

> Every future production-scale value, actor, destination and century has already
> been empirically calibrated.

OPEN means:

> The current executable still contains a placeholder, missing state/output, or
> incomplete production mechanism owned by that gap.

A gap may close only when its replacement has:

- explicit semantics;
- units where quantities exist;
- authority or model provenance;
- deterministic handoff/replay;
- tests;
- no silent conversion of UNKNOWN into zero or certainty;
- no hidden-truth leakage;
- change-control/versioning where meaning changes.

## Current gap status

| Gap | Name | Status | Immediate objective |
|---|---|---|---|
| GAP-001 | REAL_INPUT_COMPILER | CLOSED | Preserve compiler boundary; broaden coverage later without semantic drift |
| GAP-002 | ACTOR_STATE_AND_BUDGETS | CLOSED | Preserve Actor State V1 semantics; proceed without inventing budget or capability |
| GAP-003 | TRANSPORT_ACCESSIBILITY | CLOSED | Preserve scoped physics/service tri-state semantics; no inferred routes or entitlements |
| GAP-004 | DEMAND_AND_PRESSURE_MODEL | CLOSED | Preserve state-derived/unit-preserving demand semantics; no authored annual curves |
| GAP-005 | PROJECT_ECONOMICS | OPEN | Replace synthetic costs/lags/capacity units with versioned parameter sets |
| GAP-006 | MISSIONS_AND_KNOWLEDGE_UPDATE | OPEN | Integrate prospecting/observation/Bayesian knowledge evolution |
| GAP-007 | PRESSURE_OBSERVABILITY | OPEN | Emit or reconstruct pressure state and causal components |
| GAP-008 | RESOURCE_MASS_BALANCE | OPEN | Add stock/grade/yield/throughput/inventory/depletion closure |
| GAP-009 | PRODUCTION_AND_VALUE_ADDED | OPEN | Generate off-world production, capital, investment and value added |
| GAP-010 | POWER_BALANCE | OPEN | Add generation/load/storage/reserve/energy closure |
| GAP-011 | TRAFFIC_AND_FLEET | OPEN | Generate cargo/passenger/ship-call/fleet/route utilization state |
| GAP-012 | FACILITY_AND_SITE_MATERIALIZATION | OPEN | Convert modules into stable sites, orbitals, facilities and settlements |
| GAP-013 | MAINTENANCE_DEPRECIATION_RETIREMENT | OPEN | Add asset lifecycle, replacement, failure and retirement |
| GAP-014 | DEMOGRAPHIC_DEPTH | OPEN | Add cohorts, births/deaths, synthetic persons, labor and settlement viability |
| GAP-015 | ATLAS_DERIVED_METRICS | OPEN | Derive centrality/strategic/display metrics from generated state |

Detailed exit criteria and current evidence live in
engineering/civprop/gap_register_v1.json and are regression-tested against the
locked runner's gap definitions/status.

## Gap dependencies and practical order

The numeric order remains the tracking identity, not an absolute ban on parallel
work. The practical dependency structure is:

    GAP-002 actor state/budgets
        |
        +---------------------+
        |                     |
        v                     v
    GAP-003 transport     GAP-005 project economics
        |                     |
        +----------+----------+
                   |
                   v
              GAP-004 demand/pressure
                   |
          +--------+--------+
          |                 |
          v                 v
      GAP-006           GAP-007
      missions          pressure audit
          |
          v
      GAP-008 resources
          |
          +-------------+
          |             |
          v             v
      GAP-009        GAP-010
      economy        power
                       /
                      /
            v         v
             GAP-011 traffic/fleet
                    |
                    v
             GAP-012 materialization
                    |
          +---------+---------+
          |                   |
          v                   v
      GAP-013             GAP-014
      lifecycle           demography
                             /
                            /
            +-------+-------+
                    |
                    v
             GAP-015 Atlas metrics

This diagram is guidance, not a claim that every edge is mathematically mandatory.
Work may proceed in parallel where contracts are stable.

## GAP-001 closure reference

GAP-001 is represented by:

    engineering/civprop/compile_inputs_v1.py
    engineering/civprop/inputs/authority_capture_v1.json
    engineering/civprop/compiled_inputs/earth_luna_2026_2036_v1/
    engineering/civprop/test_compile_inputs_v1.py
    docs/civprop/CIVPROP_INPUT_COMPILER_V1.md

The current compiled package proves the mechanism on the Earth-Luna 2026-2036
development slice.

Before the first full 2026-2226 production run, compiler coverage must broaden to
the required Solar/body/actor universe. That is a scale/coverage extension of the
closed compiler mechanism, not permission to silently redefine input semantics.

## What is deliberately not a gap anymore

The following questions are no longer blockers:

- Which broad propagation technique should V1 use?
- Should an LLM reason inside authoritative runtime propagation?
- Should the Ceres Atlas be treated as the answer sheet?
- Should infrastructure be generic modules or pre-authored named facilities?
- Can real LOOM authority be fed to the same runner?
- Can old synthetic baselines remain reproducible while inputs improve?

Current answers are fixed for V1:

- Hybrid dynamic-recursive + pressure + actor/event architecture.
- No LLM runtime authority.
- Legacy Ceres is a comparator, not a destination.
- Infrastructure begins as generic capacity-bearing modules.
- Real authority enters through the compiler.
- Historical baselines are immutable artifacts.

## What happens after GAP-015 closes

Finishing the gap list is not the end of CIVPROP. It is the point at which we are
allowed to trust an end-to-end production candidate enough to qualify and use it.

The ordered post-gap sequence is frozen below and in the machine-readable register.

### POST-01 — Production readiness freeze

Purpose:

Declare Engine V1 production-ready only after all fifteen gaps are CLOSED and the
default input package contains no EXPLICIT_PLACEHOLDER assumptions.

Required outcomes:

- GAP-001 through GAP-015 CLOSED in default executable output;
- no Method Lab/scenario-credit production placeholders;
- full 2026-2226 horizon compiles;
- required Solar/body/actor coverage exists;
- input, engine, output, infrastructure and materialization contracts are pinned;
- one immutable production-readiness manifest records all hashes.

This is the point at which "the engine runs" becomes "the engine is a production
candidate."

### POST-02 — Qualification campaign

Purpose:

Try to break the completed engine before using a 200-year run.

Qualification includes:

- deterministic replay;
- no-oracle/hidden-truth firewall tests;
- mass, energy, population and accounting conservation;
- no-demand and demand-collapse cases;
- capital scarcity and access-loss cases;
- local-optimum and path-dependence tests;
- sensitivity/ensemble behavior;
- performance over long horizons;
- known empirical/control cases where available;
- explicit proof that legacy Ceres is not being used as an answer sheet.

A passing unit-test suite alone is not sufficient for this gate.

### POST-03 — Reference 2026-2226 propagation

Purpose:

Run the qualified engine over the full 200-year horizon.

The production campaign should include a declared seed ensemble so stochastic
path-dependence can be measured rather than hidden.

One immutable realization may be selected as the downstream Atlas reference, but:

    REFERENCE SIMULATION != CANON

unless separately promoted through governed canon process.

The reference run freezes:

- compiled input package;
- engine/version;
- infrastructure/economic parameter sets;
- seed or ensemble definition;
- complete output hashes;
- qualification report.

### POST-04 — CIVPROP run authority and persistence

Purpose:

Persist accepted simulation results as their own run authority.

Preferred long-term boundary:

    loom_earth     read-only source authority
    loom_solar     read-only source authority
    loom_timeline  read-only source authority
                   |       /
                   |      /
              loom_civprop
              run/state/event authority

The persistence layer should retain stable identities for:

- runs;
- yearly/location state;
- actor state;
- facilities/modules;
- decisions;
- events;
- flows;
- relationships;
- knowledge state;
- provenance.

Legacy CIVSTATE remains compatibility/projection material, not propagation
authority.

### POST-05 — Atlas materialization and comparator review

Purpose:

Turn the accepted CIVPROP run into the celestial-body/orbital/infrastructure Atlas.

The materializer produces:

- body state;
- surface sites;
- orbitals/free-space sites;
- facilities;
- settlements;
- owner/operator/institution links;
- demographics;
- economy;
- power;
- resources;
- cargo/passenger/ship-call state;
- derived centrality and strategic metrics.

Every substantive Atlas fact must trace to CIVPROP state or a transparent
deterministic transform.

Then compare the generated result with the old Ceres/Atlas material.

The old Atlas is:

    COMPARATOR

not:

    TARGET
    CALIBRATION ANSWER
    REQUIRED DESTINATION

A generated 2226 Ceres that differs from the old Ceres may be scientifically useful.
The comparison should explain why rather than force-fit the old answer.

### POST-06 — Solar coverage and release

Purpose:

Confirm that the production system can represent development, non-development and
abandonment across the Solar System.

Coverage sequence remains:

    Earth / Earth orbit
    Luna / cislunar
    Mars
    Belt / Ceres
    outer system

but that is a coverage/testing sequence, not a command that each region must settle.

Untouched bodies are valid outcomes.

A release manifest should pin:

- source authority versions;
- CIVPROP input package;
- engine;
- run;
- materializer;
- Atlas projections;
- derived metrics;
- uncertainty/limitations.

### POST-07 — Engine variants and iteration

Purpose:

Only after V1 produces a qualified end-to-end world do we reopen the question of
alternative propagation engines.

Future candidates may use:

- different pressure formulations;
- alternative actor policies;
- different discrete-event scheduling;
- stronger system-dynamics components;
- optimization or bounded-rational choice models;
- other non-LLM deterministic/seeded propagation methods.

Where semantics permit, they must consume the same input/output contracts.

That makes:

    Engine A vs Engine B

an experiment over the same world boundary, rather than another architecture reset.

V1 remains reproducible even if V2 later wins.

## Change-control rule for the register

The gap register is status/program authority, not simulation physics.

A gap status may change only with:

- linked evidence/artifact;
- tests;
- explicit exit-criteria review;
- update to engineering/civprop/gap_register_v1.json;
- update to the default executable's reported gap state where applicable.

Do not mark a gap CLOSED merely because a document exists.

Do not reopen a historical gap silently. If a later requirement materially changes
its semantics, either:

- reopen it explicitly with rationale; or
- create/version a new gap/contract.

## Immediate continuation

Current frontier:

    GAP-001 CLOSED
    GAP-002 CLOSED
    GAP-003 CLOSED
    GAP-004 CLOSED
    GAP-005 OPEN

GAP-002 removed the compiled-input assumptions:

    ASSUME-GAP002-AUS-BUDGET
    ASSUME-GAP002-AUS-CAPABILITIES

and replaced them with Actor State V1, explicit UNKNOWN spendable allocation,
scoped AUS evidence, replayable change events and runner-level actor-state output.

GAP-003 removed the compiled-input assumption:

    ASSUME-GAP003-ACCESSIBILITY

and replaced the default synthetic accessibility curves with Accessibility V1,
qualified frozen Solar geometry and scoped provider/service evidence.

GAP-004 removed the compiled-input assumption:

    ASSUME-GAP004-DEMAND

and replaced hand-authored annual demand curves with Demand/Pressure V1 state-derived
requirements, installed-capacity relief and decaying unit-preserving pressure.
Dynamic pressure remains internal; GAP-007 still owns its observability surface.

The next implementation target is therefore:

    GAP-005 PROJECT_ECONOMICS

That work must replace synthetic costs, lags and capacity parameterizations without
reopening GAP-002 actor semantics, GAP-003 accessibility semantics or GAP-004 causal
demand semantics.
