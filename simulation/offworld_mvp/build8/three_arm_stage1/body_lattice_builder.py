"""Offline body-blind chunk build and direct SPICE validation, never runtime-wired."""
import argparse,hashlib,json,os,time,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso
P=Path(__file__).resolve().parent
C=json.loads((P/'next_lattice_slice_config.json').read_text());B=json.loads((P/C['lattice_source_config']).read_text());E=json.loads((P/'experiment.json').read_text());REFERENCE=Path(C['output_root']);OUT=Path(C['rebuild_output_root']);OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic_json(p,x):
 temp=p.with_suffix('.pending.json');temp.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n');temp.replace(p)
def indices(n,k):
 assert k>=3 and n>=k
 a=sorted({(i*(n-1))//(k-1) for i in range(k)}|{0,n//2,n-1})
 # Preserve first/middle/last, fill remaining by uniform deterministic rank.
 if len(a)>k:
  mandatory={0,n//2,n-1};pool=[v for v in a if v not in mandatory];keep=k-len(mandatory);a=sorted(mandatory|{pool[(j*(len(pool)-1))//(keep-1)] for j in range(keep)})
 assert len(a)==k
 return a
def validate(body,array,et,target,k):
 maximum=np.zeros(6);pmax=vmax=0.
 for ix in indices(len(array),k):
  direct,_=spice.spkezr(target,float(et[ix]),'ECLIPJ2000','NONE','10');d=np.asarray(direct,dtype=np.float64);delta=np.abs(array[ix]-d);maximum=np.maximum(maximum,delta);pmax=max(pmax,float(np.linalg.norm(delta[:3])));vmax=max(vmax,float(np.linalg.norm(delta[3:])))
  if not np.array_equal(array[ix].view(np.uint64),d.view(np.uint64)):
   raise RuntimeError(f'BITWISE_MISMATCH body={body} tick={ix} components={delta.tolist()}')
 return {'samples':k,'max_position_component_km':float(maximum[:3].max()),'max_velocity_component_km_s':float(maximum[3:].max()),'max_position_norm_km':pmax,'max_velocity_norm_km_s':vmax}
def main(body):
 survey_path=P/C['survey_output_file'];assert sha(survey_path)==C['survey_output_sha256'],'SURVEY_HASH_MISMATCH';survey=json.loads(survey_path.read_text());assert body in survey['status_by_body'],'BODY_NOT_IN_SURVEY'
 begin=time.monotonic();deadline=begin+C['build_budget_seconds'];manifest=json.loads((REFERENCE/'slice_manifest.json').read_text());n=round((datetime.fromisoformat(manifest['last'].replace('Z','+00:00'))-datetime.fromisoformat(manifest['first'].replace('Z','+00:00'))).total_seconds()/(B['lattice_step_days']*86400))+1;first=datetime.fromisoformat(manifest['first'].replace('Z','+00:00'));utc0=(first-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds();ticks=np.arange(n,dtype=np.float64);utc=utc0+ticks*B['lattice_step_days']*86400
 t=OnDemandTravel(asset_root=Path(E['asset_root']));print('CONFIG',json.dumps(C,sort_keys=True),'CONFIG_SHA256',sha(P/'next_lattice_slice_config.json'),'WINDOW',manifest['first'],manifest['last'],'TICKS',n,flush=True)
 results={};src,cov=t.adapter.registry.source_for(body,manifest['first']);end_src,end_cov=t.adapter.registry.source_for(body,manifest['last']);assert src.sha256==end_src.sha256 and cov==end_cov and src.navigation_grade,'SOURCE_SEAM';t.adapter._load_source(src);target=str(t.adapter.registry.body_identifier(body).identifier_value);et=utc+np.asarray([spice.deltet(float(x),'UTC') for x in utc],dtype=np.float64);t.adapter._require_source_object_coverage(src,int(target),float(et[0]));t.adapter._require_source_object_coverage(src,int(target),float(et[-1]));folder=OUT/(body+'_chunks');folder.mkdir(exist_ok=True);progress=folder/'progress.json';identity={'config_sha256':sha(P/'next_lattice_slice_config.json'),'survey_sha256':C['survey_output_sha256'],'source_sha256':src.sha256,'first':manifest['first'],'last':manifest['last'],'n':n,'chunk_ticks':C['chunk_ticks']};saved=json.loads(progress.read_text()) if progress.exists() else {'identity':identity,'chunks':{}};assert saved['identity']==identity,'CHECKPOINT_IDENTITY_MISMATCH';size=C['chunk_ticks']
 for lo in range(0,n,size):
  hi=min(n,lo+size);key=f'{lo:06d}_{hi:06d}';file=folder/(key+'.npy')
  if key in saved['chunks']:
   assert file.exists() and sha(file)==saved['chunks'][key]['sha256'],'CHECKPOINT_HASH_MISMATCH';print('RESUMED',key,flush=True);continue
  if time.monotonic()>=deadline:print('STOP_BUDGET_BEFORE_CHUNK',key,flush=True);return 2
  st=time.perf_counter();states,_=spice.spkezr(target,et[lo:hi],'ECLIPJ2000','NONE','10');arr=np.asarray(states,dtype=np.float64);assert arr.shape==(hi-lo,6);tmp=folder/(key+'.pending.npy');np.save(tmp,arr);tmp.replace(file);saved['chunks'][key]={'sha256':sha(file),'seconds':time.perf_counter()-st,'count':hi-lo};atomic_json(progress,saved);print('CHUNK',key,'seconds',round(saved['chunks'][key]['seconds'],4),'elapsed',round(time.monotonic()-begin,2),flush=True)
 if time.monotonic()>=deadline:print('STOP_BUDGET_BEFORE_VALIDATION',flush=True);return 2
 a=np.concatenate([np.load(folder/(f'{lo:06d}_{min(n,lo+size):06d}.npy')) for lo in range(0,n,size)]);assert a.shape==(n,6);v=validate(body,a,et,target,C['validation_sample_count_per_table']);print('VALIDATED',body,v,flush=True)
 if time.monotonic()>=deadline:print('STOP_BUDGET_BEFORE_PUBLISH',flush=True);return 2
 tmp=OUT/(body+'.pending.npy');np.save(tmp,a);tmp.replace(OUT/(body+'.npy'));results[body]={'validation':v,'sha256':sha(OUT/(body+'.npy')),'source_sha256':src.sha256,'chunk_count':len(saved['chunks'])};reference=REFERENCE/(body+'.npy');assert reference.exists(),'REFERENCE_MISSING';reference_hash=sha(reference);assert reference_hash==results[body]['sha256'],'REBUILT_TABLE_HASH_MISMATCH';results[body]['reference_sha256']=reference_hash;print('REBUILT_MATCH',body,results[body],flush=True)
 report={'config_sha256':sha(P/'next_lattice_slice_config.json'),'results':results,'elapsed_seconds':time.monotonic()-begin,'complete':len(results)==1};atomic_json(OUT/(body+'_generic_validation.json'),report);print('REPORT_SHA256',sha(OUT/(body+'_generic_validation.json')),'TOTAL_SECONDS',report['elapsed_seconds'],'COMPLETE',report['complete'],flush=True)
 return 0 if report['complete'] else 3
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('body');args=parser.parse_args();sys.exit(main(args.body))
