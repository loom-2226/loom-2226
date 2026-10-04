from __future__ import annotations
from decimal import Decimal as D

from .build5_surplus_distribution_fixture import surplus_distribution_kernel
from .enterprise import build_enterprise_review_request
from .mvp_state import SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot


def repeated_enterprise_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                               demand_quantity='4',unit_price='20',
                               sponsor_capabilities=(
                                   'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT',
                                   'SELL','DISTRIBUTE_SURPLUS','CLOSE_PROJECT')):
    k,h=surplus_distribution_kernel(
        universe_id,stock,demand_quantity=demand_quantity,unit_price=unit_price,
        sponsor_capabilities=sponsor_capabilities)
    k.add_system(SystemState(
        'ENTERPRISE_REVIEW_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState(
        'ENTERPRISE_REVIEW_EXECUTOR','ENTERPRISE_LIFECYCLE_REVIEW',
        {'projects','events','enterprise_review_records'}))
    # Test-only supplier capacity for later repeated cycles.
    k.set_resource_constraint('EARTH:X',11,D('1000'),D('0.10'))
    k.set_resource_constraint('EARTH:X',12,D('1000'),D('0.10'))
    return k,h


def enterprise_review_snapshot_facts(k,extraction_record,actual_unknown=False,
                                     status_override=None,planned_override=None,
                                     actual_override=None):
    status=k.state.projects[extraction_record.project_id].status if status_override is None else str(status_override)
    planned=D(extraction_record.planned_quantity) if planned_override is None else D(planned_override)
    actual=D(extraction_record.actual_extracted) if actual_override is None else D(actual_override)
    return (
        SnapshotFact('project.STATUS',FactState.KNOWN,status,
                     f'PROJECT:{extraction_record.project_id}:STATUS'),
        SnapshotFact('cycle.PLANNED_QUANTITY',FactState.KNOWN,str(planned),
                     f'EXTRACTION:{extraction_record.extraction_event_id}:PLANNED_QUANTITY'),
        SnapshotFact(
            'cycle.ACTUAL_OUTPUT',
            FactState.UNKNOWN if actual_unknown else FactState.KNOWN,
            None if actual_unknown else str(actual),
            f'EXTRACTION:{extraction_record.extraction_event_id}:ACTUAL_OUTPUT'),
    )


def enterprise_review_snapshot(k,extraction_record,period_key,effective_time,**kw):
    return build_decision_snapshot(
        k,'SPN',str(period_key),D(str(effective_time)),
        enterprise_review_snapshot_facts(k,extraction_record,**kw))


def enterprise_review_request(extraction_record,request_id,year):
    return build_enterprise_review_request(
        request_id,year,extraction_record.project_id,
        extraction_record.extraction_event_id)
