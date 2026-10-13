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
from offworld_kernel.mvp_state import AgentState, AgentKind, Observation
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

# Route 1 run selection; trial objects stay owned by their existing callers.
_RUN_PAYLOADS = {
    'pilot': frozenset(('price_override',)),
    'nasa_a2': frozenset(('payload',)),
    'follow_on': frozenset(('payload',)),
    'cast_payments': frozenset(('payload',)),
    'two_body_campaign': frozenset(('payments', 'campaign')),
    'all_body_campaign': frozenset(('payments', 'campaign')),
}


def _resolve_run_setting(run_setting):
    if isinstance(run_setting, str):
        run_setting = {'name': run_setting}
    if not isinstance(run_setting, dict):
        raise ValueError('run_setting must name a Route 1 run')
    name = run_setting.get('name')
    if name not in _RUN_PAYLOADS:
        raise ValueError('unknown Route 1 run_setting')
    extras = set(run_setting) - {'name'}
    if extras - _RUN_PAYLOADS[name]:
        if name in ('cast_payments', 'two_body_campaign', 'all_body_campaign'):
            raise ValueError('cast payments are a separate opt-in Route 1 experiment; cannot be mixed with follow-on financing')
        raise ValueError('incompatible Route 1 run options')
    required = set() if name == 'pilot' else _RUN_PAYLOADS[name]
    if any(run_setting.get(key) is None for key in required):
        raise ValueError('Route 1 run is missing its required payload')
    return name, run_setting


def run_gate1(share=D('.10'), root=EARTH_V4_ROOT, scenario='A',
              run_setting='pilot', earth_end_year=2035):
    share=D(share)
    run_name, options = _resolve_run_setting(run_setting)
    followon_trial = options.get('payload') if run_name == 'follow_on' else None
    cast_trial = (options.get('payments') if run_name in ('two_body_campaign', 'all_body_campaign')
                  else options.get('payload') if run_name == 'cast_payments' else None)
    project_price_override = (options.get('price_override') if run_name == 'pilot'
                              else {'NASA': D('.350')} if run_name == 'nasa_a2'
                              else None)
    if scenario not in ('A','B'):
        raise ValueError('Scenario A or B only')
    if share not in (D('.10'),D('.25')):
        raise ValueError('only AUTHORED 10% and 25% shares are admitted')
    validate_authored_network_names()
    k,_,capacities,_=build_country_opening(root,world_seed='BUILD8_ROUTE1_GATE1',end_year=earth_end_year)
    extras={} if followon_trial is None else followon_trial.get('participants',{})
    if set(extras)&(set(PUBLIC)|set(PRIVATE)) or any(
            s not in followon_trial['rules'] for s in extras):
        raise ValueError('synthetic trial sponsor must be new and assigned')
    all_sponsors={**PUBLIC,**PRIVATE,
                  **{s:(row['country'],) for s,row in extras.items()}}
    trial_ceilings={} if followon_trial is None else followon_trial.get('ceilings',{})
    financed_sponsors={**CEILINGS,**trial_ceilings,**(cast_trial.ceilings if cast_trial else {})}
    by_country={}
    for sponsor,countries in all_sponsors.items():
        for country in countries:
            if (country,2026) in capacities:
                by_country.setdefault(country,[]).append(
                    (sponsor,D(PREFERENCES.get(country,{}).get(sponsor,1))))
    prospecting=load_prospecting_scenario()
    budgets={}
    for sponsor,countries in sorted(all_sponsors.items()):
        key='route1:budget:'+sponsor
        k.add_account(key,sponsor,'EARTH:'+countries[0],AccountKind.FUNDS)
        budgets[sponsor]=key
    origins={}
    for country,entries in sorted(by_country.items()):
        _,_,_,mobilized=derive_mobilization(investment_proxy=capacities[country,2026],
            commercial_opportunity=D(1),scenario=prospecting)
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
    trial_rules={} if followon_trial is None else followon_trial['rules']
    trial_order=() if followon_trial is None else tuple(followon_trial['order'])
    if len(set(trial_order))!=len(trial_order) or set(trial_order)!=set(trial_rules):
        raise ValueError('trial order must list every assigned sponsor once')
    claims={}
    ordering={s:i for i,s in enumerate(trial_order)}
    for sponsor in sorted(financed_sponsors,key=lambda s:(ordering.get(s,len(ordering)),s)):
        category=(extras[sponsor]['category'] if sponsor in extras
                  else PROJECTS[sponsor][1])
        ceiling=D(financed_sponsors[sponsor])
        quote=(cast_trial.choose_quote(sponsor,category) if cast_trial else None)
        price=(quote['price'] if quote is not None else
               D(trial_rules[sponsor]['a1_price']) if sponsor in trial_rules else
               D(project_price_override[sponsor]) if project_price_override and sponsor in project_price_override
               else DEFAULT_PRICE[category])
        budget=budgets[sponsor]
        available=k.state.accounts[budget].balance
        executor=(quote['executor'] if quote is not None else
                  extras[sponsor]['executor'] if sponsor in extras else PREFERRED[sponsor])
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
        disclosed=()
        if scenario=='B':
            # AUTHORED / TEST_ONLY / NON-CANON. Same single neutral
            # observation content for all; sponsor-held protocol identity differs.
            oid='route1:authored:observation:'+sponsor
            k.observations[oid]=Observation(oid,2026,sponsor,
                'ROUTE1_AUTHORED_NEUTRAL','AUTHORED_TEST_ONLY','NEUTRAL',False)
            k.agents[sponsor].information.add(oid)
            disclosed=(oid,)
            k.audit('ROUTE1_DISCLOSED_OBSERVATION',2026,sponsor=sponsor,
                observation=oid,signal='NEUTRAL',classification='AUTHORED TEST_ONLY NON-CANON')
        if cast_trial:
            cast_trial.audit_quote(k,2026,sponsor,category,quote)
        request=build_financing_request('route1:request:'+sponsor,1,sponsor,
                                         project,price,'DEVELOPMENT',
                                         disclosed_observation_ids=disclosed)
        k.submit_financing_request(request)
        facts=tuple(SnapshotFact(key,FactState.KNOWN,value,EVIDENCE_TAG)
                    for key,value in EVIDENCE)
        snapshot=DecisionSnapshot('ROUTE1_FINANCIER','PRIVATE_FINANCIER',
            'EARTH:'+all_sponsors[sponsor][0],
            'route1:financier:snapshot:'+sponsor,'1',available,
            ('FINANCE',),('RETURN',),disclosed,
            (('resource_exists',D('.5')),),(('resource_exists',D('.5')),),
            (),(),(),facts)
        execution=run_financier_policy(snapshot,request,manifest,
                     'route1:financier:decision:'+sponsor,allow_test_fixture=True)
        decision=execution.decision
        k.audit('ROUTE1_AUTHORED_EVIDENCE',2026,sponsor=sponsor,scenario=scenario,
                label=EVIDENCE_TAG,inputs=EVIDENCE,belief=D('.5'),
                prior=D('.5'),manifest='TEST_ONLY')
        k.audit('ROUTE1_FINANCIER_DECISION',2026,sponsor=sponsor,scenario=scenario,
                request=request.id,decision=decision.id,
                outcome=decision.outcome.value,reason=decision.reason_code.value,
                requested=price,ceiling=ceiling,available=available)
        status='WAIT_POLICY'
        commitment=None
        disbursement=None
        if ceiling<price:
            status='WAIT_CEILING_BELOW_PRICE'
        elif available<price:
            status='WAIT_CASH_BELOW_PRICE'
        elif sponsor in trial_rules and price>D(trial_rules[sponsor]['lifetime_limit']):
            status='WAIT_CUMULATIVE_LIMIT'
        elif decision.outcome.value!='APPROVE':
            status='WAIT_POLICY'
        elif sponsor in trial_rules and trial_rules[sponsor]['body'] in claims:
            status='WAIT_CLAIMED_BY_OTHER'
        else:
            if sponsor in trial_rules:
                claims[trial_rules[sponsor]['body']]=sponsor
            commitment='route1:commit:'+sponsor
            k.add_commitment(commitment,'ROUTE1_FINANCIER',project,price)
            k.audit('ROUTE1_COMMITMENT',2026,sponsor=sponsor,
                    commitment=commitment,decision=decision.id,amount=price)
            tx=k.disburse(2026,commitment,budget,price)
            disbursement=tx.id
            k.audit('ROUTE1_DISBURSEMENT',2026,sponsor=sponsor,
                    commitment=commitment,transaction=tx.id,amount=price)
            status='FUNDED_PENDING_EXECUTOR'
            if cast_trial:
                status=cast_trial.settle(k,2026,sponsor,category,quote,disbursement)
        results.append(dict(sponsor=sponsor,category=category,executor=executor,
            scenario=scenario,reason=decision.reason_code.value,
            authored_ceiling=str(ceiling),authored_price=str(price),
            opening=str(available),closing=str(k.state.accounts[budget].balance),
            policy=decision.outcome.value,
            decision=decision.id,status=status,commitment=commitment,
            disbursement=disbursement,
            **({'delivery':cast_trial.delivery_for(sponsor,2026)} if cast_trial else {})))
    k.audit('ROUTE1_GATE1_SETTLEMENT',2026,share=share,scenario=scenario,
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
        if sponsor in financed_sponsors:
            spent=sum((D(r['authored_price']) for r in results
                       if r['sponsor']==sponsor and r['disbursement']),D(0))
            if k.state.accounts[budgets[sponsor]].balance+spent!=initial:
                raise AssertionError('sponsor cash not conserved: '+sponsor)
    return results,k
