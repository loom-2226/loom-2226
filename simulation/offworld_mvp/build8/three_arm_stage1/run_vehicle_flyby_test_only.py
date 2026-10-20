"""PR427 only; 59-body table geometry and opt-in Route 1 flyby cost."""
import csv,gc,hashlib,json,math,resource,time
from collections import Counter,defaultdict
from datetime import date,timedelta
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1.run_recovered_tables_arm_a_test_only import CombinedTable,departure_dates
from simulation.offworld_mvp.build8.three_arm_stage1 import vehicle_flyby_cost_test_only as cost
from simulation.offworld_mvp.build8.route1_body_campaign import SETTINGS
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash
P=Path(__file__).resolve().parent;A=P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json';OUT=P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv';REPORT=P/'VEHICLE_FLYBY_REPORT_TEST_ONLY.json';COST=P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def peak():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def write(p,rows):
 assert not p.exists(),f'NO_OVERWRITE {p}'
 with p.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
class VehicleCampaign(AllBodyCampaign):
 def __init__(self,prices,identity):
  super().__init__(body_count=90,ceilings_enabled=False);self.prices=prices;self.identity=identity
 def attempt(self,k,sponsor,body,stage,year,used=0):
  source='UNCHANGED_A2';old=SETTINGS['A1_SERVICE_PRICE']
  try:
   if stage=='A1':
    y=year if year in (2026,2027) else 2026
    q=self.prices.get((y,body))
    if q is None:source='ABSTRACT_FALLBACK_NOT_IN_59';price=old
    else:source='VEHICLE_COST_TABLE' if year==y else 'VEHICLE_COST_HELD_2026';price=D(q['model_units'])
    SETTINGS['A1_SERVICE_PRICE']=price
   row=super().attempt(k,sponsor,body,stage,year,used)
  finally:SETTINGS['A1_SERVICE_PRICE']=old
  row['price_source']=source
  if row['outcome']=='FUNDED':self.receipts[-1]['price_source']=source
  return row
 def limits(self):
  d=super().limits();d['vehicle_flyby_identity']=self.identity;return d
 def report(self):
  d=super().report();d['vehicle_flyby_identity']=self.identity;return d

def main():
 t=time.monotonic();a=json.loads(A.read_text());assert a['departure_speed_limit'] is None and a['arrival_speed_limit'] is None
 from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
 original=list(csv.DictReader((P/'RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv').open()));old={(int(r['year']),r['body']):r for r in original if r['mission_type_id']=='flyby'};assert len(old)==118
 source=[P/'experiment.json',P/'table_manifest.json',P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json',P/'RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv',P/'A_VEHICLE_MISSION_PAIRS.csv',P/'RECOVERED_ARM_A_TABLE_PAIRS_TEST_ONLY.csv',P/'run_recovered_tables_arm_a_test_only.py',P/'vehicle_flyby_cost_test_only.py',P/'run_vehicle_flyby_test_only.py',P/'table_adapter.py',P/'RECOVERED_ARM_A_TABLE_CHECKPOINT_TEST_ONLY.json',P/'A_BODY_YEAR_REPORT_LIMITS.csv',Path('src/loom_solar_gis.py')]
 sourcehash={str(x):sha(x) for x in source};identity={'classification':'KT_AUTHORED_TEST_ONLY_NONCANON','authored_input':a,'authored_input_sha256':sha(A),'source_sha256':sourcehash,'geometry_policy':'TABLE_PATH_REUSE_PINNED_DEPARTURE_LATTICE_WITHOUT_SPEED_LIMITS','pricing_policy':'MINIMUM_DEPARTURE_VINF_PER_BODY_YEAR','held_year':2026};idh=digest(identity)
 print('AUTHORED_INPUT',json.dumps(a,sort_keys=True),'AUTHORED_SHA256',sha(A),'RUN_IDENTITY_SHA256',idh,flush=True)
 tests=cost.hand_tests(a);assert all(x['stage_count_matches'] for x in tests)
 table=CombinedTable();oldcheck=json.loads((P/'RECOVERED_ARM_A_TABLE_CHECKPOINT_TEST_ONLY.json').read_text());origcheck=json.loads((Path(json.loads((P/'table_arm_a_config.json').read_text())['output_root'])/'A_CHECKPOINT_refined_previous.json').read_text())
 rows=[];diff=[];count=0;gt=time.monotonic()
 for y in (2026,2027):
  for b in sorted({body for _,body in old}):
   key=f'{y}|{b}'
   if b in {k.split('|')[1] for k in origcheck['completed']}:
    dates=sorted(origcheck['completed'][key]['dates'])
   else:
    # Keep the original 34-body departure dates (coarse plus previously refined), no speed-filter-driven change to the lattice.
    dates=departure_dates(y)
    # Previous recovered run's refined dates are not persisted individually. Reconstruct using the authored transition rule.
    # Unrestricted speeds make all sampled transfers candidates; use the same coarse geometry and all 1-day dates
    # in previously bounded flyby/rendezvous feasibility transition brackets.
    old_recovered=oldcheck['recovered'][key];assert old_recovered['departures']>=len(dates)
    if old_recovered['departures']>len(dates):
     # Reconstruct original refinement bracket by original bounded evaluator, identical authored logic.
     from simulation.offworld_mvp.build8.three_arm_stage1 import pair_pricing as pp
     E=base.E;ps=pp.pairs(E);entries={}
     for day in dates:
      g=table.geometry(E['origin'],b,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
      entries[day]={m['mission_type_id']:pp.evaluate(g,v,m,E) for v,m in ps};table.clear()
     refined=base.refine(dates,entries,'rendezvous')+base.refine(dates,entries,'flyby');dates=sorted(set(dates+refined))
     assert len(dates)==old_recovered['departures'],('RECOVERED_DEPARTURE_SET_MISMATCH',key,len(dates),old_recovered['departures'])
   candidates=[]
   for day in dates:
    g=table.geometry(base.E['origin'],b,day,strategy=base.E['sampling']['strategy'],flight_range_days=base.E['sampling']['flight_range_days'])
    if key in origcheck['completed']:
     assert digest(g)==origcheck['completed'][key]['dates'][day]['geometry_sha256'],('ORIGINAL_GEOMETRY_MISMATCH',key,day)
    for r in g['trajectories']:
     v=float(r['departure_vinf_km_s']);candidates.append((v,day,float(r['flight_days'])))
    count+=1;table.clear()
   if not candidates:raise AssertionError('NO_TRAJECTORY:'+key)
   v,day,flight=min(candidates,key=lambda x:(x[0],x[1],x[2]));p=cost.price(v,a);o=old[(y,b)]
   record={'year':y,'body':b,'status':'PRICED_VEHICLE_TEST_ONLY','minimum_departure_vinf_km_s':repr(v),'best_departure_date':day,'best_flight_days':repr(flight),'departures_searched':len(dates),'stage_count':p['stages'],'mass_in_leo_kg':repr(p['mass_in_leo_kg']),'injection_delta_v_km_s':repr(p['leo_injection_delta_v_km_s']),'launch_cost_usd':repr(p['launch_cost_usd']),'fixed_cost_usd':repr(p['fixed_mission_cost_usd']),'vehicle_total_usd':repr(p['total_usd']),'model_units':p['model_units'],'old_proxy_status':o['status'],'old_proxy_usd':o['lowest_price_usd'],'old_proxy_departure_date':o['best_departure_date'],'old_proxy_flight_days':o['best_flight_days'],'run_identity':idh}
   rows.append(record)
   if o['status']=='PRICED_TEST_ONLY':
    if day!=o['best_departure_date']:diff.append({'year':y,'body':b,'field':'best_departure_date','old':o['best_departure_date'],'new':day})
    if o['lowest_price_usd'] and D(o['lowest_price_usd'])/D(base.E['price_rate_usd_millions_per_km_s'])/D(1000000)!=D(str(v)):
     diff.append({'year':y,'body':b,'field':'minimum_departure_speed','old':str(D(o['lowest_price_usd'])/D(base.E['price_rate_usd_millions_per_km_s'])/D(1000000)),'new':repr(v)})
   print('GEOMETRY',key,'SPEED',v,'DATE',day,'FLIGHT',flight,'STAGES',p['stages'],'USD',p['total_usd'],flush=True)
 write(OUT,rows);write(COST,[{k:r[k] for k in ('year','body','stage_count','mass_in_leo_kg','injection_delta_v_km_s','launch_cost_usd','fixed_cost_usd','vehicle_total_usd','old_proxy_status','old_proxy_usd','run_identity')} for r in rows]);geomtime=time.monotonic()-gt;print('GEOMETRY_COMPLETE',len(rows),count,'SECONDS',geomtime,'DIFFERENCES',len(diff),flush=True)
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True);control.record_states(2026);ct=time.monotonic();z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':control});paid={(r['year'],r['executor']) for r in control.receipts};z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly']);z['campaign']=control.report();z['campaign']['runtime_total_seconds']=0;controlhash=stable_hash(z);assert controlhash==a['route1_control_sha256'],controlhash
 print('CONTROL_PASS',controlhash,'SECONDS',time.monotonic()-ct,flush=True)
 vt=time.monotonic();campaign=VehicleCampaign({(int(r['year']),r['body']):r for r in rows},idh);campaign.record_states(2026);z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':campaign});paid={(r['year'],r['executor']) for r in campaign.receipts};z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly']);z['campaign']=campaign.report();z['campaign']['runtime_total_seconds']=0;vh=stable_hash(z)
 receipts=campaign.receipts;block=Counter(r['primary_blocker'] for r in campaign.attempts if r['outcome']=='BLOCKED');never=sorted(set(campaign.bodies)-{r['body'] for r in receipts});formerly=json.loads((P/'RECOVERED_FLYBY_POLICY_FULL_CLOCK_REPORT_TEST_ONLY.json').read_text())['cases'][-1]['never_funded'];first={}
 for b in formerly:
  q=next((r for r in receipts if r['body']==b and r['stage']=='A1'),None)
  first[b]={'funded':q is not None,'year':q['year'] if q else None,'sponsor':q['sponsor'] if q else None,'price_model_units':q['amount'] if q else None,'blockers':dict(Counter(x['primary_blocker'] for x in campaign.attempts if x['body']==b and x['outcome']=='BLOCKED')) if not q else {}}
 spend=sum((D(r['amount']) for r in receipts),D(0));report={'classification':'KT_AUTHORED_TEST_ONLY_NONCANON','authored_input':a,'authored_sha256':sha(A),'run_identity':identity,'run_identity_sha256':idh,'source_sha256':sourcehash,'geometry_body_years':len(rows),'geometry_departures':count,'geometry_seconds':geomtime,'geometry_differences_against_old_priced':diff,'hand_tests':tests,'control_sha256':controlhash,'variant_sha256':vh,'funded_stages':len(receipts),'funded_bodies':len({r['body'] for r in receipts}),'spent_model_units':str(spend),'blocked_attempts':sum(block.values()),'blockers':dict(block),'former_23_first_funded':first,'never_funded':never,'never_funded_blockers':{b:dict(Counter(x['primary_blocker'] for x in campaign.attempts if x['body']==b and x['outcome']=='BLOCKED')) for b in never},'route1_seconds':time.monotonic()-vt,'total_seconds':time.monotonic()-t,'peak_rss_bytes':peak(),'geometry_csv_sha256':sha(OUT),'prices_csv_sha256':sha(COST)}
 assert not REPORT.exists();REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print('COMPLETE',len(receipts),len({r['body'] for r in receipts}),'SPENT',spend,'BLOCKERS',block,'NEVER',never,'SECONDS',report['total_seconds'],'PEAK',peak(),flush=True)
if __name__=='__main__':main()
