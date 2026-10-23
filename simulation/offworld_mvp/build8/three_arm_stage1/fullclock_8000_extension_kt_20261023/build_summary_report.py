"""Recompute text-only disposition and exact independent oracle totals."""
import json,csv,hashlib,glob
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent;world=list(csv.DictReader((P.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
rows=[]
for w in world:
 b=w['body'];p=P/'results'/(b+'.json');r=json.loads(p.read_text()) if p.exists() else {'body':b,'status':'PENDING'};qpath=P/'final_oracle_results'/(b+'.json');q=json.loads(qpath.read_text()) if qpath.exists() else {}
 rows.append({'body':b,'status':r['status'],'source':r.get('source','registered' if r['status']=='PASS' else ''),'last_date':r.get('last_table_date',''),'table_path':r.get('table_path',''),'sha256':r.get('table_sha256',''),'oracle':q.get('status','PENDING'),'oracle_samples':q.get('samples',''),'reason':r.get('reason','') or q.get('reason','')})
with (P/'position_table_manifest.csv').open('w',newline='') as f:
 c=csv.DictWriter(f,fieldnames=list(rows[0]));c.writeheader();c.writerows(rows)
counts=Counter(r['status'] for r in rows);checks=Counter(r['oracle'] for r in rows);summary={'classification':'TEST_ONLY_NONCANON','required_last_date':'2057-11-25T00:00:00Z','priced_departures':'2026-01-01 through 2035-12-31','hold_after_2035':'2026 level','lattice_step_days':0.25,'body_count':90,'position_status':dict(counts),'oracle_status':dict(checks),'recovered_phase4e':sum(r['source']=='recovered_phase4e' for r in rows),'route1_control':json.loads((P/'route1_control.json').read_text()),'database_sha256':'e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde'}
(P/'position_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
