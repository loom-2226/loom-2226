# LOOM Offworld Simulation
## Guiding Functional Requirements Document
### MVP: Capital, Exploration, Resources, Agents, and Settlement

**Status:** PRELIMINARY FRD / PRE-CONTRACT  
**Authority status:** PRE-CONTRACT / SINGLE-AUTHORITY  
**Canonical status:** NON-CANON  
**Implementation authority:** SCOPED PHASE 3B AUTHORIZATIONS 001/002/003/004/005/006/007/008; FULL AUTONOMOUS AGENT ENGINE REMAINS GATED  
**Phase basis:** Phase 2 Claim and Authority Model  
**Purpose:** Define the minimum functional system required to demonstrate governed offworld civilization propagation without scripting historical outcomes.

---

## 1. Mission

LOOM shall provide a simulation in which capital originating in an Earth economy can be allocated to offworld activity by persistent institutional agents operating under imperfect information.

Those agents shall be able to explore a celestial body, acquire observations, update their internal beliefs, decide whether to invest further, establish projects, extract resources where scenario-world resources actually exist, lose capital where ventures fail, and contribute to the formation or failure of an offworld settlement.

The MVP shall demonstrate the causal chain:

`Earth Reference -> Capital -> Agent Decision -> Exploration -> Observation -> Belief -> Investment -> Extraction -> Settlement -> Realized State`

The system shall produce outcomes from state, rules, information and agent decisions. It shall **not prescribe a future history**.

## 2. MVP Success Criterion

The MVP succeeds when it can demonstrate:

> **A capital-constrained agent, operating with imperfect information about a hidden scenario-world resource, can decide whether to explore and develop it; spend capital diverted from an immutable Earth reference economy; receive imperfect observations; update its beliefs; succeed or fail against fixed hidden scenario state; extract and sell material when successful; return, lose, or reinvest capital according to explicit rules; and contribute to the growth or failure of a dependent offworld settlement without violating conservation, epistemic boundaries, causal lineage, or deterministic replay.**

Everything beyond this loop is progressive elaboration.

## 3. Governing Phase 2 Architecture

The MVP shall preserve the Phase 2 separation between:

`Evidence -> Scenario World -> Agent Information -> Agent Belief -> Decision -> Action -> Realized State`

These are not interchangeable representations of the same thing.

> **LOOM may define physical truth inside an explicitly authorized scenario. Scenario truth shall never become evidence about the real Solar System merely because it exists, is simulated repeatedly, or produces successful outcomes.**

> **An agent may act only upon information available within that agent's epistemic perspective. Permission to use information shall never create information the agent does not possess.**

## 4. Required World Contexts

The MVP shall implement the Phase 2 world-context distinction.

### 4.1 REAL

Represents propositions about the real-world evidence/reference domain, including admitted Solar evidence and Earth reference inputs.

### 4.2 SCENARIO(id)

Represents the declared hidden physical and exogenous state of a particular simulation universe.

Example:

```
SCENARIO(SPARSE-001)
Ceres
resource_X
quantity = 20 Mt
```

This proposition does not modify the corresponding REAL proposition.

### 4.3 REALIZED(run_id)

Represents state resulting from simulation transitions.

Example:

```
REALIZED(RUN-017)
Ceres
resource_X
remaining_quantity = 19.6 Mt
```

The three contexts shall remain independently queryable. No implicit crossing between them is permitted.

## 5. Required Epistemic Perspectives

The MVP shall implement at least:

- `GOVERNANCE`
- `WORLD_SIM`
- `AGENT(agent_id)`

WORLD_SIM may access authorized hidden scenario-world state. An agent shall not.

A hidden scenario quantity may coexist with an agent belief or UNKNOWN state without contradiction. An observation may change the agent state without changing hidden truth.

## 6. Evidence and Solar State

Existing Solar evidence shall remain on the REAL evidence plane.

The MVP shall preserve observed values, bounded values, physical/model-derived values with lineage, explicit UNKNOWN, evidence scope, characterized uncertainty, and search/assessment scope where relevant.

A simulation-generated quantity, composition, grade, deposit, observation, or extraction result shall never be written back as Solar evidence.

Where REAL resource quantity is UNKNOWN, a SCENARIO(id) quantity may nevertheless exist. The scenario value does **not** resolve the empirical UNKNOWN.

## 7. Earth Reference and Realized Earth State

The MVP shall distinguish `Earth_reference(t)` from `Earth_realized(t)`.

The adopted Earth BAU trajectory shall remain immutable and retain its underlying epistemic ancestry, including projection ancestry where applicable. Reference adoption shall not convert a projection into an observation.

The MVP shall initially implement Earth-realized consequences through a shadow accounting layer:

`DeltaEarth(t) = Earth_realized(t) - Earth_reference(t)`

At minimum this layer shall record capital diverted to offworld activity, capital returned, offworld purchases from Earth, Earth purchases from offworld ventures, migration from Earth, and returning population.

The MVP shall **not** modify the underlying Earth reference series. Full feedback into the Earth propagation model is outside MVP scope.

## 8. MVP Scenario Universe

The MVP shall use authored hidden scenario state rather than a generalized procedural Solar-System resource generator.

At minimum three immutable universe configurations shall exist:

- **NULL:** no commercially useful target deposit.
- **SPARSE:** a target deposit exists under deliberately constrained conditions.
- **RICH:** a materially more favorable target deposit exists.

Each universe shall be version identified. Changing hidden truth after observing results creates a **new universe version**.

An owner-authored planted value is a `SCENARIO_STIPULATION`. A future value produced by an authorized generator is a derived scenario-world proposition with generator, parameter, evidence-constraint, version, and seed lineage. A realized value changed by simulation transition is `SIMULATED` state in REALIZED(run_id).

These shall not be collapsed into one generic SCENARIO_ASSUMPTION label.

## 9. MVP Physical Target

The first executable experiment should deliberately use:

- one participating Earth economy;

The participating economy is deliberately **UNSELECTED** at the architecture level. Historical CIVPROP use of `AUS`/Australia as a bounded Earth–Luna test actor creates no default, preference, capability inheritance, budget inheritance, access inheritance, or fixture-selection priority for this MVP. A concrete economy may be chosen only by an explicit documented fixture-selection act. All interfaces and rules remain country-neutral.
- one target celestial body;
- one resource family;
- one public institutional agent;
- one private institutional agent.

The target body should preferably have sufficient admitted physical information to establish meaningful physical bounds.

Additional physical assumptions require explicit authorization and lineage.

## 10. Resource State

The model shall distinguish:

`R_in_situ != R_accessible != R_recoverable != R_reserve`

- **In-situ resource:** physical scenario-world material present.
- **Accessible resource:** material physically reachable under relevant conditions.
- **Technically recoverable resource:** material recoverable using available technology.
- **Economic reserve:** recoverable material economically worth exploiting under current scenario economic conditions.

Conceptually:

`Recoverability(t) = f(ResourceState, PhysicalAccess, Technology_t)`

`Reserve(t) = f(Recoverability, Prices_t, Transport_t, Capital_t)`

A physical deposit shall not become an economic reserve merely because it exists.

## 11. Transport

Transport shall be represented as a relationship rather than a property of a deposit.

At minimum:

`T(i,j,t) = {Cost, TravelTime, Energy, LossRisk, Capacity}`

Transport values may depend on technology state. The MVP need not implement detailed orbital logistics if an authorized simplified transport model satisfies the experiment.

Cost, time, energy, and risk shall remain conceptually distinct. A propulsion improvement alters the opportunity set; it does not directly cause investment, settlement, extraction, or economic success.

## 12. Technology

Technology shall be an exogenous scenario input for the MVP. It defines what is possible or how expensive/difficult an action is. It shall not prescribe what agents do.

Technology inputs shall retain scenario lineage and authorization.

## 13. Agent Contract

MVP runtime objects shall be classified as one of:

- SYSTEM;
- AGGREGATE;
- AGENT;
- ENTITY_ASSET.

Only AGENT represents a persistent decision-making unit. SYSTEM applies declared mechanisms/rules without beliefs or objectives. AGGREGATE represents many actors statistically/behaviorally without individual autonomous identities. ENTITY_ASSET carries persistent state/identity but does not decide.

All admitted AGENT objects implement the conceptual contract:

```
agent_id
agent_type
scope/location
assets/accounts
information
beliefs/internal_state
capabilities
objectives
decision_policy
available_actions
persistent_history
runtime_class = AGENT
```

Interaction sequence:

`World/System State -> Observation -> Agent Information -> Belief -> DecisionRequest -> Decision -> ActionRequest -> Kernel Validation -> World Transition`

An AGENT submits an action request. It shall not directly mutate world state.

Runtime complexity, economic importance, ownership, counterparty status, or possession of an identifier do not by themselves confer AGENT status. Agency shall be used where explicit bounded choice materially affects the modeled causal question.

Resolution may change only through explicit reconciliation. AGGREGATE -> AGENT exposure/promotion must preserve applicable money, ownership, population, resource, information-history and lineage state. Silent type mutation is prohibited.

The normative runtime classification decision is `PHASE3B_RUNTIME_OBJECT_CLASSIFICATION_DECISION_001.md`.

## 14. MVP Agents

The MVP may contain multiple institutional AGENT roles while using SYSTEM/AGGREGATE representations for routine mechanisms and high-volume populations.

Initial decision-bearing roles may include:

### 14.1 Public institutional agent

Represents an authorized public offworld program where an explicit institutional choice is causally relevant. It may fund or conduct exploration, publish observations, establish/support infrastructure or settlement, move population, or subsidize activity subject to funding, capability, technology and action rules.

### 14.2 Sponsor/operator agent

Represents a project sponsor/operator where explicit project initiation, continuation, abandonment, extraction, sale or reinvestment choices are required.

### 14.3 Financier agent

Represents an institutional financier where explicit underwriting/allocation decisions are required. Financier information and beliefs are separate from hidden world truth.

### 14.4 Local/offworld financier

Represents an offworld financing institution only when its own decision process is explicitly modeled. A local financing vehicle that merely holds claims/accounts may remain ENTITY_ASSET/SYSTEM-managed state rather than an AGENT.

The MVP shall not create autonomous Agents for ordinary market clearing, physical production, accounting, routine transport mechanics, households, workers, minor firms or every individual person merely because those phenomena exist. Those may remain SYSTEM or AGGREGATE representations until a causal need justifies higher resolution.

General autonomous decision-policy authority remains gated. Build 5 has individually authorized bounded autonomous policies for the private financier (Test 001), public institutional explorer (Test 002A), public observation publisher (Test 002B), and private sponsor/operator (Test 005A). Those scoped authorizations do not authorize other Agent roles or a general autonomous-agent engine. Deterministic scripted policies may continue to exercise other interfaces for validation only.

## 15. Agent Information Firewall

Agents shall never directly query hidden scenario truth.

World-side parameters and agent-side informational parameters shall remain distinct. A parameter used on both sides must either:

1. exist as a separately declared agent-side parameter with independent lineage; or
2. be explicitly stipulated as information known to the agent.

This applies to priors, detection rates, false-positive rates, likelihood functions, noise models, cost distributions, and risk estimates.

World seeds and world random streams shall never constitute agent information. Equality between a world parameter and an agent-side parameter is itself an explicit scenario assumption where material.

DECISION_WINDOW policies shall not receive the kernel, scheduler, world state, scenario-resource registry, run identity, universe identity, world seed, or hidden state. They shall receive only an immutable `DecisionSnapshot` plus an opaque deterministic decision key through `PolicyContext`.

`DecisionSnapshot` is a copied value object containing only admitted agent-visible state and explicitly admitted facts. UNKNOWN and BLOCKED facts carry no value. Generic kernel-bearing handlers are prohibited in DECISION_WINDOW.

Normative decision: `PHASE3B_DECISION_SNAPSHOT_POLICY_FIREWALL_DECISION_001.md`.

## 16. Exploration and Observation

The MVP shall implement at least:

- **Remote observation:** noisy indication concerning target resource presence.
- **Surface prospecting:** higher-quality information and potentially an estimate of grade or quantity within modeled limits.

Development may reveal additional physical state required for operation.

> **Exploration changes information, not physical reality.**

> **Extraction changes realized physical state.**

Build 5 Test 002A structurally implements the first bounded autonomous public REMOTE-observation decision path. The Agent decides whether to acquire information from admitted mission/capability/budget/cost state; a later WORLD_SIM/SYSTEM transition generates the imperfect observation from hidden scenario state.

Build 5 Test 007A structurally implements second-stage SURFACE prospecting by the same public Agent. SURFACE requires a legitimately possessed prior REMOTE observation, a separately declared cost, admitted capability and budget. WORLD_SIM generates the SURFACE signal with an explicitly versioned higher-quality Test-only error model; a later Agent-side information update uses separately declared likelihood parameters and does not query hidden truth. The qualification fixture demonstrates a NULL-world REMOTE false positive corrected by a later SURFACE negative observation while hidden resource state remains unchanged.

Test 007A closes the mandatory higher-quality surface-information path. The optional grade/quantity estimate is not implemented and shall require its own measurement/unit/uncertainty contract if later needed.

## 17. Beliefs

Each agent shall maintain an internal belief state concerning uncertain target properties. The MVP may use a simple Bayesian model.

Exact belief models and parameters are model/scenario-governed inputs requiring authorization.

Build 5 Test 007A adds the first explicit Bayesian Agent-side observation update for SURFACE prospecting. Its likelihood parameters are separately declared Test-only informational inputs and are not inferred from hidden WORLD_SIM truth. Earlier validation paths using deliberately crude belief updates remain historical structural fixtures rather than calibrated learning models.

A proposition that an agent believes a resource exists with probability 0.72 does **not** assert that probability on the REAL evidence plane or as hidden scenario truth. Belief is agent state.

## 18. Capital Origin

The earlier shorthand `P_c(t)=f I_c(t)` is superseded for executable design.

Earth `INVESTMENT_REAL_PROXY` / reference FCF is not spendable cash and shall not be converted directly into an actor balance.

The current MVP semantic chain is:

`Earth reference economic scale -> explicit financing/resource-allocation abstraction -> financing decision -> commitment -> disbursement -> expenditure -> WIP/FCF -> productive asset -> production/revenue -> surplus disposition -> later financing`.

Earth-side financing may use `FINANCING_AUTHORIZATION` as an explicit MVP abstraction for institutions not yet modeled. Separately, qualifying Earth-supplied expenditure may be bounded by an authored reference-FCF-scaled allocation constraint.

These are model abstractions, not measurements of savings, banking liquidity, fiscal capacity or supplier output.

Earth reference remains immutable. Any modeled displacement/impact is written to realized/shadow state and lineage, never by rewriting the reference trajectory.

The governing financing design is `PHASE3B_FINANCING_RECURSIVE_FCF_FINALIZED_CANDIDATE_0_1.md`; the explicit accounting boundary is `PHASE3B_MVP_ACCOUNTING_BOUNDARY_CANDIDATE_0_1.md`.

## 19. Financial Conservation

The MVP shall implement double-sided or otherwise explicitly reconcilable accounting.

At minimum:

`sum(Sources) - sum(Uses) = DeltaFinancialState`

Every payment shall have a source and destination.

Resource sales require a buyer or explicit external-market clearing account. For MVP, an authored Earth demand/price series may drive an `EARTH_MARKET` clearing account.

A sale decreases buyer cash and increases seller cash. No sale may simply increase seller cash without a corresponding counter-entry.

Failed investment may destroy economic value, but the financial transition producing the loss shall remain ledgered.

## 20. Project State

A venture shall have explicit lifecycle state, at minimum:

```
PROPOSED
EXPLORING
DEVELOPMENT
OPERATING
ABANDONED
FAILED
CLOSED
```

Transitions occur through governed world actions. Proposal or funding shall not imply successful development.

Build 5 Test 005A structurally closes bounded sponsor-controlled entry from `PROPOSED`/`EXPLORING` to `DEVELOPMENT` or `ABANDONED`. Test 006A then closes bounded SYSTEM execution from `DEVELOPMENT` through an explicit staged construction plan and persistent WIP to either `OPERATING` after full commissioning or `FAILED` after incomplete construction. `OPERATING` means the declared productive facility has been commissioned; it does not establish that hidden resource truth is favorable, extraction will succeed, or the venture is economically successful. Test 008A subsequently closes the first bounded sponsor operating-cycle decision and WORLD_SIM resource-bounded extraction from an `OPERATING` project. `CLOSED`, sponsor response after failed/zero/partial output, and repeated operating-cycle lifecycle semantics remain separately gated.

## 21. MVP Project Economics

Detailed mining engineering is outside MVP scope.

A simplified model may use:

`Revenue = q P`

`Cost = C_exploration + C_construction + C_extraction + C_transport + C_energy`

subject to appropriate difficulty/technology multipliers.

These relationships are model scaffolding, not future empirical claims. The transformation itself is a dependency with version and standing.

Build 5 Test 008A structurally implements a bounded operating-cost/extraction slice. Planned production equals admitted productive-asset capacity; planned cycle OPEX equals planned quantity times the admitted Test-only unit operating cost; OPEX is spent before WORLD_SIM resolves actual recovery; and actual extraction is bounded by realized resource remaining. Full, partial and zero-output cycles are therefore possible from identical Agent-side operating decisions. This does not calibrate real mining throughput, recovery, or cost.

## 22. Prices and Demand

The MVP may use an owner-authorized exogenous price/demand series.

Prices shall not create revenue independently. Actual sales remain constrained by modeled demand or the authorized market-clearing mechanism.

Endogenous commodity markets are outside MVP scope.

## 23. Colony MVP

A colony shall initially be a transparent stock-flow node rather than a miniature macroeconomic model.

Minimum state:

```
population
cash
productive_capital
infrastructure
resource_inventory
import_inventory
production_capacity
operating_need
external_subsidy
stage
```

The MVP should **not initially require a Cobb-Douglas production function**. Production shall arise from explicit available productive capacity, inputs, and operating rules.

## 24. Colony Stages

Stages shall be computed from realized state rather than narratively assigned.

The MVP may support:

```
PROSPECTING
EXTRACTION_ENCLAVE
DEPENDENT_SETTLEMENT
DIVERSIFYING_SETTLEMENT
HANDOFF_CANDIDATE
```

Thresholds are explicit parameters. HANDOFF_CANDIDATE raises a readiness condition; it does not automatically instantiate a full independent economy.

## 25. Population Conservation

Migration shall be ledgered.

`N_system(t+1) = N_system(t) + Births - Deaths`

Migration changes location, not total population.

An Earth departure must correspond to an offworld arrival, subject to explicitly modeled loss if mortality during transit is later included.

The MVP may initially omit births/deaths if appropriate to experiment duration, but may not create settlers ex nihilo.

## 26. Realized State

Actions shall modify only appropriate realized state.

Examples:

- spending changes realized financial state;
- exploration changes agent information;
- construction changes project/infrastructure state;
- migration changes realized population location;
- extraction changes realized resource stock and corresponding offworld resource inventory;
- sale changes inventories and financial accounts.

None modifies REAL evidence.

## 27. Events and Causal Ledger

Every state-changing operation shall produce an event identifying at minimum:

```
event_id
run_id
time
actor
action
world_context
inputs
prior_state
result
new_state
reason
parameter_version
scenario/universe_version
random_stream_identity if applicable
lineage/dependencies
```

The system shall support reconstruction of:

`Result -> Event -> Decision -> Information -> Inputs + Rules`

Failed or blocked actions are causally meaningful and inspectable where relevant.

## 28. Deterministic Randomness

Random processes shall use stable keyed streams rather than execution order.

Conceptually:

```
master_seed
run_id
year
process
agent_id
body_id
resource_id
```

The same governed input snapshot, code/model version, parameters, scenario universe, and seed shall reproduce the same run result according to the declared replay standard.

Removing an unrelated actor shall not perturb unrelated random streams.

## 29. Three-Universe Experiment

The first qualification experiment shall execute otherwise-identical runs against NULL, SPARSE, and RICH.

Before any observation capable of distinguishing the universes occurs:

`Actions_NULL = Actions_SPARSE = Actions_RICH`

assuming identical agent information and random streams.

Hidden truth alone shall not alter agent behavior. After observations differ, histories may legitimately diverge.

This is a core MVP falsification test.

## 30. Required MVP Invariants

The MVP shall enforce:

1. No evidence laundering.
2. No hidden-information leakage.
3. No money from nothing.
4. No people from nothing.
5. No resources from nothing after universe initialization.
6. No implicit world-context crossing.
7. No UNKNOWN-to-zero coercion.
8. No scenario generator distribution automatically becoming an agent prior.
9. No world random seed becoming agent information.
10. No reference mutation.
11. No outcome-conditioned universe mutation without a new universe version.
12. No direct agent mutation of world state.
13. No action outside available capability, capital, technology, and permitted action space.
14. No derived result without transformation lineage.
15. No governed consumption without declared use, time, world-context, and perspective.

## 31. Required Falsification Tests

The MVP test suite shall include deliberately failing mutations.

- **Capital:** with `f=0`, no offworld investment funded from the Earth pool.
- **Hidden resource:** removing the planted deposit prevents successful extraction.
- **Funding:** removing an agent's funding prevents spending.
- **Epistemic firewall:** changing hidden universe before distinguishing observation does not change agent behavior.
- **Beliefs:** properly modeled positive/negative observations update belief in appropriate directions.
- **Determinism:** identical input snapshot, universe, parameters, and seed reproduce the declared run hash.
- **Random-stream independence:** removing an unrelated actor does not perturb another actor's keyed stochastic sequence.
- **Accounting:** every transfer reconciles.
- **Population:** every migration reconciles.
- **Evidence:** no scenario or realized resource value appears in a REAL/GOVERNANCE evidence query.
- **Reference:** changing realized state does not mutate the adopted Earth reference.
- **Scope/admissibility:** quarantined input produces BLOCKED where required rather than UNKNOWN.

## 32. MVP Parameter Registry

Every numerical assumption shall be explicit, versioned, and lineage-bearing.

Families include capital allocation; public/private allocation; investor hurdle rate; discounting; risk tolerance; exploration cost; observation accuracy; false-positive/negative rates; agent priors; development/extraction cost; transport cost/time/energy/risk; commodity price/demand; settlement costs; operating requirements; infrastructure capacity; migration costs; public subsidy rules; reinvestment/payout rules; and colony thresholds.

Parameters shall not receive compound pseudo-epistemic labels. Their proposition role, epistemic mode, authorization, lineage, uncertainty, world-context, and governance status remain separate under Phase 2.

## 33. Explicit MVP Non-Requirements

The MVP shall not require:

- procedural generation across all 110 Solar bodies;
- detailed mine engineering;
- detailed orbital routing;
- endogenous commodity prices;
- endogenous technology development;
- banks or insurers;
- securities markets;
- inter-colony trade;
- political systems;
- law or sovereignty simulation;
- warfare;
- households;
- explicit individual humans or synthetics;
- complete Earth macroeconomic feedback;
- autonomous offworld economies;
- runtime LLM decision-making.

These remain potential later capabilities.

## 34. Preserved Long-Term Architecture

The MVP shall preserve scalable mixed resolution rather than requiring universal autonomy.

Long-term runtime composition may include:

`SYSTEM <-> AGGREGATE <-> AGENT <-> ENTITY_ASSET`

with multiple concurrent domain hierarchies such as:

`Macroeconomic Node <-> Institution <-> Firm/Household Aggregate <-> Explicit Institution/Person`

and:

`Population Aggregate <-> Cohort <-> Explicit Individual`.

Resolution is experiment-dependent. A minor firm may remain inside an AGGREGATE while a causally dominant corporation is represented as an AGENT. Promotion/exposure and any later re-aggregation require explicit reconciliation and lineage.

The generic AGENT abstraction shall not assume biological humanity. Future specializations may include Institution, Human, Synthetic, Household, Firm and Government where explicit agency is causally necessary.

## 35. Relationship to Existing CIVPROP Work

Existing CIVPROP artifacts are **archaeological and candidate reuse material**, not the governing implementation architecture for this MVP.

Potentially useful components include event/conductor concepts, deterministic keyed RNG, SPICE/transport adapters, actor capability machinery, lifecycle machinery, ledger concepts, and validation tests.

Reuse shall be component-by-component. No component acquires authority merely because it existed previously or passed a different qualification regime.

Old assumptions, commitment bridges, authority-resolution machinery, hidden-state implementations, defaults, and lifecycle behavior shall not be imported wholesale.

## 36. Relationship to Phase 3

This FRD shall serve as the principal functional stress fixture for the **Phase 3 State Model**.

Phase 3 must demonstrate simultaneous representation of:

```
REAL / GOVERNANCE
resource quantity = UNKNOWN

SCENARIO(SPARSE-001) / WORLD_SIM
resource quantity = 20 Mt

SCENARIO(SPARSE-001) / AGENT(PRIVATE_AU)
belief(resource exists) = 0.27

SCENARIO(SPARSE-001) / AGENT(PRIVATE_AU), after observation
belief(resource exists) = 0.72

REALIZED(RUN-017) / WORLD_SIM, after extraction
remaining resource = 19.6 Mt
```

without any layer acquiring another layer's epistemic standing, information access, or warrant.

Phase 3 shall perform equivalent state tracing for:

- one unit of money, proving conservation and ownership;
- one person, proving population conservation and location;
- one resource unit, proving physical conservation;
- one observation, proving information provenance;
- one belief, proving perspective isolation;
- one action, proving request-to-transition separation.

These traces bridge the Phase 2 ontology and an executable simulator.

## 37. MVP Expansion Gates

Complexity shall be added only after the preceding layer passes its invariants.

Recommended progression:

`1 economy + 1 body + 1 resource -> 2 institutional agents -> NULL/SPARSE/RICH -> multiple projects -> multiple economies -> multiple bodies/resources -> settlement -> technology transitions -> trade/markets -> coupled Earth/offworld economies -> persistent individual agents`

Each expansion shall earn its complexity by demonstrating a causal need not adequately represented at the previous level.

## 38. Guiding Requirement

The MVP shall answer:

> **Given a fixed but hidden scenario world, an immutable evidence/reference layer, finite capital, imperfect information, changing technology, and actors with different objectives, can LOOM produce a deterministic, auditable, and conservation-respecting history that was not specified in advance?**

If yes, the architectural spine exists. If no, the model is still deliberately small enough to establish why.

---

## 39. Scheduler and Coupling Requirement

The MVP shall use a deterministic scheduler contract rather than relying on incidental Python execution order.

Global time is scheduler-owned. Processes declare cadence/trigger, phase, read/write sets, state ownership, units, context/perspective and invariants.

The default macro-period phase order is:

`OPEN_PERIOD -> EXOGENOUS_INPUTS -> OBSERVATION -> INFORMATION_UPDATE -> DECISION_WINDOW -> ACTION_VALIDATION -> COMMITMENT_DISBURSEMENT -> OPERATIONS -> MARKET_CLEARING -> DEPRECIATION_AMORTIZATION -> ACCOUNTING_CLOSE -> CONSERVATION_CHECK -> SNAPSHOT_CLOSE`.

Sub-period mission/transport/operational events may occur at explicit deterministic timestamps.

Same-time tie ordering shall be stable and explicit. Queue insertion order shall not change unrelated results or random draws.

For any integrated MVP simulation run, the supported execution lifecycle is:

`initialize -> register couplings/events/handlers -> seal -> scheduled run -> immutable run result`.

Build 5 additionally supports a governed persistent decision-epoch lifecycle for repeated autonomous decisions over one kernel/world state:

`persistent state -> begin epoch -> configure fresh scheduler plan -> freeze fresh DecisionSnapshot(s) -> seal -> scheduled run -> immutable epoch result -> verified epoch completion -> persistent state -> next epoch`.

Each completed epoch records chain identity, epoch identity/ordinal, parent result fingerprint, scheduler-plan fingerprint, initial/final fingerprints, execution fingerprint and result fingerprint. Once an epoch chain starts, governed world mutators remain blocked between epochs. Persistent-state fingerprints exclude scheduler-plan state so legitimate next-epoch planning is allowed while raw world-state tampering between epochs or after epoch-open before seal is detected.

After seal, state-changing kernel methods shall reject direct calls unless they are executing inside an admitted scheduled-event context carrying the runtime execution token. Raw state or scheduler-plan mutation after seal shall invalidate the run. Legacy unsealed direct calls remain permitted only for bounded unit/validation fixtures before a decision-epoch chain starts and do not constitute a supported simulation-run pathway.

Normative candidates/decisions:

- `PHASE3B_SCHEDULER_COUPLING_CONTRACT_CANDIDATE_0_1.md`;
- `PHASE3B_SCHEDULED_EXECUTION_GATE_DECISION_001.md`;
- `PHASE3B_DECISION_SNAPSHOT_POLICY_FIREWALL_DECISION_001.md`.

## 40. ODD-Aligned Executable Specification

The MVP shall maintain an ODD-aligned operational specification covering purpose/patterns, entities/state/scales, process overview and scheduling, design concepts, initialization, input data and submodels.

This specification does not replace LOOM authority/governance records. It provides the reproducible executable-model view an independent reviewer needs to understand how a run works.

Current candidate: `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`.

## 41. Verification Versus Validation

Passing kernel tests establishes only the behavior tested against declared specifications.

The MVP shall distinguish:

- software/model verification;
- empirical/scientific validation;
- calibration;
- sensitivity analysis;
- uncertainty analysis;
- scenario exploration.

No conservation/replay pass may be described as empirical validation of long-run civilization behavior.

The methodology shall maintain validation standing by subsystem and disclose unvalidated mechanisms.

Current protocol: `PHASE3B_VERIFICATION_VALIDATION_UNCERTAINTY_PROTOCOL_0_1.md`.

## 42. Long-Horizon Uncertainty and Ensemble Requirement

The 2026–2226 horizon shall initially be treated as deep-uncertainty scenario exploration, not as a single point forecast.

Comparable runs shall vary declared scenario axes, authored parameters, characterized uncertainties and keyed stochastic realizations while preserving run identity.

An ensemble result shall support identification of:

- robust outcomes;
- divergence drivers;
- threshold/bifurcation behavior;
- sensitivity to assumptions;
- causal paths producing materially different trajectories.

Sampling a scenario does not imply a probability for that scenario.

## 43. Resolution-Reconciliation and Invariance Requirement

Before dynamic runtime resolution is used in an MVP trajectory, the executable kernel shall demonstrate both:

1. deterministic AGGREGATE -> AGENT reconciliation; and
2. resolution invariance when the exposed Agent is constrained to follow the same rule as its source Aggregate representation.

Every governed exposure shall use an explicit `ResolutionExposurePlan` declaring:

- source aggregate;
- selected agent identity;
- represented member count exposed;
- selection basis and source/authorization reference;
- allocation basis and source/authorization reference;
- explicit allocation share only when the allocation basis requires one.

Selection identity and allocation share shall not be silently invented inside the resolution transition.

At minimum the reconciliation fixture shall preserve:

- financial/account balances;
- ownership/beneficial claims where applicable;
- population or membership counts where applicable;
- assets/resources allocated to the exposed agent;
- aggregate remainder;
- history/lineage identity.

At minimum the invariance fixture shall run the same horizon twice:

- aggregate-only representation;
- aggregate plus exposed Agent representation.

While the exposed Agent follows the aggregate-equivalent rule, pathwise represented system totals shall match. Byte-identical run fingerprints are not required because representation and transaction partition may differ.

For the current validation fixture, one of four equal represented members is exposed, so the 25% share is derived as `1/4` under `EQUAL_MEMBER_PRO_RATA`, not independently authored.

Once an authorized autonomous Agent follows a different information/belief/objective/policy path, divergence is permitted only as a causally attributable consequence of those admitted differences.

If re-aggregation is implemented, it must pass reciprocal reconciliation/invariance tests where applicable.

Normative decision:

`PHASE3B_RESOLUTION_EXPOSURE_INVARIANCE_DECISION_001.md`.

## 44. Methodology-Hardening Revalidation Gate

The pre-hardening Build 4 baseline remains frozen at:

`offworld-mvp-build4-freeze-2026-10-04`.

The first methodology-hardening pass produced:

`offworld-mvp-build4-mvp-r1-2026-10-04`

at commit:

`82e31aaa218b36bbd1ba7ce75313fdccd0169c1a`.

Validation Record 005 identified one remaining execution-boundary lien: the scheduler existed and integrated fixtures used it, but inherited low-level mutation methods were still directly callable.

That lien has now been closed for integrated runs.

The scheduler-enforced Build 4-derived baseline is frozen at:

`offworld-mvp-build4-mvp-r2-scheduled-2026-10-04`

commit:

`edae7053081db20e96a00e77b752ca4c4bcecebb`.

Validation record:

`PHASE3B_KERNEL_VALIDATION_RECORD_006_SCHEDULED_RUNTIME.md`.

For an integrated MVP run, initialization occurs before seal. After seal, guarded world-state mutations are admitted only inside scheduler-dispatched runtime contexts carrying the private execution token. State or plan tampering invalidates the run, and the scheduled runtime is single-use.

This closes the scheduler-bypass lien.

The first two autonomous-policy pre-gate blockers have since been closed and frozen as:

`offworld-mvp-build4-mvp-r3-policy-firewall-2026-10-04`

at commit:

`5f3285b28e4ce05979afc52f29930f9966e79983`.

Validation record:

`PHASE3B_KERNEL_VALIDATION_RECORD_007_MUTATOR_AND_POLICY_FIREWALL.md`.

R3 adds exhaustive inherited-mutator sealing evidence and the immutable DECISION_WINDOW DecisionSnapshot/PolicyContext firewall.

The resolution-invariance pre-gate has since been closed and frozen as:

`offworld-mvp-build4-mvp-r4-resolution-invariance-2026-10-04`

at commit:

`bba276b3eff69a0101fed1235f5958cd4186e6d0`.

Validation record:

`PHASE3B_KERNEL_VALIDATION_RECORD_008_RESOLUTION_INVARIANCE.md`.

R4 adds explicit exposure-selection/allocation plans and demonstrates five-period pathwise equivalence between aggregate-only and exposed-Agent representations when the Agent follows the aggregate-equivalent rule.

The next four autonomous-policy pre-gate items have since been implemented and frozen as:

`offworld-mvp-build4-mvp-r5-underwriting-accounting-2026-10-04`

at commit:

`e952025366da44f84943fae0a9f00f4ed931fd92`.

Validation record:

`PHASE3B_KERNEL_VALIDATION_RECORD_009_ITEMS_1_4_HARDENING.md`.

R5 adds the authored underwriting input layer, ensemble reporting guardrails, scheduler-valid A1–A9 property verification, signed-boundary reconciliation, true staged multi-year WIP/depreciation, and genuine multi-rate synchronization.

It does not close Phase 3B and does not authorize autonomous decision policies.


## 45. Underwriting Input Contract

Before an underwriting policy is authorized, its required economic inputs shall exist outside the policy implementation.

The minimum MVP underwriting input set per project archetype is:

- PRICE / revenue basis;
- EXPLORATION_CAPEX;
- DEVELOPMENT_CAPEX;
- OPERATING_COST;
- LEAD_TIME.

Every input shall carry stable identity, unit, status, source or explicit scenario rationale, sensitivity range where characterized, and applicable validity/scope.

UNKNOWN is a legal input state and shall not be converted to a fallback number by a policy.

The initial executable table is explicitly a PRE-CONTRACT authored validation scenario, not empirical calibration:

`phase3b/inputs/OFFWORLD_MVP_UNDERWRITING_VALIDATION_V0_1.json`.

Normative candidate:

`PHASE3B_UNDERWRITING_INPUT_CONTRACT_CANDIDATE_0_1.md`.

## 46. Ensemble Reporting Semantics

Generating an ensemble shall not imply a probability distribution over futures.

Reporting semantics shall preserve axis meaning:

- SCENARIO -> scenario spread, not probability;
- PARAMETER -> sensitivity;
- UNCERTAINTY -> uncertainty spread;
- STOCHASTIC_KEY -> stochastic variability.

Probability-weighted summaries require an explicit weight-authority reference and complete normalized case weights. There is no default equal-probability interpretation of scenario cases.

Mean-with-interval reporting remains prohibited until both probability authority and an interval method are explicitly governed.

Normative candidate:

`PHASE3B_ENSEMBLE_REPORTING_GUARDRAILS_0_1.md`.

## 47. Executable A1–A9 Accounting Identities

The MVP adopts the A1–A9 accounting/physical identity set preserved in:

`PHASE3B_ACCOUNTING_IDENTITY_REGISTER_0_1.md`.

The executable kernel shall be able to check all nine identities against a pinned pre-transition state.

For scheduler-valid property testing, a deterministic seeded validation SYSTEM shall:

1. choose only transitions valid in current state;
2. execute them through the sealed scheduler runtime;
3. capture a pre-transition accounting snapshot;
4. check A1 through A9 immediately after every transition;
5. cover commitment/disbursement, WIP/spend/commissioning, depreciation, extraction, revenue, surplus disposition and lapse across the seeded suite.

This verification does not imply empirical validity.

## 48. Accounting and Multi-Rate Edge Requirements

The MVP shall explicitly verify the following edge cases:

### 48.1 Signed boundary reconciliation

For each Earth boundary account, the signed boundary mirror shall equal both:

- account closing balance minus registered opening balance; and
- cumulative transaction-ledger inflows minus outflows.

A mismatch is an invariant failure.

### 48.2 Staged multi-year WIP

At least one deterministic fixture shall carry the same WIP identity across multiple spending years before commissioning and then apply nonzero depreciation in a later period.

### 48.3 Genuine multi-rate synchronization

At least one deterministic fixture shall couple distinct cadences rather than merely sort fractional timestamps.

The current MVP test couples:

- day-scale mission observation events;
- quarterly financing events;
- annual Earth-system events.

At a shared effective timestamp, scheduler phase semantics determine which state each process observes.


## 49. Build 5 Entry Gates

Build 4 may close and Build 5 may branch only after all four entry gates pass:

### G5-1 Replay provenance

Every integrated run manifest shall include exact Git commit and executable-code SHA-256 together with input, parameter and table manifest identities, scheduler-plan identity, execution fingerprint, and final result fingerprint.

Normative candidate:

`PHASE3B_REPLAY_PROVENANCE_CONTRACT_0_1.md`.

### G5-2 Validation standing

Validation manifests shall distinguish calibration, validation, held-out and out-of-sample material. Empirical validation claims require explicit held-out/out-of-sample standing and disclosure. `NOT_EMPIRICALLY_VALIDATED` remains distinct.

### G5-3 Executable-to-ODD drift

The ODD specification shall contain a machine-readable registry of the executable runtime/interface dataclass fields. The regression suite shall compare that registry exactly against the executable schema and fail on undeclared additions, removals or renames.

### G5-4 Financing request / decision protocol

The pre-policy financing interface shall define immutable request and decision artifacts. Decision outcomes are exactly:

- APPROVE;
- REJECT;
- DEFER;
- BLOCKED_UNKNOWN.

Required UNKNOWN inputs shall produce BLOCKED_UNKNOWN rather than zero substitution, generic rejection, or silent defer.

Normative candidate:

`PHASE3B_FINANCING_REQUEST_DECISION_PROTOCOL_0_1.md`.

Passing these gates authorizes Build 4 closure and creation of a Build 5 branch only. It does not itself authorize autonomous policy behavior.


## Governance note

This FRD is a build-guiding candidate on a branch created from the closed Phase 2 governance branch. It does not reopen Phase 2, release Contract v1, qualify inputs, or grant implementation authority. Phase 3 state-model work must consume the consolidated Phase 2 normative model and preserve its carried liens.

## 50. Build 5 Bounded Autonomous-Agent Standing

Build 5 has now admitted individually scoped bounded autonomous policies across three institutional Agents together with governed decision-epoch and project-development lifecycle infrastructure under the PRE-CONTRACT / SINGLE-AUTHORITY model.

### 50.1 Private financier — Test 001

The bounded private-financier policy is structurally verified. It consumes only admitted Agent-visible state and a formal financing request, emits an immutable financing decision, and relies on later scheduler/kernel transitions for world consequences. Its synthetic numeric parameters remain `TEST_ONLY / NOT_POLICY_BASELINE`; operator-observed scenario output is descriptive rather than empirical validation.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_001_FINANCIER_TEST001.md`;
- `build5/BUILD5_VALIDATION_RECORD_001_FINANCIER_STRUCTURAL.md`;
- `build5/BUILD5_OPERATOR_RUN_RECORD_001_SYNTHETIC_FINANCIER.md`.

### 50.2 Public institutional explorer — Test 002A

The bounded public institutional explorer is authorized as a generic `PUBLIC_INSTITUTIONAL_AGENT`; “NASA-like” is design shorthand only. The first policy decides whether to authorize a REMOTE information-acquisition action from admitted mission objective, capability, budget and known cost. It contains no consequential numeric behavioral threshold.

If authorized, later scheduler phases ledger public funding/expenditure and invoke a WORLD_SIM observation mechanism. The policy itself receives neither hidden resource truth nor world random state. Hidden NULL/RICH state therefore cannot alter the pre-observation decision when admitted Agent state is identical; Agent information/belief may diverge only after the distinguishing observation.

Test 002A by itself does not close publication to other Agents, surface prospecting, sponsor/operator autonomy, empirical observation-model calibration, or real-institution fidelity. Publication is subsequently closed structurally by Test 002B, and the bounded higher-quality SURFACE information path is subsequently closed structurally by Test 007A.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_002_PUBLIC_EXPLORER_TEST002A.md`;
- `build5/BUILD5_VALIDATION_RECORD_002_PUBLIC_EXPLORER_STRUCTURAL.md`.

### 50.3 Public observation publication and financier response — Test 002B

The bounded public publisher policy is structurally verified as a second policy of the existing public institutional Agent. Under the declared `PUBLIC_INFORMATION` objective it may publish a legitimately possessed positive or negative observation; it does not receive hidden scenario truth and it does not use a numeric publication threshold.

A later scheduled publication SYSTEM creates an immutable public-information artifact, preserves source-observation and publisher lineage, and transfers the observation to declared recipients. The recipient financier updates its own belief using explicitly admitted financier-side likelihood parameters. Hidden NULL/RICH state cannot alter financier behavior before publication when admitted financier state is identical.

The structural fixtures demonstrate positive publication -> financier belief `0.50` -> `APPROVE`, negative publication -> financier belief `0.05882352941176470588235294118` -> `REJECT`, and a NULL-world false positive that legitimately yields financier `APPROVE` while hidden resource truth remains zero.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_003_PUBLICATION_FINANCIER_TEST002B.md`;
- `build5/BUILD5_VALIDATION_RECORD_003_PUBLICATION_FINANCIER_STRUCTURAL.md`.

Test 002B does not close surface prospecting, sponsor/operator autonomy, or empirical observation-model calibration. The subsequent governed decision-epoch runtime authorization closes the bounded repeated-decision seam without creating a mutable live-policy interface.

### 50.4 Governed persistent decision epochs — Test 004

Build 5 now supports repeated autonomous decision cycles over one persistent kernel/world state. Each epoch uses a fresh scheduler plan and fresh immutable DecisionSnapshot references, executes through the existing sealed ScheduledSimulationRuntime, and records cryptographically linked epoch provenance before the seal is released for preparation of the next epoch.

Once an epoch chain starts, governed world mutators remain blocked outside scheduled-event context, including between epochs. Persistent-state fingerprints distinguish legitimate scheduler-plan construction from world-state mutation and reject raw-state tampering between epochs or after epoch-open before seal. Stale pre-consequence Agent snapshots are rejected when later epoch registration compares them with current admitted Agent-visible state.

The structural qualification chain executes public publication in Epoch 1 and a fresh post-publication financier decision plus scheduled financing consequence in Epoch 2 on the same persistent kernel. RICH produces post-publication financier belief `0.5`, `APPROVE`, financier cash `40`, project cash `60`; NULL produces belief `0.05882352941176470588235294118`, `REJECT`, financier cash `100`, project cash `0`.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_004_DECISION_EPOCH_RUNTIME.md`;
- `build5/BUILD5_VALIDATION_RECORD_004_DECISION_EPOCH_RUNTIME.md`.

This closes the bounded repeated-decision runtime prerequisite for sponsor/operator autonomy and iterative exploration. It does not authorize additional Agent roles or empirical parameters.

### 50.5 Private sponsor/operator — Test 005A

Build 5 now contains the first bounded autonomous private sponsor/operator policy using the same generic `AGENT -> DecisionSnapshot -> PolicyContext -> Decision -> scheduled SYSTEM transition` architecture as the previously qualified institutional Agents.

The policy introduces no arbitrary probability threshold. From admitted information, beliefs/priors, project status, project cash and known development cost, it may `DEFER`, `ABANDON`, `REQUEST_FINANCE`, `DEVELOP`, or `BLOCKED_UNKNOWN`. Legitimate evidence that does not improve the sponsor's current resource belief above its prior leads to `ABANDON`; improved belief with a funding shortfall leads to a financing request for the exact shortfall; improved belief with sufficient project cash leads to `DEVELOP` when the Agent has the admitted capability.

The positive structural chain spans four persistent decision epochs: public publication -> sponsor `REQUEST_FINANCE` for `60` -> financier `APPROVE` and scheduled funding -> fresh sponsor `DEVELOP` -> governed `PROPOSED -> DEVELOPMENT`. At the end of Test 005A the project owns no WIP/productive asset, so `DEVELOPMENT` records the sponsor's decision to advance rather than successful construction or operation.

The negative structural chain publishes a negative observation, lowers sponsor belief from `0.20` to `0.05882352941176470588235294118`, and produces sponsor `ABANDON` -> governed `PROPOSED -> ABANDONED` with no financing request or funding.

Test 005A also hardens decision-epoch persistent-state fingerprints to include the full currently modeled Agent state plus project lifecycle/ownership and commitment state. Raw sponsor-capability or project-status edits between epochs are therefore detected as tampering.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_005_SPONSOR_OPERATOR_TEST005A.md`;
- `build5/BUILD5_VALIDATION_RECORD_005_SPONSOR_OPERATOR_STRUCTURAL.md`.

Test 005A by itself does not close surface prospecting, construction/WIP execution after `DEVELOPMENT`, later lifecycle transitions, autonomous extraction/sale/reinvestment, transport/technology economics, empirical sponsor calibration, or production forecasting. The subsequent Test 006A closes the bounded staged-construction execution portion only.

### 50.6 Project development lifecycle — Test 006A

Build 5 now executes an explicit immutable development plan after the sponsor has entered `DEVELOPMENT`. The lifecycle SYSTEM reuses the existing Build 4 staged-WIP, FCF, supply/resource-allocation, commissioning and accounting machinery rather than creating a parallel construction model.

The successful structural case spends `30` in year 6 and `30` in year 7 against a declared development cost of `60`, then commissions one PRODUCTIVE asset with book value `60` and structural capacity `10` at year-8 completion. The project transitions `DEVELOPMENT -> OPERATING` only after all declared stages are spent and full WIP is commissioned.

The constrained-supply structural case spends `30` in year 6, blocks the indivisible year-7 `30` stage against a Test-only Earth allocation ceiling of `20`, and resolves at completion as `FAILED`. The existing `30` WIP is explicitly written off, no productive asset is created, and the unspent `30` project cash remains reconciled. WIP now satisfies `accumulated_cost = commissioned + written_off + remaining_wip`.

Construction does not query hidden resource truth. A NULL-world false-positive case with zero hidden resource reaches the same successfully commissioned `OPERATING` facility as the otherwise-equivalent RICH case when construction inputs are identical. `OPERATING` therefore denotes a commissioned facility, not a claim that extraction will succeed or the venture is profitable.

The successful RICH history now spans five cryptographically parent-linked epochs: publication -> sponsor financing request -> financier funding -> sponsor `DEVELOP` -> staged construction/commissioning. A1-A9 and deterministic replay remain satisfied.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_006_PROJECT_LIFECYCLE_TEST006A.md`;
- `build5/BUILD5_VALIDATION_RECORD_006_PROJECT_LIFECYCLE_STRUCTURAL.md`.

Test 006A does not by itself close surface prospecting, `CLOSED`, sponsor choices after `FAILED`, autonomous extraction/sale/reinvestment, operating-cost execution, transport/technology economics, empirical construction calibration, settlement, or production forecasting. Surface prospecting is subsequently closed structurally by Test 007A.

### 50.7 Public surface prospecting — Test 007A

Build 5 now implements second-stage SURFACE prospecting through the existing generic public Agent and exploration request architecture. A SURFACE request names a prior REMOTE observation and uses channel-specific admitted cost facts. The bounded surface policy contains no probability threshold; it authorizes only when the Agent has the public-information objective, `EXPLORE` and `SURFACE_PROSPECT` capabilities, possession of the prerequisite observation, known cost and sufficient budget.

WORLD_SIM then independently validates that the prerequisite exists, is possessed, concerns the same resource and is REMOTE. The structural surface model has Test-only world false-positive/false-negative rates of `0.05/0.05`, strictly lower than the Test 002A remote references of `0.20/0.20`. Agent-side likelihood parameters remain separately declared and drive a later Bayesian information update without access to hidden truth.

The RICH qualification path is REMOTE `POSITIVE`, belief `0.20 -> 0.50`, SURFACE `POSITIVE`, belief `0.50 -> 0.95`. The pinned `NULL_SURFACE_1` path produces a legitimate REMOTE false positive from draw `0.1668687604247574150957700301`, reaches an identical pre-SURFACE Agent state and identical SURFACE decision, then produces a SURFACE `NEGATIVE` from independently keyed draw `0.1556196131252563241448988451`, updating belief `0.50 -> 0.05`. Resource quantity remains unchanged in both paths.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_007_SURFACE_PROSPECTING_TEST007A.md`;
- `build5/BUILD5_VALIDATION_RECORD_007_SURFACE_PROSPECTING_STRUCTURAL.md`.

Test 007A does not implement grade/quantity estimation, autonomous sponsor prospecting, empirical sensor calibration, extraction, operating economics, transport/technology economics, settlement, or production forecasting. The subsequent Test 008A closes the first bounded sponsor operating-cost/extraction slice only.

### 50.8 Sponsor operating cycle and physical extraction — Test 008A

Build 5 now contains a bounded autonomous `SPONSOR_OPERATING_V1` policy using the same generic `AGENT -> DecisionSnapshot -> isolated policy -> immutable Decision -> scheduled SYSTEM consequence` architecture. From admitted project status, cash, productive-asset capacity, operating cost, relevant information and sponsor belief/prior, it may `REQUEST_FINANCE`, `OPERATE`, `DEFER`, or `BLOCKED_UNKNOWN`. It receives no hidden resource quantity.

The Test-only operating fixture commissions capacity `5` and carries unit operating cost `4`, so one full planned cycle costs `20`. With project cash exhausted by construction, the sponsor first requests exactly `20` of operating finance. The existing bounded financier independently approves that formal request, after which a fresh sponsor snapshot authorizes `OPERATE` for planned quantity `5` and OPEX `20`.

A later SYSTEM spends the full authorized OPEX before physical recovery is known. Only the subsequent WORLD_SIM extraction transition may consult resource remaining, using `actual_extracted = min(planned_quantity, resource.remaining)`. The qualification cases preserve identical sponsor and financier decisions while producing RICH `5`, SPARSE `3`, and NULL `0` actual output. Resource depletion and offworld inventory increase reconcile exactly to actual output. Extraction creates no revenue.

The NULL false-positive case therefore spends the same `20` operating cost as RICH, yet recovers zero material. Project status remains `OPERATING`; Test 008A does not automatically infer shutdown from one zero-output cycle.

Test 008A also adds colony stock-flow state, including resource inventory, to persistent decision-epoch fingerprints, so raw inventory edits between epochs are detected as tampering.

Normative records:

- `build5/BUILD5_IMPLEMENTATION_AUTHORIZATION_008_OPERATING_EXTRACTION_TEST008A.md`;
- `build5/BUILD5_VALIDATION_RECORD_008_OPERATING_EXTRACTION_STRUCTURAL.md`.

Test 008A does not close sale/revenue, demand/market clearing, sponsor response to zero/partial output, repeated operating cycles, maintenance/repair, `CLOSED`, surplus distribution/reinvestment, transport/energy economics, empirical mining calibration, settlement, or production forecasting.

The full autonomous-agent engine remains gated. Each additional Agent role or materially expanded policy requires its own governed scope.



---

## Build-Independent World Science Dependency

Empirical celestial/world-science constraints intended for Offworld use are maintained under:

`simulation/offworld_mvp/world_science/`

That package is an independently versioned empirical dependency of this FRD. Numbered implementation builds may pin and consume a governed baseline, but do not own or silently redefine it.

The package preserves the separation required by this FRD between REAL evidence, SCENARIO hidden WORLD truth, REALIZED simulation state, and Agent-visible information. Its SQLite/later relational representations are not substitutes for JPL/NAIF/SPICE navigation authority, do not constitute economic reserve authority, and do not grant Agent knowledge merely by containing a proposition.

The governing discovery document is `world_science/README.md`; authority and epistemic boundaries are defined in `world_science/WORLD_SCIENCE_AUTHORITY_AND_BOUNDARY.md`.
