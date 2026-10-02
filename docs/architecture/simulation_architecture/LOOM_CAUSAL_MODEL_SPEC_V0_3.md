# LOOM CIVPROP Causal Model Specification V0.3

**RESEARCH MODEL SPEC / NON-CANON / NON-QUALIFICATION / NOT RUNTIME AUTHORITY**

## Purpose

Define the executable causal boundaries of CAUSAL_WORLD_V0_3 before adaptive actor behavior is introduced. This document describes code and governed authority; it does not create authority.

## Core execution model

Time is owned by causal_conductor_v0_3.py. The conductor processes typed events in deterministic order. causal_world_v0_3.py owns world integration and invokes qualified domain lanes. Hybrid is reference/regression machinery and must not execute in the production causal path.

The current annual world-accounting boundary remains for physical/accounting domains that are annual authorities. Actors will not receive an annual heartbeat. Actor work is event-driven through actor_activation_v0_3.py.

## Authority hierarchy and epistemic rules

- PostgreSQL validated snapshots are governed external/runtime authority only for fields their contracts actually own.
- Earth validated snapshot: earth-v0-1-9934d0ac-20260925.
- Timeline validated snapshot: timeline-v0-1-0232bf23494f-20260925.
- Timeline dates are consideration/history anchors, not automatic technology, capability, access, service or adoption.
- Candidate actor identity is not actor authority.
- Candidate relationship is not ownership, budget, legal, information-flow, capability or transaction authority until separately qualified for that use.
- UNKNOWN is preserved. It is not zero and is not permission to synthesize a plausible value.
- Earth macro capital/investment is not named-actor spendable budget.
- Earth sector capital/investment may constrain or contextualize sector capacity/opportunity only through an explicit governed derivation.
- No new external actor-capital dataset is required or authorized by this specification.

## State ownership

| State | Owner / source | Runtime treatment |
|---|---|---|
| Earth biological population | validated Earth authority | external governed boundary |
| Earth economic/sector/asset state | validated Earth authority | available for causal derivation; not named-actor budget |
| Solar object/geometry state | governed Solar/SPICE contracts | physical authority |
| Timeline milestones | validated Timeline authority | event/context input only |
| Location physical state | causal world/domain lanes | mutable causal state |
| Resource/power/traffic/production | qualified domain lanes | append-only provenance plus current-state indexes |
| Facilities/projects | causal transaction/project path | consequential physical/economic state |
| Actor identity/category | NON_CANON candidate seed until promoted | registry/discovery only |
| Actor activation | adaptive actor runtime | relevance/execution state, not substantive authority |
| Actor budget/capability/access | dedicated governed authority/derived causal state | UNKNOWN until earned |

## Event and actor activation contract

world event -> typed relevance trigger -> category candidates -> RELEVANT -> governed promotion -> role-specific action -> transaction/consequence -> demotion

Activation levels are DORMANT_CANDIDATE, RELEVANT, ACTIVE_LIGHT, and ACTIVE_TRANSACTIONAL.

Relevance grants no action authority. ACTIVE_TRANSACTIONAL is necessary but not sufficient for consequential action: role adapters must also prove the required budget/capability/access/legal/service facts.

No global 233-actor annual heartbeat is permitted.

## Current-state indexing

Historical ledgers remain append-only provenance. current_state_index_v0_3.py incrementally maintains current facility and physical-state views so domain and future actor lanes do not repeatedly scan complete history.

Indexes are derived caches, never independent authority. Deleting and rebuilding an index from the authoritative ledger must not change causal results.

## Physical/economic feedback

Current chain:

governed world state -> demand/constraint observation -> pressure -> economic opportunity

Investment threshold authority remains absent in Step 7.7, so pressure does not independently create investment.

Future actor chain:

opportunity -> relevant institutional neighborhood -> qualified role decisions -> transaction -> project -> facility/service -> production/transport -> changed world state

No stage may infer a missing downstream authority merely because an upstream condition exists.

## PostgreSQL reuse rule for Step 8

Before introducing any new actor data source, implementation must test in order:

1. Does a validated PostgreSQL snapshot already contain the required variable?
2. Can the variable be derived from governed PostgreSQL/current causal state without allocating aggregate state to a named actor?
3. Can it be produced endogenously by an already qualified transaction/event?
4. If not, preserve UNKNOWN and block the consequential action.

This applies especially to capital, investment, labor, industrial capacity, demand and technology context.

## Determinism and V&V

- Seeded deterministic replay is required before promotion.
- Step 7.7 post-purge/pre-233 control is the actor-expansion ablation baseline.
- Expansion OFF must preserve Step 7.7 causal semantics.
- Loading dormant candidates must not change physical history.
- Current-state index enabled/disabled paths must be semantically equivalent.
- Category adapters are qualified by hostile vertical slice before full-roster execution.
- Consequential actions require causal ancestry/provenance.

## Explicit non-goals before Step 8

- no invented actor budgets;
- no blanket activation of 233 actors;
- no conversion of Earth macro capital into named-actor cash;
- no calendar-date technology unlock;
- no relation-edge authority by assertion;
- no LLM as simulation kernel;
- no new external capital/economic dataset while validated PostgreSQL/current causal state can supply the required aggregate fact or causal derivation.
