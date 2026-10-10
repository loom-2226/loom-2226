"""One-year continuation of the financed lunar prospecting project; no new machinery."""
from hashlib import sha256
from decimal import Decimal as D
import uuid
import psycopg
from simulation.offworld_mvp.build7 import runtime_flow as flow
from simulation.offworld_mvp.build7 import generated_campaign as campaign
from offworld_kernel.project_study import region_study_activity_id
from offworld_kernel import policy_runner as workers
from simulation.offworld_mvp.build7.generated_campaign import ProspectingRegionBinding
from .replay_lunar_allocation_trial import replay_observed


def run():
    k,h,choice,opportunities=replay_observed()
    opportunity=sorted(opportunities,key=lambda o:o.opportunity_id)[0]
    h['agent_logins'].update(campaign._agent_logins(('agent_pub','agent_spn','agent_fin')))
    decision,creation=campaign._execute_annual_prospecting_investment(k,h,2026,opportunity,'runtime',h['named_binding'])
    if creation is None: raise AssertionError('No financed lunar project')
    pid=creation.project_id
    campaign._record_empty_year(k,h,2027)
    with psycopg.connect(service='runtime') as conn:
        scenario_id,world_id,body_id=campaign.store.read_run_body_world_identity(conn,k.boundary_manifest.run_id,creation.body_key)
    h['named_binding']=ProspectingRegionBinding(scenario_id,world_id,body_id,creation.body_key,
        'PROSPECTING_REGION:'+sha256(pid.encode()).hexdigest()[:20],creation.region_key,uuid.UUID(str(creation.location_id)))
    flow.system_epoch(k,h,'initialize_region_study','2',(2,pid,creation.location_id))
    activity_id=region_study_activity_id(pid)
    activity=k.project_activities[activity_id]
    request=campaign.build_sponsor_portfolio_request('B8:PORTFOLIO:2027',2,(activity_id,))
    portfolio,ref=flow.policy_epoch(k,h,'B8_PORTFOLIO_2027','SPN','2',request,
        request.required_fact_keys,workers.run_sponsor_portfolio_policy,
        workers.sponsor_portfolio_policy_version(),{'project_id':pid})
    if portfolio.outcome.value=='AUTHORIZE':
        flow.system_epoch(k,h,'authorize_project_study_activity','2',(2,portfolio),decision_refs=(ref,))
        flow.system_epoch(k,h,'start_project_activity','2',(2,activity_id),decision_refs=(ref,))
        flow.system_epoch(k,h,'spend_project_study_activity','2',(2,activity_id,'PROJECT'),decision_refs=(ref,))
    k.assert_invariants()
    result=(pid,portfolio.outcome.value,k.project_activities[activity_id].status.value,
        str(k.state.accounts[k.state.projects[pid].cash_account_id].balance),
        str(k.capital_coupling['USA']['F']),str(k.capital_coupling['USA']['X']))
    print('LUNAR_2027',result,flush=True)
    if portfolio.outcome.value!='AUTHORIZE':
        return result
    campaign._record_empty_year(k,h,2028)
    ref=next(r for r,(_,decision_id,_) in k._boundary_decisions.items()
        if decision_id==k.project_activities[activity_id].authorization_decision_id)
    observations,_=flow.system_epoch(k,h,'observe_region_study','3',
        (3,'SPN',creation.body_key,creation.location_id,pid,activity_id),decision_refs=(ref,))
    for observation in observations:
        belief_key='BODY:'+observation.body_id+':'+observation.question_ref
        flow.system_epoch(k,h,'update_agent_belief_from_observation','3',
            (3,'SPN',observation.id,belief_key,D('.80'),D('.20'),
             'BUILD7_REGION_MATERIAL_V1',campaign.AUTHORIZATION),decision_refs=(ref,))
    standing=campaign.classify_regional_material_observation(observations)
    result_ref='BUILD7:REGION_STUDY_RESULT:'+campaign.content_hash(
        (pid,tuple(o.id for o in observations)))[:24]
    flow.system_epoch(k,h,'complete_project_study_activity','3',
        (3,activity_id,standing.value,result_ref),decision_refs=(ref,))
    flow.system_epoch(k,h,'admit_project_activity_result','3',
        (3,activity_id,'SPN'),decision_refs=(ref,))
    k.assert_invariants()
    print('LUNAR_2028',{'project':pid,'standing':standing.value,
        'observations':len(observations),'activity_status':k.project_activities[activity_id].status.value,
        'result_records':len(k.project_study_result_records),
        'sponsor_beliefs':[(o.question_ref,str(k.agents['SPN'].beliefs.get('BODY:'+o.body_id+':'+o.question_ref))) for o in observations]},flush=True)
    campaign._record_empty_year(k,h,2029)
    review_request=campaign.build_project_study_review_request(
        'B8:STUDY_REVIEW:2029',pid,activity_id,result_ref)
    review,review_ref=flow.policy_epoch(k,h,'B8_STUDY_REVIEW_2029','SPN','4',
        review_request,review_request.required_fact_keys,
        workers.run_sponsor_study_review_policy,
        workers.sponsor_study_review_policy_version(),{'project_id':pid})
    if review.outcome.value in ('ADVANCE','DEFER','ABANDON'):
        flow.system_epoch(k,h,'execute_project_study_review','4',
            (4,review_request,review),decision_refs=(review_ref,))
    k.assert_invariants()
    print('LUNAR_2029',{'project':pid,'review':review.outcome.value,
        'project_status':k.state.projects[pid].status,
        'review_records':len(k.project_study_review_records)},flush=True)
    return result

if __name__=='__main__': run()
