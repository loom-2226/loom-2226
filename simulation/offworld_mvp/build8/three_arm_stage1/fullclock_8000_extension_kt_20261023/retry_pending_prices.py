"""Recompute only rows blocked by oracle work that later passed."""
import json,subprocess,sys,os
from pathlib import Path
P=Path(__file__).resolve().parent
for path in sorted((P/'price_rows').glob('*.json')):
 row=json.loads(path.read_text());body=row['body'];y=row['year'];limit=row['limit_days']
 if row['status']!='UNPRICED' or row.get('reason')!='NO_VERIFIED_POSITION_TABLE':continue
 needs=[b for b in ('EARTH',body) if not (P/'final_oracle_results'/(b+'.json')).exists() or json.loads((P/'final_oracle_results'/(b+'.json')).read_text())['status']!='PASS']
 if needs:continue
 print('RETRY',body,y,limit,flush=True)
 x=subprocess.run([sys.executable,str(P/'price_one.py'),body,str(y),str(limit)],capture_output=True,text=True,env=os.environ.copy());print('DONE',body,y,limit,x.returncode,(x.stdout or x.stderr)[-190:],flush=True)
