import csv,json,time,hashlib,gc,os
from pathlib import Path
from decimal import Decimal as D
from simulation.offworld_mvp.build8.three_arm_stage1 import pair_pricing as pp
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel,digest
P=Path(__file__).resolve().parent;E=json.loads((P/'experiment.json').read_text());C=json.loads((P/'table_arm_a_config.json').read_text());O=Path(C['output_root']);G=json.loads((O/'gate.json').read_text());assert G['status']=='PASS' and G['completed_count']==1202 and G['table_manifest_sha256']==C['table_manifest_sha256'];assert digest(P/C['table_manifest_file'])==C['table_manifest_sha256'];print('GATE_REUSED',G['completed_count'],flush=True)
old=json.loads((O/'A_CHECKPOINT_refined_previous.json').read_text());baseline={ (r['year'],r['body']):r for r in csv.DictReader((P/'A_BODY_YEAR_REPORT_LIMITS.csv').open())};pairs=pp.pairs(E);assert len(pairs)==2;requested=os.environ['LOOM_PAIR'];pairs=[(v,m) for v,m in pairs if m['mission_type_id']==requested];assert len(pairs)==1
id=pp.identity(E,C['table_manifest_sha256'],digest(P/'table_arm_a_config.json'));print('PAIR_IDENTITY',id,flush=True)
table=TableTravel(E['asset_root'],P/C['table_manifest_file']);out=O/'pair_run';out.mkdir(exist_ok=True);state={};peak=0;start=time.monotonic();n=0
for key,entry in sorted(old['completed'].items()):
 year,body=key.split('|');data={m['mission_type_id']:[] for _,m in pairs}
 for day in sorted(entry['dates']):
  g=table.geometry(E['origin'],body,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
  for v,m in pairs:data[m['mission_type_id']].append((day,pp.evaluate(g,v,m,E)))
  del g;table.travel._geometry.clear();table.travel._state_cache.clear();gc.collect();n+=1
  rss=int(Path('/proc/self/status').read_text().split('VmRSS:')[1].split('kB')[0].strip())*1024;peak=max(peak,rss)
  if rss>C['process_memory_limit_gib']*1024**3:raise RuntimeError('MEMORY_LIMIT')
 for v,m in pairs:
  entries=data[m['mission_type_id']];priced=[(D(r['price']),day,r) for day,r in entries if r['price'] is not None];best=min(priced,key=lambda t:(t[0],t[1],t[2]['flight_days'])) if priced else None
  row={'year':year,'body':body,'vehicle_class_id':v['class_id'],'mission_type_id':m['mission_type_id'],'status':'PRICED_TEST_ONLY' if best else 'INFEASIBLE','lowest_price_usd':str(best[0]*1000000) if best else '', 'best_departure_date':best[1] if best else '', 'best_flight_days':best[2]['flight_days'] if best else '', 'departures_searched':len(entries),'run_identity':id}
  if (v['class_id'],m['mission_type_id'])==(E['regression_reference_pair']['vehicle_class_id'],E['regression_reference_pair']['mission_type_id']):
   prior=baseline[(year,body)];assert row['status']==('PRICED_TEST_ONLY' if prior['feasible']=='YES' else 'INFEASIBLE'),(key,'status');assert (D(row['lowest_price_usd']) if best else None)==(D(prior['lowest_price_usd']) if prior['lowest_price_usd'] else None),(key,'price',row['lowest_price_usd'],prior['lowest_price_usd'])
  state[(year,body,m['mission_type_id'])]=row
 print('BODY_YEAR_PASS',key,'departures',len(entry['dates']),'total',n,flush=True)
for v,m in pairs:
 rows=[r for k,r in sorted(state.items()) if k[2]==m['mission_type_id']];f=out/(m['mission_type_id']+'.csv')
 with f.open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('CSV',m['mission_type_id'],hashlib.sha256(f.read_bytes()).hexdigest(),flush=True)
assert n==sum(len(v['dates']) for v in old['completed'].values())
with (out/'report.json').open('w') as h:json.dump({'identity':id,'gate_reused':True,'departures':n,'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':peak,'pairs':len(pairs),'pair':requested},h,indent=2)
print('COMPLETE',json.dumps(json.load((out/'report.json').open())),flush=True)
