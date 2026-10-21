"""Reprice moons from new giant planet-center flyby minima, then Route 1."""
import csv,json,time,resource,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from decimal import Decimal
from simulation.offworld_mvp.build8.three_arm_stage1.RENDEZVOUS_V2_PAIRED_REPLAY_TEST_ONLY import FlyCampaign,replay
from simulation.offworld_mvp.build8.three_arm_stage1.vehicle_flyby_cost_test_only import price
from simulation.offworld_mvp.build8.route1_all_body_campaign_pr3b import AllBodyCampaign,ALL_BODIES
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 start=time.monotonic();target=P/'PR427_GIANT_MOON_REPLAY_REPORT_TEST_ONLY.json';assert not target.exists()
 old=json.loads((P/'RENDEZVOUS_V2_PAIRED_REPLAY_REPORT_TEST_ONLY.json').read_text());geom=json.loads((P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json').read_text());auth=json.loads((P/'VEHICLE_FLYBY_AUTHORED_TEST_ONLY.json').read_text())
 world={r['body']:r for r in csv.DictReader((P/'RENDEZVOUS_WORLD_AUTHORITY_TEST_ONLY.csv').open())}
 fly={}
 for r in csv.DictReader((P/'VEHICLE_FLYBY_GEOMETRY_TEST_ONLY.csv').open()):
  fly[(int(r['year']),r['body'])]={'model_units':price(float(r['minimum_departure_vinf_km_s']),auth)['model_units'],'parent':''}
 for r in geom['body_years']:
  if r['model_units'] is not None:fly[(r['year'],r['body'])]={'model_units':r['model_units'],'parent':''}
 for year in (2026,2027):
  for body,w in world.items():
   parent=w['parent']
   if parent and (year,parent) in fly:fly[(year,body)]={'model_units':fly[(year,parent)]['model_units'],'parent':parent}
 control=AllBodyCampaign(body_count=90,ceilings_enabled=True)
 ch=replay(control);assert ch=='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
 c=FlyCampaign(fly,'A1_FLYBY_PARENT_MOONS_WITH_GIANTS');h=replay(c)
 receipts=c.receipts;counts=Counter(x['primary_blocker'] for x in c.attempts if x['outcome']=='BLOCKED')
 bodies=defaultdict(list)
 for x in receipts:bodies[x['body']].append(x)
 ranking=sorted([{'body':b,'stages':len(rr),'distinct_sponsors':len(set(x['sponsor'] for x in rr)),'sponsors':sorted(set(x['sponsor'] for x in rr)),'spent_model_units':str(sum((Decimal(x['amount']) for x in rr),Decimal(0)))} for b,rr in bodies.items()],key=lambda x:(-x['stages'],-x['distinct_sponsors'],x['body']))
 unpriced=[]
 for b,w in world.items():
  if w['parent'] and not any((y,b) in fly for y in (2026,2027)):
   unpriced.append({'moon':b,'parent':w['parent'],'reason':'PARENT_NO_SAMPLED_FLYBY_QUOTE' if not any((y,w['parent']) in fly for y in (2026,2027)) else 'UNKNOWN'})
 out={'classification':'TEST_ONLY_NONCANON','numpy_version':__import__('numpy').__version__,'control_sha256':ch,'variant_sha256':h,'funded_stages':len(receipts),'funded_bodies':len(bodies),'cash_model_units':str(sum((Decimal(x['amount']) for x in receipts),Decimal(0))),'blockers':dict(counts),'unpriced_moons':unpriced,'body_ranking':ranking,'top_ten':ranking[:10],'geometry_report_sha256':sha(P/'PR427_GIANT_FLYBY_GEOMETRY_REPORT_TEST_ONLY.json'),'table_manifest_sha256':sha(P/'PR427_GIANT_PARENT_TABLE_MANIFEST_TEST_ONLY.json'),'previous_replay_sha256':sha(P/'RENDEZVOUS_V2_PAIRED_REPLAY_REPORT_TEST_ONLY.json'),'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
 with target.open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
 print('DONE',json.dumps({k:v for k,v in out.items() if k not in ('body_ranking','top_ten')}),flush=True)
 print('TOP_TEN',json.dumps(out['top_ten']),flush=True)
if __name__=='__main__':main()
