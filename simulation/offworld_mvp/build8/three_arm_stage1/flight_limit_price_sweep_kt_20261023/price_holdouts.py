"""TEST_ONLY cost-layer repricing, no campaign and no invented positions."""
import csv,hashlib,json,math,gc
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal as D
from pathlib import Path
import numpy as np
from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
from simulation.offworld_mvp.build8.three_arm_stage1.rendezvous_decimal_fallback_test_only import rendezvous
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import replay
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
P=Path(__file__).resolve().parent;S=P.parent;cfg=json.loads((P/'scenario.json').read_text());hold=list(csv.DictReader((S/'unstarted_33_readonly_audit_kt_20261023/unstarted_33.csv').open()));assert len(hold)==33
world={r['body']:r for r in csv.DictReader((S/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())}
vehicle=json.loads((S/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text());auth=json.loads((S/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json').read_text());clean=S/'clean_price_nine_case_kt_20261023/precedence_merged_prices.json';assert hashlib.sha256(clean.read_bytes()).hexdigest()==cfg['clean_price_sha256'];clean_rows=json.loads(clean.read_text())['matrix'];prices={r['body']:r for r in clean_rows if r['calendar_year']==2026 and r['mission_type']=='rendezvous'}
old={r['body']:r for r in csv.DictReader((S/'RENDEZVOUS_V2_PRICES_TEST_ONLY.csv').open()) if r['year']=='2026'};gi={r['body']:r for r in json.loads((S/'PR427_COMPLETE_MOON_GIANT_RENDEZVOUS_REPORT_TEST_ONLY.json').read_text())['giant_rendezvous'] if r['year']==2026}
num=json.loads((S/'PR427_ASSIST_2035_NUMERIC_TABLE_MANIFEST_TEST_ONLY.json').read_text());rec=json.loads((S/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json').read_text());num_first=datetime.fromisoformat(num['first'].replace('Z','+00:00'));num_last=datetime.fromisoformat(num['last'].replace('Z','+00:00'))
assert num['step_days']==0.25
out=[];rows_by_key={};floor=D(cfg['minimum_price_model_units']);table=base.CombinedTable();old_states=table.old.travel._batch_states;arrays={};sources={}
def get_states(body,epochs):
 if body not in num['tables']:return old_states(body,epochs)
 entry=num['tables'][body];path=Path(entry['table_path'])
 if body not in arrays:
  assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'];arrays[body]=np.load(path,mmap_mode='r')
  sources[body]=table.registry.source_for(body,epochs[0].isoformat().replace('+00:00','Z'))[0]
  assert sources[body].sha256==entry['source_sha256']
 idx=[]
 for ep in epochs:
  tick=(ep-num_first).total_seconds()/(num['step_days']*86400);i=round(tick)
  if i<0 or i>=len(arrays[body]) or abs(tick-i)>1e-9:raise ValueError('NO_DATA:'+body+':'+ep.isoformat())
  idx.append(i)
 return np.asarray(arrays[body][idx]),sources[body],None
table.old.travel._batch_states=get_states
for item in hold:
 body=item['body'];p=prices[body];src=gi.get(body) or old.get(body)
 for limit in cfg['flight_time_limits_days']:
  row={'body':body,'group':item['group'],'limit_days':limit,'status':'','price_model_units':'','flight_days':'','arrival_braking_km_s':'','departure_date':'','missing_position_body':'','missing_position_date':'','source':''}
  if limit==1400:
   if p['status']=='PRICED_TEST_ONLY' and src and src.get('flight_days'):
    row.update(status='PRICED_EXISTING_2026',price_model_units=p['selected_model_units'],flight_days=src['flight_days'],arrival_braking_km_s=src['arrival_braking_delta_v_km_s'],departure_date=src['departure_date'],source=p['selected_source']);assert D(row['price_model_units'])>=floor,(body,limit,row)
   else:row.update(status='UNPRICED_EXISTING',source=p['unpriced_reason'])
  else:
   parent=world[body]['parent'] or body
   # Complete horizon is required to compare prices at the authored limit.
   horizon=num_last if parent in num['tables'] else datetime.fromisoformat(rec['last'].replace('Z','+00:00')) if parent in rec['tables'] else None
   needed=datetime(2026,2,15,tzinfo=timezone.utc)+timedelta(days=limit)
   if horizon is None or needed>horizon:
    row.update(status='NO DATA',missing_position_body=parent,missing_position_date=needed.date().isoformat(),source='POSITION_TABLE_HORIZON_NOT_SUFFICIENT');
   elif world[body]['parent'] and (not world[body]['parent_gm_km3_s2'] or not world[body]['orbit_radius_km']):
    row.update(status='NO DATA',missing_position_body=body,missing_position_date=needed.date().isoformat(),source='LOCAL_MOON_PARAMETERS_MISSING')
   else:
    row.update(status='PENDING_GEOMETRY',source='COMPLETE_COST_LAYER')
  out.append(row);rows_by_key[(body,limit)]=row
# Reprice only where existing tables cover the whole limit, sharing parent geometry.
for limit in cfg['flight_time_limits_days']:
 if limit==1400:continue
 parents=sorted({world[x['body']]['parent'] or x['body'] for x in out if x['limit_days']==limit and x['status']=='PENDING_GEOMETRY'})
 for parent in parents:
  targets=[x for x in out if x['limit_days']==limit and x['status']=='PENDING_GEOMETRY' and (world[x['body']]['parent'] or x['body'])==parent]
  best={x['body']:None for x in targets};days=[x for x in base.departure_dates(2026) if x>='2026-02-15']
  for day in days:
   try:g=table.geometry('EARTH',parent,day,strategy='daily',flight_range_days=[45.0,float(limit)])
   except (ValueError,KeyError) as exc:
    for x in targets:x.update(status='NO DATA',missing_position_body=parent,missing_position_date=str(exc).split(':')[-1],source='POSITION_LOOKUP_FAILED')
    break
   for r in g['trajectories']:
    dep=float(r['departure_vinf_km_s']);arr=float(r['arrival_vinf_km_s']);flight=float(r['flight_days'])
    for x in targets:
     w=world[x['body']];moon=bool(w['parent']);params={**auth,'parent_gm_km3_s2':w['parent_gm_km3_s2'],'orbit_radius_km':w['orbit_radius_km']} if moon else auth
     q=rendezvous(dep,arr,flight,vehicle,params,moon=moon,body=x['body'],year=2026)
     candidate=(D(str(q['total_usd'])),day,flight,q)
     if best[x['body']] is None or candidate[:3]<best[x['body']][:3]:best[x['body']]=candidate
   table.clear()
   print('GEOMETRY',limit,parent,day,flush=True)
  for x in targets:
   if x['status']!='PENDING_GEOMETRY':continue
   b=best[x['body']]
   if b is None:x.update(status='NO_SAMPLED_TRANSFER');continue
   value=D(str(b[3]['total_usd']))/D(10**9)
   assert value>=floor,('FLOOR_FAILURE',x['body'],limit,str(value))
   x.update(status='PRICED_NEW',price_model_units=str(value),flight_days=str(b[2]),arrival_braking_km_s=str(b[3]['arrival_braking_delta_v_km_s']),departure_date=b[1])
with (P/'prices_33_by_limit.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
route1=replay(AllBodyCampaign(body_count=90,ceilings_enabled=True));assert route1=='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
summary={'scenario_sha256':hashlib.sha256((P/'scenario.json').read_bytes()).hexdigest(),'clean_price_sha256':cfg['clean_price_sha256'],'route1_hash':route1,'route1_pass':True,'rows':len(out),'priced_new':sum(x['status']=='PRICED_NEW' for x in out),'priced_baseline':sum(x['status']=='PRICED_EXISTING_2026' for x in out),'no_data':sum(x['status']=='NO DATA' for x in out),'no_campaign_run':True,'new_position_tables_built':0,'independent_new_table_checks':'NOT_APPLICABLE_NO_NEW_TABLES'}
(P/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print('SUMMARY',json.dumps(summary),flush=True)
