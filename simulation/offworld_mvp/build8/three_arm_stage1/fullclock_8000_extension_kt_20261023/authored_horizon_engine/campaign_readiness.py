"""Fail closed: no four-campaign run until the four priced 2026 populations are complete."""
import csv,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
rows=[]
for limit in (1400,3000,5000,8000):
 eligible=[];missing=[];excluded=[];floor=[]
 for w in world:
  b=w['body'];f=P/'price_rows_8000'/(f'{b}_2026_8000.json') if limit==8000 else O/'parent_corrected_price_rows'/(f'{b}_2026_{limit}.json')
  if limit!=8000 and not f.exists():f=O/'price_rows'/(f'{b}_2026_{limit}.json')
  r=json.loads(f.read_text()) if f.exists() else {'status':'MISSING','reason':'NOT_COMPUTED'}
  if b in ('DACTYL','SELAM'):excluded.append(b)
  elif r['status']=='PRICED':
   if float(r['price_model_units'])<0.7:floor.append(b)
   eligible.append(b)
  else:missing.append({'body':b,'status':r['status'],'reason':r.get('reason','')})
 ready=len(eligible)==88 and len(excluded)==2 and not missing and not floor
 rows.append({'limit_days':limit,'ready':ready,'eligible_priced':len(eligible),'excluded':excluded,'missing':missing,'floor_violations':floor});print('LIMIT',limit,'READY',ready,'PRICED',len(eligible),'MISSING',len(missing),'FLOOR_FAIL',len(floor),flush=True)
(P/'campaign_readiness.json').write_text(json.dumps(rows,indent=2)+'\n')
