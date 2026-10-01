#!/usr/bin/env python3
"""Fail-closed Gate-1 verifier for the governed LOOM Solar V1 interval."""
import argparse,csv,json,sys
from pathlib import Path
REPO_ROOT=Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0,str(REPO_ROOT))
from src.loom_solar_inspector import Inspector

def main():
 p=argparse.ArgumentParser(); p.add_argument('--database',default='loom_dev'); p.add_argument('--asset-root',default='/home/ubuntu/loom_solar_assets'); p.add_argument('--output',default='engineering/solar_temporal/evidence/solar_game_interval_freeze_2026_2250'); a=p.parse_args()
 out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
 I=Inspector.connect(a.database,a.asset_root)
 start=I.time.parse('2026 JAN 01 TDB'); end=I.time.parse('2251 JAN 01 TDB')
 probes=[start,I.time.parse('2050 JAN 01 TDB'),I.time.parse('2100 JAN 01 TDB'),I.time.parse('2200 JAN 01 TDB'),I.time.parse('2226 JAN 01 TDB'),I.time.parse('2250 JAN 01 TDB'),end]
 rows=[];gaps=[];fails=[]
 bodies=sorted(I.bodies)
 for i,b in enumerate(bodies,1):
  cov=[]
  for c in I.registry.coverage:
   if c.body_id==b and c.status=='QUALIFIED':
    s=max(start,float(c.coverage_start_et));e=min(end,float(c.coverage_end_et))
    if e>=s: cov.append((s,e,c.ephemeris_source_id,I.registry.sources[c.ephemeris_source_id].state_capability))
  cov.sort();cursor=start;used=[]
  for s,e,sid,cap in cov:
   if e<cursor:continue
   if s>cursor:gaps.append({'body_id':b,'gap_start_et':cursor,'gap_end_et':s})
   cursor=max(cursor,e);used.append((sid,cap,s,e))
  if cursor<end:gaps.append({'body_id':b,'gap_start_et':cursor,'gap_end_et':end})
  pres=[]
  for t in probes:
   r=I.record(b,t); pr={'epoch_et':t,'resolution':r['resolution'],'authority_class':r.get('authority_class'),'source':r.get('state',{}).get('provenance',{}).get('ephemeris_source_id'),'reason':r.get('reason')};pres.append(pr)
   if r['resolution']!='RESOLVED':fails.append({'body_id':b,'epoch_et':t,'reason':r.get('reason')})
  rows.append({'body_id':b,'canonical_name':I.bodies[b]['canonical_name'],'continuous_coverage':not any(g['body_id']==b for g in gaps),'sources':[{'source_id':x[0],'capability':x[1],'start_et':x[2],'end_et':x[3]} for x in used],'probe_results':pres})
  print(f'[{i:03d}/{len(bodies)}] {b}: coverage={"PASS" if rows[-1]["continuous_coverage"] else "FAIL"} probes={"PASS" if all(x["resolution"]=="RESOLVED" for x in pres) else "FAIL"}',flush=True)
 payload={'schema':'loom.solar-game-interval-freeze/1.0','interval_semantics':'2026-01-01 TDB inclusive through end of 2250; qualification gate at 2251-01-01 TDB','start_et':start,'end_gate_et':end,'catalog_count':len(rows),'continuous_coverage_count':sum(r['continuous_coverage'] for r in rows),'gap_count':len(gaps),'resolver_probe_count':len(rows)*len(probes),'resolver_failure_count':len(fails),'gaps':gaps,'resolver_failures':fails,'objects':rows,'pass':len(rows)==110 and not gaps and not fails}
 (out/'coverage_matrix.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
 with (out/'coverage_matrix.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['body_id','canonical_name','continuous_2026_2250','source_chain'])
  for r in rows:w.writerow([r['body_id'],r['canonical_name'],r['continuous_coverage'],' | '.join(x['source_id']+':'+x['capability'] for x in r['sources'])])
 print(json.dumps({k:payload[k] for k in ('catalog_count','continuous_coverage_count','gap_count','resolver_probe_count','resolver_failure_count','pass')},indent=2),flush=True)
 raise SystemExit(0 if payload['pass'] else 2)
if __name__=='__main__':main()
