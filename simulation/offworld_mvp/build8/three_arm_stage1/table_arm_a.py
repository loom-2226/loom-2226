"""Isolated, checkpointed table-only Arm A; gate must pass before execution."""
import hashlib,json,os,time,sys,resource,gc
from datetime import date,timedelta,datetime,timezone
from spiceypy import str2et
import numpy as np
from pathlib import Path
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1 import run as base
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel,digest
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import dates_for,asset_index,missing_assets
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;C=json.loads((P/'table_arm_a_config.json').read_text());E=json.loads((P/'experiment.json').read_text());OUT=Path(C['output_root']);OUT.mkdir(parents=True,exist_ok=True)
def write(p,x):
 tmp=p.with_suffix('.pending.json');tmp.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n');os.replace(tmp,p)
def even(n,k):return [(i*(n-1))//(k-1) for i in range(k)]
def assess(g):
 rows=g['trajectories'];dl=D(E['departure_limit_km_s']);al=D(E['arrival_limit_km_s']);rate=D(E['price_rate_usd_millions_per_km_s']);lo=D(str(E['sampling']['flight_range_days'][0]));hi=D(str(E['sampling']['flight_range_days'][1]));
 def speeds(r):return D(str(r['departure_vinf_km_s'])),D(str(r['arrival_vinf_km_s']))
 admissible=[r for r in rows if all((lo<=D(str(r['flight_days']))<=hi,speeds(r)[0]<=dl,speeds(r)[1]<=al))]
 best=min(admissible,key=lambda r:(rate*sum(speeds(r)),D(str(r['flight_days'])))) if admissible else None
 lowest=min(rows,key=lambda r:(sum(speeds(r)),D(str(r['flight_days'])))) if rows else None
 reason=None
 if best is None:
  if lowest is None:reason='OTHER_NO_RETAINED_TRAJECTORIES'
  else:
   dep,arr=speeds(lowest);fd=D(str(lowest['flight_days']))
   reason='FLIGHT_RANGE_EDGE' if fd<=lo or fd>=hi else 'DEPARTURE_SPEED_LIMIT' if dep>dl else 'ARRIVAL_SPEED_LIMIT' if arr>al else 'OTHER_LOWEST_SPEED_ADMISSIBLE_BUT_NO_PRICE'
 return {'price':str(rate*sum(speeds(best))) if best else None,'best_flight_days':best['flight_days'] if best else None,'lowest_combined_speed_km_s':str(sum(speeds(lowest))) if lowest else None,'lowest_speed_flight_days':lowest['flight_days'] if lowest else None,'rejection_reason':reason}
def refinement_dates(coarse,rows):
 if not E['sampling']['daily_refinement'] or not all(d in rows for d in coarse):return []
 flags=[rows[d]['price'] is not None for d in coarse]
 brackets=[(a,b) for a,b,fa,fb in zip(coarse,coarse[1:],flags,flags[1:]) if fa!=fb]
 dates=[]
 for left,right in brackets[:E['sampling']['max_transition_brackets_per_body_year']]:
  d=date.fromisoformat(left)+timedelta(days=E['sampling']['refinement_step_days'])
  while d<date.fromisoformat(right):dates.append(d.isoformat());d+=timedelta(days=E['sampling']['refinement_step_days'])
 return dates
def rss_bytes():
 return int(Path('/proc/self/status').read_text().split('VmRSS:')[1].split('kB')[0].strip())*1024
def enforce(stage,peak):
 current=rss_bytes();peak=max(peak,current)
 if peak>C['process_memory_limit_gib']*1024**3:
  write(OUT/(stage+'_memory_stop.json'),{'status':'MEMORY_LIMIT','stage':stage,'peak_rss_bytes':peak,'limit_gib':C['process_memory_limit_gib']})
  print('STOP_MEMORY_LIMIT',stage,peak,flush=True);return peak,False
 return peak,True
def clear_memos(table,direct):
 for obj in (table.travel,direct):
  obj._geometry.clear();obj._state_cache.clear()
 gc.collect()
def main(*,preflight_only=False):
 begin=time.monotonic();gate_deadline=begin+C['gate_limit_seconds'];manifest=P/C['table_manifest_file'];assert digest(manifest)==C['table_manifest_sha256'],'MANIFEST_HASH_MISMATCH';table=TableTravel(E['asset_root'],manifest);direct=OnDemandTravel(asset_root=Path(E['asset_root']));m=table.manifest;data,_=base.load();cat=base.full_catalog(data);access=base.eligible_public_catalog(data,cat);assets,sources,cover=asset_index(Path(E['asset_root']));eligible={}
 for y in E['years']:
  day=f"{y}-{E['sampling']['start_month_day']}";eligible[y]=sorted(r['body_id'] for r in cat if r['body_id']!=E['origin'] and r['body_class'] not in ('STAR','BARYCENTER','SPACECRAFT') and r['body_id'] in access and table.travel.endpoint(r['body_id'],day)['status']=='DIRECT' and not missing_assets(r['body_id'],day,assets,sources,cover) and not missing_assets(E['origin'],day,assets,sources,cover))
 assert all(b in m['tables'] for bs in eligible.values() for b in bs),'ELIGIBLE_TABLE_MISSING'
 ident={'experiment_sha256':digest(P/'experiment.json'),'config_sha256':digest(P/'table_arm_a_config.json'),'table_manifest_sha256':digest(manifest),'table_source':C['state_source']};identity=hashlib.sha256(json.dumps(ident,sort_keys=True).encode()).hexdigest();print('RUN_IDENTITY',identity,'TABLE_MANIFEST_SHA256',digest(manifest),'CONFIG_SHA256',digest(P/'table_arm_a_config.json'),flush=True)
 # Survey controls SLOW classification; measured checkpoint controls SLOW cost.
 survey=json.loads((P/C['survey_output_file']).read_text());assert digest(P/C['survey_output_file'])==C['survey_output_sha256'],'SURVEY_HASH_MISMATCH'
 timing_file=P/C['checkpoint_timing_source_file'];assert digest(timing_file)==C['checkpoint_timing_source_sha256'],'TIMING_SOURCE_HASH_MISMATCH'
 timing=json.loads(timing_file.read_text());bodies=sorted(set.union(*(set(v) for v in eligible.values())))
 nflight=round((E['sampling']['flight_range_days'][1]-E['sampling']['flight_range_days'][0])/E['sampling']['flight_step_days'])+1
 estimates={};counts={};estimate_sources={}
 for b in bodies:
  slow=survey['status_by_body'][b]=='SLOW';count=C['comparison_departures_per_slow_body'] if slow else C['comparison_departures_per_body'];counts[b]=count
  if slow:
   samples=[float(row['seconds']) for key,entry in timing['completed'].items() if key.split('|',1)[1]==b for row in entry['dates'].values() if 'seconds' in row]
   if not samples:raise ValueError('NO_MEASURED_SLOW_TIMING:'+b)
   # Conservative observed maximum rather than inventing a warm-body rate.
   estimates[b]=max(samples)*count;estimate_sources[b]='A_CHECKPOINT_MAX_OBSERVED_DEPARTURE_SECONDS'
  else:
   measurements=survey['measurements'][b].get('times',{})
   if '100' not in measurements:raise ValueError('NO_MEASURED_SURVEY_RATE:'+b)
   estimates[b]=float(measurements['100'])/100*nflight*count;estimate_sources[b]='MEASURED_SURVEY_100_STATE_RATE_EXTRAPOLATION'
 total_estimate=sum(estimates.values());print('GATE_ESTIMATES',json.dumps({'seconds_by_body':estimates,'total_seconds':total_estimate,'counts':counts,'sources':estimate_sources,'timing_source':str(timing_file),'timing_source_sha256':digest(timing_file),'limit_seconds':C['gate_limit_seconds']},sort_keys=True),flush=True)
 gate_metadata={'identity':identity,'table_manifest_sha256':digest(manifest),'timing_source':str(timing_file),'timing_source_sha256':digest(timing_file),'survey_sha256':digest(P/C['survey_output_file']),'estimate_seconds_by_body':estimates,'estimate_sources':estimate_sources,'total_estimate_seconds':total_estimate,'comparison_counts':counts,'gate_limit_seconds':C['gate_limit_seconds']}
 if total_estimate>C['gate_limit_seconds']:
  write(OUT/'gate.json',{'status':'NOT_RUN_TOTAL_ESTIMATED_OVER_BUDGET',**gate_metadata});print('STOP_GATE_TOTAL_ESTIMATE_OVER_LIMIT',total_estimate,flush=True);return 4
 # Exact-time preflight: builder and direct path must use identical ET bits at every tick.
 from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso
 first=datetime.fromisoformat(m['first'].replace('Z','+00:00'));last=datetime.fromisoformat(m['last'].replace('Z','+00:00'));step=m['step_days']*86400
 n=round((last-first).total_seconds()/step)+1
 epochs=[first+timedelta(seconds=i*step) for i in range(n)]
 source,_=direct.adapter.registry.source_for(bodies[0],_iso(epochs[0]))
 direct.adapter._load_source(source)
 direct_times=np.asarray(str2et([_iso(x) for x in epochs]),dtype=np.float64)
 builder_time_path=table.root/'builder_et.npy';assert digest(builder_time_path)==m['builder_et_sha256'],'BUILDER_ET_HASH_MISMATCH'
 builder_times=np.load(builder_time_path)
 assert len(builder_times)==n,'BUILDER_ET_TICK_COUNT_MISMATCH'
 time_preflight={}
 for body in bodies:
  if len(np.load(table.root/(body+'.npy'),mmap_mode='r'))!=n:raise ValueError('TABLE_TICK_COUNT_MISMATCH:'+body)
  mismatches=int(np.count_nonzero(builder_times.view(np.uint64)!=direct_times.view(np.uint64)))
  time_preflight[body]={'ticks':n,'different_et_bits':mismatches}
  if mismatches:write(OUT/'time_preflight.json',{'status':'MISMATCH','per_body':time_preflight,'identity':identity});print('STOP_TIME_PREFLIGHT',body,flush=True);return 5
 write(OUT/'time_preflight.json',{'status':'PASS','per_body':time_preflight,'identity':identity,'table_manifest_sha256':digest(manifest)})
 print('TIME_PREFLIGHT_PASS',len(bodies),'TABLES',n,'TICKS_EACH',flush=True)
 if preflight_only:return 0
 # Persist every comparison; only an identical identity can resume.
 gate_file=OUT/'gate_comparisons.jsonl';records={};peak_gate=0
 if gate_file.exists():
  for line in gate_file.read_text().splitlines():
   row=json.loads(line)
   if row['identity']==identity and row['equal']:
    records[(row['body'],row['day'])]=row
 # Preflight samples all calendar departure dates in authored years.
 for body in bodies:
  days=[date(y,1,1)+timedelta(days=i) for y in E['years'] for i in range((date(y+1,1,1)-date(y,1,1)).days)]
  chosen=[days[i].isoformat() for i in even(len(days),counts[body])]
  for day in chosen:
   if (body,day) in records:continue
   if time.monotonic()>=gate_deadline:
    write(OUT/'gate.json',{'status':'TIME_LIMIT',**gate_metadata,'completed_count':len(records),'peak_rss_bytes':peak_gate});return 2
   kw={'strategy':E['sampling']['strategy'],'flight_range_days':E['sampling']['flight_range_days']}
   st=time.monotonic();g1=direct.geometry(E['origin'],body,day,**kw);direct_s=time.monotonic()-st
   a=base.digest(g1);del g1
   g2=table.geometry(E['origin'],body,day,**kw);b=base.digest(g2);del g2
   peak_gate=max(peak_gate,rss_bytes());clear_memos(table,direct)
   row={'identity':identity,'body':body,'day':day,'direct_seconds':direct_s,'geometry_sha256':a,'table_geometry_sha256':b,'equal':a==b,'rss_bytes':peak_gate}
   with gate_file.open('a') as h:
    h.write(json.dumps(row,sort_keys=True)+'\n');h.flush();os.fsync(h.fileno())
   records[(body,day)]=row
   print('GATE',body,day,'DIRECT_SECONDS',round(direct_s,3),'MATCH',a==b,'PEAK_RSS',peak_gate,flush=True)
   if a!=b:
    write(OUT/'gate.json',{'status':'MISMATCH',**gate_metadata,'failed':row,'completed_count':len(records),'peak_rss_bytes':peak_gate});return 3
   peak_gate,ok=enforce('gate',peak_gate)
   if not ok:return 6
 gate_summary={body:{'matches':sum(x['equal'] for (bb,_),x in records.items() if bb==body),'mismatches':sum(not x['equal'] for (bb,_),x in records.items() if bb==body),'seconds':sum(x['direct_seconds'] for (bb,_),x in records.items() if bb==body)} for body in bodies}
 write(OUT/'gate.json',{'status':'PASS',**gate_metadata,'per_body':gate_summary,'completed_count':len(records),'peak_rss_bytes':peak_gate})
 print('GATE_PASS_PER_BODY',json.dumps(gate_summary,sort_keys=True),'PEAK_RSS',peak_gate,flush=True)
 run_begin=time.monotonic();run_deadline=run_begin+C['run_limit_seconds'];peak_arm=0
 # Gate must finish before any Arm A checkpoint.
 checkpoint=OUT/'A_CHECKPOINT.json';progress=OUT/'A_PROGRESS.json';state={'identity':identity,'completed':{}}
 if checkpoint.exists():state=json.loads(checkpoint.read_text());assert state['identity']==identity,'CHECKPOINT_IDENTITY_MISMATCH'
 for year in E['years']:
  for body in eligible[year]:
   key=f'{year}|{body}';entry=state['completed'].get(key,{'dates':{}});coarse=dates_for(year,E['sampling']);dates=list(coarse)
   # Fresh runs must complete coarse dates before computing transition brackets.
   for phase in ('coarse','refinement'):
    dates=coarse if phase=='coarse' else refinement_dates(coarse,entry['dates'])
    for day in dates:
     if day in entry['dates']:continue
     if time.monotonic()>=run_deadline:write(progress,{'status':'TIME_LIMIT','identity':identity,'completed':len(state['completed'])});return 2
     st=time.monotonic();g=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days']);row={**assess(g),'geometry_sha256':base.digest(g),'seconds':time.monotonic()-st,'sampled_solutions':g['sampled_solutions']};entry['dates'][day]=row;state['completed'][key]=entry;write(checkpoint,state);del g;clear_memos(table,direct);peak_arm,ok=enforce('arm_a',peak_arm)
     if not ok:return 6
     write(progress,{'status':'RUNNING','identity':identity,'body':body,'year':year,'departure':day,'completed_departures':sum(len(v['dates']) for v in state['completed'].values())})
 report={'identity':identity,'table_manifest_sha256':digest(manifest),'config_sha256':digest(P/'table_arm_a_config.json'),'elapsed_seconds':time.monotonic()-run_begin,'peak_rss_bytes':peak_arm,'gate_peak_rss_bytes':peak_gate,'gate_elapsed_seconds':run_begin-begin,'departures':sum(len(v['dates']) for v in state['completed'].values()),'body_years':{k:{'departures':len(v['dates']),'feasible':any(r['price'] is not None for r in v['dates'].values()),'lowest_price_usd_millions':min((D(r['price']) for r in v['dates'].values() if r['price'] is not None),default=None)} for k,v in state['completed'].items()}}
 report['body_years']={k:{**v,'lowest_price_usd_millions':str(v['lowest_price_usd_millions']) if v['lowest_price_usd_millions'] is not None else None} for k,v in report['body_years'].items()};report['seconds_per_departure']=report['elapsed_seconds']/report['departures'] if report['departures'] else None;write(OUT/'A_REPORT.json',report);write(progress,{'status':'COMPLETE','identity':identity,'completed_departures':report['departures']});print('A_COMPLETE',json.dumps(report,sort_keys=True),flush=True);return 0
if __name__=='__main__':sys.exit(main(preflight_only='--preflight-only' in sys.argv[1:]))
