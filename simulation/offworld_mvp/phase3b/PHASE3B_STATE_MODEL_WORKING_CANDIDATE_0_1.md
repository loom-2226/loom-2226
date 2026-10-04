# Phase 3B State Model — Working Candidate 0.2

**Status:** PHASE 3B OPEN / PRE-CONTRACT / SINGLE-AUTHORITY  
**Purpose:** Define the minimum state ontology required for the Offworld MVP  
**Implementation authority:** NOT YET GRANTED

## 1. Design objective

Phase 3B defines what state exists, which context owns it, who may know it, and which transitions may change it.

The model must support the causal chain:

`Earth reference -> capital bridge -> agent decision -> exploration -> observation -> belief -> project/investment -> extraction -> transport/sale -> settlement -> realized state`

without collapsing evidence, hidden scenario truth, agent knowledge, belief, or realized simulation state.

## 2. Top-level state planes

### 2.1 EARTH_REFERENCE

Immutable business-as-usual / pre-offworld-impact Earth simulation trajectory.

It is not future scientific fact. It is the control/reference trajectory against which off-world-caused effects are measured.

Initial admitted concepts come only through `EARTH_REFERENCE_CONTRACT_CANDIDATE_v0`.

### 2.2 SOLAR_EVIDENCE

Empirical/research holdings about Solar System bodies, including explicit UNKNOWN_AFTER_SEARCH states and bounded evidence scope.

Simulation need may not replace empirical UNKNOWN with invented evidence.

### 2.3 SCENARIO_WORLD

Hidden scenario realization used to instantiate one simulation universe.

It may contain authored or generator-derived hidden quantities such as actual recoverable resource deposits.

Scenario-world truth is not evidence-plane truth and is not automatically available to agents.

### 2.4 AGENT_INFORMATION

Information actually available to a specific agent through initial endowment, public release, contractually available data, or explicit observation/communication channels.

Permission does not imply possession of information.

### 2.5 AGENT_BELIEF

Agent-specific estimates, distributions, hypotheses or decision-relevant expectations derived from that agent's information and declared reasoning/update process.

Belief is not world truth.

### 2.6 REALIZED_STATE

Simulation state created by executed actions and world transitions.

It includes realized Earth deviations, off-world infrastructure, extracted resources, settlements, ownership, accounts and other consequences.

It never rewrites evidence or Earth reference.

## 3. Required context keys

Every state-bearing object must be locatable by the applicable combination of:

- `world_context`: REAL, SCENARIO(id), REALIZED(run_id);
- `perspective`: GOVERNANCE, WORLD_SIM, AGENT(agent_id);
- simulation/run identifier where applicable;
- time/clock;
- location/entity identity;
- lineage/provenance identity.

Root identity is extensible under Phase 2 Erratum 001. Implementations may not encode primitive roots as a closed two-value enum.

## 4. Core entity families

Phase 3B must represent at minimum:

1. **Location**: Earth country/area, celestial body, site or facility.
2. **AgentState**: persistent public, private or later admitted actor state including assets, information references, belief references, capabilities, objectives, decision policy, available actions and persistent history.
3. **Account / Transaction / ClearingAccount**: conserved balances and explicit double-sided transfers, including an MVP external-market clearing boundary where used.
4. **Asset**: owned productive or transport asset.
5. **Project**: proposed/authorized/executing/completed/failed investment activity.
6. **Infrastructure**: realized physical capability at a location.
7. **ResourceState**: explicitly typed in-situ, accessible, technically recoverable, economic-reserve, extracted and remaining quantities with context; these are not interchangeable.
8. **Observation**: agent-accessible measurement/information event.
9. **BeliefState**: agent interpretation derived from admissible information.
10. **TechnologyState**: scenario-available technical possibility and actor-accessible/adopted capability kept distinct.
11. **PopulationState**: Earth reference biological population and realized settlement/population state without conflating synthetic-person concepts.
12. **ColonyState**: transparent stock-flow state containing at minimum population, cash, productive capital, infrastructure, resource inventory, import inventory, production capacity, operating need, external subsidy and a stage computed from realized state.
13. **DecisionRequest / Decision**: bounded choice context and selected action.
14. **Event**: causal transition record.
15. **Parameter**: explicit model/scenario parameter with lineage and authorization status.
16. **RandomState**: keyed deterministic stochastic state isolated from agent information unless observed.\n17. **TransportRelation**: directed location-to-location relation with distinct cost, travel time, energy, loss risk and capacity, potentially dependent on technology and time.\n18. **EarthImpactLedger**: explicit shadow-accounting state for causal deviations from Earth reference, including capital diversion/return, Earth/offworld purchases and population departure/return.

## 5. Earth reference / realized relation

For each admitted Earth concept:

`REFERENCE(t)` remains immutable.

Off-world economic effects create explicit realized consequences. Conceptually:

`Earth_realized(t) = transition(Earth_reference(t), prior_realized_state, causal_events)`.

No implementation may simply overwrite a reference row.

A realized value must be traceable to the reference assertion plus the events/rules that caused divergence.

## 6. Resource-state separation

For a body/resource family the model must distinguish:

- empirical evidence state;
- hidden scenario in-situ quantity;
- hidden physical accessibility;
- economically recoverable quantity under current technology/prices;
- agent observation;
- agent belief;
- realized reserve/project estimate where such a concept is later admitted;
- cumulative extraction;
- remaining realized quantity.

A single field named `resource_amount` is prohibited because humanity has suffered enough from overloaded columns.

## 7. Information firewall

World-side hidden state cannot enter an agent decision except through declared information lineage.

Required path:

`SCENARIO_WORLD -> observation/channel -> AGENT_INFORMATION -> update rule -> AGENT_BELIEF -> decision`.

Before an observation distinguishes NULL, SPARSE and RICH hidden universes, otherwise identical agents with identical information and random keys must make identical decisions.

This is an MVP falsification test.

## 8. Capital and accounting firewall

Earth `INVESTMENT_REAL_PROXY` is not spendable state.

A future coupling object must explicitly transform a reference economic scale into realized actor-accessible financing under an authorized scenario/model rule.

That bridge must create accounting entries identifying source/counterparty and whether the financing displaces Earth-side realized investment.

No money appears because an agent object requested it.

## 9. Project lifecycle

Minimum project states:

`PROPOSED -> EVALUATED -> AUTHORIZED/FUNDED -> COMMITTED -> EXECUTING -> OPERATING -> COMPLETED/FAILED/ABANDONED`.

Transitions require causal events. Capital, material, transport and labor commitments must occur at defined transitions rather than by retroactive balance adjustment.

## 10. Resource lifecycle

Minimum physical flow:

`IN_SITU -> ACCESSIBLE -> RECOVERABLE -> EXTRACTED -> INVENTORY -> TRANSPORTED -> SOLD/CONSUMED/INSTALLED`.

Not every stage implies epistemic knowledge by an agent.

Physical state and accounting/ownership state remain separate but linked by events.

## 11. Population and settlement

Earth biological population enters only through the Earth reference interface.

Off-world population movement must conserve persons unless explicit birth/death/creation concepts are later modeled.

Settlement/colony state is derived from realized conditions such as population, habitation, life support, productive assets, logistics and persistence criteria. Stage labels must not themselves cause capability.

## 12. Technology

The technology timeline defines scenario possibility/frontier.

The state model must distinguish:

- technology exists/is possible in scenario;
- actor knows about it;
- actor has access/license/capability;
- actor has adopted/deployed it;
- realized infrastructure embodies it.

Existence does not imply universal adoption.

## 13. Event and causal ledger

Every state mutation in REALIZED(run) requires an event containing at minimum:

- event_id;
- run_id;
- simulation time;
- actor/process;
- action/transition type;
- input state references;
- rule/model version;
- parameter references;
- random-key reference if stochastic;
- outputs/state mutations;
- accounting entries where relevant;
- provenance/lineage.

A result must be explainable through stable lineage:

`Result -> Event(s) -> Decision/Process -> Inputs + Rules -> Sources/Assumptions`.

## 14. Determinism and stochasticity

Randomness is keyed and replayable.

A stochastic draw is world-side state unless and until its result becomes observable through a declared channel.

Same pinned inputs, scenario, parameters and random keys must reproduce the same realized trajectory.


## 14A. MVP abstractions and deferred subsystem stubs

The MVP may simplify a subsystem when full fidelity is unnecessary to test the causal architecture. Simplification must preserve the subsystem's semantic role and interface.

Three categories remain distinct:

1. **Scenario stipulation**: authored truth inside a named SCENARIO(id), such as the hidden quantity of a planted resource deposit. This is not an MVP abstraction and not REAL evidence.
2. **MVP abstraction**: a deliberately simplified but functional representation behind a stable interface, such as simplified transport cost/time/capacity.
3. **Deferred subsystem stub**: an explicit boundary standing in for a subsystem not yet modeled, such as an external Earth market clearing account.

There is no generic PLACEHOLDER epistemic mode.

A value that is merely unknown may not be filled for convenience. It remains UNKNOWN/BLOCKED unless an explicit scenario stipulation or authorized model/abstraction creates a distinct dependent state.

Every MVP abstraction or stub must be registered with:

- abstraction_id;
- subsystem;
- category;
- temporary representation;
- interface/consumers;
- preserved invariants;
- explicit non-claims;
- parameter and authorization lineage;
- replacement/revisit trigger;
- intended future subsystem where known.

Initial expected register entries include `MVP_TRANSPORT_v0`, `EARTH_MARKET_v0`, `MVP_COLONY_OPERATIONS_v0`, `MVP_OBSERVATION_MODEL_v0`, and `MVP_PROJECT_COST_v0`. These names reserve conceptual roles only; their numerical contents are not authorized by this document.

Guiding rule: **simplify the subsystem, not the semantics**.

## 15. Minimum MVP conservation invariants

Phase 3B shall design for at least:

1. Earth reference immutability.
2. No hidden-world information leakage.
3. No empirical UNKNOWN converted to scenario fact.
4. No missing value converted to zero.
5. Money/accounting conservation under the declared accounting model.
6. Resource mass conservation.
7. Population conservation subject to explicit demographic events.
8. Ownership conservation/transfer traceability.
9. Extracted quantity cannot exceed realized recoverable quantity.
10. Installed/consumed material must come from inventory/transfer.
11. Project expenditure requires funding.
12. Technology use requires accessible/adopted capability.
13. Every realized mutation has a causal event.
14. Every stochastic outcome is replayable.
15. Reference and realized state remain separately queryable.

## 16. First vertical-slice state fixture

The first complete fixture should contain:

- one deliberately selected participating Earth economy;
- one public actor;
- one private actor;
- one celestial body;
- one resource family;
- one Earth reference economic state;
- one hidden scenario resource realization;
- one prospecting action;
- one observation;
- two potentially different agent beliefs;
- one investment/project decision;
- one extraction operation;
- one transport/sale event;
- one off-world settlement/population state;
- one Earth-side realized accounting consequence.

The fixture must trace:

- one unit of money/accounting value;
- one person;
- one unit of resource;
- one observation;
- one belief update;
- one decision;
- one causal chain from reference to realized state.

## 16A. FRD traceability requirement

Before Phase 3B closes, every normative MVP requirement in `OFFWORLD_MVP_GUIDING_FRD.md` must map to an explicit state object, transition rule, invariant, registered abstraction/stub, or declared non-state requirement. No FRD requirement may disappear merely because the MVP implementation is simplified.

## 17. Immediate Phase 3B work packages

**3B.1 Context and identity model**  
Freeze IDs, contexts, perspectives, clocks and reference identities.

**3B.2 State object schemas**  
Define fields and invariants for the core entity families.

**3B.3 Transition/event model**  
Define legal mutations and causal ledger.

**3B.4 Conservation model**  
Define accounting, resource, population and ownership invariants.

**3B.5 Information/belief model**  
Define observation channels, admissibility and agent knowledge boundaries.

**3B.6 Vertical-slice encoding**  
Encode the one-economy/one-body fixture without yet building the full engine. The economy identity remains UNSELECTED until fixture selection is a deliberate, documented act; no legacy CIVPROP default actor may fill it implicitly.

## 18. Open decisions

Phase 3B has not yet decided:

- exact financial/accounting representation;
- accessible-capital bridge semantics;
- exact resource quantity representation;
- colony-stage thresholds;
- observation noise models;
- agent belief representation;
- decision cadence;
- time-step granularity;
- project failure model;
- price formation beyond the MVP's exogenous-price assumption.

These are design decisions, not invitations for implementation to invent convenient defaults.

## 19. Phase 3B entry condition

Phase 3B is now OPEN.

Design may proceed under PRE-CONTRACT / SINGLE-AUTHORITY. No implementation may claim Authority Contract v1 governed/qualified status, and no production simulation implementation authority is granted by this document.


## 19. Legacy actor-default firewall

Historical CIVPROP experiments used `AUS` as a bounded test actor because Australia-specific lunar mission/access evidence was available. That historical fixture is archaeology only.

For this State Model:

- no country is the default participating economy;
- `AUS`, Australia, Roo-ver, Fleet Space, SPIDER, and other legacy actor-specific fixtures confer no selection priority;
- the MVP economy identity is `UNSELECTED` until an explicit fixture-selection act records the rationale;
- architecture, schemas, transitions, accounting, abstractions and tests must be country-neutral;
- selecting a country for a future fixture does not promote country-specific legacy CIVPROP assumptions, budgets, capabilities, access rights or mission evidence;
- old CIVPROP components may be reused only component-by-component under the FRD archaeology rule.

This firewall prevents a historical reference experiment from becoming an accidental architectural default.
