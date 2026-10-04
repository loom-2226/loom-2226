from __future__ import annotations
from decimal import Decimal as D

from .build5_sale_market_fixture import sale_market_kernel
from .distribution import FinancingReturnClaim
from .distribution_protocol import build_surplus_distribution_request
from .model import AccountKind
from .mvp_state import SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .underwriting import UnderwritingInputKind

RESEARCH_ADVISORY_REF=(
    'loom-2226/loom-research-lab@a47d53ce1bd06453fe4d19eeab7abbc56f924527:'
    'projects/offworld_resource_economic_coupling/RESEARCH_BRIEF_v0.1.md'
)

def surplus_distribution_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                                demand_quantity='4',unit_price='20',
                                financier_return_claim='30',
                                reinvestment_requirement='10',
                                owners=None,
                                claim_project_id='P',
                                claim_destination_account='fin_funds',
                                sponsor_capabilities=(
                                    'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT',
                                    'SELL','DISTRIBUTE_SURPLUS')):
    k,h=sale_market_kernel(
        universe_id,stock,unit_price=unit_price,demand_quantity=demand_quantity,
        sponsor_capabilities=sponsor_capabilities)

    if owners is not None:
        parsed={str(owner):D(str(share)) for owner,share in owners.items()}
        if sum(parsed.values(),D('0'))!=D('1'):
            raise ValueError('fixture owners must sum to one')
        k.state.projects['P'].owners=parsed

    k.add_account(
        'local_reinvest_funds','SPN','OFF:T1',AccountKind.FUNDS,D('0'))
    k.add_system(SystemState(
        'SURPLUS_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState(
        'SURPLUS_DISTRIBUTION_SYSTEM','PROJECT_SURPLUS_DISTRIBUTION',
        {'accounts','transactions','surplus_distribution_records','events'}))

    claim=FinancingReturnClaim(
        'FRC-010A-1','FIN',claim_project_id,claim_destination_account,
        D(financier_return_claim),
        ('C-SPONSOR-005A','C-OPERATING-008A'),
        'TEST_ONLY:BUILD5_TEST010A_FINANCING_RETURN_CLAIM|ADVISORY_RESEARCH:'+RESEARCH_ADVISORY_REF,
        'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
    k.register_financing_return_claim(claim)

    op_cost=h['operating_table'].get(
        'GENERIC_RESOURCE_PROJECT_MVP',
        UnderwritingInputKind.OPERATING_COST).value
    reserve_requirement=D(h['operating_capacity'])*D(op_cost)

    h['financing_return_claim']=claim
    h['reserve_requirement']=reserve_requirement
    h['reinvestment_requirement']=D(reinvestment_requirement)
    return k,h

def surplus_snapshot_facts(k,h,project_id='P',
                           reserve_unknown=False,claim_unknown=False,
                           reinvest_unknown=False,
                           status_override=None,cash_override=None,
                           reserve_override=None,claim_override=None,
                           reinvest_override=None):
    p=k.state.projects[project_id]
    cash=D(k.state.accounts[p.cash_account_id].balance)
    if cash_override is not None:
        cash=D(cash_override)
    reserve=D(h['reserve_requirement']) if reserve_override is None else D(reserve_override)
    claim_remaining=k.financing_return_remaining(h['financing_return_claim'].id)
    if claim_override is not None:
        claim_remaining=D(claim_override)
    reinvest=D(h['reinvestment_requirement']) if reinvest_override is None else D(reinvest_override)
    status=p.status if status_override is None else str(status_override)
    return (
        SnapshotFact(
            'project.STATUS',FactState.KNOWN,status,
            f'PROJECT:{project_id}:STATUS'),
        SnapshotFact(
            'project.CASH_BALANCE',FactState.KNOWN,str(cash),
            f'PROJECT:{project_id}:ACCOUNT:{p.cash_account_id}:BALANCE'),
        SnapshotFact(
            'project.RESERVE_REQUIREMENT',
            FactState.UNKNOWN if reserve_unknown else FactState.KNOWN,
            None if reserve_unknown else str(reserve),
            f'TEST010A:NEXT_OPERATING_CYCLE:capacity={h["operating_capacity"]}:reserve={h["reserve_requirement"]}'),
        SnapshotFact(
            'financing.RETURN_CLAIM_REMAINING',
            FactState.UNKNOWN if claim_unknown else FactState.KNOWN,
            None if claim_unknown else str(claim_remaining),
            f'CLAIM:{h["financing_return_claim"].id}:{h["financing_return_claim"].fingerprint()}'),
        SnapshotFact(
            'project.REINVESTMENT_REQUIREMENT',
            FactState.UNKNOWN if reinvest_unknown else FactState.KNOWN,
            None if reinvest_unknown else str(reinvest),
            'TEST_ONLY:BUILD5_TEST010A_LOCAL_REINVESTMENT_REQUIREMENT'),
    )

def surplus_snapshot(k,h,period_key='SURPLUS-10',effective_time='10',**kw):
    return build_decision_snapshot(
        k,'SPN',period_key,D(str(effective_time)),
        surplus_snapshot_facts(k,h,**kw))

def surplus_request(claim_id='FRC-010A-1',
                    request_id='DISTREQ-010A-1',year=10):
    return build_surplus_distribution_request(
        request_id,year,'P',claim_id)
