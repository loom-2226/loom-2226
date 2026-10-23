"""Check existing VM kernel copies against committed manifest and 2057 endpoints."""
import json,hashlib
from pathlib import Path
import spiceypy as spice
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;manifest={}
for line in (P.parent/'flight_limit_price_sweep_kt_20261023/VM_KERNEL_POSITION_MANIFEST.txt').read_text().splitlines()[3:]:
 a=line.split('\t')
 if len(a)==3:manifest[a[0]]=a[2]
t=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');results=[]
for body,name in [('NEREID','nep101xl-802.bsp'),('PROTEUS','nep098_part-3.bsp')]:
 p=Path('/home/ubuntu/LOOM-output/.phase4e_naif_stage1_20261018')/name;r={'body':body,'path':str(p),'exists':p.exists(),'source':'vm_manifest_recovered_path','status':'EXCLUDED'}
 try:
  assert p.exists() and str(p) in manifest,'NO_MANIFESTED_FILE';h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
  r['sha256']=h.hexdigest();assert h.hexdigest()==manifest[str(p)],'HASH_MISMATCH'
  spice.kclear();spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/lsk/naif0012.tls');spice.furnsh('/home/ubuntu/loom_solar_assets/kernels/spk/de440.bsp');spice.furnsh(str(p));ident=str(t.adapter.registry.body_identifier(body).identifier_value)
  for epoch in ['2026-01-01T00:00:00','2057-11-25T00:00:00']:
   et=spice.str2et(epoch);state,_=spice.spkezr(ident,et,'ECLIPJ2000','NONE','10');assert len(state)==6
  r['status']='ENDPOINTS_PASS';r['last_date']='2057-11-25T00:00:00Z'
 except Exception as e:r['reason']=type(e).__name__+':'+str(e)[:400]
 results.append(r);print(json.dumps(r),flush=True)
(P/'neptune_recovered_check.json').write_text(json.dumps(results,indent=2)+'\n')
