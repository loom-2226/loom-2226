"""Detached resumable 8000-day 2026-2035 all-body price sweep; original engine untouched."""
import subprocess,sys,csv,json,os
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;w=list(csv.DictReader((O.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()))
for year in range(2035,2025,-1):
 for r in reversed(w):
  b=r['body'];dest=P/'price_rows_8000'/(f'{b}_{year}_8000.json')
  if dest.exists():continue
  if b in ('DACTYL','SELAM'):
   dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps({'body':b,'year':year,'limit_days':8000,'status':'EXCLUDED','reason':'NO_SOURCE_AND_NO_GRAVITY_VALUE','parent_source_body':r['parent']})+'\n');continue
  parent=r['parent'] or b
  if not (O/'final_oracle_results'/(parent+'.json')).exists():
   print('NO_VERIFIED_PARENT',b,parent,flush=True);continue
  print('PRICE_START',b,year,8000,'PARENT',parent,flush=True)
  x=subprocess.run([sys.executable,str(P/'price_8000.py'),b,str(year),'8000'],capture_output=True,text=True,env=os.environ.copy());print('PRICE_END',b,year,8000,x.returncode,(x.stdout or x.stderr)[-240:],flush=True)
