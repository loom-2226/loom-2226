import csv,json,subprocess,sys,os
from pathlib import Path
P=Path(__file__).resolve().parent;w=list(csv.DictReader((P.parent/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open()));parents=sorted({x['parent'] for x in w if x['parent']});print('PARENTS',parents,flush=True)
for b in parents:
 r=P/'results'/(b+'.json');o=P/'final_oracle_results'/(b+'.json')
 if not r.exists():
  print('BUILD_PARENT',b,flush=True);x=subprocess.run([sys.executable,str(P/'build_one.py'),b],capture_output=True,text=True,env=os.environ.copy());print('BUILT',b,x.returncode,(x.stdout or x.stderr)[-220:],flush=True)
 if r.exists() and json.loads(r.read_text())['status']=='PASS' and not o.exists():
  x=subprocess.run([sys.executable,str(P/'independent_check_one.py'),b],capture_output=True,text=True,env=os.environ.copy());o.write_text(x.stdout if x.returncode==0 else json.dumps({'body':b,'status':'FAIL','reason':x.stderr[-350:]}));print('CHECKED',b,x.returncode,flush=True)
