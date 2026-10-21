"""Non-canon: local lunar pricing, giant-system rendezvous, paired Route 1."""
import csv,json,time,resource,hashlib,math
from pathlib import Path
from datetime import date,timedelta,datetime
from decimal import Decimal
from collections import Counter,defaultdict
import numpy as np
from simulation.offworld_mvp.build8.three_arm_stage1.run_recovered_tables_arm_a_test_only import CombinedTable
from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
from simulation.offworld_mvp.build8.three_arm_stage1.rendezvous_decimal_fallback_test_only import rendezvous,stack
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import FlyCampaign,replay
from simulation.offworld_mvp.build8.three_arm_stage1.run_rendezvous_kt_v2_test_only import CostCampaign
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign,ALL_BODIES
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def main():
 start=time.monotonic();out=P/'PR427_COMPLETE_MOON_GIANT_RENDEZVOUS_REPORT_TEST_ONLY.json';assert not out.exists()
 M=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text());E=json.loads((P/'experiment.json').read_text());A=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text());R=json.loads((P/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json').read_text());world={x['body']:x for x in csv.DictReader((P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())}
 assert sha(P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json')=='9ae54bc7db94039b6f5916d080f36b1cb81f8dcd347ca2789779e2403d6f3eaf'
 assert sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv')=='2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73'
 mu=float(A['earth_mu_km3_s2']);parking=float(A['earth_mean_radius_km'])+float(A['parking_orbit_altitude_km']);lunar_r=float(world['MOON']['orbit_radius_km'])
 depdv=math.sqrt(2*mu/parking)-math.sqrt(mu/parking);arrdv=math.sqrt(2*mu/lunar_r)-math.sqrt(mu/lunar_r)
 nd,flymass=stack(depdv,float(A['payload_kg']),A)[0];nb,brake=stack(arrdv,float(A['payload_kg']),A)[0];nd2,rvmass=stack(depdv,brake,A)[0]
 moon={'flight_days':'NOT_APPLICABLE','departure_speed_relative_to_earth_km_s':0,'arrival_speed_relative_to_earth_km_s':0,'parking_radius_km':parking,'moon_orbit_radius_km':lunar_r,'earth_mu_km3_s2':mu,'departure_delta_v_km_s':depdv,'arrival_braking_delta_v_km_s':arrdv,'flyby_stages':nd,'flyby_mass_in_leo_kg':flymass,'rendezvous_departure_stages':nd2,'rendezvous_braking_stages':nb,'rendezvous_braking_stack_kg':brake,'rendezvous_mass_in_leo_kg':rvmass,'hand_reference_flyby_kg':940,'hand_reference_rendezvous_kg':1040,'difference_flyby_kg':flymass-940,'difference_rendezvous_kg':rvmass-1040}
 moon['flyby_model_units']=str(Decimal(str(flymass*float(A['launch_cost_usd_per_kg_leo'])+float(A['fixed_mission_cost_usd'])))/Decimal(1000000000))
 moon['rendezvous_model_units']=str(Decimal(str(rvmass*float(A['launch_cost_usd_per_kg_leo'])+float(R['rendezvous_fixed_mission_cost_usd'])))/Decimal(1000000000))
 print('MOON',json.dumps(moon),flush=True)
 table=CombinedTable();arrays={};original=table.old.travel._batch_states
 def states(body,epochs):
  if body not in M['tables']:return original(body,epochs)
  row=M['tables'][body]
  if body not in arrays:
   path=Path(M['table_root'])/(body+'.npy');assert sha(path)==row['table_sha256'];arrays[body]=np.load(path,mmap_mode='r')
  first=datetime.fromisoformat(M['first'].replace('Z','+00:00'));idx=[]
  for ep in epochs:
   tick=(ep-first).total_seconds()/(M['step_days']*86400);i=round(tick)
   assert 0<=i<len(arrays[body]) and abs(tick-i)<1e-9,('OFF_LATTICE',body,str(ep));idx.append(i)
  source,_=table.registry.source_for(body,epochs[0].isoformat().replace('+00:00','Z'));assert source.sha256==row['source_sha256']
  return np.asarray(arrays[body][idx]),source,None
 table.old.travel._batch_states=states
 giant={};geometry_stats=[]
 for year in (2026,2027):
  for body in ('JUPITER','SATURN','URANUS','NEPTUNE'):
   dates=base.departure_dates(year);results={};samples=0;trajectories=0
   children=[(b,w) for b,w in world.items() if w['parent']==body]
   for b,w in children:assert w['orbit_radius_km'] and w['parent_gm_km3_s2'],('MOON_LOCAL_PARAMETERS_MISSING',b)
   def sample(day):
    nonlocal samples,trajectories
    g=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
    routes=g['trajectories'];samples+=1;trajectories+=len(routes);flag=any(float(x['departure_vinf_km_s'])<=10 and float(x['arrival_vinf_km_s'])<=10 for x in routes)
    fflag=any(float(x['departure_vinf_km_s'])<=10 for x in routes)
    for x in routes:
     dep=float(x['departure_vinf_km_s']);arr=float(x['arrival_vinf_km_s']);days=float(x['flight_days'])
     for target,w in [(body,None)]+children:
      if w is None:q=rendezvous(dep,arr,days,A,R,body=body,year=year)
      else:q=rendezvous(dep,arr,days,A,{**R,'parent_gm_km3_s2':w['parent_gm_km3_s2'],'orbit_radius_km':w['orbit_radius_km']},moon=True,body=target,year=year)
      key=(year,target);candidate=(Decimal(str(q['total_usd'])),day,days,dep,arr)
      if key not in giant or candidate<giant[key][0]:giant[key]=(candidate,q)
    results[day]=(flag,fflag);table.clear()
   for day in dates:sample(day)
   extras=set()
   for col in (0,1):
    brackets=[(a,b) for a,b in zip(dates,dates[1:]) if results[a][col]!=results[b][col]]
    for a,b in brackets[:E['sampling']['max_transition_brackets_per_body_year']]:
     d=date.fromisoformat(a)+timedelta(days=E['sampling']['refinement_step_days'])
     while d<date.fromisoformat(b):extras.add(d.isoformat());d+=timedelta(days=E['sampling']['refinement_step_days'])
   for day in sorted(extras-set(dates)):sample(day)
   geometry_stats.append({'year':year,'parent':body,'sampled_departures':samples,'sampled_trajectories':trajectories})
   print('RENDEZVOUS_GEOMETRY',year,body,samples,trajectories,'ELAPSED',round(time.monotonic()-start,2),flush=True)
 fly={}
 for x in csv.DictReader((P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv').open()):fly[(int(x['year']),x['body'])]={'model_units':price(float(x['minimum_departure_vinf_km_s']),A)['model_units'],'parent':''}
 oldrv={}
 for x in csv.DictReader((P/'RENDEZVOUS_V2_PRICES_TEST_ONLY.csv').open()):
  if x['status']=='PRICED_TEST_ONLY':oldrv[(int(x['year']),x['body'])]=x
 for x in json.loads((P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json').read_text())['body_years']:
  if x['model_units'] is not None:fly[(x['year'],x['body'])]={'model_units':x['model_units'],'parent':''}
 for year in (2026,2027):
  for b,w in world.items():
   if w['parent'] and (year,w['parent']) in fly:fly[(year,b)]={'model_units':fly[(year,w['parent'])]['model_units'],'parent':w['parent']}
  fly[(year,'MOON')]={'model_units':moon['flyby_model_units'],'parent':'EARTH'}
  oldrv[(year,'MOON')]={'model_units':moon['rendezvous_model_units'],'status':'PRICED_TEST_ONLY'}
 for key,(candidate,q) in giant.items():oldrv[key]={'model_units':q['model_units'],'status':'PRICED_TEST_ONLY'}
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True);control_hash=replay(control)
 assert control_hash=='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
 cases={}
 for name,cls,prices in [('A1_FLYBY_COMPLETE',FlyCampaign,fly),('A1_RENDEZVOUS_COMPLETE',CostCampaign,oldrv)]:
  c=cls(prices,name);h=replay(c);receipts=c.receipts;by=defaultdict(list)
  for r in receipts:by[r['body']].append(r)
  blockers=Counter(x['primary_blocker'] for x in c.attempts if x['outcome']=='BLOCKED')
  unpriced=sorted(b for b in ALL_BODIES if not any((y,b) in prices for y in (2026,2027)))
  cases[name]={'variant_sha256':h,'funded_stages':len(receipts),'funded_bodies':len(by),'cash_model_units':str(sum((Decimal(x['amount']) for x in receipts),Decimal(0))),'blockers':dict(blockers),'unpriced_bodies':unpriced,'body_stages':{b:{'A1':sum(x['stage']=='A1' for x in rr),'other':sum(x['stage']!='A1' for x in rr),'total':len(rr),'distinct_sponsors':len({x['sponsor'] for x in rr})} for b,rr in sorted(by.items())}}
  print('CASE',name,'FUNDED',len(receipts),len(by),'CASH',cases[name]['cash_model_units'],'BLOCKERS',dict(blockers),'UNPRICED',unpriced,flush=True)
 giant_rows=[{'year':y,'body':b,'departure_date':v[0][1],'flight_days':v[0][2],'departure_vinf_km_s':v[0][3],'arrival_vinf_km_s':v[0][4],'price_model_units':v[1]['model_units'],'mass_in_leo_kg':str(v[1]['mass_in_leo_kg']),'departure_stages':v[1]['departure_stages'],'braking_stages':v[1]['braking_stages'],'arrival_braking_delta_v_km_s':v[1]['arrival_braking_delta_v_km_s']} for (y,b),v in sorted(giant.items())]
 report={'classification':'TEST_ONLY_NONCANON','numpy_version':np.__version__,'moon':moon,'giant_rendezvous':giant_rows,'geometry_stats':geometry_stats,'cases':cases,'control_sha256':control_hash,'table_manifest_sha256':sha(P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json'),'database_sha256':sha(Path('data/LOOM_2226.sqlite3')),'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':rss()}
 with out.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('COMPLETE',sha(out),'SECONDS',report['elapsed_seconds'],'PEAK',rss(),flush=True)
if __name__=='__main__':main()
