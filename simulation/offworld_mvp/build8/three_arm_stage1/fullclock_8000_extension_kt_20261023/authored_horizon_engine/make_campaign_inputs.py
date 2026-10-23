"""2026 quotes held post-2035; fail closed on missing rows, never use old price fallback."""
import json,csv,hashlib
from decimal import Decimal
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
for limit in (1400,3000,5000,8000):
 matrix=[];counts={'PRICED':0,'UNPRICED':0,'EXCLUDED':0}
 for w in world:
  b=w['body'];f=P/'price_rows_8000'/(f'{b}_2026_8000.json') if limit==8000 else O/'parent_corrected_price_rows'/(f'{b}_2026_{limit}.json')
  if limit!=8000 and not f.exists():f=O/'price_rows'/(f'{b}_2026_{limit}.json')
  r=json.loads(f.read_text()) if f.exists() else {'status':'UNPRICED','reason':'NOT_YET_COMPUTED'}
  if b in ('DACTYL','SELAM'):status='EXCLUDED';reason='NO_SOURCE_AND_NO_GRAVITY_VALUE';quotes=[]
  elif r['status']=='PRICED':
   status='PRICED';reason=None;value=Decimal(r['price_model_units']);assert value>=Decimal('0.7'),('FLOOR_FAIL',b,limit,value)
   quote={'source':f'pr427_fullclock_{limit}','source_year':2026,'held':False,'status':'PRICED_TEST_ONLY','unit':'USD','price_fields':{'total_usd':str(value*Decimal(10**9)),'model_units':str(value)},'method_fields':{'parent_source_body':r.get('parent_source_body',w['parent'] or b),'source':r.get('source','registered'),'flight_limit_days':limit,'no_fallback':True},'run_identity':hashlib.sha256(f.read_bytes()).hexdigest()};quotes=[quote]
  else:status='UNPRICED';reason=r.get('reason','NO_DATA');quotes=[]
  counts[status]+=1;matrix.append({'body':b,'calendar_year':2026,'mission_type':'rendezvous','status':'PRICED_TEST_ONLY' if status=='PRICED' else status,'selected_status':'PRICED_TEST_ONLY' if status=='PRICED' else status,'selected_model_units':str(value) if status=='PRICED' else None,'selected_source':f'pr427_fullclock_{limit}' if status=='PRICED' else None,'quotes':quotes,'unpriced_reason':reason})
 path=P/(f'campaign_prices_{limit}.json');path.write_text(json.dumps({'classification':'TEST_ONLY_NONCANON','matrix':matrix,'limit_days':limit,'counts':counts,'no_fallback':True},indent=2)+'\n');print('CAMPAIGN_INPUT',limit,counts,'sha256',hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)
