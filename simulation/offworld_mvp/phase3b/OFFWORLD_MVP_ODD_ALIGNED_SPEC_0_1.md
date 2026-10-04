# Offworld MVP — ODD-Aligned Executable Model Specification 0.1

**Status:** DESIGN CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Basis:** ODD 2020 structure adapted to LOOM governance
**Scope:** Build 4-derived Offworld MVP before autonomous policies

## 1. Purpose and patterns

The Offworld MVP tests whether an auditable civilization-propagation loop can emerge from immutable reference/evidence state, hidden scenario state, imperfect information, finite resources, institutional decisions, explicit accounting and physical conservation.

The MVP is not a 2026–2226 forecast. It is a controlled trajectory generator whose outputs are conditional on declared scenario, model and policy assumptions.

Required patterns/falsification targets include:

- identical pre-observation behavior across otherwise identical NULL/SPARSE/RICH universes;
- divergence only after admissible information or other causal state differs;
- no financial, resource, population or ownership creation outside declared transitions;
- recursive capital formation can generate different trajectories under different disposition rules;
- deterministic replay under pinned inputs, parameters, schedule and keyed random identities.

## 2. Entities, state variables and scales

Runtime object classes:

- SYSTEM: rule/process mechanism, no beliefs/objectives;
- AGGREGATE: statistically represented many-member state;
- AGENT: persistent bounded decision-maker;
- ENTITY_ASSET: persistent non-decision object/state.

Core domain objects include Node, Account, Transaction, Commitment, Project, WIP, KnowledgeAsset, ProductiveAsset, ResourceState, Observation, BeliefState, PopulationState, ColonyState, FixedCapitalFormationEvent, ownership claims, EarthImpact state and causal events.

World contexts remain REAL, SCENARIO(id), REALIZED(run_id). Perspectives remain GOVERNANCE, WORLD_SIM and AGENT(agent_id).

Time is multi-rate and scheduler-owned. Individual subsystems do not advance global time themselves.

## 3. Process overview and scheduling

The executable scheduler contract is defined in:

`PHASE3B_SCHEDULER_COUPLING_CONTRACT_CANDIDATE_0_1.md`.

Minimum ordered phase semantics for an annual macro tick are:

1. OPEN_PERIOD
2. EXOGENOUS_INPUTS
3. OBSERVATION
4. INFORMATION_UPDATE
5. DECISION_WINDOW
6. ACTION_VALIDATION
7. COMMITMENT_DISBURSEMENT
8. OPERATIONS
9. MARKET_CLEARING
10. DEPRECIATION_AMORTIZATION
11. ACCOUNTING_CLOSE
12. CONSERVATION_CHECK
13. SNAPSHOT_CLOSE

Sub-period mission/transport/operational events may occur inside declared phases using deterministic time keys. Same-time ties require explicit stable ordering. Execution order may not be an undeclared source of randomness.

Integrated simulation runs use a sealed `ScheduledSimulationRuntime`. Model initialization occurs before seal. After seal, state-changing kernel operations are legal only inside scheduler-dispatched event contexts; direct kernel mutation is rejected. The run pins both initial-state and scheduler-plan fingerprints and is single-use.

DECISION_WINDOW policy execution is separated from kernel-bearing system handlers. Policy code receives only a frozen/slotted `PolicyContext` containing a deeply copied `DecisionSnapshot`, pinned snapshot reference and deterministic decision key. Hidden scenario resources, world/run identity, scheduler and seed state are not part of that interface.

## 4. Design concepts

### Emergence
Settlement, capital stock, ownership distribution, extraction and financing recursion are realized outcomes, not scripted historical milestones.

### Adaptation
Autonomous adaptation is not yet authorized. Scripted deterministic policies may exercise interfaces. Future Agent policies will be separately governed.

### Objectives
Agent objective state exists conceptually. No common utility function is assumed.

### Learning
Observation -> information -> belief is permitted. Build 4 uses a deliberately crude validation update and does not claim calibrated Bayesian learning.

### Prediction
Agents may later form expectations from their own information. WORLD_SIM truth may not be substituted for those expectations.

### Sensing
Only declared observation/information channels cross the hidden-world firewall.

### Interaction
Interactions occur through action requests, transactions, observations, ownership claims and system-mediated processes. Agents do not mutate world state.

### Stochasticity
Randomness is keyed and replayable. Random identities are independent of execution order.

### Collectives
AGGREGATE state may represent many actors. Split/promotion into explicit AGENT state requires deterministic reconciliation, explicit exposure-selection/allocation basis, lineage, and a resolution-invariance test.

When the exposed AGENT is constrained to follow the same rule as its source AGGREGATE representation, represented system totals must remain pathwise equivalent over the comparison horizon. Divergence is permitted only after an admitted difference in information, beliefs, objectives or policy.

### Observation
Model outputs must expose events, state snapshots, invariant failures, run identity and uncertainty/parameter identity.

## 5. Initialization

A run must pin:

- code/model contract version;
- input snapshot identifiers;
- scenario universe id/version;
- scheduler contract version;
- parameter set id;
- participating economy selection act when one is used;
- initial accounts/assets/projects/resources/population;
- agent/aggregate/system classifications;
- random master identity or keyed namespace.

No missing empirical value may be replaced by a convenience default.

## 6. Input data

Input categories remain distinct:

- Earth reference inputs;
- Solar evidence/reference inputs;
- technology scenario inputs;
- authored scenario-world hidden state;
- authored model parameters;
- deterministic validation fixtures;
- underwriting input tables carrying value, unit, status, source/rationale, sensitivity range and scope.

The current underwriting table is explicitly PRE-CONTRACT authored validation scenario data, not empirical calibration. UNKNOWN underwriting inputs remain non-numeric.

Reference/projection/scenario/simulated status must not collapse merely because all are serialized in one run package.

## 7. Submodels

Current MVP submodels/interfaces include:

- financing/commitment/disbursement;
- expenditure/WIP/capitalization;
- depreciation/amortization;
- ownership claims/disposition;
- resource extraction/inventory;
- exploration/observation;
- Earth resource-allocation/displacement proxy;
- market boundary;
- population movement;
- scheduler/coupling;
- aggregate-resolution reconciliation;
- uncertainty/ensemble runner;
- ensemble reporting guardrails that distinguish scenario spread, parameter sensitivity, uncertainty spread and stochastic variability;
- executable A1–A9 accounting/physical identity auditor;
- signed Earth-boundary reconciliation;
- staged multi-year WIP and multi-rate synchronization fixtures.

The A1–A9 property fixture captures state before every scheduler-valid transition and evaluates all nine identities immediately after each transition. Current generative coverage includes disbursement, WIP spend, commissioning, depreciation, extraction, revenue, surplus disposition and commitment lapse.

The multi-rate synchronization fixture combines day-scale mission observations, quarterly finance and annual Earth-system events under one deterministic scheduler.

Transport, technology gating, dynamic economic reserve conversion, mature colony operations and autonomous policies remain incomplete unless separately implemented and validated.

## 8. Reproducibility package

Every executable result intended for comparison must preserve:

- run manifest;
- scheduler version and event ordering;
- complete parameter values;
- universe/input snapshot identities;
- event-log fingerprint;
- terminal-state fingerprint;
- test/validation record;
- known limitations.

## 9. Relationship to governance

This ODD-aligned specification is operational documentation, not epistemic authority. It does not qualify inputs or convert validation fixtures into evidence. TRACE-like rationale, testing and validation status are carried by the Phase 3B design/validation records and the V&V protocol.

## 10. Current validation boundary

The executable kernel is verified against selected invariants and deterministic fixtures. It is not yet empirically validated as a civilization/economic forecasting model. Behavioral calibration, historical/backcast validation and out-of-sample validation are future gates.
