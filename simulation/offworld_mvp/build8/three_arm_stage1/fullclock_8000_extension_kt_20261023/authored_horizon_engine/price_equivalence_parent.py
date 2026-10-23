"""Compare same approved parent rule, original vs copied grid, exact quote hash."""
import subprocess,sys,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;O=P.parent;results=[]
for b in ('VENUS','TITAN','ERIS'):
 for limit in (1400,3000,5000):
  original=O/'parent_corrected_price_rows'/(f'{b}_2026_{limit}.json') if b=='TITAN' else O/'price_rows'/(f'{b}_2026_{limit}.json')
  if not original.exists():
   x=subprocess.run([sys.executable,str(O/'price_one_parent_corrected.py'),b,'2026',str(limit)],capture_output=True,text=True)
   if x.returncode:raise RuntimeError(('ORIGINAL',b,limit,x.stderr[-500:]))
  x=subprocess.run([sys.executable,str(P/'price_8000.py'),b,'2026',str(limit)],capture_output=True,text=True)
  if x.returncode:raise RuntimeError(('COPY',b,limit,x.stderr[-500:]))
  old=json.loads(original.read_text());new=json.loads((P/'price_rows_8000'/(f'{b}_2026_{limit}.json')).read_text());keys=['status','price_model_units','flight_days','arrival_braking_km_s','departure_date','reason'];left={k:old.get(k) for k in keys};right={k:new.get(k) for k in keys};h=lambda a:hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest();r={'body':b,'limit_days':limit,'old_sha256':h(left),'copy_sha256':h(right),'equal':h(left)==h(right)}
  if not r['equal']:r['first_difference']=next(({'field':k,'old':left[k],'copy':right[k]} for k in keys if left[k]!=right[k]),None)
  results.append(r);print(json.dumps(r),flush=True)
  (P/'price_equivalence_parent.json').write_text(json.dumps(results,indent=2)+'\n')
