"""Route 1, Gate 1: opt-in 2026 financing only. All scenario numbers AUTHORED."""
from decimal import Decimal as D
from hashlib import sha256
from .opening import build_country_opening, EARTH_V4_ROOT
from .sponsor_executor_network_trial import (PUBLIC, PRIVATE, PREFERENCES, PROJECTS,
    EXECUTORS, validate_authored_network_names)
from .four_usa_financier import UNDERWRITING
from simulation.offworld_mvp.build7.generated_campaign import load_prospecting_scenario
from offworld_kernel.prospecting import derive_mobilization
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policies.manifest import test_only_manifest

# AUTHORED proxy dollars; one network MODEL_CURRENCY = $1B proxy-scale.
CEILINGS = {'NASA':'.350','CNSA':'.300','ISRO':'.120','JAXA':'.180',
            'ESA':'.200','CNES':'.100','DLR':'.100',
            'Australian Space Agency':'.050','UAE Space Agency':'.025',
            'ispace':'.100','Interlune':'.025'}
# AUTHORED screened-delivery unit = $50M; factor 20.
DEFAULT_PRICE = {'BUILD':D('.085'),'LAND':D('.150')}
# AUTHORED uniform, neutral synthetic underwriting; no sponsor-specific evidence.
EVIDENCE = tuple((key,value) for key,value in UNDERWRITING)
EVIDENCE_TAG = 'AUTHORED:UNIFORM_NEUTRAL_ROUTE1_2026'
PREFERRED = {'NASA':'Astrobotic','CNSA':'CASC','ISRO':'HAL / L&T',
             'JAXA':'Mitsubishi Heavy Industries','ESA':'Thales Alenia Space',
             'CNES':'Airbus Defence and Space','DLR':'OHB',
             'Australian Space Agency':'Toyota','UAE Space Agency':'Thales Alenia Space',
             'ispace':'ispace','Interlune':'Northrop Grumman'}

def run_gate1(share=D('.10'), root=EARTH_V4_ROOT):
    share=D(share)
    if share not in (D('.10'),D('.25')):
        raise ValueError('only AUTHORED 10% and 25% shares are admitted')
    validate_authored_network_names()
    k,_,capacities,_=build_country_opening(root,world_seed='BUILD8_ROUTE1_GATE1')
    all_sponsors={**PUBLIC,**PRIVATE}
    by_country={}
    for sponsor,countries in all_sponsors.items():
        for country in countries:
            if (country,2026) in capacities:
                by_country.setdefault(country,[]).append(
                    (sponsor,D(PREFERENCES.get(country,{}).get(sponsor,1))))
    scenario=load_prospecting_scenario()
    budgets={}
    for sponsor,countries in sorted(all_sponsors.items()):
        key='route1:budget:'+sponsor
        k.add_account(key,sponsor,'EARTH:'+countries[0],AccountKind.FUNDS)
        budgets[sponsor]=key
    origins={}
    for country,entries in sorted(by_country.items()):
        _,_,_,mobilized=derive_mobilization(investment_proxy=capacities[country,2026],
            commercial_opportunity=D(1),scenario=scenario)
        amount=mobilized*share
        origin='route1:origin:'+country
        k.add_account(origin,'COUNTRY:'+country,'EARTH:'+country,
                      AccountKind.EARTH_BOUNDARY,amount)
        origins[country]=(origin,amount)
        total=sum((w for _,w in entries),D(0))
        for i,(sponsor,weight) in enumerate(entries):
            allocated=(k.state.accounts[origin].balance if i==len(entries)-1
                       else amount*weight/total)
            k.transfer(2026,origin,budgets[sponsor],allocated,
                       TxPurpose.OTHER_INVESTMENT)
    manifest=test_only_manifest()
    results=[]
    for sponsor in sorted(CEILINGS):
        _,category,_=PROJECTS[sponsor]
        ceiling=D(CEILINGS[sponsor])
        price=DEFAULT_PRICE[category]
        budget=budgets[sponsor]
        available=k.state.accounts[budget].balance
        executor=PREFERRED[sponsor]
        if category not in EXECUTORS[executor][1]:
            executor=sorted(e for e,(_,caps) in EXECUTORS.items() if category in caps)[0]
        node='OFF:ROUTE1:'+sponsor
        project='route1:project:'+sponsor
        cash='route1:cash:'+sponsor
        k.add_node(node,NodeKind.OFFWORLD)
        k.add_account(cash,sponsor,node,AccountKind.PROJECT_CASH)
        k.add_project(project,node,cash,{sponsor:D(1)})
        k.add_agent(AgentState(sponsor,AgentKind.PRIVATE_SPONSOR,
            'EARTH:'+all_sponsors[sponsor][0],budget,{'REQUEST_FINANCE'},
            ('RETURN',),priors={'resource_exists':D('.5')}))
        request=build_financing_request('route1:request:'+sponsor,1,sponsor,
                                         project,price,'DEVELOPMENT')
        k.submit_financing_request(request)
        facts=tuple(SnapshotFact(key,FactState.KNOWN,value,EVIDENCE_TAG)
                    for key,value in EVIDENCE)
        snapshot=DecisionSnapshot('ROUTE1_FINANCIER','PRIVATE_FINANCIER',
            'EARTH:'+all_sponsors[sponsor][0],
            'route1:financier:snapshot:'+sponsor,'1',available,
            ('FINANCE',),('RETURN',),(),
            (('resource_exists',D('.5')),),(('resource_exists',D('.5')),),
            (),(),(),facts)
        execution=run_financier_policy(snapshot,request,manifest,
                     'route1:financier:decision:'+sponsor,allow_test_fixture=True)
        decision=execution.decision
        k.audit('ROUTE1_AUTHORED_EVIDENCE',2026,sponsor=sponsor,
                label=EVIDENCE_TAG,inputs=EVIDENCE,belief=D('.5'),
                prior=D('.5'),manifest='TEST_ONLY')
        k.audit('ROUTE1_FINANCIER_DECISION',2026,sponsor=sponsor,
                request=request.id,decision=decision.id,
                outcome=decision.outcome.value,reason=decision.reason_code.value,
                requested=price,ceiling=ceiling,available=available)
        status='WAIT_POLICY'
        commitment=None
        disbursement=None
        if ceiling<price:
            status='WAIT_CEILING_BELOW_PRICE'
        elif available<ceiling:
            status='WAIT_CASH_BELOW_CEILING'
        elif decision.outcome.value!='APPROVE':
            status='WAIT_POLICY'
        else:
            commitment='route1:commit:'+sponsor
            k.add_commitment(commitment,'ROUTE1_FINANCIER',project,price)
            k.audit('ROUTE1_COMMITMENT',2026,sponsor=sponsor,
                    commitment=commitment,decision=decision.id,amount=price)
            tx=k.disburse(2026,commitment,budget,price)
            disbursement=tx.id
            k.audit('ROUTE1_DISBURSEMENT',2026,sponsor=sponsor,
                    commitment=commitment,transaction=tx.id,amount=price)
            status='FUNDED_PENDING_EXECUTOR'
        results.append(dict(sponsor=sponsor,category=category,executor=executor,
            authored_ceiling=str(ceiling),authored_price=str(price),
            opening=str(available),policy=decision.outcome.value,
            decision=decision.id,status=status,commitment=commitment,
            disbursement=disbursement))
    k.audit('ROUTE1_GATE1_SETTLEMENT',2026,share=share,
        evidence=EVIDENCE_TAG,decisions=len(results),
        commitments=sum(bool(r['commitment']) for r in results),
        disbursements=sum(bool(r['disbursement']) for r in results),
        committed_total=sum((D(r['authored_price']) for r in results
                             if r['commitment']),D(0)))
    k.assert_invariants()
    for country,(origin,_) in origins.items():
        if k.state.accounts[origin].balance!=0:
            raise AssertionError('country origin allocation not conserved')
    for sponsor in all_sponsors:
        initial=sum((D(r['opening']) for r in results if r['sponsor']==sponsor),D(0))
        if sponsor in CEILINGS:
            spent=sum((D(r['authored_price']) for r in results
                       if r['sponsor']==sponsor and r['disbursement']),D(0))
            if k.state.accounts[budgets[sponsor]].balance+spent!=initial:
                raise AssertionError('sponsor cash not conserved: '+sponsor)
    return results,k
