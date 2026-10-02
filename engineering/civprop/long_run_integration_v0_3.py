from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from engineering.civprop.long_run_integration_v0_2 import build_bundle_dir as build_v02
from engineering.civprop.contracts.solar_object_location_bridge_v0_3 import build_solar_candidate_locations
from engineering.civprop.contracts.placeholder_transport_opportunity_surface_v0_3 import build_placeholder_surface
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; NAV=ROOT/'reports/solar_civprop/NAV_READINESS_V1.json'; ACTORS=HERE/'contracts/actor_machinery_test_baseline_v0_1.json'
def load(p): return json.loads(Path(p).read_text())
def dump(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lid(b): return f'{b}_ORBIT'
def build_bundle_dir(target:Path):
 build_v02(target); sp=target/'scenario_v1.json'; tp=target/'truth_v1.json'; mp=target/'manifest_v1.json'; cp=target/'compiler_manifest_v1.json'
 s=load(sp); m=load(mp); c=load(cp); surf=build_placeholder_surface(NAV); admitted={r['destination_body_id'] for r in surf['rows']}; existing={x['location_id'] for x in s['locations']}
 for x in build_solar_candidate_locations(NAV)['locations']:
  b=x['body_id']
  if x['placement']!='ORBITAL' or b not in admitted or lid(b) in existing: continue
  s['locations'].append({'location_id':lid(b),'parent_body_id':b,'placement':'ORBITAL','initial_state':{'biological_population':0,'transient_population':0,'workforce':0,'capital':0,'capacities':{'habitat':0.0,'industrial':0.0,'power':0.0,'resource':0.0,'shipyard':0.0,'transport':0.0}}}); existing.add(lid(b)); s['accessibility_v1']['location_bindings'].append({'body_id':b,'location_id':lid(b)})
 paths=[]
 for r in surf['rows']:
  for a in load(ACTORS)['actors']:
   aid=a['actor_id']; paths.append({'service_id':f"PLACEHOLDER_SOLARV03::{aid}::{r['destination_body_id']}",'actor_id':aid,'provider_id':f'MACHINERY_TEST_PROVIDER::{aid}','subject_id':None,'origin_location_id':'EARTH_SURFACE','destination_location_id':lid(r['destination_body_id']),'mission_class':'ROBOTIC_RESOURCE_RECONNAISSANCE','service_class':'GAP016_PLACEHOLDER_TRANSPORT_OPPORTUNITY','valid_from_year':2026,'valid_to_year':2226,'target_year':None,'status':'FEASIBLE','limiting_constraints':[],'provenance_refs':['NON_CANON_PROPAGATION_TEST_PLACEHOLDER','GAP-016_TRANSPORT_OPPORTUNITY_SURFACE'],'required_technology_ids':[],'cost_components':[{'component_id':'PLACEHOLDER_TRANSPORT_OPPORTUNITY','status':'KNOWN','value':1.0,'unit':'dimensionless_test_index','uncertainty':None}],'generalized_cost':{'status':'KNOWN','value':1.0,'unit':'dimensionless_test_index','uncertainty':None}})
 s['accessibility_v1']['service_paths'].extend(paths); s['fixture_id']='SOLAR_LONG_RUN_ACTOR_INTEGRATION_V0_3_2026_2226'; s['classification']='NON_CANON_SOLAR_PROPAGATION_TEST_WITH_GAP016_PLACEHOLDER'; s['authority_context']['solar_integration_v0_3']={'transport_surface':'EXPLICIT_PLACEHOLDER','transport_gap':'GAP-016','placeholder_transport_opportunity':1.0,'placeholder_rows':len(surf['rows']),'bound_accessibility_service_paths':len(paths),'gap_014':'OPEN','gap_015':'OPEN','gap_016':'OPEN'}
 t=load(tp); t['fixture_id']=s['fixture_id']; dump(sp,s); dump(tp,t); m['fixture_id']=s['fixture_id']; m['authority']='INTEGRATED_CIVPROP_NON_CANON_SOLAR_PROPAGATION_TEST_V0_3'; m['sha256']['scenario_v1.json']=sha(sp); m['sha256']['truth_v1.json']=sha(tp); m['bundle_sha256']=hashlib.sha256(sp.read_bytes()+b'\n'+tp.read_bytes()).hexdigest(); dump(mp,m); c['compiler_id']='CIVPROP_SOLAR_LONG_RUN_INTEGRATION_ADAPTER_V0_3'; c['compiler_version']='0.3.0'; c['gap_resolution']={f'GAP-{i:03d}':'CLOSED' for i in range(1,14)}|{'GAP-014':'OPEN','GAP-015':'OPEN','GAP-016':'OPEN'}; c['runtime_input']={'authority':m['authority'],'bundle_sha256':m['bundle_sha256'],'fixture_id':m['fixture_id'],'scenario_format':s['format'],'scenario_sha256':sha(sp)}; c['package_files']={'manifest_v1.json':sha(mp),'scenario_v1.json':sha(sp),'truth_v1.json':sha(tp)}; dump(cp,c); dump(target/'placeholder_transport_surface_v0_3.json',surf); return target
def run_integrated(seed=42):
 from engineering.civprop.method_lab.contracts import load_bundle
 from engineering.civprop.run_civprop_v1 import build_output
 with tempfile.TemporaryDirectory(prefix='civprop_solar_v03_') as td:
  p=build_bundle_dir(Path(td)); load_bundle(p); return build_output(input_dir=p,infrastructure_catalog_path=HERE/'contracts/infrastructure_archetypes_v1.json',seed=seed)
