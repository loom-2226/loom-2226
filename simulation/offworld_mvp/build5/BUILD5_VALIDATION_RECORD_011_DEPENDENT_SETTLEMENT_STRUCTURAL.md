# Build 5 Validation Record 011 — Dependent Settlement Formation Test 011A

**Status:** STRUCTURAL PASS / PRE-CONTRACT / SINGLE-AUTHORITY / NOT_EMPIRICALLY_VALIDATED
**Date:** 2026-10-04
**Branch:** offworld-mvp-build5-settlement
**Authorization:** BUILD5_IMPLEMENTATION_AUTHORIZATION_011_DEPENDENT_SETTLEMENT_TEST011A.md
**Executable anchor:** e5038d34aac6cd0e9106a6ef0846b65a8a39b077
**FRD mutation:** NONE

## 1. Result

Build 5 now implements the first governed dependent-settlement formation path on top of the existing financing, project, extraction, sale, revenue and surplus-allocation chain.

Verified causal extension:

project revenue
-> sponsor local-reinvestment allocation
-> realized local infrastructure spending
-> habitat capacity
-> derived EXTRACTION_ENCLAVE
-> bounded public settlement-support decision
-> explicit public subsidy
-> conserved Earth-to-offworld migration
-> derived DEPENDENT_SETTLEMENT.

Settlement remains aggregate state.

No Settlement Agent, Household Agent, Worker Agent or Human Agent was introduced.

## 2. Research intake

Read-only advisory research:

- loom-2226/loom-research-lab
- commit 0057937bdbf9732e235a7d8d718d2466898d8740
- projects/offworld_population_labour_migration/RESEARCH_BRIEF_v0.1.md
- projects/offworld_settlement_infrastructure_operations/RESEARCH_BRIEF_v0.1.md

Standing of both sources:

RESEARCH / NON-CANON / NON-RUNTIME / NON-AUTHORITATIVE / NON-QUALIFICATION.

Research principles used:

- settlement is an AGGREGATE by default;
- population is conserved stock-flow state;
- direct aggregate migration is acceptable where transport is not yet the discriminating causal question;
- installed infrastructure creates capacity/opportunity but does not create population;
- stage labels summarize realized state and grant nothing;
- Level-A infrastructure stock is sufficient for this bounded MVP experiment;
- explicit persons, households, labour markets and infrastructure operators are not required.

Research not activated:

- cohorts;
- fertility/mortality;
- labour/skill matching;
- rotational workforce;
- in-transit population;
- detailed passenger transport;
- service/reliability networks;
- maintenance/backlog;
- settlement operator agency;
- DIVERSIFYING_SETTLEMENT;
- HANDOFF_CANDIDATE.

## 3. FRD preservation

Parent Test 010A head:

c2377227c28f906ff2fa6298277bca8e095e2f2a.

Mechanical diff against:

simulation/offworld_mvp/OFFWORLD_MVP_GUIDING_FRD.md

returned:

FRD_DIFF_LINES=0.

The executable ODD was updated because executable state/interfaces changed.

The guiding FRD was not modified.

## 4. Existing capital source

Test 011A does not invent settlement capital.

Test 010A already classifies 10 MODEL_CURRENCY as local reinvestment in the successful RICH and SPARSE cases.

That realized balance enters Test 011A as:

local_reinvest_funds = 10.

NULL reaches Test 011A with:

local_reinvest_funds = 0.

The difference is inherited from the prior economic history.

## 5. Settlement infrastructure plan

Immutable plan:

SETTLE-PLAN-011A.

Structural fixture:

- year = 11;
- node = OFF:T1;
- source = local_reinvest_funds;
- supplier = local_settlement_supplier;
- infrastructure cost = 10 MODEL_CURRENCY;
- habitat capacity = 10 PEOPLE_EQUIVALENT;
- standing = TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE.

Plan SHA-256:

ebd6f5d2fe33811a96473eccc1b621df56833e1a15ba09e4629cb551f4c7fd7c.

The cost/capacity relationship is not empirical habitat engineering.

## 6. Infrastructure realization

The deterministic settlement-infrastructure SYSTEM requires:

- target is an OFFWORLD node;
- source and supplier accounts exist at that node;
- plan values are valid;
- plan has not already installed;
- source account contains sufficient realized cash.

If funded:

- cash moves from local reinvestment funds to the local supplier;
- colony infrastructure stock increases by actual cost;
- habitat capacity increases by declared people-equivalent capacity;
- population and resource state do not change.

If unfunded:

- no transaction occurs;
- no infrastructure appears;
- no habitat capacity appears.

## 7. Colony state extension

ColonyState now includes:

habitat_capacity.

The field is aggregate realized capacity measured in PEOPLE_EQUIVALENT.

It is not a claim of detailed life-support reliability, occupancy quality or certified habitation outside the structural fixture.

## 8. Derived stage semantics

Test 011A introduces:

SETTLEMENT_STAGE_RULE_TEST011A_V0_1.

The rule is deliberately qualitative rather than a synthetic colony score.

PROSPECTING:

production_capacity <= 0.

EXTRACTION_ENCLAVE:

commissioned production capacity exists but the realized conditions for dependent settlement are not all satisfied.

DEPENDENT_SETTLEMENT:

- production_capacity > 0;
- resident population > 0;
- infrastructure > 0;
- habitat_capacity >= resident population;
- external_subsidy > 0.

The stage derivation reads realized state only.

It creates no people, money, infrastructure, resource or capability.

## 9. Productive-state aggregation

At stage evaluation, aggregate colony:

- productive_capital;
- production_capacity

are synchronized from already-realized PRODUCTIVE assets at the node.

Test 011A therefore reports the previously commissioned project facility rather than creating a second productive asset.

For qualification cases:

- productive capital = 60;
- production capacity = 5.

## 10. Public settlement Agent

The existing PUBLIC institutional Agent is reused.

Additional Test 011A capabilities:

- MIGRATE;
- SETTLEMENT_SUPPORT.

Additional objective:

- PUBLIC_SETTLEMENT.

No new public-institution class is created.

Settlement itself remains AGGREGATE.

## 11. Public policy identity

Policy:

PUBLIC_SETTLEMENT_V1.

Semantic version:

0.1.

Policy semantics:

BOUNDED_CAPACITY_AND_FUNDING_LIMITED_PUBLIC_SETTLEMENT_SUPPORT_V1.

Policy contract SHA-256:

c49da4338636a786696435af1d501dd9976bb30b930b1c0b4d0174048b74404b.

Policy version:

PUBLIC_SETTLEMENT_V1:0.1:e6dc3a54afbaae9130c2356d5fa8331a2aef5c7ba764f1f6e9c9ea526d59e4a5.

The policy contains no arbitrary probability or settlement-score threshold.

## 12. Settlement support decision contract

Immutable:

- SettlementSupportRequest;
- SettlementSupportDecision;
- SettlementSupportDecisionOutcome;
- SettlementSupportReasonCode.

Required admitted facts:

- settlement.STAGE;
- settlement.HABITAT_HEADROOM;
- settlement.REQUESTED_RESIDENTS;
- population.EARTH_AVAILABLE;
- settlement.PUBLIC_SUPPORT_COST.

Supported outcomes:

- AUTHORIZE;
- DEFER;
- BLOCKED_UNKNOWN.

## 13. Public policy semantics

The bounded public policy AUTHORIZEs only when:

- Agent kind = PUBLIC;
- objective includes PUBLIC_SETTLEMENT;
- capabilities include MIGRATE and SETTLEMENT_SUPPORT;
- stage = EXTRACTION_ENCLAVE;
- requested residents > 0;
- habitat headroom >= requested residents;
- Earth population >= requested residents;
- public balance covers declared support cost.

UNKNOWN required facts block before worker execution.

The policy itself mutates no world state.

## 14. Structural migration/support fixture

Test-only request:

- requested residents = 10;
- public support cost = 10 MODEL_CURRENCY.

Initial population ledger:

- Earth = 1000;
- OFF:T1 = 0;
- total = 1000.

The request is bounded by actual Test-only habitat capacity 10.

The values are not demographic forecasts or transport-capacity claims.

## 15. Support execution

For AUTHORIZE, the SYSTEM:

1. revalidates actual current habitat headroom;
2. revalidates actual current Earth population;
3. revalidates actual current public cash;
4. transfers public support to settlement_support using PUBLIC_SUBSIDY;
5. increases colony.external_subsidy by the same amount;
6. migrates exactly the authorized residents;
7. conserves total population;
8. re-derives settlement stage.

The migration event carries parent lineage to the settlement-support decision/request and subsidy transaction.

## 16. RICH qualification

Universe:

RICH_PUBLIC_3.

Epoch 11 infrastructure:

- outcome = INSTALLED;
- cost = 10;
- habitat capacity added = 10;
- infrastructure = 0 -> 10;
- habitat capacity = 0 -> 10;
- transaction = tx-000029.

Stage after infrastructure:

PROSPECTING -> EXTRACTION_ENCLAVE.

Aggregate productive state:

- productive capital = 60;
- production capacity = 5.

Public decision:

SETDEC-85192d0f74ff6abfaecb.

Outcome:

AUTHORIZE / SETTLEMENT_SUPPORT_AUTHORIZED.

Authorization:

- residents = 10;
- support = 10.

Execution:

- Earth population = 1000 -> 990;
- offworld population = 0 -> 10;
- total population = 1000 -> 1000;
- subsidy = 0 -> 10;
- subsidy transaction = tx-000032.

Final colony:

- population = 10;
- cash = 10;
- productive capital = 60;
- infrastructure = 10;
- habitat capacity = 10;
- production capacity = 5;
- external subsidy = 10;
- stage = DEPENDENT_SETTLEMENT.

Other final accounts:

- local_reinvest_funds = 0;
- local_settlement_supplier = 10;
- public_funds = 80;
- settlement_support = 10.

Resource state remains:

- remaining resource = 15;
- local resource inventory = 1.

## 17. SPARSE qualification

Universe:

SPARSE_PUBLIC_1.

Epoch 11:

- infrastructure outcome = INSTALLED;
- cost = 10;
- habitat capacity added = 10;
- infrastructure = 0 -> 10;
- habitat capacity = 0 -> 10.

Stage after infrastructure:

PROSPECTING -> EXTRACTION_ENCLAVE.

Public settlement decision is exactly the same decision identity as RICH:

SETDEC-85192d0f74ff6abfaecb.

Outcome:

AUTHORIZE 10 residents / 10 support.

Population:

- Earth = 1000 -> 990;
- offworld = 0 -> 10;
- total = 1000 -> 1000.

Final colony:

- population = 10;
- infrastructure = 10;
- habitat capacity = 10;
- productive capital = 60;
- production capacity = 5;
- external subsidy = 10;
- stage = DEPENDENT_SETTLEMENT.

SPARSE may therefore form the same bounded dependent settlement despite its less favorable resource/sale history because it still generated the explicit local reinvestment and retained operating reserve required by the fixture.

## 18. NULL qualification

Universe:

NULL_FP_1.

Prior Test 010A state contains:

local_reinvest_funds = 0.

Epoch 11 infrastructure attempt:

- outcome = BLOCKED_INSUFFICIENT_FUNDS;
- realized cost = 0;
- habitat capacity added = 0;
- infrastructure = 0 -> 0;
- habitat capacity = 0 -> 0;
- transaction = NONE.

Productive asset state still exists from the earlier false-positive development history:

- productive capital = 60;
- production capacity = 5.

Therefore stage derives:

PROSPECTING -> EXTRACTION_ENCLAVE.

This label does not imply economic success or population.

Public decision:

SETDEC-0de407796e6278ec8909.

Outcome:

DEFER / HABITAT_CAPACITY_LIMIT.

Authorization:

- residents = 0;
- support = 0.

No support execution record exists.

Final NULL colony:

- population = 0;
- cash = 0;
- infrastructure = 0;
- habitat capacity = 0;
- production capacity = 5;
- external subsidy = 0;
- stage = EXTRACTION_ENCLAVE.

Population remains:

- Earth = 1000;
- offworld = 0.

The NULL history cannot create a dependent settlement from an unfunded habitat plan.

## 19. Key causal result

RICH and SPARSE have identical public settlement-support decisions because their admitted settlement state at Epoch 12 is equivalent.

NULL legitimately diverges because prior realized economic history left it with:

- no local reinvestment funding;
- no installed infrastructure;
- no habitat headroom.

This divergence arises from realized post-decision history, not hidden-resource leakage.

## 20. Population conservation

For successful settlement support:

Earth_before - Earth_after
=
Offworld_after - Offworld_before
=
authorized residents.

And:

total_population_before = total_population_after.

RICH and SPARSE:

1000 = 990 + 10.

No births or deaths are modeled.

NULL:

1000 = 1000 + 0.

## 21. Financial conservation

RICH/SPARSE infrastructure:

local_reinvest_funds -10
local_settlement_supplier +10.

RICH/SPARSE public support:

public_funds -10
settlement_support +10.

No stage label creates money.

NULL infrastructure/support:

no qualifying transaction occurs.

## 22. Physical isolation

Infrastructure and settlement-support epochs do not change:

- scenario resource remaining;
- extracted local resource inventory;
- Earth market resource inventory.

Population movement does not create or destroy resource stock.

## 23. Hostile and falsification boundaries

Focused tests verify:

- insufficient local reinvestment cannot create infrastructure;
- duplicate installed plan is rejected;
- negative cost/capacity is rejected;
- wrong-node infrastructure account linkage is rejected;
- infrastructure execution changes no population/resource stock;
- stage rule cannot produce DEPENDENT_SETTLEMENT without residents;
- inadequate habitat capacity blocks dependent settlement;
- absent external support blocks dependent settlement;
- UNKNOWN habitat headroom blocks before worker;
- missing migration/support capabilities defers;
- insufficient public funds defers;
- request above habitat headroom defers;
- request above Earth population defers;
- policy evaluation alone mutates nothing;
- a forged authorization above real habitat headroom is rejected by the SYSTEM;
- support transaction uses PUBLIC_SUBSIDY;
- total population is exactly conserved;
- raw stage tampering is detected between epochs;
- raw habitat-capacity tampering is detected between epochs;
- raw population tampering is detected between epochs.

## 24. A1-A9

Both Test 011A epochs preserve A1 through A9 in RICH, SPARSE and NULL.

Epoch 11 validates local infrastructure spending or its blocked no-spend path.

Epoch 12 validates subsidy/migration or the no-support DEFER path.

Population conservation is additionally checked by SettlementSupportExecutionRecord and kernel population/colony reconciliation.

## 25. Twelve-epoch history

The integrated success history now contains:

1. public publication;
2. sponsor development-finance request;
3. financier development funding;
4. sponsor DEVELOP;
5. construction / commissioning;
6. sponsor operating-finance request;
7. financier operating funding;
8. OPERATE / OPEX / extraction;
9. sale / market clearing / project revenue;
10. surplus allocation / return / reinvestment / owner distribution;
11. settlement infrastructure realization / enclave-stage derivation;
12. public settlement support / migration / dependent-settlement derivation.

RICH:

Epoch 11 result:
c1464762987ca0a4c546ee0e07de3052a416bb6f8e285a72792c676d333a0b09.

Epoch 12 parent:
c1464762987ca0a4c546ee0e07de3052a416bb6f8e285a72792c676d333a0b09.

Epoch 12 terminal result:
98c802bf8773e1b3151d91e2843552335f9a1fc0c3ff45fc68984ede02e18b55.

SPARSE terminal result:
f64877618ac528ab15ec713e40eb4f904558a553ee082365c680435c48a00b9d.

NULL terminal result:
53de7b59754e2c527d9342b357081676f5e6ac195fcf9300176eec965926c1b8.

## 26. Deterministic replay

Repeated complete RICH, SPARSE and NULL histories reproduce exactly:

- all twelve decision-epoch records;
- infrastructure realization record;
- stage records;
- public settlement-support decision;
- support/migration record;
- population ledger;
- colony state;
- account balances;
- terminal methodology fingerprint.

Replay is exact.

## 27. Executable identity

Executable offworld_kernel source-tree SHA-256:

2ae8667bec9cf0e301ab4ee6af0ef76aa06d8b38f0b8c8de7f256623468f2739.

Git-object reconstructed source-tree SHA-256:

2ae8667bec9cf0e301ab4ee6af0ef76aa06d8b38f0b8c8de7f256623468f2739.

Commit/code linkage:

GIT_OBJECT_VERIFIED.

## 28. Regression result

Governed kernel suite command:

python3 -m unittest discover -s tests

Result at executable anchor:

266 tests executed; 266 passed in 309.492 seconds.

The Test 010A baseline contained 244 tests.

Test 011A contributes 22 focused settlement tests.

## 29. ODD standing

The executable ODD schema registry now includes:

- ColonyState.habitat_capacity;
- SettlementSupportRequest;
- SettlementSupportDecision;
- settlement support outcomes/reason codes;
- SettlementInfrastructurePlan;
- SettlementInfrastructureRecord;
- SettlementStageRecord;
- SettlementSupportExecutionRecord;
- PUBLIC_SUBSIDY transaction semantics;
- associated population/currency/capacity unit contracts.

ODD narrative records settlement as aggregate state, state-derived stage, and bounded public institutional migration support.

The FRD remains unchanged.

## 30. Transport boundary

Test 011A deliberately retains direct aggregate migration because transport is not yet the discriminating causal question.

It does not claim physically instantaneous passenger movement as a real-world model.

The separate FRD transport and technology gate remains unearned.

## 31. Not yet earned

Test 011A does not establish:

- transport cost/time/energy/risk/capacity;
- technology gating;
- in-transit population;
- rotation versus permanent-resident classes;
- labour/skill sufficiency;
- service delivery/reliability;
- maintenance;
- births/deaths;
- households;
- individual persons;
- DIVERSIFYING_SETTLEMENT;
- HANDOFF_CANDIDATE;
- long-term settlement survival;
- empirical habitat cost/capacity;
- demographic calibration;
- settlement forecast validity.

## 32. Standing

Current earned standing:

- SURPLUS / RETURN / REINVESTMENT / DISTRIBUTION TEST 010A: STRUCTURAL PASS;
- DEPENDENT SETTLEMENT FORMATION TEST 011A: STRUCTURAL PASS;
- SETTLEMENT REMAINS AGGREGATE: PASS;
- LOCAL REINVESTMENT -> REALIZED INFRASTRUCTURE: PASS;
- HABITAT CAPACITY IS REALIZED STATE: PASS;
- EXTRACTION_ENCLAVE DERIVED FROM STATE: PASS;
- PUBLIC SETTLEMENT-SUPPORT AGENT DECISION: PASS;
- PUBLIC SUBSIDY LEDGERING: PASS;
- EARTH -> OFFWORLD POPULATION CONSERVATION: PASS;
- DEPENDENT_SETTLEMENT DERIVED FROM STATE: PASS;
- NULL CANNOT BOOTSTRAP SETTLEMENT WITHOUT REINVESTMENT: PASS;
- STAGE LABEL CREATES NO CAPABILITY: PASS;
- A1-A9: PASS;
- CHAINED DETERMINISTIC REPLAY: PASS;
- FRD MUTATION: NONE;
- TRANSPORT / TECHNOLOGY GATING: UNEARNED;
- EMPIRICAL SETTLEMENT VALIDATION: UNEARNED;
- LONG-RUN SETTLEMENT FORECAST STATUS: UNEARNED.
