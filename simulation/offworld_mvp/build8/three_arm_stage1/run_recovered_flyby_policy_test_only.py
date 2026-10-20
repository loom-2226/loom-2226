"""PR427 TEST_ONLY: combined pinned flyby quotes and full-clock A1 infeasible policy."""
import csv,hashlib,json,resource,time
from collections import Counter,defaultdict
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.route1_body_campaign import SETTINGS,CEILING
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign
from simulation.offworld_mvp.build8.route1_cast_payments import run_cast_payments
from simulation.offworld_mvp.build8.three_arm_stage1.route1_flyby_price_variant import stable_hash

P=Path(__file__).resolve().parent
INPUT=P/'RECOVERED_FLYBY_POLICY_INPUT_TEST_ONLY.json'
QUOTE=P/'RECOVERED_COMBINED_59_PINNED_QUOTES_TEST_ONLY.csv'
MANIFEST=P/'RECOVERED_COMBINED_59_QUOTE_MANIFEST_TEST_ONLY.json'
REPORT=P/'RECOVERED_FLYBY_POLICY_FULL_CLOCK_REPORT_TEST_ONLY.json'
OLD=P/'A_VEHICLE_MISSION_PAIRS.csv'
REC=P/'RECOVERED_ARM_A_TABLE_PAIRS_TEST_ONLY.csv'
ORIGINAL=P/'ROUTE1_FLYBY_PRICE_PAIRED_REPORT.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def ident(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def memory():return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
def build_quotes():
 old=list(csv.DictReader(OLD.open(newline='')));new=list(csv.DictReader(REC.open(newline='')))
 fields=list(old[0]);assert len(old)==100 and len(new)==136
 assert len({(r['year'],r['body'],r['vehicle_class_id'],r['mission_type_id']) for r in old+new})==236
 assert len({r['body'] for r in old+new})==59
 provenance={}
 for source,records in [('ORIGINAL_25',old),('RECOVERED_VINTAGE_TEST_ONLY',new)]:
  for r in records:
   key='|'.join(r[k] for k in ('year','body','vehicle_class_id','mission_type_id'))
   provenance[key]={'source':source,'source_csv_sha256':sha(OLD if source=='ORIGINAL_25' else REC),'row_sha256':ident({k:r[k] for k in fields})}
 if QUOTE.exists():
  actual=list(csv.DictReader(QUOTE.open(newline='')));assert actual==[{k:r[k] for k in fields} for r in old+new]
 else:
  with QUOTE.open('x',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows({k:r[k] for k in fields} for r in old+new)
 manifest={'classification':'RECOVERED_VINTAGE_TEST_ONLY','quote_sha256':sha(QUOTE),'original_sha256':sha(OLD),'recovered_sha256':sha(REC),'recovery_manifest_sha256':sha(P/'PHASE4E_RECOVERY_34_TEST_ONLY_MANIFEST.json'),'recovered_table_manifest_sha256':sha(P/'RECOVERED_PHASE4E_TABLE_MANIFEST_TEST_ONLY.json'),'rows':provenance,'count':236,'bodies':59}
 if MANIFEST.exists():assert json.loads(MANIFEST.read_text())==manifest
 else:MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 return manifest
class PolicyCampaign(AllBodyCampaign):
 def __init__(self,policy,quotes):
  assert policy in ('ABSTRACT_FALLBACK','BLOCK')
  super().__init__(body_count=90,ceilings_enabled=False)
  self.policy=policy
  self.flyby_quotes={(int(r['year']),r['body']):r for r in quotes if r['vehicle_class_id']=='baseline' and r['mission_type_id']=='flyby'}
  assert len(self.flyby_quotes)==118
  self.price_attempts=Counter();self.price_paid=Counter()
 def attempt(self,k,sponsor,body,stage,year,used=0):
  source='UNCHANGED_A2';quote=None
  if stage=='A1':
   sy=year if year in (2026,2027) else 2026
   quote=self.flyby_quotes.get((sy,body))
   if quote and quote['status']=='INFEASIBLE' and self.policy=='BLOCK':
    # A1 never purchases, and no financing request or ledger mutation occurs.
    # Same row/audit structure as the original attempt, with explicit blocker.
    balance=k.state.accounts['route1:budget:'+sponsor].balance
    supplier=self.quote(sponsor,SETTINGS['A1_SERVICE_CATEGORY'])
    row=dict(year=year,sponsor=sponsor,body=body,stage=stage,category=SETTINGS['A1_SERVICE_CATEGORY'],
             amount='0',balance_before=str(balance),ceiling=str(D(CEILING[sponsor])),
             ceiling_enabled=False,executor=supplier['executor'] if supplier else None,
             outcome='BLOCKED',primary_blocker='INFEASIBLE_FLYBY_QUOTE',policy_reason=None,
             named_stage_limit=self.max_stages,classification='AUTHORED TEST_ONLY NON-CANON',
             study_attempt=self.a1_counts[body]+1,source_basis='GENERATED_TEST_ONLY',
             accessibility_status='QUOTE_INFEASIBLE',price_source='INFEASIBLE_BLOCK',
             binding_limit=quote.get('binding_limit','ORIGINAL_25_INFEASIBLE_LIMIT_UNSPECIFIED'))
    self.attempts.append(row)
    k.audit('BUILD8_CAMPAIGN_REQUEST',year,**{a:b for a,b in row.items() if a!='year'})
    self.price_attempts[year,'INFEASIBLE_BLOCK']+=1
    return row
   if quote and quote['status']=='PRICED_TEST_ONLY' and quote['lowest_price_usd']:
    price=D(quote['lowest_price_usd'])/D(1000000000)
    source='TABLE' if year==sy else 'HELD'
   else:
    price=D(SETTINGS['A1_SERVICE_PRICE']);source='ABSTRACT_FALLBACK'
  original=SETTINGS['A1_SERVICE_PRICE']
  try:
   if stage=='A1':SETTINGS['A1_SERVICE_PRICE']=price
   row=super().attempt(k,sponsor,body,stage,year,used)
  finally:SETTINGS['A1_SERVICE_PRICE']=original
  row['price_source']=source
  if stage=='A1':self.price_attempts[year,source]+=1
  if row['outcome']=='FUNDED':
   self.receipts[-1]['price_source']=source
   if stage=='A1':self.price_paid[year,source]+=1
  return row
 def limits(self):
  x=super().limits();x['infeasible_policy']=self.policy;return x
 def report(self):
  r=super().report();r['infeasible_policy']=self.policy
  r['price_source_attempts']=sorted((y,s,n) for (y,s),n in self.price_attempts.items())
  r['price_source_paid']=sorted((y,s,n) for (y,s),n in self.price_paid.items())
  return r
def run(case,quotes):
 t=time.monotonic()
 if case['name']=='control':c=AllBodyCampaign(body_count=90,ceilings_enabled=case['ceilings_enabled'])
 else:c=PolicyCampaign(case['infeasible_policy'],quotes)
 c.record_states(2026)
 result=run_cast_payments(end_year=2226,run_setting={'name':'all_body_campaign','campaign':c})
 paid={(r['year'],r['executor']) for r in c.receipts}
 result['executor_yearly']=tuple(dict(row,status=('PAID_TEST_ONLY_STUDY' if (row['year'],row['executor']) in paid else row['status'])) for row in result['executor_yearly'])
 result['campaign']=c.report();result['campaign']['runtime_total_seconds']=round(time.monotonic()-t,6)
 h=stable_hash(result)
 if 'expected_stable_sha256' in case:assert h==case['expected_stable_sha256'],f'CONTROL_HASH_MISMATCH {h}'
 paid_stages=len(c.receipts);bodies=len({r['body'] for r in c.receipts})
 spend=sum((D(r['amount']) for r in c.receipts),D(0))
 sources=defaultdict(lambda:{'count':0,'cash_spent_model_currency':D(0)})
 for r in c.receipts:
  source=r.get('price_source','CONTROL_UNMODIFIED')
  sources[source]['count']+=1;sources[source]['cash_spent_model_currency']+=D(r['amount'])
 blockers=Counter(r['primary_blocker'] for r in c.attempts if r['outcome']=='BLOCKED')
 body_funded={r['body'] for r in c.receipts}
 never=sorted(set(c.bodies)-body_funded)
 out={'case':case,'stable_sha256':h,'funded_stages':paid_stages,'bodies_funded':bodies,'cash_spent_model_currency':str(spend),'charges_by_price_source':{k:{'count':v['count'],'cash_spent_model_currency':str(v['cash_spent_model_currency'])} for k,v in sorted(sources.items())},'blocked_purchases_by_blocker':dict(sorted(blockers.items())),'never_funded':never,'runtime_seconds':time.monotonic()-t,'peak_rss_bytes':memory()}
 print('CASE_DONE',case['name'],'HASH',h,'FUNDED',paid_stages,'BODIES',bodies,'SPEND',spend,'BLOCKS',blockers.get('INFEASIBLE_FLYBY_QUOTE',0),'SECONDS',round(out['runtime_seconds'],2),'PEAK',memory(),flush=True)
 return out
def main():
 t=time.monotonic();manifest=build_quotes();inp=json.loads(INPUT.read_text())
 quotes=list(csv.DictReader(QUOTE.open(newline='')))
 identity={'input_sha256':sha(INPUT),'combined_quote_sha256':sha(QUOTE),'quote_manifest_sha256':sha(MANIFEST),'original_report_sha256':sha(ORIGINAL),'policy_cases':inp['cases'],'classification':'TEST_ONLY_NON_CANON'}
 report={'run_identity':identity,'run_identity_sha256':ident(identity),'cases':[],'classification':'TEST_ONLY_NON_CANON'}
 for case in inp['cases']:
  result=run(case,quotes);report['cases'].append(result)
  report['elapsed_seconds']=time.monotonic()-t;report['peak_rss_bytes']=memory()
  REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 block=report['cases'][-1];binding={r['body']:'ORIGINAL_25_INFEASIBLE_LIMIT_UNSPECIFIED' for r in quotes if r['year']=='2026' and r['mission_type_id']=='flyby' and r['status']=='INFEASIBLE'}
 recovered_rows=list(csv.DictReader(REC.open(newline='')))
 binding.update({r['body']:r['binding_limit'] for r in recovered_rows if r['year']=='2026' and r['mission_type_id']=='flyby' and r['status']=='INFEASIBLE'})
 block['never_funded_binding_limits']={b:binding.get(b,'NO_INFEASIBLE_FLYBY_QUOTE') for b in block['never_funded']}
 report['near_misses']={b:{'block_never_funded':b in block['never_funded'],'abstract_fallback_funded':b not in report['cases'][1]['never_funded'],'binding_limit':binding.get(b)} for b in ('POLYMELE','LEUCUS')}
 report['elapsed_seconds']=time.monotonic()-t;report['peak_rss_bytes']=memory()
 REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('FINISHED',round(report['elapsed_seconds'],2),memory(),flush=True)
if __name__=='__main__':main()
