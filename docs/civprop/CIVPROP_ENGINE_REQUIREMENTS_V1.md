# CIVPROP Engine Requirements V1

Date: 2026-09-29
Class: class:engineering
Status: architecture reconciliation / pre-method-fit

Current-status note (2026-09-30): the method-fit phase described by this document has
been completed for Engine V1. The selected architecture is recorded in
docs/civprop/CIVPROP_ENGINE_V1_SELECTION.md. Current gap status and continuation are
recorded in docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md and
engineering/civprop/gap_register_v1.json. This document remains historical requirements
evidence and is not the current work queue.
Promoted basis inspected: origin/main at 4d7dfa53fe81f7f9936513aa8eb1df272b6dfef1

## Purpose

Reconcile the original SOLAR-CIVPROP design with current promoted Earth, Solar,
Timeline, actor-access and CIVPROP-0 work before selecting a propagation technique.

This document does not select the final simulation method, define a permanent
PostgreSQL schema, or authorize production propagation. It defines the stable
problem the method-fit exercise must solve.

## Current conclusion

CIVPROP remains a 2026-to-2226 generative civilizational simulation whose purpose is
to produce traceable Solar-system state from authoritative inputs rather than paint
a pre-authored 2226 endpoint onto bodies.

The original LOOM_SOLAR_CIVPROP_Next_Thread_Seed_v1.2.md remains directionally
useful, but it is a planning seed, not current engine authority. Since it was
written, main has earned stronger boundaries for Earth, Solar, Timeline, actor
access, transport uncertainty, knowledge/observation, decision semantics and
deterministic replay.

## Current authoritative boundaries

### Earth

loom_earth supplies the promoted Earth temporal baseline and remains externally
owned. CIVPROP must consume pinned Earth state rather than rewrite Earth authority.

For the first engine, Earth population/economic/capital trajectories may be treated
as an exogenous reference baseline. Off-world transfers or other CIVPROP effects
must be explicit reconciled deltas so population or capital is not counted twice.

The current long-run Earth trajectory is a qualified exploratory reference scenario,
not an empirically validated two-century forecast. CIVPROP must preserve that status.

### Solar

loom_solar owns physical body identity, qualified ephemeris/state authority,
coverage and spatial provenance. CIVPROP must not create a second physical authority.

Accessibility may consume Solar state, but body importance, industrial value,
settlement value and economic attractiveness are CIVPROP/downstream derivations.

### Timeline

loom_timeline supplies source-classed chronology, scenario anchors, governing canon
comparators and interpretation rules.

A date does not automatically unlock technology for every actor, create installed
capacity, create access, establish feasibility, make an investment profitable, or
cause migration/settlement.

### Solar Facts / resource evidence

Material/resource evidence remains separately owned and must preserve scope,
uncertainty, provenance and UNKNOWN. Evidence may constrain priors or opportunity
assessment. It may not be silently converted into exact local inventory, grade,
profitability or industrial importance.

### Actors and institutions

Atlas/CIVSTATE contains useful actor, institution, authority, ownership and
infrastructure semantics, but legacy CIVSTATE is not new propagation authority.
A 2226 actor or institution does not thereby exist in 2026. Any actor baseline must
preserve temporal validity, authority class and provenance.

### Existing 2226 Atlas/CIVSTATE

The 127-node corpus may serve as semantic/reference material, compatibility output,
governing hard constraint where independently classified, soft comparison, or
validation holdout.

It is not a required generated geography and must not be used as an answer sheet.

## Semantics already earned

Current main has demonstrated the following in bounded executable form:

1. pinned run/input/model identity;
2. deterministic replay;
3. keyed stochastic separation of physical realization and observation noise;
4. hidden simulated truth separated from actor knowledge;
5. observation-mediated belief update;
6. explicit decision rationale;
7. capital transactions and funded infrastructure changes;
8. append-only causal events with stable parentage;
9. UNKNOWN distinct from INFEASIBLE;
10. actor access distinct from service scope;
11. service scope distinct from transport feasibility;
12. transport feasibility distinct from actor decision;
13. provider precedent does not qualify another future mission;
14. usable access can still produce WAIT with no expenditure;
15. read-only input capture with pinned hashes is a workable input-compiler pattern.

Future propagation must preserve these semantics unless explicitly superseded by a
qualified replacement.

## Stable engine requirements

### R1 - Replaceable engine boundary

CIVPROP must support more than one propagation engine over time.

    authoritative inputs
        -> compiled/frozen CIVPROP input
        -> propagation engine
        -> stable CIVPROP output
        -> Atlas/GIS/materialized consumers

Changing engines must not require redesigning upstream authorities or downstream
Atlas consumers.

### R2 - No LLM reasoning in authoritative propagation

Authoritative state transitions must be inspectable code, explicit equations/rules,
deterministic transforms and declared seeded stochastic processes. LLM/Codex may
assist development and review, but is not a runtime decision authority.

### R3 - Reproducibility

Fixed input bundle + engine/model version + parameters + seed must reproduce the
same complete result. Prefer order-independent keyed randomness where stochastic
choices are required.

### R4 - Conservation and continuity

The engine must prevent unexplained creation, relocation or loss of population,
capital/infrastructure, resources/materials where modeled, energy balances where
modeled, and fleet/Mc inventories when activated.

Migration is source-debited. Existing capital stays where built unless an explicit
event changes it. New infrastructure needs investment, construction and applicable
lag.

### R5 - Explicit spatial hierarchy

At minimum:

    Solar System
      -> body
      -> regional/background civilization state
      -> site/settlement/industrial zone
      -> infrastructure/facility

Initial placement classes must cover SURFACE, ORBITAL and FREE_SPACE. Later location
types may be added without replacing the basic contract.

### R6 - Emergent geography

Bodies and sites may remain untouched. New facilities, settlements and candidate
nodes may emerge outside the legacy 127-node Atlas. A legacy node is not
automatically generated unless it is a governing hard constraint.

No authored body-importance score may substitute for causal propagation.

### R7 - Infrastructure as physical state

Infrastructure/capital must be explicit state attached to a location and, where
applicable, owner/operator. Eventual output must distinguish useful capacity families
such as habitat, power, extraction/resource, industrial/manufacturing,
transport/port, shipyard and support/storage. Exact class hierarchy is not frozen.

### R8 - Path dependence

Prior investment must alter later opportunity through actual accumulated state such
as capacity, accessibility, workforce, demand or supplier networks. Path dependence
must not be an authored claim that a body is important.

### R9 - Bounded actor decisions

Countries, firms, consortia, settlements and institutions may act, but they choose
from explicit feasible opportunities using declared inputs. Person-level simulation
of billions of people is not required.

Possession, service access, physical feasibility and decision remain separate.

### R10 - Knowledge is not truth

Only observation/measurement mechanisms may read hidden simulated physical truth.
Actors act on scoped knowledge/belief state. Discovery updates knowledge rather than
creating deposits.

### R11 - Time is explicit, technique is not frozen

The engine must produce reproducible 2026-to-2226 temporal state with annual
Atlas-style inspection. Annual output does not require every internal mechanism to
use one-year integration. Method fit decides the master clock and event treatment.

### R12 - Evolving upstream inputs are isolated

The eventual engine must not depend directly on mutable live table layouts. Source
or schema changes are handled by adapters/input compilation. Value changes create a
new frozen input bundle. Genuine semantic changes create a versioned contract.

### R13 - Output stability

Regardless of engine, downstream consumers must obtain consistent logical outputs by
year/location: identity, facilities/infrastructure, surface/orbital placement,
population, workforce, capital, power, production/economic activity, transport where
modeled, actor ownership/operation/authority, events/provenance and uncertainty.

Storage schema is deferred until after propagation-method fit.

## Original design reconciliation

| Original concept | Disposition | Current requirement |
|---|---|---|
| 2026-to-2226 constrained generative reconstruction | KEEP | Core CIVPROP purpose. |
| Forward mode | KEEP | Primary engine mode. |
| Canon-reconciliation mode | MODIFY | Hard constraints only where governing; soft targets/holdouts for validation; do not optimize history to reproduce Atlas. |
| No global rational planner | KEEP | Fragmented/path-dependent behavior remains required. |
| Do not agent-model billions | KEEP | Aggregate/cohort/flow scale remains expected. |
| Preferred hybrid architecture | KEEP AS HYPOTHESIS | Method Lab must earn orchestration and subsystem techniques. |
| Ephemeris first-class | KEEP WITH CURRENT AUTHORITY | Consume loom_solar; accessibility is the civilization-facing bridge. |
| Annual civilizational clock | MODIFY | Annual inspectable output; internal timestep remains open. |
| Full historical inventory before runtime | MODIFY | Inventory only what materially constrains the selected engine/vertical slice. |
| Cohort biological demography | KEEP AS CANDIDATE | Required behavior; method to be fitted. |
| Synthetic-person demography | KEEP / DEFER | Preserve distinction from automation capital; not needed in first lab slice. |
| Habitat/settlement capital | KEEP | Population must be physically capacity constrained. |
| Workforce decomposition | KEEP / STAGE | Activate detail as demanded by selected method. |
| Reduced IO economy | KEEP AS CANDIDATE | Do not duplicate Earth authority; likely relevant to endogenous off-world production. |
| Capital accumulation/depreciation | KEEP | Required continuity behavior; formulation not frozen. |
| Technology diffusion | KEEP WITH TIMELINE CORRECTION | Timeline is frontier/constraint, not adoption. |
| Energy/resource modules | KEEP / STAGE | Needed for mature propagation; may be simplified in lab. |
| Migration discrete choice | KEEP AS CANDIDATE | Must stay conserved/habitat constrained; benchmark alternatives. |
| Firm/industrial location choice | KEEP AS CANDIDATE | Central to emergent geography; method not frozen. |
| OD demand/mode/fleet/ports/queues | DEFER FIRST FIT | Preserve interface need; activate later. |
| Shock mechanism | KEEP / DEFER | Later resilience/path-dependence feature. |
| Epistemic/control classifications | KEEP AND ALIGN | Preserve current evidence/status boundaries. |
| Ensembles/hindcasting/conservation tests | KEEP | Validation remains required. |
| Bitemporal/model lineage | KEEP | Simulation time and model-development lineage remain distinct. |
| Proposed schema-13 table design | SUPERSEDE / DEFER | No implementation before method fit and stable contracts. |
| GIS materialization | KEEP | Atlas remains downstream inspection/projection. |
| Institutions/inherited capital | KEEP WITH PROVENANCE | 2226 Atlas state is not automatic 2026 state. |
| Existing stocks are not reallocated | KEEP | Only explicit loss/transfer/project events move/change stock. |
| Macro-to-node allocation | KEEP AS PROBLEM, NOT METHOD | Spatial allocation required; technique remains open. |
| 127-node canonical layer | MODIFY | Reference/constraint/holdout and compatibility output, not a closed universe. |
| Regional/background state | KEEP | Named nodes do not absorb all civilization. |
| Emergent candidate nodes | KEEP | Noncanonical locations may emerge and remain noncanon. |
| Empty persistent runtime before science | DEFER | Select propagation architecture first. |
| Old immediate work: inventory plus schema scaffolding | SUPERSEDED | Immediate next step is propagation-method fit. |

## Solar Emergence v0 reconciliation

LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md is a useful unexecuted method
hypothesis and should feed the Method Lab rather than be mistaken for the selected
engine.

| Solar Emergence v0 concept | Disposition |
|---|---|
| Every registered body eligible; untouched allowed | KEEP |
| Facility as primary generated object | TEST AS STRONG HYPOTHESIS |
| Body state derived from facilities | KEEP WITH REGIONAL/BACKGROUND STATE |
| CREATE_FACILITY / EXPAND_CAPABILITY | KEEP FOR METHOD LAB ONLY |
| Earth economies as financing pools | MODIFY; useful fixture, not complete actor model |
| Softmax/discrete-choice investment location | TEST |
| Construction lag + accumulated local capital | KEEP |
| Source-debited habitat-constrained migration | TEST |
| No calibration to Ceres/127-node Atlas | KEEP |
| Same decision machinery for all countries | KEEP FOR METHOD LAB ONLY |
| Mesa/ABM deferred | KEEP; actor-heavy approach belongs in comparison |

No Solar Emergence v0 implementation is present on current main; only its workplan
was promoted.

## Open method-fit questions

Before full CIVPROP input/state contracts or persistence are frozen, the Method Lab
must resolve:

1. master orchestration: dynamic-recursive, system-dynamics-heavy,
   actor/discrete-event-heavy, or bounded hybrid;
2. internal timestep and exact-date project/mission handling;
3. whether facility is the primary generated spatial object or whether a more generic
   infrastructure/capital object sits beneath it;
4. opportunity generation without enumerating desired outcomes;
5. bounded actor investment/abandonment decision rule;
6. spatial allocation of new capital while old capital remains continuous;
7. migration coupling to jobs, habitat and accessibility;
8. which Earth quantities stay exogenous and which become endogenous off Earth;
9. minimum transport detail needed for credible accessibility;
10. where seeded stochasticity is useful rather than decorative noise;
11. feedback loops requiring inner iteration;
12. minimum stable Atlas output independent of engine implementation.

## Gate to Method Lab

The Method Lab must:

- use one frozen synthetic Earth-Orbit-Luna/cislunar input across candidates;
- require the same minimal output contract from every prototype;
- not calibrate to Atlas/Ceres outcomes;
- test conservation, causal traceability, construction lag, habitat constraint,
  path dependence, technology/access constraints, emergent investment location,
  legitimate failure/no-investment, deterministic replay, order independence,
  parameter burden and runtime;
- never write production databases;
- never use LLM reasoning at runtime.

Only after method selection should CIVPROP freeze its full INPUT, STATE, OUTPUT and
engine contracts.

## Evidence inspected

Promoted repository material inspected:

- research/seeds/LOOM_SOLAR_CIVPROP_Next_Thread_Seed_v1.2.md
- research/seeds/LOOM_SOLAR_EMERGENCE_V0_TEST_WORKPLAN_2026_09_24.md
- docs/civprop/CIVPROP_GAME_PLAN_VERIFICATION_V1.md
- docs/civprop/CIVPROP_ACTOR_CAPABILITY_FOUNDATION_V1.md
- reports/civprop/CIVPROP_0_EARTH_LUNA_PROSPECTING_REPORT.md
- engineering/civprop/civprop0/
- docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md
- docs/database_semantics/recovery/LOOM_CIVSTATE_RECOVERY_CONSOLIDATION_v1.0.md
- current Earth/Solar/Timeline contracts referenced by the promoted CIVPROP docs.

No production database, schema, propagation runtime, canon record or existing
authority was changed by this reconciliation.
