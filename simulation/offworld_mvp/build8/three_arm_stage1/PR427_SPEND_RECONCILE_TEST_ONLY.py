"""Test-only original-flyby and rendezvous replay; never runs geometry."""
import csv,json,time,resource,hashlib
from pathlib import Path
from decimal import Decimal
from collections import Counter
from simulation.offworld_mvp.build8.three_arm_stage1.run_vehicle_flyby_test_only import VehicleCampaign
from simulation.offworld_mvp.build8.three_arm_stage1.run_rendezvous_kt_v2_test_only import CostCampaign
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import FlyCampaign
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash
P=Path(__file__).resolve().parent
def rows(name):return list(csv.DictReader((P/name).open()))
def replay(c):
 c.record_states(2026)
 z=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':c})
 paid={(r['year'],r['executor']) for r in c.receipts}
 z['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in z['executor_yearly'])
 z['campaign']=c.report();z['campaign']['runtime_total_seconds']=0
 return stable_hash(z)
def summary(c):
 d={}
 for r in c.receipts:
  b=r['body'];v=d.setdefault(b,{'stages':[],'sponsors':[],'years':[],'prices_model_units':[]})
  v['stages'].append(r['stage']);v['sponsors'].append(r['sponsor']);v['years'].append(r['year']);v['prices_model_units'].append(r['amount'])
 return d
def main():
 start=time.monotonic()
 old=json.loads((P/'VEHICLE_FLYBY_REPORT_TEST_ONLY.json').read_text())
 rv_old=json.loads((P/'RENDEZVOUS_V2_ROUTE1_REPORT_TEST_ONLY.json').read_text())
 orig=rows('VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv')
 old_campaign=VehicleCampaign({(int(r['year']),r['body']):r for r in orig},old['run_identity_sha256'])
 old_hash=replay(old_campaign)
 assert old_hash==old['variant_sha256'],('OLD_FLYBY_HASH',old_hash,old['variant_sha256'])
 rv=rows('RENDEZVOUS_V2_PRICES_TEST_ONLY.csv')
 rv_campaign=CostCampaign({(int(r['year']),r['body']):r for r in rv if r['status']=='PRICED_TEST_ONLY'},rv_old['identity_sha256'])
 rv_hash=replay(rv_campaign)
 assert rv_hash==rv_old['variant_sha256'],('RENDEZVOUS_HASH',rv_hash,rv_old['variant_sha256'])
 # Reconstruct exactly the flyby parent pricing from the previously recorded flyby minimum speeds.
 from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
 authored=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text())
 fly={(int(r['year']),r['body']):{'model_units':price(float(r['minimum_departure_vinf_km_s']),authored)['model_units'],'parent':''} for r in orig}
 for r in rv:
  if r['parent']:
   key=(int(r['year']),r['body']);parent=(key[0],r['parent'])
   if parent in fly:fly[key]={'model_units':fly[parent]['model_units'],'parent':r['parent']}
 new_campaign=FlyCampaign(fly,'A1_FLYBY_PARENT_MOONS')
 new_hash=replay(new_campaign)
 prior=json.loads((P/'RENDEZVOUS_V2_PAIRED_REPLAY_REPORT_TEST_ONLY.json').read_text())['cases']['A1_FLYBY_PARENT_MOONS']
 assert new_hash==prior['variant_sha256'],('NEW_FLYBY_HASH',new_hash,prior['variant_sha256'])
 o,n=summary(old_campaign),summary(new_campaign)
 entries=[]
 for body in sorted(set(o)|set(n)):
  entries.append({'body':body,'old':o.get(body),'new':n.get(body),
   'old_spend_model_units':str(sum((Decimal(x) for x in o.get(body,{}).get('prices_model_units',[])),Decimal(0))),
   'new_spend_model_units':str(sum((Decimal(x) for x in n.get(body,{}).get('prices_model_units',[])),Decimal(0)))})
 old_spend=sum((Decimal(r['amount']) for r in old_campaign.receipts),Decimal(0))
 new_spend=sum((Decimal(r['amount']) for r in new_campaign.receipts),Decimal(0))
 assert str(old_spend)==old['spent_model_units'] and str(new_spend)==prior['cash_model_units']
 out={'classification':'TEST_ONLY_NONCANON','numpy_version':__import__('numpy').__version__,'old_flyby_sha256':old_hash,'new_flyby_sha256':new_hash,'rendezvous_original_identity_sha256':rv_old['identity_sha256'],'rendezvous_replay_sha256':rv_hash,'rendezvous_expected_sha256':rv_old['variant_sha256'],'old_spend_model_units':str(old_spend),'new_spend_model_units':str(new_spend),'delta_spend_model_units':str(new_spend-old_spend),'old_funded_bodies':len(o),'new_funded_bodies':len(n),'old_funded_stages':len(old_campaign.receipts),'new_funded_stages':len(new_campaign.receipts),'body_comparison':entries,'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 path=P/'PR427_SPEND_RECONCILE_REPORT_TEST_ONLY.json'
 with path.open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
 print('RECONCILED',json.dumps({k:v for k,v in out.items() if k!='body_comparison'}),flush=True)
if __name__=='__main__':main()
