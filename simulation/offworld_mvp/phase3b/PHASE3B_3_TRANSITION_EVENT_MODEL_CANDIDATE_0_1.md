# Phase 3B.3 — Transition and Event Model Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN CANDIDATE

## 1. Mutation rule

Agents do not mutate world state.

Required sequence:

`DecisionRequest -> Decision -> ActionRequest -> Validation -> WorldTransition -> Event -> Mutations`.

Validation may return BLOCKED/FAILED with an inspectable event and no state mutation.

## 2. Transition authority

A transition declares:

`transition_type, allowed_actor/process, required_context, preconditions, consumed state, produced/mutated state, accounting effects, conservation checks, information effects, model/rule version, parameters, abstraction dependencies`.

No generic update-state transition is admitted.

## 3. Minimum transition families

### OBSERVE_REMOTE / PROSPECT_SURFACE
Consumes capability, funding where required, target and observation model. Produces Observation and AgentInformation. Does not change hidden deposit quantity.

### UPDATE_BELIEF
Consumes prior BeliefState plus admissible AgentInformation and update rule. Produces new BeliefState. Does not change hidden truth.

### FUND_PROJECT
Consumes accessible financing/account balances under the capital bridge and funding rule. Produces transactions and funded ProjectState. Does not imply development success.

### COMMIT_PROJECT / START_DEVELOPMENT
Consumes funded project, capabilities, technology and required resources. Produces commitments, spending transactions and project lifecycle mutation.

### CONSTRUCT
Consumes project funding, materials/inventory, transport/logistics and capability. Produces infrastructure/assets only if transition succeeds.

### EXTRACT
Consumes operating project/infrastructure/capability and realized recoverable resource. Decreases remaining resource and increases owned inventory. Cannot exceed available recoverable quantity/capacity.

### TRANSPORT
Consumes inventory, route/TransportRelation, capacity and funding/energy treatment. Changes inventory location/quantity subject to modeled loss and produces accounting/events.

### SELL
Consumes seller inventory and market/buyer demand. Produces inventory transfer/reduction and balanced transaction. Price alone cannot create revenue.

### MIGRATE
Consumes origin population, transport/capacity and applicable funding/support. Decreases origin realized population and increases destination population subject to explicit modeled losses. Reference population is not mutated.

### SUBSIDIZE / SUPPORT_COLONY
Transfers funds/resources from an identified source to colony accounts/inventory. No unilateral subsidy balance creation.

### RETURN_CAPITAL
Transfers realized offworld financial value to an Earth-side account/clearing boundary and records EarthImpactLedger consequence.

### ABANDON / FAIL / CLOSE_PROJECT
Changes lifecycle state and realizes explicit accounting/asset consequences. It does not erase historical spending.

## 4. Project lifecycle mapping

Candidate legal progression:

`PROPOSED -> EVALUATED -> AUTHORIZED/FUNDED -> COMMITTED -> EXECUTING -> OPERATING -> COMPLETED | FAILED | ABANDONED | CLOSED`.

Not every project must traverse every success state. Failure/abandonment transitions require reason/event lineage.

## 5. Information effects versus physical effects

Observation transitions change information state.

Belief transitions change agent belief state.

Extraction/construction/transport/migration change realized physical state.

Financial transitions change realized accounting state.

No transition may use a change in one plane as an implicit mutation of another.

## 6. Event atomicity

A successful world transition emits one causal event envelope containing all logically coupled mutations and transaction references. If the storage layer later requires multiple rows, they share an atomic transition/event identity.

A failed validation may emit a blocked/failed event but no partial mutation unless the transition explicitly models a cost incurred before failure.

## 7. Precondition behavior

Missing required state does not default.

- empirical missing/UNKNOWN follows epistemic rules;
- unavailable capability/funding causes BLOCKED;
- stochastic operational failure may produce FAILED after action commitment;
- conflict/admissibility follows the Authority model.

BLOCKED and FAILED are not synonyms.

## 8. Earth consequence rule

Offworld actions never mutate Earth reference.

Any Earth-side consequence writes realized accounting/population state plus EarthImpactLedger entries tied to the causing event.

## 9. Abstraction boundary

A transition may call a registered MVP abstraction such as transport, project cost, observation or market clearing.

The event records the abstraction/version, model and parameters used. Replacement of the abstraction must not silently alter the transition's semantic meaning.

## 10. Deterministic replay

Transition randomness uses keyed streams. Reordering unrelated transitions must not change unrelated stochastic outcomes when their causal inputs and keys are unchanged.

## 11. Required negative tests

The eventual executable model must reject at least:

- direct agent mutation of resource quantity;
- extraction without recoverable resource;
- spending without funding;
- sale without buyer/clearing counter-entry;
- migration without origin population;
- observation reading hidden truth outside its observation model;
- technology use without access/adoption;
- mutation of Earth reference;
- use of an unregistered convenience placeholder;
- partial mutation after a blocked transition.
