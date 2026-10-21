"""Extend pinned, non-recovered planetary tables to 2035-12-31, bitwise SPICE."""
import hashlib,json,os,resource,time
from pathlib import Path
from datetime import datetime,timedelta,timezone
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;OUT=Path('/home/ubuntu/LOOM-output/pr427_assist_2035_tables_test_only')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();old=json.loads((P/'table_manifest_direct_time.json').read_text());giant=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text());e=json.loads((P/'experiment.json').read_text());travel=OnDemandTravel(asset_root=e['asset_root']);first=datetime.fromisoformat(old['first'].replace('Z','+00:00'));last=datetime(2035,12,31,tzinfo=timezone.utc);step=old['step_days'];count=int((last-first).total_seconds()/(step*86400))+1;et=np.array([spice.str2et((first+timedelta(days=i*step)).strftime('%Y-%m-%dT%H:%M:%S')) for i in range(count)],dtype=np.float64)
 # Explicitly do not extend recovered small-body lane, even if raw SPK has mathematical coverage.
 requested=['EARTH','MERCURY','VENUS','MARS','JUPITER','SATURN','URANUS','NEPTUNE','PLUTO'];report={'classification':'TEST_ONLY_NONCANON','first':old['first'],'last':last.isoformat(),'step_days':step,'time_samples':count,'parent_manifest_hashes':{'original_25':sha(P/'table_manifest_direct_time.json'),'giants':sha(P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json'),'earth':sha(P/'PR427_ASSIST_EARTH_TABLE_REPORT_TEST_ONLY.json')},'table_root':str(OUT),'tables':{},'excluded':{},'recovered_small_bodies_policy':'NO_EXTENSION_AFTER_2031-12-31'}
 OUT.mkdir(parents=True,exist_ok=True);manifest=P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json';assert not manifest.exists()
 for body in requested:
  t=time.monotonic();path=OUT/(body+'.npy');assert not path.exists(),('OUTPUT_EXISTS',str(path))
  try:
   source,_=travel.adapter.registry.source_for(body,old['first']);end,_=travel.adapter.registry.source_for(body,'2035-12-31T00:00:00Z');assert source.sha256==end.sha256 and source.navigation_grade and source.status=='QUALIFIED',('SOURCE_NOT_QUALIFIED',body)
   for asset in source.kernel_assets:assert asset.path.exists() and sha(asset.path)==asset.sha256,('KERNEL_HASH',str(asset.path))
   target=str(travel.adapter.registry.body_identifier(body).identifier_value);travel.adapter._load_source(source);travel.adapter._require_source_object_coverage(source,int(target),float(et[0]));travel.adapter._require_source_object_coverage(source,int(target),float(et[-1]))
  except Exception as ex:
   report['excluded'][body]=str(ex);print('EXCLUDED',body,str(ex),flush=True);continue
  arr=[]
  for i in range(0,len(et),1000):
   states,_=spice.spkezr(target,et[i:i+1000],'ECLIPJ2000','NONE','10');arr.append(np.asarray(states,dtype=np.float64))
  arr=np.concatenate(arr);assert arr.shape==(len(et),6)
  for i in range(len(et)):
   direct,_=spice.spkezr(target,float(et[i]),'ECLIPJ2000','NONE','10')
   assert np.array_equal(arr[i].view(np.uint64),np.asarray(direct,dtype=np.float64).view(np.uint64)),('BITWISE_MISMATCH',body,i)
  np.save(path,arr);report['tables'][body]={'spice_id':int(target),'source_file':source.asset_filename,'source_sha256':source.sha256,'kernel_files':[{'path':str(a.path),'sha256':a.sha256} for a in source.kernel_assets],'table_path':str(path),'sha256':sha(path),'validation_samples':len(et),'seconds':time.monotonic()-t};print('TABLE',body,report['tables'][body]['sha256'],'SECONDS',round(time.monotonic()-t,2),flush=True)
 report['elapsed_seconds']=time.monotonic()-start;report['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
 with manifest.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('DONE',sha(manifest),'SECONDS',report['elapsed_seconds'],'PEAK',report['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
