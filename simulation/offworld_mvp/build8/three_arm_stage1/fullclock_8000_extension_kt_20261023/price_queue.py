"""Checkpointed all-body 2026-2035 × four-limit price jobs."""
import sys,json,csv,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent;world=list(csv.DictReader((S/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
for year in range(2026,2036):
 for limit in (1400,3000,5000,8000):
  for w in world:
   b=w['body'];dest=P/'price_rows'/(f'{b}_{year}_{limit}.json');q=P/'final_oracle_results'/(b+'.json')
   if dest.exists() or not q.exists():continue
   print('PRICE_START',year,limit,b,flush=True)
   x=subprocess.run([sys.executable,str(P/'price_one.py'),b,str(year),str(limit)],capture_output=True,text=True,env=os.environ.copy())
   print('PRICE_END',year,limit,b,'return',x.returncode,(x.stdout or x.stderr)[-260:],flush=True)
