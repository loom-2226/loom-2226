"""One-assist coarse-grid Lambert pilot. No changes to existing geometry."""
import csv,hashlib,json,math,resource,sqlite3,time
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter
import numpy as np
from lamberthub import izzo2015
from simulation.offworld_mvp.build7 import compile_solar_accessibility as legacy
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();cfg=json.loads((P/'PR427_ASSIST_PILOT_INPUT_TEST_ONLY.json').read_text());old=json.loads((P/'table_manifest_direct_time.json').read_text());giant=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text());earth=json.loads((P/'PR427_ASSIST_EARTH_TABLE_REPORT_TEST_ONLY.json').read_text());auth=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text())
 for name,digest in cfg['parent_hashes'].items():
  path=P/name if name!='earth_table_sha256' else Path(earth['table_path'])
  assert sha(path)==digest,('PARENT_HASH_MISMATCH',name)
 assert cfg['one_assist_per_trip']==1 and cfg['total_trip_days_max'] is None and cfg['direct_allowed']
 db=ROOT/'data/LOOM_2226.sqlite3';conn=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True);conn.row_factory=sqlite3.Row
 mapping={'EARTH':'EA','JUPITER':'JU','SATURN':'SA','URANUS':'UR','NEPTUNE':'NE','MARS':'MA','MERCURY':'ME','VENUS':'VE','CERES':'CER','PLUTO':'PL','HYGIEA':'HYG','PALLAS':'PAL','PSYCHE':'PSY','VESTA':'VST'}
 names=set(old['tables'])|set(giant['tables'])|{'EARTH'}
 authority={}
 for body,id in mapping.items():
  x=conn.execute('select gm_km3_s2,mean_radius_km from celestial_dynamics where entity_id=?',(id,)).fetchone()
  if x and x['gm_km3_s2'] is not None and x['mean_radius_km'] is not None:authority[body]={'gm':float(x['gm_km3_s2']),'radius':float(x['mean_radius_km']),'source':'data/LOOM_2226.sqlite3:celestial_dynamics:'+id}
 eligible=sorted((names & set(authority)) - {'EARTH'});skips=[]
 for b in sorted(names-{'EARTH'}):
  if b not in authority:skips.append({'body':b,'reason':'NO_WORLD_AUTHORITY_GM_OR_RADIUS'})
 for b in sorted(set(mapping)-names):skips.append({'body':b,'reason':'NO_STATE_TABLE'})
 arrays={};first=datetime.fromisoformat(old['first'].replace('Z','+00:00'));step=old['step_days']*86400
 def state(b,epoch):
  if b not in arrays:
   if b=='EARTH':path=Path(earth['table_path']);digest=earth['table_sha256']
   elif b in giant['tables']:path=Path(giant['table_root'])/(b+'.npy');digest=giant['tables'][b]['table_sha256']
   else:path=Path(old['table_root'])/(b+'.npy');digest=old['tables'][b]['sha256']
   assert sha(path)==digest,('STATE_HASH_MISMATCH',b);arrays[b]=np.load(path,mmap_mode='r')
  i=round((epoch-first).total_seconds()/step);assert 0<=i<len(arrays[b]) and first+timedelta(seconds=i*step)==epoch,('OFF_LATTICE',b,str(epoch));return arrays[b][i]
 def leg(a,b,ta,tb):
  x=state(a,ta);y=state(b,tb);v,w=izzo2015(legacy.SUN_GM_KM3_S2,x[:3],y[:3],(tb-ta).total_seconds(),M=0,prograde=True,low_path=True);return v-x[3:],w-y[3:]
 def burn(vi,vo,mu,r):
  a=float(np.linalg.norm(vi));b=float(np.linalg.norm(vo));rp=r+cfg['minimum_altitude_km'];bend=2*math.asin(1/(1+rp*a*a/mu));angle=math.atan2(float(np.linalg.norm(np.cross(vi,vo))),float(np.dot(vi,vo)))
  if bend<math.radians(cfg['minimum_bend_degrees']):return None,bend,'BELOW_ONE_DEGREE'
  if angle<=bend:return abs(b-a),bend,None
  return math.sqrt(a*a+b*b-2*a*b*math.cos(angle-bend)),bend,None
 def stage(dv,payload):
  ve=float(auth['hydrolox_exhaust_velocity_km_s']);eps=float(auth['dry_mass_fraction_dry_over_dry_plus_propellant']);n=max(1,math.floor(dv/(ve*math.log(1/eps)))+1)
  while eps*math.exp(dv/(n*ve))>=1:n+=1
  q=math.exp(dv/(n*ve));return payload*(q*(1-eps)/(1-eps*q))**n,n
 def evaluate(dep,assist,target,ta,tb,tc):
  vin,ain=leg('EARTH',assist,ta,tb);aout,vout=leg(assist,target,tb,tc);dv,bend,skip=burn(ain,aout,authority[assist]['gm'],authority[assist]['radius'])
  if skip:return None,skip,bend
  payload=float(auth['payload_kg']);payload,nassist=stage(dv,payload);mu=authority['EARTH']['gm'];r=authority['EARTH']['radius']+float(auth['parking_orbit_altitude_km']);vinf=float(np.linalg.norm(vin));departure=math.sqrt(vinf*vinf+2*mu/r)-math.sqrt(mu/r);mass,ndep=stage(departure,payload)
  usd=mass*float(auth['launch_cost_usd_per_kg_leo'])+float(auth['fixed_mission_cost_usd']);return {'route':['EARTH',assist,target],'departure':ta.isoformat(),'assist_arrival':tb.isoformat(),'target_arrival':tc.isoformat(),'leg_days':[(tb-ta).days,(tc-tb).days],'assist_burn_km_s':dv,'max_bend_degrees':math.degrees(bend),'departure_vinf_km_s':vinf,'arrival_vinf_km_s':float(np.linalg.norm(vout)),'departure_stages':ndep,'assist_stages':nassist,'mass_in_leo_kg':mass,'price_usd':usd},None,bend
 # Hand arithmetic, using authority Earth radius and gravity; exact geometric construction.
 mu=authority['EARTH']['gm'];rp=authority['EARTH']['radius']+cfg['minimum_altitude_km'];v=5.;bend=2*math.asin(1/(1+rp*v*v/mu));assert burn(np.array([v,0.,0.]),np.array([v,0.,0.]),mu,authority['EARTH']['radius'])[0]==0
 mismatch=burn(np.array([v,0.,0.]),np.array([v+1,0.,0.]),mu,authority['EARTH']['radius'])[0];assert mismatch==1.
 print('HAND_TEST',json.dumps({'earth_mu':mu,'earth_pass_radius_km':rp,'v_km_s':v,'bend_degrees':math.degrees(bend),'matched_burn_km_s':0,'one_km_s_mismatch_burn_km_s':mismatch}),flush=True)
 report={'classification':'TEST_ONLY_NONCANON','input_sha256':sha(P/'PR427_ASSIST_PILOT_INPUT_TEST_ONLY.json'),'world_database_sha256':sha(db),'earth_table_sha256':earth['table_sha256'],'candidate_list':eligible,'excluded':skips,'hand_bend_degrees':math.degrees(bend),'pilot':[],'search_bound':'EXHAUSTIVE_AUTHORED_DISCRETE_GRID_NO_HIDDEN_CAP','full_run_executed':False}
 path=P/'PR427_ASSIST_PILOT_PROGRESS_TEST_ONLY.jsonl';assert not path.exists()
 def checkpoint(row):
  with path.open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
 # Every loop bound is authored. Arrival times on the same quarter-day lattice.
 for target in cfg['pilot_targets_2026']:
  for label,steps in [('base',cfg['search_steps_days']),('half',cfg['halved_search_steps_days'])] if target==cfg['pilot_targets_2026'][0] else [('base',cfg['search_steps_days'])]:
   t=time.monotonic();count=0;solved=0;below=Counter();best=None;failure=Counter();depstep=steps['departure'];astep=steps['assist_arrival'];tstep=steps['target_arrival']
   depdates=[first+timedelta(days=d) for d in range(0,(datetime(2027,1,1,tzinfo=timezone.utc)-first).days,depstep)]
   leg1=range(cfg['leg_days_min'],cfg['leg_days_max']+1,astep);leg2=range(cfg['leg_days_min'],cfg['leg_days_max']+1,tstep)
   for assist in eligible:
    if assist==target:continue
    for ta in depdates:
     for d1 in leg1:
      tb=ta+timedelta(days=d1)
      for d2 in leg2:
       tc=tb+timedelta(days=d2);count+=1
       try:row,reason,b= evaluate(None,assist,target,ta,tb,tc)
       except (ValueError,RuntimeError,ZeroDivisionError,OverflowError) as e:failure[type(e).__name__]+=1;continue
       solved+=1
       if reason:below[assist]+=1;continue
       if best is None or (row['price_usd'],row['route'],row['departure'],row['assist_arrival'],row['target_arrival'])<(best['price_usd'],best['route'],best['departure'],best['assist_arrival'],best['target_arrival']):best=row
   direct=json.loads((P/'PR427_GIANT_MOON_REPLAY_REPORT_TEST_ONLY.json').read_text())
   # Direct price from already pinned 2026 flyby geometry, never new geometry.
   baseline=[r for r in csv.DictReader((P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv').open()) if r['body']==target and r['year']=='2026']
   if not baseline:
    baseline=[r for r in json.loads((P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json').read_text())['body_years'] if r['body']==target and r['year']==2026]
    direct_price=float(baseline[0]['model_units'])*1e9 if baseline and baseline[0]['model_units'] is not None else None
   else:direct_price=price(float(baseline[0]['minimum_departure_vinf_km_s']),auth)['total_usd']
   winning=best if best is not None and (direct_price is None or best['price_usd']<direct_price) else {'route':['EARTH',target],'price_usd':direct_price,'direct':True}
   row={'target':target,'search':label,'steps_days':steps,'trajectory_count':count,'solved_lambert_pairs':solved,'below_bend_by_candidate':dict(below),'errors':dict(failure),'best_assisted':best,'direct_price_usd':direct_price,'winning':winning,'elapsed_seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
   report['pilot'].append(row);checkpoint(row);print('PILOT',json.dumps(row,sort_keys=True),flush=True)
 report['elapsed_seconds']=time.monotonic()-start;report['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
 report['estimated_full_63x2_seconds']=sum(r['elapsed_seconds'] for r in report['pilot'] if r['search']=='base')/len(cfg['pilot_targets_2026'])*cfg['full_scope_body_count']*len(cfg['full_scope_years'])
 out=P/'PR427_ASSIST_PILOT_REPORT_TEST_ONLY.json';assert not out.exists();out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('DONE',sha(out),report['elapsed_seconds'],report['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
