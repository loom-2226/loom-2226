"""Resume numeric-lattice 2035 planetary tables. Atomic fsync + rename; verify every completed file."""
import hashlib,json,os,resource,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;OUT=Path('/home/ubuntu/LOOM-output/pr427_assist_2035_numeric_tables_test_only')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 started=time.monotonic();lsk=Path('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls');assert sha(lsk)=='678e32bdb5a744117a467cd9601cd6b373f0e9bc9bbde1371d5eee39600a039b';spice.furnsh(str(lsk))
 old=json.loads((P/'table_manifest_direct_time.json').read_text());original=json.loads((P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json').read_text());experiment=json.loads((P/'experiment.json').read_text());travel=OnDemandTravel(asset_root=experiment['asset_root']);first=datetime.fromisoformat(old['first'].replace('Z','+00:00'));last=datetime(2035,12,31,tzinfo=timezone.utc);step=old['step_days'];n=int((last-first).total_seconds()/(step*86400))+1;utc=np.asarray([(first+timedelta(days=i*step)-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds() for i in range(n)],dtype=np.float64);et=np.asarray([u+spice.deltet(float(u),'UTC') for u in utc],dtype=np.float64)
 assert n==14425
 mismatches=[i for i,x in enumerate(et) if spice.et2utc(float(x),'ISOC',0)!=(first+timedelta(days=i*step)).strftime('%Y-%m-%dT%H:%M:%S')];assert not mismatches,('UTC_ROUNDTRIP',mismatches[:5]);print('EPOCH_ROUNDTRIP',n,'PASS',flush=True)
 OUT.mkdir(parents=True,exist_ok=True);result={'classification':'TEST_ONLY_NONCANON','lattice':'NUMERIC_UTC_PLUS_DELTET','first':old['first'],'last':last.isoformat(),'step_days':step,'time_samples':n,'lsk_sha256':sha(lsk),'original_2035_manifest_sha256':sha(P/'PR427_ASSIST_2035_TABLE_MANIFEST_TEST_ONLY.json'),'tables':{},'excluded':{},'no_future_leap_seconds_assumed':True}
 for body in ['EARTH','MERCURY','VENUS','MARS','JUPITER','SATURN','URANUS','NEPTUNE','PLUTO']:
  t=time.monotonic();source,_=travel.adapter.registry.source_for(body,old['first']);end,_=travel.adapter.registry.source_for(body,'2035-12-31T00:00:00Z');assert source.sha256==end.sha256 and source.navigation_grade and source.status=='QUALIFIED';assert all(sha(x.path)==x.sha256 for x in source.kernel_assets);target=str(travel.adapter.registry.body_identifier(body).identifier_value);travel.adapter._load_source(source);travel.adapter._require_source_object_coverage(source,int(target),float(et[0]));travel.adapter._require_source_object_coverage(source,int(target),float(et[-1]));path=OUT/(body+'.npy')
  if path.exists():
   arr=np.load(path,mmap_mode='r');assert arr.shape==(n,6) and arr.dtype==np.float64
   assert all(np.array_equal(np.asarray(arr[i]).view(np.uint64),np.asarray(spice.spkezr(target,float(et[i]),'ECLIPJ2000','NONE','10')[0]).view(np.uint64)) for i in range(n)),('EXISTING_INVALID',body)
   action='VERIFIED_RESUME'
  else:
   chunks=[]
   for i in range(0,n,1000):chunks.append(np.asarray(spice.spkezr(target,et[i:i+1000],'ECLIPJ2000','NONE','10')[0],dtype=np.float64))
   arr=np.concatenate(chunks);assert arr.shape==(n,6)
   assert all(np.array_equal(arr[i].view(np.uint64),np.asarray(spice.spkezr(target,float(et[i]),'ECLIPJ2000','NONE','10')[0]).view(np.uint64)) for i in range(n)),('NEW_INVALID',body)
   tmp=OUT/(body+'.pending.npy');assert not tmp.exists();
   with tmp.open('xb') as f:np.save(f,arr);f.flush();os.fsync(f.fileno())
   os.replace(tmp,path);fd=os.open(str(OUT),os.O_RDONLY);os.fsync(fd);os.close(fd);action='BUILT_ATOMIC'
  result['tables'][body]={'spice_id':int(target),'source_sha256':source.sha256,'source_file':source.asset_filename,'table_path':str(path),'sha256':sha(path),'validation_samples':n,'epoch_roundtrip_samples':n,'action':action,'seconds':time.monotonic()-t};print('TABLE',body,action,result['tables'][body]['sha256'],'SECONDS',round(time.monotonic()-t,2),flush=True)
 result['elapsed_seconds']=time.monotonic()-started;result['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024;manifest=P/'PR427_ASSIST_2035_NUMERIC_TABLE_MANIFEST_TEST_ONLY.json';assert not manifest.exists()
 with manifest.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print('DONE',sha(manifest),result['elapsed_seconds'],result['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
