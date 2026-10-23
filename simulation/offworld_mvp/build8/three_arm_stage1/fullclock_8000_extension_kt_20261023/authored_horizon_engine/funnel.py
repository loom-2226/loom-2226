"""Aggregate four complete campaign reports; never fabricate missing runs."""
import csv,json
from pathlib import Path
from decimal import Decimal
P=Path(__file__).resolve().parent;O=P.parent;world=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));summary=[];body_rows=[]
for limit in (1400,3000,5000,8000):
 f=P/f'fullclock_{limit}_days_report.json'
 if not f.exists():print('MISSING_CAMPAIGN',limit,flush=True);continue
 r=json.loads(f.read_text());starts=[x for y in r['per_year'] for x in (y.get('dominant_started') or [])];counts={b:sum(x['body']==b for x in starts) for b in [w['body'] for w in world]};total=sum((Decimal(str(x['total_capital_commitment'])) for x in starts),Decimal(0));row={'flight_limit_days':limit,'projects_started':r['projects_started'],'bodies_started':r['distinct_started_bodies'],'last_start_year':max((int(x['year']) for x in starts),default=None),'total_committed':str(total),'sponsors':r.get('campaign_sponsors'),'year_count':r.get('year_count')};summary.append(row)
 for w in world:
  b=w['body'];p=P/'price_rows_8000'/(f'{b}_2026_8000.json') if limit==8000 else O/'parent_corrected_price_rows'/(f'{b}_2026_{limit}.json')
  if limit!=8000 and not p.exists():p=O/'price_rows'/(f'{b}_2026_{limit}.json')
  price=json.loads(p.read_text()) if p.exists() else {'status':'MISSING','reason':'NOT_YET_COMPUTED'}
  body_rows.append({'flight_limit_days':limit,'body':b,'projects_started':counts[b],'price_status':price['status'],'price_model_units':price.get('price_model_units',''),'unpriced_reason':price.get('reason','')})
(P/'campaign_funnel_summary.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'campaign_funnel_by_body.json').write_text(json.dumps(body_rows,indent=2)+'\n');print(json.dumps(summary,indent=2))
if len(summary)==4:
 never=[r for r in body_rows if r['flight_limit_days']==8000 and r['projects_started']==0];(P/'never_started_8000.json').write_text(json.dumps(never,indent=2)+'\n');print('NEVER_STARTED_8000',len(never))
