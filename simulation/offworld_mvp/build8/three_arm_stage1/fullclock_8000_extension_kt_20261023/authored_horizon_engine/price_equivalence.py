import subprocess,sys,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent
samples=['VENUS','TITAN','ERIS'];results=[]
for b in samples:
 x=subprocess.run([sys.executable,str(P/'price_8000.py'),b,'2026','1400'],capture_output=True,text=True)
 if x.returncode:raise RuntimeError((b,x.stderr[-600:]))
 old=json.loads((O/'price_rows'/(b+'_2026_1400.json')).read_text());new=json.loads((P/'price_rows_8000'/(b+'_2026_1400.json')).read_text())
 keys=['status','price_model_units','flight_days','arrival_braking_km_s','departure_date','reason'];left={k:old.get(k) for k in keys};right={k:new.get(k) for k in keys};h=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest();r={'body':b,'old_sha256':h(left),'copy_sha256':h(right),'equal':h(left)==h(right)}
 if not r['equal']:r['first_difference']=next(({'field':k,'old':left[k],'copy':right[k]} for k in keys if left[k]!=right[k]),None)
 results.append(r);print(json.dumps(r),flush=True)
(P/'price_equivalence.json').write_text(json.dumps(results,indent=2)+'\n')
