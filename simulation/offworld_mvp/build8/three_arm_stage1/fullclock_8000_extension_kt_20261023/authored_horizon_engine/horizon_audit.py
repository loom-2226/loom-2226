from datetime import date,timedelta
from pathlib import Path
import json,csv
P=Path(__file__).resolve().parent;last=date(2035,12,31)+timedelta(days=8000);assert last.isoformat()=='2057-11-25';first=date(2026,1,1);rows=[]
for p in (P/'price_rows_8000').glob('*.json'):
 r=json.loads(p.read_text());day=r.get('departure_date');limit=int(r['limit_days']);end=(date.fromisoformat(day)+timedelta(days=limit)) if day else date(int(r['year']),12,31)+timedelta(days=limit)
 status='WITHIN_HORIZON' if end<=last else 'NO_DATA';assert status=='WITHIN_HORIZON',r
 rows.append({'body':r['body'],'year':r['year'],'limit':limit,'max_arrival':end.isoformat(),'status':r['status']})
out={'priced_departure_last':'2035-12-31','flight_limit_days':8000,'last_arrival':'2057-11-25','derivation':'2035-12-31 plus 8000 calendar days','rows_checked':len(rows),'out_of_horizon':0};(P/'horizon_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
