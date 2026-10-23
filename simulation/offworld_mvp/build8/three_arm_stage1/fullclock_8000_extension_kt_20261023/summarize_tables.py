"""Report one-body disposition and independently checked dates."""
import json,csv,hashlib
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent;world=list(csv.DictReader((P.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
rows=[]
for x in world:
 b=x['body'];rpath=P/'results'/(b+'.json');r=json.loads(rpath.read_text()) if rpath.exists() else {'body':b,'status':'PENDING'}
 oracle=P/'oracle_results'/(b+'.json');q=json.loads(oracle.read_text()) if oracle.exists() else {}
 rows.append({'body':b,'table_status':r['status'],'last_table_date':r.get('last_table_date',''),'source':r.get('source','registered' if r['status']=='PASS' else ''),'kernel_path':r.get('kernel_path',r.get('kernel_source','')),'table_sha256':r.get('table_sha256',''),'independent_oracle_status':q.get('status','PENDING'),'independent_oracle_samples':q.get('samples',''),'reason':r.get('reason','') or q.get('reason','')})
with (P/'table_disposition.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('TABLES',Counter(x['table_status'] for x in rows),'ORACLE',Counter(x['independent_oracle_status'] for x in rows),'RECOVERED',sum(x['source']=='recovered_phase4e' for x in rows))
