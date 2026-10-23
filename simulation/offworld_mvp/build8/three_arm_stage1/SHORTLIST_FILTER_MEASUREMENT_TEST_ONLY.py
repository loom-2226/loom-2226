"""PR427 new-file-only table-backed controlled counterfactual. No existing code edits."""
import csv,gc,hashlib,json,math,os,resource,time
from datetime import date,timedelta,datetime,timezone
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1 import pair_pricing as pp
from simulation.offworld_mvp.build8.three_arm_stage1.table_adapter import TableTravel
P=Path(__file__).resolve().parent
E=json.loads((P/'experiment.json').read_text()); C=json.loads((P/'table_arm_a_config.json').read_text())
REF=P/'A_VEHICLE_MISSION_PAIRS.csv'; CHECK=Path(C['output_root'])/'A_CHECKPOINT_refined_previous.json'; MAN=P/C['table_manifest_file']
OUTPUT=P/'SHORTLIST_FILTER_MEASUREMENT_REPORT_TEST_ONLY.json';DETAIL=P/'SHORTLIST_FILTER_DIFFERENCES_TEST_ONLY.csv'
FIELDS=['year','body','mission_type_id','field','authored','filter_off','difference_usd']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def rss():return int(Path('/proc/self/status').read_text().split('VmRSS:')[1].split('kB')[0])*1024
def run():
 assert not OUTPUT.exists() and not DETAIL.exists(),'NO_OVERWRITE'
 assert sha(MAN)==C['table_manifest_sha256'],'TABLE_MANIFEST_CHANGED'
 prior=json.loads(CHECK.read_text())['completed'];reference={(int(x['year']),x['body'],x['mission_type_id']):x for x in csv.DictReader(REF.open())}
 assert len(prior)==50 and len(reference)==100
 bodies=sorted({k.split('|')[1] for k in prior});years=E['years'];assert len(bodies)==25 and years==[2026,2027]
 # The source four-arm program applies B and C to other arms, never A.
 # Here the requested 'as authored' condition is the actual Arm A (filter absent),
 # and the explicit toggle-on condition is a counterfactual C cheap-cost top 8.
 from simulation.offworld_mvp.build8.travel_pilot.on_demand import OnDemandTravel
 source=OnDemandTravel(asset_root=Path(E['asset_root']))
 rank={}
 for y in years:
  epoch=datetime(y,1,1,tzinfo=timezone.utc);origin,_=source._state(E['origin'],epoch);r0=math.dist(origin.position_km,(0,0,0));vals={}
  for b in bodies:
   s,_=source._state(b,epoch);vals[b]=abs(math.dist(s.position_km,(0,0,0))-r0)
  rank[str(y)]=sorted(bodies,key=lambda b:(vals[b],b))
 authored={'filter':'OFF_AS_AUTHORED_ARM_A','cheap_cost_count':E['cheap_cost_count'],'shortlist_count':E['shortlist_count'],'heuristic':E['cheap_cost_rule'],'counterfactual':'C_CHEAP_COST_TOP_8_APPLIED_TO_ARM_A','years':years,'bodies':bodies,'table_path':'TABLE_ONLY','mission_types':E['selected_mission_types']}
 pins={str(p):sha(p) for p in (P/'experiment.json',P/'run.py',P/'pair_pricing.py',P/'table_adapter.py',P/'table_arm_a_config.json',MAN,CHECK,REF,Path(__file__))}
 ident=digest({'authored':authored,'source_sha256':pins,'table_binaries_sha256':json.loads(MAN.read_text())['tables']})
 print('AUTHORED_INPUT',json.dumps(authored,sort_keys=True),'AUTHORED_SHA256',digest(authored),'RUN_IDENTITY',ident,flush=True)
 table=TableTravel(E['asset_root'],MAN);pairs=pp.pairs(E);assert len(pairs)==2
 results={};stats={};hashes={}
 for label,enabled in [('AS_AUTHORED_ARM_A',False),('FILTER_ON_CHEAP_COST_8',True)]:
  started=time.monotonic();peak=rss();out={};verified=0
  for y in years:
   chosen=set(rank[str(y)][:E['cheap_cost_count']]) if enabled else set(bodies)
   for b in bodies:
    key=f'{y}|{b}'
    if b not in chosen:
     for v,m in pairs:out[(y,b,m['mission_type_id'])]={'status':'NOT_EVALUATED_FILTERED','lowest_price_usd':'','best_departure_date':'','best_flight_days':''}
     continue
    entries={}
    for day,old in sorted(prior[key]['dates'].items()):
     geo=table.geometry(E['origin'],b,day,strategy=E['sampling']['strategy'],flight_range_days=E['sampling']['flight_range_days'])
     actual=digest(geo)
     if actual!=old['geometry_sha256']:raise AssertionError('GEOMETRY_HASH_MISMATCH:'+key+':'+day)
     verified+=1
     for v,m in pairs:entries.setdefault(m['mission_type_id'],[]).append((day,pp.evaluate(geo,v,m,E)))
     table.travel._geometry.clear();table.travel._state_cache.clear();gc.collect()
     peak=max(peak,rss())
    for v,m in pairs:
     name=m['mission_type_id'];choices=[(D(r['price'])*D(1000000),day,r['flight_days']) for day,r in entries[name] if r['price'] is not None]
     best=min(choices,key=lambda x:(x[0],x[1],x[2])) if choices else None
     out[(y,b,name)]={'status':'PRICED_TEST_ONLY' if best else 'INFEASIBLE','lowest_price_usd':str(best[0]) if best else '', 'best_departure_date':best[1] if best else '', 'best_flight_days':str(best[2]) if best else ''}
    print('BODY',label,key,'GEOMETRIES',len(prior[key]['dates']),flush=True)
  seconds=time.monotonic()-started
  results[label]=out;stats[label]={'elapsed_seconds':seconds,'peak_rss_bytes':peak,'geometry_hashes_verified':verified,'body_years_evaluated':sum(len(rank[str(y)][:E['cheap_cost_count']]) if enabled else len(bodies) for y in years)}
  print('MODE_DONE',label,stats[label],flush=True)
 differences=[];legacy=[]
 for k,a in results['AS_AUTHORED_ARM_A'].items():
  old=reference[k]
  for f in ('status','lowest_price_usd','best_departure_date','best_flight_days'):
   if str(a[f])!=str(old[f]) and not (f=='lowest_price_usd' and a[f] and old[f] and D(a[f])==D(old[f])):legacy.append({'key':k,'field':f,'computed':a[f],'reference':old[f]})
  b=results['FILTER_ON_CHEAP_COST_8'][k]
  for f in ('status','lowest_price_usd','best_departure_date','best_flight_days'):
   if str(a[f])!=str(b[f]):differences.append({'year':k[0],'body':k[1],'mission_type_id':k[2],'field':f,'authored':a[f],'filter_off':b[f],'difference_usd':str(D(a[f])-D(b[f])) if f=='lowest_price_usd' and a[f] and b[f] else ''})
 if legacy:raise AssertionError('OLD_PAIRS_REGRESSION_MISMATCH:'+str(legacy[:3]))
 with DETAIL.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(differences)
 report={'classification':'TEST_ONLY_NONCANON_NONRUNTIME','interpretation':'Arm A has no shortlist; counterfactual applies C_CHEAP_COST top 8 to Arm A, not the reverse','authored_input':authored,'authored_sha256':digest(authored),'run_identity':ident,'source_hashes':pins,'table_manifest_sha256':sha(MAN),'selected_by_year':{str(y):rank[str(y)][:E['cheap_cost_count']] for y in years},'runs':stats,'legacy_regression_differences':legacy,'differences':differences,'difference_count':len(differences),'different_body_year_missions':len(set((x['year'],x['body'],x['mission_type_id']) for x in differences)),'difference_csv_sha256':sha(DETAIL),'comparison_note':'NOT_EVALUATED_FILTERED is missing price due to candidate suppression, not physical infeasibility; numeric price deltas are undefined when dropped'}
 OUTPUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print('COMPLETE',json.dumps({k:report[k] for k in ('run_identity','difference_count','different_body_year_missions','difference_csv_sha256')},sort_keys=True),flush=True)
if __name__=='__main__':run()
