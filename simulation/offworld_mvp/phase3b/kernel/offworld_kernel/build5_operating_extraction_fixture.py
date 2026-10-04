from __future__ import annotations
from dataclasses import replace
from decimal import Decimal as D

from .build5_project_lifecycle_fixture import project_lifecycle_kernel
from .mvp_state import SystemState
from .operating_protocol import build_operating_cycle_request
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .underwriting import (
    UnderwritingInputKind,
    UnderwritingTable,
    mvp_validation_underwriting_table,
)

def operating_validation_underwriting_table():
    base=mvp_validation_underwriting_table()
    inputs=tuple(
        replace(
            x,
            source_or_rationale_ref=x.source_or_rationale_ref+':CARRIED_TEST008A',
            valid_to=20,
        )
        for x in base.inputs
    )
    return UnderwritingTable(
        'OFFWORLD_MVP_OPERATING_VALIDATION_V0_1','0.1',
        'PRE_CONTRACT_AUTHORED_SCENARIO',inputs
    ).validate()

def operating_extraction_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                                commissioned_capacity='5',
                                sponsor_capabilities=(
                                    'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT')):
    k,h=project_lifecycle_kernel(
        universe_id,stock,commissioned_capacity=commissioned_capacity,
        sponsor_capabilities=sponsor_capabilities)

    for system in (
        SystemState('OPERATING_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState(
            'OPERATING_ACTION_EXECUTOR','SPONSOR_OPERATING_ACTION',
            {'financing_requests','events'}),
        SystemState(
            'OPERATING_FINANCE_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState(
            'OPERATING_FINANCE_EXECUTOR','FINANCE_EXECUTION',
            {'accounts','commitments'}),
        SystemState(
            'OPERATING_COST_SYSTEM','OPERATING_COST_EXECUTION',
            {'accounts','transactions','resource_constraints','events','operating_cost_records'}),
        SystemState(
            'EXTRACTION_RESOLUTION_SYSTEM','RESOURCE_EXTRACTION_RESOLUTION',
            {'resources','colonies','events','extraction_resolution_records'}),
    ):
        k.add_system(system)

    # Test-only supplier capacity for one operating cycle.
    k.set_resource_constraint('EARTH:X',9,D('1000'),D('0.10'))

    h['operating_table']=operating_validation_underwriting_table()
    h['operating_capacity']=D(commissioned_capacity)
    return k,h

def operating_snapshot_facts(k,table,project_id='P',asset_id='MINE-P',
                             opex_unknown=False):
    p=k.state.projects[project_id]
    cash=k.state.accounts[p.cash_account_id].balance
    asset=k.state.assets[asset_id]
    opex=table.get('GENERIC_RESOURCE_PROJECT_MVP',UnderwritingInputKind.OPERATING_COST)
    return (
        SnapshotFact('project.STATUS',FactState.KNOWN,p.status,
                     f'PROJECT:{project_id}:STATUS'),
        SnapshotFact('project.CASH_BALANCE',FactState.KNOWN,str(cash),
                     f'PROJECT:{project_id}:ACCOUNT:{p.cash_account_id}:BALANCE'),
        SnapshotFact('asset.CAPACITY',FactState.KNOWN,str(asset.capacity),
                     f'ASSET:{asset_id}:CAPACITY:STRUCTURAL_TEST008A'),
        SnapshotFact(
            'underwriting.OPERATING_COST',
            FactState.UNKNOWN if opex_unknown else FactState.KNOWN,
            None if opex_unknown else str(opex.value),
            f'{table.table_id}:{opex.input_id}:{opex.source_or_rationale_ref}:{opex.unit}:basis_year={opex.basis_year}:valid={opex.valid_from}-{opex.valid_to}'),
    )

def operating_snapshot(k,table,period_key,effective_time,opex_unknown=False):
    return build_decision_snapshot(
        k,'SPN',period_key,D(str(effective_time)),
        operating_snapshot_facts(k,table,opex_unknown=opex_unknown))

def operating_request(observation_id,request_id,year):
    return build_operating_cycle_request(
        request_id,year,'P','RES','MINE-P',observation_id)
