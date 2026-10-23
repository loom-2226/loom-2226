"""Adjacent TEST ONLY sponsor selection. Does not alter the four-case runner."""
import csv, hashlib, json
from decimal import Decimal as D
from pathlib import Path
from .outcome_resolver import resolve
from .sponsor_ledger_slice import check_ledger, canonical, sha

HERE=Path(__file__).resolve().parent

def run(scenario_path=HERE/'SPONSOR_SELECTION_SCENARIO.json', scenario_override=None):
    path=Path(scenario_path)
    raw=path.read_bytes()
    scenario=json.loads(raw) if scenario_override is None else scenario_override
    if scenario['classification']!='TEST_ONLY_NONCANON_NONRUNTIME': raise ValueError('CLASSIFICATION')
    quote_raw=(path.parent/scenario['quote_csv']).read_bytes()
    cast_raw=(path.parent/scenario['executor_cast_file']).resolve().read_bytes()
    if sha(quote_raw)!=scenario['quote_sha256']: raise ValueError('QUOTE_HASH_MISMATCH')
    if sha(cast_raw)!=scenario['executor_cast_sha256']: raise ValueError('CAST_HASH_MISMATCH')
    cast=json.loads(cast_raw)['casts'][scenario['executor_cast_id']]
    executor=next(e for e in cast['executors'] if e['name']==scenario['executor_name'])
    b=executor['beliefs']
    chance=D(b['success'])/(D(b['success'])+D(b['failure']))
    if scenario['tie_break']!='PRIORITY_THEN_ID_ASC': raise ValueError('TIE_BREAK')
    quotes={}
    for q in csv.DictReader(quote_raw.decode().splitlines()):
        if q['run_identity']!=scenario['quote_run_identity']: raise ValueError('QUOTE_IDENTITY_MISMATCH')
        key=(q['year'],q['body'],q['mission_type_id'],q['vehicle_class_id'])
        if key in quotes: raise ValueError('DUPLICATE_QUOTE')
        quotes[key]=q
    ids=[c['candidate_id'] for c in scenario['candidates']]
    if len(ids)!=len(set(ids)): raise ValueError('DUPLICATE_CANDIDATE')
    identity=sha(canonical(dict(scenario_sha256=sha(canonical(scenario)),quote_sha256=sha(quote_raw),
        quote_run_identity=scenario['quote_run_identity'],cast_sha256=sha(cast_raw),
        resolver_sha256=sha((HERE/'outcome_resolver.py').read_bytes()),
        selector_sha256=sha(Path(__file__).read_bytes()))))
    output=[]
    for sponsor in scenario['sponsors']:
        initial=D(sponsor['initial_budget_usd'])
        rows=[]
        for c in scenario['candidates']:
            cid=c['candidate_id']
            delivered,failed=map(D,sponsor['values'][cid])
            q=quotes.get((str(c['year']),c['target_body_id'],c['mission_type_id'],c['vehicle_class_id']))
            status=q['status'] if q else 'MISSING'
            price=D(q['lowest_price_usd']) if q and status=='PRICED_TEST_ONLY' and q['lowest_price_usd'] else None
            expected=chance*delivered+(1-chance)*failed
            surplus=expected-price if price is not None else None
            reason=('MISSING' if q is None else 'INFEASIBLE' if status=='INFEASIBLE'
                else 'UNPRICED' if price is None else 'UNAFFORDABLE' if price>initial else None)
            rows.append(dict(candidate_id=cid,target_body_id=c['target_body_id'],mission_type_id=c['mission_type_id'],
                vehicle_class_id=c['vehicle_class_id'],year=c['year'],priority=c['priority'],
                quote_status=status,quote_usd=str(price) if price is not None else None,
                value_if_delivered_test_only_usd=str(delivered),value_if_failed_test_only_usd=str(failed),
                expected_value_test_only_usd=str(expected),expected_surplus_test_only_usd=str(surplus) if surplus is not None else None,
                exclusion_reason=reason,best_departure_date=q['best_departure_date'] if q else '',
                best_flight_days=q['best_flight_days'] if q else ''))
        eligible=sorted((r for r in rows if r['exclusion_reason'] is None),
            key=lambda r:(-D(r['expected_surplus_test_only_usd']),r['priority'],r['candidate_id']))
        winner=eligible[0] if eligible else None
        threshold=D(sponsor.get('minimum_surplus_usd',scenario['minimum_surplus_usd']))
        defer=sponsor.get('defer',False)
        decision=('DEFER' if defer else 'REJECT' if winner is None or D(winner['expected_surplus_test_only_usd'])<threshold else 'ACCEPT')
        selected=winner if decision=='ACCEPT' else None
        spent=D(selected['quote_usd']) if selected else D(0)
        balance=initial-spent
        check_ledger(initial,spent,balance)
        outcome=resolve(sponsor.get('outcome_seed',scenario['outcome_seed']),chance,
            sponsor['sponsor_id']+'|'+selected['candidate_id']) if selected else {'outcome':'NOT_EXECUTED'}
        output.append(dict(sponsor_id=sponsor['sponsor_id'],decision=decision,
            selected_candidate_id=selected['candidate_id'] if selected else None,
            best_candidate_id=winner['candidate_id'] if winner else None,
            minimum_surplus_test_only_usd=str(threshold),success_chance_test_only=str(chance),
            outcome=outcome,candidates=rows,ledger=dict(initial_budget_usd=str(initial),
                spent_usd=str(spent),balance_usd=str(balance),selected_quote_usd=selected['quote_usd'] if selected else None,
                best_departure_date=selected['best_departure_date'] if selected else '',
                best_flight_days=selected['best_flight_days'] if selected else '')))
    return dict(classification='TEST_ONLY_NONCANON_NONRUNTIME',price_warning='TEST ONLY / UNCALIBRATED PRICE PROXY',
        value_warning='ALL SPONSOR VALUES ARE ARBITRARY TEST ONLY DECISION UTILITY, NOT LEDGER FUNDS',
        run_identity=identity,scenario_sha256=sha(canonical(scenario)),scenario_file_sha256=sha(raw),
        quote_sha256=sha(quote_raw),cast_sha256=sha(cast_raw),
        resolver_sha256=sha((HERE/'outcome_resolver.py').read_bytes()),
        selector_sha256=sha(Path(__file__).read_bytes()),quote_run_identity=scenario['quote_run_identity'],
        tie_break=scenario['tie_break'],sponsors=output)

if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
