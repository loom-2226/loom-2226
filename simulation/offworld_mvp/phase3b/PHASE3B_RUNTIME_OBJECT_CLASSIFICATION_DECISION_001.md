# Phase 3B Runtime Object Classification Decision 001

**Status:** ACCEPTED DESIGN DECISION / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Scope:** Offworld MVP Phase 3B runtime ontology
**Implementation effect:** State-kernel/schema classification is authorized. This does not open the autonomous-agent-engine gate.

## 1. Decision

LOOM shall not model every consequential object or process as an autonomous agent.

Phase 3B distinguishes four runtime object classes:

1. SYSTEM
2. AGGREGATE
3. AGENT
4. ENTITY_ASSET

The classification describes causal role and permitted behavior. It is not an epistemic mode, authority class, storage type, or claim of real-world ontology.

## 2. SYSTEM

A SYSTEM is a mechanism/process that applies declared rules to state and may produce transitions, prices, flows, constraints or derived values.

A SYSTEM has no beliefs, intentions or objectives; does not choose through an Agent decision policy; may be deterministic or keyed-stochastic; may operate on many entities, aggregates or agents; and must obey event, lineage, accounting and conservation rules.

Candidate examples include market clearing, transport-network mechanics, physical production, accounting/clearing, demographic propagation and resource-depletion mechanics.

EARTH_MARKET_v0 remains a non-agent boundary/system abstraction.

## 3. AGGREGATE

An AGGREGATE represents many actors/items statistically or behaviorally without assigning each member an autonomous identity.

It has explicit aggregation scope; may evolve under deterministic or stochastic behavioral rules; does not possess a singular belief/objective/decision policy unless separately promoted to an Agent; and must reconcile with any entities split out of it.

Aggregation is a resolution choice, not evidence that members lack real agency.

## 4. AGENT

An AGENT is a persistent decision-making modeled entity for which bounded choice under information materially affects the simulated trajectory.

An AGENT may carry identity, location/scope, accounts/assets, information, beliefs/internal state, capabilities, objectives, decision policy, available actions and persistent history.

Only an AGENT may execute the Agent decision sequence:

DecisionRequest -> Decision -> ActionRequest.

An AGENT cannot mutate world state. The kernel validates its ActionRequest and performs any admitted WorldTransition.

Agent status must be justified by decision significance or required causal resolution. It is not the default representation for every person, firm, agency or operational process.

## 5. ENTITY_ASSET

ENTITY_ASSET is non-decision-making persistent state with identity.

It may be owned, located, transferred, depleted, constructed, damaged, commissioned or retired, but it has no beliefs/objectives/decision policy.

Examples include projects, facilities, vehicles, infrastructure, resource deposits/sites and productive/knowledge assets. Existing domain-specific schemas remain authoritative for their semantics; ENTITY_ASSET is a runtime classification, not a replacement for them.

## 6. Agency firewall

The runtime must not infer autonomy from having an identifier, owning or holding state, being economically important, being a counterparty, causing a transition through a rule, appearing in the event ledger, possessing a complex model, or historical CIVPROP actor labels.

Systems and aggregates may cause modeled outcomes through declared rules without becoming Agents.

## 7. Resolution transitions

Runtime resolution may change, but not silently.

Permitted conceptual changes include AGGREGATE -> AGENT when a consequential member/institution is exposed as an explicit decision maker; AGENT -> AGGREGATE only under an explicit reconciliation rule; and SYSTEM replacement/refinement under a versioned semantic interface.

A resolution transition requires an explicit event/model-version boundary and reconciliation. It must not create or destroy money, ownership, population, resource quantity, information history or other conserved state.

ENTITY_ASSET -> AGENT is allowed only if the modeled object actually acquires an admitted decision-making role, not because implementation convenience suggests it.

## 8. Promotion criterion

Creating an explicit AGENT is warranted when at least one is true:

1. choices create material branching not adequately represented by an aggregate/system rule;
2. information/beliefs differ materially from peers and affect decisions;
3. assets/market share/control make individual decisions causally significant;
4. governance/scenario requirements require decisions to be separately inspectable;
5. an experiment tests heterogeneity/strategic interaction requiring explicit agency.

Computational novelty alone is not sufficient.

## 9. MVP classification

For the present Offworld MVP:

- kernel/accounting/conservation mechanics: SYSTEM;
- EARTH_MARKET_v0: SYSTEM / deferred boundary abstraction, never an Agent;
- transport mechanics when implemented: SYSTEM;
- physical extraction/production mechanics: SYSTEM, while an operator decision to initiate, expand or abandon may belong to an AGENT;
- broad households/workers/consumers/minor firms when needed: AGGREGATE unless explicitly promoted;
- PUB, SPN, FIN and LOCAL roles: AGENT types, with concrete runtime instances as AGENT entities;
- projects, WIP, knowledge/productive assets, deposits and infrastructure: ENTITY_ASSET or their more specific non-agent schemas;
- ColonyState: non-agent realized stock-flow state. A future settlement authority would be a separate AGENT.

## 10. Relationship to existing Phase 3B design

This decision refines the phrase core entity families in the State Model. It does not erase or rename existing domain schemas.

The existing rule that Agents do not mutate world state remains unchanged.

The transition model allowed_actor/process distinction is now explicit: actor means admitted AGENT where a decision is required; process means SYSTEM/AGGREGATE mechanism where no autonomous decision is represented.

The information firewall remains specific to AGENT information/belief/decision paths. SYSTEM hidden-world access remains limited to its declared world-side rule and may not leak hidden state into an Agent except through an admitted observation/information channel.

## 11. Implementation boundary

Under Phase 3B Implementation Authorization 001, code may add runtime object-class identifiers, schema validation preventing non-Agents from carrying Agent-only decision state, tests that non-Agents cannot submit Agent decisions, and classification metadata on deterministic fixtures.

This is state-kernel/schema work. It does not authorize autonomous decision policies, runtime LLM authority, or the full agent engine.

## 12. Required tests before autonomous-agent authorization

At minimum:

1. SYSTEM cannot possess Agent belief/objective/policy state through the common runtime envelope;
2. AGGREGATE cannot submit an Agent DecisionRequest without explicit promotion;
3. ENTITY_ASSET cannot submit an Agent DecisionRequest;
4. AGENT can submit an ActionRequest but cannot directly mutate world state;
5. aggregate-to-agent split reconciles conserved state in a deterministic fixture;
6. re-aggregation, if implemented, reconciles the same;
7. EARTH_MARKET_v0 remains non-agent;
8. changing runtime resolution is represented in lineage/event history rather than silent type mutation.

## 13. Non-claims

This decision does not determine which real-world institutions become explicit Agents, how many Agents are appropriate, autonomous policy architecture, LLM use, individual-human simulation, exact promotion thresholds, or permanent classification of every future subsystem.

**Guiding rule:** use autonomy where choice matters; use systems and aggregates where rules and flows are the causal object.
