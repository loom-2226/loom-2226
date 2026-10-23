import csv,json,hashlib
from datetime import datetime,timedelta,timezone
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
P=Path(__file__).resolve().parent;S=P.parent
world=list(csv.DictReader((S/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
end=(datetime(2226,12,31,tzinfo=timezone.utc)+timedelta(days=8000)).isoformat();start='2026-01-01T00:00:00Z'
t=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets');rows=[]
for w in world:
 body=w['body'];r={'body':body,'required_end':end,'status':'EXCLUDED','kernel':'','reason':''}
 try:
  a,_=t.adapter.registry.source_for(body,start);b,_=t.adapter.registry.source_for(body,end)
  assert a.sha256==b.sha256,'DIFFERENT_SOURCE_AT_ENDPOINTS'
  assert a.navigation_grade and a.status=='QUALIFIED','SOURCE_NOT_QUALIFIED'
  for x in a.kernel_assets:assert x.path.exists() and hashlib.sha256(x.path.read_bytes()).hexdigest()==x.sha256,'KERNEL_HASH_MISMATCH:'+str(x.path)
  t.adapter._load_source(a);ident=int(t.adapter.registry.body_identifier(body).identifier_value)
  import spiceypy as spice
  for ep in (start,end):t.adapter._require_source_object_coverage(a,ident,spice.str2et(ep))
  r.update(status='COVERED',kernel=a.asset_filename,spice_id=ident)
 except Exception as ex:r['reason']=type(ex).__name__+': '+str(ex)[:450]
 rows.append(r);print(body,r['status'],r['reason'][:110],flush=True);(P/'coverage_partial.json').write_text(json.dumps({'start':start,'end':end,'rows':rows},indent=2)+'\n')
(P/'coverage.json').write_text(json.dumps({'start':start,'end':end,'rows':rows},indent=2)+'\n')
print('TOTAL',len(rows),'COVERED',sum(x['status']=='COVERED' for x in rows),flush=True)
