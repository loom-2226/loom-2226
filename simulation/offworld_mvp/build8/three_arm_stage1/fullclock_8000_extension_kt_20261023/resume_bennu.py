"""Resume interrupted one-body BENNU lattice without recomputing verified chunks."""
import json,hashlib,resource
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;body='BENNU';path=P/'tables/BENNU.npy';assert path.exists();m=np.load(path,mmap_mode='r+');assert m.shape==(46605,6)
travel=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');source,_=travel.adapter.registry.source_for(body,'2026-01-01T00:00:00Z');end,_=travel.adapter.registry.source_for(body,'2057-11-25T00:00:00Z');assert source.sha256==end.sha256
for a in source.kernel_assets:
 assert a.path.exists()
 h=hashlib.sha256()
 with a.path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 assert h.hexdigest()==a.sha256
travel.adapter._load_source(source);spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls');ident=int(travel.adapter.registry.body_identifier(body).identifier_value)
first=datetime(2026,1,1,tzinfo=timezone.utc);origin=(first-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()
def et(i):
 u=origin+i*21600;return u+spice.deltet(u,'UTC')
used=np.flatnonzero(np.any(m!=0,axis=1));assert len(used)>0;start=(int(used[-1])//512)*512;print('RESUME_FROM',start,'OF',len(m),flush=True)
# Exact oracle samples across the already written prefix.
for i in sorted(set([0,start//2,max(0,start-512)]+list(range(0,start,1200)))):
 direct,_=spice.spkezr(str(ident),et(i),'ECLIPJ2000','NONE','10');assert np.array_equal(np.asarray(direct).view(np.uint64),np.asarray(m[i]).view(np.uint64)),('PREFIX_ORACLE_FAIL',i)
n=0
for lo in range(start,len(m),512):
 hi=min(len(m),lo+512);times=np.array([et(i) for i in range(lo,hi)]);states,_=spice.spkezr(str(ident),times,'ECLIPJ2000','NONE','10');m[lo:hi]=states
 for i in (lo,(lo+hi-1)//2,hi-1):
  direct,_=spice.spkezr(str(ident),et(i),'ECLIPJ2000','NONE','10');assert np.array_equal(np.asarray(direct).view(np.uint64),np.asarray(m[i]).view(np.uint64)),('ORACLE_FAIL',i);n+=1
 if lo%2048==0:print('CHUNK',lo,hi,flush=True)
m.flush();del m
h=hashlib.sha256()
with path.open('rb') as f:
 for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
r={'body':body,'first':first.isoformat(),'last_requested':'2057-11-25T00:00:00+00:00','step_days':0.25,'samples':46605,'status':'PASS','oracle':'BITWISE_SCALAR_SPICE_VS_VECTOR_SPICE_WITH_PREFIX_RECHECK','oracle_samples':n,'table_path':str(path.resolve()),'table_sha256':h.hexdigest(),'kernel_source':source.asset_filename,'last_table_date':'2057-11-25T00:00:00+00:00','peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
(P/'results/BENNU.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT',json.dumps(r),flush=True)
