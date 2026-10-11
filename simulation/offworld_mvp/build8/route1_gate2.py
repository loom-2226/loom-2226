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

def run_gate2(share=D('.10'),root=EARTH_V4_ROOT):
    """Returns rows for 2026-2029, including original Gate 1 2026 B results."""
    share=D(share)
    rows,k=run_gate1(share,root=root,scenario='B')
    for row in rows:
        row['year']=2026
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
    purchased={r['sponsor'] for r in rows if r['disbursement']}
    for year in (2027,2028,2029):
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
        for sponsor in sorted(CEILINGS):
            budget='route1:budget:'+sponsor
            opening=before[sponsor]
            available=k.state.accounts[budget].balance
            category=PROJECTS[sponsor][1]
            price=DEFAULT_PRICE[category]
            ceiling=D(CEILINGS[sponsor])
            commitment=disbursement=None
            if sponsor in purchased:
                decision='NOT_EVALUATED'
                reason='ALREADY_PURCHASED'
                status='COMPLETE'
            else:
                oid='route1:authored:observation:'+sponsor
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
                        observation=oid,classification='AUTHORED TEST_ONLY NON-CANON')
                k.audit('ROUTE1_FINANCIER_DECISION',year,sponsor=sponsor,
                        scenario='B',decision=decision_obj.id,
                        outcome=decision,reason=reason,requested=price,
                        ceiling=ceiling,available=available)
                if ceiling<price:
                    status='WAIT_CEILING_BELOW_PRICE'
                elif available<price:
                    status='WAIT_CASH_BELOW_PRICE'
                elif decision!='APPROVE':
                    status='WAIT_POLICY'
                else:
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
        k.assert_invariants()
    return rows,k
