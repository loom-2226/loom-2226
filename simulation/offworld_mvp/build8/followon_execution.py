"""Build 8 only: opt-in reconstruction of ONE funded authored 6C activity.

The 6C opening balance is an execution representation of one already-debited
Route 1 disbursement, never another Earth capital source. Not continuation.
"""
from decimal import Decimal as D
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import AgentKind, AgentState, SystemState
from offworld_kernel.project_activity import ProjectActivity
from offworld_kernel.project_study import ProjectStudyPlan, ProjectStudyState
from offworld_kernel.named_portfolio import load_build6c_scenario
from tests.test_build6b_staged_prospecting import Build6BStagedProspectingTests

def execute_stage(sponsor,activity_id,disbursement,amount,funding_year,prior=None,
                  portfolio=None):
    """Execute an authored activity only after a real opt-in Route 1 disbursement."""
    if not disbursement:
        raise ValueError('unfunded execution prohibited')
    scenario=load_build6c_scenario() if portfolio is None else portfolio
    spec=scenario.activity(activity_id)
    binding=scenario.binding_for_body(spec.body_id)
    amount=D(amount)
    native=amount*100
    if native!=spec.cost:
        raise ValueError('funded amount differs from pinned 6C activity price')
    maturity=(prior['kernel'].project_study_states[binding.project_id].maturity
              if prior else binding.opening_maturity)
    if maturity!=spec.required_maturity:
        raise ValueError('preceding review did not earn required maturity')
    authorization=max(D(funding_year),prior['review'].effective_time if prior else D(funding_year))
    start=max(spec.earliest_start, authorization,
              spec.window_open if spec.window_open is not None else spec.earliest_start)
    if spec.window_close is not None and start>spec.window_close:
        raise ValueError('activity window missed')
    completion=start+spec.duration_years
    admission=completion+D('.01')
    review_time=completion+D('.02')
    rid=RunIdentity('FOLLOWON_'+sponsor.replace(' ','_')+'_'+activity_id,'v1',
        scenario.scenario_sha256,'EXPERIMENTAL_RECONSTRUCTION_NOT_CONTINUATION',
        (('standing','NON_CANON'),('currency','AUTHORED_TEST_ONLY_10M_USD_PER_6C_UNIT')))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node(binding.node_id,NodeKind.OFFWORLD)
    k.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,native)
    k.add_account('study_supplier','VENDOR','EARTH:X',AccountKind.SUPPLIER,D(0))
    k.add_account('project_cash','SPN',binding.node_id,AccountKind.PROJECT_CASH,D(0))
    k.add_project(binding.project_id,binding.node_id,'project_cash',{'SPN':D(1)})
    k.state.projects[binding.project_id].status=(
        prior['kernel'].state.projects[binding.project_id].status if prior else 'EXPLORING')
    k.register_project_study_state(ProjectStudyState(binding.project_id,maturity,
        prior['review'].decision_id if prior else ''))
    for rec in scenario.evidence_records:
        if rec.body_id==spec.body_id:
            k.register_named_body_evidence(rec)
    k.register_body_portfolio_binding(binding)
    agent=AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities={'AUTHORIZE_ACTIVITY','REVIEW_STUDY'},objectives=('RETURN',),
        decision_policy='SPONSOR_PORTFOLIO_V1')
    k.add_agent(agent)
    agent.information.update(prior['kernel'].agents['SPN'].information if prior
                             else binding.evidence_ids)
    for year in range(2026,2042):
        k.set_resource_constraint('EARTH:X',year,D('10000'),D(1))
    for sid,kind,writes in (
        ('PORTFOLIO_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        ('PROJECT_STUDY_AUTHORIZER','PROJECT_STUDY_AUTHORIZATION',
            {'project_activities','activity_transitions'}),
        ('PROJECT_STUDY_STARTER','PROJECT_STUDY_START',
            {'project_activities','activity_transitions','project_study_expense'}),
        ('PROJECT_STUDY_COMPLETER','PROJECT_STUDY_COMPLETION',
            {'project_activities','activity_transitions','project_study_results'}),
        ('PROJECT_ACTIVITY_INFORMATION_ADMISSION','PROJECT_ACTIVITY_INFORMATION_ADMISSION',
            {'agent_information','activity_information'}),
        ('STUDY_REVIEW_ORCHESTRATOR','STUDY_REVIEW_DECISION',set()),
        ('STUDY_REVIEW_EXECUTOR','STUDY_REVIEW_EXECUTION',
            {'project_study_state','projects','study_review_records'}),
    ):
        k.add_system(SystemState(sid,kind,writes))
    k.register_project_activity(ProjectActivity(spec.activity_id,spec.project_id,
        spec.activity_type,'SPN',spec.priority,spec.earliest_start,
        spec.duration_years,spec.cost,f'{spec.activity_type}_RESULT',
        opportunity_window_id=spec.opportunity_window_id,
        window_open=spec.window_open,window_close=spec.window_close))
    k.register_project_study_plan(ProjectStudyPlan('PLAN:'+spec.activity_id,
        spec.activity_id,spec.project_id,spec.required_maturity,spec.next_maturity,
        'study_supplier',f'{spec.activity_type}_RESULT'))
    k.audit('RECONSTRUCTION, NOT CONTINUATION',int(D(funding_year)),
        experiment='AUTHORED TEST_ONLY NON-CANON',
        injected_test_portfolio=portfolio is not None,
        sponsor=sponsor,body=spec.body_id,activity=activity_id,
        funding_transaction=disbursement,opening_native_units=native,
        prior_result_ref=prior['result'].result_ref if prior else None,
        prior_review_id=prior['review'].decision_id if prior else None,
        prior_fingerprint=prior['kernel'].fingerprint() if prior else None)
    h=Build6BStagedProspectingTests()
    h.CHAIN='CHAIN-FOLLOWON-'+sponsor+'-'+spec.body_id+'-'+spec.activity_id
    h.portfolio_epoch(k,'E-AUTH',str(authorization),
        (spec.activity_id,),'Q-FOLLOWON-'+spec.activity_id,first=True)
    h.start_and_spend_epoch(k,'E-START',spec.activity_id,str(start))
    h.complete_and_admit_epoch(k,'E-COMP',spec.activity_id,str(completion),
                               str(admission),spec.result_standing)
    h.review_epoch(k,'E-REVIEW',spec.activity_id,str(review_time))
    k.assert_methodology_invariants()
    if k.state.accounts['sponsor_funds'].balance!=0:
        raise AssertionError('stage did not exhaust its specifically funded balance')
    if sum((r.amount for r in k.project_activity_expense_records),D(0))!=native:
        raise AssertionError('execution cost not conserved')
    result=next(r for r in k.project_study_result_records if r.activity_id==activity_id)
    admitted=next(r for r in k.project_activity_information_records if r.activity_id==activity_id)
    reviewed=next(r for r in k.project_study_review_records if r.activity_id==activity_id)
    return {'kernel':k,'result':result,'admitted':admitted,'review':reviewed,
            'activity':activity_id,'sponsor':sponsor,'body':spec.body_id,
            'disbursement':disbursement,'amount':amount,
            'start':start,'completion':completion}

def admitted_evidence(stage):
    return {'activity_id':stage['activity'],
            'standing':stage['result'].standing.value,
            'result_ref':stage['result'].result_ref,
            'admitted_at':str(stage['admitted'].admitted_at),
            'review_at':str(stage['review'].effective_time),
            'review_outcome':stage['review'].outcome.value,
            'source_fingerprint':stage['kernel'].fingerprint()}


def route1_funding_handoff(row,sponsor,activity_id,prior=None,portfolio=None):
    # Sole Route 1 -> 6C execution handoff: assert a real matching transfer
    # before representing its disbursement as 6C opening funds. Never add
    # the second ledger's native units back into Route 1.
    if row.get('sponsor')!=sponsor or not row.get('disbursement'):
        raise ValueError('funded Route 1 sponsor/transaction mismatch')
    if 'year' not in row:
        raise ValueError('funding year is required for chronological handoff')
    return execute_stage(sponsor,activity_id,row['disbursement'],
                         row['authored_price'],row['year'],prior=prior,
                         portfolio=portfolio)
