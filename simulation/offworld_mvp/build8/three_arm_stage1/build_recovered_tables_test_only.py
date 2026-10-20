"""PR427-only recovered SPK table build, original bitwise validation semantics."""
import hashlib,json,os,time,resource
from pathlib import Path
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.three_arm_stage1.recovered_phase4e_registry import recovered_registry,test_only_run_identity
from simulation.offworld_mvp.build8.three_arm_stage1.body_lattice_builder import indices
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel

P=Path(__file__).resolve().parent
OLD=json.loads((P/'table_manifest_direct_time.json').read_text())
E=json.loads((P/'experiment.json').read_text())
OUT=Path('/home/ubuntu/LOOM-output/stage1_recovered_phase4e_pr427_test_only')
MANIFEST=P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json'
PROGRESS=P/'RECOVERED_PHASE4E_TABLE_BUILD_PROGRESS_TEST_ONLY.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(path,data):
 tmp=path.with_suffix('.pending.json');tmp.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');os.replace(tmp,path)
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def main():
 start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
 assert not MANIFEST.exists(),'MANIFEST_EXISTS'
 root=Path(OLD['table_root']);et=np.load(root/'builder_et.npy');assert sha(root/'builder_et.npy')==OLD['builder_et_sha256']
 assert len(et)==8337 and OLD['step_days']==0.25
 recovery=json.loads((P/'PHASE4E_RECOVERY_34_TEST_ONLY_MANIFEST.json').read_text())['files']
 assert len(recovery)==34
 travel=OnDemandTravel(asset_root=E['asset_root']);travel.adapter.registry=recovered_registry(E['asset_root'])
 identity={**test_only_run_identity(),'builder':'body_lattice_builder.py:17-30,33-49','first':OLD['first'],'last':OLD['last'],'step_days':OLD['step_days'],'dtype':'float64','shape':[len(et),6],'builder_et_sha256':OLD['builder_et_sha256']}
 if PROGRESS.exists():
  state=json.loads(PROGRESS.read_text());assert state['identity']==identity
 else:state={'identity':identity,'tables':{},'started':time.time()}
 for row in recovery:
  body=row['body'];path=OUT/(body+'.npy')
  if body in state['tables']:
   assert path.exists() and sha(path)==state['tables'][body]['sha256'];continue
  assert not path.exists(),'UNTRACKED_EXISTING_BINARY:'+body
  began=time.monotonic()
  source,coverage=travel.adapter.registry.source_for(body,OLD['first'])
  assert source.sha256==row['sha256'] and source.navigation_grade and source.status=='QUALIFIED'
  endsource,_=travel.adapter.registry.source_for(body,OLD['last']);assert endsource.sha256==source.sha256
  travel.adapter._load_source(source)
  target=str(travel.adapter.registry.body_identifier(body).identifier_value)
  travel.adapter._require_source_object_coverage(source,int(target),float(et[0]))
  travel.adapter._require_source_object_coverage(source,int(target),float(et[-1]))
  # Exactly the same ECLIPJ2000/NONE/10 state generation and float64 format.
  pieces=[]
  for lo in range(0,len(et),1000):
   hi=min(len(et),lo+1000)
   states,_=spice.spkezr(target,et[lo:hi],'ECLIPJ2000','NONE','10')
   a=np.asarray(states,dtype=np.float64);assert a.shape==(hi-lo,6);pieces.append(a)
  arr=np.concatenate(pieces);assert arr.shape==(len(et),6)
  maximum=np.zeros(6,dtype=np.float64);pmax=vmax=0.
  for ix in indices(len(arr),1000):
   direct,_=spice.spkezr(target,float(et[ix]),'ECLIPJ2000','NONE','10')
   d=np.asarray(direct,dtype=np.float64);delta=np.abs(arr[ix]-d)
   maximum=np.maximum(maximum,delta);pmax=max(pmax,float(np.linalg.norm(delta[:3])));vmax=max(vmax,float(np.linalg.norm(delta[3:])))
   if not np.array_equal(arr[ix].view(np.uint64),d.view(np.uint64)):
    raise RuntimeError(f'BITWISE_MISMATCH body={body} tick={ix} components={delta.tolist()}')
  temp=OUT/(body+'.pending.npy');np.save(temp,arr);os.replace(temp,path)
  validation={'samples':1000,'max_position_component_km':float(maximum[:3].max()),'max_velocity_component_km_s':float(maximum[3:].max()),'max_position_norm_km':pmax,'max_velocity_norm_km_s':vmax,'bitwise_identical':True}
  state['tables'][body]={'sha256':sha(path),'source_sha256':source.sha256,'validation':validation,'validation_samples':1000,'seconds':time.monotonic()-began,'bytes':path.stat().st_size}
  atomic(PROGRESS,state)
  print('TABLE_VALIDATED',body,'SECONDS',round(state['tables'][body]['seconds'],2),'MAX_POS',pmax,'MAX_VEL',vmax,'TOTAL',round(time.monotonic()-start,2),'PEAK',rss(),flush=True)
 manifest={**identity,'classification':'RECOVERED_VINTAGE_TEST_ONLY','table_root':str(OUT),'tables':{body:{'sha256':v['sha256'],'source_sha256':v['source_sha256'],'validation_samples':1000,'validation':v['validation']} for body,v in state['tables'].items()},'build_elapsed_seconds':time.monotonic()-start,'build_peak_rss_bytes':rss()}
 assert len(manifest['tables'])==34
 atomic(MANIFEST,manifest)
 print('BUILD_COMPLETE',sha(MANIFEST),'SECONDS',round(time.monotonic()-start,2),'PEAK',rss(),flush=True)
if __name__=='__main__':main()
