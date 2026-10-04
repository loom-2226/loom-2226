from __future__ import annotations

from decimal import Decimal as D

from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .project_activity import (
    ProjectActivity,
    ProjectActivityStatus,
    build_sponsor_portfolio_request,
)


def temporal_multiproject_kernel():
    rid=RunIdentity(
        'BUILD6A_TEST001A','v1','SYNTH_BUILD6A_TEST001A',
        'BUILD6A_TEMPORAL_MULTIPROJECT',
        (('standing','STRUCTURAL_ONLY'),)
    )
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)

    k.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,D('100'))
    for tag in ('A','B','C'):
        aid=f'project_cash_{tag}'
        pid=f'P-{tag}'
        k.add_account(aid,'SPN','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
        k.add_project(pid,'OFF:T1',aid,{'SPN':D('1')})

    sponsor=AgentState(
        'SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY'},objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    k.add_agent(sponsor)

    for system in (
        SystemState('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState('PROJECT_ACTIVITY_AUTHORIZER','PROJECT_ACTIVITY_AUTHORIZATION',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_ACTIVITY_STARTER','PROJECT_ACTIVITY_START',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_ACTIVITY_COMPLETER','PROJECT_ACTIVITY_COMPLETION',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',
                    {'agent_information','activity_information'}),
    ):
        k.add_system(system)

    # Structural-only authored activities. Same body, generic projects.
    # A: immediate, large reservation, short duration.
    # C: smaller reservation but cannot start until a future opportunity window.
    # B: large reservation, initially blocked while A+C capital is committed.
    activities=(
        ProjectActivity(
            'ACT-A','P-A','GENERIC_PROSPECTING','SPN',1,D('1'),D('2'),D('60'),
            'GENERIC_INFORMATION_RESULT'),
        ProjectActivity(
            'ACT-B','P-B','GENERIC_PROSPECTING','SPN',3,D('1'),D('4'),D('60'),
            'GENERIC_INFORMATION_RESULT'),
        ProjectActivity(
            'ACT-C','P-C','GENERIC_PROSPECTING','SPN',2,D('1'),D('1'),D('30'),
            'GENERIC_INFORMATION_RESULT',
            opportunity_window_id='WINDOW-C',window_open=D('4'),window_close=D('4.5')),
    )
    for a in activities:
        k.register_project_activity(a)

    return k,{'activity_ids':tuple(a.id for a in activities)}


def portfolio_snapshot_facts(k,activity_ids,effective_time,unknown_key=''):
    t=D(str(effective_time))
    facts=[
        SnapshotFact(
            'portfolio.AVAILABLE_CAPITAL',FactState.KNOWN,
            str(k.project_activity_available_capital('SPN')),
            'BUILD6A:DERIVED:SPONSOR_ACCOUNT_MINUS_ACTIVE_ACTIVITY_RESERVATIONS')
    ]
    for aid in sorted(activity_ids):
        a=k.project_activities[aid]
        p=k.state.projects[a.project_id]
        window_valid=(not a.opportunity_window_id) or t<=D(a.window_close)
        values={
            f'activity.{aid}.PROJECT_ID':a.project_id,
            f'activity.{aid}.PROJECT_STATUS':str(p.status),
            f'activity.{aid}.STATUS':a.status.value,
            f'activity.{aid}.COMMITMENT':str(a.capital_commitment),
            f'activity.{aid}.PRIORITY':str(a.priority),
            f'activity.{aid}.WINDOW_VALID':'1' if window_valid else '0',
        }
        for key,value in values.items():
            facts.append(SnapshotFact(
                key,
                FactState.UNKNOWN if key==unknown_key else FactState.KNOWN,
                None if key==unknown_key else value,
                f'BUILD6A:ACTIVITY:{aid}:{key.rsplit(".",1)[-1]}'
            ))
    return tuple(facts)


def portfolio_snapshot(k,period_key,effective_time,activity_ids,unknown_key=''):
    return build_decision_snapshot(
        k,'SPN',str(period_key),D(str(effective_time)),
        portfolio_snapshot_facts(k,activity_ids,effective_time,unknown_key=unknown_key)
    )


def portfolio_request(request_id,effective_time,activity_ids):
    return build_sponsor_portfolio_request(
        request_id,D(str(effective_time)),tuple(activity_ids))
