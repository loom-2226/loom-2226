"""PR427 paired replay. New artifacts only; no geometry integration."""
import csv,json,time,resource,hashlib
from pathlib import Path
from decimal import Decimal
from collections import Counter
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
from simulation.offworld_mvp.build8.three_arm_stage1.run_rendezvous_kt_v2_test_only import CostCampaign
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign,ALL_BODIES
from simulation.offworld_mvp.build8.route1_body_campaign import SETTINGS
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash
P=Path(__file__).resolve().parent
def read(n):return list(csv.DictReader((P/n).open()))
def sha(n):return hashlib.sha256((P/n).read_bytes()).hexdigest()
def replay(c):
 c.record_states(2026)
 z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':c})
 paid={(r['year'],r['executor']) for r in c.receipts}
 z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly'])
 z['campaign']=c.report();z['campaign']['runtime_total_seconds']=0
 return stable_hash(z)
class FlyCampaign(CostCampaign):
 def attempt(self,k,sponsor,body,stage,year,used=0):
  row=super().attempt(k,sponsor,body,stage,year,used)
  if stage=='A1' and row['price_source']!='UNPRICED':
   y=year if year in (2026,2027) else 2026
   source='FLYBY_PARENT' if self.prices[(y,body)].get('parent') else 'FLYBY_DIRECT'
   row['price_source']=source
   if row['outcome']=='FUNDED':self.receipts[-1]['price_source']=source
  return row
def main():
 t=time.monotonic()
 files=['VEHICLE_FLYBY_PRICES_TEST_ONLY.csv','VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json','RENDEZVOUS_V2_SAMPLED_DEPARTURES_TEST_ONLY.csv','RENDEZVOUS_V2_PRICES_TEST_ONLY.csv','RENDEZVOUS_V2_ROUTE1_REPORT_TEST_ONLY.json','RECOVERED_FLYBY_POLICY_FULL_CLOCK_REPORT_TEST_ONLY.json']
 hashes={n:sha(n) for n in files}
 assert hashes[files[0]]=='2a36b2ef103480c7b8624b86d6910becd69472ad78913ec2ea60141e64643b73'
 a=json.loads((P/files[1]).read_text());old=read(files[0]);sample=read(files[2]);rv=read(files[3])
 assert len(old)==118 and len(sample)==3731 and len(rv)==180
 best={}
 for x in sample:
  if x['min_departure_vinf_km_s']:
   k=(int(x['year']),x['body']);v=(float(x['min_departure_vinf_km_s']),x['departure_date']);best[k]=min(best.get(k,v),v)
 differences=[];fly={}
 for x in old:
  k=(int(x['year']),x['body']);v,day=best[k];p=price(v,a)
  fly[k]={'model_units':p['model_units'],'parent':''}
  for field,value in [('stage_count',p['stages']),('mass_in_leo_kg',p['mass_in_leo_kg']),('injection_delta_v_km_s',p['leo_injection_delta_v_km_s']),('launch_cost_usd',p['launch_cost_usd']),('fixed_cost_usd',p['fixed_mission_cost_usd']),('vehicle_total_usd',p['total_usd'])]:
   if str(value)!=x[field]:differences.append({'year':k[0],'body':k[1],'field':field,'pinned':x[field],'recomputed':str(value)})
 for x in rv:
  if x['parent']:
   k=(int(x['year']),x['body']);parent=(k[0],x['parent'])
   if parent in fly:fly[k]={'model_units':fly[parent]['model_units'],'parent':x['parent']}
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True);ch=replay(control)
 assert ch=='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
 old31=sorted(set(ALL_BODIES)-{b for _,b in best})
 old23=json.loads((P/files[5]).read_text())['cases'][-1]['never_funded']
 cases={}
 for name,prices,cls in [('A1_FLYBY_PARENT_MOONS',fly,FlyCampaign),('A1_RENDEZVOUS',{(int(x['year']),x['body']):x for x in rv if x['status']=='PRICED_TEST_ONLY'},CostCampaign)]:
  c=cls(prices,name);h=replay(c);receipts=c.receipts
  blockers=Counter(x['primary_blocker'] for x in c.attempts if x['outcome']=='BLOCKED')
  def prior(bodies):
   d={}
   for b in bodies:
    q=next((x for x in receipts if x['body']==b and x['stage']=='A1'),None)
    d[b]={'funded':q is not None,'year':q['year'] if q else None,'sponsor':q['sponsor'] if q else None,'price_model_units':q['amount'] if q else None}
   return d
  cases[name]={'variant_sha256':h,'funded_stages':len(receipts),'funded_bodies':len({x['body'] for x in receipts}),'cash_model_units':str(sum((Decimal(x['amount']) for x in receipts),Decimal(0))),'blockers':dict(blockers),'blocked_attempts':sum(blockers.values()),'old31':prior(old31),'old23':prior(old23)}
  print('CASE',name,json.dumps({k:v for k,v in cases[name].items() if k not in ('old31','old23')}),flush=True)
 report={'classification':'TEST_ONLY_NONCANON','previous_report_used':'A1_RENDEZVOUS','flyby_method':'Recompute flyby vehicle cost from minimum departure speed in saved sampled-departure rows; no new trajectory geometry','comparison':'Exact string comparison of six pinned numeric fields; all differences retained','literal_fields':['classification','previous_report_used','flyby_method','comparison','literal_fields'],'numpy_version':__import__('numpy').__version__,'sampled_departures':len(sample),'flyby_body_years':len(old),'flyby_differences':differences,'control_sha256':ch,'source_sha256':hashes,'cases':cases,'elapsed_seconds':time.monotonic()-t,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 target=P/'RENDEZVOUS_V2_PAIRED_REPLAY_REPORT_TEST_ONLY.json'
 with target.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('DIFFERENCES',json.dumps(differences),flush=True)
 print('DONE',report['elapsed_seconds'],report['peak_rss_bytes'],flush=True)
if __name__=='__main__':main()
