"""CIVPROP long-run integration adapter V0.2.

Builds a temporary 2026-2226 Method Lab bundle from the promoted GAP-013
compiled authority plus the non-canon 2026 actor machinery fixture.  It does
not implement propagation.  Propagation remains HYBRID_V1 and the promoted
GAP contracts consumed by run_civprop_v1.build_output().
"""
from __future__ import annotations
import copy, hashlib, json, tempfile
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent
BASE=HERE/'compiled_inputs/earth_luna_2026_2036_v1'
ACTORS=HERE/'contracts/actor_machinery_test_baseline_v0_1.json'
SUPPORT=HERE/'compiled_inputs/actor_earth_support_v0_1.json'
PARAMS=HERE/'contracts/actor_bridge_parameters_v0_1.json'
CATALOG=HERE/'contracts/infrastructure_archetypes_v1.json'

TECH_REQUIREMENTS={
 'ORBITAL_CONSTRUCTION':('ORBITAL_LAUNCH','SPACECRAFT_OPS'),
 'OFFWORLD_POWER':('LUNAR_DELIVERY',),
 'OFFWORLD_HABITAT':('LUNAR_DELIVERY','SURFACE_INFRASTRUCTURE'),
 'LUNAR_SURFACE_OPERATIONS':('LUNAR_DELIVERY','SPACECRAFT_OPS'),
 'LUNAR_RESOURCE_PROCESSING':('LUNAR_DELIVERY','SURFACE_INFRASTRUCTURE'),
}


def _load(p:Path): return json.loads(p.read_text())
def _dump(p:Path,obj:Any): p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def _sha(p:Path): return hashlib.sha256(p.read_bytes()).hexdigest()

def _factset(records): return {'status':'KNOWN_RECORDS' if records else 'KNOWN_NONE','records':records}

def _tech_status(actor, tech):
    vals=[actor['capability'].get(x,'UNKNOWN') for x in TECH_REQUIREMENTS[tech]]
    if any(x=='UNKNOWN' for x in vals): return 'UNKNOWN'
    if any(x=='DEVELOPMENT' for x in vals): return 'CONDITIONAL'
    return 'USABLE'  # OPERATIONAL or explicitly admitted ACCESS in machinery fixture

def _annual_budget(actor, year, support_by, params):
    inv=sum(float(support_by[(year,iso)]['investment']) for iso in actor['earth_economy_links'])/1e9
    cls=actor['actor_class']
    frac=(params['commercial_host_investment_allocation_fraction'] if cls=='COMMERCIAL'
          else params['multinational_member_allocation_fraction'] if cls=='MULTINATIONAL_AGENCY'
          else params['public_investment_allocation_fraction'])
    return inv*float(frac)

def _actor_state(actor_pkg,support,params):
    support_by={(x['year'],x['iso3']):x for x in support['rows']}
    actors=[]; events=[]
    for a in actor_pkg['actors']:
        aid=a['actor_id']; caps=[]
        for tech in sorted(TECH_REQUIREMENTS):
            caps.append({'record_id':f'{aid}_{tech}_MACHINERY_V02','subject_id':None,'status':_tech_status(a,tech),
                         'scope':'NON_CANON_MACHINERY_TEST_TECH_BRIDGE','counterparty_id':None,'provider_id':None,
                         'capability_id':tech,'valid_from':2026,'valid_to':None,
                         'provenance_refs':['actor_machinery_test_baseline_v0_1','actor_bridge_parameters_v0_1']})
        provider={'record_id':f'{aid}_GENERIC_LOGISTICS_ACCESS_V02','subject_id':None,'status':'MACHINERY_TEST_ACCESS',
                  'scope':'GENERIC_LOGISTICS_NON_CANON_MACHINERY_TEST','counterparty_id':None,
                  'provider_id':f'MACHINERY_TEST_PROVIDER::{aid}','capability_id':'GENERIC_LOGISTICS',
                  'valid_from':2026,'valid_to':2226,'provenance_refs':['actor_machinery_test_baseline_v0_1']}
        amount=_annual_budget(a,2026,support_by,params)
        blank={'status':'KNOWN_NONE','records':[]}
        actors.append({'actor_id':aid,
          'actor_type':'STATE' if a['actor_class']=='PUBLIC_AGENCY' else ('PUBLIC_FINANCER' if a['actor_class']=='MULTINATIONAL_AGENCY' else 'COMMERCIAL'),
          'identity':{'display_name':aid,'provenance_refs':['actor_machinery_test_baseline_v0_1']},
          'budget':{'spendable_allocation':{'status':'KNOWN','amount':amount,'unit':params['capital_unit'],'scope':'GENERAL_CIVPROP_PROJECT_DECISION_BUDGET','provenance_refs':['actor_earth_support_v0_1','actor_bridge_parameters_v0_1']},'committed_funds':[]},
          'ownership':copy.deepcopy(blank),'operation':copy.deepcopy(blank),'access_rights':copy.deepcopy(blank),'contracts':copy.deepcopy(blank),
          'provider_service_access':_factset([provider]),'installed_capability':_factset(caps),'acquired_capability':copy.deepcopy(blank),
          'experience':copy.deepcopy(blank),'owned_infrastructure':copy.deepcopy(blank),'relationships':copy.deepcopy(blank)})
        for year in range(2027,2227):
            events.append({'event_id':f'{aid}_BUDGET_{year}','year':year,'actor_id':aid,'event_type':'BUDGET_ALLOCATION_SET',
              'payload':{'amount':_annual_budget(a,year,support_by,params),'unit':params['capital_unit'],'scope':'GENERAL_CIVPROP_PROJECT_DECISION_BUDGET'},
              'provenance':{'class':'NON_CANON_MACHINERY_TEST_ASSUMPTION','ref':'actor_earth_support_v0_1+actor_bridge_parameters_v0_1'}})
    return {'format':'CIVPROP_ACTOR_STATE_V1','contract_version':'1.0.0','as_of_year':2026,'actors':actors,'events':events}

def _accessibility(base, actor_pkg):
    pkg=copy.deepcopy(base)
    pkg['service_paths']=list(pkg.get('service_paths',[]))
    # Existing 2030 geometry remains evidence context only; V0.2 service cost is an explicit
    # non-empirical machinery-test generalized cost, never fabricated ephemeris geometry.
    component={'component_id':'MACHINERY_TEST_SERVICE_PRICE','status':'KNOWN','value':1.0,'unit':'USD_2026_billion','uncertainty':None}
    gc={'status':'KNOWN','value':1.0,'unit':'USD_2026_billion','uncertainty':None}
    destinations=('EARTH_ORBIT','LUNA_SURFACE','CISLUNAR_FREE_SPACE')
    for a in actor_pkg['actors']:
        aid=a['actor_id']; provider=f'MACHINERY_TEST_PROVIDER::{aid}'
        for dest in destinations:
            for mission_class in ('PROJECT_DEPLOYMENT','ROBOTIC_RESOURCE_PROSPECTING'):
                pkg['service_paths'].append({'service_id':f'{aid}_{dest}_{mission_class}_V02','actor_id':aid,'provider_id':provider,
                  'subject_id':None,'origin_location_id':'EARTH_SURFACE','destination_location_id':dest,
                  'mission_class':mission_class,'service_class':'GENERIC_LOGISTICS','valid_from_year':2026,'valid_to_year':2226,
                  'target_year':None,'status':'FEASIBLE','limiting_constraints':[],
                  'provenance_refs':['NON_CANON_MACHINERY_TEST_ACCESS_V0_2'],'required_technology_ids':[],
                  'cost_components':[component],'generalized_cost':gc})
    return pkg

def build_bundle_dir(target:Path)->Path:
    actor_pkg=_load(ACTORS); support=_load(SUPPORT); params=_load(PARAMS)
    target.mkdir(parents=True,exist_ok=True)
    scenario=_load(BASE/'scenario_v1.json'); truth=_load(BASE/'truth_v1.json'); manifest=_load(BASE/'manifest_v1.json')
    scenario['fixture_id']='EARTH_LUNA_LONG_RUN_ACTOR_INTEGRATION_V0_2_2026_2226'
    truth['fixture_id']=scenario['fixture_id']
    scenario['horizon']['end_year']=2226
    scenario['classification']='NON_CANON_MACHINERY_TEST_INTEGRATED_CIVPROP'
    scenario['actors']=[{'actor_id':a['actor_id'],'actor_type':('STATE' if a['actor_class']=='PUBLIC_AGENCY' else 'PUBLIC_FINANCER' if a['actor_class']=='MULTINATIONAL_AGENCY' else 'COMMERCIAL')} for a in actor_pkg['actors']]
    scenario['actor_state_v1']=_actor_state(actor_pkg,support,params)
    scenario['accessibility_v1']=_accessibility(scenario['accessibility_v1'],actor_pkg)
    # Admit the full infrastructure catalog's surface transport bootstrap through the
    # existing Project Economics/Production/Power contracts.  PROSPECTING_SURVEY stays
    # mission-only and is never inserted into project_archetypes.
    if not any(x['project_archetype_id']=='SURFACE_PORT' for x in scenario['project_archetypes']):
        pe=next(x for x in scenario['project_economics_v1']['projects'] if x['project_archetype_id']=='SURFACE_PORT')
        scenario['project_archetypes'].append({'project_archetype_id':'SURFACE_PORT','project_kind':'FACILITY','allowed_placements':['SURFACE'],'required_tech':[],
          'capital_cost':float(pe['capital_cost']['nominal']),'construction_lag_years':int(pe['construction_lag']['nominal']),
          'output_capacities':{'transport':float(pe['outputs']['transport']['nominal'])},'minimum_input_capacities':{}})
        prod=copy.deepcopy(next(x for x in scenario['production_accounting_v1']['facility_models'] if x['project_archetype_id']=='LOGISTICS_NODE'))
        prod['project_archetype_id']='SURFACE_PORT'; prod['production_model_id']='SURFACE_PORT_PRODUCTION_V0_2'; prod['provenance_refs']=['NON_CANON_MACHINERY_TEST_INTEGRATION_V0_2']
        scenario['production_accounting_v1']['facility_models'].append(prod)
        load=copy.deepcopy(next(x for x in scenario['power_balance_v1']['facility_load_models'] if x['project_archetype_id']=='LOGISTICS_NODE'))
        load['project_archetype_id']='SURFACE_PORT'; load['provenance_refs']=['NON_CANON_MACHINERY_TEST_INTEGRATION_V0_2']
        scenario['power_balance_v1']['facility_load_models'].append(load)
    scenario['demand_pressure_v1']['strategic_requirements']=[]
    for row in params.get('strategic_bootstrap_requirements',[]):
        r=copy.deepcopy(row); r['provenance_refs']=['actor_bridge_parameters_v0_1:NON_CANON_MACHINERY_TEST_ASSUMPTION']
        scenario['demand_pressure_v1']['strategic_requirements'].append(r)
    for dm in scenario['mission_knowledge_v1']['decision_models']:
        if dm['mission_archetype_id']=='LUNAR_RESOURCE_PROSPECTING_SURVEY':
            dm['success_value']={'status':'SCENARIO_ASSUMPTION','value':float(params['prospecting_follow_on_success_value_usd_2026_billion']),'unit':'USD_2026_billion','provenance_refs':['actor_bridge_parameters_v0_1:NON_CANON_MACHINERY_TEST_ASSUMPTION']}
    # GAP-011's frozen AUS allocation is not transferable to unrelated actors.  Keep the
    # traffic mechanism active but remove that actor-specific allocation rather than infer one.
    scenario['traffic_fleet_v1']['demand_allocations']=[]
    scenario['authority_context']['long_run_integration_v0_2']={
      'status':'NON_CANON_MACHINERY_TEST','earth_support_designation':support['source_designation'],
      'actor_fixture_sha256':_sha(ACTORS),'earth_support_sha256':_sha(SUPPORT),'bridge_parameters_sha256':_sha(PARAMS),
      'closed_gap_policy':'NO_PARALLEL_SUBSTITUTE_FOR_GAP_001_THROUGH_GAP_013'}
    sp=target/'scenario_v1.json'; tp=target/'truth_v1.json'; mp=target/'manifest_v1.json'
    _dump(sp,scenario); _dump(tp,truth)
    manifest['fixture_id']=scenario['fixture_id']; manifest['authority']='INTEGRATED_CIVPROP_NON_CANON_MACHINERY_TEST_V0_2'
    manifest['sha256']['scenario_v1.json']=_sha(sp); manifest['sha256']['truth_v1.json']=_sha(tp)
    manifest['bundle_sha256']=hashlib.sha256(sp.read_bytes()+b'\n'+tp.read_bytes()).hexdigest()
    _dump(mp,manifest)
    compiler=_load(BASE/'compiler_manifest_v1.json')
    compiler['compiler_id']='CIVPROP_LONG_RUN_INTEGRATION_ADAPTER_V0_2'
    compiler['compiler_version']='0.2.0'
    compiler['gap_resolution']={f'GAP-{i:03d}':'CLOSED' for i in range(1,14)} | {'GAP-014':'OPEN','GAP-015':'OPEN'}
    compiler['runtime_input']={'authority':manifest['authority'],'bundle_sha256':manifest['bundle_sha256'],'fixture_id':manifest['fixture_id'],'scenario_format':scenario['format'],'scenario_sha256':_sha(sp)}
    compiler['package_files']={'manifest_v1.json':_sha(mp),'scenario_v1.json':_sha(sp),'truth_v1.json':_sha(tp)}
    _dump(target/'compiler_manifest_v1.json',compiler)
    return target

def run_integrated(seed=42):
    from engineering.civprop.method_lab.contracts import load_bundle
    from engineering.civprop.run_civprop_v1 import build_output
    with tempfile.TemporaryDirectory(prefix='civprop_longrun_v02_') as td:
        path=build_bundle_dir(Path(td))
        # fail closed through the promoted Method Lab validator before propagation
        b=load_bundle(path)
        if (b.scenario.start_year,b.scenario.end_year)!=(2026,2226): raise ValueError('long-run horizon mismatch')
        return build_output(input_dir=path,infrastructure_catalog_path=CATALOG,seed=seed)
