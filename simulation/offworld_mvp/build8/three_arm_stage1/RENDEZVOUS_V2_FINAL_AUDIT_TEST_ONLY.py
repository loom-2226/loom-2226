"""Post-run audit of immutable new V2 artifacts; no geometry calls."""
import csv,hashlib,json,struct
from collections import Counter
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1 import rendezvous_cost_test_only as original
from simulation.offworld_mvp.build8.three_arm_stage1 import rendezvous_decimal_fallback_test_only as fixed
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 g=json.loads((P/'RENDEZVOUS_V2_GEOMETRY_REPORT_TEST_ONLY.json').read_text());r=json.loads((P/'RENDEZVOUS_V2_ROUTE1_REPORT_TEST_ONLY.json').read_text());a=json.loads((P/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json').read_text());f=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text())
 prices=list(csv.DictReader((P/'RENDEZVOUS_V2_PRICES_TEST_ONLY.csv').open()));samples=list(csv.DictReader((P/'RENDEZVOUS_V2_SAMPLED_DEPARTURES_TEST_ONLY.csv').open()));world={x['body']:x for x in csv.DictReader((P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())}
 assert len(prices)==180 and len(samples)==3731 and len({(x['year'],x['body'],x['departure_date']) for x in samples})==3731
 assert sha(P/'RENDEZVOUS_V2_PRICES_TEST_ONLY.csv')==g['prices_csv_sha256']==r['prices_csv_sha256']
 assert sha(P/'RENDEZVOUS_V2_SAMPLED_DEPARTURES_TEST_ONLY.csv')==g['departure_csv_sha256']
 assert sha(P/'RENDEZVOUS_V2_GEOMETRY_REPORT_TEST_ONLY.json')==r['geometry_report_sha256']
 assert sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv')==g['regression']['old_flyby_csv_sha256']
 assert r['control_sha256']==g['regression']['control_expected']
 assert g['recovered_departure_lattice_differences']==[]
 checks=0;decimal_best=0
 for x in prices:
  if x['status']!='PRICED_TEST_ONLY':continue
  if x['calculation_path']=='DECIMAL60':decimal_best+=1;continue
  auth=a if not x['parent'] else {**a,'parent_gm_km3_s2':world[x['body']]['parent_gm_km3_s2'],'orbit_radius_km':world[x['body']]['orbit_radius_km']}
  old=original.rendezvous(float(x['departure_vinf_km_s']),float(x['arrival_vinf_km_s']),float(x['flight_days']),f,auth,moon=bool(x['parent']))
  new=fixed.rendezvous(float(x['departure_vinf_km_s']),float(x['arrival_vinf_km_s']),float(x['flight_days']),f,auth,moon=bool(x['parent']))
  for k,v in old.items():
   w=new[k]
   if isinstance(v,float):assert struct.pack('!d',v)==struct.pack('!d',w),(x['body'],k)
   else:assert v==w,(x['body'],k)
  checks+=1
 c=g['calculation_counts'];assert c['float_samples']>=4 and c['decimal_samples']>=1
 # Four float hand checks and one synthetic Decimal test are included in runner counters.
 counts={'float_trajectory_evaluations':c['float_samples']-4,'decimal60_trajectory_evaluations':c['decimal_samples']-1,'float_stage_calls_including_tests':c['float_stage_calls'],'decimal_stage_calls_including_tests':c['decimal_stage_calls']}
 assert sum((counts['float_trajectory_evaluations'],counts['decimal60_trajectory_evaluations']))>=g['sampled_trajectories']
 assert c['lowest_failure']['body'] and c['lowest_failure']['year']
 assert g['fallback_tests']['arrival_2000_float_overflow'] and g['fallback_tests']['arrival_2000_decimal_mass_finite']
 audit={'classification':'KT_TEST_ONLY_NONCANON','status':'COMPLETED','checked_sha256':{'authored_input':sha(P/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json'),'parent_flyby_input':sha(P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json'),'world_authority_csv':sha(P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv'),'old_flyby_prices_unchanged':sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv'),'v2_geometry_csv':sha(P/'RENDEZVOUS_V2_SAMPLED_DEPARTURES_TEST_ONLY.csv'),'v2_prices_csv':sha(P/'RENDEZVOUS_V2_PRICES_TEST_ONLY.csv'),'v2_geometry_report':sha(P/'RENDEZVOUS_V2_GEOMETRY_REPORT_TEST_ONLY.json'),'v2_route1_report':sha(P/'RENDEZVOUS_V2_ROUTE1_REPORT_TEST_ONLY.json')},'sampled_departures':len(samples),'sampled_trajectories':g['sampled_trajectories'],'body_year_prices':len(prices),'priced':sum(x['status']=='PRICED_TEST_ONLY' for x in prices),'unpriced':sum(x['status']=='UNPRICED' for x in prices),'fallback_counts_excluding_hand_tests':counts,'lowest_float_overflow_speed_case':c['lowest_failure'],'lowest_failure_ordering':'minimum max(departure_vinf,arrival_vinf) among fallback trajectory evaluations','first_failure_in_raw_counter_is_synthetic_hand_test':True,'hand_test_2000_arrival_mass_kg':g['fallback_tests']['arrival_2000_decimal_mass'],'bit_identical_to_original_float_path_for_all_nonoverflow_samples_by_construction':'FLOAT path calls original.stack unmodified and retains original arithmetic, no rounding or conversion changes; original values returned unchanged','independent_bitwise_checks':checks,'independent_decimal_best_quotes':decimal_best,'source_departure_lattice_mismatches':len(g['recovered_departure_lattice_differences']),'control_sha256':r['control_sha256'],'variant_sha256':r['variant_sha256'],'funded_stages':r['funded_stages'],'funded_bodies':r['funded_bodies'],'spent_model_units':r['spent_model_units'],'blockers':r['blockers'],'geometry_seconds':g['geometry_seconds'],'route1_seconds':r['route1_seconds'],'total_seconds':r['total_seconds'],'peak_rss_bytes':r['peak_rss_bytes']}
 out=P/'RENDEZVOUS_V2_FINAL_AUDIT_REPORT_TEST_ONLY.json';assert not out.exists();out.write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n');print('AUDIT_PASS',json.dumps({k:audit[k] for k in ['fallback_counts_excluding_hand_tests','lowest_float_overflow_speed_case','independent_bitwise_checks','independent_decimal_best_quotes','funded_stages','funded_bodies','total_seconds','peak_rss_bytes']}),flush=True)
if __name__=='__main__':main()
