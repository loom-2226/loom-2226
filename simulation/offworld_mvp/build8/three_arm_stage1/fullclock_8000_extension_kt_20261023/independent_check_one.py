"""Separate-process sampled scalar SPICE oracle on one disk table; exact bits."""
import sys,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;body=sys.argv[1];r=json.loads((P/'results'/(body+'.json')).read_text());assert r['status']=='PASS'
p=Path(r['table_path']);assert p.exists();h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==r['table_sha256'];m=np.load(p,mmap_mode='r');assert m.shape==(46605,6)
spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls');travel=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');ident=int(travel.adapter.registry.body_identifier(body).identifier_value)
if r.get('source')=='recovered_phase4e':
 k=Path(r['kernel_path']);assert hashlib.sha256(k.read_bytes()).hexdigest()==r['kernel_sha256'];spice.furnsh(str(k))
else:
 source,_=travel.adapter.registry.source_for(body,'2026-01-01T00:00:00Z');travel.adapter._load_source(source)
origin=(datetime(2026,1,1,tzinfo=timezone.utc)-datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()
indices=sorted(set([0,len(m)//2,len(m)-1]+list(range(0,len(m),1200))))
for i in indices:
 u=origin+i*.25*86400;et=u+spice.deltet(u,'UTC');s,_=spice.spkezr(str(ident),float(et),'ECLIPJ2000','NONE','10');assert np.array_equal(np.asarray(s,dtype=np.float64).view(np.uint64),np.asarray(m[i]).view(np.uint64)),('EXACT_ORACLE_MISMATCH',body,i)
print(json.dumps({'body':body,'status':'PASS','independent_checker':'separate_process_scalar_SPICE_exact_bits','samples':len(indices),'source':r.get('source','registered'),'table_sha256':h,'last_table_date':r['last_table_date']}))
