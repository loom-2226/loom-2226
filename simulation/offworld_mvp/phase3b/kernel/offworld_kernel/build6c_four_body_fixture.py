from __future__ import annotations

from decimal import Decimal as D

from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, SystemState
from .project_activity import ProjectActivity
from .project_study import ProjectStudyPlan, ProjectStudyState
from .named_portfolio import load_build6c_scenario
from .build6a_temporal_multiproject_fixture import (
    portfolio_request,
    portfolio_snapshot,
)
from .build6b_staged_prospecting_fixture import (
    study_review_request,
    study_review_snapshot,
)


def four_body_portfolio_kernel():
    scenario=load_build6c_scenario()
    rid=RunIdentity(
        'BUILD6C_TEST001A','v1',scenario.scenario_sha256,
        'BUILD6C_FOUR_BODY_PORTFOLIO_2026_2041',
        (
            ('standing','STRUCTURAL_SCENARIO_NOT_EMPIRICALLY_VALIDATED'),
            ('calendar_reference',scenario.reference_calendar),
            ('scenario_sha256',scenario.scenario_sha256),
        )
    )
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    for binding in scenario.body_bindings:
        k.add_node(binding.node_id,NodeKind.OFFWORLD)

    k.add_account(
        'sponsor_funds',scenario.sponsor_id,'EARTH:X',
        AccountKind.FUNDS,scenario.opening_capital)
    k.add_account('study_supplier','VENDOR','EARTH:X',AccountKind.SUPPLIER,D('0'))

    for binding in scenario.body_bindings:
        cash_id=f"project_cash_{binding.body_id.lower()}"
        k.add_account(cash_id,scenario.sponsor_id,binding.node_id,AccountKind.PROJECT_CASH,D('0'))
        k.add_project(binding.project_id,binding.node_id,cash_id,{scenario.sponsor_id:D('1')})
        k.state.projects[binding.project_id].status='EXPLORING'
        k.register_project_study_state(
            ProjectStudyState(binding.project_id,binding.opening_maturity))

    for rec in scenario.evidence_records:
        k.register_named_body_evidence(rec)
    for binding in scenario.body_bindings:
        k.register_body_portfolio_binding(binding)

    sponsor=AgentState(
        scenario.sponsor_id,AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY','REVIEW_STUDY'},
        objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    k.add_agent(sponsor)
    for rec in scenario.evidence_records:
        sponsor.information.add(rec.evidence_id)

    for year in range(2026,2042):
        k.set_resource_constraint('EARTH:X',year,D('10000'),D('1'))

    systems=(
        SystemState('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState('PROJECT_STUDY_AUTHORIZER','PROJECT_STUDY_AUTHORIZATION',
                    {'project_activities','activity_transitions'}),
        SystemState('PROJECT_STUDY_STARTER','PROJECT_STUDY_START',
                    {'project_activities','activity_transitions','project_study_expense'}),
        SystemState('PROJECT_STUDY_COMPLETER','PROJECT_STUDY_COMPLETION',
                    {'project_activities','activity_transitions','project_study_results'}),
        SystemState('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',
                    {'agent_information','activity_information'}),
        SystemState('STUDY_REVIEW_ORCHESTRATOR','STUDY_REVIEW_DECISION',set()),
        SystemState('STUDY_REVIEW_EXECUTOR','STUDY_REVIEW_EXECUTION',
                    {'project_study_state','projects','study_review_records'}),
    )
    for system in systems:
        k.add_system(system)

    for spec in scenario.activity_specs:
        k.register_project_activity(ProjectActivity(
            spec.activity_id,spec.project_id,spec.activity_type,scenario.sponsor_id,
            spec.priority,spec.earliest_start,spec.duration_years,spec.cost,
            f'{spec.activity_type}_RESULT',
            opportunity_window_id=spec.opportunity_window_id,
            window_open=spec.window_open,window_close=spec.window_close,
        ))
        k.register_project_study_plan(ProjectStudyPlan(
            f'PLAN:{spec.activity_id}',spec.activity_id,spec.project_id,
            spec.required_maturity,spec.next_maturity,'study_supplier',
            f'{spec.activity_type}_RESULT',
        ))

    k.assert_methodology_invariants()
    return k,scenario


def body_terminal_report(k,scenario):
    rows=[]
    spent_by_project={}
    for rec in k.project_activity_expense_records:
        spent_by_project[rec.project_id]=spent_by_project.get(rec.project_id,D('0'))+D(rec.amount)
    for binding in sorted(scenario.body_bindings,key=lambda x:x.body_id):
        state=k.project_study_states[binding.project_id]
        activities=[
            a for a in k.project_activities.values()
            if a.project_id==binding.project_id
        ]
        rows.append({
            'body_id':binding.body_id,
            'project_id':binding.project_id,
            'project_status':str(k.state.projects[binding.project_id].status),
            'study_maturity':state.maturity.value,
            'spent':str(spent_by_project.get(binding.project_id,D('0'))),
            'activities':tuple(sorted((a.id,a.status.value) for a in activities)),
            'evidence_ids':binding.evidence_ids,
        })
    return tuple(rows)
