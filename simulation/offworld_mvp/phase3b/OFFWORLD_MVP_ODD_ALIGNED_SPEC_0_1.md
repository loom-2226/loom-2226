# Offworld MVP — ODD-Aligned Executable Model Specification 0.1

**Status:** DESIGN CANDIDATE / PRE-CONTRACT / SINGLE-AUTHORITY
**Basis:** ODD 2020 structure adapted to LOOM governance
**Scope:** Build 5 Offworld MVP with bounded autonomous institutional policies and governed decision epochs

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

Build 5 decision-epoch mode chains multiple such sealed runs over one persistent kernel state. Each epoch resets only scheduler-plan state, freezes new DecisionSnapshot references from the verified post-epoch world state, and records chain id, epoch id/ordinal, parent result fingerprint, plan fingerprint, initial/final fingerprints, execution fingerprint and result fingerprint. Successful epoch completion is the only path that releases the seal for preparation of the next epoch. Once an epoch chain starts, governed world mutators remain blocked between epochs, and persistent-state fingerprints detect raw state tampering both between epochs and after epoch-open before seal.

DECISION_WINDOW policy execution is separated from kernel-bearing system handlers. Policy code receives only a frozen/slotted `PolicyContext` containing a deeply copied `DecisionSnapshot`, pinned snapshot reference and deterministic decision key. Hidden scenario resources, world/run identity, scheduler and seed state are not part of that interface.

## 4. Design concepts

### Emergence
Settlement, capital stock, ownership distribution, extraction and financing recursion are realized outcomes, not scripted historical milestones.

### Adaptation
General autonomous adaptation remains gated. Build 5 currently contains individually authorized bounded autonomous policies for the private financier and public institutional explorer/publisher. Additional Agent roles or materially expanded policies require separate governance.

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
- governed persistent decision-epoch chaining;
- public observation publication and cross-Agent information transfer;
- aggregate-resolution reconciliation;
- uncertainty/ensemble runner;
- ensemble reporting guardrails that distinguish scenario spread, parameter sensitivity, uncertainty spread and stochastic variability;
- executable A1–A9 accounting/physical identity auditor;
- signed Earth-boundary reconciliation;
- staged multi-year WIP and multi-rate synchronization fixtures.

The A1–A9 property fixture captures state before every scheduler-valid transition and evaluates all nine identities immediately after each transition. Current generative coverage includes disbursement, WIP spend, commissioning, depreciation, extraction, revenue, surplus disposition and commitment lapse.

The multi-rate synchronization fixture combines day-scale mission observations, quarterly finance and annual Earth-system events under one deterministic scheduler.

Transport, technology gating, dynamic economic reserve conversion, mature colony operations, sponsor/operator autonomy and surface prospecting remain incomplete unless separately implemented and validated.

## 8. Reproducibility package

Every executable result intended for comparison must preserve:

- run manifest;
- exact repository and Git commit identity;
- SHA-256 of the executable Python source tree;
- input snapshot id(s);
- parameter-manifest id(s);
- table-manifest id(s), or explicit NO_EXTERNAL_TABLES;
- scheduler version and scheduler-plan fingerprint;
- event ordering and execution/event-results fingerprint;
- initial and terminal-state fingerprints;
- provenance fingerprint;
- final result fingerprint;
- test/validation record;
- known limitations.

## 9. Executable Schema Registry

The ODD state/interface registry below is machine-checked against executable dataclass field names **and field types**, registered enum values, and declared unit semantics. A field addition/removal/rename, type change, enum-value change, or unit-contract change without an ODD update fails the regression suite.

<!-- ODD_SCHEMA_REGISTRY_BEGIN -->
```json
{
  "enums": {
    "AccountKind": [
      "FUNDS",
      "PROJECT_CASH",
      "EARTH_BOUNDARY",
      "SUPPLIER"
    ],
    "ActionKind": [
      "EXPLORE",
      "PUBLISH",
      "REQUEST_FINANCE",
      "FINANCE",
      "DEVELOP",
      "ABANDON",
      "EXTRACT",
      "SELL",
      "MIGRATE",
      "REINVEST"
    ],
    "AgentKind": [
      "PUBLIC",
      "PRIVATE_SPONSOR",
      "PRIVATE_FINANCIER",
      "LOCAL_FINANCIER"
    ],
    "AssetKind": [
      "WIP",
      "EXPLORATION_WIP",
      "KNOWLEDGE",
      "PRODUCTIVE"
    ],
    "AxisKind": [
      "SCENARIO",
      "PARAMETER",
      "UNCERTAINTY",
      "STOCHASTIC_KEY"
    ],
    "ExplorationDecisionOutcome": [
      "AUTHORIZE",
      "DECLINE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "ExplorationReasonCode": [
      "APPROVED_PUBLIC_INFORMATION_MISSION",
      "INSUFFICIENT_BUDGET",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "DEFER_UNSUPPORTED_CHANNEL",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
    ],
    "ExposureAllocationBasis": [
      "EQUAL_MEMBER_PRO_RATA",
      "EXPLICIT_AUTHORIZED_SHARE",
      "EVIDENCE_DERIVED_SHARE"
    ],
    "ExposureSelectionBasis": [
      "VALIDATION_FIXTURE_STABLE_ID",
      "EXPLICIT_AUTHORIZED_ID",
      "EVIDENCE_RULE"
    ],
    "FactState": [
      "KNOWN",
      "UNKNOWN",
      "BLOCKED"
    ],
    "FinancingDecisionOutcome": [
      "APPROVE",
      "REJECT",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "FinancingReasonCode": [
      "SCRIPTED_VALIDATION",
      "APPROVED_POLICY_RULE",
      "REJECTED_RETURN",
      "REJECTED_RISK",
      "BELOW_RETURN",
      "CEILING",
      "CONCENTRATION",
      "DEFER_MORE_INFORMATION",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN",
      "REQUEST_INVALID",
      "INSUFFICIENT_CAPITAL",
      "CAPABILITY_OR_AUTHORITY_BLOCK"
    ],
    "NodeKind": [
      "EARTH",
      "OFFWORLD"
    ],
    "ObservationKnowledgeRelation": [
      "PERFECT_OBSERVATION_MODEL_KNOWLEDGE_ASSUMPTION",
      "INDEPENDENT_AGENT_LIKELIHOOD_MODEL"
    ],
    "OutOfSampleStatus": [
      0,
      1,
      2,
      3,
      4
    ],
    "Phase": [
      10,
      20,
      30,
      40,
      50,
      60,
      70,
      80,
      90,
      100,
      110,
      120,
      130
    ],
    "PolicyParameterStatus": [
      "AUTHORIZED",
      "TEST_ONLY"
    ],
    "PublicationDecisionOutcome": [
      "PUBLISH",
      "WITHHOLD"
    ],
    "PublicationReasonCode": [
      "PUBLISH_PUBLIC_INFORMATION",
      "OBSERVATION_NOT_POSSESSED",
      "OBJECTIVE_OR_CLASS_BLOCK"
    ],
    "RuntimeObjectClass": [
      "SYSTEM",
      "AGGREGATE",
      "AGENT",
      "ENTITY_ASSET"
    ],
    "SponsorProjectDecisionOutcome": [
      "REQUEST_FINANCE",
      "DEVELOP",
      "DEFER",
      "ABANDON",
      "BLOCKED_UNKNOWN"
    ],
    "SponsorProjectReasonCode": [
      "POSITIVE_EVIDENCE_FINANCE_REQUIRED",
      "POSITIVE_EVIDENCE_FUNDED",
      "NO_RELEVANT_INFORMATION",
      "NONPOSITIVE_EVIDENCE",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "PROJECT_STATE_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
    ],
    "SpreadMeaning": [
      "SCENARIO_SPREAD_NOT_PROBABILITY",
      "PARAMETER_SENSITIVITY",
      "UNCERTAINTY_SPREAD",
      "STOCHASTIC_VARIABILITY"
    ],
    "TxPurpose": [
      "DISBURSE",
      "CAPEX",
      "EXPLORATION",
      "OPEX",
      "REVENUE",
      "RETURN_TO_EARTH",
      "LOCAL_RETENTION",
      "LOCAL_REINVESTMENT",
      "OTHER_INVESTMENT",
      "RESERVE"
    ],
    "UnderwritingInputKind": [
      "PRICE",
      "EXPLORATION_CAPEX",
      "DEVELOPMENT_CAPEX",
      "OPERATING_COST",
      "LEAD_TIME"
    ],
    "UnderwritingInputStatus": [
      "AUTHORED_SCENARIO",
      "EVIDENCE_DERIVED",
      "UNKNOWN"
    ],
    "ValidationLevel": [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ],
    "VerificationLevel": [
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ]
  },
  "registry_version": "ODD_SCHEMA_REGISTRY_0_7",
  "types": {
    "Account": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "owner_id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "kind",
        "type": "AccountKind"
      },
      {
        "name": "balance",
        "type": "D"
      }
    ],
    "AgentState": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "kind",
        "type": "AgentKind"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "account_id",
        "type": "str"
      },
      {
        "name": "capabilities",
        "type": "set[str]"
      },
      {
        "name": "objectives",
        "type": "tuple[str, ...]"
      },
      {
        "name": "runtime_class",
        "type": "RuntimeObjectClass"
      },
      {
        "name": "decision_policy",
        "type": "str"
      },
      {
        "name": "information",
        "type": "set[str]"
      },
      {
        "name": "beliefs",
        "type": "Dict[str, D]"
      },
      {
        "name": "history",
        "type": "List[str]"
      },
      {
        "name": "asset_refs",
        "type": "set[str]"
      },
      {
        "name": "resource_holdings",
        "type": "Dict[str, D]"
      },
      {
        "name": "claim_holdings",
        "type": "Dict[str, D]"
      },
      {
        "name": "lineage_refs",
        "type": "List[str]"
      },
      {
        "name": "priors",
        "type": "Dict[str, D]"
      }
    ],
    "AggregateState": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "account_id",
        "type": "str"
      },
      {
        "name": "member_count",
        "type": "int"
      },
      {
        "name": "asset_refs",
        "type": "set[str]"
      },
      {
        "name": "resource_holdings",
        "type": "Dict[str, D]"
      },
      {
        "name": "claim_holdings",
        "type": "Dict[str, D]"
      },
      {
        "name": "history_refs",
        "type": "List[str]"
      },
      {
        "name": "runtime_class",
        "type": "RuntimeObjectClass"
      }
    ],
    "Asset": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "kind",
        "type": "AssetKind"
      },
      {
        "name": "book_value",
        "type": "D"
      },
      {
        "name": "capacity",
        "type": "D"
      }
    ],
    "ColonyState": [
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "population",
        "type": "int"
      },
      {
        "name": "cash",
        "type": "D"
      },
      {
        "name": "productive_capital",
        "type": "D"
      },
      {
        "name": "infrastructure",
        "type": "D"
      },
      {
        "name": "resource_inventory",
        "type": "D"
      },
      {
        "name": "import_inventory",
        "type": "D"
      },
      {
        "name": "production_capacity",
        "type": "D"
      },
      {
        "name": "operating_need",
        "type": "D"
      },
      {
        "name": "external_subsidy",
        "type": "D"
      },
      {
        "name": "stage",
        "type": "str"
      }
    ],
    "Commitment": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "financier_id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "committed",
        "type": "D"
      },
      {
        "name": "disbursed",
        "type": "D"
      },
      {
        "name": "lapsed",
        "type": "D"
      }
    ],
    "CouplingSpec": [
      {
        "name": "process_id",
        "type": "str"
      },
      {
        "name": "version",
        "type": "str"
      },
      {
        "name": "runtime_class",
        "type": "RuntimeObjectClass"
      },
      {
        "name": "owned_state",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "read_set",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "write_set",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "cadence_or_trigger",
        "type": "str"
      },
      {
        "name": "phase",
        "type": "Phase"
      },
      {
        "name": "unit_basis",
        "type": "Tuple[Tuple[str, str], ...]"
      },
      {
        "name": "world_context",
        "type": "str"
      },
      {
        "name": "perspective",
        "type": "str"
      },
      {
        "name": "direction",
        "type": "str"
      },
      {
        "name": "transition_interfaces",
        "type": "Tuple[str, ...]"
      }
    ],
    "DecisionEpochRecord": [
      {
        "name": "chain_id",
        "type": "str"
      },
      {
        "name": "epoch_id",
        "type": "str"
      },
      {
        "name": "ordinal",
        "type": "int"
      },
      {
        "name": "parent_result_fingerprint",
        "type": "str"
      },
      {
        "name": "plan_fingerprint",
        "type": "str"
      },
      {
        "name": "initial_fingerprint",
        "type": "str"
      },
      {
        "name": "final_fingerprint",
        "type": "str"
      },
      {
        "name": "execution_fingerprint",
        "type": "str"
      },
      {
        "name": "result_fingerprint",
        "type": "str"
      }
    ],
    "DecisionSnapshot": [
      {
        "name": "agent_id",
        "type": "str"
      },
      {
        "name": "agent_kind",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "period_key",
        "type": "str"
      },
      {
        "name": "effective_time",
        "type": "str"
      },
      {
        "name": "account_balance",
        "type": "D"
      },
      {
        "name": "capabilities",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "objectives",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "information_refs",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "beliefs",
        "type": "Tuple[Tuple[str, D], ...]"
      },
      {
        "name": "priors",
        "type": "Tuple[Tuple[str, D], ...]"
      },
      {
        "name": "asset_refs",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "resource_holdings",
        "type": "Tuple[Tuple[str, D], ...]"
      },
      {
        "name": "claim_holdings",
        "type": "Tuple[Tuple[str, D], ...]"
      },
      {
        "name": "admitted_facts",
        "type": "Tuple[SnapshotFact, ...]"
      }
    ],
    "EarthImpactLedger": [
      {
        "name": "qualifying_supplied_expenditure",
        "type": "Dict[tuple[str, int], D]"
      },
      {
        "name": "terrestrial_fcf_delta",
        "type": "Dict[tuple[str, int], D]"
      }
    ],
    "EntityAssetRef": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "domain_type",
        "type": "str"
      },
      {
        "name": "state_ref",
        "type": "str"
      },
      {
        "name": "runtime_class",
        "type": "RuntimeObjectClass"
      }
    ],
    "ExplorationDecision": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "request_id",
        "type": "str"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "authorized",
        "type": "bool"
      },
      {
        "name": "authorized_cost",
        "type": "D"
      },
      {
        "name": "channel",
        "type": "str"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "outcome",
        "type": "ExplorationDecisionOutcome"
      },
      {
        "name": "reason_code",
        "type": "ExplorationReasonCode"
      },
      {
        "name": "unknown_input_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "input_snapshot_ref",
        "type": "str"
      },
      {
        "name": "policy_version",
        "type": "str"
      },
      {
        "name": "decision_version",
        "type": "str"
      }
    ],
    "ExplorationRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "channel",
        "type": "str"
      },
      {
        "name": "required_fact_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "currency_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
      }
    ],
    "FinancierPolicyManifest": [
      {
        "name": "manifest_id",
        "type": "str"
      },
      {
        "name": "policy_id",
        "type": "str"
      },
      {
        "name": "semantic_version",
        "type": "str"
      },
      {
        "name": "parameters",
        "type": "Tuple[PolicyParameter, ...]"
      },
      {
        "name": "observation_knowledge_relation",
        "type": "ObservationKnowledgeRelation"
      },
      {
        "name": "world_observation_model_ref",
        "type": "str"
      },
      {
        "name": "world_detection_rate",
        "type": "D | None"
      },
      {
        "name": "world_false_positive_rate",
        "type": "D | None"
      },
      {
        "name": "manifest_status",
        "type": "PolicyParameterStatus"
      }
    ],
    "FinancingDecision": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "request_id",
        "type": "str"
      },
      {
        "name": "financier_id",
        "type": "str"
      },
      {
        "name": "approved",
        "type": "bool"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "instrument",
        "type": "str"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "outcome",
        "type": "FinancingDecisionOutcome | None"
      },
      {
        "name": "reason_code",
        "type": "FinancingReasonCode | None"
      },
      {
        "name": "unknown_input_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "input_snapshot_ref",
        "type": "str"
      },
      {
        "name": "policy_version",
        "type": "str"
      },
      {
        "name": "decision_version",
        "type": "str"
      }
    ],
    "FinancingRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "sponsor_id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "stage",
        "type": "str"
      },
      {
        "name": "disclosed_observation_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "required_underwriting_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "required_belief_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "required_prior_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "currency_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
      }
    ],
    "FixedCapitalFormationEvent": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "asset_id",
        "type": "str"
      },
      {
        "name": "owner_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "financing_origin_nodes",
        "type": "tuple[str, ...]"
      },
      {
        "name": "supplier_node",
        "type": "str"
      },
      {
        "name": "asset_node",
        "type": "str"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "asset_class",
        "type": "str"
      },
      {
        "name": "parent_ids",
        "type": "tuple[str, ...]"
      }
    ],
    "KernelState": [
      {
        "name": "nodes",
        "type": "Dict[str, Node]"
      },
      {
        "name": "accounts",
        "type": "Dict[str, Account]"
      },
      {
        "name": "commitments",
        "type": "Dict[str, Commitment]"
      },
      {
        "name": "projects",
        "type": "Dict[str, Project]"
      },
      {
        "name": "assets",
        "type": "Dict[str, Asset]"
      },
      {
        "name": "transactions",
        "type": "List[Transaction]"
      },
      {
        "name": "fcf_events",
        "type": "List[FixedCapitalFormationEvent]"
      },
      {
        "name": "earth_impact",
        "type": "EarthImpactLedger"
      }
    ],
    "Node": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "kind",
        "type": "NodeKind"
      }
    ],
    "Observation": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "channel",
        "type": "str"
      },
      {
        "name": "signal",
        "type": "str"
      },
      {
        "name": "public",
        "type": "bool"
      }
    ],
    "PolicyContext": [
      {
        "name": "snapshot",
        "type": "DecisionSnapshot"
      },
      {
        "name": "snapshot_ref",
        "type": "str"
      },
      {
        "name": "decision_key",
        "type": "str"
      }
    ],
    "PolicyExecutionResult": [
      {
        "name": "decision",
        "type": "object"
      },
      {
        "name": "policy_version",
        "type": "str"
      },
      {
        "name": "parameter_manifest_hash",
        "type": "str"
      },
      {
        "name": "worker_fingerprint",
        "type": "str"
      },
      {
        "name": "metrics",
        "type": "Tuple[Tuple[str, str], ...]"
      },
      {
        "name": "sandbox_mode",
        "type": "str"
      }
    ],
    "PolicyParameter": [
      {
        "name": "parameter_id",
        "type": "str"
      },
      {
        "name": "semantic_name",
        "type": "str"
      },
      {
        "name": "value",
        "type": "D"
      },
      {
        "name": "unit",
        "type": "str"
      },
      {
        "name": "authorization_ref",
        "type": "str"
      },
      {
        "name": "status",
        "type": "PolicyParameterStatus"
      },
      {
        "name": "sensitivity_low",
        "type": "D"
      },
      {
        "name": "sensitivity_high",
        "type": "D"
      },
      {
        "name": "local_perturbation",
        "type": "D"
      },
      {
        "name": "valid_from_version",
        "type": "str"
      },
      {
        "name": "valid_to_version",
        "type": "str"
      }
    ],
    "PopulationLedger": [
      {
        "name": "earth",
        "type": "int"
      },
      {
        "name": "offworld",
        "type": "Dict[str, int]"
      }
    ],
    "Project": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "cash_account_id",
        "type": "str"
      },
      {
        "name": "owners",
        "type": "Dict[str, D]"
      },
      {
        "name": "status",
        "type": "str"
      }
    ],
    "PublicInformationArtifact": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "publisher_id",
        "type": "str"
      },
      {
        "name": "source_observation_id",
        "type": "str"
      },
      {
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "channel",
        "type": "str"
      },
      {
        "name": "signal",
        "type": "str"
      },
      {
        "name": "audience",
        "type": "str"
      },
      {
        "name": "recipient_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "artifact_version",
        "type": "str"
      }
    ],
    "PublicationDecision": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "request_id",
        "type": "str"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "publish",
        "type": "bool"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "outcome",
        "type": "PublicationDecisionOutcome"
      },
      {
        "name": "reason_code",
        "type": "PublicationReasonCode"
      },
      {
        "name": "input_snapshot_ref",
        "type": "str"
      },
      {
        "name": "policy_version",
        "type": "str"
      },
      {
        "name": "decision_version",
        "type": "str"
      }
    ],
    "PublicationRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "observation_id",
        "type": "str"
      },
      {
        "name": "audience",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
      }
    ],
    "ReplayProvenance": [
      {
        "name": "repository",
        "type": "str"
      },
      {
        "name": "git_commit",
        "type": "str"
      },
      {
        "name": "code_tree_sha256",
        "type": "str"
      },
      {
        "name": "input_snapshot_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "parameter_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "table_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "policy_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "commit_code_linkage",
        "type": "str"
      },
      {
        "name": "provenance_source",
        "type": "str"
      }
    ],
    "ResolutionExposurePlan": [
      {
        "name": "plan_id",
        "type": "str"
      },
      {
        "name": "aggregate_id",
        "type": "str"
      },
      {
        "name": "selected_agent_id",
        "type": "str"
      },
      {
        "name": "members_exposed",
        "type": "int"
      },
      {
        "name": "selection_basis",
        "type": "ExposureSelectionBasis"
      },
      {
        "name": "selection_ref",
        "type": "str"
      },
      {
        "name": "allocation_basis",
        "type": "ExposureAllocationBasis"
      },
      {
        "name": "allocation_ref",
        "type": "str"
      },
      {
        "name": "explicit_share",
        "type": "D | None"
      }
    ],
    "ResolutionExposureRecord": [
      {
        "name": "plan_id",
        "type": "str"
      },
      {
        "name": "resolution_id",
        "type": "str"
      },
      {
        "name": "aggregate_id",
        "type": "str"
      },
      {
        "name": "agent_id",
        "type": "str"
      },
      {
        "name": "members_exposed",
        "type": "int"
      },
      {
        "name": "selection_basis",
        "type": "str"
      },
      {
        "name": "selection_ref",
        "type": "str"
      },
      {
        "name": "allocation_basis",
        "type": "str"
      },
      {
        "name": "allocation_ref",
        "type": "str"
      },
      {
        "name": "allocation_fraction",
        "type": "D"
      }
    ],
    "ScenarioResource": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "family",
        "type": "str"
      },
      {
        "name": "in_situ",
        "type": "D"
      },
      {
        "name": "accessible",
        "type": "D"
      },
      {
        "name": "recoverable",
        "type": "D"
      },
      {
        "name": "remaining",
        "type": "D"
      }
    ],
    "ScheduledEvent": [
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "effective_time",
        "type": "D"
      },
      {
        "name": "phase",
        "type": "Phase"
      },
      {
        "name": "priority",
        "type": "int"
      },
      {
        "name": "stable_key",
        "type": "str"
      },
      {
        "name": "process_id",
        "type": "str"
      },
      {
        "name": "payload",
        "type": "Tuple[Tuple[str, str], ...]"
      },
      {
        "name": "parent_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "snapshot_ref",
        "type": "str"
      }
    ],
    "ScheduledRunResult": [
      {
        "name": "run_mode",
        "type": "str"
      },
      {
        "name": "scheduler_contract_version",
        "type": "str"
      },
      {
        "name": "plan_fingerprint",
        "type": "str"
      },
      {
        "name": "initial_fingerprint",
        "type": "str"
      },
      {
        "name": "final_fingerprint",
        "type": "str"
      },
      {
        "name": "execution_log",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "event_results",
        "type": "Tuple[Tuple[str, str], ...]"
      },
      {
        "name": "verification_status",
        "type": "str"
      },
      {
        "name": "validation_status",
        "type": "str"
      },
      {
        "name": "repository",
        "type": "str"
      },
      {
        "name": "git_commit",
        "type": "str"
      },
      {
        "name": "code_tree_sha256",
        "type": "str"
      },
      {
        "name": "input_snapshot_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "parameter_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "table_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "policy_manifest_ids",
        "type": "Tuple[str, ...]"
      },
      {
        "name": "commit_code_linkage",
        "type": "str"
      },
      {
        "name": "provenance_fingerprint",
        "type": "str"
      },
      {
        "name": "execution_fingerprint",
        "type": "str"
      },
      {
        "name": "result_fingerprint",
        "type": "str"
      }
    ],
    "SnapshotFact": [
      {
        "name": "key",
        "type": "str"
      },
      {
        "name": "state",
        "type": "FactState"
      },
      {
        "name": "value",
        "type": "str | None"
      },
      {
        "name": "source_ref",
        "type": "str"
      }
    ],
    "SponsorProjectDecision": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "request_id",
        "type": "str"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "outcome",
        "type": "SponsorProjectDecisionOutcome"
      },
      {
        "name": "requested_financing",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "SponsorProjectReasonCode"
      },
      {
        "name": "unknown_input_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "input_snapshot_ref",
        "type": "str"
      },
      {
        "name": "policy_version",
        "type": "str"
      },
      {
        "name": "decision_version",
        "type": "str"
      }
    ],
    "SponsorProjectDecisionRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "observation_id",
        "type": "str"
      },
      {
        "name": "required_fact_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "required_belief_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "required_prior_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "currency_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
      }
    ],
    "SystemState": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "process_type",
        "type": "str"
      },
      {
        "name": "owned_state_refs",
        "type": "set[str]"
      },
      {
        "name": "runtime_class",
        "type": "RuntimeObjectClass"
      }
    ],
    "Transaction": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "source_account",
        "type": "str"
      },
      {
        "name": "destination_account",
        "type": "str"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "purpose",
        "type": "TxPurpose"
      },
      {
        "name": "source_location",
        "type": "str"
      },
      {
        "name": "destination_location",
        "type": "str"
      },
      {
        "name": "supplier_location",
        "type": "Optional[str]"
      },
      {
        "name": "asset_location",
        "type": "Optional[str]"
      },
      {
        "name": "parent_ids",
        "type": "tuple[str, ...]"
      }
    ],
    "UnderwritingInput": [
      {
        "name": "input_id",
        "type": "str"
      },
      {
        "name": "archetype_id",
        "type": "str"
      },
      {
        "name": "kind",
        "type": "UnderwritingInputKind"
      },
      {
        "name": "value",
        "type": "D | None"
      },
      {
        "name": "unit",
        "type": "str"
      },
      {
        "name": "status",
        "type": "UnderwritingInputStatus"
      },
      {
        "name": "source_or_rationale_ref",
        "type": "str"
      },
      {
        "name": "basis_year",
        "type": "int"
      },
      {
        "name": "sensitivity_low",
        "type": "D | None"
      },
      {
        "name": "sensitivity_high",
        "type": "D | None"
      },
      {
        "name": "valid_from",
        "type": "int | None"
      },
      {
        "name": "valid_to",
        "type": "int | None"
      }
    ],
    "UnderwritingTable": [
      {
        "name": "table_id",
        "type": "str"
      },
      {
        "name": "version",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "inputs",
        "type": "Tuple[UnderwritingInput, ...]"
      }
    ]
  },
  "units": {
    "Account.balance": "MODEL_CURRENCY",
    "Asset.book_value": "MODEL_CURRENCY",
    "Asset.capacity": "ASSET_CLASS_CAPACITY_UNIT",
    "Commitment.amount": "MODEL_CURRENCY",
    "Commitment.committed": "MODEL_CURRENCY",
    "Commitment.disbursed": "MODEL_CURRENCY",
    "Commitment.lapsed": "MODEL_CURRENCY",
    "DecisionSnapshot.effective_time": "SIM_TIME",
    "EarthImpactLedger.qualifying_supplied_expenditure": "MODEL_CURRENCY",
    "EarthImpactLedger.terrestrial_fcf_delta": "MODEL_CURRENCY",
    "ExplorationDecision.authorized_cost": "REQUEST_CURRENCY_UNIT",
    "ExplorationRequest.year": "SIM_YEAR",
    "FinancierPolicyManifest.world_detection_rate": "PROBABILITY",
    "FinancierPolicyManifest.world_false_positive_rate": "PROBABILITY",
    "FinancingDecision.amount": "REQUEST_CURRENCY_UNIT",
    "FinancingRequest.amount": "FIELD:FinancingRequest.currency_unit",
    "FinancingRequest.year": "SIM_YEAR",
    "FixedCapitalFormationEvent.amount": "MODEL_CURRENCY",
    "FixedCapitalFormationEvent.year": "SIM_YEAR",
    "Observation.year": "SIM_YEAR",
    "PolicyParameter.local_perturbation": "FIELD:PolicyParameter.unit",
    "PolicyParameter.sensitivity_high": "FIELD:PolicyParameter.unit",
    "PolicyParameter.sensitivity_low": "FIELD:PolicyParameter.unit",
    "PolicyParameter.value": "FIELD:PolicyParameter.unit",
    "Project": "NO_INTRINSIC_SCALAR_UNIT",
    "PublicInformationArtifact.year": "SIM_YEAR",
    "PublicationRequest.year": "SIM_YEAR",
    "ResolutionExposureRecord.allocation_fraction": "DIMENSIONLESS_SHARE",
    "ScenarioResource.accessible": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.in_situ": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.recoverable": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.remaining": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScheduledEvent.effective_time": "SIM_TIME",
    "SponsorProjectDecision.requested_financing": "REQUEST_CURRENCY_UNIT",
    "SponsorProjectDecisionRequest.year": "SIM_YEAR",
    "Transaction.amount": "MODEL_CURRENCY",
    "Transaction.year": "SIM_YEAR",
    "UnderwritingInput.basis_year": "SIM_YEAR",
    "UnderwritingInput.sensitivity_high": "FIELD:UnderwritingInput.unit",
    "UnderwritingInput.sensitivity_low": "FIELD:UnderwritingInput.unit",
    "UnderwritingInput.valid_from": "SIM_YEAR",
    "UnderwritingInput.valid_to": "SIM_YEAR",
    "UnderwritingInput.value": "FIELD:UnderwritingInput.unit"
  }
}
```
<!-- ODD_SCHEMA_REGISTRY_END -->

## 10. Relationship to governance

This ODD-aligned specification is operational documentation, not epistemic authority. It does not qualify inputs or convert validation fixtures into evidence. TRACE-like rationale, testing and validation status are carried by the Phase 3B design/validation records and the V&V protocol.

## 11. Current validation boundary

The executable kernel is verified against selected invariants and deterministic fixtures. It is not yet empirically validated as a civilization/economic forecasting model. Behavioral calibration, historical/backcast validation and out-of-sample validation are future gates.
