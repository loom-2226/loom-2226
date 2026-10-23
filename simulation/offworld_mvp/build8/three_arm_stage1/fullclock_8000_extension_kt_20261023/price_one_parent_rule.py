"""All-body, year/limit rendezvous pricing using only verified 2057 tables."""
import sys,csv,json,hashlib,gc,time
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal as D
import numpy as np
from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
from simulation.offworld_mvp.build8.three_arm_stage1.rendezvous_decimal_fallback_test_only import rendezvous
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel
from simulation.offworld_mvp.build8.three_arm_stage1.recovered_phase4e_registry import recovered_registry
P=Path(__file__).resolve().parent;S=P.parent;body=sys.argv[1];year=int(sys.argv[2]);limit=int(sys.argv[3]);assert 2026<=year<=2035 and limit in (1400,3000,5000,8000)
rows={r['body']:r for r in csv.DictReader((S/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())};assert len(rows)==90;w=rows[body];parent=w['parent'] or body
results={x.stem:json.loads(x.read_text()) for x in (P/'results').glob('*.json')};oracle={x.stem:json.loads(x.read_text()) for x in (P/'final_oracle_results').glob('*.json')}
missing=[b for b in ('EARTH',parent) if b not in results or results[b]['status']!='PASS' or oracle.get(b,{}).get('status')!='PASS']
out={'body':body,'year':year,'limit_days':limit,'price_model_units':'','flight_days':'','arrival_braking_km_s':'','departure_date':'','status':'UNPRICED','missing_body':','.join(sorted(set(missing))),'missing_date':f'{year}-12-31+{limit}d','source':results.get(parent,{}).get('source','registered'),'parent_source_body':parent,'reason':''}
if body in ('DACTYL','SELAM'):out['reason']='EXCLUDED_NO_GRAVITY_VALUE';missing=[body]
elif missing:out['reason']='NO_VERIFIED_PARENT_POSITION_TABLE' if body not in ('DACTYL','SELAM') else 'EXCLUDED_NO_GRAVITY_VALUE'
else:
 vehicle=json.loads((S/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text());auth=json.loads((S/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json').read_text());table=TableTravel(base.E['asset_root'],base.OLD);table.travel.adapter.registry=recovered_registry(base.E['asset_root'])
 cache={};first=datetime(2026,1,1,tzinfo=timezone.utc);step=21600
 def states(b,epochs):
  if b not in cache:
   r=results[b];p=Path(r['table_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['table_sha256'];cache[b]=np.load(p,mmap_mode='r')
  a=cache[b];idx=[]
  for ep in epochs:
   t=(ep-first).total_seconds()/step;i=round(t)
   if i<0 or i>=len(a) or abs(t-i)>1e-9:raise ValueError('NO_DATA:'+b+':'+ep.isoformat())
   idx.append(i)
  src,cov=table.travel.adapter.registry.source_for(b,epochs[0].isoformat().replace('+00:00','Z'))
  return np.asarray(a[idx]),src,cov
 table.travel._batch_states=states
 best=None;start=time.monotonic()
 try:
  for day in base.departure_dates(year):
   g=table.geometry('EARTH',parent,day,strategy='daily',flight_range_days=[45.0,float(limit)])
   for route in g['trajectories']:
    moon=bool(w['parent']);params={**auth,'parent_gm_km3_s2':w['parent_gm_km3_s2'],'orbit_radius_km':w['orbit_radius_km']} if moon else auth
    q=rendezvous(float(route['departure_vinf_km_s']),float(route['arrival_vinf_km_s']),float(route['flight_days']),vehicle,params,moon=moon,body=body,year=year)
    candidate=(D(str(q['total_usd'])),day,float(route['flight_days']),q)
    if best is None or candidate[:3]<best[:3]:best=candidate
   table.travel._geometry.clear();table.travel._state_cache.clear();gc.collect()
  if best:
   value=best[0]/D(10**9);assert value>=D('0.7'),('FLOOR_FAIL',body,year,limit,str(value))
   out.update(status='PRICED',price_model_units=str(value),flight_days=str(best[2]),arrival_braking_km_s=str(best[3]['arrival_braking_delta_v_km_s']),departure_date=best[1],missing_body='',missing_date='')
  else:out['reason']='NO_SAMPLED_TRANSFER'
 except Exception as e:out.update(status='UNPRICED',reason=type(e).__name__+':'+str(e)[:250])
 out['elapsed_seconds']=round(time.monotonic()-start,3)
(P/'price_rows').mkdir(exist_ok=True);(P/'price_rows'/(f'{body}_{year}_{limit}.json')).write_text(json.dumps(out,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True),flush=True)
