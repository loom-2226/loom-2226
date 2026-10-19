"""TEST ONLY quote-to-ledger slice; does not invoke or modify frozen executor."""
import csv
import hashlib
import json
from decimal import Decimal as D
from pathlib import Path
from .outcome_resolver import resolve

HERE = Path(__file__).resolve().parent

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def check_ledger(initial, spent, balance):
    if initial != spent + balance:
        raise AssertionError('LEDGER_CONSERVATION_FAILED')

def run(scenario_path=HERE/'SPONSOR_LEDGER_SCENARIO.json'):
    scenario_path = Path(scenario_path)
    raw = scenario_path.read_bytes(); scenario = json.loads(raw)
    if scenario['classification'] != 'TEST_ONLY_NONCANON_NONRUNTIME': raise ValueError('NOT_TEST_ONLY')
    quote_path = (scenario_path.parent/scenario['quote_csv']).resolve()
    quote_raw = quote_path.read_bytes()
    if sha(quote_raw) != scenario['quote_sha256']: raise ValueError('QUOTE_HASH_MISMATCH')
    cast_path = (scenario_path.parent/scenario['executor_cast_file']).resolve()
    cast_raw = cast_path.read_bytes()
    if sha(cast_raw) != scenario['executor_cast_sha256']: raise ValueError('CAST_HASH_MISMATCH')
    cast = json.loads(cast_raw)['casts'][scenario['executor_cast_id']]
    executors = {e['name']:e for e in cast['executors']}
    if scenario['chance_source'] != 'EXECUTOR_BELIEFS_SUCCESS_OVER_SUCCESS_PLUS_FAILURE': raise ValueError('CHANCE_SOURCE')
    if scenario['ledger_debit_rule'] != 'DEBIT_QUOTE_ON_ACCEPT': raise ValueError('DEBIT_RULE')
    module_sha = sha((HERE/'outcome_resolver.py').read_bytes())
    runner_sha = sha(Path(__file__).read_bytes())
    identity = sha(canonical({'scenario_sha256':sha(raw),'quote_sha256':sha(quote_raw),
      'quote_run_identity':scenario['quote_run_identity'],'cast_sha256':sha(cast_raw),
      'resolver_sha256':module_sha,'runner_sha256':runner_sha}))
    quotes = {}
    for r in csv.DictReader(quote_raw.decode().splitlines()):
        if r['run_identity'] != scenario['quote_run_identity']: raise ValueError('QUOTE_IDENTITY_MISMATCH')
        key = (r['year'],r['body'],r['vehicle_class_id'],r['mission_type_id'])
        if key in quotes: raise ValueError('DUPLICATE_QUOTE')
        quotes[key] = r
    results=[]
    for case in scenario['cases']:
        if case['decision_rule'] != 'AFFORDABLE_ACCEPT_ELSE_REJECT': raise ValueError('DECISION_RULE')
        key=(str(case['year']),case['target_body_id'],case['vehicle_class_id'],case['mission_type_id'])
        q=quotes.get(key)
        initial=D(case['initial_budget_usd']); spent=D('0'); balance=initial
        check_ledger(initial,spent,balance)
        quoted = q is not None and q['status']=='PRICED_TEST_ONLY' and q['lowest_price_usd']!=''
        amount=D(q['lowest_price_usd']) if quoted else None
        decision='ACCEPT' if quoted and amount<=balance else 'REJECT'
        if decision != case['expected_decision']: raise AssertionError('EXPECTED_DECISION_MISMATCH')
        if decision=='ACCEPT':
            beliefs=executors[case['executor_name']]['beliefs']
            chance=D(beliefs['success'])/(D(beliefs['success'])+D(beliefs['failure']))
            outcome=resolve(case['outcome_seed'],chance,case['case_id'])
            spent+=amount;balance-=amount
        else: outcome={'outcome':'NOT_EXECUTED'}
        check_ledger(initial,spent,balance)
        entry={'case_id':case['case_id'],'sponsor_id':case['sponsor_id'],
          'target_body_id':case['target_body_id'],'vehicle_class_id':case['vehicle_class_id'],
          'mission_type_id':case['mission_type_id'],'quote_status':q['status'] if q else 'MISSING',
          'quote_test_only':True,'best_departure_date':q['best_departure_date'] if q else '',
          'best_flight_days':q['best_flight_days'] if q else '',
          'decision':decision,'outcome':outcome,'initial_budget_usd':str(initial),
          'spent_usd':str(spent),'balance_usd':str(balance),
          'quote_usd':q['lowest_price_usd'] if q else '',
          'executor_name':case['executor_name'] if decision=='ACCEPT' else None,
          'chance_basis':'PINNED_EXECUTOR_BELIEFS_TEST_ONLY' if decision=='ACCEPT' else None}
        results.append(entry)
    return {'classification':'TEST_ONLY_UNCALIBRATED_PRICE_PROXY','run_identity':identity,
      'quote_sha256':sha(quote_raw),'scenario_sha256':sha(raw),
      'cast_sha256':sha(cast_raw),'resolver_sha256':module_sha,'runner_sha256':runner_sha,
      'cases':results}

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
