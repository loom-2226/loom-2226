"""PR427-only table-backed Arm A. Gate old 25 before recovered pricing."""
import argparse,csv,gc,hashlib,json,os,resource,time
from datetime import date,timedelta
from decimal import Decimal as D
from pathlib import Path
import numpy as np
from simulation.offworld_mvp.build8.three_arm_stage1 import pair_pricing as pp
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel,digest as filehash
from simulation.offworld_mvp.build8.three_arm_stage1.recovered_phase4e_registry import recovered_registry,test_only_run_identity
from simulation.offworld_mvp.build8.travel_pilot.pilot import _iso

P=Path(__file__).resolve().parent;E=json.loads((P/'experiment.json').read_text());C=json.loads((P/'table_arm_a_config.json').read_text())
OLD=P/C['table_manifest_file'];NEW=P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json'
CHECK=P/'RECOVERED_ARM_A_TABLE_CHECKPOINT_TEST_ONLY.json'
CSV=P/'RECOVERED_ARM_A_TABLE_PAIRS_TEST_ONLY.csv';REPORT=P/'RECOVERED_ARM_A_TABLE_REPORT_TEST_ONLY.json'
OLD_CSV=P/'A_VEHICLE_MISSION_PAIRS.csv'
BASE=Path(C['output_root'])/'A_CHECKPOINT_refined_previous.json'
PAIRS=pp.pairs(E)
FIELDS=['year','body','vehicle_class_id','mission_type_id','status','lowest_price_usd','best_departure_date','best_flight_days','departures_searched','run_identity','needed_departure_speed_km_s','departure_limit_km_s','needed_arrival_speed_km_s','arrival_limit_km_s','binding_limit','classification']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def peak():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def atomic(path,data):
 tmp=path.with_suffix('.pending.json');tmp.write_text(json.dumps(data,indent=2,sort_keys=True,default=str)+'\n');os.replace(tmp,path)
def departure_dates(year):
 start=date(year,1,1);end=date(year+1,1,1);step=E['sampling']['stride_days'];days=[];d=start
 while d<end:days.append(d.isoformat());d+=timedelta(days=step)
 if E['sampling']['include_last_day'] and days[-1]!=(end-timedelta(days=1)).isoformat():days.append((end-timedelta(days=1)).isoformat())
 return days
def refine(coarse,entries,mission):
 flags=[entries[d][mission]['price'] is not None for d in coarse]
 brackets=[(a,b) for a,b,fa,fb in zip(coarse,coarse[1:],flags,flags[1:]) if fa!=fb]
 dates=[]
 for a,b in brackets[:E['sampling']['max_transition_brackets_per_body_year']]:
  d=date.fromisoformat(a)+timedelta(days=E['sampling']['refinement_step_days'])
  while d<date.fromisoformat(b):dates.append(d.isoformat());d+=timedelta(days=E['sampling']['refinement_step_days'])
 return dates
def summarize(year,body,entries,identity):
 result=[]
 for vehicle,mission in PAIRS:
  m=mission['mission_type_id']
  priced=[(D(x[m]['price']),day,x[m]) for day,x in entries.items() if x[m]['price'] is not None]
  best=min(priced,key=lambda z:(z[0],z[1],z[2]['flight_days'])) if priced else None
  # Find minimum departure speed and minimum arrival speed independently.
  routes=[r for x in entries.values() for r in x['routes']]
  dep=min((float(r['departure_vinf_km_s']) for r in routes),default=None)
  arr=min((float(r['arrival_vinf_km_s']) for r in routes),default=None)
  dl=float(vehicle['departure_limit_km_s']);al=float(vehicle['arrival_limit_km_s'])
  dep_violation=dep is not None and dep>dl
  arr_violation=arr is not None and arr>al and mission['enforce_arrival_limit']
  if best:binding='NONE'
  elif not routes:binding='NO_SAMPLED_TRANSFER'
  elif dep_violation and arr_violation:binding='DEPARTURE_AND_ARRIVAL_SPEED'
  elif dep_violation:binding='DEPARTURE_SPEED'
  elif arr_violation:binding='ARRIVAL_SPEED'
  else:binding='COUPLED_SPEED_LIMITS_OR_CALIBRATION; NO_SINGLE_LIMIT_PROVEN'
  result.append({'year':year,'body':body,'vehicle_class_id':vehicle['class_id'],'mission_type_id':m,'status':'PRICED_TEST_ONLY' if best else 'INFEASIBLE' if routes else 'UNPRICED','lowest_price_usd':str(best[0]*D(1000000)) if best else '','best_departure_date':best[1] if best else '','best_flight_days':best[2]['flight_days'] if best else '','departures_searched':len(entries),'run_identity':identity,'needed_departure_speed_km_s':dep if dep is not None else '','departure_limit_km_s':dl,'needed_arrival_speed_km_s':arr if arr is not None else '','arrival_limit_km_s':al if mission['enforce_arrival_limit'] else 'NOT_ENFORCED','binding_limit':binding,'classification':'RECOVERED_VINTAGE_TEST_ONLY'})
 return result
class CombinedTable:
 def __init__(self):
  self.old=TableTravel(E['asset_root'],OLD)
  self.new=json.loads(NEW.read_text())
  self.registry=recovered_registry(E['asset_root'])
  self.old.travel.adapter.registry=self.registry
  self._original=self.old._batch_states
  self.old.travel._batch_states=self._states
  self.arrays={}
 def _states(self,body,epochs):
  if body not in self.new['tables']:return self._original(body,epochs)
  entry=self.new['tables'][body];root=Path(self.new['table_root']);file=root/(body+'.npy')
  if body not in self.arrays:
   assert sha(file)==entry['sha256'],'RECOVERED_TABLE_HASH_MISMATCH:'+body
   self.arrays[body]=np.load(file,mmap_mode='r')
  src,cov=self.registry.source_for(body,_iso(epochs[0]))
  assert src.sha256==entry['source_sha256'],'RECOVERED_SOURCE_HASH_MISMATCH:'+body
  first=date.fromisoformat(self.new['first'][:10]);step=self.new['step_days']*86400
  from datetime import datetime,timezone
  first_dt=datetime.fromisoformat(self.new['first'].replace('Z','+00:00'))
  idx=[]
  for epoch in epochs:
   tick=(epoch-first_dt).total_seconds()/step;i=round(tick)
   if i<0 or i>=len(self.arrays[body]) or abs(tick-i)>1e-9:raise ValueError('RECOVERED_OFF_LATTICE:'+body+':'+_iso(epoch))
   idx.append(i)
  return np.asarray(self.arrays[body][idx]),src,cov
 def geometry(self,*args,**kwargs):return self.old.geometry(*args,**kwargs)
 def clear(self):
  self.old.travel._geometry.clear();self.old.travel._state_cache.clear();gc.collect()
def main(smoke=False):
 begin=time.monotonic()
 assert not CSV.exists() and not REPORT.exists(),'OUTPUT_EXISTS'
 table=CombinedTable()
 runid={**test_only_run_identity(),'experiment_sha256':sha(P/'experiment.json'),'old_table_manifest_sha256':sha(OLD),'recovered_table_manifest_sha256':sha(NEW),'old_pairs_sha256':sha(OLD_CSV),'old_checkpoint_sha256':sha(BASE),'runner_sha256':sha(Path(__file__)),'mode':'ARM_A_TABLE_25_REGRESSION_THEN_34_RECOVERED'}
 ident=digest(runid)
 checkpoint=json.loads(CHECK.read_text()) if CHECK.exists() else {'identity':ident,'regression':{},'recovered':{},'classification':'TEST_ONLY'}
 assert checkpoint['identity']==ident,'CHECKPOINT_IDENTITY_MISMATCH'
 original={(int(r['year']),r['body'],r['mission_type_id']):r for r in csv.DictReader(OLD_CSV.open())}
 old=json.loads(BASE.read_text())['completed'];recovered=[r['body'] for r in json.loads((P/'PHASE4E_RECOVERY_34_TEST_ONLY_MANIFEST.json').read_text())['files']]
 assert len(original)==100 and len(old)==50 and len(recovered)==34
 for key,record in sorted(old.items()):
  if key in checkpoint['regression']:continue
  year,body=key.split('|');entries={};hash_count=0
  for day,prior in sorted(record['dates'].items()):
   geo=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
   actual=digest(geo)
   if actual!=prior['geometry_sha256']:
    atomic(REPORT,{'status':'STOP_REGRESSION_GEOMETRY_DIFFERENCE','body':body,'year':year,'day':day,'expected':prior['geometry_sha256'],'actual':actual,'run_identity':runid,'elapsed_seconds':time.monotonic()-begin,'peak_rss_bytes':peak()})
    raise RuntimeError('STOP_REGRESSION_GEOMETRY_DIFFERENCE:'+key+':'+day)
   hash_count+=1
   entries[day]={m['mission_type_id']:pp.evaluate(geo,v,m,E) for v,m in PAIRS}
   entries[day]['routes']=geo['trajectories']
   table.clear()
  rows=summarize(int(year),body,entries,ident);differences=[]
  for row in rows:
   prior=original[(int(year),body,row['mission_type_id'])]
   for field in ('status','lowest_price_usd','best_departure_date','best_flight_days','departures_searched'):
    a=str(prior[field]);b=str(row[field]);match=D(a)==D(b) if field=='lowest_price_usd' and a and b else a==b
    if not match:differences.append({'body':body,'year':year,'mission':row['mission_type_id'],'field':field,'expected':a,'actual':b})
  if differences:
   atomic(REPORT,{'status':'STOP_REGRESSION_DIFFERENCE','differences':differences,'run_identity':runid,'elapsed_seconds':time.monotonic()-begin,'peak_rss_bytes':peak()})
   raise RuntimeError('STOP_REGRESSION_DIFFERENCE:'+key)
  checkpoint['regression'][key]={'rows':rows,'hashes_verified':hash_count};atomic(CHECK,checkpoint)
  print('REGRESSION_PASS',key,'HASHES',hash_count,'ELAPSED',round(time.monotonic()-begin,2),flush=True)
  if smoke:
   print('SMOKE_FIRST_BODY_COMPLETE',key,flush=True);return
 if smoke:
  print('SMOKE_RESUME_SKIPPED_COMPLETE',len(checkpoint['regression']),flush=True);return
 print('GATE_25_PASS',len(checkpoint['regression']),'BODY_YEARS',flush=True)
 for year in E['years']:
  for body in recovered:
   key=f'{year}|{body}'
   if key in checkpoint['recovered']:continue
   entries={};coarse=departure_dates(year)
   for phase in ('coarse','refined'):
    days=coarse if phase=='coarse' else sorted(set(refine(coarse,entries,'rendezvous')+refine(coarse,entries,'flyby')))
    for day in days:
     if day in entries:continue
     try:geo=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
     except (ValueError,KeyError,RuntimeError) as exc:
      if 'UNKNOWN_EPHEMERIS_MISSING' in str(exc) or 'OFF_LATTICE' in str(exc) or 'UNQUALIFIED' in str(exc):
       print('RECOVERED_WINDOW_EXCLUDED',key,day,str(exc),flush=True);continue
      raise
     entries[day]={m['mission_type_id']:pp.evaluate(geo,v,m,E) for v,m in PAIRS}
     entries[day]['routes']=geo['trajectories']
     table.clear()
   rows=summarize(year,body,entries,ident)
   checkpoint['recovered'][key]={'rows':rows,'departures':len(entries)}
   atomic(CHECK,checkpoint)
   print('RECOVERED_PASS',key,'DEPARTURES',len(entries),'STATUSES',[r['status'] for r in rows],'ELAPSED',round(time.monotonic()-begin,2),flush=True)
 rows=[r for key in sorted(checkpoint['recovered']) for r in checkpoint['recovered'][key]['rows']]
 assert len(rows)==34*2*2
 with CSV.open('x',newline='') as h:
  w=csv.DictWriter(h,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 report={'status':'COMPLETE_TEST_ONLY','run_identity':runid,'identity':ident,'regression':{'body_years':len(checkpoint['regression']),'geometry_hashes_verified':sum(x['hashes_verified'] for x in checkpoint['regression'].values()),'differences':[],'original_bodies':25},'recovered':{'body_years':len(checkpoint['recovered']),'pairs':len(rows),'status_counts':{s:sum(r['status']==s for r in rows) for s in ('PRICED_TEST_ONLY','INFEASIBLE','UNPRICED')},'per_body':rows},'elapsed_seconds':time.monotonic()-begin,'peak_rss_bytes':peak(),'csv_sha256':sha(CSV)}
 atomic(REPORT,report);print('COMPLETE',json.dumps({'elapsed_seconds':report['elapsed_seconds'],'peak_rss_bytes':peak(),'status_counts':report['recovered']['status_counts'],'csv_sha256':sha(CSV)}),flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--smoke',action='store_true');args=parser.parse_args();main(args.smoke)
