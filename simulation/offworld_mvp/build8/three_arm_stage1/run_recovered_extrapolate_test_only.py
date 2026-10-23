"""PR427 new-only EXTRAPOLATED_TEST_ONLY full-clock experiment."""
import csv,hashlib,json,resource,time
from collections import Counter,defaultdict
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.route1_body_campaign import SETTINGS
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash

P=Path(__file__).resolve().parent
INPUT=P/'RECOVERED_EXTRAPOLATE_INPUT_TEST_ONLY.json'
OUTPUT=P/'RECOVERED_EXTRAPOLATE_FULL_CLOCK_REPORT_TEST_ONLY.json'
BALANCES=P/'RECOVERED_EXTRAPOLATE_SPONSOR_BALANCES_TEST_ONLY.csv'
BLOCKED=P/'RECOVERED_EXTRAPOLATE_BLOCKED_ATTEMPTS_TEST_ONLY.csv'
QUOTE=P/'RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv'
LIMITS=P/'A_BODY_YEAR_REPORT_LIMITS.csv'
REC=P/'RECOVERED_ARM_A_TABLE_PAIRS_TEST_ONLY.csv'
PRIOR=P/'RECOVERED_FLYBY_POLICY_FULL_CLOCK_REPORT_TEST_ONLY.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()
def mem():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def prices(rule):
 quotes=list(csv.DictReader(QUOTE.open(newline='')))
 old=list(csv.DictReader(LIMITS.open(newline='')))
 new=list(csv.DictReader(REC.open(newline='')))
 speeds=defaultdict(list)
 for r in old:
  if r['lowest_speed_departure_km_s']:speeds[r['body']].append((D(r['lowest_speed_departure_km_s']),int(r['year']),'ORIGINAL_LIMITS_CSV'))
 for r in new:
  if r['mission_type_id']=='flyby' and r['needed_departure_speed_km_s']:speeds[r['body']].append((D(r['needed_departure_speed_km_s']),int(r['year']),'RECOVERED_PAIRS_CSV'))
 infeasible={r['body'] for r in quotes if r['mission_type_id']=='flyby' and r['status']=='INFEASIBLE'}
 values={};missing=[]
 for b in sorted(infeasible):
  options=[x for x in speeds[b] if x[1] in rule['source_years']]
  if not options:missing.append(b);continue
  v,year,source=min(options)
  values[b]={'minimum_departure_km_s':str(v),'minimum_source_year':year,'minimum_source':source,'price_model_units':str(v*D(rule['proxy_usd_millions_per_km_s'])/D(1000)),'status':'EXTRAPOLATED_TEST_ONLY'}
 return quotes,values,missing
class ExtrapolateCampaign(AllBodyCampaign):
 def __init__(self,quotes,extrapolated,rule):
  super().__init__(body_count=90,ceilings_enabled=False)
  self.rule=rule;self.extrapolated=extrapolated
  self.flyby_quotes={(int(r['year']),r['body']):r for r in quotes if r['vehicle_class_id']=='baseline' and r['mission_type_id']=='flyby'}
  self.year_balances={};self.high=defaultdict(lambda:D('-Infinity'))
 def snap(self,k,year,sponsor):
  value=k.state.accounts['route1:budget:'+sponsor].balance
  self.high[year,sponsor]=max(self.high[year,sponsor],value)
  return value
 def on_year(self,year,k,rows):
  if SETTINGS['CAMPAIGN_START_YEAR']<=year<=SETTINGS['CAMPAIGN_END_YEAR']:
   for sponsor in self.requesters:
    opening=next((r['opening'] for r in rows if r['sponsor']==sponsor),None)
    self.year_balances[year,sponsor]={'start_of_year':opening,'maximum_reached':str(self.snap(k,year,sponsor))}
  super().on_year(year,k,rows)
  if SETTINGS['CAMPAIGN_START_YEAR']<=year<=SETTINGS['CAMPAIGN_END_YEAR']:
   for sponsor in self.requesters:
    self.year_balances[year,sponsor]['maximum_reached']=str(max(self.snap(k,year,sponsor),D(self.year_balances[year,sponsor]['start_of_year']),self.high[year,sponsor]))
 def attempt(self,k,sponsor,body,stage,year,used=0):
  self.snap(k,year,sponsor)
  source='UNCHANGED_A2';status='NOT_APPLICABLE';price=None
  if stage=='A1':
   sy=year if year in (2026,2027) else 2026
   quote=self.flyby_quotes.get((sy,body))
   if quote and quote['status']=='INFEASIBLE' and body in self.extrapolated:
    price=D(self.extrapolated[body]['price_model_units']);source='EXTRAPOLATED_PROXY';status='EXTRAPOLATED_TEST_ONLY'
   elif quote and quote['status']=='PRICED_TEST_ONLY' and quote['lowest_price_usd']:
    price=D(quote['lowest_price_usd'])/D(1000000000);source='TABLE' if year==sy else 'HELD';status='PRICED_TEST_ONLY'
   else:source='ABSTRACT_FALLBACK';status='ABSTRACT_TEST_ONLY'
  original=SETTINGS['A1_SERVICE_PRICE']
  try:
   if price is not None:SETTINGS['A1_SERVICE_PRICE']=price
   row=super().attempt(k,sponsor,body,stage,year,used)
  finally:SETTINGS['A1_SERVICE_PRICE']=original
  row['price_source']=source;row['quote_status']=status
  if row['outcome']=='FUNDED':
   self.receipts[-1]['price_source']=source
   self.receipts[-1]['quote_status']=status
  self.snap(k,year,sponsor)
  return row
 def limits(self):
  x=super().limits();x['infeasible_policy']='EXTRAPOLATE_PROXY';x['extrapolated_quote_status']='EXTRAPOLATED_TEST_ONLY';return x
 def report(self):
  x=super().report();x['infeasible_policy']='EXTRAPOLATE_PROXY';x['extrapolated_quote_status']='EXTRAPOLATED_TEST_ONLY';return x
def write_csv(path,rows,fields):
 with path.open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 t=time.monotonic();rule=json.loads(INPUT.read_text())
 assert rule['infeasible_policy']=='EXTRAPOLATE_PROXY' and rule['quote_status']=='EXTRAPOLATED_TEST_ONLY' and rule['ceilings_enabled'] is False and rule['held_year']==2026
 quotes,extrapolated,missing=prices(rule)
 prior=json.loads(PRIOR.read_text());never=prior['cases'][-1]['never_funded']
 hashes={p.name:sha(p) for p in (INPUT,QUOTE,LIMITS,REC,PRIOR,P/'RECOVERED_COMBINED_59_QUOTE_MANIFEST_TEST_ONLY.json')}
 identity={'classification':'EXTRAPOLATED_TEST_ONLY_NON_CANON','policy':rule,'source_sha256':hashes,'missing_original_speed':missing}
 print('INPUT',canonical(identity),'EXTRAPOLATED_BODIES',len(extrapolated),'MISSING',missing,flush=True)
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True);control.record_states(2026)
 a=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':control})
 paid={(r['year'],r['executor']) for r in control.receipts}
 a['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in a['executor_yearly'])
 a['campaign']=control.report();a['campaign']['runtime_total_seconds']=0
 ch=stable_hash(a)
 assert ch==rule['control_expected_sha256'],f'CONTROL_HASH_CHANGED:{ch}'
 print('CONTROL_PASS',ch,'SECONDS',round(time.monotonic()-t,2),flush=True)
 vt=time.monotonic();c=ExtrapolateCampaign(quotes,extrapolated,rule);c.record_states(2026)
 result=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':c})
 paid={(r['year'],r['executor']) for r in c.receipts}
 result['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in result['executor_yearly'])
 result['campaign']=c.report();result['campaign']['runtime_total_seconds']=0
 vh=stable_hash(result)
 balances=[]
 for row in result['rows']:
  y=int(row['year']);s=row['sponsor']
  if (y,s) in c.year_balances:
   start=c.year_balances[y,s]['start_of_year']
   peak=str(max(D(c.year_balances[y,s]['maximum_reached']),D(start),D(row['closing'])))
  else:
   start=row['opening'];peak=str(max(D(row['opening']),D(row['closing'])))
  balances.append({'year':y,'sponsor':s,'start_of_year_balance':start,'maximum_reached_balance':peak,'closing_balance':row['closing']})
 assert len({(r['year'],r['sponsor']) for r in balances})==len(balances)
 write_csv(BALANCES,balances,['year','sponsor','start_of_year_balance','maximum_reached_balance','closing_balance'])
 blocked=[{'year':r['year'],'sponsor':r['sponsor'],'body':r['body'],'stage':r['stage'],'balance_before':r['balance_before'],'requested_price':r['amount'],'blocker':r['primary_blocker'],'price_source':r.get('price_source'),'quote_status':r.get('quote_status')} for r in c.attempts if r['outcome']=='BLOCKED']
 write_csv(BLOCKED,blocked,['year','sponsor','body','stage','balance_before','requested_price','blocker','price_source','quote_status'])
 sources=defaultdict(lambda:{'count':0,'spent':D(0)})
 for r in c.receipts:
  z=sources[r['price_source']];z['count']+=1;z['spent']+=D(r['amount'])
 by_body=defaultdict(list)
 for r in c.receipts:
  if r['stage']=='A1':by_body[r['body']].append({'year':r['year'],'sponsor':r['sponsor'],'price_model_units':r['amount'],'source':r['price_source'],'quote_status':r['quote_status']})
 largest=max(D(r['maximum_reached_balance']) for r in balances)
 summary={}
 for b in never:
  rows=by_body[b];summary[b]={'funded':bool(rows),'purchases':rows,'minimum_departure_km_s':extrapolated.get(b,{}).get('minimum_departure_km_s'),'quoted_price_model_units':extrapolated.get(b,{}).get('price_model_units'),'original_speed_source':extrapolated.get(b,{}).get('minimum_source'),'if_unfunded_blocker':'CASH_OR_FINANCIER_OR_OTHER_AS_RECORDED_IN_BLOCKED_CSV' if not rows else None,'largest_any_sponsor_balance_model_units':str(largest) if not rows else None}
 blockers=Counter(r['blocker'] for r in blocked)
 categories={'cash':sum(n for k,n in blockers.items() if k=='ACTUAL_SPONSOR_CASH'),'financier':sum(n for k,n in blockers.items() if k and k.startswith('FINANCIER_')),'other':sum(n for k,n in blockers.items() if k!='ACTUAL_SPONSOR_CASH' and not (k and k.startswith('FINANCIER_')))}
 report={'classification':'EXTRAPOLATED_TEST_ONLY_NON_CANON','infeasible_policy':'EXTRAPOLATE_PROXY','quote_status':'EXTRAPOLATED_TEST_ONLY','run_identity':identity,'run_identity_sha256':canonical(identity),'control_stable_sha256':ch,'variant_stable_sha256':vh,'funded_stages':len(c.receipts),'bodies_funded':len({r['body'] for r in c.receipts}),'cash_spent_model_units':str(sum((D(r['amount']) for r in c.receipts),D(0))),'charges_by_source':{k:{'count':v['count'],'spent_model_units':str(v['spent'])} for k,v in sorted(sources.items())},'blocked_attempts':len(blocked),'blockers':dict(blockers),'blocker_categories':categories,'former_block_23':summary,'extrapolated_body_source':extrapolated,'missing_original_speed':missing,'balance_records':len(balances),'largest_any_sponsor_balance_model_units':str(largest),'control_seconds':vt-t,'variant_seconds':time.monotonic()-vt,'total_seconds':time.monotonic()-t,'peak_rss_bytes':mem(),'output_sha256':{BALANCES.name:sha(BALANCES),BLOCKED.name:sha(BLOCKED)}}
 OUTPUT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('DONE',len(c.receipts),len({r['body'] for r in c.receipts}),report['cash_spent_model_units'],'FORMER_FUNDED',sum(v['funded'] for v in summary.values()),'BLOCKED',len(blocked),'SECONDS',round(report['total_seconds'],2),'RSS',mem(),flush=True)
if __name__=='__main__':main()
