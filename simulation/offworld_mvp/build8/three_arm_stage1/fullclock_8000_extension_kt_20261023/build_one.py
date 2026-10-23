"""One-body, on-disk numeric UTC/deltet lattice; sampled scalar SPICE oracle."""
import sys,json,hashlib,resource
from pathlib import Path
from datetime import datetime,timedelta,timezone
import numpy as np
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;body=sys.argv[1];out=P/'tables';out.mkdir(exist_ok=True)
first=datetime(2026,1,1,tzinfo=timezone.utc);last=datetime(2057,11,25,tzinfo=timezone.utc);step=.25;count=int((last-first).total_seconds()/86400/step)+1
result={'body':body,'first':first.isoformat(),'last_requested':last.isoformat(),'step_days':step,'samples':count,'status':'EXCLUDED','oracle':'NOT_RUN'}
try:
 travel=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');source,_=travel.adapter.registry.source_for(body,first.isoformat().replace('+00:00','Z'));end,_=travel.adapter.registry.source_for(body,last.isoformat().replace('+00:00','Z'))
 assert source.sha256==end.sha256,'SOURCE_SWITCH';assert source.navigation_grade and source.status=='QUALIFIED','SOURCE_UNQUALIFIED'
 for a in source.kernel_assets:
  assert a.path.exists(),'MISSING_REGISTERED_KERNEL:'+str(a.path)
  h=hashlib.sha256()
  with a.path.open('rb') as f:
   for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
  assert h.hexdigest()==a.sha256,'KERNEL_SHA_MISMATCH:'+str(a.path)
 travel.adapter._load_source(source);ident=int(travel.adapter.registry.body_identifier(body).identifier_value)
 spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls')
 first_utc=(first-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()
 def et(i):
  u=first_utc+i*step*86400;return u+spice.deltet(u,'UTC')
 for i in [0,count-1]:travel.adapter._require_source_object_coverage(source,ident,et(i))
 path=out/(body+'.npy');assert not path.exists(),'TABLE_ALREADY_EXISTS'
 mm=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(count,6));oracle_count=0
 for lo in range(0,count,512):
  hi=min(count,lo+512);times=np.array([et(i) for i in range(lo,hi)],dtype=np.float64)
  states,_=spice.spkezr(str(ident),times,'ECLIPJ2000','NONE','10');mm[lo:hi]=states
  for i in (lo,(lo+hi-1)//2,hi-1):
   direct,_=spice.spkezr(str(ident),float(et(i)),'ECLIPJ2000','NONE','10')
   assert np.array_equal(np.asarray(direct,dtype=np.float64).view(np.uint64),np.asarray(mm[i]).view(np.uint64)),('ORACLE_BITWISE_MISMATCH',i)
   oracle_count+=1
 mm.flush();del mm
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 result.update(status='PASS',oracle='BITWISE_SCALAR_SPICE_VS_VECTOR_SPICE',oracle_samples=oracle_count,table_path=str(path),table_sha256=h.hexdigest(),kernel_source=source.asset_filename,last_table_date=last.isoformat())
except Exception as e:
 result['reason']=type(e).__name__+': '+str(e)[:500]
 if 'path' in locals() and path.exists() and result['status']!='PASS':path.unlink()
result['peak_rss_kb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(P/'results').mkdir(exist_ok=True);(P/'results'/(body+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True),flush=True)
