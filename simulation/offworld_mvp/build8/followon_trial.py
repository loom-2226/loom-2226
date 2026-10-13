"""Opt-in two-sponsor Build 8 follow-on proof; PR 2 adds remaining sponsors/bodies.

Four-body expansion is intentionally NOT implemented here. The baseline runner,
default rows/fingerprints and standalone NASA A1/A2 remain unchanged when off.
"""
from decimal import Decimal as D
from .route1_gate1 import run_gate1, CEILINGS
from .route1_gate2 import run_gate2
from .followon_rules import trial_rules, FIXED_CLAIM_ORDER
from .followon_execution import route1_funding_handoff, admitted_evidence

def _classify(row):
    status=row['status']
    policy=row['policy']
    reason=row['reason']
    if status=='WAIT_CEILING_BELOW_PRICE':
        return 'BUILT_IN', 'ASSIGNED_PRICE_OVER_SPONSOR_CEILING'
    if status in ('WAIT_CASH_BELOW_PRICE','WAIT_CUMULATIVE_LIMIT',
                  'WAIT_CLAIMED_BY_OTHER'):
        return 'EMERGENT', status
    if reason in ('CONCENTRATION','CEILING'):
        return 'EMERGENT', 'FINANCIER_'+reason
    if policy in ('REJECT','DEFER','BLOCKED_UNKNOWN'):
        return 'EMERGENT', 'FINANCIER_'+reason
    return None, None

def run_trial(order=FIXED_CLAIM_ORDER,share=D('.25'),carry_cap=2):
    """Bounded Scenario B pilot. An A1 approval precedes any reconstructed study."""
    if D(share)!=D('.25') or carry_cap!=2:
        raise ValueError('PR 1 qualifies only Scenario B / 25% / 2x trial carry')
    trial=trial_rules(order)
    initial,_=run_gate1(D(share),scenario='B',run_setting={'name':'follow_on','payload':trial})
    a1={}
    for sponsor,rule in trial['rules'].items():
        opening=next(r for r in initial if r['sponsor']==sponsor)
        if not opening['disbursement']:
            # Later-year A1 starts are part of PR 2; fail honestly, never forge a result.
            raise RuntimeError('PR1_REQUIRES_FUNDED_2026_A1:'+sponsor)
        a1[sponsor]=route1_funding_handoff({**opening,'year':2026},sponsor,rule['a1'])
    trial['evidence']={s:admitted_evidence(st) for s,st in a1.items()}
    ledger,earth=run_gate2(D(share),carry_cap=carry_cap,end_year=2035,
                            run_setting={'name':'follow_on','payload':trial})
    a2={}
    for sponsor,rule in trial['rules'].items():
        opening=next(r for r in ledger if r['sponsor']==sponsor and r['year']==2026)
        assert opening['disbursement']==a1[sponsor]['disbursement'], 'A1 disbursement drift'
        funded=[r for r in ledger if r['sponsor']==sponsor and r['year']>2026
                and r['disbursement']]
        if len(funded)>1:
            raise AssertionError('more than one funded follow-on per sponsor')
        if funded:
            r=funded[0]
            if r['year']>2035:
                raise AssertionError('financing after cutoff')
            a2[sponsor]=route1_funding_handoff(r,sponsor,rule['a2'],prior=a1[sponsor])
    report=[]
    stops={}
    for sponsor,rule in trial['rules'].items():
        if sponsor in a2:
            standing=a2[sponsor]['result'].standing.value
            stops[sponsor]=('RESULT_'+standing if standing!='SUPPORTS_ADVANCE'
                            else 'NO_NEXT_AUTHORED_ACTIVITY')
        else:
            stops[sponsor]='FINANCING_HORIZON_ENDED'
    stop_year={s:int(x['review'].effective_time) for s,x in a2.items()}
    for r in ledger:
        sponsor=r['sponsor']
        if sponsor not in trial['rules']:
            continue
        rule=trial['rules'][sponsor]
        cls,code=_classify(r)
        stage=('A1' if r['year']==2026 or
               not any(x['year']<r['year'] and x['sponsor']==sponsor
                       and x['disbursement'] for x in ledger)
               else 'A2')
        event='REQUEST' if r['policy']!='NOT_EVALUATED' else 'NO_REQUEST'
        final=(stops[sponsor] if r['year']>=stop_year.get(sponsor,2035)
               else None)
        report.append({
            'scenario':'B','share':str(D(share)),'claim_order':tuple(order),
            'year':r['year'],'sponsor':sponsor,'body':rule['body'],
            'stage':stage,'activity':rule['a1'] if stage=='A1' else rule['a2'],
            'event':event,'requested':r['authored_price'] if event=='REQUEST' else None,
            'available':r['available'] if 'available' in r else r['opening'],
            'ceiling':str(D(CEILINGS[sponsor])),
            'lifetime_limit':rule['lifetime_limit'],
            'decision':r['policy'],'financier_reason':r['reason'],
            'status':r['status'],'failure_class':cls,'failure_reason':code,
            'disbursement':r['disbursement'],
            'closing':r['closing'],'lapsed':r.get('lapsed_amount','0'),
            'chain_stop':final})
    for sponsor in trial['rules']:
        if len([r for r in report if r['sponsor']==sponsor])!=10:
            raise AssertionError('missing sponsor-year report rows')
        paid=sum((D(r['authored_price']) for r in ledger
                  if r['sponsor']==sponsor and r['disbursement']),D(0))
        if paid>D(trial['rules'][sponsor]['lifetime_limit']):
            raise AssertionError('sponsor cumulative limit exceeded')
        if sponsor in a2 and a2[sponsor]['result'].standing.value!='INSUFFICIENT':
            raise AssertionError('PR 1 authored A2 result drift')
    earth.assert_invariants()
    return {'classification':'AUTHORED TEST_ONLY NON-CANON',
            'claim_order':tuple(order),'scenario':'B','share':str(D(share)),
            'carry_cap':'2x next authored activity price',
            'yearly':tuple(report),'stops':stops,
            'earth_fingerprint':earth.fingerprint(),
            'a1_fingerprints':{s:x['kernel'].fingerprint() for s,x in a1.items()},
            'a2_fingerprints':{s:x['kernel'].fingerprint() for s,x in a2.items()},
            'a1':a1,'a2':a2,'ledger':ledger}

def compare_order():
    """Report semantic outcomes, not transaction IDs that depend on evaluation order."""
    a=run_trial(order=FIXED_CLAIM_ORDER)
    b=run_trial(order=tuple(reversed(FIXED_CLAIM_ORDER)))
    def decisions(run):
        return {(r['sponsor'],r['year']):(r['decision'],r['financier_reason'],
                r['status'],bool(r['disbursement']),r['failure_class'],
                r['chain_stop']) for r in run['yearly']}
    changed=[key for key in sorted(decisions(a))
             if decisions(a)[key]!=decisions(b)[key]]
    return {'recorded_order':FIXED_CLAIM_ORDER,
            'reversed_order':tuple(reversed(FIXED_CLAIM_ORDER)),
            'outcome_changed':bool(changed),'changed_sponsor_years':changed}
