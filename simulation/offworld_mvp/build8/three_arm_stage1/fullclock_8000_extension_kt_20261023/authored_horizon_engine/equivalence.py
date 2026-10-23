"""Exact bitwise test of copied grid vs original for every integer max <= 5000."""
import hashlib,json
from pathlib import Path
from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
from engine import AuthoredHorizonTravel
P=Path(__file__).resolve().parent
copy=AuthoredHorizonTravel(scenario_path=P/'scenario.json')
rows=[]
for step in (0.25,1.,10.,30.):
 for limit in range(46,5001):
  old=OnDemandTravel._times(step,[45.,float(limit)]);new=copy._times(step,[45.,float(limit)])
  a=json.dumps(old,separators=(',',':')).encode();b=json.dumps(new,separators=(',',':')).encode()
  if hashlib.sha256(a).digest()!=hashlib.sha256(b).digest():
   first=next(((i,x,y) for i,(x,y) in enumerate(zip(old,new)) if x!=y),None)
   raise AssertionError(('FIRST_DIFFERENCE',step,limit,first,len(old),len(new)))
  rows.append(hashlib.sha256(a).hexdigest())
r={'status':'PASS','comparison':'exact SHA256 of full flight-grid arrays, no tolerance','step_days':[0.25,1.,10.,30.],'limits_integer_days':'46..5000','comparisons':len(rows),'aggregate_sha256':hashlib.sha256(''.join(rows).encode()).hexdigest(),'scope_limit':'grid only, not yet price equivalence across sample bodies','scenario_sha256':copy.scenario_sha256}
(P/'equivalence_grid.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
