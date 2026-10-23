"""Read-only 90-body endpoint registry screen. Not a SPICE oracle or table qualification."""
import csv,json
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
p=Path(__file__).resolve().parent;s=p.parent
world=list(csv.DictReader((s/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
travel=OnDemandTravel(asset_root='/home/ubuntu/loom_solar_assets')
start='2026-01-01T00:00:00Z';end='2248-11-25T00:00:00Z';rows=[]
for w in world:
 b=w['body'];r={'body':b,'required_start':start,'required_end':end,'start_source':'','end_source':'','status':'','reason':''}
 for ep,key in [(start,'start_source'),(end,'end_source')]:
  try:
   source,cov=travel.adapter.registry.source_for(b,ep);r[key]=source.sha256
  except Exception as exc:r['reason']+=(key+': '+str(exc)[:160]+'; ')
 r['status']='REGISTRY_ENDPOINTS_PRESENT' if r['start_source'] and r['end_source'] else 'REGISTRY_GAP'
 rows.append(r);print(b,r['status'],flush=True)
(p/'registry_screen.json').write_text(json.dumps({'classification':'PRELIMINARY_NOT_INDEPENDENT_VERIFICATION','rows':rows},indent=2)+'\n')
print('COMPLETE',len(rows),sum(x['status']=='REGISTRY_ENDPOINTS_PRESENT' for x in rows),flush=True)
