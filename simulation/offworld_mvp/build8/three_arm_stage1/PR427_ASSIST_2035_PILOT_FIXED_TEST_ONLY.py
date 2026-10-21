"""2026 three-target one-assist pilot on extended qualified planet tables."""
import csv,hashlib,json,math,resource,sqlite3,time
from pathlib import Path
from datetime import datetime,timedelta,timezone
from collections import Counter
import numpy as np
from lamberthub import izzo2015
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
P=Path(__file__).resolve().parent;ROOT=P.parents[3];OUT=Path('/home/ubuntu/LOOM-output/pr427_assist_2035_tables_test_only')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();cfg=json.loads((P/'PR427_ASSIST_PILOT_INPUT_TEST_ONLY.json').read_text());manifest=json.loads((P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json').read_text());old=json.loads((P/'table_manifest_direct_time.json').read_text());a=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text());db=ROOT/'data/LOOM_2226.sqlite3';con=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True);names=manifest['tables'];assert manifest['last'].startswith('2035-12-31') and cfg['one_assist_per_trip']==1
 for key,digest in cfg['parent_hashes'].items():
  path=P/key if key!='earth_table_sha256' else Path(json.loads((P/'PR427_ASSIST_EARTH_TABLE_REPORT_TEST_ONLY.json').read_text())['table_path']);assert sha(path)==digest,(key,'PARENT_HASH')
 ids={'EARTH':'EA','MERCURY':'ME','VENUS':'VE','MARS':'MA','JUPITER':'JU','SATURN':'SA','URANUS':'UR','NEPTUNE':'NE','PLUTO':'PL'};grav={};excluded=[]
 for b in sorted(set(old['tables'])|set(names)):
  if b not in names:excluded.append({'body':b,'reason':'NO_EXTENDED_TABLE_RECOVERED_SMALL_BODY_WINDOW_ENDS_2031-12-31'});continue
  x=con.execute('select gm_km3_s2,mean_radius_km from celestial_dynamics where entity_id=?',(ids[b],)).fetchone()
  if x is None or None in x:excluded.append({'body':b,'reason':'MISSING_WORLD_AUTHORITY_GM_OR_RADIUS'});continue
  grav[b]=(float(x[0]),float(x[1]))
 assert all(b in grav for b in ['EARTH','NEPTUNE','PLUTO','MARS']);candidates=sorted(set(grav)-{'EARTH'});first=datetime.fromisoformat(old['first'].replace('Z','+00:00'));step=old['step_days'];arrays={}
 for b in names:
  p=Path(names[b]['table_path']);assert sha(p)==names[b]['sha256'],('TABLE_HASH',b);arrays[b]=np.load(p,mmap_mode='r')
 def state(b,dt):
  k=round((dt-first).total_seconds()/(86400*step));assert 0<=k<len(arrays[b]) and first+timedelta(days=k*step)==dt,('OFF_LATTICE',b,dt.isoformat());return arrays[b][k]
 mu_sun=float(con.execute("select gm_km3_s2 from celestial_dynamics where entity_id='SU'").fetchone()[0])
 def leg(a,b,t,u):
  x=state(a,t);y=state(b,u);v,w=izzo2015(mu_sun,x[:3],y[:3],(u-t).total_seconds(),M=0,prograde=True,low_path=True);return v-x[3:],w-y[3:]
 def stage(dv,m):
  ve=float(a['hydrolox_exhaust_velocity_km_s']);eps=float(a['dry_mass_fraction_dry_over_dry_plus_propellant']);n=max(1,math.floor(dv/(ve*math.log(1/eps)))+1)
  while eps*math.exp(dv/(n*ve))>=1:n+=1
  q=math.exp(dv/(n*ve));return m*(q*(1-eps)/(1-eps*q))**n,n
 def bend(vi,vo,gm,radius):
  aa=float(np.linalg.norm(vi));bb=float(np.linalg.norm(vo));d=2*math.asin(1/(1+(radius+cfg['minimum_altitude_km'])*aa*aa/gm));theta=math.atan2(float(np.linalg.norm(np.cross(vi,vo))),float(np.dot(vi,vo)))
  if d<math.radians(cfg['minimum_bend_degrees']):return None,d
  if theta<=d:return abs(bb-aa),d
  return math.sqrt(aa*aa+bb*bb-2*aa*bb*math.cos(theta-d)),d
 earth=grav['EARTH'];v=np.array([5.,0.,0.]);zero,bd=bend(v,v,*earth);one,_=bend(v,v+np.array([1.,0.,0.]),*earth);assert zero==0 and one==1
 report={'classification':'TEST_ONLY_NONCANON','input_sha256':sha(P/'PR427_ASSIST_PILOT_INPUT_TEST_ONLY.json'),'table_manifest_sha256':sha(P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json'),'database_sha256':sha(db),'candidate_bodies':candidates,'excluded_candidates':excluded,'hand_tests':{'earth_max_bend_degrees_at_5_km_s':math.degrees(bd),'matched_speed_burn_km_s':zero,'one_km_s_speed_mismatch_burn_km_s':one},'pilot':[],'full_run_executed':False};progress=P/'PR427_ASSIST_2035_PILOT_PROGRESS_TEST_ONLY.jsonl';assert not progress.exists()
 directrows=list(csv.DictReader((P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv').open()));giants=json.loads((P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json').read_text())['body_years']
 for target in ['MARS','PLUTO','NEPTUNE']:
  for label,steps in ([('base',cfg['search_steps_days']),('half',cfg['halved_search_steps_days'])] if target=='MARS' else [('base',cfg['search_steps_days'])]):
   t=time.monotonic();count=0;solved=0;low=Counter();errors=Counter();best=None
   dates=[first+timedelta(days=d) for d in range(0,(datetime(2027,1,1,tzinfo=timezone.utc)-first).days,steps['departure'])]
   for assist in candidates:
    if assist==target:continue
    for dep in dates:
     for d1 in range(cfg['leg_days_min'],cfg['leg_days_max']+1,steps['assist_arrival']):
      mid=dep+timedelta(days=d1)
      for d2 in range(cfg['leg_days_min'],cfg['leg_days_max']+1,steps['target_arrival']):
       end=mid+timedelta(days=d2);count+=1
       try:vin,ain=leg('EARTH',assist,dep,mid);aout,vout=leg(assist,target,mid,end)
       except (ValueError,RuntimeError,ZeroDivisionError,OverflowError) as ex:errors[type(ex).__name__]+=1;continue
       solved+=1;burn,d=bend(ain,aout,*grav[assist]);
       if burn is None:low[assist]+=1;continue
       payload=float(a['payload_kg']);post,nassist=stage(burn,payload);gm,radius=earth;vinf=float(np.linalg.norm(vin));r=radius+float(a['parking_orbit_altitude_km']);departure=math.sqrt(vinf*vinf+2*gm/r)-math.sqrt(gm/r);mass,ndep=stage(departure,post);usd=mass*float(a['launch_cost_usd_per_kg_leo'])+float(a['fixed_mission_cost_usd'])
       item={'route':['EARTH',assist,target],'departure':dep.isoformat(),'assist_arrival':mid.isoformat(),'target_arrival':end.isoformat(),'leg_days':[d1,d2],'price_usd':usd,'assist_burn_km_s':burn,'max_bend_degrees':math.degrees(d),'arrival_vinf_km_s':float(np.linalg.norm(vout)),'departure_stages':ndep,'assist_stages':nassist,'mass_in_leo_kg':mass}
       if best is None or (usd,item['route'],item['departure'],item['assist_arrival'])<(best['price_usd'],best['route'],best['departure'],best['assist_arrival']):best=item
   dr=next((r for r in directrows if r['body']==target and r['year']=='2026'),None)
   if dr:direct=float(dr['vehicle_total_usd'])
   else:
    gr=next((r for r in giants if r['body']==target and r['year']==2026),None);assert gr is not None and gr['model_units'] is not None;direct=float(gr['model_units'])*1e9
   winner=best if best and best['price_usd']<direct else {'route':['EARTH',target],'price_usd':direct,'direct':True}
   row={'target':target,'search':label,'steps_days':steps,'trajectory_count':count,'solved_lambert_pairs':solved,'below_bend_by_candidate':dict(low),'lambert_failures':dict(errors),'best_assisted':best,'direct_price_usd':direct,'winning':winner,'elapsed_seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
   report['pilot'].append(row)
   with progress.open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
   print('PILOT',json.dumps(row,sort_keys=True),flush=True)
 report['elapsed_seconds']=time.monotonic()-start;report['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;report['estimated_full_63x2_seconds']=sum(x['elapsed_seconds'] for x in report['pilot'] if x['search']=='base')/3*126
 out=P/'PR427_ASSIST_2035_PILOT_REPORT_TEST_ONLY.json';assert not out.exists();out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('DONE',sha(out),report['elapsed_seconds'],report['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
