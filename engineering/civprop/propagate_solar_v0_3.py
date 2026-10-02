"""Run Hybrid V1 on executable Solar V0.3 bundle; keep generic Solar missions at predecision."""
import argparse,hashlib,json,tempfile
from collections import Counter
from pathlib import Path
from engineering.civprop.long_run_integration_v0_3 import build_bundle_dir
from engineering.civprop.method_lab.contracts import load_bundle
from engineering.civprop.run_civprop_v1 import build_output
from engineering.civprop.contracts.solar_transport_opportunity_v0_3 import TransferOpportunity
from engineering.civprop.contracts.solar_transport_actor_access_v0_3 import assess_actor_transport
from engineering.civprop.contracts.solar_mission_opportunity_bridge_v0_3 import build_solar_mission_opportunity_catalog
from engineering.civprop.contracts.timeline_technology_bridge_v0_3 import build_timeline_technology_bridge
ROOT=Path(__file__).resolve().parents[2]
def run(seed,cache_path):
 cache=json.loads(cache_path.read_text())
 with tempfile.TemporaryDirectory(prefix='civprop_solar_v03_') as td:
  bp=build_bundle_dir(Path(td),cache_path); load_bundle(bp); hybrid=build_output(input_dir=bp,infrastructure_catalog_path=ROOT/'engineering/civprop/contracts/infrastructure_archetypes_v1.json',seed=seed)
 actors=json.loads((ROOT/'engineering/civprop/contracts/actor_machinery_test_baseline_v0_1.json').read_text())['actors']; tl={x['source_milestone_id']:x for x in build_timeline_technology_bridge(ROOT/'docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md','timeline-v0-1-0232bf23494f-20260925')['technology_frontier']}; cat=build_solar_mission_opportunity_catalog(ROOT/'reports/solar_civprop/NAV_READINESS_V1.json',ROOT/'dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv'); qb={}
 for q in cat['questions']: qb.setdefault(q['body_id'],[]).append(q)
 ledger=[]; counts=Counter()
 for row in cache['rows']:
  x=TransferOpportunity(**{k:(tuple(row[k]) if k=='provenance_refs' else row[k]) for k in TransferOpportunity.__dataclass_fields__})
  for a in actors:
   ass=assess_actor_transport(x,'CHEMICAL_IMPULSIVE',a['actor_id'],a['capability'],tl); gate='PREDECISION_WAIT' if ass.status=='SCREENABLE_GEOMETRY_AND_ACTOR_ACCESS' else 'TRANSPORT_OR_ACTOR_GATED'; reasons=['KNOWLEDGE_PRIOR_NOT_AUTHORIZED','GENERIC_OBSERVATION_ECONOMICS_NOT_AUTHORIZED'] if gate=='PREDECISION_WAIT' else list(ass.limiting_constraints); counts[gate]+=len(qb.get(x.destination_body_id,())); ledger.append({'year':int(x.departure_epoch_utc[:4]),'actor_id':a['actor_id'],'body_id':x.destination_body_id,'transport_status':ass.status,'predecision_status':gate,'rationale_codes':reasons,'departure_epoch_utc':x.departure_epoch_utc,'arrival_epoch_utc':x.arrival_epoch_utc,'time_of_flight_days':x.time_of_flight_days,'c3_km2_s2':x.c3_km2_s2,'heliocentric_transfer_dv_km_s':x.heliocentric_transfer_dv_km_s,'question_ids':[q['question_id'] for q in qb.get(x.destination_body_id,())]})
 return {'format':'CIVPROP_SOLAR_LONG_RUN_V0_3','classification':'NON_CANON_MACHINERY_TEST_PRE_GAP14','seed':seed,'hybrid_v0_3_bound_bundle':hybrid,'solar_candidate_catalog_counts':cat['counts'],'solar_transport_cache':{'start_year':cache['start_year'],'end_year':cache['end_year'],'rows':len(cache['rows']),'failures':len(cache['failures']),'departure_sampling':cache['departure_sampling']},'solar_predecision_ledger':ledger,'solar_predecision_counts':dict(sorted(counts.items())),'semantics':{'solar_transport_bound_into_accessibility_v1':True,'solar_ledger_is_not_parallel_decision_engine':True,'gap014_held_open':True,'advanced_propulsion_not_simulated':True}}
def canonical_sha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--transport-cache',required=True); ap.add_argument('--output',required=True); a=ap.parse_args(); o=run(a.seed,Path(a.transport_cache)); Path(a.output).write_text(json.dumps(o,sort_keys=True,separators=(',',':'))+'\n'); print('CIVPROP SOLAR V0.3 PRE-GAP14'); print('cache',o['solar_transport_cache']); print('predecision',o['solar_predecision_counts']); print('sha256',canonical_sha(o))
if __name__=='__main__': main()
