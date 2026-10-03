# LOOM Offworld Simulation
## Guiding Functional Requirements Document
### MVP: Capital, Exploration, Resources, Agents, and Settlement

**Status:** PRELIMINARY FRD / PRE-CONTRACT  
**Authority status:** PRE-CONTRACT / SINGLE-AUTHORITY  
**Canonical status:** NON-CANON  
**Implementation authority:** NOT YET GRANTED  
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

All MVP institutional actors shall implement a common conceptual contract:

```
agent_id
agent_type
scope/location
assets
information
beliefs/internal_state
capabilities
objectives
decision_policy
available_actions
persistent_history
```

Interaction sequence:

`World -> Observation -> Agent Information -> Belief -> Available Actions -> Decision -> Action Request -> World Transition`

An agent submits an action request. It shall not directly mutate world state.

## 14. MVP Agents

### 14.1 Public Agent

The public agent represents an authorized public offworld program. It need not maximize financial return.

It may fund or conduct exploration, publish observations, establish infrastructure, establish/support settlement, move population, and subsidize a dependent settlement.

It remains constrained by available budget, capability, technology, and action rules.

### 14.2 Private Agent

The private agent seeks financial return. Its decision policy shall consider at minimum available capital, agent belief, expected revenue, expected cost, risk, time horizon, hurdle rate, maximum capital at risk, and abandonment criteria.

Conceptually:

`Invest iff E[Return | B_i(t)] > H_i`

subject to available capital and capability.

The private agent shall calculate expected value from **its belief state**, not hidden world truth.

## 15. Agent Information Firewall

Agents shall never directly query hidden scenario truth.

World-side parameters and agent-side informational parameters shall remain distinct. A parameter used on both sides must either:

1. exist as a separately declared agent-side parameter with independent lineage; or
2. be explicitly stipulated as information known to the agent.

This applies to priors, detection rates, false-positive rates, likelihood functions, noise models, cost distributions, and risk estimates.

World seeds and world random streams shall never constitute agent information. Equality between a world parameter and an agent-side parameter is itself an explicit scenario assumption where material.

## 16. Exploration and Observation

The MVP shall implement at least:

- **Remote observation:** noisy indication concerning target resource presence.
- **Surface prospecting:** higher-quality information and potentially an estimate of grade or quantity within modeled limits.

Development may reveal additional physical state required for operation.

> **Exploration changes information, not physical reality.**

> **Extraction changes realized physical state.**

## 17. Beliefs

Each agent shall maintain an internal belief state concerning uncertain target properties. The MVP may use a simple Bayesian model.

Exact belief models and parameters are model/scenario-governed inputs requiring authorization.

A proposition that an agent believes a resource exists with probability 0.72 does **not** assert that probability on the REAL evidence plane or as hidden scenario truth. Belief is agent state.

## 18. Capital Origin

All MVP offworld capital shall originate from the participating Earth economy.

For declared reference investment flow:

`P_c(t) = f I_c(t)`

where `f` is an authorized scenario/model parameter.

Capital allocation shall create an equal shadow debit against Earth-realized accounting. No capital may appear merely because an agent wants to undertake a project.

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

## 21. MVP Project Economics

Detailed mining engineering is outside MVP scope.

A simplified model may use:

`Revenue = q P`

`Cost = C_exploration + C_construction + C_extraction + C_transport + C_energy`

subject to appropriate difficulty/technology multipliers.

These relationships are model scaffolding, not future empirical claims. The transformation itself is a dependency with version and standing.

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
- extraction changes realized resource stock;
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

The MVP shall not preclude eventual progression:

`Macroeconomic Node <-> Institution <-> Population Aggregate <-> Persistent Agent`

or:

`Aggregate -> Cohort -> Persistent Individual -> High Fidelity`

The generic Agent abstraction shall not assume biological humanity. Future specializations may include Institution, Human, Synthetic, Household, Firm, and Government.

Promotion from aggregate population into explicit agents shall conserve corresponding macro quantities.

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

## Governance note

This FRD is a build-guiding candidate on a branch created from the closed Phase 2 governance branch. It does not reopen Phase 2, release Contract v1, qualify inputs, or grant implementation authority. Phase 3 state-model work must consume the consolidated Phase 2 normative model and preserve its carried liens.
