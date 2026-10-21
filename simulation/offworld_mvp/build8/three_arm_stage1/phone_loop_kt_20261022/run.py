"""Small TEST_ONLY phone story; genuine pinned quotes, labeled synthetic joins."""
import csv,hashlib,json,sys
from decimal import Decimal as D
from pathlib import Path
from simulation.offworld_mvp.build8.return_routing import DESTINATIONS,SOURCE
P=Path(__file__).resolve().parent
raw=(P/'scenario.json').read_bytes();s=json.loads(raw)
def sha(b):return hashlib.sha256(b).hexdigest()
def money(v):return f'${v:,.2f}'
def d(k):return D(s[k])
def emit(year,who,what,delta=None):
 events.append({'year':year,'who':who,'what':what,'usd_delta':str(delta) if delta is not None else None})
def source(key,hashkey):
 b=(P/s[key]).resolve().read_bytes();assert sha(b)==s[hashkey],key;return b
quotes=list(csv.DictReader(source('source_quotes','source_quote_sha256').decode().splitlines()))
source('source_ceres','source_ceres_sha256');source('source_return_table','source_return_sha256');source('source_material_prior','source_material_prior_sha256')
assert s['classification']=='TEST_ONLY_PLACEHOLDER_PHONE_LOOP'
assert len(s['prior_rows'])==2
assert s['material_family_for_sale']=='VOLATILES' # Fixture supports volatiles only; reject other family instead of inventing it.
assert D(s['prior_rows'][s['first_mission']['body']]['free_ice_weight'])>0
rule=DESTINATIONS[(SOURCE,s['owner_type'])]
assert rule[1]==s['authored_appropriation_delay_years']
assert sum(d(k) for k in ('financier_return_share','local_reinvest_share','owner_return_share','reserve_share'))==1
assert d('quantity_model_units')<=min(d('recoverable_model_units'),d('productive_capacity_model_units'),d('buyer_demand_model_units'))
def quote(m,year):
 rows=[r for r in quotes if (r['body'],r['mission_type_id'],r['vehicle_class_id'],r['year'])==(m['body'],m['mission_type_id'],m['vehicle_class_id'],str(year))]
 assert len(rows)==1 and rows[0]['status']=='PRICED_TEST_ONLY',(m,year,rows)
 return D(rows[0]['lowest_price_usd']),rows[0]
start=s['first_mission']['year'];q1,qrow=quote(s['first_mission'],start)
# HELD 2026 rule: next departure quote comes from the 2026 price table, regardless of next calendar year.
q2,nextrow=quote(s['next_mission'],start)
assert qrow['run_identity']==nextrow['run_identity']
budget=d('initial_budget_usd');assert budget>=q1
ident=sha(json.dumps({'scenario_sha256':sha(raw),'quote_sha256':s['source_quote_sha256'],'return_table_sha256':s['source_return_sha256'],'ceres_sha256':s['source_ceres_sha256'],'material_prior_sha256':s['source_material_prior_sha256']},sort_keys=True).encode())
events=[];emit(start,s['sponsor'],'Opening mission budget (PLACEHOLDER USD)',budget)
budget-=q1;emit(start,s['sponsor'],f'Funds {s["first_mission"]["body"]} {s["first_mission"]["mission_type_id"]} at HELD 2026 PR quote (REAL quote, PLACEHOLDER payment)',-q1)
completion=start+s['mission_completion_delay_years'];emit(completion,s['executor'],f'{s["first_mission"]["body"]} mission completed (PLACEHOLDER timing/outcome)',D(0))
family=s['material_family_for_sale'];emit(completion,s['sponsor'],f'{family} permitted by positive free-ice prior (PLACEHOLDER material-truth inference)',D(0))
operation=completion+s['development_delay_years']+s['extraction_delay_years'];quantity=d('quantity_model_units');gross=quantity*d('unit_sale_price_model_currency');conv=d('sale_unit_conversion_usd_per_model_currency');gross_usd=gross*conv
emit(operation,s['executor'],f'Extracts {quantity} model resource units; Ceres yield fixture (PLACEHOLDER)',D(0))
emit(operation,s['buyer'],f'Buys {quantity} {family} units; Ceres sale 0.050 model currency/unit, synthetic USD bridge',-gross_usd)
owner=gross*d('owner_return_share')*conv;fin=gross*d('financier_return_share')*conv;local=gross*d('local_reinvest_share')*conv;reserve=gross*d('reserve_share')*conv
assert owner+fin+local+reserve==gross_usd
emit(operation,s['owner'],f'Owner share routed to {rule[0]} (REAL routing rule; PLACEHOLDER amounts)',owner)
emit(operation,'financier',f'Financier claim share (PLACEHOLDER claim)',fin)
emit(operation,'project',f'Local reinvestment share (PLACEHOLDER)',local)
emit(operation,'project',f'Retained reserve (PLACEHOLDER)',reserve)
return_year=operation+rule[1];appropriation=owner*d('return_to_sponsor_fraction');emit(return_year,s['sponsor'],f'Authored treasury appropriation after {rule[1]} years (PLACEHOLDER decision)',appropriation);budget+=appropriation
assert budget>=q2,('INSUFFICIENT_REFILL',budget,q2)
budget-=q2;emit(return_year,s['sponsor'],f'Funds next mission: {s["next_mission"]["body"]}, HELD {start} quote (REAL price; PLACEHOLDER choice)',-q2)
assert budget>=0
result={'classification':s['classification'],'run_identity':ident,'scenario_sha256':sha(raw),'source_hashes':{k:s[k] for k in s if k.endswith('_sha256')},'events':events,'remaining_budget_usd':str(budget),'quote_first_usd':str(q1),'quote_next_usd':str(q2),'gross_sale_model_currency':str(gross),'gross_sale_placeholder_usd':str(gross_usd),'owner_return_placeholder_usd':str(owner),'parts':{'mission_quote_2026':'REAL: pinned PR427 TEST_ONLY cost-layer price, not market-calibrated','held_2026_rule':'REAL: price lookup uses first year for both missions','mission_funding':'PLACEHOLDER: sponsor budget and payment','mission_completion':'PLACEHOLDER: elapsed years and success','material_prior':'REAL: pinned Build6E authored free-ice prior','material_family_inference':'PLACEHOLDER: positive free-ice prior implies VOLATILES; not generated hidden truth','resource_stock_and_yield':'PLACEHOLDER: Ceres synthetic values reused','extraction':'PLACEHOLDER: no physical kernel operation','sale_quantity_and_model_price':'PLACEHOLDER: Ceres synthetic market fixture','usd_conversion':'PLACEHOLDER: arbitrary bridge from MODEL_CURRENCY to USD','buyer_payment':'PLACEHOLDER: not cleared by kernel','return_destination_and_delay':'REAL: main return-routing owner-type rule','distribution_amounts':'PLACEHOLDER: Ceres synthetic shares, not executed kernel transfers','treasury_appropriation':'PLACEHOLDER: authored decision at eligible year','next_mission':'PLACEHOLDER: selection and payment using REAL pinned 2026 quote','conservation':'REAL within illustrative ledger arithmetic only, not kernel-qualified'}}
(P/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
lines=['# One crude Route 1 loop','',f'Run identity: `{ident}`',f'Scenario SHA-256: `{sha(raw)}`','', 'TEST ONLY. Money is USD placeholders except the pinned mission quotes.','', '## Timeline','']
for e in events:
 delta=e['usd_delta'];amt='no cash' if delta is None else ('in ' if D(delta)>0 else 'out ' if D(delta)<0 else 'no cash ')+money(abs(D(delta)))
 lines.append(f'{e["year"]} | {e["who"]} | {e["what"]} | {amt}')
lines.extend(['','## Parts','', '| Part | REAL or PLACEHOLDER |','|---|---|'])
for k,v in result['parts'].items():lines.append(f'| {k.replace("_"," ")} | {v} |')
lines.extend(['',f'Closing sponsor budget: {money(budget)}','',f'Pinned quote SHA-256: `{s["source_quote_sha256"]}`',f'Ceres source SHA-256: `{s["source_ceres_sha256"]}`',f'Return routing SHA-256: `{s["source_return_sha256"]}`',f'Material prior SHA-256: `{s["source_material_prior_sha256"]}`',''])
(P/'PHONE_REPORT.md').write_text('\n'.join(lines))
print('\n'.join(lines))
