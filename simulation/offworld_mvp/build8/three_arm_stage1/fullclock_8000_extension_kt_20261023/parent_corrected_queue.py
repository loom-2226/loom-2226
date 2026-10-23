"""Wait for parent tables, then reprice moon rows without altering original rows."""
import sys,json,csv,subprocess,os,time
from pathlib import Path
P=Path(__file__).resolve().parent;world=list(csv.DictReader((P.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));parents=sorted({r['parent'] for r in world if r['parent']})
while any(not (P/'final_oracle_results'/(b+'.json')).exists() for b in parents):
 print('WAIT_PARENT_ORACLE',[(b) for b in parents if not (P/'final_oracle_results'/(b+'.json')).exists()],flush=True);time.sleep(120)
for year in range(2026,2036):
 for limit in (1400,3000,5000,8000):
  for w in world:
   body=w['body'];old=P/'price_rows'/(f'{body}_{year}_{limit}.json');new=P/'parent_corrected_price_rows'/(f'{body}_{year}_{limit}.json')
   if new.exists() or not w['parent']:continue
   if body in ('DACTYL','SELAM'):
    record={'body':body,'year':year,'limit_days':limit,'status':'EXCLUDED','reason':'NO_SOURCE_AND_NO_GRAVITY_VALUE','parent_source_body':w['parent']};new.parent.mkdir(exist_ok=True);new.write_text(json.dumps(record)+'\n');continue
   print('REPRICE_MOON',year,limit,body,'PARENT',w['parent'],flush=True)
   x=subprocess.run([sys.executable,str(P/'price_one_parent_corrected.py'),body,str(year),str(limit)],capture_output=True,text=True,env=os.environ.copy());print('RESULT',year,limit,body,x.returncode,(x.stdout or x.stderr)[-170:],flush=True)
