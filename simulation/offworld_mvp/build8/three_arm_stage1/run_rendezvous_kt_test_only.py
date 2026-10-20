"""PR427 one geometry pass; incremental durable outputs; test-only."""
import csv,hashlib,json,math,resource,time
from collections import Counter,defaultdict
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.three_arm_stage1 import run_recovered_tables_arm_a_test_only as base
from simulation.offworld_mvp.build8.three_arm_stage1 import rendezvous_cost_test_only as rv
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price as flyby
from simulation.offworld_mvp.build8.route1_body_campaign import SETTINGS
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign,ALL_BODIES
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash
P=Path(__file__).resolve().parent;ROOT=P.parents[3];F=P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json';A=P/'RENDEZVOUS_KT_AUTHORED_TEST_ONLY.json';W=P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv';G=P/'RENDEZVOUS_SAMPLED_DEPARTURES_TEST_ONLY.csv';PR=P/'RENDEZVOUS_PRICES_TEST_ONLY.csv';GR=P/'RENDEZVOUS_GEOMETRY_REPORT_TEST_ONLY.json';RR=P/'RENDEZVOUS_ROUTE1_REPORT_TEST_ONLY.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def peak():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def save(p,d):
 assert not p.exists();p.write_text(json.dumps(d,sort_keys=True,indent=2,default=str)+'\n')
def append(f,w,row):w.writerow(row);f.flush()
class CostCampaign(AllBodyCampaign):
 def __init__(self,prices,identity):super().__init__(body_count=90,ceilings_enabled=False);self.prices=prices;self.identity=identity
 def attempt(self,k,sponsor,body,stage,year,used=0):
  source='UNCHANGED_A2';old=SETTINGS['A1_SERVICE_PRICE']
  if stage=='A1':
   y=year if year in (2026,2027) else 2026;q=self.prices.get((y,body))
   if q is None:
    # Explicitly UNPRICED; never substitute an abstract service cost.
    balance=k.state.accounts['route1:budget:'+sponsor].balance
    row=dict(year=year,sponsor=sponsor,body=body,stage=stage,category=SETTINGS['A1_SERVICE_CATEGORY'],amount=None,balance_before=str(balance),ceiling_enabled=False,executor=None,outcome='BLOCKED',primary_blocker='UNPRICED_NO_PARENT_QUOTE_OR_PHYSICAL_PARAMETER',policy_reason=None,classification='KT_TEST_ONLY_NONCANON',price_source='UNPRICED')
    self.attempts.append(row);k.audit('BUILD8_CAMPAIGN_REQUEST',year,**{a:b for a,b in row.items() if a!='year'});return row
   source='RENDEZVOUS_COST_TABLE' if y==year else 'RENDEZVOUS_COST_HELD_2026';SETTINGS['A1_SERVICE_PRICE']=D(q['model_units'])
  try:row=super().attempt(k,sponsor,body,stage,year,used)
  finally:SETTINGS['A1_SERVICE_PRICE']=old
  row['price_source']=source
  if row['outcome']=='FUNDED':self.receipts[-1]['price_source']=source
  return row
 def limits(self):d=super().limits();d['rendezvous_run_identity']=self.identity;return d
 def report(self):d=super().report();d['rendezvous_run_identity']=self.identity;return d

def main():
 start=time.monotonic();a=json.loads(A.read_text());f=json.loads(F.read_text());assert sha(F)==a['parent_input_sha256'];world={r['body']:r for r in csv.DictReader(W.open())};assert len(world)==90
 oldprice=list(csv.DictReader((P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv').open()));oldgeom=list(csv.DictReader((P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv').open()));assert sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv')=='2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73'
 old={(int(r['year']),r['body']):r for r in oldgeom};assert len(old)==118
 source=[A,F,W,P/'RENDEZVOUS_WORLD_AUTHORITY_REPORT_TEST_ONLY.json',P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv',P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv',P/'experiment.json',P/'table_manifest.json',P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json',P/'RECOVERED_ARM_A_TABLE_CHECKPOINT_TEST_ONLY.json',P/'table_arm_a_config.json',P/'rendezvous_cost_test_only.py',P/'run_rendezvous_kt_test_only.py',ROOT/'src/loom_solar_gis.py',ROOT/'data/LOOM_2226.sqlite3']
 identity={'classification':'KT_RENDEZVOUS_TEST_ONLY_NONCANON','authored_input':a,'authored_input_sha256':sha(A),'parent_input':f,'parent_input_sha256':sha(F),'source_hashes':{str(x):sha(x) for x in source},'pricing':'COST_MINIMIZED_PER_SAMPLED_BODY_YEAR','flight_range':'UNCHANGED_45_1400','held_rule':'2026_AFTER_2027','moons':'PARENT_TRAJECTORY_BRaking_PARENT_MU_ORBIT_RADIUS_MOON_GRAVITY_IGNORED'};idh=digest(identity)
 print('INPUT',json.dumps(a,sort_keys=True),'INPUT_SHA',sha(A),'PARENT_SHA',sha(F),'RUN_IDENTITY',idh,flush=True)
 # Hand test includes independent fully shown arithmetic in report.
 hand=[]
 for dep,arr in [(10.,3.),(20.,5.)]:
  p=rv.rendezvous(dep,arr,365.25,f,a);hand.append({'departure_vinf':dep,'arrival_vinf':arr,'braking_delta_v':p['arrival_braking_delta_v_km_s'],'braking_stages':p['braking_stages'],'braking_stack_kg':p['braking_stack_mass_kg'],'departure_delta_v':p['departure_delta_v_km_s'],'departure_stages':p['departure_stages'],'leo_mass_kg':p['mass_in_leo_kg'],'launch_cost_usd':p['launch_cost_usd'],'fixed_cost_usd':a['rendezvous_fixed_mission_cost_usd'],'operating_cost_usd':p['operating_cost_usd'],'total_usd':p['total_usd']})
 print('HAND',json.dumps(hand),flush=True)
 assert hand[0]['braking_stages']==1
 # Parent orbit metadata exists for moons of Mars/Pluto; Earth/Jupiter/etc have no 59-body table quote.
 children=defaultdict(list)
 for b,w in world.items():
  if w['parent']:children[w['parent']].append(b)
 table=base.CombinedTable();oldcheck=json.loads((P/'RECOVERED_ARM_A_TABLE_CHECKPOINT_TEST_ONLY.json').read_text());oc=json.loads((Path(json.loads((P/'table_arm_a_config.json').read_text())['output_root'])/'A_CHECKPOINT_refined_previous.json').read_text())['completed']
 gfields=['year','body','departure_date','sampled_trajectories','min_departure_vinf_km_s','min_arrival_vinf_km_s','cost_min_departure_vinf_km_s','cost_min_arrival_vinf_km_s','cost_min_flight_days','cost_min_total_usd','run_identity']
 pfields=['year','body','status','parent','departure_date','flight_days','departure_vinf_km_s','arrival_vinf_km_s','departure_delta_v_km_s','arrival_braking_delta_v_km_s','departure_stages','braking_stages','braking_stack_mass_kg','mass_in_leo_kg','launch_cost_usd','operating_cost_usd','total_usd','model_units','flyby_price_usd','flyby_source','reason','run_identity']
 assert not G.exists() and not PR.exists()
 best={};count=0;trajectories=0;geo_start=time.monotonic();geometry_errors=[]
 with G.open('x',newline='') as gf,PR.open('x',newline='') as pf:
  gw=csv.DictWriter(gf,gfields,lineterminator='\n');pw=csv.DictWriter(pf,pfields,lineterminator='\n');gw.writeheader();pw.writeheader();gf.flush();pf.flush()
  for year in (2026,2027):
   for body in sorted({b for _,b in old}):
    key=f'{year}|{body}';original=key in oc;coarse=sorted(oc[key]['dates']) if original else base.departure_dates(year);dates=set(coarse);entries={};results={};candidate_children=[c for c in children.get(body,[]) if world[c]['orbit_radius_km'] and world[c]['parent_gm_km3_s2']]
    def do_day(day):
     nonlocal count,trajectories
     g=table.geometry(base.E['origin'],body,day,strategy=base.E['sampling']['strategy'],flight_range_days=base.E['sampling']['flight_range_days']);routes=g['trajectories'];count+=1;trajectories+=len(routes)
     if original:assert digest(g)==oc[key]['dates'][day]['geometry_sha256'],('GEOMETRY_HASH',key,day)
     lowest=None;mins=(float('inf'),float('inf'))
     for r in routes:
      dep=float(r['departure_vinf_km_s']);arr=float(r['arrival_vinf_km_s']);days=float(r['flight_days']);mins=(min(mins[0],dep),min(mins[1],arr))
      p=rv.rendezvous(dep,arr,days,f,a)
      if lowest is None or (p['total_usd'],day,days)<(lowest[0]['total_usd'],day,lowest[2]):lowest=(p,day,days)
      for child in candidate_children:
       w=world[child];q=rv.rendezvous(dep,arr,days,f,{**a,'parent_gm_km3_s2':w['parent_gm_km3_s2'],'orbit_radius_km':w['orbit_radius_km']},moon=True)
       k=(year,child);prior=best.get(k)
       if prior is None or (q['total_usd'],day,days)<(prior[0]['total_usd'],prior[1],prior[2]):best[k]=(q,day,days,body)
     if lowest:
      k=(year,body);prior=best.get(k)
      if prior is None or (lowest[0]['total_usd'],day,lowest[2])<(prior[0]['total_usd'],prior[1],prior[2]):best[k]=(*lowest,body)
     append(gf,gw,dict(year=year,body=body,departure_date=day,sampled_trajectories=len(routes),min_departure_vinf_km_s=repr(mins[0]) if routes else '',min_arrival_vinf_km_s=repr(mins[1]) if routes else '',cost_min_departure_vinf_km_s=repr(lowest[0]['departure_vinf_km_s']) if lowest else '',cost_min_arrival_vinf_km_s=repr(lowest[0]['arrival_vinf_km_s']) if lowest else '',cost_min_flight_days=repr(lowest[2]) if lowest else '',cost_min_total_usd=repr(lowest[0]['total_usd']) if lowest else '',run_identity=idh))
     entries[day]=min((r['departure_vinf_km_s'],r['arrival_vinf_km_s']) for r in routes) if routes else None
     table.clear()
    for day in coarse:do_day(day)
    if not original:
     # Recreate prior speed-limited transition refinements from the same geometry pass.
     # A date is feasible iff any sampled trajectory passes both authored old speed limits.
     # Feasibility booleans below require the full routes, not just independent minima.
     # Prior flyby runner used original pair_pricing evaluation on the coarse dates.
     # The prior saved recovered checkpoint has counts but not dates; this one-pass run
     # therefore uses the prior 2026/2027 best flyby date as an additional sample.
     oldbest=old[(year,body)]['best_departure_date']
     if oldbest and oldbest not in dates:dates.add(oldbest);do_day(oldbest)
     expected=oldcheck['recovered'][key]['departures']
     if len(dates)!=expected:geometry_errors.append({'body':body,'year':year,'previous_departures':expected,'this_departures':len(dates),'reason':'PRIOR_REFINED_DATES_NOT_SAVED; ONE_PASS_NO_INVENTED_DATES'})
    for target in [body]+children.get(body,[]):
     w=world[target];k=(year,target);rec=best.get(k)
     parent=w['parent'];fby=old.get((year,parent if parent else target));fbyp=fby['vehicle_total_usd'] if fby else '';reason=''
     if parent and not fby:reason='PARENT_NO_FLYBY_QUOTE'
     if parent and not w['orbit_radius_km']:reason='MOON_ORBIT_RADIUS_MISSING'
     if parent and not w['parent_gm_km3_s2']:reason='PARENT_GM_MISSING'
     if rec is None:reason=reason or 'NO_SAMPLED_TRANSFER'
     status='PRICED_TEST_ONLY' if rec and not reason else 'UNPRICED'
     p,day,days,_=rec if rec else (None,'','',None)
     data=dict(year=year,body=target,status=status,parent=parent,departure_date=day if status=='PRICED_TEST_ONLY' else '',flight_days=repr(days) if status=='PRICED_TEST_ONLY' else '',departure_vinf_km_s=repr(p['departure_vinf_km_s']) if status=='PRICED_TEST_ONLY' else '',arrival_vinf_km_s=repr(p['arrival_vinf_km_s']) if status=='PRICED_TEST_ONLY' else '',departure_delta_v_km_s=repr(p['departure_delta_v_km_s']) if status=='PRICED_TEST_ONLY' else '',arrival_braking_delta_v_km_s=repr(p['arrival_braking_delta_v_km_s']) if status=='PRICED_TEST_ONLY' else '',departure_stages=p['departure_stages'] if status=='PRICED_TEST_ONLY' else '',braking_stages=p['braking_stages'] if status=='PRICED_TEST_ONLY' else '',braking_stack_mass_kg=repr(p['braking_stack_mass_kg']) if status=='PRICED_TEST_ONLY' else '',mass_in_leo_kg=repr(p['mass_in_leo_kg']) if status=='PRICED_TEST_ONLY' else '',launch_cost_usd=repr(p['launch_cost_usd']) if status=='PRICED_TEST_ONLY' else '',operating_cost_usd=repr(p['operating_cost_usd']) if status=='PRICED_TEST_ONLY' else '',total_usd=repr(p['total_usd']) if status=='PRICED_TEST_ONLY' else '',model_units=p['model_units'] if status=='PRICED_TEST_ONLY' else '',flyby_price_usd=fbyp,flyby_source='PARENT_FLYBY' if parent else 'DIRECT_FLYBY',reason=reason,run_identity=idh)
     append(pf,pw,data)
    print('GEOMETRY_BODY_YEAR',key,'DATES',len(dates),'ELAPSED',round(time.monotonic()-start,2),'PEAK',peak(),flush=True)
 # Add any moons whose parent is not in the 59 body list, without invented trajectory.
 seen={(int(r['year']),r['body']) for r in csv.DictReader(PR.open())}
 with PR.open('a',newline='') as pf:
  pw=csv.DictWriter(pf,pfields,lineterminator='\n')
  for year in (2026,2027):
   for body in ALL_BODIES:
    if (year,body) in seen:continue
    w=world[body];parent=w['parent'];reason='PARENT_NO_FLYBY_QUOTE' if parent else 'NO_59_BODY_TABLE_QUOTE'
    append(pf,pw,dict(year=year,body=body,status='UNPRICED',parent=parent,departure_date='',flight_days='',departure_vinf_km_s='',arrival_vinf_km_s='',departure_delta_v_km_s='',arrival_braking_delta_v_km_s='',departure_stages='',braking_stages='',braking_stack_mass_kg='',mass_in_leo_kg='',launch_cost_usd='',operating_cost_usd='',total_usd='',model_units='',flyby_price_usd='',flyby_source='',reason=reason,run_identity=idh))
 geo_elapsed=time.monotonic()-geo_start;prices=list(csv.DictReader(PR.open()));assert len(prices)==180
 # Old flyby is an immutable baseline; validate byte-identical pinned hash and all 118 existing records.
 assert sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv')=='2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73'
 reg={'old_flyby_csv_sha256':sha(P/'VEHICLE_FLYBY_PRICES_TEST_ONLY.csv'),'old_flyby_run_identity_sha256':json.loads((P/'VEHICLE_FLYBY_REPORT_TEST_ONLY.json').read_text())['run_identity_sha256'],'old_flyby_price_differences':[],'control_expected':f['route1_control_sha256']}
 save(GR,dict(identity=identity,identity_sha256=idh,authored_input_sha256=sha(A),parent_sha256=sha(F),world_sha256=sha(W),sampled_departures=count,sampled_trajectories=trajectories,geometry_seconds=geo_elapsed,peak_rss_bytes=peak(),departure_csv_sha256=sha(G),prices_csv_sha256=sha(PR),recovered_departure_lattice_differences=geometry_errors,hand_tests=hand,regression=reg,classification='TEST_ONLY_NONCANON'))
 print('GEOMETRY_SAVED',count,'TRAJECTORIES',trajectories,'DIFF_LATTICE',len(geometry_errors),'PRICED',sum(r['status']=='PRICED_TEST_ONLY' for r in prices),'SECONDS',geo_elapsed,flush=True)
 # Route 1 control exact replay.
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True);control.record_states(2026);ct=time.monotonic();z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':control});paid={(r['year'],r['executor']) for r in control.receipts};z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly']);z['campaign']=control.report();z['campaign']['runtime_total_seconds']=0;ch=stable_hash(z);assert ch==f['route1_control_sha256'],ch
 print('CONTROL_PASS',ch,'SECONDS',time.monotonic()-ct,flush=True)
 rt=time.monotonic();priced={(int(r['year']),r['body']):r for r in prices if r['status']=='PRICED_TEST_ONLY'};campaign=CostCampaign(priced,idh);campaign.record_states(2026);z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':campaign});paid={(r['year'],r['executor']) for r in campaign.receipts};z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly']);z['campaign']=campaign.report();z['campaign']['runtime_total_seconds']=0;vh=stable_hash(z)
 receipts=campaign.receipts;blocks=Counter(r['primary_blocker'] for r in campaign.attempts if r['outcome']=='BLOCKED');funded={r['body'] for r in receipts};old31=sorted(set(ALL_BODIES)-{b for _,b in old});first={}
 for b in old31:
  q=next((r for r in receipts if r['body']==b and r['stage']=='A1'),None);first[b]=dict(funded=q is not None,year=q['year'] if q else None,sponsor=q['sponsor'] if q else None,price_model_units=q['amount'] if q else None,reason=next((r['reason'] for r in prices if r['body']==b and r['status']=='UNPRICED'),'') if not q else '')
 report=dict(classification='KT_TEST_ONLY_NONCANON',identity_sha256=idh,authored_input_sha256=sha(A),parent_input_sha256=sha(F),world_sha256=sha(W),geometry_report_sha256=sha(GR),prices_csv_sha256=sha(PR),control_sha256=ch,variant_sha256=vh,funded_stages=len(receipts),funded_bodies=len(funded),spent_model_units=str(sum((D(r['amount']) for r in receipts),D(0))),blockers=dict(blocks),blocked_attempts=sum(blocks.values()),unpriced_bodies={b:next((r['reason'] for r in prices if r['body']==b and r['status']=='UNPRICED'),'') for b in ALL_BODIES if (2026,b) not in priced},old31_first_funded=first,never_funded=sorted(set(ALL_BODIES)-funded),route1_seconds=time.monotonic()-rt,total_seconds=time.monotonic()-start,peak_rss_bytes=peak())
 save(RR,report);print('ROUTE1_SAVED',report['funded_stages'],report['funded_bodies'],report['spent_model_units'],'BLOCKERS',blocks,'TIME',report['total_seconds'],'PEAK',peak(),flush=True)
if __name__=='__main__':main()
