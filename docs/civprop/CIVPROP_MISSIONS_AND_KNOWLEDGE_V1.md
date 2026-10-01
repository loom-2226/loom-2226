# CIVPROP Missions and Knowledge V1

Date: 2026-10-01
Class: class:engineering
Status: GAP-006 closure contract

## Purpose

Mission/Knowledge V1 promotes the proven CIVPROP-0 observe/Bayes loop into the
selected Hybrid V1 engine as a general mission/event lane.

The governing causal chain is:

    actor-visible knowledge
        -> mission opportunity
        -> access / capability / budget / economics / value of information
        -> mission decision
        -> mission execution
        -> noisy observation
        -> knowledge update
        -> later project/economic decision

Mission actions are not infrastructure archetypes.

Discovery changes knowledge. It does not create or modify the physical deposit.

## Contracts

Implementation:

    engineering/civprop/contracts/mission_knowledge_v1.py

Parameter package:

    engineering/civprop/contracts/mission_knowledge_v1.json

Hybrid adapter:

    engineering/civprop/method_lab/mission_lane_v1.py

Identity:

    CIVPROP_MISSION_KNOWLEDGE_V1
    contract_version = 1.0.0
    package_id = EARTH_LUNA_MISSION_KNOWLEDGE_V1_2026_2036
    package_status = GENERAL_CONTRACT_BINARY_RESOURCE_IMPLEMENTATION_V1

The contracts are general enough to separate missions, observations and knowledge
state, while the first admitted scientific implementation remains deliberately
narrow: binary lunar-resource presence detection.

## General contract surfaces

Mission V1 carries:

- mission archetype identity;
- actor;
- scientific/operational question;
- origin and destination;
- mission/service class;
- required technologies;
- linked Project Economics V1 parameterization;
- commitment and execution years;
- capital cost and unit;
- status;
- visibility/provenance.

Observation V1 carries:

- mission identity;
- actor;
- question, subject and spatial scope;
- observation year;
- observed result;
- sensitivity;
- false-positive probability;
- quantity/unit;
- error model;
- visibility;
- authority class.

Knowledge State V1 carries:

- actor owner;
- question and subject;
- spatial scope;
- current probability;
- evidence/source identity;
- valid year;
- complete applied-observation ID chain;
- visibility;
- authority class.

Mission Decision V1 carries:

- actor and mission archetype;
- question and target;
- action/status;
- expected value of information when calculable;
- value unit;
- rationale codes.

## First admitted scientific question

The first question is:

    MOON_POLAR_WATER_PRESENT

Subject:

    MOON_POLAR_WATER

Location:

    LUNA_SURFACE

Question kind:

    BINARY_PRESENCE

Initial probability:

    0.45

Prior status:

    EMPIRICAL_PRESENCE_PLUS_SCENARIO_PRIOR

The empirical evidence establishes scoped lunar-water presence evidence. It does not
establish a universal numeric probability of 0.45.

The 0.45 probability therefore remains a versioned scenario-model parameter inside
the now-closed mechanism.

Closing GAP-006 means the knowledge mechanism is explicit and governed. It does not
turn an uncalibrated prior into an empirical measurement.

## First observation model

The first observation model is:

    LUNAR_WATER_BINARY_DETECTION_V1
    BERNOULLI_CONFUSION_MATRIX_V1

Current parameters:

    sensitivity = 0.80
    false_positive_probability = 0.10

Parameter status:

    UNCALIBRATED_SCENARIO_OBSERVATION_MODEL

These values preserve the CIVPROP-0 test mechanism. They are not claimed instrument
performance for Roo-ver, a named NASA payload, or any operational lunar instrument.

The model is intentionally narrow enough to be auditable:

    if hidden resource present:
        P(detected) = sensitivity

    if hidden resource absent:
        P(detected) = false-positive probability

## Epistemic firewall

The strongest GAP-006 rule is:

    HIDDEN PHYSICAL REALIZATION
        IS NOT
    ACTOR KNOWLEDGE

Actors do not receive:

    present = true

They receive observations generated through an instrument/error model.

Only:

    BinaryObservationRuntime.observe(...)

accepts the hidden present/absent realization.

Hybrid V1 itself does not read evaluator truth.

Mission selection does not read evaluator truth.

Value-of-information calculation does not read evaluator truth.

Project scoring does not read evaluator truth.

The Hybrid adapter reads hidden realization only when an admitted mission has
actually reached its execution year, and passes it directly into the observation
runtime.

The resulting observation, not the truth value, is then delivered to the actor.

## Independent keyed stochasticity

Observation noise is keyed using:

- simulation seed;
- Mission/Knowledge package identity;
- mission identity;
- question identity;
- observation-model identity;
- observation year.

Therefore:

    unrelated simulation insertion
        !=
    changed observation draw

Adding an unrelated mission or random call does not move the random stream for an
existing observation.

Physical realization, observation noise and actor/project randomness remain separate
conceptual stochastic layers.

## Bayesian update

For a positive binary observation:

    P(H | +)
      =
    P(H) sensitivity
    -----------------------------------------------
    P(H) sensitivity + (1-P(H)) false_positive

For a negative observation:

    P(H | -)
      =
    P(H) (1-sensitivity)
    ----------------------------------------------------
    P(H) (1-sensitivity) + (1-P(H)) (1-false_positive)

The update fails closed for:

- wrong actor;
- wrong question;
- wrong subject;
- wrong location;
- duplicate observation;
- observation older than the current knowledge state.

The observation ID is appended to the knowledge state's evidence chain.

## Visibility

The initial lunar-water question is:

    PRIVATE

The first observation inherits the mission visibility and updates only that actor's
knowledge.

Mission/Knowledge V1 therefore supports actor-scoped knowledge as a first-class
state concept.

The contract allows PRIVATE, PUBLIC and PARTNER visibility, but GAP-006 does not yet
invent dissemination/sharing events. Those can be added through a later versioned
event rule rather than assuming every discovery instantly enters universal public
knowledge.

## Mission archetype

The first mission archetype is:

    LUNAR_RESOURCE_PROSPECTING_SURVEY

Mission class:

    ROBOTIC_RESOURCE_PROSPECTING

Origin:

    EARTH_SURFACE

Destination:

    LUNA_SURFACE

Required technology:

    LUNAR_SURFACE_OPERATIONS

Project Economics V1 reference:

    PROSPECTING_SURVEY

Follow-on economic question:

    RESOURCE_PLANT

The production-facing compiled scenario no longer contains PROSPECTING_SURVEY as a
project/infrastructure archetype.

Its economics remain in Project Economics V1 because an action still has cost and
duration.

This is the clean boundary:

    project_economics parameterizes a mission
        !=
    mission is infrastructure

## Value of information

Mission V1 preserves the CIVPROP-0 expected-value-of-sample-information mechanism.

The actor compares:

    expected best post-observation continuation value
      - best current continuation value
      - mission cost

A mission can commit only when:

- accessibility is FEASIBLE;
- required capability is USABLE;
- budget is KNOWN;
- budget unit matches mission economics;
- mission is affordable;
- follow-on success value is known;
- expected value of information exceeds the threshold.

The default production package deliberately defines:

    follow_on success value = UNKNOWN

for the current lunar-resource survey.

Why?

Because GAP-006 owns the mission/knowledge mechanism. It does not own a calibrated
economic value for a successful lunar-water development opportunity.

GAP-009 still owns production and value added.

Therefore the real default AUS run correctly returns:

    WAIT
    FOLLOW_ON_VALUE_UNKNOWN

rather than inventing a resource-project payoff merely to make a mission happen.

## Hostile fixture

The historical Method Lab scenario provides a bounded test fixture with:

- known synthetic actor budget;
- lunar accessibility becoming feasible;
- usable lunar-surface capability for LAB_PUBLIC;
- explicit scenario mission/follow-on economics;
- evaluator-only binary resource realization.

For the hostile fixture only, a declared scenario follow-on value is supplied.

The result proves the complete loop:

    2026-2028
        WAIT while access/capability are unresolved

    2029
        positive value of information
        COMMIT_MISSION

    2030
        mission executes
        observation generated
        observation received
        Bayesian update performed

With seed 42 and the favourable keyed observation, the LAB_PUBLIC belief moves from:

    0.45
        ->
    approximately 0.8675

With seed 5 and an adverse keyed observation, it moves from:

    0.45
        ->
    approximately 0.1538

The pre-observation mission decisions are identical when the hidden truth fixture is
manually switched from present to absent.

That is a direct hostile test of the no-oracle boundary.

## Posterior handoff

Hybrid project opportunity scoring no longer has to use only the scenario resource
prior.

When actor knowledge exists, the resource probability consumed by later project
scoring is the actor's latest scoped posterior.

Therefore:

    observation
        -> posterior
        -> later project utility/economics

is an executable causal path.

The hidden truth never appears in that handoff.

## Event ordering

For each year on the Mission/Knowledge V1 path:

    apply actor budget events
    commission due projects
    execute missions due this year
    produce observations
    update actor knowledge
    derive demand/pressure
    score project opportunities using updated knowledge
    evaluate new missions
    debit committed mission capital
    evaluate/commit projects
    migration compatibility step
    annual snapshot

This ordering permits an observation received in year N to affect a later investment
decision in year N without permitting the observation to affect a mission decision
made in an earlier year.

## Finance replay

Mission commitments debit the same actor spendable-allocation surface used by project
commitments.

Runner-level actor-state projection replays:

    MISSION_COMMITMENT

transactions from the mission decision record and year-resolved Project Economics V1
mission cost.

A mission therefore cannot disappear from the finance ledger merely because it is
not a facility.

## Output surface

Runner V1.8 continues to expose:

    mission_knowledge_boundary
    mission_decisions
    missions
    observations
    knowledge_states

alongside the existing:

    actor_states
    annual_states
    facilities
    decisions
    events
    flows

Evaluator truth is not emitted as actor state.

Runner metadata records:

    evaluator_truth_access_policy
      =
    OBSERVATION_RUNTIME_ONLY_WHEN_ADMITTED_MISSION_EXECUTES

and whether evaluator truth was actually consumed in that run.

## Default seed-42 behavior

The promoted-facing AUS seed-42 baseline contains:

    44 annual location states
    11 annual actor states
    11 project decisions
    11 mission decisions
    1 knowledge state
    46 events
    0 missions
    0 observations
    0 facilities
    0 actor transactions
    0 actor-state events
    0 migration flows

All project decisions are WAIT.

All mission decisions are WAIT.

The initial actor-visible knowledge state is:

    actor = AUS
    question = MOON_POLAR_WATER_PRESENT
    location = LUNA_SURFACE
    probability = 0.45
    visibility = PRIVATE

The mission waits because the current production-facing evidence still includes
unresolved access/capability/budget conditions and, independently, the follow-on
success value is UNKNOWN.

Since no mission executes:

    evaluator_truth_consumed_by_engine = false

This is an important closure result.

The mission lane exists without forcing the baseline to consume the answer key.

## Historical CIVPROP-0 preservation

The promoted architecture is based on the already-tested CIVPROP-0 components:

    engineering/civprop/civprop0/actor.py
    engineering/civprop/civprop0/observation.py
    engineering/civprop/civprop0/experiment.py

CIVPROP-0 remains historical evidence and a narrow reference demonstrator.

Mission/Knowledge V1 generalizes its boundaries rather than replacing those files or
rewriting their frozen favourable/adverse run artifacts.

## Hostile tests

Tests prove:

- missions are distinct from infrastructure;
- default unknown follow-on value forces WAIT;
- a bounded scenario value can create positive VOI;
- actor mission decisions do not accept hidden truth;
- hidden realization enters only the observation runtime;
- same seed/evidence/mission reproduces the same observation;
- unrelated random work does not change the keyed observation;
- positive observation increases the posterior;
- negative observation decreases the posterior;
- duplicate evidence is rejected;
- wrong-location evidence is rejected;
- backward-time evidence is rejected;
- unit mismatches fail closed;
- Hybrid mission commit/execution/observation/update works end to end;
- pre-observation mission decisions are identical under opposite hidden truth;
- posterior knowledge is consumed by later project scoring;
- historical Method Lab result hashes remain unchanged when Mission V1 is absent.

## GAP-006 closure

GAP-006 is closed because the default production-facing architecture now:

1. represents mission actions separately from infrastructure;
2. chooses missions from actor-visible knowledge and existing actor/access/economic
   boundaries only;
3. generates noisy observations from hidden physical realization plus a declared
   instrument error model;
4. uses keyed, deterministic replay semantics;
5. performs auditable Bayesian knowledge updates;
6. feeds the actor posterior into later project scoring;
7. exposes missions, observations, mission decisions and knowledge state in the
   runner output;
8. retains the hidden-truth firewall.

Closure does not mean:

- the 0.45 prior is empirical;
- the 0.80/0.10 instrument model describes a real named instrument;
- lunar-water project value is known;
- the synthetic hidden truth fixture is Solar authority;
- multi-hypothesis scientific inference is solved;
- knowledge sharing/classification policy is complete.

## Pressure observability handoff

GAP-007 PRESSURE_OBSERVABILITY is CLOSED.

Pressure Observability V1 now emits reconstructable pressure state, quantified
contributions and qualification provenance without changing the GAP-006 mission or
knowledge behavior. The complete pre-existing GAP-006 behavioral arrays remain
byte-identical under the GAP-007 baseline.

GAP-008 RESOURCE_MASS_BALANCE is now CLOSED. The immediate frontier is GAP-009 PRODUCTION_AND_VALUE_ADDED.
