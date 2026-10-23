import json,subprocess,sys,os
from pathlib import Path
P=Path(__file__).resolve().parent
for f in sorted((P/'results').glob('*.json')):
 r=json.loads(f.read_text());body=r['body']
 if r['status']=='PASS' or 'MISSING_REGISTERED_KERNEL' not in r.get('reason',''):continue
 kernel=Path('/home/ubuntu/LOOM-output/PHASE4E_RECOVERY_20261020')/(body.lower()+'_2026_2251.bsp')
 if not kernel.is_file():print('NO_RECOVERED',body,flush=True);continue
 print('RETRY',body,flush=True)
 x=subprocess.run([sys.executable,str(P/'build_recovered_manifest.py'),body],capture_output=True,text=True,env=os.environ.copy());print('DONE',body,x.returncode,(x.stdout or x.stderr)[-240:],flush=True)
