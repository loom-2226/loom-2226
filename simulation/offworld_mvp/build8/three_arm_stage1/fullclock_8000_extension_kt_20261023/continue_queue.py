"""Second one-body worker queue, skips completed, never duplicates active BENNU."""
import csv,subprocess,sys,json,os
from pathlib import Path
p=Path(__file__).resolve().parent;world=list(csv.DictReader((p.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));assert len(world)==90
for i,r in enumerate(world,1):
 b=r['body'];result=p/'results'/(b+'.json')
 if b=='BENNU' or result.exists():continue
 print('START',i,b,flush=True)
 cmd=[sys.executable,str(p/'build_one.py'),b]
 run=subprocess.run(cmd,cwd=p.parents[4],env=os.environ.copy(),capture_output=True,text=True)
 print('END',i,b,'return',run.returncode,(run.stdout or run.stderr)[-350:],flush=True)
