"""Isolated process per body. Never loads two table arrays together."""
import csv,subprocess,sys,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=p.parent
names=[x['body'] for x in csv.DictReader((s/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())];assert len(names)==90
for i,body in enumerate(names,1):
 print('START',i,len(names),body,flush=True)
 r=subprocess.run([sys.executable,str(p/'build_one.py'),body],cwd=p.parents[4],env=__import__('os').environ.copy(),capture_output=True,text=True)
 if r.returncode:print('FAIL',body,r.returncode,r.stderr[-300:],flush=True)
 else:print('END',body,r.stdout[-260:],flush=True)
