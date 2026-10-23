"""One checker process at a time, fail closed and preserve reason."""
import sys,json,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parent;(P/'oracle_results').mkdir(exist_ok=True)
for f in sorted((P/'results').glob('*.json')):
 r=json.loads(f.read_text());body=r['body'];dest=P/'oracle_results'/(body+'.json')
 if dest.exists():continue
 if r['status']!='PASS':dest.write_text(json.dumps({'body':body,'status':'EXCLUDED','reason':r.get('reason','')})+'\n');continue
 v=subprocess.run([sys.executable,str(P/'independent_check_one.py'),body],capture_output=True,text=True,env=os.environ.copy());result=json.loads(v.stdout) if v.returncode==0 else {'body':body,'status':'FAIL','reason':v.stderr[-500:]};dest.write_text(json.dumps(result,indent=2)+'\n');print('ORACLE',body,result['status'],flush=True)
