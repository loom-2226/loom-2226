"""Build 7 forward-runtime orchestration over the existing qualified Offworld kernel.

This module contains only the narrow scheduling/policy composition needed by Build 7.
It deliberately does not import the historical Build 6E qualification fixture.
"""
from dataclasses import fields, is_dataclass, replace
from decimal import Decimal as D
from hashlib import sha256
from pathlib import Path
import json

from offworld_kernel.boundary import ConsumptionRequest, admit_for_use, snapshot_facts
from offworld_kernel.causal_trace import validate_trace
from offworld_kernel.policy import build_decision_snapshot
from offworld_kernel.scheduler import CouplingSpec, ScheduledEvent, Phase
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.accounting import AccountingPeriodSnapshot, AccountingIdentityAuditor
from offworld_kernel.mvp_state import RuntimeObjectClass
from offworld_kernel.policies.manifest import policy_source_bytes
from offworld_kernel import policy_runner as workers
from offworld_kernel.operating_protocol import build_operating_cycle_request
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.enterprise import build_enterprise_review_request

NODE_ID='__BUILD7_TARGET__'

OWNERS={
'add_commitment':('commitments',),'disburse':('accounts','transactions','commitments','earth_impact','events'),
'reserve_earth_supply':('resource_constraints',),
'explore_paid':('accounts','transactions','assets','observations','agents','events','resource_constraints','earth_impact'),
'surface_prospect_paid':('accounts','transactions','assets','observations','agents','events','resource_constraints','earth_impact','surface_prospecting_records'),
'update_agent_belief_from_observation':('agents','events','observation_belief_update_records'),
'publish_observation':('agents','public_information','events'),
'submit_financing_request':('financing_requests','events','agents'),
'transition_project_status':('projects','events','agents'),
'execute_development_stage':('projects','assets','accounts','transactions','wip','fcf','earth_impact','resource_constraints','events','development_stage_records','agents'),
'resolve_development_plan':('projects','wip','assets','events','development_resolution_records','agents'),
'spend_operating_cycle':('earth_impact','accounts','transactions','resource_constraints','events','operating_cost_records','agents'),
'resolve_operating_extraction':('resources','colonies','events','extraction_resolution_records','agents'),
'clear_market_sale':('accounts','transactions','colonies','market_resource_inventory','market_clearing_records','boundary_net','events','agents','earth_impact'),
'execute_surplus_distribution':('accounts','transactions','surplus_distribution_records','events','agents','earth_impact'),
'execute_settlement_infrastructure':('accounts','transactions','colonies','settlement_infrastructure_records','events','agents'),
'update_settlement_stage':('colonies','settlement_stage_records','events','agents'),
'execute_transport_settlement_departure':('accounts','transactions','colonies','population','passenger_transport_departures','events','agents','earth_impact'),
'execute_passenger_transport_arrival':('colonies','population','passenger_transport_arrivals','settlement_stage_records','events','agents','earth_impact'),
'execute_enterprise_review':('projects','events','enterprise_review_records','agents'),
'admit_realized_output_observation':('agents','events'),
'boundary_purchase':('accounts','transactions','market_resource_inventory','boundary_net','events','earth_impact'),
'assess_resource_recoverability':('resources','events'),'record_earth_reference_year':('events',),
}

LIVE={
'agent.STATE':('AGENT_STATE','SELF','TYPED_AGENT_STATE'),
'agent.BELIEF':('BELIEF','SELF','PROBABILITY'),'agent.PRIOR':('PRIOR','SELF','PROBABILITY'),
'observation.SIGNAL':('OBSERVATION','OBSERVATION','SIGNAL_CATEGORY'),
'information.ARTIFACT':('PUBLIC_INFORMATION','INFORMATION','TYPED_INFORMATION_ARTIFACT'),
'project.STATUS':('PROJECT:P:STATUS','P','STATUS_CATEGORY'),
'project.CASH_BALANCE':('PROJECT:P:CASH','P','MODEL_CURRENCY'),
'asset.CAPACITY':('ASSET:MINE-P:CAPACITY','P','MODEL_RESOURCE_UNIT_PER_CYCLE'),
'inventory.AVAILABLE':('COLONY:INVENTORY',NODE_ID,'MODEL_RESOURCE_UNIT_BY_FAMILY'),
'market.UNIT_PRICE':('MARKET:PRICE','MKT','MODEL_CURRENCY_PER_RESOURCE_UNIT'),
'market.REMAINING_DEMAND':('MARKET:DEMAND','MKT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
'financing.RETURN_CLAIM_REMAINING':('CLAIM','FRC','MODEL_CURRENCY'),
'settlement.STAGE':('COLONY:STAGE',NODE_ID,'STATUS_CATEGORY'),
'settlement.HABITAT_HEADROOM':('COLONY:HEADROOM',NODE_ID,'PERSON'),
'population.EARTH_AVAILABLE':('POPULATION','EARTH:USA','PERSON'),
'cycle.PLANNED_QUANTITY':('EXTRACTION_PLANNED','OUTPUT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
'cycle.ACTUAL_OUTPUT':('EXTRACTION_ACTUAL','OUTPUT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
}
for key,unit in [('AVAILABLE','BOOLEAN'),('RELATIONSHIP_ID','IDENTITY'),('CAPACITY','PERSON'),('COST_PER_PASSENGER','MODEL_CURRENCY_PER_PERSON'),('TRAVEL_TIME','SIM_TIME_DURATION'),('ENERGY_PER_PASSENGER','MODEL_ENERGY_PER_PERSON'),('LOSS_RISK','PROBABILITY')]:
    LIVE['transport.'+key]=('TRANSPORT:'+key,'TR-USA-BUILD7',unit)
LIVE['technology.STATE_ID']=('TRANSPORT:STATE_ID','TECH-BUILD7','IDENTITY')
LIVE['opportunity.NAMED_LOCATION']=('CATALOG:BODY','BODY','CATALOG_LOCATION_IDENTITY')
LIVE['opportunity.AUTHORED_SITE']=('SCENARIO_SITE',NODE_ID,'AUTHORED_SITE_IDENTITY')

_TEMPORAL_FIELDS=frozenset(('year','effective_time','departure_time','arrival_time','event_time','decision_time','authorization_time','realized_time'))
_SYSTEM_TIME_INDEX={'disburse':0,'reserve_earth_supply':1,'explore_paid':0,'surface_prospect_paid':0,
    'update_agent_belief_from_observation':0,'publish_observation':0,'transition_project_status':0,
    'execute_development_stage':0,'resolve_development_plan':0,'spend_operating_cycle':0,
    'resolve_operating_extraction':0,'admit_realized_output_observation':0,'clear_market_sale':0,
    'execute_surplus_distribution':0,'execute_settlement_infrastructure':0,'update_settlement_stage':0,
    'execute_enterprise_review':0,'assess_resource_recoverability':0,'record_earth_reference_year':0}

def _target_runtime(kernel):
    """Resolve the current campaign target without changing the frozen 6E defaults."""
    params=dict(kernel.boundary_manifest.parameters)
    node=params.get('build7.site_node_id',NODE_ID)
    return {
        'node':node,
        'site_ref':params.get('build7.site_ref','SITE:'+node),
        'catalog_subject':params.get('build7.catalog_subject','MOON:CABEU'),
        'catalog_scope':params.get('build7.catalog_scope','LOCATION:MOON:CABEU'),
    }

def policy_inputs(k,actor,time,concepts,subjects=None):
    subjects=subjects or {};receipts=[];target=_target_runtime(k)
    for concept in ('agent.STATE','agent.BELIEF','agent.PRIOR',*concepts):
        if concept in LIVE:
            _,subject,unit=LIVE[concept];subject=actor if subject=='SELF' else subject
            if subject==NODE_ID:subject=target['node']
            subject=subjects.get(concept,subject)
            scope='AGENT:'+actor if concept.startswith('agent.') else 'PROJECT:P' if subject=='P' else target['site_ref']
            if concept=='opportunity.NAMED_LOCATION':
                scope=target['catalog_scope'];subject=target['catalog_subject'];context='REAL';cid='';role='ADMITTED_CATALOG_IDENTITY'
            elif concept=='opportunity.AUTHORED_SITE':
                scope=target['site_ref'];subject=target['site_ref'];context='SCENARIO';cid=k.boundary_manifest.scenario_id;role='POLICY_PARAMETER'
            else:
                context='REALIZED';cid=k.boundary_manifest.run_id;role='ADMITTED_INFORMATION'
        else:
            a=next(x for x in k.boundary_manifest.assertions if x.assertion_id==actor+':'+concept)
            subject=a.subject_id;scope=a.scope;unit=a.unit;context='SCENARIO';cid=k.boundary_manifest.scenario_id;role='POLICY_PARAMETER'
        req=ConsumptionRequest(actor+':'+str(time)+':'+concept,actor,'POLICY',subject,concept,scope,'SIM_TIME',str(time),str(time),context,cid,'AGENT',actor,'ADMITTED',unit,role)
        receipts.append(admit_for_use(k,req)[1])
    return tuple(receipts)

def _shift_temporal_record(value,delta):
    if not delta or not is_dataclass(value):return value
    updates={}
    for f in fields(value):
        current=getattr(value,f.name)
        if f.name in _TEMPORAL_FIELDS and isinstance(current,(int,str,D)):
            updates[f.name]=type(current)(D(current)+delta) if type(current) is D else int(D(current)+delta) if type(current) is int else str(D(current)+delta)
        elif is_dataclass(current):updates[f.name]=_shift_temporal_record(current,delta)
    return replace(value,**updates) if updates else value

def _shift_method_arguments(method,args,delta):
    values=list(args)
    idx=_SYSTEM_TIME_INDEX.get(method)
    if delta and idx is not None and idx<len(values):
        v=values[idx]
        if isinstance(v,(int,str,D)):values[idx]=int(D(v)+delta) if type(v) is int else str(D(v)+delta) if type(v) is str else D(v)+delta
    # Only the explicit operation-time argument is mapped. Nested typed
    # requests/records keep their decision, source and realized timestamps.
    return tuple(values)

def _policy_epoch_body(k,h,label,actor,time,request,concepts,runner,version,subjects=None):
    h['counter']+=1;period=label
    delta=0 if label=='TRANSPORT' else int(h['params'].get('time_offset',0))
    time=str(D(time)+delta)
    # Map the request once into the same SIM decision clock as its window.
    # Later consequence events map their explicit operation-time argument;
    # nested requests/records must not be shifted a second time.
    request=_shift_temporal_record(request,delta)
    from offworld_kernel.boundary import BUILD6E_CONTRACT
    opening_epoch=(k.boundary_manifest.contract_version==BUILD6E_CONTRACT and not k._boundary_opening_validated)
    if opening_epoch:
        k.begin_decision_epoch(label,'BUILD6E_CORE_CHAIN' if k.decision_epoch_chain_id is None else None)
    receipts=policy_inputs(k,actor,time,concepts,subjects)
    snap=build_decision_snapshot(k,actor,period,D(time),snapshot_facts(k,receipts),admission_receipts=receipts)
    if not opening_epoch:
        k.begin_decision_epoch(label,'BUILD6E_CORE_CHAIN' if k.decision_epoch_chain_id is None else None)
    k.scheduler.register_coupling(CouplingSpec('DECISION','BUILD6E_V1',RuntimeObjectClass.SYSTEM,(),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
    ref=k.scheduler.open_decision_window(period,snap.fingerprint());eid=label+':decision'
    k.scheduler.schedule(ScheduledEvent(eid,D(time),Phase.DECISION_WINDOW,0,actor,'DECISION',snapshot_ref=ref))
    rt=ScheduledSimulationRuntime(k,strict_provenance(k,('UNDERWRITING:'+h['table'].fingerprint(),),(version,)))
    def policy(ctx):
        result=runner(ctx.snapshot,request,ctx.decision_key);h['policies'][label]=result;return result
    rt.register_policy_handler(eid,actor,snap,'B6E:'+label,policy,request=request,admission_receipts=receipts,expected_policy_version=version)
    before=AccountingPeriodSnapshot.capture(k,int(D(time)));rt.seal();h['results'].append(rt.run());h['audits'].append(AccountingIdentityAuditor(k,before).check_all())
    h['snapshots'][label]=snap;h['requests'][label]=request;h['last_time']=D(time)
    return h['policies'][label].decision,next(ref for ref,(_,did,_) in k._boundary_decisions.items() if did==h['policies'][label].decision.id)

def policy_epoch(k,h,label,actor,time,request,concepts,runner,version,subjects=None):
    if not h.get('wa_service'):
        return _policy_epoch_body(k,h,label,actor,time,request,concepts,runner,version,subjects)
    from simulation.offworld_mvp.build6e.named_world import execute_persisted_epoch
    effective = D(time) + (0 if label=='TRANSPORT' else D(int(h['params'].get('time_offset',0))))
    result, status = execute_persisted_epoch(service_name=h['wa_service'], kernel=k,
        binding=h['named_binding'], epoch_id=label, effective_time=effective,
        agent_logins=h['agent_logins'],
        execute=lambda: _policy_epoch_body(k,h,label,actor,time,request,concepts,runner,version,subjects))
    h.setdefault('epoch_commits', []).append((label,status))
    return result

def _system_epoch_body(k,h,method,time,args=(),kwargs=None,decision_refs=()):
    delta=0 if method in ('execute_transport_settlement_departure','execute_passenger_transport_arrival') else int(h['params'].get('time_offset',0))
    time=str(D(time)+delta)
    args=_shift_method_arguments(method,args,delta)
    h['counter']+=1;label='ACTION:'+str(h['counter'])+':'+method;sid='SYS:'+method
    k.begin_decision_epoch(label,'BUILD6E_CORE_CHAIN' if k.decision_epoch_chain_id is None else None)
    owned=OWNERS[method]
    # Keep process identity as the existing system transition, while the
    # causal actor identifies the Agent whose typed decision authorizes it.
    # World Authority's frozen loop contract requires that exact principal
    # continuity; it must not infer an Agent from a system process later.
    authorized_actors=set()
    for decision_ref in decision_refs:
        decision=json.loads(k.causal_artifacts[decision_ref][1])['fields']['decision']
        actor=decision['fields'].get('actor_id',decision['fields'].get('financier_id',{})).get('value')
        if actor:authorized_actors.add(actor)
    if len(authorized_actors)>1:
        raise RuntimeError('BLOCKED_MULTIPLE_AUTHORIZING_AGENTS')
    event_actor=next(iter(authorized_actors),sid)
    event=ScheduledEvent(label,D(time),Phase.OPERATIONS,0,event_actor,sid)
    q=ConsumptionRequest(label,sid,'SYSTEM_TRANSITION',sid,'transition.RULE','PROCESS:'+sid,'SIM_TIME',str(time),str(time),'SCENARIO',k.boundary_manifest.scenario_id,'WORLD_SIM','','ADMITTED','TYPED_RULE','TRANSITION_RULE')
    receipt=admit_for_use(k,q)[1];receipts=[receipt];holder={}
    target=_target_runtime(k)
    def live(concept,subject,scope,unit,role):
        request=ConsumptionRequest(label+':'+concept+':'+subject,sid,'SYSTEM_TRANSITION',subject,concept,scope,'SIM_TIME',str(time),str(time),'REALIZED',k.boundary_manifest.run_id,'WORLD_SIM','','ADMITTED',unit,role)
        receipts.append(admit_for_use(k,request)[1])
    if method=='record_earth_reference_year':
        calendar=str(int(D(time))+2025)
        for concept,unit in (('population','PERSON'),('value_added','EARTH_REAL_PROXY_VALUE_ADDED_PER_YEAR'),('gross_output','EARTH_REAL_PROXY_GROSS_OUTPUT_PER_YEAR'),('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('capital','EARTH_REAL_PROXY_CAPITAL'),('legacy_employment','PERSON_FTE_PROXY')):
            request=ConsumptionRequest(label+':EARTH:'+concept,sid,'SYSTEM_TRANSITION','USA',concept,'COUNTRY:USA','SIM_TIME',str(time),str(time),'SCENARIO',k.boundary_manifest.scenario_id,'WORLD_SIM','','ADMITTED',unit,'EARTH_REFERENCE')
            receipts.append(admit_for_use(k,request)[1])
    if method in ('explore_paid','surface_prospect_paid','assess_resource_recoverability','resolve_operating_extraction'):
        build7=dict(k.boundary_manifest.parameters).get('build7.profile')=='BUILD7_GENERATED_CAMPAIGN_V1'
        physical_concept='R_IN_SITU' if build7 and method in ('explore_paid','surface_prospect_paid','assess_resource_recoverability') else 'R_RECOVERABLE'
        live(physical_concept,'RES',target['site_ref'],'MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
    if method in ('reserve_earth_supply','explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage'):
        live('Earth_supply.AVAILABLE','EARTH:USA:SIM'+str(time),'ECONOMY:USA:SUPPLY','MODEL_SUPPLY_CLAIM_CURRENCY','SUPPLIER_CAPACITY')
    if method in ('explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage','clear_market_sale','execute_surplus_distribution'):
        project='EXP' if method in ('explore_paid','surface_prospect_paid') else 'P'
        live('project.CASH_BALANCE',project,'PROJECT:'+project,'MODEL_CURRENCY','FINANCIAL_STATE')
    if method in ('surface_prospect_paid','publish_observation','update_agent_belief_from_observation'):
        obs_id=args[6] if method=='surface_prospect_paid' else args[2]
        live('observation.SIGNAL',obs_id,target['site_ref'],'SIGNAL_CATEGORY','OBSERVATION')
    if method=='resolve_operating_extraction':live('cycle.PAID_OPEX',args[4].event_id,'PROJECT:P','TYPED_EXPENSE_RECORD','REALIZED_EXPENSE')
    if method=='admit_realized_output_observation':live('cycle.ACTUAL_OUTPUT',args[2],target['site_ref'],'MODEL_RESOURCE_UNIT_BY_FAMILY','REALIZED_OUTPUT')
    if method=='update_agent_belief_from_observation':live('actor.BELIEF',args[1],'AGENT:'+args[1],'PROBABILITY','ACTOR_BELIEF')
    if method=='publish_observation':
        for actor,_,_,_ in args[4]:live('actor.BELIEF',actor,'AGENT:'+actor,'PROBABILITY','ACTOR_BELIEF')
    read_set=tuple(sorted(set(receipt.consumption_request.concept for receipt in receipts)))
    k.scheduler.register_coupling(CouplingSpec(sid,'BUILD6E_V1',RuntimeObjectClass.SYSTEM,owned,read_set,owned,'EVENT',Phase.OPERATIONS))
    k.scheduler.schedule(event)
    def apply(kernel,event):holder['value']=getattr(kernel,method)(*args,**(kwargs or {}));return 'REALIZED:'+method
    rt=ScheduledSimulationRuntime(k,strict_provenance(k))
    rt.register_handler(sid,apply,admission_receipts=tuple(receipts),decision_refs=decision_refs,transition_methods=(method,))
    before=AccountingPeriodSnapshot.capture(k,int(D(time)));rt.seal();h['results'].append(rt.run());h['audits'].append(AccountingIdentityAuditor(k,before).check_all());h['last_time']=D(time)
    return holder['value']

def system_epoch(k,h,method,time,args=(),kwargs=None,decision_refs=()):
    if not h.get('wa_service'):
        return _system_epoch_body(k,h,method,time,args,kwargs,decision_refs)
    from simulation.offworld_mvp.build6e.named_world import execute_persisted_epoch
    preview_counter=h['counter']+1
    epoch_id='ACTION:'+str(preview_counter)+':'+method
    delta=0 if method in ('execute_transport_settlement_departure','execute_passenger_transport_arrival') else int(h['params'].get('time_offset',0))
    effective=D(time)+delta
    result,status=execute_persisted_epoch(service_name=h['wa_service'],kernel=k,
        binding=h['named_binding'],epoch_id=epoch_id,effective_time=effective,
        agent_logins=h['agent_logins'],
        execute=lambda:_system_epoch_body(k,h,method,time,args,kwargs,decision_refs))
    h.setdefault('epoch_commits',[]).append((epoch_id,status))
    return result

def finance(k,h,label,time,request):
    version=h['manifest'].policy_version_hash(policy_source_bytes())
    d,ref=policy_epoch(k,h,label,'FIN',str(time),request,tuple('underwriting.'+x.kind.value for x in h['table'].inputs),lambda s,q,key:workers.run_financier_policy(s,q,h['manifest'],key,allow_test_fixture=True),version)
    if d.outcome.value=='APPROVE':
        cid='C-DEV' if request.stage=='DEVELOPMENT' else 'C-OP-'+str(int(D(time)))
        system_epoch(k,h,'add_commitment',str(time),(cid,'FIN','P',d.amount),decision_refs=(ref,))
        system_epoch(k,h,'disburse',str(time),(int(time),cid,'fin_funds',d.amount),decision_refs=(ref,))
    return d,ref

def operate(k,h,label,time,obs):
    request=build_operating_cycle_request(label+':request',int(time),'P','RES','MINE-P',obs.id)
    d,ref=policy_epoch(k,h,label,'SPN',str(time),request,('project.STATUS','project.CASH_BALANCE','asset.CAPACITY','underwriting.OPERATING_COST'),workers.run_sponsor_operating_policy,workers.sponsor_operating_policy_version())
    request=h['requests'][label]
    if d.outcome.value=='REQUEST_FINANCE':
        q=build_financing_request('OP-FIN-'+str(int(D(time))),int(time),'SPN','P',d.requested_financing,'OPERATING',(obs.id,));system_epoch(k,h,'submit_financing_request',str(time),(q,),decision_refs=(ref,))
        fd,_=finance(k,h,label+':finance',time,q)
        if fd.outcome.value!='APPROVE':return None
        d,ref=policy_epoch(k,h,label+':funded','SPN',str(time),replace(request,id=label+':funded:request'),('project.STATUS','project.CASH_BALANCE','asset.CAPACITY','underwriting.OPERATING_COST'),workers.run_sponsor_operating_policy,workers.sponsor_operating_policy_version());request=h['requests'][label+':funded']
    if d.outcome.value!='OPERATE':return None
    cost=system_epoch(k,h,'spend_operating_cycle',str(time),(int(time),'SPN',request,d,'earth_supplier',D(h['params']['opex_per_unit'])),decision_refs=(ref,))
    output=system_epoch(k,h,'resolve_operating_extraction',str(time),(int(time),'SPN',request,d,cost),decision_refs=(ref,))
    system_epoch(k,h,'admit_realized_output_observation',str(time),(int(time),'SPN',output.extraction_event_id),decision_refs=(ref,))
    return output

def review(k,h,label,time,output):
    req=build_enterprise_review_request(label+':request',int(time),'P',output.extraction_event_id)
    d,ref=policy_epoch(k,h,label,'SPN',str(time),req,('project.STATUS','cycle.PLANNED_QUANTITY','cycle.ACTUAL_OUTPUT'),workers.run_sponsor_enterprise_review_policy,workers.sponsor_enterprise_review_policy_version(),{'cycle.PLANNED_QUANTITY':output.extraction_event_id,'cycle.ACTUAL_OUTPUT':output.extraction_event_id})
    req=h['requests'][label]
    if d.outcome.value in ('CONTINUE','CLOSE'):system_epoch(k,h,'execute_enterprise_review',str(time),(int(time),'SPN',req,d),decision_refs=(ref,))
    return d

def strict_provenance(k,tables=(),policies=('NO_POLICY_THIS_EPOCH',)):
    m=k.boundary_manifest
    labels=[('BOUNDARY_SHA256',m.fingerprint()),('EARTH_SLICE_SHA256',m.earth_slice_ref[1]),
            ('COMPARISON_CONFIG_SHA256',m.comparison_spec_ref[1]),('QUALIFICATION_PROTOCOL_SHA256',m.qualification_protocol_ref[1])]
    for ref,digest in m.harness_refs:
        label={
            'simulation/offworld_mvp/build6e/qualification/qualify_build6e.py':'QUALIFICATION_DRIVER_SHA256',
            'simulation/offworld_mvp/build7/runtime_flow.py':'BUILD7_RUNTIME_FLOW_SHA256',
            'simulation/offworld_mvp/build6e/named_world.py':'NAMED_WORLD_COMPILER_SHA256',
            'src/loom_world_authority/store.py':'WORLD_AUTHORITY_STORE_SHA256',
            'simulation/offworld_mvp/build7/generated_campaign.py':'BUILD7_CAMPAIGN_SHA256',
        }.get(ref)
        if label is None:raise RuntimeError('undeclared Build 7 harness module: '+ref)
        labels.append((label,digest))
    if not hasattr(k,'_boundary_candidate_provenance'):k._boundary_candidate_provenance=ReplayProvenance.from_kernel(k)
    return replace(k._boundary_candidate_provenance,table_manifest_ids=tuple(key+':'+value for key,value in labels)+tuple(tables),policy_manifest_ids=tuple(policies)).validate()
