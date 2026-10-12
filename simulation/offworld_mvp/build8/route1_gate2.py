"""Route 1 Gate 2: 2027-2029 Scenario B continuation on one conserved ledger."""
from decimal import Decimal as D
from .route1_gate1 import (run_gate1, CEILINGS, DEFAULT_PRICE, EVIDENCE,
    EVIDENCE_TAG, PUBLIC, PRIVATE, PREFERENCES, PROJECTS, EARTH_V4_ROOT)
from .country_capital_input import load_investment_capacity
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from offworld_kernel.prospecting import derive_mobilization
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policies.manifest import test_only_manifest

def run_gate2(share=D('.10'),root=EARTH_V4_ROOT,carry_cap=None,end_year=2029,
              nasa_a2_evidence=None,followon_trial=None):
    """Returns rows for 2026-2029, including original Gate 1 2026 B results."""
    share=D(share)
    if nasa_a2_evidence is not None and followon_trial is not None:
        raise ValueError('legacy NASA A2 and general follow-ons cannot be combined')
    trial_rules={} if followon_trial is None else followon_trial['rules']
    trial_order=() if followon_trial is None else tuple(followon_trial['order'])
    if len(set(trial_order))!=len(trial_order) or set(trial_order)!=set(trial_rules):
        raise ValueError('trial order must list each assigned sponsor once')
    ordering={s:i for i,s in enumerate(trial_order)}
    if not isinstance(end_year,int) or not 2029 <= end_year <= 2035:
        raise ValueError('end_year must be 2029..2035, bounded by Earth investment data')
    if carry_cap not in (None,0,1,2):
        raise ValueError('carry cap must be unlimited, 0, 1, or 2')
    rows,k=run_gate1(share,root=root,scenario='B',
        project_price_override={'NASA':D('.350')} if nasa_a2_evidence else None,
        followon_trial=followon_trial)
    for row in rows:
        row['year']=2026
    sink='route1:earth:carry_lapse'
    if carry_cap is not None:
        k.add_account(sink,'ROUTE1_EARTH_LAPSE','EARTH:USA',
                      AccountKind.EARTH_BOUNDARY)
    def lapse(year,annual_rows):
        if carry_cap is None:
            return
        for row in annual_rows:
            sponsor=row['sponsor']
            account='route1:budget:'+sponsor
            balance=k.state.accounts[account].balance
            price=DEFAULT_PRICE[PROJECTS[sponsor][1]]
            if sponsor in trial_rules and sponsor not in followon_funded:
                next_stage='a2' if sponsor in purchased else 'a1'
                price=D(trial_rules[sponsor][next_stage+'_price'])
            amount=max(D(0),balance-D(carry_cap)*price)
            if amount:
                tx=k.transfer(year,account,sink,amount,TxPurpose.OTHER_INVESTMENT)
                k.audit('ROUTE1_CARRY_CAP_LAPSE',year,sponsor=sponsor,
                        amount=amount,cap=carry_cap,price=price,
                        destination=sink,transaction=tx.id)
            row['cash_before_lapse']=str(balance)
            row['lapsed_amount']=str(amount)
            row['cash_after_lapse']=str(k.state.accounts[account].balance)
            if abs(k.state.accounts[account].balance+amount-balance)>D('1e-24'):
                raise AssertionError('lapse cash not conserved: '+sponsor)
        k.assert_invariants()
    purchased={r['sponsor'] for r in rows if r['disbursement']}
    followon_funded=set()
    claims={trial_rules[r['sponsor']]['body']:r['sponsor'] for r in rows
            if r['disbursement'] and r['sponsor'] in trial_rules}
    spent={s:sum((D(r['authored_price']) for r in rows
                  if r['sponsor']==s and r['disbursement']),D(0)) for s in trial_rules}
    lapse(2026,rows)
    capacities,_=load_investment_capacity(root)
    all_sponsors={**PUBLIC,**PRIVATE}
    countries={}
    for sponsor,participation in all_sponsors.items():
        for country in participation:
            if (country,2026) in capacities:
                countries.setdefault(country,[]).append(
                    (sponsor,D(PREFERENCES.get(country,{}).get(sponsor,1))))
    prospecting=load_prospecting_scenario()
    manifest=test_only_manifest()
    required={country for country,entries in countries.items() if entries}
    for country in required:
        for year in range(2026,end_year+1):
            if (country,year) not in capacities:
                raise ValueError(f'missing Earth investment: {country} {year}')
    for year in range(2027,end_year+1):
        before={s:k.state.accounts['route1:budget:'+s].balance for s in all_sponsors}
        allocated={s:D(0) for s in all_sponsors}
        for country,entries in sorted(countries.items()):
            _,_,_,mobilized=derive_mobilization(
                investment_proxy=capacities[country,year],
                commercial_opportunity=D(1),scenario=prospecting)
            amount=mobilized*share
            origin=f'route1:origin:{country}:{year}'
            k.add_account(origin,'COUNTRY:'+country,'EARTH:'+country,
                          AccountKind.EARTH_BOUNDARY,amount)
            total=sum((w for _,w in entries),D(0))
            for i,(sponsor,weight) in enumerate(entries):
                allocation=(k.state.accounts[origin].balance if i==len(entries)-1
                            else amount*weight/total)
                k.transfer(year,origin,'route1:budget:'+sponsor,
                           allocation,TxPurpose.OTHER_INVESTMENT)
                allocated[sponsor]+=allocation
            if k.state.accounts[origin].balance!=0:
                raise AssertionError(f'country allocation not conserved: {country} {year}')
        for sponsor in sorted(CEILINGS,key=lambda s:(ordering.get(s,len(ordering)),s)):
            budget='route1:budget:'+sponsor
            opening=before[sponsor]
            available=k.state.accounts[budget].balance
            category=PROJECTS[sponsor][1]
            price=DEFAULT_PRICE[category]
            rule=trial_rules.get(sponsor)
            if rule and sponsor not in purchased:
                price=D(rule['a1_price'])
            evidence=(followon_trial.get('evidence',{}).get(sponsor) if rule else None)
            evidence_ready=(bool(evidence) and evidence.get('activity_id')==rule['a1']
                and evidence.get('standing')=='SUPPORTS_ADVANCE'
                and evidence.get('review_outcome')=='ADVANCE'
                and evidence.get('result_ref')
                and D(evidence.get('admitted_at','9999'))<D(evidence.get('review_at','0'))
                and D(evidence.get('review_at','9999'))<D(year+1)) if rule else False
            ceiling=D(CEILINGS[sponsor])
            commitment=disbursement=None
            # Off by default. Evaluate the admitted A1 result after the 2029
            # country allocation, before this year's carry-cap lapse.
            followon=(sponsor=='NASA' and year==2029 and nasa_a2_evidence is not None)
            if rule and sponsor in purchased and sponsor not in followon_funded and evidence_ready:
                followon=True
                price=D(rule['a2_price'])
            if sponsor in purchased and not followon:
                decision='NOT_EVALUATED'
                reason=('WAIT_RESULT' if rule and sponsor not in followon_funded else 'ALREADY_PURCHASED')
                status='COMPLETE' if reason=='ALREADY_PURCHASED' else 'WAIT_RESULT'
            else:
                oid='route1:authored:observation:'+sponsor
                if followon:
                    if rule:
                        oid=f'route1:6c:{rule["a1"]}:admitted:{sponsor}:{year}'
                        from offworld_kernel.mvp_state import Observation
                        k.observations[oid]=Observation(oid,int(D(evidence['admitted_at'])),
                            sponsor,rule['a1'],evidence['result_ref'],
                            'SUPPORTS_ADVANCE',False)
                        k.agents[sponsor].information.add(oid)
                    else:
                        oid='route1:6c:a1:admitted:NASA'
                        if nasa_a2_evidence['standing']!='SUPPORTS_ADVANCE' or not nasa_a2_evidence['reviewed']:
                            raise ValueError('A1 result/review not eligible for A2')
                        from offworld_kernel.mvp_state import Observation
                        k.observations[oid]=Observation(oid,2029,sponsor,
                            'MOON-A1-SURFACE',nasa_a2_evidence['result_ref'],
                            'SUPPORTS_ADVANCE',False)
                        k.agents[sponsor].information.add(oid)
                        price=D('.300')
                request=build_financing_request(
                    f'route1:request:{sponsor}:{year}',year-2025,sponsor,
                    'route1:project:'+sponsor,price,'DEVELOPMENT',
                    disclosed_observation_ids=(oid,))
                k.submit_financing_request(request)
                facts=tuple(SnapshotFact(key,FactState.KNOWN,value,EVIDENCE_TAG)
                            for key,value in EVIDENCE)
                snapshot=DecisionSnapshot(
                    'ROUTE1_FINANCIER','PRIVATE_FINANCIER',
                    'EARTH:'+all_sponsors[sponsor][0],
                    f'route1:financier:snapshot:{sponsor}:{year}',str(year-2025),
                    available,('FINANCE',),('RETURN',),(oid,),
                    (('resource_exists',D('.5')),),(('resource_exists',D('.5')),),
                    (),(),(),facts)
                decision_obj=run_financier_policy(
                    snapshot,request,manifest,
                    f'route1:financier:decision:{sponsor}:{year}',
                    allow_test_fixture=True).decision
                decision=decision_obj.outcome.value
                reason=decision_obj.reason_code.value
                k.audit('ROUTE1_AUTHORED_EVIDENCE',year,sponsor=sponsor,
                        scenario='B',label=EVIDENCE_TAG,inputs=EVIDENCE,
                        belief=D('.5'),prior=D('.5'),manifest='TEST_ONLY',
                        observation=oid,classification='AUTHORED TEST_ONLY NON-CANON',
                        a1_provenance=(evidence if rule and followon else
                                       nasa_a2_evidence if followon else None),
                        experiment='result-triggered, not result-priced' if followon else None)
                k.audit('ROUTE1_FINANCIER_DECISION',year,sponsor=sponsor,
                        scenario='B',decision=decision_obj.id,
                        outcome=decision,reason=reason,requested=price,
                        ceiling=ceiling,available=available)
                if ceiling<price:
                    status='WAIT_CEILING_BELOW_PRICE'
                elif available<price:
                    status='WAIT_CASH_BELOW_PRICE'
                elif rule and spent[sponsor]+price>D(rule['lifetime_limit']):
                    status='WAIT_CUMULATIVE_LIMIT'
                elif decision!='APPROVE':
                    status='WAIT_POLICY'
                elif rule and rule['body'] in claims and claims[rule['body']]!=sponsor:
                    status='WAIT_CLAIMED_BY_OTHER'
                else:
                    if rule:
                        claims[rule['body']]=sponsor
                        spent[sponsor]+=price
                        if followon:
                            followon_funded.add(sponsor)
                    commitment=f'route1:commit:{sponsor}:{year}'
                    k.add_commitment(commitment,'ROUTE1_FINANCIER',
                                     'route1:project:'+sponsor,price)
                    k.audit('ROUTE1_COMMITMENT',year,sponsor=sponsor,
                            commitment=commitment,decision=decision_obj.id,amount=price)
                    disbursement=k.disburse(year,commitment,budget,price).id
                    k.audit('ROUTE1_DISBURSEMENT',year,sponsor=sponsor,
                            commitment=commitment,transaction=disbursement,amount=price)
                    purchased.add(sponsor)
                    status='FUNDED_PENDING_EXECUTOR'
            closing=k.state.accounts[budget].balance
            expected=opening+allocated[sponsor]-(price if disbursement else D(0))
            if abs(closing-expected)>D('1e-24'):
                raise AssertionError(f'sponsor cash not conserved: {sponsor} {year}')
            rows.append(dict(year=year,sponsor=sponsor,scenario='B',
                category=category,authored_ceiling=str(ceiling),
                authored_price=str(price),opening=str(opening),
                allocated=str(allocated[sponsor]),available=str(available),
                closing=str(closing),policy=decision,reason=reason,
                status=status,commitment=commitment,disbursement=disbursement))
        for sponsor in all_sponsors:
            if sponsor not in CEILINGS:
                if abs(k.state.accounts['route1:budget:'+sponsor].balance-before[sponsor]-allocated[sponsor])>D('1e-24'):
                    raise AssertionError(f'other sponsor cash not conserved: {sponsor} {year}: {k.state.accounts["route1:budget:"+sponsor].balance} vs {before[sponsor]+allocated[sponsor]}')
        k.audit('ROUTE1_YEAR_SETTLEMENT',year,share=share,
                decisions=sum(r['year']==year and r['policy']!='NOT_EVALUATED' for r in rows),
                concentration_rejections=sum(r['year']==year and r['reason']=='CONCENTRATION' for r in rows),
                commitments=sum(r['year']==year and bool(r['commitment']) for r in rows),
                disbursements=sum(r['year']==year and bool(r['disbursement']) for r in rows))
        lapse(year,[r for r in rows if r['year']==year])
        k.assert_invariants()
    return rows,k
