import json,csv,collections
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));allrows=[]
for limit in (1400,3000,5000,8000):
 grouped=collections.Counter();priced=0;pending=0
 for y in range(2026,2036):
  for w in world:
   b=w['body'];name=f'{b}_{y}_{limit}.json';files=([P/'price_rows_8000'/name] if limit==8000 else [O/'parent_corrected_price_rows'/name,O/'price_rows'/name]);f=next((x for x in files if x.exists()),None)
   if f is None:grouped['NOT_YET_COMPUTED']+=1;pending+=1;continue
   r=json.loads(f.read_text());reason=r.get('reason','')
   if r['status']=='PRICED':priced+=1;continue
   if b in ('DACTYL','SELAM'):key='EXCLUDED_NO_SOURCE_AND_NO_GRAVITY'
   elif 'INVALID_FLIGHT_RANGE' in reason:key='FLIGHT_GRID_MAX_5000'
   elif 'UNKNOWN_EPHEMERIS_MISSING' in reason:key='LEGACY_ENDPOINT_UNKNOWN_EPHEMERIS_MISSING'
   elif 'UNKNOWN_LOCAL_LEG' in reason:key='LEGACY_ENDPOINT_UNKNOWN_LOCAL_LEG'
   elif 'NO_VERIFIED_POSITION_TABLE' in reason:key='LEGACY_MOON_OWN_TABLE_GATE'
   elif 'NO_VERIFIED_PARENT_POSITION_TABLE' in reason:key='PARENT_TABLE_UNVERIFIED'
   elif 'CelestialStateError' in reason:key='LEGACY_SOURCE_COVERAGE_ERROR'
   elif 'NO_DATA' in reason:key='NO_DATA'
   else:key=reason.split(':')[0] if reason else r['status']
   grouped[key]+=1
  
 row={'limit_days':limit,'total':900,'priced':priced,'unpriced_including_pending':900-priced,'pending':pending,'reason_groups':dict(grouped)};allrows.append(row);print(json.dumps(row,sort_keys=True))
(P/'counts_detailed_live.json').write_text(json.dumps(allrows,indent=2)+'\n')
