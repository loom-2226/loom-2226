"""Isolated first destination-state lattice slice; no travel pilot modifications."""
import hashlib,json,time,sys
from datetime import datetime,date,timedelta,timezone
from pathlib import Path
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.solar_reach_executor_spike import load,full_catalog,eligible_public_catalog
from simulation.offworld_mvp.build8.box2_lazy_proof.proof import asset_index,missing_assets,dates_for
from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso
P=Path(__file__).resolve().parent
C=json.loads((P/'first_lattice_slice_config.json').read_text());E=json.loads((P/'experiment.json').read_text());V=json.loads((P/C['validation_config']).read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def digest(p):return sha(p.read_bytes())
def iso_day(s):return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)
def main():
 start=time.monotonic();deadline=start+C['build_budget_seconds'];root=Path(E['asset_root']);out=Path('/home/ubuntu/LOOM-output/stage1_destination_lattice_first_slice');out.mkdir(exist_ok=True)
 data,_=load();cat=full_catalog(data);access=eligible_public_catalog(data,cat);assets,sources,cover=asset_index(root);t=OnDemandTravel(asset_root=root)
 epoch=f"{min(E['years'])}-{E['sampling']['start_month_day']}";excluded=C['survey_slow_exclusions'];bodies=sorted(r['body_id'] for r in cat if r['body_id']!=E['origin'] and r['body_class'] not in ('STAR','BARYCENTER','SPACECRAFT') and r['body_id'] in access and t.endpoint(r['body_id'],epoch)['status']=='DIRECT' and not missing_assets(r['body_id'],epoch,assets,sources,cover) and not missing_assets(E['origin'],epoch,assets,sources,cover) and r['body_id'] not in excluded)
 all_dep=[iso_day(x) for y in E['years'] for x in dates_for(y,E['sampling'])];step=C['lattice_step_days'];first=min(all_dep)+timedelta(days=E['sampling']['flight_range_days'][0]);last=max(all_dep)+timedelta(days=E['sampling']['flight_range_days'][1]);n=round((last-first).total_seconds()/(step*86400))+1
 ticks=np.arange(n,dtype=np.float64);utc0=(first-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds();utc=utc0+ticks*step*86400
 print('AUTHORED_CONFIG_SHA256',digest(P/'first_lattice_slice_config.json'),'VALIDATION_SHA256',digest(P/C['validation_config']),'EXCLUDED_SLOW',excluded,'BODIES',len(bodies),'LATTICE',_iso(first),_iso(last),'STEP_DAYS',step,'TICKS',n,flush=True)
 results={};
 for body in bodies:
  if time.monotonic()>=deadline:print('STOP_BUDGET',body,flush=True);break
  began=time.monotonic()
  try:
   src,cov=t.adapter.registry.source_for(body,_iso(first));end_src,end_cov=t.adapter.registry.source_for(body,_iso(last));assert src.sha256==end_src.sha256 and cov==end_cov and src.navigation_grade,'SOURCE_SEAM';t.adapter._load_source(src)
   target=str(t.adapter.registry.body_identifier(body).identifier_value)
   # UTC->ET conversion is numeric; no str2et or per-tick date-text parsing.
   et=utc+np.asarray([spice.deltet(float(x),'UTC') for x in utc],dtype=np.float64)
   t.adapter._require_source_object_coverage(src,int(target),float(et[0]));t.adapter._require_source_object_coverage(src,int(target),float(et[-1]))
   fetch=time.perf_counter();state,_=spice.spkezr(target,et,'ECLIPJ2000','NONE','10');arr=np.asarray(state,dtype=np.float64);fetch_seconds=time.perf_counter()-fetch;assert arr.shape==(n,6)
   required=set([0,n//2,n-1]);div=V['design_validation']['sample_divisor'];limit=V['design_validation']['maximum_sample_count'];required.update(range(0,n,max(1,(n-1)//div)));indices=sorted(required)
   if len(indices)>limit:indices=sorted(set([0,n//2,n-1]+[i for i in indices if i not in (0,n//2,n-1)][:limit-3]))
   maxpos=maxvel=maxcomponentpos=maxcomponentvel=0.
   for i in indices:
    direct,_=spice.spkezr(target,float(et[i]),'ECLIPJ2000','NONE','10');a=np.asarray(direct,dtype=np.float64);diff=np.abs(arr[i]-a);maxcomponentpos=max(maxcomponentpos,float(diff[:3].max()));maxcomponentvel=max(maxcomponentvel,float(diff[3:].max()));maxpos=max(maxpos,float(np.linalg.norm(diff[:3])));maxvel=max(maxvel,float(np.linalg.norm(diff[3:])));
    if not np.array_equal(arr[i].view(np.uint64),a.view(np.uint64)):raise ValueError('BITWISE_MISMATCH tick='+str(i)+' max='+str(diff.max()))
   if time.monotonic()>deadline:print('STOP_BUDGET_AFTER_VALIDATION',body,flush=True);break
   file=out/(body+'.npy');temp=out/(body+'.pending.npy');np.save(temp,arr);temp.replace(file)
   row={'status':'VALIDATED','states':n,'fetch_seconds':fetch_seconds,'elapsed_seconds':time.monotonic()-began,'source':src.ephemeris_source_id,'kernel_sha256':src.sha256,'table_sha256':digest(file),'sample_count':len(indices),'max_abs_position_component_km':maxcomponentpos,'max_abs_velocity_component_km_s':maxcomponentvel,'max_position_norm_km':maxpos,'max_velocity_norm_km_s':maxvel};results[body]=row;print('BUILT',body,json.dumps(row,sort_keys=True),flush=True)
  except Exception as ex:print('STOP_FAILURE',body,type(ex).__name__,str(ex),flush=True);break
 # Write only report metadata outside repository. Do not expose incomplete as ready.
 manifest={'config_sha256':digest(P/'first_lattice_slice_config.json'),'validation_config_sha256':digest(P/C['validation_config']),'first':_iso(first),'last':_iso(last),'step_days':step,'excluded_slow':excluded,'eligible_bodies':bodies,'built':results,'complete':len(results)==len(bodies),'elapsed_seconds':time.monotonic()-start};mp=out/'slice_manifest.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');print('MANIFEST',mp,'SHA256',digest(mp),'COMPLETE',manifest['complete'],'TOTAL_SECONDS',manifest['elapsed_seconds'],flush=True)
 if not manifest['complete']:return 2
 # Compare same AMUN departure, using isolated instance override only.
 body=bodies[0];day=dates_for(min(E['years']),E['sampling'])[0];raw=OnDemandTravel(asset_root=root);cached=OnDemandTravel(asset_root=root);table=np.load(out/(body+'.npy'),mmap_mode='r');original=cached._batch_states
 def from_table(b,epochs):
  if b!=body:return original(b,epochs)
  ids=[round((x-first).total_seconds()/(step*86400)) for x in epochs]
  if any(i<0 or i>=n or abs((epochs[j]-first).total_seconds()-i*step*86400)>1e-6 for j,i in enumerate(ids)):raise ValueError('OFF_LATTICE')
  src,cov=cached.adapter.registry.source_for(b,_iso(epochs[0]));return np.asarray(table[ids]),src,cov
 cached._batch_states=from_table
 kw={'strategy':E['sampling']['strategy'],'flight_range_days':E['sampling']['flight_range_days']};st=time.perf_counter();direct=raw.geometry(E['origin'],body,day,**kw);direct_s=time.perf_counter()-st;st=time.perf_counter();reuse=cached.geometry(E['origin'],body,day,**kw);reuse_s=time.perf_counter()-st;equal=direct==reuse;print('COMPARE',json.dumps({'body':body,'departure':day,'direct_seconds':direct_s,'table_seconds':reuse_s,'geometry_equal':equal,'samples':direct['sampled_solutions']}),flush=True)
 return 0 if equal else 3
if __name__=='__main__':sys.exit(main())
