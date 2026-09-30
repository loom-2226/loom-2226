# CIVPROP Engine V1 Selection

Date: 2026-09-30
Class: class:engineering
Status: selected architecture / executable Method Lab reference

## Decision

CIVPROP Engine V1 will use:

    annual dynamic-recursive skeleton
            +
    system-dynamics stocks / pressures
            +
    actor / event decisions for major discrete commitments

This is an engineering selection, not a claim that alternative propagation methods
are invalid. Future engines may use different techniques behind the same versioned
input/output boundaries.

The purpose of selecting V1 now is to stop architecture churn and build a usable
propagation engine.

## Semantic interpretation

The three layers answer different questions.

### Dynamic-recursive skeleton

Answers: What is civilization state at time t, and how does it become state t+1?

This is the master temporal spine. Annual state remains inspectable even when some
internal events occur at finer resolution.

It owns continuity of population, capital, installed capacity, workforce,
production/resource stocks when activated, accumulated knowledge and actor state,
and other future state variables.

### System-dynamics pressures

Answers: What unmet structural pressures are becoming important enough to create a
serious opportunity?

Pressure may arise from demand, scarcity, congestion, accessibility, resource
knowledge, installed complementary capacity, strategic requirements or other
explicit modeled state.

Pressure is stateful but must not be immortal. The V1 reference implementation uses
decay so weak historical signals disappear unless current conditions continue to
support them.

Pressure does not itself build infrastructure.

### Actor / event decisions

Answers: Who actually commits capital, under what capability/access constraints, and
when?

Actors see only explicitly qualified opportunities. Major commitments are discrete,
causal events. Construction, commissioning, failure, abandonment and other later
project transitions remain event-addressable.

Actors do not query hidden truth and do not use LLM reasoning.

## Causal loop

    state(t)
      -> update / decay structural pressures
      -> generate feasible opportunities from current state
      -> pressure qualifies some opportunities
      -> eligible actors evaluate qualified opportunities
      -> actor commits / waits / later abandons
      -> discrete project and mission events
      -> stock / flow / population updates
      -> conservation + validation
      -> state(t+1)

Then the changed state alters the next round of pressure.

The intended feedback is:

    pressure creates opportunity
    actor converts opportunity into history
    history changes state
    state changes future pressure

## Why V1 was selected

The Method Lab showed useful failure modes when each mechanism was exaggerated in
isolation.

The dynamic-recursive candidate represented path-dependent annual choice well but
could become locally greedy around already-attractive infrastructure.

The system-dynamics-heavy candidate allowed weak signals to accumulate into long-term
development pressure, but a pure pressure model risks turning persistent positive
signals into inevitable projects.

The actor/discrete-event candidate represented institutional causality and ownership
well, but a pure actor ranking model can also become myopic and repeatedly choose
near-term local opportunities.

The selected hybrid makes these mechanisms constrain one another rather than asking
one of them to explain all history.

## V1 runtime rule

No LLM, Codex, Sol or other generative model is an authoritative runtime propagation
component.

Authoritative propagation consists of explicit code, equations/rules, versioned
parameters and declared seeded stochastic processes.

Models may assist engineering, review, explanation and non-authoritative experiments.

## V1 reference implementation

The first executable reference is:

engineering/civprop/method_lab/prototypes/hybrid_v1.py

It runs against the synthetic Method Lab only. This is deliberate.

It proves the selected causal architecture before implementation is coupled to the
evolving Earth, Solar, Timeline, Solar Facts and actor authorities.

The reference implementation includes annual recursive state progression, decaying
pressure reservoirs, pressure-qualified opportunities, explicit actor selection,
discrete project commitments, construction lags and commissioning, source-debited
migration, capacity/habitat constraints, deterministic keyed stochasticity, and
event/decision/flow output.

It is not yet the production 2026-to-2226 engine and its synthetic coefficients are
not production economics.

## What is now fixed versus still replaceable

Fixed for Engine V1:

- three-layer propagation architecture;
- no LLM runtime authority;
- annual inspectable state;
- pressure qualification before major commitment;
- actor/event causality for major projects;
- deterministic replay;
- hidden truth firewall;
- conservation/continuity requirements;
- replaceable versioned engine boundary.

Still intentionally replaceable:

- pressure equations and decay constants;
- actor decision functions;
- economic production model;
- migration equation;
- opportunity generator;
- resource economics;
- transport/accessibility implementation;
- actor archetypes;
- stochastic distributions;
- internal sub-annual scheduling;
- persistence backend.

## Current continuation

The method-selection sequence recorded above has now been executed far enough to
select and lock Engine V1.

Current promoted continuation authority is:

    docs/civprop/CIVPROP_GAP_REGISTER_AND_POST_GAP_PLAN_V1.md
    engineering/civprop/gap_register_v1.json

As of the register basis commit:

    GAP-001 REAL_INPUT_COMPILER        CLOSED
    GAP-002 ACTOR_STATE_AND_BUDGETS   CLOSED
    GAP-003 TRANSPORT_ACCESSIBILITY   CLOSED
    GAP-004 DEMAND_AND_PRESSURE_MODEL CLOSED
    GAP-005 PROJECT_ECONOMICS         CLOSED
    GAP-006 MISSIONS_AND_KNOWLEDGE_UPDATE CLOSED

The selected Hybrid V1 architecture remains fixed while GAP-007 through GAP-015
replace the remaining placeholders and missing state/output surfaces.

The post-gap sequence is also frozen in that register so completion of the gap list
has an explicit destination: production-readiness freeze, qualification campaign,
full 2026-2226 reference propagation, CIVPROP run persistence, Atlas materialization,
Solar coverage/release, then optional alternative-engine comparison.

Alternative engines remain a future supported option rather than a current blocker.
