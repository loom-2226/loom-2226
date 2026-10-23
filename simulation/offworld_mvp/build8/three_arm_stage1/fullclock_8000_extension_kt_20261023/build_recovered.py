"""Approved recovered Phase4E source, one-body disk lattice and exact oracle."""
import sys,json,hashlib,resource
from pathlib import Path
from datetime import datetime,timedelta,timezone
import numpy as np
import spiceypy as spice
P=Path(__file__).resolve().parent;body=sys.argv[1];r=json.loads((P/'recovered_sources.json').read_text());assert body in r;src=r[body];assert src['source']=='recovered_phase4e';kernel=Path(src['path']);assert kernel.is_file();assert hashlib.sha256(kernel.read_bytes()).hexdigest()==src['sha256']
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
travel=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');reg,_=travel.adapter.registry.source_for(body,'2026-01-01T00:00:00Z');ident=int(travel.adapter.registry.body_identifier(body).identifier_value)
spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls');spice.furnsh(str(kernel))
first=datetime(2026,1,1,tzinfo=timezone.utc);last=datetime(2057,11,25,tzinfo=timezone.utc);step=.25;count=int((last-first).total_seconds()/86400/step)+1
out=P/'tables';out.mkdir(exist_ok=True);path=out/(body+'.npy');assert not path.exists()
result={'body':body,'source':'recovered_phase4e','kernel_path':str(kernel),'kernel_sha256':src['sha256'],'first':first.isoformat(),'last_requested':last.isoformat(),'step_days':step,'samples':count,'status':'EXCLUDED'}
try:
 origin=(first-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()
 def et(i):
  u=origin+i*step*86400;return u+spice.deltet(u,'UTC')
 for i in (0,count-1):spice.spkezr(str(ident),et(i),'ECLIPJ2000','NONE','10')
 mm=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(count,6));oracle_count=0
 for lo in range(0,count,512):
  hi=min(count,lo+512);times=np.asarray([et(i) for i in range(lo,hi)]);states,_=spice.spkezr(str(ident),times,'ECLIPJ2000','NONE','10');mm[lo:hi]=states
  for i in (lo,(lo+hi-1)//2,hi-1):
   scalar,_=spice.spkezr(str(ident),et(i),'ECLIPJ2000','NONE','10');assert np.array_equal(np.asarray(scalar).view(np.uint64),np.asarray(mm[i]).view(np.uint64)),('ORACLE_FAIL',i);oracle_count+=1
  if lo%4096==0:print('CHUNK',body,lo,hi,flush=True)
 mm.flush();del mm
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 result.update(status='PASS',oracle='BITWISE_SCALAR_SPICE_VS_VECTOR_SPICE',oracle_samples=oracle_count,table_path=str(path),table_sha256=h.hexdigest(),last_table_date=last.isoformat())
except Exception as e:
 result['reason']=type(e).__name__+': '+str(e)[:400]
 if path.exists():path.unlink()
result['peak_rss_kb']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(P/'results').mkdir(exist_ok=True);(P/'results'/(body+'.json')).write_text(json.dumps(result,indent=2)+'\n');print('RESULT',json.dumps(result),flush=True)
