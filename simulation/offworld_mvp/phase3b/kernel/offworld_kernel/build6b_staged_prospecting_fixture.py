from __future__ import annotations

from decimal import Decimal as D

from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .project_activity import ProjectActivity
from .project_study import (
    ProjectStudyMaturity,
    ProjectStudyPlan,
    ProjectStudyState,
    build_project_study_review_request,
)
from .build6a_temporal_multiproject_fixture import (
    portfolio_request,
    portfolio_snapshot,
)


def staged_prospecting_kernel():
    rid=RunIdentity(
        'BUILD6B_TEST001A','v1','SYNTH_BUILD6B_TEST001A',
        'BUILD6B_STAGED_PROSPECTING',
        (('standing','STRUCTURAL_ONLY'),)
    )
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)

    k.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,D('150'))
    k.add_account('study_supplier','VENDOR','EARTH:X',AccountKind.SUPPLIER,D('0'))

    for tag in ('A','B','C'):
        aid=f'project_cash_{tag}'
        pid=f'P-{tag}'
        k.add_account(aid,'SPN','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
        k.add_project(pid,'OFF:T1',aid,{'SPN':D('1')})
        k.state.projects[pid].status='EXPLORING'
        k.register_project_study_state(
            ProjectStudyState(pid,ProjectStudyMaturity.SCREENED))

    sponsor=AgentState(
        'SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY','REVIEW_STUDY'},
        objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    k.add_agent(sponsor)

    for year in range(1,11):
        k.set_resource_constraint('EARTH:X',year,D('1000'),D('1'))

    systems=(
        SystemState('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState('PROJECT_STUDY_AUTHORIZER','PROJECT_STUDY_AUTHORIZATION',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_STUDY_STARTER','PROJECT_STUDY_START',
                    {'project_activities','activity_transitions','project_study_expense'}),
        SystemState('PROJECT_STUDY_COMPLETER','PROJECT_STUDY_COMPLETION',
                    {'project_activities','activity_transitions','project_study_results'}),
        SystemState('PROJECT_STUDY_CANCELLER','PROJECT_STUDY_CANCELLATION',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',
                    {'agent_information','activity_information'}),
        SystemState('STUDY_REVIEW_ORCHESTRATOR','STUDY_REVIEW_DECISION',set()),
        SystemState('STUDY_REVIEW_EXECUTOR','STUDY_REVIEW_EXECUTION',
                    {'project_study_state','projects','study_review_records'}),
    )
    for x in systems:
        k.add_system(x)

    activities=(
        # Large unspent reservation proving a blocked competing project, then cancellation.
        ProjectActivity(
            'ACT-B-WAIT','P-B','REMOTE_FOLLOWUP','SPN',1,D('1'),D('1'),D('80'),
            'REMOTE_CHARACTERIZATION_RESULT',
            opportunity_window_id='WINDOW-B-WAIT',window_open=D('3'),window_close=D('3.5')),
        # A progresses through multiple consecutive study stages.
        ProjectActivity(
            'ACT-A-REMOTE','P-A','REMOTE_FOLLOWUP','SPN',2,D('1'),D('1'),D('30'),
            'REMOTE_CHARACTERIZATION_RESULT'),
        ProjectActivity(
            'ACT-A-SURFACE','P-A','SURFACE_OR_SAMPLE_STUDY','SPN',1,D('2.7'),D('1.5'),D('25'),
            'SURFACE_CHARACTERIZATION_RESULT'),
        ProjectActivity(
            'ACT-A-ASSESS','P-A','RESOURCE_ASSESSMENT_STUDY','SPN',1,D('4.4'),D('1'),D('20'),
            'RESOURCE_ASSESSMENT_RESULT'),
        # C is initially capital blocked and later executes an insufficient study.
        ProjectActivity(
            'ACT-C-REMOTE','P-C','REMOTE_FOLLOWUP','SPN',3,D('1'),D('1'),D('50'),
            'REMOTE_CHARACTERIZATION_RESULT'),
        # B redesigns after cancellation, executes cheaply, and returns a negative result.
        ProjectActivity(
            'ACT-B-REDESIGN','P-B','REMOTE_FOLLOWUP_REDESIGN','SPN',1,D('1.5'),D('1'),D('20'),
            'REMOTE_CHARACTERIZATION_RESULT'),
    )
    for a in activities:
        k.register_project_activity(a)

    plans=(
        ProjectStudyPlan(
            'PLAN-B-WAIT','ACT-B-WAIT','P-B',
            ProjectStudyMaturity.SCREENED,ProjectStudyMaturity.REMOTE_CHARACTERIZED,
            'study_supplier','REMOTE_CHARACTERIZATION_RESULT'),
        ProjectStudyPlan(
            'PLAN-A-REMOTE','ACT-A-REMOTE','P-A',
            ProjectStudyMaturity.SCREENED,ProjectStudyMaturity.REMOTE_CHARACTERIZED,
            'study_supplier','REMOTE_CHARACTERIZATION_RESULT'),
        ProjectStudyPlan(
            'PLAN-A-SURFACE','ACT-A-SURFACE','P-A',
            ProjectStudyMaturity.REMOTE_CHARACTERIZED,
            ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED,
            'study_supplier','SURFACE_CHARACTERIZATION_RESULT'),
        ProjectStudyPlan(
            'PLAN-A-ASSESS','ACT-A-ASSESS','P-A',
            ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED,
            ProjectStudyMaturity.RESOURCE_ASSESSMENT,
            'study_supplier','RESOURCE_ASSESSMENT_RESULT'),
        ProjectStudyPlan(
            'PLAN-C-REMOTE','ACT-C-REMOTE','P-C',
            ProjectStudyMaturity.SCREENED,ProjectStudyMaturity.REMOTE_CHARACTERIZED,
            'study_supplier','REMOTE_CHARACTERIZATION_RESULT'),
        ProjectStudyPlan(
            'PLAN-B-REDESIGN','ACT-B-REDESIGN','P-B',
            ProjectStudyMaturity.SCREENED,ProjectStudyMaturity.REMOTE_CHARACTERIZED,
            'study_supplier','REMOTE_CHARACTERIZATION_RESULT'),
    )
    for p in plans:
        k.register_project_study_plan(p)

    return k,{'activity_ids':tuple(a.id for a in activities)}


def study_review_snapshot(k,period_key,effective_time,activity_id,unknown_key=''):
    plan=k._project_study_plan_for_activity(activity_id)
    state=k.project_study_states[plan.project_id]
    project=k.state.projects[plan.project_id]
    results=[r for r in k.project_study_result_records if r.activity_id==activity_id]
    if len(results)!=1:
        raise RuntimeError('study review snapshot requires completed result')
    result=results[0]
    values={
        'project.STATUS':str(project.status),
        'study.CURRENT_MATURITY':state.maturity.value,
        'study.ACTIVITY_ID':activity_id,
        'study.RESULT_REF':result.result_ref,
        'study.RESULT_STANDING':result.standing.value,
        'study.NEXT_MATURITY':plan.next_maturity.value,
    }
    facts=tuple(
        SnapshotFact(
            key,
            FactState.UNKNOWN if key==unknown_key else FactState.KNOWN,
            None if key==unknown_key else value,
            f'BUILD6B:STUDY_REVIEW:{activity_id}:{key}'
        )
        for key,value in values.items()
    )
    return build_decision_snapshot(
        k,'SPN',str(period_key),D(str(effective_time)),facts)


def study_review_request(request_id,k,activity_id):
    a=k.project_activities[activity_id]
    return build_project_study_review_request(
        request_id,a.project_id,activity_id,a.result_ref)
