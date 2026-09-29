# CIVPROP Method Lab Prototype Engines V1

Status: engineering prototypes; synthetic; non-canon; non-production.

## Purpose

Implement three deliberately small propagation architectures against the exact same
frozen Method Lab input bundle and common output contract.

These are candidates for hostile comparison, not production engines and not a
selection result.

## Shared mechanics

All three candidates reuse the same bounded helper layer for initial-state loading,
technology/frontier and actor-capability gating, accessibility lookup, local
prerequisite checks, construction lag, facility commissioning, source-debited
migration, capacity accounting, event/decision/flow recording, and deterministic
serialization.

The common helper layer is intentional. The comparison is about propagation
orchestration and decision structure, not allowing each candidate to redefine
physical feasibility.

None of the candidate engine modules reads evaluator-only hidden truth.

## Candidate A: DYNAMIC_RECURSIVE

Module: prototypes/dynamic_recursive.py

Annual stock/state recursion commissions due projects, refreshes actor capital,
generates feasible opportunities, applies a seeded softmax/discrete choice per
actor, commits projects, applies bounded migration, and emits an annual snapshot.

This is the closest prototype to the original dynamic-recursive plus discrete-choice
hypothesis.

## Candidate B: SYSTEM_DYNAMICS_HEAVY

Module: prototypes/system_dynamics.py

Aggregate development pressure accumulates by feasible location/project pair.
Pressure crossing a threshold, together with capital availability, commits a
project. Migration adjusts gradually. The prototype is intentionally behaviorally
deterministic even though the common result metadata records the supplied seed.

This tests whether aggregate feedback and stock-flow pressure can generate useful
spatial development without a rich actor-decision layer.

## Candidate C: ACTOR_DISCRETE_EVENT

Module: prototypes/actor_event.py

A priority queue schedules actor decisions, migration, snapshots and future project
commissioning. Actors rank the same feasible opportunity set with bounded actor-type
weights and keyed deterministic jitter.

This tests a more actor/event-heavy architecture without Mesa or person-level agents.

## Shared synthetic economics

All candidates use the same Method Lab fixture economics: exogenous demand signals,
generalized access cost, complementary installed capacity, diminishing returns when
capacity outruns demand, resource prior where relevant, and project capital cost.

These coefficients are lab fixtures, not scientific claims, forecasts, or proposed
production CIVPROP economics.

## Seed-42 smoke run

prototype_seed42_summary_v1.json is a committed reproducibility summary, not a
winner table.

The smoke run proves that all three candidates consume the same frozen input bundle,
satisfy the same result validator, generate off-world infrastructure, conserve
biological population under migration, respect construction lag, respect technology
and actor-access gates, emit annual state for every location, and reproduce exactly.

The three histories are behaviorally distinct. That is expected. Step 4 must compare
them with preregistered hostile benchmarks rather than aesthetic preference.

## Reproduce

From repository root:

    python3 -m unittest engineering.civprop.method_lab.test_prototypes -v
    python3 -m engineering.civprop.method_lab.run_prototypes --seed 42

No candidate writes a production database or modifies Earth, Solar, Timeline,
Atlas/CIVSTATE or CIVPROP-0 authority.
