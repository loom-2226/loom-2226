# Phase 3B.2 — State Object Schemas Candidate 0.1

**Status:** PRE-CONTRACT / SINGLE-AUTHORITY / DESIGN CANDIDATE
**Purpose:** Semantic schemas, not database DDL.

## 1. Common state envelope

Every state object carries, where applicable:

`state_id, entity_id, world_context, perspective, effective_time, lineage_refs, model_or_rule_version, parameter_refs, abstraction_refs, value_state, uncertainty_state`.

Objects add domain-specific fields below. Fields marked required are semantic requirements; physical serialization is deferred.

## 2. AgentState

Required:

`actor_id, actor_type, location/scope, asset_refs, account_refs, information_refs, belief_refs, capability_refs, objective_ref, decision_policy_ref, available_action_types, persistent_history_ref, status`.

AgentState cannot contain hidden WORLD_SIM truth unless that truth has entered the agent perspective through valid information lineage.

## 3. Account

Required:

`account_id, owner_entity_id, account_type, unit_basis, balance, status`.

Account balance is realized accounting state, not Earth reference proxy state.

### Transaction

`transaction_id, time, debit_account, credit_account, amount, unit_basis, purpose, event_id, counterparty_refs`.

No unilateral cash creation through a transaction type unless an explicitly modeled source/issuance mechanism is later admitted.

## 4. EarthImpactState

Required dimensions:

`area_id, time, reference_assertion_refs, capital_diverted, capital_returned, earth_purchases_from_offworld, offworld_purchases_from_earth, population_departed, population_returned, causal_event_refs`.

This is shadow/delta accounting. It does not overwrite Earth reference.

## 5. ResourceState

Resource quantities are typed, not aliases:

`resource_family_id, location/site_id, in_situ_quantity, accessible_quantity, technically_recoverable_quantity, economic_reserve_quantity, cumulative_extracted_quantity, remaining_quantity, quantity_unit, grade/composition_state_if_used, physical_access_ref, technology_ref, economic_condition_refs`.

Not every field exists in every context. REAL may be UNKNOWN while SCENARIO contains hidden in-situ state and REALIZED contains extraction state.

Reserve is economic/model-derived and may change without physical deposit quantity changing.

## 6. TransportRelation

Required:

`transport_relation_id, origin_location_id, destination_location_id, effective_time, technology_ref, cost, travel_time, energy, loss_risk, capacity, unit_basis_by_dimension, model_ref, abstraction_ref`.

Cost/time/energy/risk/capacity remain separate.

For MVP, `MVP_TRANSPORT_v0` may populate these fields once its numerical model is separately authorized.

## 7. ProjectState

Required:

`project_id, owner/sponsor_refs, target_location, resource_family_if_any, lifecycle_state, committed_capital, spent_capital, asset_refs, infrastructure_refs, capability_requirements, technology_requirements, start_time, decision/event_refs, failure/abandonment_reason_if_any`.

Lifecycle values are governed by the transition model, not freely edited labels.

## 8. AssetState

`asset_id, owner_id, location_id, asset_type, capability_refs, capacity, condition/status, acquisition_event, disposition_event_if_any`.

Ownership changes require explicit transfer/event lineage.

## 9. InfrastructureState

`infrastructure_id, owner/operator_refs, location_id, infrastructure_type, capacity, technology_embodied_refs, operating_requirements, status, construction/project_refs`.

Infrastructure capability derives from realized state, not project intent.

## 10. TechnologyState

Separate dimensions:

`technology_id, scenario_availability_state, agent_knowledge_state, agent_access_state, adoption_state, deployment_refs, capability_effects`.

The same technology can exist in scenario while an actor lacks knowledge/access/adoption.

## 11. Observation

`observation_id, time, producer/channel, subject_ref, recipient_perspective, observed_variables, observed_values, uncertainty/noise_metadata, world_process_ref, random_key_ref_if_any, information_release_state, lineage`.

Observation asserts what was observed, not hidden truth.

## 12. AgentInformationState

`information_item_id, actor_id, acquired_time, source/observation_ref, proposition/content_ref, admissibility/status, uncertainty_metadata, disclosure_scope`.

## 13. BeliefState

`belief_state_id, actor_id, subject/proposition_ref, effective_time, belief_representation, belief_value_or_parameters, prior_belief_ref, information_inputs, update_rule_ref, parameter_refs`.

Belief is perspective-isolated agent state.

## 14. PopulationState

`population_state_id, population_type, location_id, count, time, source/reference_refs, migration_event_refs, demographic_event_refs`.

MVP Earth reference input uses biological population. Offworld migration must reconcile departures and arrivals.

## 15. ColonyState

Minimum transparent stock-flow state:

`colony_state_id, location_id, population, cash/account_refs, productive_capital/asset_refs, infrastructure_refs, resource_inventory, import_inventory, production_capacity, operating_need, external_subsidy, stage, stage_rule_ref, project/event_refs`.

Stage is computed from realized stocks/flows and explicit thresholds. It is not causal by itself.

## 16. DecisionRequest

`request_id, actor_id, time, available_action_set, information_snapshot_refs, belief_snapshot_refs, account/asset/capability_refs, objective_ref, policy_ref, constraints, decision_context`.

### Decision

`decision_id, request_id, actor_id, selected_action, rationale/decision_metrics, policy_version, belief/input_refs, action_request_ref, time`.

A Decision cannot mutate world state.

## 17. Event

`event_id, run_id, time, actor_or_process, action/transition_type, prior_state_refs, input_refs, rule/model_version, parameter_refs, abstraction_refs, random_key_ref, result/status, mutation_refs, transaction_refs, provenance/lineage`.

Blocked/failed events may have no mutations but remain causally inspectable.

## 18. Parameter

`parameter_id, name, semantic_role, value/value_state, unit_basis, world_context, perspective_if_applicable, epistemic_mode, authorization/lineage_refs, uncertainty_state, effective_scope/time, version`.

World-side and agent-side informational parameters remain separate objects unless explicitly stipulated as shared information.

## 19. RandomState / RandomKey

`master_seed_ref, run_id, process_id, time_key, actor_id_if_applicable, body/location_id_if_applicable, resource_id_if_applicable, draw_key, distribution/model_ref`.

Execution order is not a random-stream identity.

## 20. InventoryState

`inventory_id, owner_id, location_id, material/resource_id, quantity, unit, acquisition/source_event_refs, reserved_quantity, status`.

Extraction creates inventory only through an explicit event; sale/consumption/installation reduces/transfers it through explicit events.

## 21. MVP abstraction usage

A state object produced by an MVP abstraction records the abstraction ID/version plus its actual model/parameter lineage.

The abstraction register is not permission to populate unspecified numbers.

## 22. Cross-object invariants

- account transfers reconcile;
- resource extraction reconciles with resource state and inventory;
- ownership transfers reconcile;
- migration reconciles population locations;
- project spending reconciles transactions;
- observation/belief lineage never aliases hidden truth;
- realized state references causal events;
- Earth reference assertions are referenced, never mutated;
- scenario truth is immutable per scenario version;
- derived colony stage matches stage rule and underlying state.
