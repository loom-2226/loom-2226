"""Direct table-backed giant planet flyby geometry; original sampling/refinement."""
import csv,json,time,resource,hashlib
from pathlib import Path
from datetime import date,timedelta
from decimal import Decimal
import numpy as np
from simulation.offworld_mvp.build8.three_arm_stage1.run_recovered_tables_arm_a_test_only import CombinedTable
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
P=Path(__file__).resolve().parent
M=json.loads((P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json').read_text())
F=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text())
E=json.loads((P/'experiment.json').read_text())
OUT=P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 t=time.monotonic();assert not OUT.exists()
 tab=CombinedTable()
 def states(body,epochs):
  if body not in M['tables']:return tab._states_original(body,epochs)
  row=M['tables'][body]
  if body not in arrays:
   path=Path(M['table_root'])/(body+'.npy');assert sha(path)==row['table_sha256'];arrays[body]=np.load(path,mmap_mode='r')
  first=__import__('datetime').datetime.fromisoformat(M['first'].replace('Z','+00:00'))
  ix=[]
  for ep in epochs:
   tick=(ep-first).total_seconds()/(M['step_days']*86400);i=round(tick)
   assert 0<=i<len(arrays[body]) and abs(tick-i)<1e-9,('OFF_LATTICE',body,str(ep))
   ix.append(i)
  source,_=tab.registry.source_for(body,epochs[0].isoformat().replace('+00:00','Z'))
  assert source.sha256==row['source_sha256']
  return np.asarray(arrays[body][ix]),source,None
 arrays={}
 tab._states_original=tab.old.travel._batch_states
 tab.old.travel._batch_states=states
 output=[]
 for year in (2026,2027):
  for body in ('JUPITER','SATURN','URANUS','NEPTUNE'):
   dates=base.departure_dates(year);res={};count=0
   def calc(day):
    nonlocal count
    g=tab.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
    routes=g['trajectories'];count+=1
    best=min((float(x['departure_vinf_km_s']) for x in routes),default=None)
    res[day]={'best':best,'feasible':best is not None and best<=10,'trajectories':len(routes)}
    tab.clear()
   for day in dates:calc(day)
   flags=[res[d]['feasible'] for d in dates]
   brackets=[(a,b) for a,b,fa,fb in zip(dates,dates[1:],flags,flags[1:]) if fa!=fb]
   extra=set()
   for a,b in brackets[:E['sampling']['max_transition_brackets_per_body_year']]:
    d=date.fromisoformat(a)+timedelta(days=E['sampling']['refinement_step_days'])
    while d<date.fromisoformat(b):
     extra.add(d.isoformat());d+=timedelta(days=E['sampling']['refinement_step_days'])
   for day in sorted(extra-set(dates)):calc(day)
   choices=[(v['best'],day) for day,v in res.items() if v['best'] is not None]
   best,day=min(choices) if choices else (None,None)
   output.append({'year':year,'body':body,'departures':count,'sampled_trajectories':sum(v['trajectories'] for v in res.values()),'best_departure_vinf_km_s':best,'best_departure_date':day,'model_units':price(best,F)['model_units'] if best is not None else None,'reason':None if best is not None else 'NO_SAMPLED_TRANSFER'})
   print('GEOMETRY',year,body,'DEPARTURES',count,'MIN',best,'ELAPSED',time.monotonic()-t,flush=True)
 report={'classification':'TEST_ONLY_NONCANON','table_manifest_sha256':sha(P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json'),'body_years':output,'elapsed_seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 with OUT.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('DONE',sha(OUT),report['elapsed_seconds'],report['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
