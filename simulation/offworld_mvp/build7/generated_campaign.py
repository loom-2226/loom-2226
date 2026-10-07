"""LOOM Offworld Build 7 integrated generated-WORLD campaign runtime.

Build 7 composes the existing qualified Offworld kernel with generated hidden WORLD
truth, current promoted Earth reference state, read-only Timeline context, and World
Authority persistence.  It is intentionally a composition layer, not a second sim.
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
    ConsumptionRequest, admit_for_use, earth_supply_value,
)
from offworld_kernel.causal_trace import canonical, content_hash, validate_trace
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind, NodeKind
from offworld_kernel.mvp_state import (
    AgentKind, AgentState, ScenarioResource, SystemState, PopulationLedger, ColonyState,
)
from offworld_kernel.policy import FactState
from offworld_kernel.project_lifecycle import ProjectDevelopmentPlan
from offworld_kernel.surface_prospecting import SurfaceProspectingModel
from offworld_kernel.market import CommodityMarketEnvelope
from offworld_kernel.distribution import FinancingReturnClaim
from offworld_kernel.settlement import SettlementInfrastructurePlan
from offworld_kernel.transport import TechnologyCapabilityState, TransportRelationship
from offworld_kernel.underwriting import UnderwritingTable, mvp_validation_underwriting_table
from offworld_kernel.policies.manifest import test_only_manifest, ObservationKnowledgeRelation, policy_source_bytes
from offworld_kernel import policy_runner as workers
from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel.publication_protocol import build_publication_request
from offworld_kernel.sponsor_protocol import build_sponsor_project_request
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.market_protocol import build_sale_decision_request
from offworld_kernel.distribution_protocol import build_surplus_distribution_request
from offworld_kernel.transport_protocol import build_transport_settlement_request

from simulation.offworld_mvp.build6e.generated_world import generate_solar_system, bind_generated_target
from simulation.offworld_mvp.build6e.named_world import NamedLocationBinding
from simulation.offworld_mvp.build7 import runtime_flow as flow

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
INPUT = ROOT / 'inputs/BUILD7_GENERATED_CAMPAIGN_V1.json'
EARTH_INPUT = ROOT / 'inputs/BUILD7_EARTH_USA_2026_2045_V1.json'
TIMELINE_INPUT = ROOT / 'inputs/BUILD7_TIMELINE_SNAPSHOT_V1.json'
SOLAR_CATALOG_INPUT = ROOT / 'inputs/BUILD7_SOLAR_BODY_CATALOG_V1.json'
AUTHORIZATION = 'BUILD7_HIDDEN_WORLD_BASELINE_001'
PROFILE = 'BUILD7_GENERATED_CAMPAIGN_V1'
EARTH_SCHEMA = 'BUILD7_EARTH_USA_2026_2045_V1'
TIMELINE_SCHEMA = 'BUILD7_TIMELINE_SNAPSHOT_V1'


class Build7Blocked(RuntimeError):
    pass


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_config() -> dict:
    doc=json.loads(INPUT.read_text())
    if set(doc)!={'schema','standing','runtime','structural_parameters','recovery_capability'} or doc['schema']!=PROFILE:
        raise Build7Blocked('BUILD7_CONFIG_PROFILE')
    if doc['runtime']['opening_effective_time']!='1' or int(doc['runtime']['time_offset'])!=0:
        raise Build7Blocked('BUILD7_2026_CLOCK_PROFILE')
    cap=doc['recovery_capability']
    required={'profile_id','standing','max_depth_m','max_temperature_k','max_pressure_pa','compatible_forms','recovery_yield'}
    if set(cap)!=required:raise Build7Blocked('BUILD7_RECOVERY_CAPABILITY_PROFILE')
    return doc


def _source(assertion_id,subject,concept,scope,context,context_id,perspective,actor,
            value,unit,source_hash,role='POLICY_PARAMETER',*,source_ref=PROFILE,
            epistemic_mode='AUTHORED_SCENARIO'):
    return ContextValue(
        assertion_id=assertion_id,subject_id=subject,concept=concept,scope=scope,
        world_context=context,context_id=context_id,perspective=perspective,perspective_actor_id=actor,
        value_state=FactState.UNKNOWN if value is None else FactState.KNOWN,value=value,unit=unit,
        reason_code='ADMITTED',proposition_kind='BUILD7_SCENARIO_INPUT',proposition_role=role,
        epistemic_mode=epistemic_mode,admission_state='ADMITTED',uncertainty_state='UNCHARACTERIZED',
        uncertainty_ref='NOT_SUPPLIED',valid_from='0',valid_to='20',time_basis='SIM_TIME',available_from='0',
        source_refs=(source_ref,),source_hashes=(source_hash,),warrant_refs=(AUTHORIZATION,),
        support_conflict_refs=(),dependency_refs=(),transformation_ref='',transformation_version='',
        authorization_ref=AUTHORIZATION,reference_role='NOT_EARTH_REFERENCE',
        exception_flags=(('empirical_calibration','NOT_SUPPLIED'),),record_version='CONTEXT_VALUE_V1',source_time='0')


def _load_earth_authority():
    raw=EARTH_INPUT.read_bytes(); doc=json.loads(raw)
    if doc.get('schema')!=EARTH_SCHEMA or doc.get('source_snapshot_id')!='earth-v0-1-9934d0ac-20260925':
        raise Build7Blocked('BUILD7_EARTH_AUTHORITY_PROFILE')
    cov=doc['coverage']
    if (cov['iso3'],cov['start_year'],cov['end_year'],cov['economic_rows'],cov['demographic_rows'])!=('USA',2026,2045,20,20):
        raise Build7Blocked('BUILD7_EARTH_COVERAGE')
    if doc['economic_pointer']['active_designation']!=doc['source_model'] or doc['demographic_pointer']['active_designation']!=doc['source_model']:
        raise Build7Blocked('BUILD7_EARTH_POINTER_DRIFT')
    by_econ={int(r['year']):r for r in doc['economic']};by_demo={int(r['year']):r for r in doc['demographic']};by_labor={int(r['year']):r for r in doc['legacy_labor']}
    if set(by_econ)!=set(range(2026,2046)) or set(by_demo)!=set(range(2026,2046)):
        raise Build7Blocked('BUILD7_EARTH_YEAR_GAP')
    units={'investment':'EARTH_REAL_PROXY_INVESTMENT_PER_YEAR','population':'PERSON','biological_population':'PERSON',
           'value_added':'EARTH_REAL_PROXY_VALUE_ADDED_PER_YEAR','gross_output':'EARTH_REAL_PROXY_GROSS_OUTPUT_PER_YEAR',
           'capital':'EARTH_REAL_PROXY_CAPITAL','legacy_employment':'PERSON_FTE_PROXY'}
    values=[];input_hash=sha256(raw).hexdigest();promotion=doc['promotion_manifest_sha256']
    for year in range(2026,2046):
        merged={**by_econ[year],**by_demo[year],**by_labor[year]}
        concept_values={'investment':merged['investment'],'population':merged['biological_population'],
                        'value_added':merged['value_added'],'gross_output':merged['gross_output'],
                        'capital':merged['capital'],'legacy_employment':merged['legacy_employment']}
        for concept,value in concept_values.items():
            values.append(ContextValue(
                assertion_id=f'USA:{year}:{concept}',subject_id='USA',concept=concept,scope='COUNTRY:USA',
                world_context='REAL',context_id='',perspective='GOVERNANCE',perspective_actor_id='',
                value_state=FactState.KNOWN,value=str(value),unit=units[concept],reason_code='ADMITTED',
                proposition_kind='MODEL_PROJECTION',proposition_role='EARTH_REFERENCE',epistemic_mode='MODEL_PROJECTION',
                admission_state='ADMITTED',uncertainty_state='UNCHARACTERIZED',uncertainty_ref='PROMOTED_EARTH_AUTHORITY',
                valid_from=str(year),valid_to=str(year),time_basis='CALENDAR_YEAR',available_from='2026',
                source_refs=(doc['source_snapshot_id'],doc['source_model'],f'USA:{year}'),
                source_hashes=(promotion,input_hash,content_hash((year,concept,str(value)))),
                warrant_refs=('CURRENT_PROMOTED_EARTH_AUTHORITY',),support_conflict_refs=(),dependency_refs=(),
                transformation_ref='',transformation_version='',authorization_ref=AUTHORIZATION,
                reference_role='ADOPTED_REFERENCE',exception_flags=(),record_version='CONTEXT_VALUE_V1',source_time=str(year)))
    return tuple(values),input_hash,doc


def _load_timeline():
    raw=TIMELINE_INPUT.read_bytes();doc=json.loads(raw);digest=sha256(raw).hexdigest()
    if doc.get('schema')!=TIMELINE_SCHEMA or len(doc.get('milestones',()))!=43:
        raise Build7Blocked('BUILD7_TIMELINE_PROFILE')
    if doc['source_projection_manifest']['total_milestones']!=43 or doc['usage_contract'].get('auto_unlock') is not False:
        raise Build7Blocked('BUILD7_TIMELINE_CONTRACT')
    if doc['interpretation_rules'].get('DATE_DOES_NOT_UNLOCK') is None:
        raise Build7Blocked('BUILD7_TIMELINE_UNLOCK_RULE')
    return doc,digest


def _load_solar_catalog():
    raw=SOLAR_CATALOG_INPUT.read_bytes();doc=json.loads(raw);digest=sha256(raw).hexdigest()
    if doc.get('schema')!='BUILD7_SOLAR_BODY_CATALOG_V1' or doc.get('eligible_count')!=90 or len(doc.get('bodies',()))!=90:
        raise Build7Blocked('BUILD7_SOLAR_CATALOG_PROFILE')
    body_bytes=json.dumps(doc['bodies'],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
    support_bytes=json.dumps(doc.get('supporting_bodies',()),sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
    if sha256(body_bytes).hexdigest()!=doc.get('body_rows_sha256') or sha256(support_bytes).hexdigest()!=doc.get('support_rows_sha256'):
        raise Build7Blocked('BUILD7_SOLAR_CATALOG_DIGEST')
    for ref in doc.get('source_refs',()):
        path=(REPO/ref['path']).resolve()
        if not path.is_relative_to(REPO) or not path.is_file() or _sha(path)!=ref['sha256']:
            raise Build7Blocked('BUILD7_SOLAR_CATALOG_SOURCE:'+ref['path'])
    return doc,digest


def _target_from_generated(binding: Mapping, config: Mapping) -> dict:
    scale=D(config['runtime']['kg_per_model_resource_unit'])
    if scale<=0:raise Build7Blocked('BUILD7_RESOURCE_SCALE')
    node='OFF:'+binding['body_key']+':GEN_SITE_1';site_ref='SITE:'+node
    resource=ScenarioResource('RES',node,binding['resource_class'],D(binding['block']['target_mass_kg'])/scale,None,None,None)
    named=NamedLocationBinding(
        body_id=binding['body_id'],parent_location_id=None,authored_site_id=binding['site_id'],
        local_feature_id=binding['feature_id'],scenario_id=binding['scenario_id'],model_id=binding['model_id'],
        policy_id=binding['policy_id'],world_id=binding['world_id'],world_site_id=binding['world_site_id'],
        deposit_id=binding['deposit_id'],assertion_id=None,support_id=None,admission_id=None,
        site_node_id=node,resource_id='RES',settlement_id='SET:'+binding['body_key']+':GEN_SITE_1',
        resource_unit_key='GEN_KG_V1',resource_scale=scale)
    return dict(body_key=binding['body_key'],body_name=binding['body_name'],node=node,site_ref=site_ref,
        catalog_subject=binding['body_key'],catalog_scope='BODY:'+binding['body_key'],
        site_name=binding['body_name']+' generated prospecting domain',resource=resource,binding=named,
        world_seed=None,scenario_key=binding['scenario_key'],result_hash=binding['result_hash'],world_payload={'block':binding['block']})


def _target_from_bound(reference_reader, runtime_service: str, run_id: str, binding_key: str, config: Mapping) -> dict:
    import psycopg
    with psycopg.connect(service=runtime_service) as conn:
        physical=store.load_bound_world(conn,run_id,binding_key,context='REALIZED',effective_time=D('999999'))
    realization=physical['realization']
    if realization is None or len(physical['sites'])!=1 or len(physical['deposits'])!=1:
        raise Build7Blocked('BUILD7_BOUND_WORLD_CARDINALITY')
    catalog_doc,_=_load_solar_catalog();catalog=store.read_generation_catalog(reference_reader,WA_SOURCE_SHA,catalog_doc['body_rows_sha256'])
    body=next((b for b in catalog if b['body_id']==realization['body_id']),None)
    if body is None:raise Build7Blocked('BUILD7_BOUND_BODY_NOT_IN_CATALOG')
    site=physical['sites'][0];deposit=physical['deposits'][0]
    if deposit['resource_class']!='WATER_BEARING_MATERIAL' or deposit['initial_in_situ_state']!='KNOWN' or deposit['unit_key']!='GEN_KG_V1':
        raise Build7Blocked('BUILD7_BOUND_DEPOSIT_PROFILE')
    scale=D(config['runtime']['kg_per_model_resource_unit']);node='OFF:'+body['semantic_key']+':GEN_SITE_1';site_ref='SITE:'+node
    resource=ScenarioResource('RES',node,deposit['resource_class'],D(deposit['initial_in_situ_quantity'])/scale,None,None,None)
    named=NamedLocationBinding(
        body_id=realization['body_id'],parent_location_id=None,authored_site_id=site['location_id'],local_feature_id=deposit['location_id'],
        scenario_id=realization['scenario_id'],model_id=realization['model_id'],policy_id=realization['policy_id'],world_id=realization['world_id'],
        world_site_id=site['site_id'],deposit_id=deposit['deposit_id'],assertion_id=None,support_id=None,admission_id=None,
        site_node_id=node,resource_id='RES',settlement_id='SET:'+body['semantic_key']+':GEN_SITE_1',resource_unit_key='GEN_KG_V1',resource_scale=scale)
    initial_payload={**physical,'stock_history':()}
    return dict(body_key=body['semantic_key'],body_name=body['canonical_name'],node=node,site_ref=site_ref,
        catalog_subject=body['semantic_key'],catalog_scope='BODY:'+body['semantic_key'],site_name=site['name'],resource=resource,binding=named,
        world_seed=realization['world_seed_lexeme'],scenario_key=physical['scenario_semantic_key'],result_hash=realization['generator_output_sha256'],
        world_payload=initial_payload)


def _recovery_profile(target: Mapping,config: Mapping) -> dict:
    cap=config['recovery_capability']
    return {'resource_id':'RES','node_id':target['node'],'max_depth_m':cap['max_depth_m'],
        'max_temperature_k':cap['max_temperature_k'],'max_pressure_pa':cap['max_pressure_pa'],
        'compatible_forms':tuple(cap['compatible_forms']),'recovery_yield':cap['recovery_yield'],
        'kg_per_model_unit':config['runtime']['kg_per_model_resource_unit']}


def _build_kernel(target: Mapping, config: Mapping, *, world_seed: str):
    params=dict(config['structural_parameters'])
    earth,earth_hash,earth_doc=_load_earth_authority();timeline,timeline_hash=_load_timeline();solar_catalog,solar_catalog_hash=_load_solar_catalog()
    earth_2026=next(v for v in earth if v.concept=='population' and v.valid_from=='2026')
    params.update({'resource_id':'RES','N':earth_2026.value,'reference_population_bound':earth_2026.value,
        'opening_effective_time':config['runtime']['opening_effective_time'],'time_offset':str(config['runtime']['time_offset']),
        'site_binding_key':config['runtime']['site_binding_key'],'build7.site_node_id':target['node'],'build7.site_ref':target['site_ref'],
        'build7.catalog_subject':target['catalog_subject'],'build7.catalog_scope':target['catalog_scope'],'build7.profile':PROFILE})
    config_hash=_sha(INPUT)
    comparison={'world_seed':str(world_seed),'policy_seed':config['runtime']['policy_seed'],
        'comparison_group':config['runtime']['comparison_group'],'algorithm':'SHA256_FIRST64_DECIMAL_V1',
        'key_schema':'LOOM_COMPARISON_RANDOM_V1','decimal_precision':28,'decimal_rounding':'ROUND_HALF_EVEN'}
    scenario_id=target['scenario_key']
    run_id=scenario_id+':'+content_hash((str(target['binding'].world_id),config_hash,earth_hash,timeline_hash,_sha(Path(__file__).resolve()),tuple(sorted(params.items())),tuple(sorted(comparison.items()))))[:16]

    old_policy=test_only_manifest()
    policy_values={'hurdle_rate':params['financier_hurdle_rate'],'horizon_years':params['financier_horizon_years'],
        'agent_detection_rate':params['publication_detection'],'agent_false_positive_rate':params['publication_fp'],
        'normalized_throughput':params['financier_normalized_throughput'],'max_concentration_fraction':params['financier_max_concentration_fraction']}
    policy_manifest=replace(old_policy,manifest_id='BUILD7_FINANCIER_STRUCTURAL_PARAMS_V1',
        parameters=tuple(replace(x,parameter_id='B7:'+x.parameter_id,value=D(policy_values[x.semantic_name]),authorization_ref=AUTHORIZATION,
            valid_from_version='BUILD7_V1',valid_to_version='BUILD7_V1') for x in old_policy.parameters),
        observation_knowledge_relation=ObservationKnowledgeRelation.INDEPENDENT_AGENT_LIKELIHOOD_MODEL,
        world_observation_model_ref='INDEPENDENT_AGENT_MODEL_NOT_WORLD_PARAMETER_ACCESS',world_detection_rate=None,world_false_positive_rate=None).validate(require_authorized=False)
    table_values={'PRICE':params['unit_price'],'EXPLORATION_CAPEX':params['remote_cost'],'DEVELOPMENT_CAPEX':params['capex'],
        'OPERATING_COST':params['opex_per_unit'],'LEAD_TIME':params['lead_time']}
    table=UnderwritingTable('BUILD7_STRUCTURAL_UNDERWRITING_V1','1','PRE_CONTRACT_AUTHORED_SCENARIO',
        tuple(replace(x,value=D(table_values[x.kind.value]),valid_to=20,source_or_rationale_ref=AUTHORIZATION+':STRUCTURAL_PARAMETER')
              for x in mvp_validation_underwriting_table().inputs)).validate()

    static={'exploration.REMOTE_COST':(params['remote_cost'],'MODEL_CURRENCY'),'exploration.SURFACE_COST':(params['surface_cost'],'MODEL_CURRENCY'),
        'project.RESERVE_REQUIREMENT':(params['reserve_requirement'],'MODEL_CURRENCY'),'project.REINVESTMENT_REQUIREMENT':(params['reinvestment'],'MODEL_CURRENCY'),
        'settlement.REQUESTED_RESIDENTS':(params['requested_residents'],'PERSON'),'settlement.PUBLIC_SUPPORT_COST':(params['support_cost'],'MODEL_CURRENCY')}
    for x in table.inputs:static['underwriting.'+x.kind.value]=(str(x.value),x.unit)
    earth_sim=[]
    sim_concepts={'population','value_added','gross_output','investment','capital','legacy_employment'}
    for source in earth:
        if source.concept not in sim_concepts:continue
        sim_year=str(int(source.valid_from)-2025)
        earth_sim.append(replace(source,assertion_id='SIM:'+source.assertion_id,world_context='SCENARIO',context_id=scenario_id,
            perspective='WORLD_SIM',perspective_actor_id='',proposition_kind='DERIVED_REFERENCE',epistemic_mode='CLOCK_TRANSFORMED_REFERENCE',
            valid_from=sim_year,valid_to=sim_year,time_basis='SIM_TIME',available_from='1',source_refs=(source.assertion_id,),
            source_hashes=(source.fingerprint(),),dependency_refs=(source.assertion_id,),transformation_ref='SIM_YEAR_PLUS_2025_V1',
            transformation_version='1',source_time=sim_year))
    assertions=[*earth,*earth_sim];contracts=[];bindings=[]
    for actor in ('PUB','SPN','FIN'):
        for concept,(value,unit) in static.items():
            subject='P';scope='PROJECT:P'
            if concept.startswith('exploration.'):
                subject='EXP';scope='PROJECT:EXP'
            assertions.append(_source(actor+':'+concept,subject,concept,scope,'SCENARIO',scenario_id,'AGENT',actor,value,unit,config_hash))
            contracts.append((actor,'POLICY',concept,scope,'SCENARIO','AGENT',unit,'POLICY_PARAMETER'))
        for concept,(selector,subject,unit) in flow.LIVE.items():
            if concept.startswith('opportunity.'):continue
            subject=actor if subject=='SELF' else target['node'] if subject==flow.NODE_ID else subject
            scope='AGENT:'+actor if concept.startswith('agent.') else 'PROJECT:P' if subject=='P' else target['site_ref']
            contracts.append((actor,'POLICY',concept,scope,'REALIZED','AGENT',unit,'ADMITTED_INFORMATION'))
            bindings.append((actor,concept,selector))
    assertions.extend((
        replace(_source('WA_CATALOG:BODY:'+target['body_key'],target['catalog_subject'],'opportunity.NAMED_LOCATION',target['catalog_scope'],'REAL','','AGENT','PUB',
            target['body_name'],'CATALOG_LOCATION_IDENTITY',WA_SOURCE_SHA,role='ADMITTED_CATALOG_IDENTITY',source_ref='WA_CATALOG:BODY:'+target['body_key'],epistemic_mode='CATALOG_IDENTITY'),
            proposition_kind='REAL_CATALOG_IDENTITY',authorization_ref='WA_CATALOG_IMPORT_V1'),
        _source('BUILD7_AUTHORED_SITE:'+target['body_key'],target['site_ref'],'opportunity.AUTHORED_SITE',target['site_ref'],'SCENARIO',scenario_id,'AGENT','PUB',
            target['site_name'],'AUTHORED_SITE_IDENTITY',config_hash),))
    contracts.extend((('PUB','POLICY','opportunity.NAMED_LOCATION',target['catalog_scope'],'REAL','AGENT','CATALOG_LOCATION_IDENTITY','ADMITTED_CATALOG_IDENTITY'),
        ('PUB','POLICY','opportunity.AUTHORED_SITE',target['site_ref'],'SCENARIO','AGENT','AUTHORED_SITE_IDENTITY','POLICY_PARAMETER')))

    used_methods=('add_commitment','disburse','reserve_earth_supply','explore_paid','surface_prospect_paid','update_agent_belief_from_observation',
        'publish_observation','submit_financing_request','transition_project_status','execute_development_stage','resolve_development_plan',
        'assess_resource_recoverability','spend_operating_cycle','resolve_operating_extraction','admit_realized_output_observation','clear_market_sale',
        'execute_surplus_distribution','execute_settlement_infrastructure','update_settlement_stage','execute_transport_settlement_departure',
        'execute_passenger_transport_arrival','execute_enterprise_review','record_earth_reference_year')
    allowed=[]
    for method in used_methods:
        sid='SYS:'+method;allowed.append((sid,(method,)));scope='PROCESS:'+sid
        assertions.append(_source(sid,sid,'transition.RULE',scope,'SCENARIO',scenario_id,'WORLD_SIM','',canonical((method,tuple(sorted(params.items())))),
            'TYPED_RULE',config_hash,role='TRANSITION_RULE'))
        contracts.append((sid,'SYSTEM_TRANSITION','transition.RULE',scope,'SCENARIO','WORLD_SIM','TYPED_RULE','TRANSITION_RULE'))
        if method in ('update_agent_belief_from_observation','publish_observation'):
            for actor in (('PUB',) if method=='update_agent_belief_from_observation' else ('FIN','SPN')):
                contracts.append((sid,'SYSTEM_TRANSITION','actor.BELIEF','AGENT:'+actor,'REALIZED','WORLD_SIM','PROBABILITY','ACTOR_BELIEF'))
            bindings.append((sid,'actor.BELIEF','ACTOR_BELIEF'))
        if method in ('explore_paid','surface_prospect_paid','assess_resource_recoverability'):
            contracts.append((sid,'SYSTEM_TRANSITION','R_IN_SITU',target['site_ref'],'REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
            bindings.append((sid,'R_IN_SITU','RESOURCE'))
        if method=='record_earth_reference_year':
            for concept,unit in (('population','PERSON'),('value_added','EARTH_REAL_PROXY_VALUE_ADDED_PER_YEAR'),('gross_output','EARTH_REAL_PROXY_GROSS_OUTPUT_PER_YEAR'),('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('capital','EARTH_REAL_PROXY_CAPITAL'),('legacy_employment','PERSON_FTE_PROXY')):
                contracts.append((sid,'SYSTEM_TRANSITION',concept,'COUNTRY:USA','SCENARIO','WORLD_SIM',unit,'EARTH_REFERENCE'))
        if method=='resolve_operating_extraction':
            contracts.append((sid,'SYSTEM_TRANSITION','R_RECOVERABLE',target['site_ref'],'REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
            bindings.append((sid,'R_RECOVERABLE','RESOURCE'))
        if method in ('reserve_earth_supply','explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage'):
            contracts.append((sid,'SYSTEM_TRANSITION','Earth_supply.AVAILABLE','ECONOMY:USA:SUPPLY','REALIZED','WORLD_SIM','MODEL_SUPPLY_CLAIM_CURRENCY','SUPPLIER_CAPACITY'))
            bindings.append((sid,'Earth_supply.AVAILABLE','EARTH_SUPPLY'))
        if method in ('explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage','clear_market_sale','execute_surplus_distribution'):
            for project in (('EXP',) if method in ('explore_paid','surface_prospect_paid') else ('P',)):
                contracts.append((sid,'SYSTEM_TRANSITION','project.CASH_BALANCE','PROJECT:'+project,'REALIZED','WORLD_SIM','MODEL_CURRENCY','FINANCIAL_STATE'))
            bindings.append((sid,'project.CASH_BALANCE','PROJECT_CASH'))
        if method in ('surface_prospect_paid','publish_observation','update_agent_belief_from_observation'):
            contracts.append((sid,'SYSTEM_TRANSITION','observation.SIGNAL',target['site_ref'],'REALIZED','WORLD_SIM','SIGNAL_CATEGORY','OBSERVATION'))
            bindings.append((sid,'observation.SIGNAL','OBSERVATION'))
        if method=='resolve_operating_extraction':
            contracts.append((sid,'SYSTEM_TRANSITION','cycle.PAID_OPEX','PROJECT:P','REALIZED','WORLD_SIM','TYPED_EXPENSE_RECORD','REALIZED_EXPENSE'));bindings.append((sid,'cycle.PAID_OPEX','REALIZED_COST'))
        if method=='admit_realized_output_observation':
            contracts.append((sid,'SYSTEM_TRANSITION','cycle.ACTUAL_OUTPUT',target['site_ref'],'REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','REALIZED_OUTPUT'));bindings.append((sid,'cycle.ACTUAL_OUTPUT','EXTRACTION_ACTUAL'))
    for concept,unit in [('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('population','PERSON')]:
        contracts.append(('GENESIS','EARTH_REFERENCE',concept,'COUNTRY:USA','REAL','GOVERNANCE',unit,'EARTH_REFERENCE'))

    here=Path(__file__).resolve();runtime_flow=ROOT/'runtime_flow.py';named=ROOT.parent/'build6e/named_world.py';store_path=REPO/'src/loom_world_authority/store.py'
    harness=tuple((str(p.relative_to(REPO)),_sha(p)) for p in (here,runtime_flow,named,store_path))
    authority_sources=(('EARTH_AUTHORITY:'+earth_doc['source_snapshot_id'],earth_doc['promotion_manifest_sha256']),
        ('TIMELINE:'+timeline['source_projection_manifest']['snapshot_id'],timeline['source_projection_manifest']['projection_sha256']),
        ('SOLAR_BODY_CATALOG',solar_catalog['body_rows_sha256']))
    definitions=((INPUT.name,config_hash),(TIMELINE_INPUT.name,timeline_hash),(SOLAR_CATALOG_INPUT.name,solar_catalog_hash))
    m=BoundaryManifest(BUILD6E_CONTRACT,'BUILD7_INPUT:'+content_hash((definitions,earth_hash,tuple(sorted(params.items())),authority_sources)),scenario_id,'V1',run_id,
        definitions,authority_sources,'0'*64,(('PARAMETERS:'+scenario_id,content_hash(tuple(sorted(params.items())))),
        ('FINANCIER_POLICY_PARAMETERS',policy_manifest.parameter_manifest_hash()),('WORLD_REALIZATION:'+str(target['binding'].world_id),target['result_hash']),
        ('TIMELINE_READ_ONLY',timeline_hash)),tuple(contracts),tuple(bindings),('BUILD7_COMPARISON',content_hash(tuple(sorted(comparison.items())))),
        (EARTH_INPUT.name,earth_hash),(INPUT.name,config_hash),'SIM_YEAR_PLUS_2025_V1','ODD_SCHEMA_REGISTRY_0_20',BUILD6E_AUTHORIZATION,
        tuple(assertions),tuple(sorted((str(k),str(v)) for k,v in params.items())),tuple(sorted(comparison.items())),tuple(allowed),(),harness)
    rid=RunIdentity(str(target['binding'].world_id),'BUILD7_V1',m.input_snapshot_id,BUILD6E_CONTRACT,m.parameters)
    k=MethodologyHardenedBuild4Kernel(rid,boundary_manifest=m,lambda_displacement=D(params['lambda']))
    node=target['node'];k.add_node('EARTH:USA',NodeKind.EARTH);k.add_node(node,NodeKind.OFFWORLD)
    accounts=[('public_funds','PUB','EARTH:USA',AccountKind.FUNDS,params['P']),('fin_funds','FIN','EARTH:USA',AccountKind.FUNDS,params['F']),
        ('earth_market','EARTH_MARKET','EARTH:USA',AccountKind.EARTH_BOUNDARY,params['B']),('sponsor_funds','SPN','EARTH:USA',AccountKind.FUNDS,'0'),
        ('earth_supplier','SUP','EARTH:USA',AccountKind.SUPPLIER,'0'),('transport_provider','TRANSPORT_PROVIDER','EARTH:USA',AccountKind.SUPPLIER,'0'),
        ('explore_cash','EXP',node,AccountKind.PROJECT_CASH,'0'),('project_cash','SPN',node,AccountKind.PROJECT_CASH,'0'),
        ('local_reinvest_funds','SPN',node,AccountKind.FUNDS,'0'),('local_settlement_supplier','SUP',node,AccountKind.SUPPLIER,'0'),
        ('settlement_support','SETTLEMENT',node,AccountKind.FUNDS,'0')]
    for aid,owner,where,kind,value in accounts:k.add_account(aid,owner,where,kind,D(value))
    k.add_project('EXP',node,'explore_cash',{'PUB':D(1)});k.add_project('P',node,'project_cash',{'SPN':D(1)})
    for aid,kind,account,caps,objectives in (
        ('PUB',AgentKind.PUBLIC,'public_funds',{'EXPLORE','SURFACE_PROSPECT','MIGRATE','SETTLEMENT_SUPPORT'},('PUBLIC_INFORMATION','PUBLIC_SETTLEMENT')),
        ('FIN',AgentKind.PRIVATE_FINANCIER,'fin_funds',{'FINANCE'},('RETURN',)),
        ('SPN',AgentKind.PRIVATE_SPONSOR,'sponsor_funds',{'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL','DISTRIBUTE_SURPLUS','CLOSE_PROJECT'},('RETURN',))):
        a=AgentState(aid,kind,'EARTH:USA',account,caps,objectives);key=params['belief_key.'+aid];a.priors[key]=D(params['prior']);a.beliefs[key]=D(params['prior']);k.add_agent(a)
    k.add_resource(target['resource']);k.population=PopulationLedger(int(D(params['N'])),{node:0});k.colonies[node]=ColonyState(node)
    for value in earth:
        if value.concept=='investment':
            year=int(value.valid_from)-2025;k.set_resource_constraint('EARTH:USA',year,D(value.value)/D(params['S']),D(params.get('f.'+str(year),params['f'])))
    for method in used_methods:k.add_system(SystemState('SYS:'+method,'EXISTING_TRANSITION',set(flow.OWNERS[method])))
    k.add_system(SystemState('DECISION','DECISION_ORCHESTRATION',set()));k.add_system(SystemState('AUDIT','QUALIFICATION_AUDIT',set()))
    plan=ProjectDevelopmentPlan('DEV','P','WIP-P','MINE-P','earth_supplier',node,D(params['capex']),((6,D(params['stage_amount'])),(7,D(params['stage_amount']))),8,D(params['capacity']),AUTHORIZATION)
    k.register_development_plan(plan)
    k.register_market_envelope(CommodityMarketEnvelope('MKT',10,'RES','earth_market',D(params['unit_price']),D(params['first_demand']),'MODEL_CURRENCY','MODEL_RESOURCE_UNIT_BY_FAMILY',AUTHORIZATION,'STRUCTURAL_NOT_CALIBRATED').validate())
    k.register_financing_return_claim(FinancingReturnClaim('FRC','FIN','P','fin_funds',D(params['return_claim']),('C-DEV','C-OP-9'),AUTHORIZATION,'STRUCTURAL_NOT_CALIBRATED').validate())
    k.register_settlement_infrastructure_plan(SettlementInfrastructurePlan('INFRA',11,node,'local_reinvest_funds','local_settlement_supplier',D(params['infrastructure_cost']),int(D(params['habitat_capacity'])),AUTHORIZATION,'STRUCTURAL_NOT_CALIBRATED').validate())
    tech=TechnologyCapabilityState(params['technology_state_id'],D(1),D(20),(params['transport_capability'],) if params['technology_qualified']=='TRUE' else (),AUTHORIZATION,'FIXED_2026_CAPABILITY_THROUGH_2045').validate();k.register_technology_capability_state(tech)
    rel=TransportRelationship(params['transport_relationship_id'],'EARTH:USA',node,D(1),D(20),params['transport_capability'],D(params['transport_cost']),D(params['travel_time']),D(params['energy']),D(params['loss_risk']),int(D(params['transport_capacity'])),'PASSENGER',AUTHORIZATION,'FIXED_2026_CAPABILITY_THROUGH_2045').validate()
    if params['relationship_registered']=='TRUE':k.register_transport_relationship(rel)

    genesis=[];derived=[]
    for source in earth:
        if source.concept!='investment':continue
        year=int(source.valid_from)-2025
        request=ConsumptionRequest('EARTH_SOURCE:'+str(year),'GENESIS','EARTH_REFERENCE','USA','investment','COUNTRY:USA','CALENDAR_YEAR',source.valid_from,source.available_from,'REAL','','GOVERNANCE','','ADMITTED',source.unit,'EARTH_REFERENCE')
        value,receipt=admit_for_use(k,request);transformed=earth_supply_value(value,params['S'],params.get('f.'+str(year),params['f']),year,scenario_id)
        transformed=replace(transformed,dependency_refs=(*transformed.dependency_refs,receipt.receipt_id));derived.append(transformed);genesis.append((receipt,value))
    population=earth_2026
    request=ConsumptionRequest('EARTH_POPULATION_BOUND','GENESIS','EARTH_REFERENCE','USA','population','COUNTRY:USA','CALENDAR_YEAR','2026','2026','REAL','','GOVERNANCE','','ADMITTED','PERSON','EARTH_REFERENCE')
    bound,receipt=admit_for_use(k,request);genesis.append((receipt,bound));k._boundary_genesis_inputs=tuple(genesis)
    opening_records={'profile':PROFILE,'agents':tuple(sorted(k.agents.items())),'systems':tuple(sorted(k.systems.items())),
        'projects':tuple(sorted(k.state.projects.items())),'accounts':tuple(sorted(k.state.accounts.items())),'initial_population':k.population,
        'settlement_id':target['binding'].settlement_id,'settlement_node':node,'initial_colony':k.colonies[node],
        'cohort_id':config['runtime']['cohort_id'],'population_source_receipt':receipt.receipt_id,
        'earth_supply_transformations':tuple(derived),'earth_authority_snapshot':earth_doc['source_snapshot_id'],
        'timeline_snapshot':timeline['source_projection_manifest']['snapshot_id'],'timeline_milestone_count':43,'solar_eligible_body_count':90,'technology_profile':'FIXED_2026'}
    k._boundary_authored_inputs=(table,policy_manifest,opening_records)
    m=replace(m,assertions=(*m.assertions,*derived));k.boundary_manifest=m
    opening=tuple((key,canonical(k._boundary_opening_value(key))) for key in ('accounts','agents','resources','constraints','population','earth_admission_receipts'))
    k.boundary_manifest=replace(m,opening_bindings=opening,opening_state_hash=content_hash(k._boundary_projection()))
    h={'params':params,'table':table,'manifest':policy_manifest,'timeline':timeline,'earth':earth_doc,
       'model':SurfaceProspectingModel('BUILD7_SURFACE',D(params['surface_fp']),D(params['surface_fn']),D(params['surface_detection']),D(params['surface_fp']),D(params['remote_fp']),D(params['remote_fn']),'STRUCTURAL_NOT_CALIBRATED',AUTHORIZATION).validate(),
       'recovery_profile':_recovery_profile(target,config),'target_world_payload':target['world_payload'],
       'results':[],'audits':[],'policies':{},'snapshots':{},'requests':{},'counter':0,'last_time':D(0)}
    return k,h


def _agent_logins(service_names=('agent_pub','agent_spn','agent_fin')):
    import psycopg
    result={}
    for actor,service in zip(('PUB','SPN','FIN'),service_names,strict=True):
        with psycopg.connect(service=service) as conn:result[actor]=conn.execute('select session_user').fetchone()[0]
    return result


def _attach_persistence(h,target,runtime_service,agent_logins):
    h['wa_service']=runtime_service;h['named_binding']=target['binding'];h['agent_logins']=agent_logins


def run_remote(k,h):
    p=h['params'];req=build_exploration_request('REMOTE:request',1,'EXP','RES','REMOTE')
    d,ref=flow.policy_epoch(k,h,'REMOTE','PUB','1',req,('exploration.REMOTE_COST','opportunity.NAMED_LOCATION','opportunity.AUTHORED_SITE'),workers.run_public_explorer_policy,workers.public_explorer_policy_version())
    if d.outcome.value!='AUTHORIZE':return None
    flow.system_epoch(k,h,'add_commitment','1',('C-REMOTE','PUB','EXP',d.authorized_cost),decision_refs=(ref,));flow.system_epoch(k,h,'disburse','1',(1,'C-REMOTE','public_funds',d.authorized_cost),decision_refs=(ref,));flow.system_epoch(k,h,'reserve_earth_supply','1',('EARTH:USA',1,d.authorized_cost),decision_refs=(ref,))
    obs,asset,draw=flow.system_epoch(k,h,'explore_paid','1',(1,'PUB','RES','EXP','earth_supplier',d.authorized_cost),dict(channel='REMOTE',public=False,false_positive=D(p['remote_fp']),false_negative=D(p['remote_fn']),update_belief=False,parent_ids=(d.id,)),(ref,))
    h['REMOTE']=obs;h['REMOTE_draw']=draw;flow.system_epoch(k,h,'update_agent_belief_from_observation','1',(1,'PUB',obs.id,'RES',D(p['remote_detection']),D(p['remote_fp']),'BUILD7_REMOTE',AUTHORIZATION),decision_refs=(ref,));return obs


def run_surface(k,h):
    if 'REMOTE' not in h:raise Build7Blocked('BUILD7_REMOTE_REQUIRED')
    p=h['params'];req=build_exploration_request('SURFACE:request',2,'EXP','RES','SURFACE',prerequisite_observation_id=h['REMOTE'].id)
    d,ref=flow.policy_epoch(k,h,'SURFACE','PUB','2',req,('exploration.SURFACE_COST',),workers.run_public_surface_prospector_policy,workers.public_surface_prospector_policy_version())
    if d.outcome.value!='AUTHORIZE':return None
    flow.system_epoch(k,h,'add_commitment','2',('C-SURFACE','PUB','EXP',d.authorized_cost),decision_refs=(ref,));flow.system_epoch(k,h,'disburse','2',(2,'C-SURFACE','public_funds',d.authorized_cost),decision_refs=(ref,));flow.system_epoch(k,h,'reserve_earth_supply','2',('EARTH:USA',2,d.authorized_cost),decision_refs=(ref,))
    obs,asset,draw,_=flow.system_epoch(k,h,'surface_prospect_paid','2',(2,'PUB','RES','EXP','earth_supplier',d.authorized_cost,h['REMOTE'].id,h['model']),dict(parent_ids=(d.id,)),(ref,))
    h['SURFACE']=obs;h['SURFACE_draw']=draw;flow.system_epoch(k,h,'update_agent_belief_from_observation','2',(2,'PUB',obs.id,'RES',D(p['surface_detection']),D(p['surface_fp']),'BUILD7_SURFACE',AUTHORIZATION),decision_refs=(ref,));return obs


def run_full_chain(k,h,target):
    if 'SURFACE' not in h:raise Build7Blocked('BUILD7_SURFACE_REQUIRED')
    p=h['params'];obs=h['SURFACE'];terminal='SURFACE_COMPLETE'
    req=build_publication_request('PUB:request',2,obs.id,'PUBLIC_FINANCIERS')
    d,ref=flow.policy_epoch(k,h,'PUBLICATION','PUB','2',req,(),workers.run_public_publisher_policy,workers.public_publisher_policy_version())
    if d.outcome.value!='PUBLISH':return terminal+'|NO_PUBLICATION'
    h['publication']=flow.system_epoch(k,h,'publish_observation','2',(2,'PUB',obs.id,req.audience,(('FIN','resource_exists',D(p['publication_detection']),D(p['publication_fp'])),('SPN','resource_exists',D(p['publication_detection']),D(p['publication_fp'])))),decision_refs=(ref,))
    req=build_sponsor_project_request('SPONSOR:request',3,'P','RES',obs.id)
    d,ref=flow.policy_epoch(k,h,'SPONSOR','SPN','3',req,('project.STATUS','project.CASH_BALANCE','underwriting.DEVELOPMENT_CAPEX'),workers.run_sponsor_operator_policy,workers.sponsor_operator_policy_version())
    if d.outcome.value=='ABANDON':
        flow.system_epoch(k,h,'transition_project_status','3',(3,'SPN','P','ABANDONED',d.id),decision_refs=(ref,));return 'ABANDONED'
    if d.outcome.value!='REQUEST_FINANCE':return 'SPONSOR_STOP:'+d.outcome.value
    q=build_financing_request('DEV-FIN',3,'SPN','P',d.requested_financing,'DEVELOPMENT',(obs.id,));flow.system_epoch(k,h,'submit_financing_request','3',(q,),decision_refs=(ref,))
    fd,_=flow.finance(k,h,'DEV_FINANCE',4,q)
    if fd.outcome.value!='APPROVE':return 'FINANCE_'+fd.outcome.value
    req=build_sponsor_project_request('DEVELOP:request',5,'P','RES',obs.id)
    d,ref=flow.policy_epoch(k,h,'DEVELOP','SPN','5',req,('project.STATUS','project.CASH_BALANCE','underwriting.DEVELOPMENT_CAPEX'),workers.run_sponsor_operator_policy,workers.sponsor_operator_policy_version())
    if d.outcome.value!='DEVELOP':return 'DEVELOP_'+d.outcome.value
    flow.system_epoch(k,h,'transition_project_status','5',(5,'SPN','P','DEVELOPMENT',d.id),decision_refs=(ref,))
    for year in (6,7):flow.system_epoch(k,h,'execute_development_stage',str(year),(year,'DEV'),decision_refs=(ref,))
    flow.system_epoch(k,h,'resolve_development_plan','8',(8,'DEV'),decision_refs=(ref,))
    if k.state.projects['P'].status!='OPERATING':return 'DEVELOPMENT_FAILED'
    assessed=bind_generated_target(h['target_world_payload'],h['recovery_profile'])
    flow.system_epoch(k,h,'assess_resource_recoverability','8',(8,'RES',assessed))
    h['recovery_assessment']=assessed
    first=flow.operate(k,h,'FIRST_OPERATING',9,obs);h['first_output']=first
    if first is None:return 'OPERATING_STOP'
    req=build_sale_decision_request('SALE:request',10,'P','RES','MKT',obs.id)
    d,ref=flow.policy_epoch(k,h,'SALE','SPN','10',req,('project.STATUS','inventory.AVAILABLE','market.UNIT_PRICE','market.REMAINING_DEMAND'),workers.run_sponsor_sale_policy,workers.sponsor_sale_policy_version())
    if d.outcome.value!='OFFER':flow.review(k,h,'ZERO_OUTPUT_REVIEW',10,first);return 'NO_SALE:'+d.outcome.value
    req=h['requests']['SALE'];h['sale']=flow.system_epoch(k,h,'clear_market_sale','10',(10,'SPN',req,d),decision_refs=(ref,))
    req=build_surplus_distribution_request('DISTRIBUTE:request',10,'P','FRC')
    d,ref=flow.policy_epoch(k,h,'DISTRIBUTE','SPN','10',req,('project.STATUS','project.CASH_BALANCE','project.RESERVE_REQUIREMENT','financing.RETURN_CLAIM_REMAINING','project.REINVESTMENT_REQUIREMENT'),workers.run_sponsor_surplus_policy,workers.sponsor_surplus_policy_version())
    if d.outcome.value=='DISTRIBUTE':
        req=h['requests']['DISTRIBUTE'];h['distribution']=flow.system_epoch(k,h,'execute_surplus_distribution','10',(10,'SPN',req,d,'local_reinvest_funds'),decision_refs=(ref,))
        flow.system_epoch(k,h,'execute_settlement_infrastructure','11',(11,'INFRA','SPN'),decision_refs=(ref,));flow.system_epoch(k,h,'update_settlement_stage','11',(11,target['node']))
        req=build_transport_settlement_request('TRANSPORT:request',D(p['departure']),'EARTH:USA',target['node'],'settlement_support','transport_provider',int(D(p['requested_residents'])),D(p['support_cost']),p['transport_relationship_id'],p['technology_state_id'])
        concepts=('settlement.STAGE','settlement.HABITAT_HEADROOM','settlement.REQUESTED_RESIDENTS','population.EARTH_AVAILABLE','settlement.PUBLIC_SUPPORT_COST',*(key for key in flow.LIVE if key.startswith(('transport.','technology.'))))
        td,tref=flow.policy_epoch(k,h,'TRANSPORT','PUB',p['departure'],req,concepts,workers.run_public_settlement_transport_policy,workers.public_settlement_transport_policy_version())
        if td.outcome.value=='AUTHORIZE':
            dep=flow.system_epoch(k,h,'execute_transport_settlement_departure',p['departure'],('PUB',req,td),decision_refs=(tref,));flow.system_epoch(k,h,'execute_passenger_transport_arrival',str(dep.arrival_time),(dep.arrival_time,dep.departure_id),decision_refs=(tref,))
    flow.review(k,h,'FIRST_REVIEW',14,first)
    if k.state.projects['P'].status!='OPERATING':return 'REVIEW_CLOSED'
    second=flow.operate(k,h,'SECOND_OPERATING',15,obs);h['second_output']=second
    if second is not None:flow.review(k,h,'SECOND_REVIEW',15,second)
    validate_trace(k.causal_envelopes,k.causal_artifacts)
    return 'OPERATING' if k.state.projects['P'].status=='OPERATING' else k.state.projects['P'].status


def advance_earth_to_horizon(k,h):
    """Advance admitted Earth context to 2045 after the active Offworld chain."""
    econ={int(r['year']):r for r in h['earth']['economic']};demo={int(r['year']):r for r in h['earth']['demographic']};labor={int(r['year']):r for r in h['earth']['legacy_labor']}
    start=max(1,int(D(h['last_time']))+1)
    for sim_year in range(start,21):
        cal=sim_year+2025;e=econ[cal];d=demo[cal];l=labor[cal]
        flow.system_epoch(k,h,'record_earth_reference_year',str(sim_year),(sim_year,cal,'USA',d['biological_population'],e['value_added'],e['gross_output'],e['investment'],e['capital'],l['legacy_employment']))
    return h['last_time']


def _summary(k,h,target,*,generated_status=None):
    r=k.resources['RES'];colony=k.colonies[target['node']]
    return dict(run_id=k.boundary_manifest.run_id,body=target['body_key'],world_id=str(target['binding'].world_id),generated_status=generated_status,
        last_sim_year=str(h['last_time']),last_calendar_year=2025+int(D(h['last_time'])),timeline_milestones=len(h['timeline']['milestones']),
        earth_snapshot=h['earth']['source_snapshot_id'],technology_profile='FIXED_2026',project_status=k.state.projects['P'].status,
        hidden_in_situ_model_units=str(r.in_situ),accessible_model_units=None if r.accessible is None else str(r.accessible),
        recoverable_remaining_model_units=None if r.remaining is None else str(r.remaining),offworld_population=colony.population,
        epoch_commits=tuple(h.get('epoch_commits',())))


def start_campaign(*,reference_service,science_writer_service,world_writer_service,runtime_service,world_seed,body,science_cutoff,authorization_ref=AUTHORIZATION,full=False):
    import psycopg
    config=load_config();body=body.upper()
    solar_catalog,_=_load_solar_catalog()
    with psycopg.connect(service=reference_service) as reader, psycopg.connect(service=science_writer_service) as science, psycopg.connect(service=world_writer_service) as writer:
        catalog_status=store.install_generation_body_catalog(science,solar_catalog)
        generated=generate_solar_system(reader,science,writer,seed=world_seed,authorization_ref=authorization_ref,science_cutoff=science_cutoff,return_bindings=True,supplemental_catalog_sha256=solar_catalog['body_rows_sha256'])
    if body not in generated['_bindings']:raise Build7Blocked('BUILD7_BODY_NOT_GENERATED:'+body)
    target=_target_from_generated(generated['_bindings'][body],config);target['world_seed']=world_seed
    k,h=_build_kernel(target,config,world_seed=world_seed);_attach_persistence(h,target,runtime_service,_agent_logins())
    remote=run_remote(k,h);h['terminal']='REMOTE' if not full else None
    if full:
        surface=run_surface(k,h);h['terminal']='NO_SURFACE' if surface is None else run_full_chain(k,h,target)
        advance_earth_to_horizon(k,h)
    result=_summary(k,h,target,generated_status=generated['status']);result['catalog_status']=catalog_status;result['generated_body_count']=generated['body_count'];result['remote_signal']=None if remote is None else remote.signal;result['terminal']=h['terminal'];return result


def resume_campaign(*,reference_service,runtime_service,run_id,full=True):
    import psycopg
    config=load_config()
    with psycopg.connect(service=reference_service) as reader:target=_target_from_bound(reader,runtime_service,run_id,config['runtime']['site_binding_key'],config)
    k,h=_build_kernel(target,config,world_seed=target['world_seed']);_attach_persistence(h,target,runtime_service,_agent_logins())
    remote=run_remote(k,h);surface=run_surface(k,h);terminal='SURFACE_COMPLETE'
    if full and surface is not None:terminal=run_full_chain(k,h,target)
    if full:advance_earth_to_horizon(k,h)
    if k.boundary_manifest.run_id!=run_id:raise Build7Blocked('BUILD7_RESUME_RUN_ID_MISMATCH')
    result=_summary(k,h,target);result.update(remote_signal=None if remote is None else remote.signal,surface_signal=None if surface is None else surface.signal,terminal=terminal);return result


def main(argv=None):
    ap=argparse.ArgumentParser(description='LOOM Offworld Build 7 integrated generated-WORLD campaign')
    sub=ap.add_subparsers(dest='command',required=True)
    new=sub.add_parser('new');new.add_argument('--reference-service',default='reference_reader');new.add_argument('--science-writer-service',default='science_writer');new.add_argument('--world-writer-service',default='world_writer');new.add_argument('--runtime-service',default='runtime');new.add_argument('--world-seed',required=True);new.add_argument('--body',required=True);new.add_argument('--science-cutoff',type=int,default=0);new.add_argument('--full',action='store_true')
    resume=sub.add_parser('resume');resume.add_argument('--reference-service',default='reference_reader');resume.add_argument('--runtime-service',default='runtime');resume.add_argument('--run-id',required=True);resume.add_argument('--opening-only',action='store_true')
    args=ap.parse_args(argv)
    result=start_campaign(reference_service=args.reference_service,science_writer_service=args.science_writer_service,world_writer_service=args.world_writer_service,runtime_service=args.runtime_service,world_seed=args.world_seed,body=args.body,science_cutoff=args.science_cutoff,full=args.full) if args.command=='new' else resume_campaign(reference_service=args.reference_service,runtime_service=args.runtime_service,run_id=args.run_id,full=not args.opening_only)
    print(json.dumps(result,sort_keys=True,default=str))


if __name__=='__main__':main()
