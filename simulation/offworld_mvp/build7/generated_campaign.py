"""Build 7: generated hidden-WORLD campaign entrypoint.

This is deliberately small.  The existing Offworld kernel remains the runtime;
World Authority remains the durable store.  Build 7 only composes a generated
private WORLD with the existing decision/prospecting machinery without importing
Cabeus resource claims into the campaign.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from decimal import Decimal as D
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from loom_world_authority import store
from loom_world_authority.etl import SOURCE_SHA as WA_SOURCE_SHA
from offworld_kernel.boundary import (
    BUILD6E_AUTHORIZATION, BUILD6E_CONTRACT, BoundaryManifest, ContextValue,
    ConsumptionRequest, admit_for_use, load_earth_assertions, earth_supply_value,
)
from offworld_kernel.causal_trace import canonical, content_hash
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import (
    AgentKind, AgentState, ScenarioResource, SystemState, PopulationLedger, ColonyState,
)
from offworld_kernel.policy import FactState
from offworld_kernel.surface_prospecting import SurfaceProspectingModel
from offworld_kernel.underwriting import UnderwritingTable, mvp_validation_underwriting_table
from offworld_kernel.policies.manifest import test_only_manifest, ObservationKnowledgeRelation
from offworld_kernel import policy_runner as workers
from offworld_kernel.exploration_protocol import build_exploration_request

from simulation.offworld_mvp.build6e.generated_world import generate_solar_system
from simulation.offworld_mvp.build6e.named_world import NamedLocationBinding
from simulation.offworld_mvp.build6e.qualification import build6e_fixture as flow

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'inputs/BUILD7_GENERATED_CAMPAIGN_V1.json'
EARTH_PATH = ROOT.parent / 'build6e/inputs/BUILD6E_EARTH_REFERENCE_SLICE_V1.json'
EARTH_PARENT = Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')
AUTHORIZATION = 'BUILD7_HIDDEN_WORLD_BASELINE_001'
PROFILE = 'BUILD7_GENERATED_CAMPAIGN_V1'


class Build7Blocked(RuntimeError):
    pass


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_config() -> dict:
    doc=json.loads(INPUT.read_text())
    if set(doc)!={'schema','standing','runtime','structural_parameters'} or doc['schema']!=PROFILE:
        raise Build7Blocked('BUILD7_CONFIG_PROFILE')
    return doc


def _source(assertion_id,subject,concept,scope,context,context_id,perspective,actor,
            value,unit,source_hash,role='POLICY_PARAMETER',*,source_ref=PROFILE,
            epistemic_mode='AUTHORED_SCENARIO'):
    return ContextValue(assertion_id,subject,concept,scope,context,context_id,perspective,actor,
        FactState.UNKNOWN if value is None else FactState.KNOWN,value,unit,'ADMITTED',
        'BUILD7_SCENARIO_INPUT',role,epistemic_mode,'ADMITTED','UNCHARACTERIZED','NOT_SUPPLIED',
        '0','20','SIM_TIME','0',(source_ref,),(source_hash,),(AUTHORIZATION,),(),(),'', '',AUTHORIZATION,
        'NOT_EARTH_REFERENCE',(('empirical_calibration','NOT_SUPPLIED'),),'CONTEXT_VALUE_V1','0')


def _target_from_generated(binding: Mapping, config: Mapping) -> dict:
    scale=D(config['runtime']['kg_per_model_resource_unit'])
    if scale<=0:raise Build7Blocked('BUILD7_RESOURCE_SCALE')
    node='OFF:'+binding['body_key']+':GEN_SITE_1'
    site_ref='SITE:'+node
    resource=ScenarioResource('RES',node,binding['resource_class'],
        D(binding['block']['target_mass_kg'])/scale,None,None,None)
    named=NamedLocationBinding(
        body_id=binding['body_id'],parent_location_id=None,authored_site_id=binding['site_id'],
        local_feature_id=binding['feature_id'],scenario_id=binding['scenario_id'],
        model_id=binding['model_id'],policy_id=binding['policy_id'],world_id=binding['world_id'],
        world_site_id=binding['world_site_id'],deposit_id=binding['deposit_id'],
        assertion_id=None,support_id=None,admission_id=None,site_node_id=node,resource_id='RES',
        settlement_id='SET:'+binding['body_key']+':GEN_SITE_1',resource_unit_key='GEN_KG_V1',
        resource_scale=scale)
    return dict(body_key=binding['body_key'],body_name=binding['body_name'],node=node,
        site_ref=site_ref,catalog_subject=binding['body_key'],catalog_scope='BODY:'+binding['body_key'],
        site_name=binding['body_name']+' generated prospecting domain',resource=resource,binding=named,
        world_seed=None,scenario_key=binding['scenario_key'],result_hash=binding['result_hash'])


def _target_from_bound(reference_reader, runtime_service: str, run_id: str,
                       binding_key: str, config: Mapping) -> dict:
    import psycopg
    with psycopg.connect(service=runtime_service) as conn:
        physical=store.load_bound_world(conn,run_id,binding_key,context='REALIZED',effective_time=D('999999'))
    realization=physical['realization']
    if realization is None or len(physical['sites'])!=1 or len(physical['deposits'])!=1:
        raise Build7Blocked('BUILD7_BOUND_WORLD_CARDINALITY')
    catalog=store.read_generation_catalog(reference_reader,WA_SOURCE_SHA)
    body=next((b for b in catalog if b['body_id']==realization['body_id']),None)
    if body is None:raise Build7Blocked('BUILD7_BOUND_BODY_NOT_IN_CATALOG')
    site=physical['sites'][0];deposit=physical['deposits'][0]
    if deposit['resource_class']!='WATER_BEARING_MATERIAL' or deposit['initial_in_situ_state']!='KNOWN' or deposit['unit_key']!='GEN_KG_V1':
        raise Build7Blocked('BUILD7_BOUND_DEPOSIT_PROFILE')
    scale=D(config['runtime']['kg_per_model_resource_unit'])
    node='OFF:'+body['semantic_key']+':GEN_SITE_1';site_ref='SITE:'+node
    resource=ScenarioResource('RES',node,deposit['resource_class'],D(deposit['initial_in_situ_quantity'])/scale,None,None,None)
    named=NamedLocationBinding(
        body_id=realization['body_id'],parent_location_id=None,authored_site_id=site['location_id'],
        local_feature_id=deposit['location_id'],scenario_id=realization['scenario_id'],
        model_id=realization['model_id'],policy_id=realization['policy_id'],world_id=realization['world_id'],
        world_site_id=site['site_id'],deposit_id=deposit['deposit_id'],assertion_id=None,support_id=None,
        admission_id=None,site_node_id=node,resource_id='RES',settlement_id='SET:'+body['semantic_key']+':GEN_SITE_1',
        resource_unit_key='GEN_KG_V1',resource_scale=scale)
    return dict(body_key=body['semantic_key'],body_name=body['canonical_name'],node=node,site_ref=site_ref,
        catalog_subject=body['semantic_key'],catalog_scope='BODY:'+body['semantic_key'],
        site_name=site['name'],resource=resource,binding=named,
        world_seed=realization['world_seed_lexeme'],scenario_key=physical['scenario_semantic_key'],result_hash=realization['generator_output_sha256'])


def _build_kernel(target: Mapping, config: Mapping, *, world_seed: str):
    params=dict(config['structural_parameters'])
    params.update({
        'resource_id':'RES','reference_population_bound':'349892943',
        'opening_effective_time':config['runtime']['opening_effective_time'],
        'time_offset':str(config['runtime']['time_offset']),
        'site_binding_key':config['runtime']['site_binding_key'],
        'build7.site_node_id':target['node'],'build7.site_ref':target['site_ref'],
        'build7.catalog_subject':target['catalog_subject'],'build7.catalog_scope':target['catalog_scope'],
        'build7.profile':PROFILE,
    })
    config_hash=_sha(INPUT);earth,earth_hash=load_earth_assertions(EARTH_PATH,parent_root=EARTH_PARENT)
    comparison={'world_seed':str(world_seed),'policy_seed':config['runtime']['policy_seed'],
        'comparison_group':config['runtime']['comparison_group'],'algorithm':'SHA256_FIRST64_DECIMAL_V1',
        'key_schema':'LOOM_COMPARISON_RANDOM_V1','decimal_precision':28,'decimal_rounding':'ROUND_HALF_EVEN'}
    scenario_id=target['scenario_key']
    run_id=scenario_id+':'+content_hash((str(target['binding'].world_id),config_hash,_sha(Path(__file__).resolve()),tuple(sorted(params.items())),tuple(sorted(comparison.items()))))[:16]

    old_policy=test_only_manifest()
    policy_values={'hurdle_rate':params['financier_hurdle_rate'],'horizon_years':params['financier_horizon_years'],
        'agent_detection_rate':params['publication_detection'],'agent_false_positive_rate':params['publication_fp'],
        'normalized_throughput':params['financier_normalized_throughput'],'max_concentration_fraction':params['financier_max_concentration_fraction']}
    policy_manifest=replace(old_policy,manifest_id='BUILD7_FINANCIER_STRUCTURAL_PARAMS_V1',
        parameters=tuple(replace(x,parameter_id='B7:'+x.parameter_id,value=D(policy_values[x.semantic_name]),
            authorization_ref=AUTHORIZATION,valid_from_version='BUILD7_V1',valid_to_version='BUILD7_V1') for x in old_policy.parameters),
        observation_knowledge_relation=ObservationKnowledgeRelation.INDEPENDENT_AGENT_LIKELIHOOD_MODEL,
        world_observation_model_ref='INDEPENDENT_AGENT_MODEL_NOT_WORLD_PARAMETER_ACCESS',world_detection_rate=None,
        world_false_positive_rate=None).validate(require_authorized=False)
    table_values={'PRICE':params['unit_price'],'EXPLORATION_CAPEX':params['remote_cost'],
        'DEVELOPMENT_CAPEX':params['capex'],'OPERATING_COST':params['opex_per_unit'],'LEAD_TIME':params['lead_time']}
    table=UnderwritingTable('BUILD7_STRUCTURAL_UNDERWRITING_V1','1','PRE_CONTRACT_AUTHORED_SCENARIO',
        tuple(replace(x,value=D(table_values[x.kind.value]),valid_to=20,
            source_or_rationale_ref=AUTHORIZATION+':STRUCTURAL_PARAMETER') for x in mvp_validation_underwriting_table().inputs)).validate()

    static={'exploration.REMOTE_COST':(params['remote_cost'],'MODEL_CURRENCY'),
            'exploration.SURFACE_COST':(params['surface_cost'],'MODEL_CURRENCY')}
    assertions=list(earth);contracts=[];bindings=[]
    for actor in ('PUB','SPN','FIN'):
        for concept in ('agent.STATE','agent.BELIEF','agent.PRIOR'):
            selector,_,unit=flow.LIVE[concept]
            contracts.append((actor,'POLICY',concept,'AGENT:'+actor,'REALIZED','AGENT',unit,'ADMITTED_INFORMATION'))
            bindings.append((actor,concept,selector))
    for concept,(value,unit) in static.items():
        assertions.append(_source('PUB:'+concept,'EXP',concept,'PROJECT:EXP','SCENARIO',scenario_id,'AGENT','PUB',value,unit,config_hash))
        contracts.append(('PUB','POLICY',concept,'PROJECT:EXP','SCENARIO','AGENT',unit,'POLICY_PARAMETER'))
    assertions.extend((
        replace(_source('WA_CATALOG:BODY:'+target['body_key'],target['catalog_subject'],'opportunity.NAMED_LOCATION',
            target['catalog_scope'],'REAL','','AGENT','PUB',target['body_name'],'CATALOG_LOCATION_IDENTITY',WA_SOURCE_SHA,
            role='ADMITTED_CATALOG_IDENTITY',source_ref='WA_CATALOG:BODY:'+target['body_key'],epistemic_mode='CATALOG_IDENTITY'),
            proposition_kind='REAL_CATALOG_IDENTITY',authorization_ref='WA_CATALOG_IMPORT_V1'),
        _source('BUILD7_AUTHORED_SITE:'+target['body_key'],target['site_ref'],'opportunity.AUTHORED_SITE',target['site_ref'],
            'SCENARIO',scenario_id,'AGENT','PUB',target['site_name'],'AUTHORED_SITE_IDENTITY',config_hash),
    ))
    contracts.extend((
        ('PUB','POLICY','opportunity.NAMED_LOCATION',target['catalog_scope'],'REAL','AGENT','CATALOG_LOCATION_IDENTITY','ADMITTED_CATALOG_IDENTITY'),
        ('PUB','POLICY','opportunity.AUTHORED_SITE',target['site_ref'],'SCENARIO','AGENT','AUTHORED_SITE_IDENTITY','POLICY_PARAMETER'),
    ))

    used_methods=('add_commitment','disburse','reserve_earth_supply','explore_paid','surface_prospect_paid','update_agent_belief_from_observation')
    allowed=[]
    for method in used_methods:
        sid='SYS:'+method;allowed.append((sid,(method,)))
        scope='PROCESS:'+sid
        assertions.append(_source(sid,sid,'transition.RULE',scope,'SCENARIO',scenario_id,'WORLD_SIM','',
            canonical((method,tuple(sorted(params.items())))),'TYPED_RULE',config_hash,role='TRANSITION_RULE'))
        contracts.append((sid,'SYSTEM_TRANSITION','transition.RULE',scope,'SCENARIO','WORLD_SIM','TYPED_RULE','TRANSITION_RULE'))
        if method in ('explore_paid','surface_prospect_paid'):
            contracts.append((sid,'SYSTEM_TRANSITION','R_IN_SITU',target['site_ref'],'REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
            bindings.append((sid,'R_IN_SITU','RESOURCE'))
        if method in ('reserve_earth_supply','explore_paid','surface_prospect_paid'):
            contracts.append((sid,'SYSTEM_TRANSITION','Earth_supply.AVAILABLE','ECONOMY:USA:SUPPLY','REALIZED','WORLD_SIM','MODEL_SUPPLY_CLAIM_CURRENCY','SUPPLIER_CAPACITY'))
            bindings.append((sid,'Earth_supply.AVAILABLE','EARTH_SUPPLY'))
        if method in ('explore_paid','surface_prospect_paid'):
            contracts.append((sid,'SYSTEM_TRANSITION','project.CASH_BALANCE','PROJECT:EXP','REALIZED','WORLD_SIM','MODEL_CURRENCY','FINANCIAL_STATE'))
            bindings.append((sid,'project.CASH_BALANCE','PROJECT_CASH'))
        if method in ('surface_prospect_paid','update_agent_belief_from_observation'):
            contracts.append((sid,'SYSTEM_TRANSITION','observation.SIGNAL',target['site_ref'],'REALIZED','WORLD_SIM','SIGNAL_CATEGORY','OBSERVATION'))
            bindings.append((sid,'observation.SIGNAL','OBSERVATION'))
        if method=='update_agent_belief_from_observation':
            contracts.append((sid,'SYSTEM_TRANSITION','actor.BELIEF','AGENT:PUB','REALIZED','WORLD_SIM','PROBABILITY','ACTOR_BELIEF'))
            bindings.append((sid,'actor.BELIEF','ACTOR_BELIEF'))
    for concept,unit in [('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('population','PERSON')]:
        contracts.append(('GENESIS','EARTH_REFERENCE',concept,'COUNTRY:USA','REAL','GOVERNANCE',unit,'EARTH_REFERENCE'))

    here=Path(__file__).resolve();named=ROOT.parent/'build6e/named_world.py';fixture=ROOT.parent/'build6e/qualification/build6e_fixture.py';store_path=ROOT.parents[2]/'src/loom_world_authority/store.py'
    harness=tuple((str(p.relative_to(ROOT.parents[2])),_sha(p)) for p in (here,fixture,named,store_path))
    authority_sources=tuple((s.source_refs[0],s.source_hashes[0]) for s in earth[::2])
    definitions=((INPUT.name,config_hash),)
    m=BoundaryManifest(BUILD6E_CONTRACT,'BUILD7_INPUT:'+content_hash((definitions,earth_hash,tuple(sorted(params.items())),authority_sources)),
        scenario_id,'V1',run_id,definitions,authority_sources,'0'*64,
        (('PARAMETERS:'+scenario_id,content_hash(tuple(sorted(params.items())))),('FINANCIER_POLICY_PARAMETERS',policy_manifest.parameter_manifest_hash()),('WORLD_REALIZATION:'+str(target['binding'].world_id),target['result_hash'])),
        tuple(contracts),tuple(bindings),('BUILD7_COMPARISON',content_hash(tuple(sorted(comparison.items())))),
        (EARTH_PATH.name,earth_hash),(INPUT.name,config_hash),'SIM_YEAR_PLUS_2025_V1','ODD_SCHEMA_REGISTRY_0_20',
        BUILD6E_AUTHORIZATION,tuple(assertions),tuple(sorted(params.items())),tuple(sorted(comparison.items())),tuple(allowed),(),harness)
    rid=RunIdentity(str(target['binding'].world_id),'BUILD7_V1',m.input_snapshot_id,BUILD6E_CONTRACT,m.parameters)
    k=MethodologyHardenedBuild4Kernel(rid,boundary_manifest=m,lambda_displacement=D(params['lambda']))
    node=target['node'];k.add_node('EARTH:USA',NodeKind.EARTH);k.add_node(node,NodeKind.OFFWORLD)
    accounts=[('public_funds','PUB','EARTH:USA',AccountKind.FUNDS,params['P']),
        ('fin_funds','FIN','EARTH:USA',AccountKind.FUNDS,params['F']),('earth_market','EARTH_MARKET','EARTH:USA',AccountKind.EARTH_BOUNDARY,params['B']),
        ('sponsor_funds','SPN','EARTH:USA',AccountKind.FUNDS,'0'),('earth_supplier','SUP','EARTH:USA',AccountKind.SUPPLIER,'0'),
        ('explore_cash','EXP',node,AccountKind.PROJECT_CASH,'0'),('project_cash','SPN',node,AccountKind.PROJECT_CASH,'0')]
    for aid,owner,where,kind,value in accounts:k.add_account(aid,owner,where,kind,D(value))
    k.add_project('EXP',node,'explore_cash',{'PUB':D(1)});k.add_project('P',node,'project_cash',{'SPN':D(1)})
    for aid,kind,account,caps,objectives in (
        ('PUB',AgentKind.PUBLIC,'public_funds',{'EXPLORE','SURFACE_PROSPECT'},('PUBLIC_INFORMATION',)),
        ('FIN',AgentKind.PRIVATE_FINANCIER,'fin_funds',{'FINANCE'},('RETURN',)),
        ('SPN',AgentKind.PRIVATE_SPONSOR,'sponsor_funds',{'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL'},('RETURN',))):
        a=AgentState(aid,kind,'EARTH:USA',account,caps,objectives);key=params['belief_key.'+aid]
        a.priors[key]=D(params['prior']);a.beliefs[key]=D(params['prior']);k.add_agent(a)
    k.add_resource(target['resource'])
    k.population=PopulationLedger(int(params['N']),{node:0});k.colonies[node]=ColonyState(node)
    for value in earth:
        if value.concept=='investment':
            year=int(value.valid_from)-2025
            k.set_resource_constraint('EARTH:USA',year,D(value.value)/D(params['S']),D(params.get('f.'+str(year),params['f'])))
    for method in used_methods:k.add_system(SystemState('SYS:'+method,'EXISTING_TRANSITION',set(flow.OWNERS[method])))
    k.add_system(SystemState('DECISION','DECISION_ORCHESTRATION',set()));k.add_system(SystemState('AUDIT','QUALIFICATION_AUDIT',set()))

    genesis=[];derived=[]
    for source in earth:
        if source.concept!='investment':continue
        year=int(source.valid_from)-2025
        request=ConsumptionRequest('EARTH_SOURCE:'+str(year),'GENESIS','EARTH_REFERENCE','USA','investment','COUNTRY:USA',
            'CALENDAR_YEAR',source.valid_from,source.available_from,'REAL','','GOVERNANCE','','ADMITTED',source.unit,'EARTH_REFERENCE')
        value,receipt=admit_for_use(k,request)
        transformed=earth_supply_value(value,params['S'],params.get('f.'+str(year),params['f']),year,scenario_id)
        transformed=replace(transformed,dependency_refs=(*transformed.dependency_refs,receipt.receipt_id))
        derived.append(transformed);genesis.append((receipt,value))
    population=next(a for a in earth if a.concept=='population' and a.valid_from=='2027')
    request=ConsumptionRequest('EARTH_POPULATION_BOUND','GENESIS','EARTH_REFERENCE','USA','population','COUNTRY:USA',
        'CALENDAR_YEAR','2027','2027','REAL','','GOVERNANCE','','ADMITTED','PERSON','EARTH_REFERENCE')
    bound,receipt=admit_for_use(k,request);genesis.append((receipt,bound));k._boundary_genesis_inputs=tuple(genesis)
    opening_records={'profile':PROFILE,'agents':tuple(sorted(k.agents.items())),'systems':tuple(sorted(k.systems.items())),
        'projects':tuple(sorted(k.state.projects.items())),'accounts':tuple(sorted(k.state.accounts.items())),
        'initial_population':k.population,'settlement_id':target['binding'].settlement_id,'settlement_node':node,
        'initial_colony':k.colonies[node],'cohort_id':config['runtime']['cohort_id'],
        'population_source_receipt':next(r.receipt_id for r,v in genesis if r.consumption_request.concept=='population'),
        'earth_supply_transformations':tuple(derived)}
    k._boundary_authored_inputs=(table,policy_manifest,opening_records)
    m=replace(m,assertions=(*m.assertions,*derived));k.boundary_manifest=m
    opening=tuple((key,canonical(k._boundary_opening_value(key))) for key in ('accounts','agents','resources','constraints','population','earth_admission_receipts'))
    k.boundary_manifest=replace(m,opening_bindings=opening,opening_state_hash=content_hash(k._boundary_projection()))
    h={'params':params,'table':table,'manifest':policy_manifest,
       'model':SurfaceProspectingModel('BUILD7_SURFACE',D(params['surface_fp']),D(params['surface_fn']),
           D(params['surface_detection']),D(params['surface_fp']),D(params['remote_fp']),D(params['remote_fn']),
           'STRUCTURAL_NOT_CALIBRATED',AUTHORIZATION).validate(),
       'results':[],'audits':[],'policies':{},'snapshots':{},'requests':{},'counter':0,'last_time':D(0)}
    return k,h


def _agent_logins(service_names=('agent_pub','agent_spn','agent_fin')):
    import psycopg
    result={}
    for actor,service in zip(('PUB','SPN','FIN'),service_names,strict=True):
        with psycopg.connect(service=service) as conn:
            result[actor]=conn.execute('select session_user').fetchone()[0]
    return result


def _attach_persistence(h,target,runtime_service,agent_logins):
    h['wa_service']=runtime_service;h['named_binding']=target['binding'];h['agent_logins']=agent_logins


def run_remote(k,h):
    p=h['params']
    req=build_exploration_request('REMOTE:request',1,'EXP','RES','REMOTE')
    d,ref=flow.policy_epoch(k,h,'REMOTE','PUB','1',req,
        ('exploration.REMOTE_COST','opportunity.NAMED_LOCATION','opportunity.AUTHORED_SITE'),
        workers.run_public_explorer_policy,workers.public_explorer_policy_version())
    if d.outcome.value!='AUTHORIZE':return None
    flow.system_epoch(k,h,'add_commitment','1',('C-REMOTE','PUB','EXP',d.authorized_cost),decision_refs=(ref,))
    flow.system_epoch(k,h,'disburse','1',(1,'C-REMOTE','public_funds',d.authorized_cost),decision_refs=(ref,))
    flow.system_epoch(k,h,'reserve_earth_supply','1',('EARTH:USA',1,d.authorized_cost),decision_refs=(ref,))
    obs,asset,draw=flow.system_epoch(k,h,'explore_paid','1',
        (1,'PUB','RES','EXP','earth_supplier',d.authorized_cost),
        dict(channel='REMOTE',public=False,false_positive=D(p['remote_fp']),false_negative=D(p['remote_fn']),
             update_belief=False,parent_ids=(d.id,)),(ref,))
    h['REMOTE']=obs;h['REMOTE_draw']=draw
    flow.system_epoch(k,h,'update_agent_belief_from_observation','1',
        (1,'PUB',obs.id,'RES',D(p['remote_detection']),D(p['remote_fp']),'BUILD7_REMOTE',AUTHORIZATION),decision_refs=(ref,))
    return obs


def run_surface(k,h):
    if 'REMOTE' not in h:raise Build7Blocked('BUILD7_REMOTE_REQUIRED')
    p=h['params'];req=build_exploration_request('SURFACE:request',2,'EXP','RES','SURFACE',prerequisite_observation_id=h['REMOTE'].id)
    d,ref=flow.policy_epoch(k,h,'SURFACE','PUB','2',req,('exploration.SURFACE_COST',),
        workers.run_public_surface_prospector_policy,workers.public_surface_prospector_policy_version())
    if d.outcome.value!='AUTHORIZE':return None
    flow.system_epoch(k,h,'add_commitment','2',('C-SURFACE','PUB','EXP',d.authorized_cost),decision_refs=(ref,))
    flow.system_epoch(k,h,'disburse','2',(2,'C-SURFACE','public_funds',d.authorized_cost),decision_refs=(ref,))
    flow.system_epoch(k,h,'reserve_earth_supply','2',('EARTH:USA',2,d.authorized_cost),decision_refs=(ref,))
    obs,asset,draw,_=flow.system_epoch(k,h,'surface_prospect_paid','2',
        (2,'PUB','RES','EXP','earth_supplier',d.authorized_cost,h['REMOTE'].id,h['model']),dict(parent_ids=(d.id,)),(ref,))
    h['SURFACE']=obs;h['SURFACE_draw']=draw
    flow.system_epoch(k,h,'update_agent_belief_from_observation','2',
        (2,'PUB',obs.id,'RES',D(p['surface_detection']),D(p['surface_fp']),'BUILD7_SURFACE',AUTHORIZATION),decision_refs=(ref,))
    return obs


def start_campaign(*,reference_service,science_writer_service,world_writer_service,runtime_service,
                   world_seed,body,science_cutoff,authorization_ref=AUTHORIZATION):
    import psycopg
    config=load_config();body=body.upper()
    with psycopg.connect(service=reference_service) as reader, psycopg.connect(service=science_writer_service) as science, \
         psycopg.connect(service=world_writer_service) as writer:
        generated=generate_solar_system(reader,science,writer,seed=world_seed,authorization_ref=authorization_ref,
            science_cutoff=science_cutoff,return_bindings=True)
    if body not in generated['_bindings']:raise Build7Blocked('BUILD7_BODY_NOT_GENERATED:'+body)
    target=_target_from_generated(generated['_bindings'][body],config);target['world_seed']=world_seed
    k,h=_build_kernel(target,config,world_seed=world_seed);_attach_persistence(h,target,runtime_service,_agent_logins())
    obs=run_remote(k,h)
    return dict(run_id=k.boundary_manifest.run_id,body=body,world_id=str(target['binding'].world_id),
        generated_status=generated['status'],remote_signal=None if obs is None else obs.signal,
        epoch_commits=tuple(h.get('epoch_commits',())),hidden_in_situ_model_units=str(target['resource'].in_situ))


def resume_campaign(*,reference_service,runtime_service,run_id):
    import psycopg
    config=load_config()
    with psycopg.connect(service=reference_service) as reader:
        target=_target_from_bound(reader,runtime_service,run_id,config['runtime']['site_binding_key'],config)
    k,h=_build_kernel(target,config,world_seed=target['world_seed']);_attach_persistence(h,target,runtime_service,_agent_logins())
    remote=run_remote(k,h);surface=run_surface(k,h)
    if k.boundary_manifest.run_id!=run_id:raise Build7Blocked('BUILD7_RESUME_RUN_ID_MISMATCH')
    return dict(run_id=run_id,body=target['body_key'],world_id=str(target['binding'].world_id),
        remote_signal=None if remote is None else remote.signal,surface_signal=None if surface is None else surface.signal,
        epoch_commits=tuple(h.get('epoch_commits',())),hidden_in_situ_model_units=str(target['resource'].in_situ))


def main(argv=None):
    ap=argparse.ArgumentParser(description='LOOM Offworld Build 7 generated-WORLD campaign')
    sub=ap.add_subparsers(dest='command',required=True)
    new=sub.add_parser('new');new.add_argument('--reference-service',default='reference_reader');new.add_argument('--science-writer-service',default='science_writer')
    new.add_argument('--world-writer-service',default='world_writer');new.add_argument('--runtime-service',default='runtime')
    new.add_argument('--world-seed',required=True);new.add_argument('--body',required=True);new.add_argument('--science-cutoff',type=int,default=0)
    resume=sub.add_parser('resume');resume.add_argument('--reference-service',default='reference_reader');resume.add_argument('--runtime-service',default='runtime');resume.add_argument('--run-id',required=True)
    args=ap.parse_args(argv)
    result=start_campaign(reference_service=args.reference_service,science_writer_service=args.science_writer_service,
        world_writer_service=args.world_writer_service,runtime_service=args.runtime_service,world_seed=args.world_seed,
        body=args.body,science_cutoff=args.science_cutoff) if args.command=='new' else resume_campaign(
        reference_service=args.reference_service,runtime_service=args.runtime_service,run_id=args.run_id)
    print(json.dumps(result,sort_keys=True,default=str))


if __name__=='__main__':main()
