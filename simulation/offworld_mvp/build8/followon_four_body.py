"""AUTHORED / TEST_ONLY / NON-CANON four-body financing histories, Build 8 only.

A single Route 1 ledger decides annual finance. Independently reconstructed 6C
stages supply *future* evidence, admitted only in/after its review year.
No live cash duplication and no financing after 2035.
"""
from decimal import Decimal as D
from .followon_rules import FOUR_BODY_ORDER, four_body_rules
from .followon_execution import route1_funding_handoff, admitted_evidence
from .followon_trial import _classify
from .route1_gate2 import run_gate2

def run_four_body(scenario='B',share=D('.25'),overrides=True,order=FOUR_BODY_ORDER,
                  assignments=None,portfolio=None,participants=None):
    """Run ONE independent counterfactual, returning actual funding and study events."""
    if scenario not in ('A','B') or D(share) not in (D('.10'),D('.25')):
        raise ValueError('Scenario A/B and shares 10%/25% only')
    trial=four_body_rules(order,overrides,assignments=assignments,
                          portfolio=portfolio,participants=participants)
    stages={}
    events=[]
    def on_year(year,year_rows,earth):
        for row in year_rows:
            sponsor=row['sponsor']
            if sponsor not in trial['rules'] or not row['disbursement']:
                continue
            rule=trial['rules'][sponsor]
            previous=stages.get(sponsor,{}).get('A1')
            which='A2' if previous is not None else 'A1'
            if which=='A2' and 'A2' in stages[sponsor]:
                raise AssertionError('duplicate funded follow-on')
            stage=route1_funding_handoff(row,sponsor,rule[which.lower()],
                prior=previous,portfolio=portfolio)
            stages.setdefault(sponsor,{})[which]=stage
            if which=='A1':
                trial['evidence'][sponsor]=admitted_evidence(stage)
            events.extend((
                {'time':str(stage['start']),'year':int(stage['start']),
                 'sponsor':sponsor,'body':rule['body'],
                 'event':which+'_START','activity':stage['activity']},
                {'time':str(stage['completion']),'year':int(stage['completion']),
                 'sponsor':sponsor,'body':rule['body'],
                 'event':which+'_RESULT_'+stage['result'].standing.value,
                 'activity':stage['activity']},
                {'time':str(stage['admitted'].admitted_at),
                 'year':int(stage['admitted'].admitted_at),
                 'sponsor':sponsor,'body':rule['body'],
                 'event':which+'_ADMITTED','activity':stage['activity']},
                {'time':str(stage['review'].effective_time),
                 'year':int(stage['review'].effective_time),
                 'sponsor':sponsor,'body':rule['body'],
                 'event':which+'_REVIEW_'+stage['review'].outcome.value,
                 'activity':stage['activity']},
            ))
    trial['on_year']=on_year
    ledger,earth=run_gate2(D(share),carry_cap=2,end_year=2035,
                            followon_trial=trial,scenario=scenario)
    rules=trial['rules']
    yearly=[]
    for row in ledger:
        sponsor=row['sponsor']
        if sponsor not in rules:
            continue
        rule=rules[sponsor]
        stage='A2' if any(r['sponsor']==sponsor and r['year']<row['year']
                            and r['disbursement'] for r in ledger) else 'A1'
        failure_class,failure_reason=_classify(row)
        trial_ceiling=D(trial['ceilings'][sponsor])
        # The impossible authored assignment is BUILT_IN even if its window
        # subsequently closes or somebody else claims the opportunity.
        if D(rule[stage.lower()+'_price'])>trial_ceiling:
            failure_class,failure_reason='BUILT_IN','ASSIGNED_PRICE_OVER_SPONSOR_CEILING'
        elif row['status']=='WAIT_WINDOW_EXPIRED':
            failure_class,failure_reason='EMERGENT','WINDOW_EXPIRED'
        elif row['status']=='WAIT_CLAIMED_BY_OTHER':
            failure_class,failure_reason='EMERGENT','CLAIMED_BY_OTHER'
        request=row['policy']!='NOT_EVALUATED'
        yearly.append({
            'scenario':scenario,'share':str(D(share)),'overrides':bool(overrides),
            'claim_order':tuple(order),'year':row['year'],'sponsor':sponsor,
            'body':rule['body'],'stage':stage,
            'activity':rule[stage.lower()],'event':'REQUEST' if request else 'NO_REQUEST',
            'requested':row['authored_price'] if request else None,
            'available':row.get('available',row['opening']),
            'ceiling':str(D(trial['ceilings'][sponsor])),
            'lifetime_limit':rule['lifetime_limit'],
            'decision':row['policy'],'financier_reason':row['reason'],
            'status':row['status'],'failure_class':failure_class,
            'failure_reason':failure_reason,'disbursement':row['disbursement'],
            'closing':row['closing'],'lapsed':row.get('lapsed_amount','0')})
    by_body={}
    for body in dict.fromkeys(rule['body'] for rule in rules.values()):
        funded=[s for s,rule in rules.items()
                if rule['body']==body and 'A1' in stages.get(s,{})]
        if len(funded)>1:
            raise AssertionError('duplicate funded claimant for body '+body)
        claimant=funded[0] if funded else None
        acts=stages.get(claimant,{}) if claimant else {}
        a1=acts.get('A1');a2=acts.get('A2')
        sponsor_rows=[r for r in yearly if r['sponsor']==claimant] if claimant else []
        if a2:
            standing=a2['result'].standing.value
            stop=('RESULT_'+standing if standing!='SUPPORTS_ADVANCE'
                  else 'NO_NEXT_AUTHORED_ACTIVITY')
        elif a1:
            if D(rules[claimant]['a2_price'])>D(trial['ceilings'][claimant]):
                stop='FOLLOWON_BUILT_IN_CEILING'
            elif any(r['status']=='WAIT_WINDOW_EXPIRED' for r in sponsor_rows):
                stop='WINDOW_EXPIRED'
            else:
                stop='FINANCING_HORIZON_ENDED'
        else:
            stopped=[r for r in yearly if r['body']==body]
            if stopped and all(D(rules[r['sponsor']]['a1_price'])>
                              D(trial['ceilings'][r['sponsor']])
                              for r in stopped):
                stop='BUILT_IN_CEILING'
            elif any(r['status']=='WAIT_WINDOW_EXPIRED' for r in stopped):
                stop='WINDOW_EXPIRED'
            else:
                stop='UNFUNDED_BY_2035'
        def record(stage):
            return (None if stage is None else {
                'activity':stage['activity'],
                'funded_year':next(r['year'] for r in yearly if r['sponsor']==claimant
                                  and r['disbursement'] and r['activity']==stage['activity']),
                'funding_tx':stage['disbursement'],'start':str(stage['start']),
                'completion':str(stage['completion']),
                'result':stage['result'].standing.value,
                'review':stage['review'].outcome.value,
                'review_at':str(stage['review'].effective_time)})
        by_body[body]={'claimant':claimant,'a1':record(a1),'a2':record(a2),'stop':stop}
    # Specific per-sponsor/year outputs also describe losers and actors never financed.
    for sponsor,rule in rules.items():
        rows=[r for r in yearly if r['sponsor']==sponsor]
        if len(rows)!=10:
            raise AssertionError('missing annual sponsor rows')
        financed=[r for r in rows if r['disbursement']]
        paid=sum((D(r['requested']) for r in financed),D(0))
        if paid>D(rule['lifetime_limit']) or len(financed)>2:
            raise AssertionError('funding exceeds cumulative/stage bounds')
        if len([r for r in rows if r['stage']=='A2' and r['event']=='REQUEST'
                and r['year']==2035])>1:
            raise AssertionError('repeat follow-on request')
        if any(r['year']>2035 for r in financed):
            raise AssertionError('financing after available Earth horizon')
        for r in rows:
            review_time=(stages[sponsor]['A1']['review'].effective_time
                         if r['stage']=='A2' and 'A1' in stages.get(sponsor,{})
                         else D(r['year']))
            event_time=max(D(r['year']),review_time) if r['event']=='REQUEST' else D(r['year'])
            events.append({'time':str(event_time),'year':r['year'],'sponsor':sponsor,
                'body':rule['body'],'event':('FUNDED_'+r['stage'] if r['disbursement']
                else r['status'] if r['event']=='REQUEST' else r['financier_reason']),
                'activity':r['activity']})
    order_index={s:i for i,s in enumerate(order)}
    events.sort(key=lambda e:(D(e['time']),order_index[e['sponsor']],e['event']))
    earth.assert_invariants()
    return {'classification':'AUTHORED TEST_ONLY NON-CANON','scenario':scenario,
        'share':str(D(share)),'overrides':bool(overrides),'claim_order':tuple(order),
        'carry_cap':'2x next authored activity price','annual':tuple(yearly),
        'timeline':tuple(events),'bodies':by_body,'stages':stages,'ledger':ledger,
        'earth_fingerprint':earth.fingerprint()}
