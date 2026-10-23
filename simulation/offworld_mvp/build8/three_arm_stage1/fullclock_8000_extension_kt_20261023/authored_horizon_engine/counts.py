"""Non-authoritative live audit, explicitly segregating originals and corrections."""
import json,csv,collections
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));rows=[]
for limit in (1400,3000,5000,8000):
 cases=[]
 for y in range(2026,2036):
  for w in world:
   b=w['body'];name=f'{b}_{y}_{limit}.json';files=[P/'price_rows_8000'/name] if limit==8000 else [O/'parent_corrected_price_rows'/name,O/'price_rows'/name]
   file=next((f for f in files if f.exists()),None);r=json.loads(file.read_text()) if file else {'body':b,'year':y,'limit_days':limit,'status':'MISSING','reason':'NOT_YET_COMPUTED'};cases.append(r)
 groups=collections.Counter((x.get('reason') or 'PRICED').split(':')[0] for x in cases if x['status']!='PRICED');row={'limit_days':limit,'total':len(cases),'priced':sum(x['status']=='PRICED' for x in cases),'unpriced':sum(x['status']!='PRICED' for x in cases),'reasons':dict(groups)};rows.append(row)
 print(json.dumps(row,sort_keys=True))
(P/'counts_live.json').write_text(json.dumps(rows,indent=2)+'\n')
