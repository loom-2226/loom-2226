"""Strict Build 6E composition of qualified executors and workers.

This is a qualification adapter, not another runtime or economic model.
"""
from dataclasses import fields, is_dataclass, replace
from decimal import Decimal as D
from hashlib import sha256
from pathlib import Path
import json

from offworld_kernel.boundary import (BUILD6E_AUTHORIZATION as AUTHORIZATION,BUILD6E_CONTRACT as CONTRACT,BoundaryManifest,ContextValue,ConsumptionRequest,
    admit_for_use,snapshot_facts,load_earth_assertions,earth_supply_value)
from offworld_kernel.causal_trace import canonical,content_hash,validate_trace
from offworld_kernel.build3 import RunIdentity
from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
from offworld_kernel.model import AccountKind,NodeKind
from offworld_kernel.mvp_state import AgentKind,AgentState,ScenarioResource,SystemState,PopulationLedger,ColonyState,RuntimeObjectClass
from offworld_kernel.policy import FactState,build_decision_snapshot
from offworld_kernel.scheduler import CouplingSpec,ScheduledEvent,Phase
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.accounting import AccountingPeriodSnapshot,AccountingIdentityAuditor
from offworld_kernel.project_lifecycle import ProjectDevelopmentPlan
from offworld_kernel.surface_prospecting import SurfaceProspectingModel
from offworld_kernel.market import CommodityMarketEnvelope
from offworld_kernel.distribution import FinancingReturnClaim
from offworld_kernel.settlement import SettlementInfrastructurePlan
from offworld_kernel.transport import TechnologyCapabilityState,TransportRelationship
from offworld_kernel.underwriting import UnderwritingTable,mvp_validation_underwriting_table,underwriting_snapshot_facts
from offworld_kernel.policies.manifest import test_only_manifest,policy_source_bytes,ObservationKnowledgeRelation
from offworld_kernel import policy_runner as workers
from offworld_kernel.exploration_protocol import build_exploration_request
from offworld_kernel.publication_protocol import build_publication_request
from offworld_kernel.sponsor_protocol import build_sponsor_project_request
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.operating_protocol import build_operating_cycle_request
from offworld_kernel.market_protocol import build_sale_decision_request
from offworld_kernel.distribution_protocol import build_surplus_distribution_request
from offworld_kernel.enterprise import build_enterprise_review_request
from offworld_kernel.transport_protocol import build_transport_settlement_request
from loom_world_authority.etl import SOURCE_SHA as WA_SOURCE_SHA

BASE=Path(__file__).resolve().parents[1]
EARTH_PARENT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')
SCENARIO_PATH=BASE/'inputs/BUILD6E_NAMED_WORLD_V1.json'
EARTH_PATH=BASE/'inputs/BUILD6E_EARTH_REFERENCE_SLICE_V1.json'
PROTOCOL_PATH=BASE/'inputs/BUILD6E_QUALIFICATION_V1.json'
NODE_ID='OFF:MOON:CABEU:B6E_SITE_01'

# Existing store names are explicit ownership declarations, not a second ledger.
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
}
LIVE={
'agent.STATE':('AGENT_STATE','SELF','TYPED_AGENT_STATE'),
'agent.BELIEF':('BELIEF','SELF','PROBABILITY'),'agent.PRIOR':('PRIOR','SELF','PROBABILITY'),
'observation.SIGNAL':('OBSERVATION','OBSERVATION','SIGNAL_CATEGORY'),
'information.ARTIFACT':('PUBLIC_INFORMATION','INFORMATION','TYPED_INFORMATION_ARTIFACT'),
'project.STATUS':('PROJECT:P:STATUS','P','STATUS_CATEGORY'),
'project.CASH_BALANCE':('PROJECT:P:CASH','P','MODEL_CURRENCY'),
'asset.CAPACITY':('ASSET:MINE-P:CAPACITY','P','MODEL_RESOURCE_UNIT_PER_CYCLE'),
'inventory.AVAILABLE':('COLONY:INVENTORY','OFF:MOON:CABEU:B6E_SITE_01','MODEL_RESOURCE_UNIT_BY_FAMILY'),
'market.UNIT_PRICE':('MARKET:PRICE','MKT','MODEL_CURRENCY_PER_RESOURCE_UNIT'),
'market.REMAINING_DEMAND':('MARKET:DEMAND','MKT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
'financing.RETURN_CLAIM_REMAINING':('CLAIM','FRC','MODEL_CURRENCY'),
'settlement.STAGE':('COLONY:STAGE','OFF:MOON:CABEU:B6E_SITE_01','STATUS_CATEGORY'),
'settlement.HABITAT_HEADROOM':('COLONY:HEADROOM','OFF:MOON:CABEU:B6E_SITE_01','PERSON'),
'population.EARTH_AVAILABLE':('POPULATION','EARTH:USA','PERSON'),
'cycle.PLANNED_QUANTITY':('EXTRACTION_PLANNED','OUTPUT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
'cycle.ACTUAL_OUTPUT':('EXTRACTION_ACTUAL','OUTPUT','MODEL_RESOURCE_UNIT_BY_FAMILY'),
}
for key,unit in [('AVAILABLE','BOOLEAN'),('RELATIONSHIP_ID','IDENTITY'),('CAPACITY','PERSON'),('COST_PER_PASSENGER','MODEL_CURRENCY_PER_PERSON'),('TRAVEL_TIME','SIM_TIME_DURATION'),('ENERGY_PER_PASSENGER','MODEL_ENERGY_PER_PERSON'),('LOSS_RISK','PROBABILITY')]:
    LIVE['transport.'+key]=('TRANSPORT:'+key,'TR-USA-B6E',unit)
LIVE['technology.STATE_ID']=('TRANSPORT:STATE_ID','TECH-B6E','IDENTITY')
LIVE['opportunity.NAMED_LOCATION']=('CATALOG:MOON:CABEU','MOON:CABEU','CATALOG_LOCATION_IDENTITY')
LIVE['opportunity.AUTHORED_SITE']=('SCENARIO_SITE','SITE:OFF:MOON:CABEU:B6E_SITE_01','AUTHORED_SITE_IDENTITY')


def _source(assertion_id,subject,concept,scope,context,context_id,perspective,actor,value,unit,source_hash,role='POLICY_PARAMETER'):
    return ContextValue(assertion_id,subject,concept,scope,context,context_id,perspective,actor,
        FactState.UNKNOWN if value is None else FactState.KNOWN,value,unit,'ADMITTED',
        'AUTHORED_SCENARIO_PARAMETER',role,'AUTHORED_SCENARIO','ADMITTED','UNCHARACTERIZED','NOT_SUPPLIED',
        '0','20','SIM_TIME','0',('BUILD6E_NAMED_WORLD_V1',),(source_hash,),(AUTHORIZATION,),(),(),'', '',AUTHORIZATION,
        'NOT_EARTH_REFERENCE',(('empirical_calibration','NOT_SUPPLIED'),),'CONTEXT_VALUE_V1','0')


def make_kernel(world='RICH',overrides=None,*,world_seed=None,policy_seed=None,source_row=None):
    doc=json.loads(SCENARIO_PATH.read_text())
    params={**doc['g4_structural_parameters'],**(overrides or {})}
    params.update({
        'resource_id':doc['world_generation']['resource_id'],
        'belief_key.PUB':doc['g4_structural_parameters']['belief_key.PUB'],
        'belief_key.SPN':doc['g4_structural_parameters']['belief_key.SPN'],
        'belief_key.FIN':doc['g4_structural_parameters']['belief_key.FIN'],
        'reference_population_bound':'349892943',
        'node_id':doc['runtime']['node_id'],
        'time_offset':int(doc['runtime']['time_offset']),
        'departure':doc['g4_structural_parameters']['departure'],
        'arrival':doc['g4_structural_parameters']['arrival'],
        'opening_effective_time':doc['runtime']['opening_effective_time'],
        'named_site_id':doc['runtime']['site_id'],
        'named_feature_id':doc['runtime']['feature_id'],
        'site_binding_key':doc['runtime']['site_binding_key'],
    })
    doc['worlds']={k:v['recoverable'] for k,v in doc['world_generation']['scenarios'].items()}
    doc['comparison']={
        'world_seed':doc['world_generation']['world_seed'] if world_seed is None else str(world_seed),
        'policy_seed':doc['world_generation']['policy_seed'] if policy_seed is None else str(policy_seed),
        'comparison_group':doc['world_generation']['comparison_group'],
        'algorithm':doc['world_generation']['random_algorithm'],
        'key_schema':doc['world_generation']['key_schema'],
        'decimal_precision':28,
        'decimal_rounding':'ROUND_HALF_EVEN',
    }
    definitions=tuple((p.name,sha256(p.read_bytes()).hexdigest()) for p in (SCENARIO_PATH,PROTOCOL_PATH))
    earth,earth_hash=load_earth_assertions(EARTH_PATH,parent_root=EARTH_PARENT)
    scenario_id='B6E:'+content_hash((tuple(sorted(params.items())),world,doc['worlds'][world],doc['world_generation']['model_version'],doc['world_generation']['policy_version'],tuple(sorted(doc['comparison'].items()))))[:16]
    run_id=scenario_id+':'+world
    old_policy=test_only_manifest()
    policy_values={'hurdle_rate':params['financier_hurdle_rate'],'horizon_years':params['financier_horizon_years'],
                   'agent_detection_rate':params['publication_detection'],'agent_false_positive_rate':params['publication_fp'],
                   'normalized_throughput':params['financier_normalized_throughput'],'max_concentration_fraction':params['financier_max_concentration_fraction']}
    policy_manifest=replace(old_policy,manifest_id='BUILD6E_FINANCIER_STRUCTURAL_PARAMS_V1',
        parameters=tuple(replace(x,parameter_id='B6E:'+x.parameter_id,value=D(policy_values[x.semantic_name]),authorization_ref=AUTHORIZATION,valid_from_version='BUILD6E_V1',valid_to_version='BUILD6E_V1') for x in old_policy.parameters),
        observation_knowledge_relation=ObservationKnowledgeRelation.INDEPENDENT_AGENT_LIKELIHOOD_MODEL,
        world_observation_model_ref='INDEPENDENT_AGENT_MODEL_NOT_WORLD_PARAMETER_ACCESS',world_detection_rate=None,world_false_positive_rate=None).validate(require_authorized=False)
    table_values={'PRICE':params['unit_price'],'EXPLORATION_CAPEX':params['remote_cost'],'DEVELOPMENT_CAPEX':params['capex'],'OPERATING_COST':params['opex_per_unit'],'LEAD_TIME':params['lead_time']}
    table=UnderwritingTable('BUILD6D_VALIDATION_UNDERWRITING_V1','1','PRE_CONTRACT_AUTHORED_SCENARIO',tuple(replace(x,value=D(table_values[x.kind.value]),valid_to=20,source_or_rationale_ref=AUTHORIZATION+':STRUCTURAL_BRANCH_PARAMETER') for x in mvp_validation_underwriting_table().inputs)).validate()
    static={'exploration.REMOTE_COST':(params['remote_cost'],'MODEL_CURRENCY'),
            'exploration.SURFACE_COST':(params['surface_cost'],'MODEL_CURRENCY'),
            'project.RESERVE_REQUIREMENT':(params['reserve_requirement'],'MODEL_CURRENCY'),
            'project.REINVESTMENT_REQUIREMENT':(params['reinvestment'],'MODEL_CURRENCY'),
            'settlement.REQUESTED_RESIDENTS':(params['requested_residents'],'PERSON'),
            'settlement.PUBLIC_SUPPORT_COST':(params['support_cost'],'MODEL_CURRENCY')}
    for x in table.inputs:static['underwriting.'+x.kind.value]=(str(x.value),x.unit)
    assertions=list(earth);contracts=[];bindings=[]
    for actor in ('PUB','SPN','FIN'):
        for concept,(value,unit) in static.items():
            scope='PROJECT:P';subject='P'
            assertions.append(_source(actor+':'+concept,subject,concept,scope,'SCENARIO',scenario_id,'AGENT',actor,value,unit,definitions[0][1]))
            contracts.append((actor,'POLICY',concept,scope,'SCENARIO','AGENT',unit,'POLICY_PARAMETER'))
        for concept,(selector,subject,unit) in LIVE.items():
            if concept.startswith('opportunity.'):
                continue
            subject=actor if subject=='SELF' else subject
            scope='AGENT:'+actor if concept.startswith('agent.') else 'PROJECT:P' if subject=='P' else 'SITE:OFF:MOON:CABEU:B6E_SITE_01'
            contracts.append((actor,'POLICY',concept,scope,'REALIZED','AGENT',unit,'ADMITTED_INFORMATION'))
            bindings.append((actor,concept,selector))
    assertions.extend((
        replace(_source('WA_CATALOG:MOON:CABEU','MOON:CABEU','opportunity.NAMED_LOCATION',
            'LOCATION:MOON:CABEU','REAL','','AGENT','PUB','Moon — Cabeus crater',
            'CATALOG_LOCATION_IDENTITY',definitions[0][1],role='ADMITTED_CATALOG_IDENTITY'),
            source_refs=('WA_CATALOG:MOON:CABEU',),source_hashes=(WA_SOURCE_SHA,),
            proposition_kind='REAL_CATALOG_IDENTITY',epistemic_mode='CATALOG_IDENTITY',
            authorization_ref='WA_CATALOG_IMPORT_V1'),
        _source('B6E_AUTHORED:SITE01','SITE:OFF:MOON:CABEU:B6E_SITE_01','opportunity.AUTHORED_SITE',
            'SITE:OFF:MOON:CABEU:B6E_SITE_01','SCENARIO',scenario_id,'AGENT','PUB',
            'Moon — Cabeus region, authored site01','AUTHORED_SITE_IDENTITY',definitions[0][1]),
    ))
    contracts.extend((
        ('PUB','POLICY','opportunity.NAMED_LOCATION','LOCATION:MOON:CABEU','REAL','AGENT','CATALOG_LOCATION_IDENTITY','ADMITTED_INFORMATION'),
        ('PUB','POLICY','opportunity.AUTHORED_SITE','SITE:OFF:MOON:CABEU:B6E_SITE_01','SCENARIO','AGENT','AUTHORED_SITE_IDENTITY','POLICY_PARAMETER'),
    ))
    allowed=[]
    for method in OWNERS:
        sid='SYS:'+method;allowed.append((sid,(method,)))
        scope='PROCESS:'+sid
        assertions.append(_source(sid,sid,'transition.RULE',scope,'SCENARIO',scenario_id,'WORLD_SIM','',canonical((method,tuple(sorted(params.items())))), 'TYPED_RULE',definitions[0][1],role='TRANSITION_RULE'))
        contracts.append((sid,'SYSTEM_TRANSITION','transition.RULE',scope,'SCENARIO','WORLD_SIM','TYPED_RULE','TRANSITION_RULE'))
        if method in ('update_agent_belief_from_observation','publish_observation'):
            for actor in (('PUB',) if method=='update_agent_belief_from_observation' else ('FIN','SPN')):
                contracts.append((sid,'SYSTEM_TRANSITION','actor.BELIEF','AGENT:'+actor,'REALIZED','WORLD_SIM','PROBABILITY','ACTOR_BELIEF'))
            bindings.append((sid,'actor.BELIEF','ACTOR_BELIEF'))
        if method in ('explore_paid','surface_prospect_paid','resolve_operating_extraction'):
            contracts.append((sid,'SYSTEM_TRANSITION','R_RECOVERABLE','SITE:OFF:MOON:CABEU:B6E_SITE_01','REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
            bindings.append((sid,'R_RECOVERABLE','RESOURCE'))
        if method in ('reserve_earth_supply','explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage'):
            contracts.append((sid,'SYSTEM_TRANSITION','Earth_supply.AVAILABLE','ECONOMY:USA:SUPPLY','REALIZED','WORLD_SIM','MODEL_SUPPLY_CLAIM_CURRENCY','SUPPLIER_CAPACITY'))
            bindings.append((sid,'Earth_supply.AVAILABLE','EARTH_SUPPLY'))
        if method in ('explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage','clear_market_sale','execute_surplus_distribution'):
            for scope in ('PROJECT:P','PROJECT:EXP'):
                contracts.append((sid,'SYSTEM_TRANSITION','project.CASH_BALANCE',scope,'REALIZED','WORLD_SIM','MODEL_CURRENCY','FINANCIAL_STATE'))
            bindings.append((sid,'project.CASH_BALANCE','PROJECT_CASH'))
        if method in ('surface_prospect_paid','publish_observation','update_agent_belief_from_observation'):
            contracts.append((sid,'SYSTEM_TRANSITION','observation.SIGNAL','SITE:OFF:MOON:CABEU:B6E_SITE_01','REALIZED','WORLD_SIM','SIGNAL_CATEGORY','OBSERVATION'))
            bindings.append((sid,'observation.SIGNAL','OBSERVATION'))
        if method=='resolve_operating_extraction':
            contracts.append((sid,'SYSTEM_TRANSITION','cycle.PAID_OPEX','PROJECT:P','REALIZED','WORLD_SIM','TYPED_EXPENSE_RECORD','REALIZED_EXPENSE'))
            bindings.append((sid,'cycle.PAID_OPEX','REALIZED_COST'))
        if method=='admit_realized_output_observation':
            contracts.append((sid,'SYSTEM_TRANSITION','cycle.ACTUAL_OUTPUT','SITE:OFF:MOON:CABEU:B6E_SITE_01','REALIZED','WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','REALIZED_OUTPUT'))
            bindings.append((sid,'cycle.ACTUAL_OUTPUT','EXTRACTION_ACTUAL'))
    for concept in ('R_IN_SITU','R_ACCESSIBLE','R_RECOVERABLE','R_RESERVE'):
        for context,context_id in (('SCENARIO',scenario_id),('REALIZED',run_id)):
            contracts.append(('AUDIT','QUALIFICATION',concept,'SITE:OFF:MOON:CABEU:B6E_SITE_01',context,'WORLD_SIM','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
            if context=='SCENARIO':assertions.append(replace(_source(context+concept,'RES',concept,'SITE:OFF:MOON:CABEU:B6E_SITE_01',context,context_id,'WORLD_SIM','',None if concept=='R_RESERVE' else doc['worlds'][world],'MODEL_RESOURCE_UNIT_BY_FAMILY',definitions[0][1],role='PHYSICAL_STATE'),proposition_kind='SCENARIO_STIPULATION',epistemic_mode='SCENARIO_STIPULATION'))
        contracts.append(('GENESIS','QUALIFICATION',concept,'SITE:OFF:MOON:CABEU:B6E_SITE_01','REAL','GOVERNANCE','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE'))
        bindings.append(('AUDIT',concept,'RESOURCE'))
    for concept,unit in [('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('population','PERSON')]:
        contracts.append(('GENESIS','EARTH_REFERENCE',concept,'COUNTRY:USA','REAL','GOVERNANCE',unit,'EARTH_REFERENCE'))
    root=BASE.parent.parent.parent
    harness_paths=(root/'simulation/offworld_mvp/build6e/qualification/qualify_build6e.py',
        Path(__file__),root/'simulation/offworld_mvp/build6e/named_world.py',root/'src/loom_world_authority/store.py')
    harness=tuple((str(p.relative_to(root)),sha256(p.read_bytes()).hexdigest()) for p in harness_paths if p.is_file())
    authority_sources=tuple((s.source_refs[0],s.source_hashes[0]) for s in earth[::2])
    if source_row is not None:
        authority_sources=(*authority_sources,
            ('WA_ASSERTION:'+str(source_row['semantic_key']),source_row['metadata_sha256']),
            ('WA_SOURCE_SNAPSHOT:'+str(source_row['snapshot_id']),doc['accepted_source']['source_snapshot_sha256']))
    m=BoundaryManifest(CONTRACT,'BUILD6E_INPUT:'+content_hash((definitions,earth_hash,tuple(sorted(params.items())),authority_sources)),scenario_id,'V1',run_id,
        definitions,authority_sources,'0'*64,
        (('PARAMETERS:'+scenario_id,content_hash(tuple(sorted(params.items())))),('FINANCIER_POLICY_PARAMETERS',policy_manifest.parameter_manifest_hash())),tuple(contracts),tuple(bindings),
        ('COMPARISON_RANDOM_V1',content_hash(tuple(sorted(doc['comparison'].items())))),(EARTH_PATH.name,earth_hash),
        (PROTOCOL_PATH.name,definitions[1][1]),'SIM_YEAR_PLUS_2025_V1','ODD_SCHEMA_REGISTRY_0_20',AUTHORIZATION,
        tuple(assertions),tuple(sorted(params.items())),tuple(sorted(doc['comparison'].items())),tuple(allowed),(),harness)
    rid=RunIdentity(world,'BUILD6E_V1',m.input_snapshot_id,CONTRACT,m.parameters)
    k=MethodologyHardenedBuild4Kernel(rid,boundary_manifest=m,lambda_displacement=D(params['lambda']))
    k.add_node('EARTH:USA',NodeKind.EARTH);k.add_node('OFF:MOON:CABEU:B6E_SITE_01',NodeKind.OFFWORLD)
    for aid,owner,node,kind,value in [('public_funds','PUB','EARTH:USA',AccountKind.FUNDS,params['P']),('fin_funds','FIN','EARTH:USA',AccountKind.FUNDS,params['F']),('earth_market','EARTH_MARKET','EARTH:USA',AccountKind.EARTH_BOUNDARY,params['B']),('sponsor_funds','SPN','EARTH:USA',AccountKind.FUNDS,'0'),('earth_supplier','SUP','EARTH:USA',AccountKind.SUPPLIER,'0'),('transport_provider','TRANSPORT_PROVIDER','EARTH:USA',AccountKind.SUPPLIER,'0'),('explore_cash','EXP','OFF:MOON:CABEU:B6E_SITE_01',AccountKind.PROJECT_CASH,'0'),('project_cash','SPN','OFF:MOON:CABEU:B6E_SITE_01',AccountKind.PROJECT_CASH,'0'),('local_reinvest_funds','SPN','OFF:MOON:CABEU:B6E_SITE_01',AccountKind.FUNDS,'0'),('local_settlement_supplier','SUP','OFF:MOON:CABEU:B6E_SITE_01',AccountKind.SUPPLIER,'0'),('settlement_support','SETTLEMENT','OFF:MOON:CABEU:B6E_SITE_01',AccountKind.FUNDS,'0')]:k.add_account(aid,owner,node,kind,D(value))
    k.add_project('EXP','OFF:MOON:CABEU:B6E_SITE_01','explore_cash',{'PUB':D(1)});k.add_project('P','OFF:MOON:CABEU:B6E_SITE_01','project_cash',{'SPN':D(1)})
    for aid,kind,account,caps,objectives in [('PUB',AgentKind.PUBLIC,'public_funds',{'EXPLORE','SURFACE_PROSPECT','MIGRATE','SETTLEMENT_SUPPORT'},('PUBLIC_INFORMATION','PUBLIC_SETTLEMENT')),('FIN',AgentKind.PRIVATE_FINANCIER,'fin_funds',{'FINANCE'},('RETURN',)),('SPN',AgentKind.PRIVATE_SPONSOR,'sponsor_funds',{'REQUEST_FINANCE','DEVELOP','OPERATE','EXTRACT','SELL','DISTRIBUTE_SURPLUS','CLOSE_PROJECT'},('RETURN',))]:
        key=params['belief_key.'+aid];a=AgentState(aid,kind,'EARTH:USA',account,caps,objectives)
        a.priors[key]=D(params['prior']);a.beliefs[key]=D(params['prior']);k.add_agent(a)
    q=D(doc['worlds'][world]);k.add_resource(ScenarioResource('RES','OFF:MOON:CABEU:B6E_SITE_01',doc['world_generation']['resource_family'],q,q,q,q))
    k.population=PopulationLedger(int(params['N']),{'OFF:MOON:CABEU:B6E_SITE_01':0});k.colonies['OFF:MOON:CABEU:B6E_SITE_01']=ColonyState('OFF:MOON:CABEU:B6E_SITE_01')
    for value in earth:
        if value.concept=='investment':
            y=int(value.valid_from)-2025
            k.set_resource_constraint('EARTH:USA',y,D(value.value)/D(params['S']),D(params.get('f.'+str(y),params['f'])))
    for method,owned in OWNERS.items():k.add_system(SystemState('SYS:'+method,'EXISTING_TRANSITION',set(owned)))
    k.add_system(SystemState('DECISION','DECISION_ORCHESTRATION',set()));k.add_system(SystemState('AUDIT','QUALIFICATION_AUDIT',set()))
    plan=ProjectDevelopmentPlan('DEV','P','WIP-P','MINE-P','earth_supplier',NODE_ID,D(params['capex']),((7,D(params['stage_amount'])),(8,D(params['stage_amount']))),9,D(params['capacity']),AUTHORIZATION)
    k.register_development_plan(plan)
    market=CommodityMarketEnvelope('MKT',11,'RES','earth_market',D(params['unit_price']),D(params['first_demand']),'MODEL_CURRENCY','MODEL_RESOURCE_UNIT_BY_FAMILY',AUTHORIZATION,'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate();k.register_market_envelope(market)
    claim=FinancingReturnClaim('FRC','FIN','P','fin_funds',D(params['return_claim']),('C-DEV','C-OP'),AUTHORIZATION,'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate();k.register_financing_return_claim(claim)
    infra=SettlementInfrastructurePlan('INFRA',12,NODE_ID,'local_reinvest_funds','local_settlement_supplier',D(params['infrastructure_cost']),int(params['habitat_capacity']),AUTHORIZATION,'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate();k.register_settlement_infrastructure_plan(infra)
    tech=TechnologyCapabilityState(params['technology_state_id'],D(13),D(21),(params['transport_capability'],) if params['technology_qualified']=='TRUE' else (),AUTHORIZATION,'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate();k.register_technology_capability_state(tech)
    rel=TransportRelationship(params['transport_relationship_id'],'EARTH:USA',NODE_ID,D(13),D(21),params['transport_capability'],D(params['transport_cost']),D(params['travel_time']),D(params['energy']),D(params['loss_risk']),int(params['transport_capacity']),'PASSENGER',AUTHORIZATION,'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate();k.register_transport_relationship(rel) if params['relationship_registered']=='TRUE' else None
    genesis=[];derived=[]
    for source in earth:
        if source.concept!='investment':continue
        year=int(source.valid_from)-2025
        request=ConsumptionRequest('EARTH_SOURCE:'+str(year),'GENESIS','EARTH_REFERENCE','USA','investment','COUNTRY:USA','CALENDAR_YEAR',source.valid_from,source.available_from,'REAL','','GOVERNANCE','','ADMITTED',source.unit,'EARTH_REFERENCE')
        value,receipt=admit_for_use(k,request)
        transformed=earth_supply_value(value,params['S'],params.get('f.'+str(year),params['f']),year,scenario_id)
        transformed=replace(transformed,dependency_refs=(*transformed.dependency_refs,receipt.receipt_id))
        derived.append(transformed);genesis.append((receipt,transformed))
        if k.resource_constraints[('EARTH:USA',year)].ceiling!=D(transformed.value):raise RuntimeError('Earth transform/constraint mismatch')
    population=next(a for a in earth if a.concept=='population' and a.valid_from=='2027')
    request=ConsumptionRequest('EARTH_POPULATION_BOUND','GENESIS','EARTH_REFERENCE','USA','population','COUNTRY:USA','CALENDAR_YEAR','2027','2027','REAL','','GOVERNANCE','','ADMITTED','PERSON','EARTH_REFERENCE')
    bound,receipt=admit_for_use(k,request);genesis.append((receipt,bound))
    k._boundary_genesis_inputs=tuple(genesis)
    k._boundary_authored_inputs=(table,policy_manifest)
    m=replace(m,assertions=(*m.assertions,*derived));k.boundary_manifest=m
    opening=tuple((key,canonical(k._boundary_opening_value(key))) for key in ('accounts','agents','resources','constraints','population','earth_admission_receipts'))
    k.boundary_manifest=replace(m,opening_bindings=opening,opening_state_hash=content_hash(k._boundary_projection()))
    return k,{'params':params,'table':table,'manifest':policy_manifest,'model':SurfaceProspectingModel('B6D_SURFACE',D(params['surface_fp']),D(params['surface_fn']),D(params['surface_detection']),D(params['surface_fp']),D(params['remote_fp']),D(params['remote_fn']),'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE',AUTHORIZATION).validate(),'results':[],'audits':[],'policies':{},'snapshots':{},'requests':{},'counter':0,'last_time':D(0)}


def policy_inputs(k,actor,time,concepts,subjects=None):
    subjects=subjects or {};receipts=[]
    for concept in ('agent.STATE','agent.BELIEF','agent.PRIOR',*concepts):
        if concept in LIVE:
            _,subject,unit=LIVE[concept];subject=actor if subject=='SELF' else subject
            subject=subjects.get(concept,subject)
            scope='AGENT:'+actor if concept.startswith('agent.') else 'PROJECT:P' if subject=='P' else 'SITE:OFF:MOON:CABEU:B6E_SITE_01'
            if concept=='opportunity.NAMED_LOCATION':
                scope='LOCATION:MOON:CABEU';subject='MOON:CABEU';context='REAL';cid='';role='ADMITTED_CATALOG_IDENTITY'
            elif concept=='opportunity.AUTHORED_SITE':
                scope='SITE:OFF:MOON:CABEU:B6E_SITE_01';subject='SITE:OFF:MOON:CABEU:B6E_SITE_01';context='SCENARIO';cid=k.boundary_manifest.scenario_id;role='POLICY_PARAMETER'
            else:
                context='REALIZED';cid=k.boundary_manifest.run_id;role='ADMITTED_INFORMATION'
        else:
            a=next(x for x in k.boundary_manifest.assertions if x.assertion_id==actor+':'+concept)
            subject=a.subject_id;scope=a.scope;unit=a.unit;context='SCENARIO';cid=k.boundary_manifest.scenario_id;role='POLICY_PARAMETER'
        req=ConsumptionRequest(actor+':'+str(time)+':'+concept,actor,'POLICY',subject,concept,scope,'SIM_TIME',str(time),str(time),context,cid,'AGENT',actor,'ADMITTED',unit,role)
        receipts.append(admit_for_use(k,req)[1])
    return tuple(receipts)


_TEMPORAL_FIELDS=frozenset(('year','effective_time','departure_time','arrival_time','event_time','decision_time','authorization_time','realized_time'))

def _shift_temporal_record(value,delta):
    if not delta or not is_dataclass(value):return value
    updates={}
    for f in fields(value):
        current=getattr(value,f.name)
        if f.name in _TEMPORAL_FIELDS and isinstance(current,(int,str,D)):
            updates[f.name]=type(current)(D(current)+delta) if type(current) is D else int(D(current)+delta) if type(current) is int else str(D(current)+delta)
        elif is_dataclass(current):updates[f.name]=_shift_temporal_record(current,delta)
    return replace(value,**updates) if updates else value

_SYSTEM_TIME_INDEX={'disburse':0,'reserve_earth_supply':1,'explore_paid':0,'surface_prospect_paid':0,
    'update_agent_belief_from_observation':0,'publish_observation':0,'transition_project_status':0,
    'execute_development_stage':0,'resolve_development_plan':0,'spend_operating_cycle':0,
    'resolve_operating_extraction':0,'admit_realized_output_observation':0,'clear_market_sale':0,
    'execute_surplus_distribution':0,'execute_settlement_infrastructure':0,'update_settlement_stage':0,
    'execute_enterprise_review':0}

def _shift_method_arguments(method,args,delta):
    values=list(args)
    idx=_SYSTEM_TIME_INDEX.get(method)
    if delta and idx is not None and idx<len(values):
        v=values[idx]
        if isinstance(v,(int,str,D)):values[idx]=int(D(v)+delta) if type(v) is int else str(D(v)+delta) if type(v) is str else D(v)+delta
    return tuple(_shift_temporal_record(v,delta) for v in values)


def _policy_epoch_body(k,h,label,actor,time,request,concepts,runner,version,subjects=None):
    h['counter']+=1;period=label
    delta=0 if label=='TRANSPORT' else int(h['params'].get('time_offset',0))
    time=str(D(time)+delta)
    request=_shift_temporal_record(request,delta)
    receipts=policy_inputs(k,actor,time,concepts,subjects)
    snap=build_decision_snapshot(k,actor,period,D(time),snapshot_facts(k,receipts),admission_receipts=receipts)
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
    from named_world import execute_persisted_epoch
    effective = D(time) + (0 if label=='TRANSPORT' else D(int(h['params'].get('time_offset',0))))
    result, status = execute_persisted_epoch(service_name=h['wa_service'], kernel=k,
        binding=h['named_binding'], epoch_id=label, effective_time=effective,
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
    event=ScheduledEvent(label,D(time),Phase.OPERATIONS,0,sid,sid)
    q=ConsumptionRequest(label,sid,'SYSTEM_TRANSITION',sid,'transition.RULE','PROCESS:'+sid,'SIM_TIME',str(time),str(time),'SCENARIO',k.boundary_manifest.scenario_id,'WORLD_SIM','','ADMITTED','TYPED_RULE','TRANSITION_RULE')
    receipt=admit_for_use(k,q)[1];receipts=[receipt];holder={}
    def live(concept,subject,scope,unit,role):
        request=ConsumptionRequest(label+':'+concept,sid,'SYSTEM_TRANSITION',subject,concept,scope,'SIM_TIME',str(time),str(time),'REALIZED',k.boundary_manifest.run_id,'WORLD_SIM','','ADMITTED',unit,role)
        receipts.append(admit_for_use(k,request)[1])
    if method in ('explore_paid','surface_prospect_paid','resolve_operating_extraction'):
        live('R_RECOVERABLE','RES','SITE:OFF:MOON:CABEU:B6E_SITE_01','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE')
    if method in ('reserve_earth_supply','explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage'):
        live('Earth_supply.AVAILABLE','EARTH:USA:SIM'+str(time),'ECONOMY:USA:SUPPLY','MODEL_SUPPLY_CLAIM_CURRENCY','SUPPLIER_CAPACITY')
    if method in ('explore_paid','surface_prospect_paid','spend_operating_cycle','execute_development_stage','clear_market_sale','execute_surplus_distribution'):
        project='EXP' if method in ('explore_paid','surface_prospect_paid') else 'P'
        live('project.CASH_BALANCE',project,'PROJECT:'+project,'MODEL_CURRENCY','FINANCIAL_STATE')
    if method in ('surface_prospect_paid','publish_observation','update_agent_belief_from_observation'):
        obs_id=args[6] if method=='surface_prospect_paid' else args[2]
        live('observation.SIGNAL',obs_id,'SITE:OFF:MOON:CABEU:B6E_SITE_01','SIGNAL_CATEGORY','OBSERVATION')
    if method=='resolve_operating_extraction':live('cycle.PAID_OPEX',args[4].event_id,'PROJECT:P','TYPED_EXPENSE_RECORD','REALIZED_EXPENSE')
    if method=='admit_realized_output_observation':live('cycle.ACTUAL_OUTPUT',args[2],'SITE:OFF:MOON:CABEU:B6E_SITE_01','MODEL_RESOURCE_UNIT_BY_FAMILY','REALIZED_OUTPUT')
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
    from named_world import execute_persisted_epoch
    preview_counter=h['counter']+1
    epoch_id='ACTION:'+str(preview_counter)+':'+method
    delta=0 if method in ('execute_transport_settlement_departure','execute_passenger_transport_arrival') else int(h['params'].get('time_offset',0))
    effective=D(time)+delta
    result,status=execute_persisted_epoch(service_name=h['wa_service'],kernel=k,
        binding=h['named_binding'],epoch_id=epoch_id,effective_time=effective,
        execute=lambda:_system_epoch_body(k,h,method,time,args,kwargs,decision_refs))
    h.setdefault('epoch_commits',[]).append((epoch_id,status))
    return result


def finance(k,h,label,time,request):
    version=h['manifest'].policy_version_hash(policy_source_bytes())
    d,ref=policy_epoch(k,h,label,'FIN',str(time),request,tuple('underwriting.'+x.kind.value for x in h['table'].inputs),lambda s,q,key:workers.run_financier_policy(s,q,h['manifest'],key,allow_test_fixture=True),version)
    if d.outcome.value=='APPROVE':
        cid='C-DEV' if request.stage=='DEVELOPMENT' else 'C-OP'
        system_epoch(k,h,'add_commitment',str(time),(cid,'FIN','P',d.amount),decision_refs=(ref,))
        system_epoch(k,h,'disburse',str(time),(int(time),cid,'fin_funds',d.amount),decision_refs=(ref,))
    return d,ref


def operate(k,h,label,time,obs):
    request=build_operating_cycle_request(label+':request',int(time),'P','RES','MINE-P',obs.id)
    d,ref=policy_epoch(k,h,label,'SPN',str(time),request,('project.STATUS','project.CASH_BALANCE','asset.CAPACITY','underwriting.OPERATING_COST'),workers.run_sponsor_operating_policy,workers.sponsor_operating_policy_version())
    if d.outcome.value=='REQUEST_FINANCE':
        q=build_financing_request('OP-FIN',int(time),'SPN','P',d.requested_financing,'OPERATING',(obs.id,));system_epoch(k,h,'submit_financing_request',str(time),(q,),decision_refs=(ref,))
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
    if d.outcome.value in ('CONTINUE','CLOSE'):system_epoch(k,h,'execute_enterprise_review',str(time),(int(time),'SPN',req,d),decision_refs=(ref,))
    return d


def _run_case(k,h):
    p=h['params']
    for channel,time,cost,runner,version in [('REMOTE',1,p['remote_cost'],workers.run_public_explorer_policy,workers.public_explorer_policy_version()),('SURFACE',2,p['surface_cost'],workers.run_public_surface_prospector_policy,workers.public_surface_prospector_policy_version())]:
        if channel=='SURFACE' and 'REMOTE' not in h:return k,h
        req=build_exploration_request(channel+':request',time,'EXP','RES',channel,prerequisite_observation_id=h['REMOTE'].id if channel=='SURFACE' else '')
        concepts=('exploration.'+channel+'_COST',)
        if channel=='REMOTE':concepts=('exploration.REMOTE_COST','opportunity.NAMED_LOCATION','opportunity.AUTHORED_SITE')
        d,ref=policy_epoch(k,h,channel,'PUB',str(time),req,concepts,runner,version)
        if d.outcome.value!='AUTHORIZE':return k,h
        system_epoch(k,h,'add_commitment',str(time),('C-'+channel,'PUB','EXP',d.authorized_cost),decision_refs=(ref,))
        system_epoch(k,h,'disburse',str(time),(time,'C-'+channel,'public_funds',d.authorized_cost),decision_refs=(ref,))
        system_epoch(k,h,'reserve_earth_supply',str(time),('EARTH:USA',time,d.authorized_cost),decision_refs=(ref,))
        if channel=='REMOTE':
            obs,asset,draw=system_epoch(k,h,'explore_paid',str(time),(time,'PUB','RES','EXP','earth_supplier',d.authorized_cost),dict(channel='REMOTE',public=False,false_positive=D(p['remote_fp']),false_negative=D(p['remote_fn']),update_belief=False,parent_ids=(d.id,)),(ref,))
            det=D(p['remote_detection']);fp=D(p['remote_fp'])
        else:
            obs,asset,draw,_=system_epoch(k,h,'surface_prospect_paid',str(time),(time,'PUB','RES','EXP','earth_supplier',d.authorized_cost,h['REMOTE'].id,h['model']),dict(parent_ids=(d.id,)),(ref,))
            det=D(p['surface_detection']);fp=D(p['surface_fp'])
        h[channel]=obs;h[channel+'_draw']=draw
        system_epoch(k,h,'update_agent_belief_from_observation',str(time),(time,'PUB',obs.id,'RES',det,fp,'B6D_'+channel,AUTHORIZATION),decision_refs=(ref,))
    obs=h['SURFACE'];req=build_publication_request('PUB:request',2,obs.id,'PUBLIC_FINANCIERS')
    d,ref=policy_epoch(k,h,'PUBLICATION','PUB','2',req,(),workers.run_public_publisher_policy,workers.public_publisher_policy_version())
    if d.outcome.value!='PUBLISH':return k,h
    h['publication']=system_epoch(k,h,'publish_observation','2',(2,'PUB',obs.id,req.audience,(('FIN','resource_exists',D(p['publication_detection']),D(p['publication_fp'])),('SPN','resource_exists',D(p['publication_detection']),D(p['publication_fp'])))),decision_refs=(ref,))
    req=build_sponsor_project_request('SPONSOR:request',3,'P','RES',obs.id)
    d,ref=policy_epoch(k,h,'SPONSOR','SPN','3',req,('project.STATUS','project.CASH_BALANCE','underwriting.DEVELOPMENT_CAPEX'),workers.run_sponsor_operator_policy,workers.sponsor_operator_policy_version())
    if d.outcome.value=='ABANDON':system_epoch(k,h,'transition_project_status','3',(3,'SPN','P','ABANDONED',d.id),decision_refs=(ref,));return k,h
    if d.outcome.value!='REQUEST_FINANCE':return k,h
    q=build_financing_request('DEV-FIN',3,'SPN','P',d.requested_financing,'DEVELOPMENT',(obs.id,));system_epoch(k,h,'submit_financing_request','3',(q,),decision_refs=(ref,))
    fd,_=finance(k,h,'DEV_FINANCE',4,q)
    if fd.outcome.value!='APPROVE':return k,h
    req=build_sponsor_project_request('DEVELOP:request',5,'P','RES',obs.id)
    d,ref=policy_epoch(k,h,'DEVELOP','SPN','5',req,('project.STATUS','project.CASH_BALANCE','underwriting.DEVELOPMENT_CAPEX'),workers.run_sponsor_operator_policy,workers.sponsor_operator_policy_version())
    if d.outcome.value!='DEVELOP':return k,h
    system_epoch(k,h,'transition_project_status','5',(5,'SPN','P','DEVELOPMENT',d.id),decision_refs=(ref,))
    for year in (6,7):system_epoch(k,h,'execute_development_stage',str(year),(year,'DEV'),decision_refs=(ref,))
    system_epoch(k,h,'resolve_development_plan','8',(8,'DEV'),decision_refs=(ref,))
    if k.state.projects['P'].status!='OPERATING':return k,h
    first=operate(k,h,'FIRST_OPERATING',9,obs);h['first_output']=first
    if first is None:return k,h
    req=build_sale_decision_request('SALE:request',10,'P','RES','MKT',obs.id)
    d,ref=policy_epoch(k,h,'SALE','SPN','10',req,('project.STATUS','inventory.AVAILABLE','market.UNIT_PRICE','market.REMAINING_DEMAND'),workers.run_sponsor_sale_policy,workers.sponsor_sale_policy_version())
    if d.outcome.value!='OFFER':
        review(k,h,'ZERO_OUTPUT_REVIEW',10,first)
        return k,h
    h['sale']=system_epoch(k,h,'clear_market_sale','10',(10,'SPN',req,d),decision_refs=(ref,))
    req=build_surplus_distribution_request('DISTRIBUTE:request',10,'P','FRC')
    d,ref=policy_epoch(k,h,'DISTRIBUTE','SPN','10',req,('project.STATUS','project.CASH_BALANCE','project.RESERVE_REQUIREMENT','financing.RETURN_CLAIM_REMAINING','project.REINVESTMENT_REQUIREMENT'),workers.run_sponsor_surplus_policy,workers.sponsor_surplus_policy_version())
    if d.outcome.value=='DISTRIBUTE':
        h['distribution']=system_epoch(k,h,'execute_surplus_distribution','10',(10,'SPN',req,d,'local_reinvest_funds'),decision_refs=(ref,))
        system_epoch(k,h,'execute_settlement_infrastructure','11',(11,'INFRA','SPN'),decision_refs=(ref,))
        system_epoch(k,h,'update_settlement_stage','11',(11,'OFF:MOON:CABEU:B6E_SITE_01'))
        req=build_transport_settlement_request('TRANSPORT:request',D(p['departure']),'EARTH:USA','OFF:MOON:CABEU:B6E_SITE_01','settlement_support','transport_provider',int(p['requested_residents']),D(p['support_cost']),p['transport_relationship_id'],p['technology_state_id'])
        concepts=('settlement.STAGE','settlement.HABITAT_HEADROOM','settlement.REQUESTED_RESIDENTS','population.EARTH_AVAILABLE','settlement.PUBLIC_SUPPORT_COST',*(key for key in LIVE if key.startswith(('transport.','technology.'))))
        d,ref=policy_epoch(k,h,'TRANSPORT','PUB',p['departure'],req,concepts,workers.run_public_settlement_transport_policy,workers.public_settlement_transport_policy_version())
        if d.outcome.value=='AUTHORIZE':
            dep=system_epoch(k,h,'execute_transport_settlement_departure',p['departure'],('PUB',req,d),decision_refs=(ref,))
            system_epoch(k,h,'execute_passenger_transport_arrival',str(dep.arrival_time),(dep.arrival_time,dep.departure_id),decision_refs=(ref,))
    review(k,h,'FIRST_REVIEW',13,first)
    second=operate(k,h,'SECOND_OPERATING',14,obs);h['second_output']=second
    if second is not None:review(k,h,'SECOND_REVIEW',14,second)
    validate_trace(k.causal_envelopes,k.causal_artifacts)
    return k,h


def run_case(world='RICH',overrides=None,*,wa_service=None,named_binding=None,source_row=None,world_seed=None,policy_seed=None):
    from offworld_kernel.kernel import InvariantError
    k,h=make_kernel(world,overrides,world_seed=world_seed,policy_seed=policy_seed,source_row=source_row)
    if wa_service:
        if named_binding is None:raise ValueError('named World Authority binding required')
        h['wa_service']=wa_service;h['named_binding']=named_binding
    try:return _run_case(k,h)
    except InvariantError as exc:
        if k._boundary_invalid or str(exc).startswith(('INVALID_RUN','TRACE_INCOMPLETE')):raise
        h['blocked']=str(exc)
        validate_trace(k.causal_envelopes,k.causal_artifacts)
        return k,h


def strict_provenance(k,tables=(),policies=('NO_POLICY_THIS_EPOCH',)):
    m=k.boundary_manifest
    labels=[('BOUNDARY_SHA256',m.fingerprint()),('EARTH_SLICE_SHA256',m.earth_slice_ref[1]),
            ('COMPARISON_CONFIG_SHA256',m.comparison_spec_ref[1]),('QUALIFICATION_PROTOCOL_SHA256',m.qualification_protocol_ref[1])]
    for ref,digest in m.harness_refs:
        label={
            'simulation/offworld_mvp/build6e/qualification/qualify_build6e.py':'QUALIFICATION_DRIVER_SHA256',
            'simulation/offworld_mvp/build6e/qualification/build6e_fixture.py':'QUALIFICATION_FIXTURE_SHA256',
            'simulation/offworld_mvp/build6e/named_world.py':'NAMED_WORLD_COMPILER_SHA256',
            'src/loom_world_authority/store.py':'WORLD_AUTHORITY_STORE_SHA256',
        }.get(ref)
        if label is None:raise RuntimeError('undeclared Build 6E harness module: '+ref)
        labels.append((label,digest))
    if not hasattr(k,'_boundary_candidate_provenance'):k._boundary_candidate_provenance=ReplayProvenance.from_kernel(k)
    return replace(k._boundary_candidate_provenance,table_manifest_ids=tuple(key+':'+value for key,value in labels)+tuple(tables),policy_manifest_ids=tuple(policies)).validate()
