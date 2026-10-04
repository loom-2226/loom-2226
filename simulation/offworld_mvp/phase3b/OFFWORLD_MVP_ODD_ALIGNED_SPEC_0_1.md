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
General autonomous adaptation remains gated. Build 5 currently contains individually authorized bounded autonomous policies for the private financier, public institutional remote explorer/surface prospector/publisher/settlement-support role, and private sponsor/operator including project advancement, operating-cycle, inventory-sale and project-surplus allocation decisions. Settlement itself remains an AGGREGATE; it is not promoted to an Agent merely because it contains population, infrastructure and economic state. Additional Agent roles or materially expanded policies require separate governance.

### Objectives
Agent objective state exists conceptually. No common utility function is assumed.

### Learning
Observation -> information -> belief is permitted. Legacy Build 4/early Build 5 fixtures retain deliberately crude validation updates. Build 5 Test 007A additionally implements a bounded Bayesian Agent-side update for SURFACE observations using separately declared Test-only likelihood parameters. No current belief-update path is empirically calibrated.

### Prediction
Agents may later form expectations from their own information. WORLD_SIM truth may not be substituted for those expectations.

### Sensing
Only declared observation/information channels cross the hidden-world firewall.

### Interaction
Interactions occur through action requests, transactions, observations, ownership claims and system-mediated processes. Agents do not mutate world state. Test 009A keeps commodity clearing as a SYSTEM process: the sponsor may offer realized inventory from admitted exogenous price/demand state, while the market SYSTEM validates current inventory and remaining demand and records the physical/financial clearing. It does not read hidden scenario resource truth. Test 010A separately distinguishes financing-return claims from project ownership claims: the sponsor chooses bounded category totals from admitted project cash/obligations, while the distribution SYSTEM validates disbursed-financing lineage, preserves reserve cash, executes local reinvestment, and routes owner residual strictly by the ownership ledger. Test 011A consumes already-realized local reinvestment through a bounded settlement-infrastructure SYSTEM, derives settlement stage from realized productive/infrastructure/population/support state, and permits the existing public institutional Agent to authorize migration only within realized habitat headroom, Earth population and public funding. Migration remains aggregate and population-conserving. Test 012A adds an exogenous capability-qualified Earth-to-offworld passenger transport relationship with separately represented Cost, TravelTime, Energy, LossRisk and Capacity; the public Agent authorizes use from admitted service state, while SYSTEM execution separately charges support and transport, holds passengers in aggregate in-transit population until deterministic arrival, and preserves total population exactly.

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
- public REMOTE and second-stage higher-quality SURFACE information acquisition with separate world/Agent likelihood semantics;
- public observation publication and cross-Agent information transfer;
- bounded sponsor/operator project advancement, financing-request and abandonment decisions;
- explicit staged project-development plans, construction WIP, commissioning, failure and WIP write-off;
- bounded sponsor operating working-capital decisions, OPEX execution and WORLD_SIM resource-bounded extraction into offworld inventory;
- bounded sponsor inventory-sale decisions plus immutable exogenous commodity-market envelopes, signed Earth-boundary clearing, physical inventory transfer and project revenue;
- bounded sponsor project-surplus allocation with separately declared financing-return claims, retained operating reserve, local reinvestment and ownership-ledger-pro-rata owner distributions;
- bounded settlement formation using realized local-reinvestment-funded infrastructure stock, explicit people-equivalent habitat capacity, aggregate conserved Earth-to-offworld migration, explicit public subsidy, and state-derived EXTRACTION_ENCLAVE / DEPENDENT_SETTLEMENT stages;
- aggregate-resolution reconciliation;
- uncertainty/ensemble runner;
- ensemble reporting guardrails that distinguish scenario spread, parameter sensitivity, uncertainty spread and stochastic variability;
- executable A1–A9 accounting/physical identity auditor;
- signed Earth-boundary reconciliation;
- staged multi-year WIP and multi-rate synchronization fixtures.

The A1–A9 property fixture captures state before every scheduler-valid transition and evaluates all nine identities immediately after each transition. Current generative coverage includes disbursement, WIP spend, commissioning, depreciation, extraction, revenue, surplus disposition and commitment lapse.

The multi-rate synchronization fixture combines day-scale mission observations, quarterly finance and annual Earth-system events under one deterministic scheduler.

Transport, technology gating, dynamic economic reserve conversion, mature colony service/reliability operations, labour/skill matching, cohorts/households/individual persons, DIVERSIFYING_SETTLEMENT and HANDOFF_CANDIDATE mechanics, grade/quantity prospecting estimates, `CLOSED` and post-failure/zero-output lifecycle semantics, autonomous sponsor prospecting, repeated operating/sale/distribution cycles, empirical financing terms and debt/equity waterfalls, endogenous reinvestment-opportunity search, endogenous price formation, price-responsive demand, multi-buyer/multi-seller competition, country-policy market intervention, empirical sensor calibration, empirical construction calibration, empirical mining calibration, empirical habitat/migration calibration, and empirical market calibration remain incomplete unless separately implemented and validated.

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


### 50.13 Earth reference / realized shadow accounting — Test 013A

Build 5 now records realized offworld-caused Earth consequences in the existing
`EarthImpactLedger` without mutating the adopted Earth reference lineage. The shadow
layer separately records capital diverted to offworld activity, capital returned to
Earth, offworld purchases from Earth, Earth purchases from offworld ventures, migration
from Earth, and the explicit returning-population channel, alongside the pre-existing
qualifying Earth-supplied expenditure and terrestrial-FCF displacement view.

Shadow entries are derived from realized ledger/population transitions and do not emit
transactions, create decisions, or feed back into Earth propagation. Hidden scenario
resource truth does not alter shadow classification when realized flows are held fixed.
Test 013A does not authorize a return-transport transition; returning population remains
zero unless a separately authorized transition exists.


### 50.14 Repeated enterprise operating lifecycle — Test 014A

Build 5 now supports repeated sponsor operating cycles over one persistent kernel/world
state by reusing the existing operating, extraction, market, surplus-reserve, financing,
and decision-epoch machinery. A new bounded post-cycle sponsor review consumes only
admitted project status plus planned and realized output from a completed extraction
record. Under the Test-only structural strategy, positive realized output authorizes
`CONTINUE`; zero realized output authorizes `CLOSE`. No profitability threshold or
hidden resource state is exposed to the sponsor.

`CONTINUE` does not mutate project lifecycle state. `CLOSE` is the only newly earned
world transition and is executable only after SYSTEM validation of exact extraction
lineage, zero realized output, sponsor identity, and `CLOSE_PROJECT` capability. The
generic historical sponsor project-transition method is not widened; `OPERATING ->
CLOSED` remains confined to the Test 014A review executor.

The qualification chain reuses the Test 010 next-cycle operating reserve. RICH and
SPARSE therefore attempt a later operating cycle from retained reserve without synthetic
new financing. After reserve exhaustion, the unchanged operating policy may request the
exact next-cycle finance shortfall and the unchanged financier machinery may recapitalize
a still-open venture. Test 014A does not add maintenance, repair, bankruptcy, salvage,
reopening, endogenous pricing, or a calibrated closure strategy.

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
      "CONSTRUCT",
      "OPERATE",
      "CLOSE",
      "FAIL",
      "ABANDON",
      "EXTRACT",
      "SELL",
      "MIGRATE",
      "TRANSPORT",
      "REINVEST",
      "DISTRIBUTE",
      "SETTLE"
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
    "DevelopmentResolutionOutcome": [
      "OPERATING",
      "FAILED"
    ],
    "DevelopmentStageOutcome": [
      "SPENT",
      "BLOCKED_PROJECT_CASH",
      "BLOCKED_SUPPLY"
    ],
    "EnterpriseReviewDecisionOutcome": [
      "CONTINUE",
      "CLOSE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "EnterpriseReviewReasonCode": [
      "POSITIVE_OUTPUT_CONTINUE",
      "ZERO_OUTPUT_CLOSE",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "PROJECT_STATE_BLOCK",
      "OUTPUT_RECORD_INVALID",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
    ],
    "ExplorationDecisionOutcome": [
      "AUTHORIZE",
      "DECLINE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "ExplorationReasonCode": [
      "APPROVED_PUBLIC_INFORMATION_MISSION",
      "APPROVED_SURFACE_INFORMATION_MISSION",
      "INSUFFICIENT_BUDGET",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "DEFER_UNSUPPORTED_CHANNEL",
      "DEFER_PREREQUISITE_OBSERVATION",
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
    "OperatingCycleDecisionOutcome": [
      "REQUEST_FINANCE",
      "OPERATE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "OperatingCycleReasonCode": [
      "POSITIVE_EVIDENCE_FINANCE_REQUIRED",
      "OPERATING_CYCLE_AUTHORIZED",
      "NONPOSITIVE_EVIDENCE",
      "NO_RELEVANT_INFORMATION",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "PROJECT_STATE_BLOCK",
      "ASSET_OR_CAPACITY_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
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
    "SaleDecisionOutcome": [
      "OFFER",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "SaleReasonCode": [
      "MARKET_OFFER_AUTHORIZED",
      "NO_SELLABLE_INVENTORY",
      "NO_POSITIVE_PRICE",
      "NO_MARKET_DEMAND",
      "NO_RELEVANT_INFORMATION",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "PROJECT_STATE_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
    ],
    "SettlementSupportDecisionOutcome": [
      "AUTHORIZE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "SettlementSupportReasonCode": [
      "SETTLEMENT_SUPPORT_AUTHORIZED",
      "STAGE_BLOCK",
      "NO_REQUESTED_RESIDENTS",
      "HABITAT_CAPACITY_LIMIT",
      "ORIGIN_POPULATION_LIMIT",
      "INSUFFICIENT_PUBLIC_FUNDS",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
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
    "SurplusDistributionDecisionOutcome": [
      "DISTRIBUTE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "SurplusDistributionReasonCode": [
      "DISTRIBUTION_AUTHORIZED",
      "NO_DISTRIBUTABLE_CASH",
      "PROJECT_STATE_BLOCK",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
    ],
    "TransportSettlementDecisionOutcome": [
      "AUTHORIZE",
      "DEFER",
      "BLOCKED_UNKNOWN"
    ],
    "TransportSettlementReasonCode": [
      "SETTLEMENT_TRANSPORT_AUTHORIZED",
      "STAGE_BLOCK",
      "NO_REQUESTED_RESIDENTS",
      "HABITAT_CAPACITY_LIMIT",
      "ORIGIN_POPULATION_LIMIT",
      "TRANSPORT_UNAVAILABLE",
      "TRANSPORT_CAPACITY_LIMIT",
      "LOSS_RISK_UNSUPPORTED",
      "INSUFFICIENT_PUBLIC_FUNDS",
      "CAPABILITY_OR_OBJECTIVE_BLOCK",
      "BLOCKED_REQUIRED_INPUT_UNKNOWN"
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
      "RESERVE",
      "FINANCIER_RETURN",
      "OWNER_DISTRIBUTION",
      "PUBLIC_SUBSIDY",
      "TRANSPORT_PAYMENT"
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
  "registry_version": "ODD_SCHEMA_REGISTRY_0_16",
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
        "name": "habitat_capacity",
        "type": "int"
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
    "CommodityMarketEnvelope": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "buyer_account_id",
        "type": "str"
      },
      {
        "name": "unit_price",
        "type": "D"
      },
      {
        "name": "demand_quantity",
        "type": "D"
      },
      {
        "name": "currency_unit",
        "type": "str"
      },
      {
        "name": "quantity_unit",
        "type": "str"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "envelope_version",
        "type": "str"
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
    "DevelopmentResolutionRecord": [
      {
        "name": "plan_id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "outcome",
        "type": "DevelopmentResolutionOutcome"
      },
      {
        "name": "required_cost",
        "type": "D"
      },
      {
        "name": "accumulated_cost",
        "type": "D"
      },
      {
        "name": "commissioned",
        "type": "D"
      },
      {
        "name": "written_off",
        "type": "D"
      },
      {
        "name": "asset_id",
        "type": "str"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "DevelopmentStageRecord": [
      {
        "name": "plan_id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "planned_amount",
        "type": "D"
      },
      {
        "name": "outcome",
        "type": "DevelopmentStageOutcome"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "transaction_id",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
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
      },
      {
        "name": "capital_diverted_to_offworld",
        "type": "Dict[tuple[str, int], D]"
      },
      {
        "name": "capital_returned_to_earth",
        "type": "Dict[tuple[str, int], D]"
      },
      {
        "name": "offworld_purchases_from_earth",
        "type": "Dict[tuple[str, int], D]"
      },
      {
        "name": "earth_purchases_from_offworld",
        "type": "Dict[tuple[str, int], D]"
      },
      {
        "name": "migration_from_earth",
        "type": "Dict[int, int]"
      },
      {
        "name": "returning_population",
        "type": "Dict[int, int]"
      }
    ],
    "EnterpriseReviewDecision": [
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
        "type": "EnterpriseReviewDecisionOutcome"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "EnterpriseReviewReasonCode"
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
    "EnterpriseReviewRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
      },
      {
        "name": "request_id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "extraction_event_id",
        "type": "str"
      },
      {
        "name": "planned_quantity",
        "type": "D"
      },
      {
        "name": "actual_output",
        "type": "D"
      },
      {
        "name": "outcome",
        "type": "EnterpriseReviewDecisionOutcome"
      },
      {
        "name": "status_before",
        "type": "str"
      },
      {
        "name": "status_after",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "EnterpriseReviewRequest": [
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
        "name": "extraction_event_id",
        "type": "str"
      },
      {
        "name": "required_fact_keys",
        "type": "tuple[str, ...]"
      },
      {
        "name": "quantity_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
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
        "name": "prerequisite_observation_id",
        "type": "str"
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
    "ExtractionResolutionRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
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
        "name": "resource_id",
        "type": "str"
      },
      {
        "name": "planned_quantity",
        "type": "D"
      },
      {
        "name": "actual_extracted",
        "type": "D"
      },
      {
        "name": "resource_before",
        "type": "D"
      },
      {
        "name": "resource_after",
        "type": "D"
      },
      {
        "name": "inventory_before",
        "type": "D"
      },
      {
        "name": "inventory_after",
        "type": "D"
      },
      {
        "name": "extraction_event_id",
        "type": "str"
      },
      {
        "name": "record_version",
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
    "FinancingReturnClaim": [
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
        "name": "destination_account_id",
        "type": "str"
      },
      {
        "name": "maximum_return_amount",
        "type": "D"
      },
      {
        "name": "source_commitment_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "claim_version",
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
    "MarketClearingRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "market_state_id",
        "type": "str"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
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
        "name": "offered_quantity",
        "type": "D"
      },
      {
        "name": "demand_before",
        "type": "D"
      },
      {
        "name": "cleared_quantity",
        "type": "D"
      },
      {
        "name": "demand_after",
        "type": "D"
      },
      {
        "name": "unit_price",
        "type": "D"
      },
      {
        "name": "transaction_value",
        "type": "D"
      },
      {
        "name": "local_inventory_before",
        "type": "D"
      },
      {
        "name": "local_inventory_after",
        "type": "D"
      },
      {
        "name": "market_inventory_before",
        "type": "D"
      },
      {
        "name": "market_inventory_after",
        "type": "D"
      },
      {
        "name": "transaction_id",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
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
    "ObservationBeliefUpdateRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "agent_id",
        "type": "str"
      },
      {
        "name": "observation_id",
        "type": "str"
      },
      {
        "name": "belief_key",
        "type": "str"
      },
      {
        "name": "prior",
        "type": "D"
      },
      {
        "name": "posterior",
        "type": "D"
      },
      {
        "name": "detection_rate",
        "type": "D"
      },
      {
        "name": "false_positive_rate",
        "type": "D"
      },
      {
        "name": "model_id",
        "type": "str"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "OperatingCostRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
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
        "name": "supplier_account_id",
        "type": "str"
      },
      {
        "name": "planned_quantity",
        "type": "D"
      },
      {
        "name": "unit_opex",
        "type": "D"
      },
      {
        "name": "total_opex",
        "type": "D"
      },
      {
        "name": "transaction_id",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "OperatingCycleDecision": [
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
        "type": "OperatingCycleDecisionOutcome"
      },
      {
        "name": "requested_financing",
        "type": "D"
      },
      {
        "name": "planned_quantity",
        "type": "D"
      },
      {
        "name": "authorized_opex",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "OperatingCycleReasonCode"
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
    "OperatingCycleRequest": [
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
        "name": "asset_id",
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
        "name": "quantity_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
      }
    ],
    "OwnerDistributionAllocation": [
      {
        "name": "owner_id",
        "type": "str"
      },
      {
        "name": "destination_account_id",
        "type": "str"
      },
      {
        "name": "ownership_share",
        "type": "D"
      },
      {
        "name": "amount",
        "type": "D"
      },
      {
        "name": "transaction_id",
        "type": "str"
      }
    ],
    "PassengerTransportArrivalRecord": [
      {
        "name": "departure_id",
        "type": "str"
      },
      {
        "name": "relationship_id",
        "type": "str"
      },
      {
        "name": "destination_node_id",
        "type": "str"
      },
      {
        "name": "passengers",
        "type": "int"
      },
      {
        "name": "arrival_time",
        "type": "D"
      },
      {
        "name": "in_transit_before",
        "type": "int"
      },
      {
        "name": "in_transit_after",
        "type": "int"
      },
      {
        "name": "offworld_population_before",
        "type": "int"
      },
      {
        "name": "offworld_population_after",
        "type": "int"
      },
      {
        "name": "total_population_before",
        "type": "int"
      },
      {
        "name": "total_population_after",
        "type": "int"
      },
      {
        "name": "arrival_event_id",
        "type": "str"
      },
      {
        "name": "stage_event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "PassengerTransportDepartureRecord": [
      {
        "name": "departure_id",
        "type": "str"
      },
      {
        "name": "decision_id",
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
        "name": "technology_state_id",
        "type": "str"
      },
      {
        "name": "relationship_id",
        "type": "str"
      },
      {
        "name": "origin_node_id",
        "type": "str"
      },
      {
        "name": "destination_node_id",
        "type": "str"
      },
      {
        "name": "passengers",
        "type": "int"
      },
      {
        "name": "support_amount",
        "type": "D"
      },
      {
        "name": "transport_amount",
        "type": "D"
      },
      {
        "name": "departure_time",
        "type": "D"
      },
      {
        "name": "arrival_time",
        "type": "D"
      },
      {
        "name": "earth_population_before",
        "type": "int"
      },
      {
        "name": "earth_population_after",
        "type": "int"
      },
      {
        "name": "in_transit_before",
        "type": "int"
      },
      {
        "name": "in_transit_after",
        "type": "int"
      },
      {
        "name": "total_population_before",
        "type": "int"
      },
      {
        "name": "total_population_after",
        "type": "int"
      },
      {
        "name": "subsidy_before",
        "type": "D"
      },
      {
        "name": "subsidy_after",
        "type": "D"
      },
      {
        "name": "support_transaction_id",
        "type": "str"
      },
      {
        "name": "transport_transaction_id",
        "type": "str"
      },
      {
        "name": "departure_event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
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
      },
      {
        "name": "in_transit",
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
    "ProjectDevelopmentPlan": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "wip_id",
        "type": "str"
      },
      {
        "name": "asset_id",
        "type": "str"
      },
      {
        "name": "supplier_account_id",
        "type": "str"
      },
      {
        "name": "asset_node_id",
        "type": "str"
      },
      {
        "name": "required_cost",
        "type": "D"
      },
      {
        "name": "stage_schedule",
        "type": "tuple[tuple[int, D], ...]"
      },
      {
        "name": "completion_year",
        "type": "int"
      },
      {
        "name": "commissioned_capacity",
        "type": "D"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "plan_version",
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
    "SaleDecision": [
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
        "type": "SaleDecisionOutcome"
      },
      {
        "name": "offered_quantity",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "SaleReasonCode"
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
    "SaleDecisionRequest": [
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
        "name": "market_state_id",
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
        "name": "currency_unit",
        "type": "str"
      },
      {
        "name": "quantity_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
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
    "SettlementInfrastructurePlan": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "source_account_id",
        "type": "str"
      },
      {
        "name": "supplier_account_id",
        "type": "str"
      },
      {
        "name": "infrastructure_cost",
        "type": "D"
      },
      {
        "name": "habitat_capacity",
        "type": "int"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "plan_version",
        "type": "str"
      }
    ],
    "SettlementInfrastructureRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "plan_id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "outcome",
        "type": "str"
      },
      {
        "name": "cost",
        "type": "D"
      },
      {
        "name": "habitat_capacity_added",
        "type": "int"
      },
      {
        "name": "infrastructure_before",
        "type": "D"
      },
      {
        "name": "infrastructure_after",
        "type": "D"
      },
      {
        "name": "habitat_capacity_before",
        "type": "int"
      },
      {
        "name": "habitat_capacity_after",
        "type": "int"
      },
      {
        "name": "transaction_id",
        "type": "str"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "SettlementStageRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "prior_stage",
        "type": "str"
      },
      {
        "name": "new_stage",
        "type": "str"
      },
      {
        "name": "productive_capital",
        "type": "D"
      },
      {
        "name": "production_capacity",
        "type": "D"
      },
      {
        "name": "population",
        "type": "int"
      },
      {
        "name": "infrastructure",
        "type": "D"
      },
      {
        "name": "habitat_capacity",
        "type": "int"
      },
      {
        "name": "external_subsidy",
        "type": "D"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "rule_version",
        "type": "str"
      }
    ],
    "SettlementSupportDecision": [
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
        "type": "SettlementSupportDecisionOutcome"
      },
      {
        "name": "authorized_residents",
        "type": "int"
      },
      {
        "name": "support_amount",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "SettlementSupportReasonCode"
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
    "SettlementSupportExecutionRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "authorized_residents",
        "type": "int"
      },
      {
        "name": "support_amount",
        "type": "D"
      },
      {
        "name": "earth_population_before",
        "type": "int"
      },
      {
        "name": "earth_population_after",
        "type": "int"
      },
      {
        "name": "offworld_population_before",
        "type": "int"
      },
      {
        "name": "offworld_population_after",
        "type": "int"
      },
      {
        "name": "total_population_before",
        "type": "int"
      },
      {
        "name": "total_population_after",
        "type": "int"
      },
      {
        "name": "subsidy_before",
        "type": "D"
      },
      {
        "name": "subsidy_after",
        "type": "D"
      },
      {
        "name": "support_transaction_id",
        "type": "str"
      },
      {
        "name": "migration_event_id",
        "type": "str"
      },
      {
        "name": "stage_event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "SettlementSupportRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "node_id",
        "type": "str"
      },
      {
        "name": "support_account_id",
        "type": "str"
      },
      {
        "name": "requested_residents",
        "type": "int"
      },
      {
        "name": "support_cost",
        "type": "D"
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
        "name": "population_unit",
        "type": "str"
      },
      {
        "name": "request_version",
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
    "SurfaceProspectingModel": [
      {
        "name": "model_id",
        "type": "str"
      },
      {
        "name": "world_false_positive",
        "type": "D"
      },
      {
        "name": "world_false_negative",
        "type": "D"
      },
      {
        "name": "agent_detection_rate",
        "type": "D"
      },
      {
        "name": "agent_false_positive_rate",
        "type": "D"
      },
      {
        "name": "remote_world_false_positive_reference",
        "type": "D"
      },
      {
        "name": "remote_world_false_negative_reference",
        "type": "D"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "model_version",
        "type": "str"
      }
    ],
    "SurfaceProspectingWorldRecord": [
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
        "name": "prerequisite_observation_id",
        "type": "str"
      },
      {
        "name": "observation_id",
        "type": "str"
      },
      {
        "name": "world_model_id",
        "type": "str"
      },
      {
        "name": "world_false_positive",
        "type": "D"
      },
      {
        "name": "world_false_negative",
        "type": "D"
      },
      {
        "name": "deterministic_draw",
        "type": "D"
      },
      {
        "name": "signal",
        "type": "str"
      },
      {
        "name": "expenditure_transaction_id",
        "type": "str"
      },
      {
        "name": "exploration_asset_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "SurplusDistributionDecision": [
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
        "type": "SurplusDistributionDecisionOutcome"
      },
      {
        "name": "reserve",
        "type": "D"
      },
      {
        "name": "financier_return",
        "type": "D"
      },
      {
        "name": "local_reinvestment",
        "type": "D"
      },
      {
        "name": "owner_distribution",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "SurplusDistributionReasonCode"
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
    "SurplusDistributionRecord": [
      {
        "name": "year",
        "type": "int"
      },
      {
        "name": "project_id",
        "type": "str"
      },
      {
        "name": "actor_id",
        "type": "str"
      },
      {
        "name": "decision_id",
        "type": "str"
      },
      {
        "name": "financing_return_claim_id",
        "type": "str"
      },
      {
        "name": "opening_project_cash",
        "type": "D"
      },
      {
        "name": "reserve",
        "type": "D"
      },
      {
        "name": "financier_return",
        "type": "D"
      },
      {
        "name": "local_reinvestment",
        "type": "D"
      },
      {
        "name": "local_reinvestment_account_id",
        "type": "str"
      },
      {
        "name": "owner_distribution",
        "type": "D"
      },
      {
        "name": "owner_allocations",
        "type": "tuple[OwnerDistributionAllocation, ...]"
      },
      {
        "name": "closing_project_cash",
        "type": "D"
      },
      {
        "name": "transaction_ids",
        "type": "tuple[str, ...]"
      },
      {
        "name": "event_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "SurplusDistributionRequest": [
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
        "name": "financing_return_claim_id",
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
    "TechnologyCapabilityState": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "effective_from",
        "type": "D"
      },
      {
        "name": "effective_to",
        "type": "D"
      },
      {
        "name": "qualified_capabilities",
        "type": "tuple[str, ...]"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "state_version",
        "type": "str"
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
    "TransportQualificationRecord": [
      {
        "name": "technology_state_id",
        "type": "str"
      },
      {
        "name": "relationship_id",
        "type": "str"
      },
      {
        "name": "effective_time",
        "type": "D"
      },
      {
        "name": "available",
        "type": "bool"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "required_capability_id",
        "type": "str"
      },
      {
        "name": "record_version",
        "type": "str"
      }
    ],
    "TransportRelationship": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "origin_node_id",
        "type": "str"
      },
      {
        "name": "destination_node_id",
        "type": "str"
      },
      {
        "name": "effective_from",
        "type": "D"
      },
      {
        "name": "effective_to",
        "type": "D"
      },
      {
        "name": "required_capability_id",
        "type": "str"
      },
      {
        "name": "cost_per_passenger",
        "type": "D"
      },
      {
        "name": "travel_time",
        "type": "D"
      },
      {
        "name": "energy_per_passenger",
        "type": "D"
      },
      {
        "name": "loss_risk",
        "type": "D"
      },
      {
        "name": "capacity",
        "type": "int"
      },
      {
        "name": "passenger_class",
        "type": "str"
      },
      {
        "name": "source_ref",
        "type": "str"
      },
      {
        "name": "epistemic_status",
        "type": "str"
      },
      {
        "name": "relationship_version",
        "type": "str"
      }
    ],
    "TransportSettlementDecision": [
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
        "type": "TransportSettlementDecisionOutcome"
      },
      {
        "name": "authorized_residents",
        "type": "int"
      },
      {
        "name": "support_amount",
        "type": "D"
      },
      {
        "name": "transport_amount",
        "type": "D"
      },
      {
        "name": "relationship_id",
        "type": "str"
      },
      {
        "name": "technology_state_id",
        "type": "str"
      },
      {
        "name": "departure_time",
        "type": "D"
      },
      {
        "name": "arrival_time",
        "type": "D"
      },
      {
        "name": "reason",
        "type": "str"
      },
      {
        "name": "reason_code",
        "type": "TransportSettlementReasonCode"
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
    "TransportSettlementRequest": [
      {
        "name": "id",
        "type": "str"
      },
      {
        "name": "departure_time",
        "type": "D"
      },
      {
        "name": "origin_node_id",
        "type": "str"
      },
      {
        "name": "destination_node_id",
        "type": "str"
      },
      {
        "name": "support_account_id",
        "type": "str"
      },
      {
        "name": "transport_account_id",
        "type": "str"
      },
      {
        "name": "requested_residents",
        "type": "int"
      },
      {
        "name": "support_cost",
        "type": "D"
      },
      {
        "name": "transport_relationship_id",
        "type": "str"
      },
      {
        "name": "technology_state_id",
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
        "name": "population_unit",
        "type": "str"
      },
      {
        "name": "time_unit",
        "type": "str"
      },
      {
        "name": "request_version",
        "type": "str"
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
    "ColonyState.habitat_capacity": "PEOPLE_EQUIVALENT",
    "ColonyState.population": "PEOPLE_EQUIVALENT",
    "Commitment.amount": "MODEL_CURRENCY",
    "Commitment.committed": "MODEL_CURRENCY",
    "Commitment.disbursed": "MODEL_CURRENCY",
    "Commitment.lapsed": "MODEL_CURRENCY",
    "CommodityMarketEnvelope.demand_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "CommodityMarketEnvelope.unit_price": "MODEL_CURRENCY_PER_RESOURCE_UNIT",
    "CommodityMarketEnvelope.year": "SIM_YEAR",
    "DecisionSnapshot.effective_time": "SIM_TIME",
    "DevelopmentResolutionRecord.accumulated_cost": "MODEL_CURRENCY",
    "DevelopmentResolutionRecord.commissioned": "MODEL_CURRENCY",
    "DevelopmentResolutionRecord.required_cost": "MODEL_CURRENCY",
    "DevelopmentResolutionRecord.written_off": "MODEL_CURRENCY",
    "DevelopmentResolutionRecord.year": "SIM_YEAR",
    "DevelopmentStageRecord.planned_amount": "MODEL_CURRENCY",
    "DevelopmentStageRecord.year": "SIM_YEAR",
    "EarthImpactLedger.capital_diverted_to_offworld": "MODEL_CURRENCY",
    "EarthImpactLedger.capital_returned_to_earth": "MODEL_CURRENCY",
    "EarthImpactLedger.earth_purchases_from_offworld": "MODEL_CURRENCY",
    "EarthImpactLedger.migration_from_earth": "PEOPLE_EQUIVALENT",
    "EarthImpactLedger.offworld_purchases_from_earth": "MODEL_CURRENCY",
    "EarthImpactLedger.qualifying_supplied_expenditure": "MODEL_CURRENCY",
    "EarthImpactLedger.returning_population": "PEOPLE_EQUIVALENT",
    "EarthImpactLedger.terrestrial_fcf_delta": "MODEL_CURRENCY",
    "EnterpriseReviewRecord.actual_output": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "EnterpriseReviewRecord.planned_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "EnterpriseReviewRecord.year": "SIM_YEAR",
    "EnterpriseReviewRequest.year": "SIM_YEAR",
    "ExplorationDecision.authorized_cost": "REQUEST_CURRENCY_UNIT",
    "ExplorationRequest.year": "SIM_YEAR",
    "ExtractionResolutionRecord.actual_extracted": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.inventory_after": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.inventory_before": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.planned_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.resource_after": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.resource_before": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ExtractionResolutionRecord.year": "SIM_YEAR",
    "FinancierPolicyManifest.world_detection_rate": "PROBABILITY",
    "FinancierPolicyManifest.world_false_positive_rate": "PROBABILITY",
    "FinancingDecision.amount": "REQUEST_CURRENCY_UNIT",
    "FinancingRequest.amount": "FIELD:FinancingRequest.currency_unit",
    "FinancingRequest.year": "SIM_YEAR",
    "FinancingReturnClaim.maximum_return_amount": "MODEL_CURRENCY",
    "FixedCapitalFormationEvent.amount": "MODEL_CURRENCY",
    "FixedCapitalFormationEvent.year": "SIM_YEAR",
    "MarketClearingRecord.cleared_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.demand_after": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.demand_before": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.local_inventory_after": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.local_inventory_before": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.market_inventory_after": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.market_inventory_before": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.offered_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "MarketClearingRecord.transaction_value": "MODEL_CURRENCY",
    "MarketClearingRecord.unit_price": "MODEL_CURRENCY_PER_RESOURCE_UNIT",
    "MarketClearingRecord.year": "SIM_YEAR",
    "Observation.year": "SIM_YEAR",
    "ObservationBeliefUpdateRecord.detection_rate": "PROBABILITY",
    "ObservationBeliefUpdateRecord.false_positive_rate": "PROBABILITY",
    "ObservationBeliefUpdateRecord.posterior": "PROBABILITY",
    "ObservationBeliefUpdateRecord.prior": "PROBABILITY",
    "ObservationBeliefUpdateRecord.year": "SIM_YEAR",
    "OperatingCostRecord.planned_quantity": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "OperatingCostRecord.total_opex": "MODEL_CURRENCY",
    "OperatingCostRecord.unit_opex": "MODEL_CURRENCY_PER_RESOURCE_UNIT",
    "OperatingCostRecord.year": "SIM_YEAR",
    "OperatingCycleDecision.authorized_opex": "FIELD:OperatingCycleRequest.currency_unit",
    "OperatingCycleDecision.planned_quantity": "FIELD:OperatingCycleRequest.quantity_unit",
    "OperatingCycleDecision.requested_financing": "REQUEST_CURRENCY_UNIT",
    "OperatingCycleRequest.year": "SIM_YEAR",
    "OwnerDistributionAllocation.amount": "MODEL_CURRENCY",
    "OwnerDistributionAllocation.ownership_share": "DIMENSIONLESS_SHARE",
    "PassengerTransportArrivalRecord.arrival_time": "SIM_TIME",
    "PassengerTransportArrivalRecord.in_transit_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.in_transit_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.offworld_population_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.offworld_population_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.passengers": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.total_population_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportArrivalRecord.total_population_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.arrival_time": "SIM_TIME",
    "PassengerTransportDepartureRecord.departure_time": "SIM_TIME",
    "PassengerTransportDepartureRecord.earth_population_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.earth_population_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.in_transit_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.in_transit_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.passengers": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.subsidy_after": "MODEL_CURRENCY",
    "PassengerTransportDepartureRecord.subsidy_before": "MODEL_CURRENCY",
    "PassengerTransportDepartureRecord.support_amount": "MODEL_CURRENCY",
    "PassengerTransportDepartureRecord.total_population_after": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.total_population_before": "PEOPLE_EQUIVALENT",
    "PassengerTransportDepartureRecord.transport_amount": "MODEL_CURRENCY",
    "PolicyParameter.local_perturbation": "FIELD:PolicyParameter.unit",
    "PolicyParameter.sensitivity_high": "FIELD:PolicyParameter.unit",
    "PolicyParameter.sensitivity_low": "FIELD:PolicyParameter.unit",
    "PolicyParameter.value": "FIELD:PolicyParameter.unit",
    "PopulationLedger.earth": "PEOPLE_EQUIVALENT",
    "PopulationLedger.in_transit": "PEOPLE_EQUIVALENT_BY_TRANSPORT_BATCH",
    "PopulationLedger.offworld": "PEOPLE_EQUIVALENT_BY_NODE",
    "Project": "NO_INTRINSIC_SCALAR_UNIT",
    "ProjectDevelopmentPlan.commissioned_capacity": "ASSET_CLASS_CAPACITY_UNIT",
    "ProjectDevelopmentPlan.completion_year": "SIM_YEAR",
    "ProjectDevelopmentPlan.required_cost": "MODEL_CURRENCY",
    "ProjectDevelopmentPlan.stage_schedule": "SIM_YEAR_AND_MODEL_CURRENCY_SCHEDULE",
    "PublicInformationArtifact.year": "SIM_YEAR",
    "PublicationRequest.year": "SIM_YEAR",
    "ResolutionExposureRecord.allocation_fraction": "DIMENSIONLESS_SHARE",
    "SaleDecision.offered_quantity": "FIELD:SaleDecisionRequest.quantity_unit",
    "SaleDecisionRequest.year": "SIM_YEAR",
    "ScenarioResource.accessible": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.in_situ": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.recoverable": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScenarioResource.remaining": "MODEL_RESOURCE_UNIT_BY_FAMILY",
    "ScheduledEvent.effective_time": "SIM_TIME",
    "SettlementInfrastructurePlan.habitat_capacity": "PEOPLE_EQUIVALENT",
    "SettlementInfrastructurePlan.infrastructure_cost": "MODEL_CURRENCY",
    "SettlementInfrastructurePlan.year": "SIM_YEAR",
    "SettlementInfrastructureRecord.cost": "MODEL_CURRENCY",
    "SettlementInfrastructureRecord.habitat_capacity_added": "PEOPLE_EQUIVALENT",
    "SettlementInfrastructureRecord.habitat_capacity_after": "PEOPLE_EQUIVALENT",
    "SettlementInfrastructureRecord.habitat_capacity_before": "PEOPLE_EQUIVALENT",
    "SettlementInfrastructureRecord.infrastructure_after": "MODEL_CURRENCY",
    "SettlementInfrastructureRecord.infrastructure_before": "MODEL_CURRENCY",
    "SettlementInfrastructureRecord.year": "SIM_YEAR",
    "SettlementStageRecord.external_subsidy": "MODEL_CURRENCY",
    "SettlementStageRecord.habitat_capacity": "PEOPLE_EQUIVALENT",
    "SettlementStageRecord.infrastructure": "MODEL_CURRENCY",
    "SettlementStageRecord.population": "PEOPLE_EQUIVALENT",
    "SettlementStageRecord.production_capacity": "ASSET_CLASS_CAPACITY_UNIT",
    "SettlementStageRecord.productive_capital": "MODEL_CURRENCY",
    "SettlementStageRecord.year": "SIM_YEAR",
    "SettlementSupportDecision.authorized_residents": "REQUEST_POPULATION_UNIT",
    "SettlementSupportDecision.support_amount": "REQUEST_CURRENCY_UNIT",
    "SettlementSupportExecutionRecord.authorized_residents": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.earth_population_after": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.earth_population_before": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.offworld_population_after": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.offworld_population_before": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.subsidy_after": "MODEL_CURRENCY",
    "SettlementSupportExecutionRecord.subsidy_before": "MODEL_CURRENCY",
    "SettlementSupportExecutionRecord.support_amount": "MODEL_CURRENCY",
    "SettlementSupportExecutionRecord.total_population_after": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.total_population_before": "PEOPLE_EQUIVALENT",
    "SettlementSupportExecutionRecord.year": "SIM_YEAR",
    "SettlementSupportRequest.requested_residents": "FIELD:SettlementSupportRequest.population_unit",
    "SettlementSupportRequest.support_cost": "FIELD:SettlementSupportRequest.currency_unit",
    "SettlementSupportRequest.year": "SIM_YEAR",
    "SponsorProjectDecision.requested_financing": "REQUEST_CURRENCY_UNIT",
    "SponsorProjectDecisionRequest.year": "SIM_YEAR",
    "SurfaceProspectingModel.agent_detection_rate": "PROBABILITY",
    "SurfaceProspectingModel.agent_false_positive_rate": "PROBABILITY",
    "SurfaceProspectingModel.remote_world_false_negative_reference": "PROBABILITY",
    "SurfaceProspectingModel.remote_world_false_positive_reference": "PROBABILITY",
    "SurfaceProspectingModel.world_false_negative": "PROBABILITY",
    "SurfaceProspectingModel.world_false_positive": "PROBABILITY",
    "SurfaceProspectingWorldRecord.deterministic_draw": "UNIT_INTERVAL_DRAW",
    "SurfaceProspectingWorldRecord.world_false_negative": "PROBABILITY",
    "SurfaceProspectingWorldRecord.world_false_positive": "PROBABILITY",
    "SurfaceProspectingWorldRecord.year": "SIM_YEAR",
    "SurplusDistributionDecision.financier_return": "FIELD:SurplusDistributionRequest.currency_unit",
    "SurplusDistributionDecision.local_reinvestment": "FIELD:SurplusDistributionRequest.currency_unit",
    "SurplusDistributionDecision.owner_distribution": "FIELD:SurplusDistributionRequest.currency_unit",
    "SurplusDistributionDecision.reserve": "FIELD:SurplusDistributionRequest.currency_unit",
    "SurplusDistributionRecord.closing_project_cash": "MODEL_CURRENCY",
    "SurplusDistributionRecord.financier_return": "MODEL_CURRENCY",
    "SurplusDistributionRecord.local_reinvestment": "MODEL_CURRENCY",
    "SurplusDistributionRecord.opening_project_cash": "MODEL_CURRENCY",
    "SurplusDistributionRecord.owner_distribution": "MODEL_CURRENCY",
    "SurplusDistributionRecord.reserve": "MODEL_CURRENCY",
    "SurplusDistributionRecord.year": "SIM_YEAR",
    "SurplusDistributionRequest.year": "SIM_YEAR",
    "TechnologyCapabilityState.effective_from": "SIM_TIME",
    "TechnologyCapabilityState.effective_to": "SIM_TIME",
    "Transaction.amount": "MODEL_CURRENCY",
    "Transaction.year": "SIM_YEAR",
    "TransportQualificationRecord.effective_time": "SIM_TIME",
    "TransportRelationship.capacity": "PEOPLE_EQUIVALENT",
    "TransportRelationship.cost_per_passenger": "MODEL_CURRENCY_PER_PERSON",
    "TransportRelationship.effective_from": "SIM_TIME",
    "TransportRelationship.effective_to": "SIM_TIME",
    "TransportRelationship.energy_per_passenger": "MODEL_ENERGY_PER_PERSON",
    "TransportRelationship.loss_risk": "PROBABILITY",
    "TransportRelationship.travel_time": "SIM_TIME_DURATION",
    "TransportSettlementDecision.arrival_time": "SIM_TIME",
    "TransportSettlementDecision.authorized_residents": "REQUEST_POPULATION_UNIT",
    "TransportSettlementDecision.departure_time": "SIM_TIME",
    "TransportSettlementDecision.support_amount": "REQUEST_CURRENCY_UNIT",
    "TransportSettlementDecision.transport_amount": "REQUEST_CURRENCY_UNIT",
    "TransportSettlementRequest.departure_time": "SIM_TIME",
    "TransportSettlementRequest.requested_residents": "FIELD:TransportSettlementRequest.population_unit",
    "TransportSettlementRequest.support_cost": "FIELD:TransportSettlementRequest.currency_unit",
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
