"""Checkpointed Stage 1 PR426 departure policy; noncanon experiment only."""
import json,hashlib,time,os,sys
from pathlib import Path
from datetime import date,timedelta
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1 import run as base
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import dates_for
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).parent
C=json.loads((P/'experiment.json').read_text());CH=base.hfile(P/'experiment.json')
START=time.monotonic()
def write(path,obj):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,sort_keys=True,indent=2,default=str)+'\n');os.replace(tmp,path)
def price(geo):
 rows=OnDemandTravel.admissible(geo,departure_limit=float(C['departure_limit_km_s']),arrival_limit=float(C['arrival_limit_km_s']))
 if not rows:return None
 p=min(D(C['price_rate_usd_millions_per_km_s'])*(D(str(x['departure_vinf_km_s']))+D(str(x['arrival_vinf_km_s']))) for x in rows)
 return {'status':'PRICED','usd_millions':str(p),'usd':str(p*D('1000000')),'route1_units':str(p/D(C['route1_unit_usd_millions']))}
def run():
 data,cast_sha=base.load();catalog=base.full_catalog(data);access=base.eligible_public_catalog(data,catalog)
 t=OnDemandTravel(asset_root=Path(C['asset_root']));eligible={}
 for year in C['years']:
  eligible[year]=[r['body_id'] for r in catalog if r['body_id']!=C['origin'] and r['body_class'] not in ('STAR','BARYCENTER','SPACECRAFT') and r['body_id'] in access and t.endpoint(r['body_id'],f'{year}-01-01')['status']=='DIRECT']
 checkpoint=P/'A_CHECKPOINT.json';progress=P/'PROGRESS.json';table=P/'A_TABLE.json';state={'authored_sha256':CH,'completed':{},'started_unix':time.time()}
 if checkpoint.exists():
  state=json.loads(checkpoint.read_text());assert state['authored_sha256']==CH,'CHECKPOINT_AUTHORED_MISMATCH'
 total=sum(len(v) for v in eligible.values());print('PRELAUNCH A body-years',total,'coarse',total*14,'max',total*41,'seconds_estimate',total*41*float(C['estimate_seconds_per_geometry']),flush=True)
 for year in C['years']:
  for body in eligible[year]:
   key=f'{year}|{body}';entry=state['completed'].get(key,{'dates':{},'refinement_done':False});coarse=dates_for(year,C['sampling']);dates=list(coarse)
   if all(d in entry['dates'] for d in coarse):
    flags=[bool(entry['dates'][d].get('price')) for d in coarse];trans=[(a,b) for a,b,fa,fb in zip(coarse,coarse[1:],flags,flags[1:]) if fa!=fb]
    if trans:
     left,right=trans[0];d=date.fromisoformat(left)+timedelta(days=1)
     while d<date.fromisoformat(right):dates.append(d.isoformat());d+=timedelta(days=1)
   for day in dates:
    if day in entry['dates']:continue
    if time.monotonic()-START>int(C['hard_stop_seconds']):write(progress,{'status':'TIME_LIMIT','completed_body_years':len(state['completed']),'total_body_years':total,'authored_sha256':CH});return
    st=time.monotonic()
    try:
     g=t.geometry(C['origin'],body,day,strategy=C['sampling']['strategy'],flight_range_days=C['sampling']['flight_range_days']);q=price(g);row={'price':q,'geometry_sha256':base.digest(g),'sampled_solutions':g['sampled_solutions'],'status':'PRICED' if q else 'INFEASIBLE_SAMPLED'}
    except Exception as e:row={'status':'UNSUPPORTED','reason':type(e).__name__+':'+str(e),'price':None}
    row['seconds']=time.monotonic()-st;entry['dates'][day]=row;state['completed'][key]=entry;write(checkpoint,state)
    write(progress,{'status':'RUNNING','year':year,'body':body,'departure':day,'completed_departures':sum(len(v['dates']) for v in state['completed'].values()),'completed_body_years':sum(all(d in v['dates'] for d in dates_for(int(k.split('|')[0]),C['sampling'])) for k,v in state['completed'].items()),'total_body_years':total,'elapsed_seconds':time.monotonic()-START,'internal_solves':t.solve_count,'authored_sha256':CH})
   entry['refinement_done']=True;state['completed'][key]=entry;write(checkpoint,state)
 write(table,{'authored_sha256':CH,'source':'A_EXHAUSTIVE','completed':state['completed']});write(progress,{'status':'A_COMPLETE','table_sha256':base.hfile(table),'elapsed_seconds':time.monotonic()-START,'internal_solves':t.solve_count,'body_years':total,'authored_sha256':CH});print('A COMPLETE',base.hfile(table),flush=True)
if __name__=='__main__':run()
