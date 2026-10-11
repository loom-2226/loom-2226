"""EXPERIMENTAL / NON-CANON / NON-RUNTIME-DEFAULT: NASA -> Moon A1."""
from decimal import Decimal as D
from .route1_gate1 import run_gate1
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AgentKind, AgentState, SystemState
from offworld_kernel.project_activity import ProjectActivity
from offworld_kernel.project_study import ProjectStudyPlan, ProjectStudyState
from offworld_kernel.named_portfolio import load_build6c_scenario
from offworld_kernel.build6a_temporal_multiproject_fixture import portfolio_request, portfolio_snapshot
from offworld_kernel.build6b_staged_prospecting_fixture import study_review_request, study_review_snapshot
from tests.test_build6b_staged_prospecting import Build6BStagedProspectingTests

LABEL='AUTHORED_6C_CURRENCY_INTERPRETATION_10M_USD_PER_UNIT'

def run():
    rows,earth=run_gate1(D('.25'),scenario='B',project_price_override={'NASA':D('.350')})
    nasa=next(r for r in rows if r['sponsor']=='NASA')
    if nasa['policy']!='APPROVE':
        raise RuntimeError('FINANCIER_REJECTED:'+nasa['reason'])
    if nasa['status']!='FUNDED_PENDING_EXECUTOR' or not nasa['disbursement']:
        raise RuntimeError('FINANCING_BLOCKED:'+nasa['status']+':'+nasa['reason'])
    amount=D(nasa['authored_price'])
    if amount!=D('.350') or D(nasa['opening'])-D(nasa['closing'])!=amount:
        raise AssertionError('Route 1 NASA cash discrepancy')
    # The 6C SPN identifier is a local NASA execution alias, not another investor.
    scenario=load_build6c_scenario()
    binding=scenario.binding_for_body('MOON')
    spec=scenario.activity('MOON-A1-SURFACE')
    units=amount*D('100')
    if units!=spec.cost: raise AssertionError('conversion discrepancy')
    rid=RunIdentity('NASA_MOON_A1','v1',scenario.scenario_sha256,
        'EXPERIMENTAL_NASA_FUNDED_MOON_A1',(('standing','NON_CANON'),('currency',LABEL)))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node(binding.node_id,NodeKind.OFFWORLD)
    k.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,units)
    k.add_account('study_supplier','VENDOR','EARTH:X',AccountKind.SUPPLIER,D(0))
    k.add_account('project_cash_moon','SPN',binding.node_id,AccountKind.PROJECT_CASH,D(0))
    k.add_project(binding.project_id,binding.node_id,'project_cash_moon',{'SPN':D(1)})
    k.state.projects[binding.project_id].status='EXPLORING'
    k.register_project_study_state(ProjectStudyState(binding.project_id,binding.opening_maturity))
    for rec in scenario.evidence_records:
        if rec.body_id=='MOON': k.register_named_body_evidence(rec)
    k.register_body_portfolio_binding(binding)
    sponsor=AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY','REVIEW_STUDY'},objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    k.add_agent(sponsor)
    sponsor.information.update(binding.evidence_ids)
    for year in range(2026,2031): k.set_resource_constraint('EARTH:X',year,D('10000'),D(1))
    for sid,kind,writes in (
        ('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        ('PROJECT_STUDY_AUTHORIZER','PROJECT_STUDY_AUTHORIZATION',{'project_activities','activity_transitions'}),
        ('PROJECT_STUDY_STARTER','PROJECT_STUDY_START',{'project_activities','activity_transitions','project_study_expense'}),
        ('PROJECT_STUDY_COMPLETER','PROJECT_STUDY_COMPLETION',{'project_activities','activity_transitions','project_study_results'}),
        ('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',{'agent_information','activity_information'}),
        ('STUDY_REVIEW_ORCHESTRATOR','STUDY_REVIEW_DECISION',set()),
        ('STUDY_REVIEW_EXECUTOR','STUDY_REVIEW_EXECUTION',{'project_study_state','projects','study_review_records'})):
        k.add_system(SystemState(sid,kind,writes))
    k.register_project_activity(ProjectActivity(spec.activity_id,spec.project_id,
        spec.activity_type,'SPN',spec.priority,spec.earliest_start,
        spec.duration_years,spec.cost,f'{spec.activity_type}_RESULT',
        opportunity_window_id=spec.opportunity_window_id,
        window_open=spec.window_open,window_close=spec.window_close))
    k.register_project_study_plan(ProjectStudyPlan('PLAN:'+spec.activity_id,
        spec.activity_id,spec.project_id,spec.required_maturity,spec.next_maturity,
        'study_supplier',f'{spec.activity_type}_RESULT'))
    k.assert_methodology_invariants()
    if set(k.project_activities)!={'MOON-A1-SURFACE'}: raise AssertionError('activity isolation')
    h=Build6BStagedProspectingTests();h.CHAIN='CHAIN-NASA-MOON-A1'
    h.portfolio_epoch(k,'E-AUTH','2026.25',(spec.activity_id,),'Q-NASA-MOON',first=True)
    h.start_and_spend_epoch(k,'E-START',spec.activity_id,'2027.50')
    h.complete_and_admit_epoch(k,'E-COMP',spec.activity_id,'2029.00','2029.01',spec.result_standing)
    h.review_epoch(k,'E-REVIEW',spec.activity_id,'2029.02')
    k.assert_methodology_invariants()
    spent=sum((r.amount for r in k.project_activity_expense_records),D(0))
    if spent!=units or spent>D(35): raise AssertionError('study spend mismatch')
    if k.state.accounts['sponsor_funds'].balance!=0: raise AssertionError('SPN alias double balance')
    if 'MOON-A2-ASSESS' in k.project_activities: raise AssertionError('A2 registered')
    return nasa,earth,k
