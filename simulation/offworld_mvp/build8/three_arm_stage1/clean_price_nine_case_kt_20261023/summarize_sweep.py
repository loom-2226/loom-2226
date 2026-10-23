"""Summarize nine completed clean-price runs; never executes a simulation."""
import csv,hashlib,json
from pathlib import Path
from decimal import Decimal as D
O=Path(__file__).resolve().parent
P=O.parent
summary=json.loads((O/'summary.json').read_text())
assert len(summary['cases'])==9
expected='49fbd0f1015268d24e931b9e1d7083cb8a0cd3f6c02a4942a130d0885695922f'
assert hashlib.sha256((O/'precedence_merged_prices.json').read_bytes()).hexdigest()==expected
assert summary['route1_hash']=='4df0a020fd3714650129f18d78cbfe7440fa35ecb3e4807873aea993c4656430'
assert summary['ceres_equivalence']['result']=='PASS'
assert summary['db_sha256_before']==summary['db_sha256_after']=='e21304e687e63e264edb44f36ff7c68fa3f119307315bce49008711547fa7cde'
old=list(csv.DictReader((P/'unstarted_33_readonly_audit_kt_20261023/unstarted_33.csv').open()))
assert len(old)==33
starts={}
for c in summary['cases']:
 report=json.loads((O/(c['case']+'_report.json')).read_text())
 assert report['projects_started']==c['projects_started']
 for y in report['per_year']:
  for x in y['dominant_started'] or []:
   starts.setdefault(x['body'],[]).append((c['case'],x['year']))
for row in old:
 cases=starts.get(row['body'],[])
 row['first_case_started']=cases[0][0] if cases else 'NEVER'
 row['first_start_year']=cases[0][1] if cases else ''
 row['all_cases_started']=';'.join(c for c,y in cases)
with (O/'unstarted_33_first_case.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(old[0]));w.writeheader();w.writerows(old)
never=[x for x in old if x['first_case_started']=='NEVER'];priced=[x for x in never if x['price_model_units']!='UNPRICED'];cheapest=min(priced,key=lambda x:D(x['price_model_units'])) if priced else None
out={'cases':summary['cases'],'never_started_count':len(never),'cheapest_priced_never':{'body':cheapest['body'],'price_model_units':cheapest['price_model_units']} if cheapest else None,'unpriced_never_count':sum(x['price_model_units']=='UNPRICED' for x in never),'all_bodies_ever_started':len(starts),'source_sha256':expected,'route1_pass':True,'ceres_pass':True,'db_unchanged':True}
(O/'sweep_results.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
lines=['# Clean price: nine-case sponsor refill sensitivity','','TEST_ONLY / NON-CANON. All 90 bodies; 20 sponsors; 2026–2226. Rendezvous, high buyer budget, four-sale cap. No existing source files edited.','','Clean price SHA-256: `'+expected+'`. Strict floor check passes on all campaign-used rendezvous prices; 205 unused below-floor flyby rows are not modified.','','## Nine-case results','','| Treasury share | Material price | Starts | Sponsors | Bodies | Last start | Committed | Returned | Refilled |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
for c in summary['cases']:
 lines.append('| '+ ' | '.join(str(c[k]) for k in ['refill_share','price_multiplier','projects_started','sponsors_ever_started','bodies_ever_started','last_start_year','total_committed','total_returned','total_refilled'])+' |')
lines+=['','## Previously unstarted 33: first case that starts','','Order: treasury share 0, 0.5, 1; within each share material price x1, x3, x10. “NEVER” means no start in any of these nine cases.','','| Body | Group | Price (model units) | First case | Start year |','|---|---|---:|---|---:|']
for group in ['earlier outer 24','six additional moons','unpriced']:
 for x in old:
  if x['group']!=group:continue
  lines.append('| '+' | '.join(str(x[k] or '—') for k in ['body','group','price_model_units','first_case_started','first_start_year'])+' |')
lines+=['',f"**Never started in any case: {len(never)} of the original 33.**",f"Cheapest priced body among them: **{cheapest['body']} at {cheapest['price_model_units']} model units**." if cheapest else 'No priced body remained never-started.','','## Controls','','- Route 1 control hash: `'+summary['route1_hash']+'` PASS.','- Ceres equivalence: PASS (no lifecycle source changed).','- Database SHA-256 before and after: `'+summary['db_sha256_before']+'`.','- Study retry rules unchanged.','- No installs, downloads or pre-existing file edits.','']
(O/'RESULTS.md').write_text('\n'.join(lines))
print(json.dumps({'never':len(never),'cheapest':out['cheapest_priced_never'],'starts':[c['projects_started'] for c in summary['cases']]},sort_keys=True))
