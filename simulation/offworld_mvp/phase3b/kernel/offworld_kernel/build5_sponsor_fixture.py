from __future__ import annotations
from dataclasses import replace
from decimal import Decimal as D

from .build5_publication_fixture import publication_handoff_kernel
from .mvp_state import SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .sponsor_protocol import build_sponsor_project_request
from .underwriting import (
    UnderwritingInputKind,
    mvp_validation_underwriting_table,
)

def sponsor_operator_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                            sponsor_capabilities=('REQUEST_FINANCE','DEVELOP'),
                            sponsor_objectives=('RETURN',),
                            initial_project_cash='0'):
    k,pub_snapshot,pub_request,manifest,obs,wip,draw,before=publication_handoff_kernel(
        universe_id,stock)

    spn=k.agents['SPN']
    spn.capabilities=set(sponsor_capabilities)
    spn.objectives=tuple(sponsor_objectives)
    spn.decision_policy='SPONSOR_OPERATOR_V1'
    spn.beliefs['resource_exists']=D('0.20')
    spn.priors['resource_exists']=D('0.20')
    k.state.accounts['project_cash'].balance=D(initial_project_cash)

    # All decision/action systems needed by the bounded chain are registered
    # before the first decision epoch starts. Epoch mode correctly forbids
    # later structural mutation of the world object graph.
    for system in (
        SystemState('SPONSOR_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState('SPONSOR_ACTION_EXECUTOR','SPONSOR_ACTION_EXECUTION',
                    {'financing_requests','project_state','events'}),
        SystemState('FINANCE_DECISION_ORCHESTRATOR_SPONSOR','DECISION_ORCHESTRATION',set()),
        SystemState('FINANCE_EXECUTOR_SPONSOR','FINANCE_EXECUTION',
                    {'accounts','commitments'}),
    ):
        k.add_system(system)

    table=mvp_validation_underwriting_table()
    request=build_sponsor_project_request(
        'SPREQ-005A-1',1,'P','RES',obs.id)
    return k,pub_snapshot,pub_request,manifest,obs,wip,draw,table,request

def sponsor_snapshot_facts(k,table,project_id='P',year=1,
                           development_unknown=False):
    p=k.state.projects[project_id]
    cash=k.state.accounts[p.cash_account_id].balance
    dev=table.get('GENERIC_RESOURCE_PROJECT_MVP',
                  UnderwritingInputKind.DEVELOPMENT_CAPEX)
    return (
        SnapshotFact(
            'project.STATUS',FactState.KNOWN,str(p.status),
            f'PROJECT:{project_id}:STATUS'),
        SnapshotFact(
            'project.CASH_BALANCE',FactState.KNOWN,str(cash),
            f'PROJECT:{project_id}:ACCOUNT:{p.cash_account_id}:BALANCE'),
        SnapshotFact(
            'underwriting.DEVELOPMENT_CAPEX',
            FactState.UNKNOWN if development_unknown else FactState.KNOWN,
            None if development_unknown else str(dev.value),
            f'{table.table_id}:{dev.input_id}:{dev.source_or_rationale_ref}:{dev.unit}:basis_year={dev.basis_year}:valid={dev.valid_from}-{dev.valid_to}'),
    )

def sponsor_snapshot(k,table,period_key,effective_time,development_unknown=False):
    return build_decision_snapshot(
        k,'SPN',period_key,D(str(effective_time)),
        sponsor_snapshot_facts(k,table,development_unknown=development_unknown))

def sponsor_request_for_epoch(observation_id,request_id,year):
    return build_sponsor_project_request(
        request_id,year,'P','RES',observation_id)
