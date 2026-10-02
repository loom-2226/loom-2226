"""Assemble executable full-Solar CIVPROP V0.3 machinery-test bundle.

GAP-014 and GAP-015 remain OPEN. GAP-016 owns the explicit dimensionless
transport-opportunity placeholder. No SPICE/trajectory result is consumed here.
"""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
from engineering.civprop.long_run_integration_v0_2 import build_bundle_dir as build_v02
from engineering.civprop.contracts.solar_object_location_bridge_v0_3 import build_solar_candidate_locations
from engineering.civprop.contracts.solar_mission_opportunity_bridge_v0_3 import build_solar_mission_opportunity_catalog
from engineering.civprop.contracts.placeholder_transport_opportunity_surface_v0_3 import friction_for_body,semantics as placeholder_semantics

ROOT=Path(__file__).resolve().parents[2]
NAV=ROOT/'reports/solar_civprop/NAV_READINESS_V1.json'
M4B=ROOT/'dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv'
ACTORS=ROOT/'engineering/civprop/contracts/actor_machinery_test_baseline_v0_1.json'

def _load(p): return json.loads(Path(p).read_text())
def _dump(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _zero_state():
 return {'biological_population':0,'transient_population':0,'workforce':0,'capital':0,
         'capacities':{'habitat':0.0,'industrial':0.0,'power':0.0,'resource':0.0,'shipyard':0.0,'transport':0.0}}

def build_bundle_dir(target:Path)->Path:
 build_v02(target)
 sp=target/'scenario_v1.json'; mp=target/'manifest_v1.json'; cp=target/'compiler_manifest_v1.json'; tp=target/'truth_v1.json'
 s=_load(sp); actors=_load(ACTORS)['actors']
 bridge=build_solar_candidate_locations(NAV)
 # Preserve qualified V0.2 Earth/Luna runtime identities. Do not silently create aliases.
 existing={x['location_id'] for x in s['locations']}
 added=[]
 for x in bridge['locations']:
  if x['body_id'] in {'EARTH','MOON'}: continue
  if x['candidate_status']!='NAV1_CANDIDATE': continue
  if x['location_id'] in existing: continue
  s['locations'].append({'location_id':x['location_id'],'parent_body_id':x['body_id'],
                         'placement':x['placement'],'initial_state':_zero_state()})
  existing.add(x['location_id']); added.append(x)
 # Bind explicit placeholder into Accessibility V1. Its scalar is a qualification
 # switch only. The separate USD 1bn service price is inherited V0.2 machinery-test
 # economics and MUST NOT be interpreted as derived from the scalar.
 acc=s['accessibility_v1']; services=acc['service_paths']
 # Bind added candidate identities into Accessibility V1 without adding geometry samples.
 bound={x['location_id'] for x in acc['location_bindings']}
 for x in added:
  if x['location_id'] not in bound:
   acc['location_bindings'].append({'location_id':x['location_id'],'body_id':x['body_id']}); bound.add(x['location_id'])
 for a in actors:
  aid=a['actor_id']; provider=f'MACHINERY_TEST_PROVIDER::{aid}'
  for x in added:
   friction=friction_for_body(x['body_id'],x['body_class'])
   # Map the dimensionless friction monotonically into the existing machinery-test
   # generalized-cost channel. This is explicitly NOT a physical or empirical price.
   placeholder_cost=round(friction,6)
   component={'component_id':'SOLAR_V03_GAP016_FRICTION_PROXY','status':'KNOWN','value':placeholder_cost,'unit':'USD_2026_billion','uncertainty':None}
   gc={'status':'KNOWN','value':placeholder_cost,'unit':'USD_2026_billion','uncertainty':None}
   for mission_class in ('PROJECT_DEPLOYMENT','ROBOTIC_RESOURCE_PROSPECTING'):
    services.append({'service_id':f'{aid}_{x["location_id"]}_{mission_class}_SOLAR_V03',
      'actor_id':aid,'provider_id':provider,'subject_id':None,'origin_location_id':'EARTH_SURFACE',
      'destination_location_id':x['location_id'],'mission_class':mission_class,'service_class':'GENERIC_LOGISTICS',
      'valid_from_year':2026,'valid_to_year':2226,'target_year':None,'status':'FEASIBLE',
      'limiting_constraints':[],'required_technology_ids':[],
      'provenance_refs':['EXPLICIT_PLACEHOLDER:GAP-016','NON_CANON_SOLAR_V03_PROPAGATION_TEST'],
      'cost_components':[component],'generalized_cost':gc})
 catalog=build_solar_mission_opportunity_catalog(NAV,M4B)
 s['fixture_id']='SOLAR_LONG_RUN_PROPAGATION_V0_3_2026_2226'
 truth=_load(tp); truth['fixture_id']=s['fixture_id']; _dump(tp,truth)
 s['classification']='NON_CANON_MACHINERY_TEST_EXPLICIT_GAP016_PLACEHOLDER'
 s['authority_context']['solar_v0_3']={
   'status':'NON_CANON_PROPAGATION_TEST',
   'candidate_location_bridge':bridge['format'],
   'added_nav1_locations':len(added),
   'mission_opportunity_catalog':catalog['format'],
   'knowledge_questions':catalog['counts']['questions'],
   'candidate_mission_opportunities':catalog['counts']['candidate'],
   'transport_opportunity_surface':{
      'status':'EXPLICIT_AUTHORED_FRICTION_PLACEHOLDER','unit':'DIMENSIONLESS_GENERALIZED_FRICTION_PLACEHOLDER',
      'earth_reference':1.0,'examples':{'MARS':6.0,'CERES':18.0,'PLUTO':500.0},
      'gap_owner':'GAP-016','semantics':placeholder_semantics()},
   'service_price_boundary':'GAP016_FRICTION_MONOTONIC_PROXY_IN_EXISTING_COST_CHANNEL_NOT_EMPIRICAL_PRICE',
   'gap_014':'OPEN_UNTOUCHED','gap_015':'OPEN_UNTOUCHED','gap_016':'OPEN_PLACEHOLDER_ACTIVE',
   'spice_consumed':False,
 }
 _dump(sp,s)
 m=_load(mp); m['fixture_id']=s['fixture_id']; m['authority']='SOLAR_V0_3_NON_CANON_EXPLICIT_GAP016_PLACEHOLDER'
 m['sha256']['scenario_v1.json']=_sha(sp); m['sha256']['truth_v1.json']=_sha(tp)
 m['bundle_sha256']=hashlib.sha256(sp.read_bytes()+b'\n'+tp.read_bytes()).hexdigest(); _dump(mp,m)
 c=_load(cp); c['compiler_id']='CIVPROP_SOLAR_V0_3_BUNDLE_ADAPTER'; c['compiler_version']='0.3.0'
 c['gap_resolution']={f'GAP-{i:03d}':'CLOSED' for i in range(1,14)}|{'GAP-014':'OPEN','GAP-015':'OPEN','GAP-016':'OPEN_EXPLICIT_PLACEHOLDER'}
 c['runtime_input']={'authority':m['authority'],'bundle_sha256':m['bundle_sha256'],'fixture_id':m['fixture_id'],
                     'scenario_format':s['format'],'scenario_sha256':_sha(sp)}
 c['package_files']={'manifest_v1.json':_sha(mp),'scenario_v1.json':_sha(sp),'truth_v1.json':_sha(tp)}
 _dump(cp,c)
 return target
