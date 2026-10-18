"""Isolated, checkpointed table-only Arm A; gate must pass before execution."""
import hashlib,json,os,time,sys
from datetime import date,timedelta,datetime,timezone
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
def price(g):
 rows=OnDemandTravel.admissible(g,departure_limit=float(E['departure_limit_km_s']),arrival_limit=float(E['arrival_limit_km_s']))
 if not rows:return None
 p=min(D(E['price_rate_usd_millions_per_km_s'])*(D(str(x['departure_vinf_km_s']))+D(str(x['arrival_vinf_km_s']))) for x in rows)
 return str(p)
def main():
 begin=time.monotonic();deadline=begin+C['hard_limit_seconds'];manifest=P/C['table_manifest_file'];assert digest(manifest)==C['table_manifest_sha256'],'MANIFEST_HASH_MISMATCH';table=TableTravel(E['asset_root'],manifest);direct=OnDemandTravel(asset_root=Path(E['asset_root']));m=table.manifest;data,_=base.load();cat=base.full_catalog(data);access=base.eligible_public_catalog(data,cat);assets,sources,cover=asset_index(Path(E['asset_root']));eligible={}
 for y in E['years']:
  day=f"{y}-{E['sampling']['start_month_day']}";eligible[y]=sorted(r['body_id'] for r in cat if r['body_id']!=E['origin'] and r['body_class'] not in ('STAR','BARYCENTER','SPACECRAFT') and r['body_id'] in access and table.travel.endpoint(r['body_id'],day)['status']=='DIRECT' and not missing_assets(r['body_id'],day,assets,sources,cover) and not missing_assets(E['origin'],day,assets,sources,cover))
 assert all(b in m['tables'] for bs in eligible.values() for b in bs),'ELIGIBLE_TABLE_MISSING'
 ident={'experiment_sha256':digest(P/'experiment.json'),'config_sha256':digest(P/'table_arm_a_config.json'),'table_manifest_sha256':digest(manifest),'table_source':C['state_source']};identity=hashlib.sha256(json.dumps(ident,sort_keys=True).encode()).hexdigest();print('RUN_IDENTITY',identity,'TABLE_MANIFEST_SHA256',digest(manifest),'CONFIG_SHA256',digest(P/'table_arm_a_config.json'),flush=True)
 # Preflight budget gate: an observed SLOW body may make 50 independent direct
 # geometry fetches impossible within the authorized full-process limit.
 survey=json.loads((P/C['survey_output_file']).read_text());assert digest(P/C['survey_output_file'])==C['survey_output_sha256'],'SURVEY_HASH_MISMATCH'
 nflight=round((E['sampling']['flight_range_days'][1]-E['sampling']['flight_range_days'][0])/E['sampling']['flight_step_days'])+1
 estimates={}
 for b in sorted(set.union(*(set(v) for v in eligible.values()))):
  measurements=survey['measurements'][b].get('times',{})
  if '100' in measurements:
   estimates[b]=float(measurements['100'])/100*nflight*C['comparison_departures_per_body']
 # This is only an estimate, not a measured gate runtime. Stop conservatively
 # rather than start an authorized 60-minute run known to be infeasible.
 if any(survey['status_by_body'][b]=='SLOW' for b in estimates) or any(x>C['hard_limit_seconds'] for x in estimates.values()):
  write(OUT/'gate.json',{'status':'NOT_RUN_ESTIMATED_OVER_BUDGET','identity':identity,'estimate_seconds_by_body':estimates,'survey_slow_bodies':[b for b in estimates if survey['status_by_body'][b]=='SLOW'],'limit_seconds':C['hard_limit_seconds'],'table_manifest_sha256':digest(manifest)})
  print('STOP_PREFLIGHT_SLOW_DIRECT_PATH',json.dumps([b for b in estimates if survey['status_by_body'][b]=='SLOW']),flush=True)
  return 4
 # Preflight samples all calendar departure dates in authored years; independent of adaptive refinement.
 checks=[]
 for body in sorted(set.union(*(set(v) for v in eligible.values()))):
  days=[date(y,1,1)+timedelta(days=i) for y in E['years'] for i in range((date(y+1,1,1)-date(y,1,1)).days)];chosen=[days[i].isoformat() for i in even(len(days),C['comparison_departures_per_body'])]
  for day in chosen:
   if time.monotonic()>=deadline:write(OUT/'gate.json',{'status':'TIME_LIMIT','identity':identity,'completed':checks});print('STOP_GATE_TIME_LIMIT',body,day,flush=True);return 2
   kw={'strategy':E['sampling']['strategy'],'flight_range_days':E['sampling']['flight_range_days']};st=time.monotonic();g1=direct.geometry(E['origin'],body,day,**kw);direct_s=time.monotonic()-st
   g2=table.geometry(E['origin'],body,day,**kw);a=base.digest(g1);b=base.digest(g2);checks.append({'body':body,'day':day,'direct_seconds':direct_s,'geometry_sha256':a,'equal':a==b});print('GATE',body,day,'DIRECT_SECONDS',round(direct_s,3),'MATCH',a==b,flush=True)
   if a!=b:write(OUT/'gate.json',{'status':'MISMATCH','identity':identity,'completed':checks});return 3
 write(OUT/'gate.json',{'status':'PASS','identity':identity,'completed':checks})
 # Gate must finish before any Arm A checkpoint.
 checkpoint=OUT/'A_CHECKPOINT.json';progress=OUT/'A_PROGRESS.json';state={'identity':identity,'completed':{}}
 if checkpoint.exists():state=json.loads(checkpoint.read_text());assert state['identity']==identity,'CHECKPOINT_IDENTITY_MISMATCH'
 for year in E['years']:
  for body in eligible[year]:
   key=f'{year}|{body}';entry=state['completed'].get(key,{'dates':{}});coarse=dates_for(year,E['sampling']);dates=list(coarse)
   if all(d in entry['dates'] for d in coarse):
    flags=[entry['dates'][d]['price'] is not None for d in coarse];trans=[(a,b) for a,b,fa,fb in zip(coarse,coarse[1:],flags,flags[1:]) if fa!=fb]
    if trans:
     left,right=trans[0];d=date.fromisoformat(left)+timedelta(days=1)
     while d<date.fromisoformat(right):dates.append(d.isoformat());d+=timedelta(days=1)
   for day in dates:
    if day in entry['dates']:continue
    if time.monotonic()>=deadline:write(progress,{'status':'TIME_LIMIT','identity':identity,'completed':len(state['completed'])});return 2
    st=time.monotonic();g=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days']);row={'price':price(g),'geometry_sha256':base.digest(g),'seconds':time.monotonic()-st,'sampled_solutions':g['sampled_solutions']};entry['dates'][day]=row;state['completed'][key]=entry;write(checkpoint,state);write(progress,{'status':'RUNNING','identity':identity,'body':body,'year':year,'departure':day,'completed_departures':sum(len(v['dates']) for v in state['completed'].values())})
 report={'identity':identity,'table_manifest_sha256':digest(manifest),'config_sha256':digest(P/'table_arm_a_config.json'),'elapsed_seconds':time.monotonic()-begin,'departures':sum(len(v['dates']) for v in state['completed'].values()),'body_years':{k:{'departures':len(v['dates']),'feasible':any(r['price'] is not None for r in v['dates'].values()),'lowest_price_usd_millions':min((D(r['price']) for r in v['dates'].values() if r['price'] is not None),default=None)} for k,v in state['completed'].items()}}
 report['body_years']={k:{**v,'lowest_price_usd_millions':str(v['lowest_price_usd_millions']) if v['lowest_price_usd_millions'] is not None else None} for k,v in report['body_years'].items()};report['seconds_per_departure']=report['elapsed_seconds']/report['departures'] if report['departures'] else None;write(OUT/'A_REPORT.json',report);print('A_COMPLETE',json.dumps(report,sort_keys=True),flush=True);return 0
if __name__=='__main__':sys.exit(main())
