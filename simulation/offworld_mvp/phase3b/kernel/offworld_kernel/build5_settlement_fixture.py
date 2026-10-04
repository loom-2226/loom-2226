from __future__ import annotations
from decimal import Decimal as D

from .build5_surplus_distribution_fixture import surplus_distribution_kernel
from .model import AccountKind
from .mvp_state import PopulationLedger, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .settlement import SettlementInfrastructurePlan
from .settlement_protocol import build_settlement_support_request

RESEARCH_POPULATION_REF=(
    'loom-2226/loom-research-lab@0057937bdbf9732e235a7d8d718d2466898d8740:'
    'projects/offworld_population_labour_migration/RESEARCH_BRIEF_v0.1.md'
)
RESEARCH_SETTLEMENT_REF=(
    'loom-2226/loom-research-lab@0057937bdbf9732e235a7d8d718d2466898d8740:'
    'projects/offworld_settlement_infrastructure_operations/RESEARCH_BRIEF_v0.1.md'
)

def settlement_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                      public_balance=None,earth_population=1000,
                      public_settlement_capabilities=True,
                      infrastructure_cost='10',habitat_capacity=10,
                      requested_residents=10,public_support_cost='10'):
    k,h=surplus_distribution_kernel(universe_id,stock)

    pub=k.agents['PUB']
    if public_settlement_capabilities:
        pub.capabilities.update({'MIGRATE','SETTLEMENT_SUPPORT'})
    pub.objectives=tuple(dict.fromkeys((*pub.objectives,'PUBLIC_SETTLEMENT')))
    if public_balance is not None:
        k.state.accounts['public_funds'].balance=D(public_balance)

    k.population=PopulationLedger(
        earth=int(earth_population),offworld={'OFF:T1':0})

    k.add_account(
        'local_settlement_supplier','LSETTLE_SUP','OFF:T1',
        AccountKind.SUPPLIER,D('0'))
    k.add_account(
        'settlement_support','SETTLEMENT','OFF:T1',
        AccountKind.FUNDS,D('0'))

    for system in (
        SystemState(
            'SETTLEMENT_INFRASTRUCTURE_SYSTEM','SETTLEMENT_INFRASTRUCTURE_REALIZATION',
            {'accounts','transactions','colonies','settlement_infrastructure_records','events'}),
        SystemState(
            'SETTLEMENT_STAGE_SYSTEM','SETTLEMENT_STAGE_DERIVATION',
            {'colonies','settlement_stage_records','events'}),
        SystemState(
            'SETTLEMENT_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState(
            'SETTLEMENT_SUPPORT_SYSTEM','PUBLIC_SETTLEMENT_SUPPORT',
            {'accounts','transactions','colonies','population',
             'settlement_support_records','settlement_stage_records','events'}),
    ):
        k.add_system(system)

    plan=SettlementInfrastructurePlan(
        'SETTLE-PLAN-011A',11,'OFF:T1',
        'local_reinvest_funds','local_settlement_supplier',
        D(infrastructure_cost),int(habitat_capacity),
        ('TEST_ONLY:BUILD5_TEST011A_SETTLEMENT_INFRASTRUCTURE_PLAN'
         +'|ADVISORY_POP:'+RESEARCH_POPULATION_REF
         +'|ADVISORY_SETTLEMENT:'+RESEARCH_SETTLEMENT_REF),
        'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
    k.register_settlement_infrastructure_plan(plan)

    h['settlement_infrastructure_plan']=plan
    h['requested_residents']=int(requested_residents)
    h['public_support_cost']=D(public_support_cost)
    return k,h

def settlement_support_facts(k,h,headroom_unknown=False,
                             stage_override=None,headroom_override=None,
                             requested_override=None,earth_override=None,
                             support_cost_override=None):
    c=k.colonies['OFF:T1']
    stage=c.stage if stage_override is None else str(stage_override)
    headroom=k.settlement_habitat_headroom('OFF:T1')
    if headroom_override is not None:
        headroom=int(headroom_override)
    requested=h['requested_residents']
    if requested_override is not None:
        requested=int(requested_override)
    earth=k.population.earth
    if earth_override is not None:
        earth=int(earth_override)
    support=D(h['public_support_cost'])
    if support_cost_override is not None:
        support=D(support_cost_override)
    return (
        SnapshotFact(
            'settlement.STAGE',FactState.KNOWN,stage,
            'SETTLEMENT_STAGE_RULE_TEST011A_V0_1'),
        SnapshotFact(
            'settlement.HABITAT_HEADROOM',
            FactState.UNKNOWN if headroom_unknown else FactState.KNOWN,
            None if headroom_unknown else str(headroom),
            f'COLONY:OFF:T1:HABITAT_CAPACITY={c.habitat_capacity}:POPULATION={c.population}'),
        SnapshotFact(
            'settlement.REQUESTED_RESIDENTS',FactState.KNOWN,str(requested),
            'TEST_ONLY:BUILD5_TEST011A_REQUESTED_RESIDENTS'),
        SnapshotFact(
            'population.EARTH_AVAILABLE',FactState.KNOWN,str(earth),
            'POPULATION_LEDGER:EARTH'),
        SnapshotFact(
            'settlement.PUBLIC_SUPPORT_COST',FactState.KNOWN,str(support),
            'TEST_ONLY:BUILD5_TEST011A_PUBLIC_SUPPORT_COST'),
    )

def settlement_support_snapshot(k,h,period_key='SETTLEMENT-12',
                                effective_time='12',**kw):
    return build_decision_snapshot(
        k,'PUB',period_key,D(str(effective_time)),
        settlement_support_facts(k,h,**kw))

def settlement_support_request(h,requested_residents=None,
                               request_id='SETREQ-011A-1',year=12):
    requested=h['requested_residents'] if requested_residents is None else int(requested_residents)
    return build_settlement_support_request(
        request_id,year,'OFF:T1','settlement_support',
        requested,h['public_support_cost'])
