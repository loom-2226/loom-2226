"""Four giant planet-center state tables; bitwise direct SPICE validation."""
import json,hashlib,time,resource,os
from pathlib import Path
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.three_arm_stage1.body_lattice_builder import indices
from simulation.offworld_mvp.build8.travel_pilot.eligibility import catalog_registry
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent
E=json.loads((P/'experiment.json').read_text());OLD=json.loads((P/'table_manifest_direct_time.json').read_text())
OUT=Path('/home/ubuntu/LOOM-output/pr427_giant_parent_tables_test_only')
MAN=P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rss():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def main():
 t=time.monotonic();assert not MAN.exists(),'MANIFEST_ALREADY_EXISTS';OUT.mkdir(parents=True,exist_ok=True)
 etpath=Path(OLD['table_root'])/'builder_et.npy';assert sha(etpath)==OLD['builder_et_sha256']
 et=np.load(etpath);assert len(et)==8337
 travel=OnDemandTravel(asset_root=E['asset_root']);entries={}
 for body in ('JUPITER','SATURN','URANUS','NEPTUNE'):
  st=time.monotonic();source,coverage=travel.adapter.registry.source_for(body,OLD['first']);end,_=travel.adapter.registry.source_for(body,OLD['last']);assert source.sha256==end.sha256 and source.navigation_grade and source.status=='QUALIFIED'
  for asset in source.kernel_assets:assert asset.path.exists() and sha(asset.path)==asset.sha256,('MISSING_OR_WRONG_KERNEL',body,str(asset.path))
  target=str(travel.adapter.registry.body_identifier(body).identifier_value)
  assert target in ('599','699','799','899'),('NOT_PLANET_CENTER',body,target)
  travel.adapter._load_source(source)
  travel.adapter._require_source_object_coverage(source,int(target),float(et[0]));travel.adapter._require_source_object_coverage(source,int(target),float(et[-1]))
  path=OUT/(body+'.npy');assert not path.exists(),('OUTPUT_EXISTS',str(path))
  chunks=[]
  for lo in range(0,len(et),1000):
   hi=min(len(et),lo+1000);states,_=spice.spkezr(target,et[lo:hi],'ECLIPJ2000','NONE','10');chunks.append(np.asarray(states,dtype=np.float64))
  arr=np.concatenate(chunks);assert arr.shape==(len(et),6)
  for ix in indices(len(et),1000):
   direct,_=spice.spkezr(target,float(et[ix]),'ECLIPJ2000','NONE','10');d=np.asarray(direct,dtype=np.float64)
   if not np.array_equal(arr[ix].view(np.uint64),d.view(np.uint64)):raise RuntimeError('BITWISE_MISMATCH:'+body+':'+str(ix))
  tmp=OUT/(body+'.pending.npy');np.save(tmp,arr);os.replace(tmp,path)
  entries[body]={'spice_id':int(target),'spice_id_type':'PLANET_CENTER','source_file':str(next(a.path for a in source.kernel_assets if a.sha256==source.sha256)),'source_sha256':source.sha256,'kernel_files':[{'path':str(a.path),'sha256':a.sha256} for a in source.kernel_assets],'table_sha256':sha(path),'validation_samples':1000,'bitwise_direct_spice':True,'seconds':time.monotonic()-st}
  print('VALIDATED',body,target,entries[body]['table_sha256'],'SECONDS',entries[body]['seconds'],flush=True)
 report={'classification':'TEST_ONLY_NONCANON','first':OLD['first'],'last':OLD['last'],'step_days':OLD['step_days'],'table_root':str(OUT),'builder_et_sha256':OLD['builder_et_sha256'],'tables':entries,'elapsed_seconds':time.monotonic()-t,'peak_rss_bytes':rss(),'numpy_version':np.__version__,'spiceypy_version':spice.__version__}
 with MAN.open('x') as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
 print('DONE',sha(MAN),report['elapsed_seconds'],rss(),flush=True)
if __name__=='__main__':main()
