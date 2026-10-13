"""EXPERIMENTAL / NON-CANON / NON-RUNTIME-DEFAULT; result-triggered, not result-priced."""
from decimal import Decimal as D
from .nasa_moon_a1 import run as run_a1, LABEL
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import NodeKind
from offworld_kernel.mvp_state import AgentKind, AgentState, SystemState
from offworld_kernel.project_study import ProjectStudyState
from .route1_gate2 import run_gate2
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.project_activity import ProjectActivity
from offworld_kernel.project_study import ProjectStudyPlan
from offworld_kernel.named_portfolio import load_build6c_scenario
from tests.test_build6b_staged_prospecting import Build6BStagedProspectingTests

def run(carry_cap=None):
    if carry_cap not in (None,1): raise ValueError('only unlimited or 1x')
    nasa,_,moon=run_a1()
    a1=next(r for r in moon.project_study_result_records if r.activity_id=='MOON-A1-SURFACE')
    admitted=next(r for r in moon.project_activity_information_records if r.activity_id=='MOON-A1-SURFACE')
    review=next(r for r in moon.project_study_review_records if r.activity_id=='MOON-A1-SURFACE')
    if a1.standing.value!='SUPPORTS_ADVANCE' or review.outcome.value!='ADVANCE' or admitted.admitted_at!=D('2029.01') or review.effective_time!=D('2029.02'):
        raise RuntimeError('A1 evidence/review boundary not satisfied')
    evidence={'standing':a1.standing.value,'result_ref':a1.result_ref,
              'reviewed':True,'admitted_at':str(admitted.admitted_at),
              'review_at':str(review.effective_time),'6c_activity':'MOON-A1-SURFACE',
              '6c_scenario':load_build6c_scenario().scenario_sha256}
    # Gate 2 credits the 2029 Earth allocation BEFORE evaluating the sole A2
    # exception at ALREADY_PURCHASED, and lapses excess cash AFTER the decision.
    rows,earth=run_gate2(D('.25'),carry_cap=carry_cap,end_year=2030,
                          run_setting={'name':'nasa_a2','payload':evidence})
    follow=[r for r in rows if r['sponsor']=='NASA' and r['year']==2029]
    if len(follow)!=1: raise AssertionError('not exactly one A2 request')
    decision=follow[0]
    if decision['policy']!='APPROVE':
        raise RuntimeError('FINANCIER_REJECTED:'+decision['reason'])
    if not decision['disbursement']: raise RuntimeError('FINANCING_BLOCKED:'+decision['status'])
    amount=D(decision['authored_price'])
    if amount!=D('.300') or D(decision['available'])-D(decision['closing'])!=amount:
        raise AssertionError('Route 1 A2 disbursement not conserved')
    spec=load_build6c_scenario().activity('MOON-A2-ASSESS')
    units=amount*100
    if units!=spec.cost or units!=30: raise AssertionError('A2 conversion')
    # RECONSTRUCTION, NOT CONTINUATION: Route 1 is decided first. A2's
    # opening funds exist only on approval; no cash enters the A1 chain.
    scenario=load_build6c_scenario();binding=scenario.binding_for_body('MOON')
    maturity=moon.project_study_states[binding.project_id].maturity
    if maturity!=spec.required_maturity: raise AssertionError('A1 maturity not eligible')
    rid=RunIdentity('NASA_MOON_A2','v1',scenario.scenario_sha256,
        'EXPERIMENTAL_RECONSTRUCTION_NOT_CONTINUATION',
        (('standing','NON_CANON'),('currency',LABEL)))
    a2=MethodologyHardenedBuild4Kernel(rid)
    a2.add_node('EARTH:X',NodeKind.EARTH)
    a2.add_node(binding.node_id,NodeKind.OFFWORLD)
    a2.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,units)
    a2.add_account('study_supplier','VENDOR','EARTH:X',AccountKind.SUPPLIER,D(0))
    a2.add_account('project_cash_moon','SPN',binding.node_id,AccountKind.PROJECT_CASH,D(0))
    a2.add_project(binding.project_id,binding.node_id,'project_cash_moon',{'SPN':D(1)})
    a2.state.projects[binding.project_id].status=moon.state.projects[binding.project_id].status
    a2.register_project_study_state(ProjectStudyState(binding.project_id,maturity,
        review.decision_id))
    for rec in scenario.evidence_records:
        if rec.body_id=='MOON': a2.register_named_body_evidence(rec)
    a2.register_body_portfolio_binding(binding)
    sponsor=AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY','REVIEW_STUDY'},objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    a2.add_agent(sponsor)
    sponsor.information.update(moon.agents['SPN'].information)
    for year in range(2026,2032): a2.set_resource_constraint('EARTH:X',year,D('10000'),D(1))
    for sid,kind,writes in (
        ('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        ('PROJECT_STUDY_AUTHORIZER','PROJECT_STUDY_AUTHORIZATION',{'project_activities','activity_transitions'}),
        ('PROJECT_STUDY_STARTER','PROJECT_STUDY_START',{'project_activities','activity_transitions','project_study_expense'}),
        ('PROJECT_STUDY_COMPLETER','PROJECT_STUDY_COMPLETION',{'project_activities','activity_transitions','project_study_results'}),
        ('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',{'agent_information','activity_information'}),
        ('STUDY_REVIEW_ORCHESTRATOR','STUDY_REVIEW_DECISION',set()),
        ('STUDY_REVIEW_EXECUTOR','STUDY_REVIEW_EXECUTION',{'project_study_state','projects','study_review_records'})):
        a2.add_system(SystemState(sid,kind,writes))
    a2.audit('RECONSTRUCTION, NOT CONTINUATION',2029,
        experiment='result-triggered, not result-priced',
        funding_transaction=decision['disbursement'],opening_native_units=units,
        a1_result_ref=a1.result_ref,a1_standing=a1.standing.value,
        a1_review_decision=review.decision_id,a1_review_outcome=review.outcome.value,
        a1_maturity=maturity.value,a1_fingerprint=moon.fingerprint(),
        a1_admitted_information=tuple(sorted(moon.agents['SPN'].information)))
    a2.register_project_activity(ProjectActivity(spec.activity_id,spec.project_id,
        spec.activity_type,'SPN',spec.priority,spec.earliest_start,
        spec.duration_years,spec.cost,f'{spec.activity_type}_RESULT',
        opportunity_window_id=spec.opportunity_window_id,
        window_open=spec.window_open,window_close=spec.window_close))
    a2.register_project_study_plan(ProjectStudyPlan('PLAN:'+spec.activity_id,
        spec.activity_id,spec.project_id,spec.required_maturity,spec.next_maturity,
        'study_supplier',f'{spec.activity_type}_RESULT'))
    h=Build6BStagedProspectingTests();h.CHAIN='CHAIN-NASA-MOON-A2'
    h.portfolio_epoch(a2,'A2-AUTH','2029.03',(spec.activity_id,),'Q-NASA-A2',first=True)
    h.start_and_spend_epoch(a2,'A2-START',spec.activity_id,'2029.10')
    h.complete_and_admit_epoch(a2,'A2-COMP',spec.activity_id,'2030.60','2030.61',spec.result_standing)
    h.review_epoch(a2,'A2-REVIEW',spec.activity_id,'2030.62')
    a2.assert_methodology_invariants();moon.assert_methodology_invariants();earth.assert_invariants()
    spent_a1=sum((r.amount for r in moon.project_activity_expense_records),D(0))
    spent_a2=sum((r.amount for r in a2.project_activity_expense_records),D(0))
    if (spent_a1,spent_a2)!=(D(35),D(30)): raise AssertionError('separate expenses')
    if set(a2.project_activities)!={'MOON-A2-ASSESS'}: raise AssertionError('A2 isolation')
    if a2.state.accounts['sponsor_funds'].balance!=0: raise AssertionError('A2 unspent cash')
    if a2.project_study_result_records[0].standing.value!='INSUFFICIENT': raise AssertionError('A2 standing')
    if a2.project_activities[spec.activity_id].actual_completion!=D('2030.60'): raise AssertionError('A2 completion')
    if moon.project_study_result_records[0]!=a1: raise AssertionError('A1 mutated')
    if len([r for r in rows if r['sponsor']=='NASA' and r['disbursement']])!=2:
        raise AssertionError('unexpected funding request')
    return rows,earth,moon,a2,decision,evidence
