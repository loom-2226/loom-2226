"""Noncanon USA financier fixture: frozen request screening, authored score clearing."""
from decimal import Decimal as D
from hashlib import sha256
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy_runner import run_sponsor_prospecting_policy
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.policies.manifest import test_only_manifest

SEED='BUILD8_USA_FINANCIER_TEST_0'  # Authored tie control, not economic authority.
UNDERWRITING=(('underwriting.PRICE','1'),('underwriting.EXPLORATION_CAPEX','.125'),
              ('underwriting.DEVELOPMENT_CAPEX','.125'),('underwriting.OPERATING_COST','.5'),
              ('underwriting.LEAD_TIME','1'))  # All synthetic fixture values.

def finance_requests(k,h,names,order,public,private,positive,disclose_private,cost,budget,mobilization):
    manifest=test_only_manifest()  # TEST_ONLY, explicitly NOT an authorized policy.
    limit=dict((p.semantic_name,p.value) for p in manifest.parameters)['max_concentration_fraction']
    assert cost/budget<=limit, 'single-project concentration cap'
    assert mobilization.strategic_pressure==D(0), 'pressure remains zero'
    k.add_account('usa:financier:fund','USA:AUTHORED_INVESTMENT_FUND','EARTH:USA',AccountKind.FUNDS)
    k.transfer(1,'usa:trial:pool','usa:financier:fund',budget,TxPurpose.OTHER_INVESTMENT,
               parent_ids=(mobilization.transaction_id,))
    fin=AgentState('USA_FINANCIER',AgentKind.PRIVATE_FINANCIER,'EARTH:USA','usa:financier:fund',
                   {'FINANCE'},('RETURN',),priors={'resource_exists:'+n:D('.5') for n in names})
    k.add_agent(fin)
    # Financier learns only disclosed observations. Each project's belief stays separate.
    for name in names:
        for obs in public:
            if obs.question_ref=='VOLATILES_PRESENT':
                k.publish_observation(2,'PUB',obs.id,'USA_FINANCIER_DISCLOSURE',
                    (('USA_FINANCIER','resource_exists:'+name,D('.8'),D('.2')),))
    if positive and disclose_private:
        k.publish_observation(2,'SpaceX',private.id,'USA_FINANCIER_PRIVATE_DISCLOSURE',
            (('USA_FINANCIER','resource_exists:SpaceX',D('.8'),D('.2')),))
    # All requests and snapshots are fixed before the first transfer.
    frozen=k.state.accounts['usa:financier:fund'].balance
    screened={}
    for name in order:
        sponsor=k.agents[name]
        from .test_four_usa_agents import KEYS
        sponsor_snapshot=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:USA','usa:sponsor:frozen:'+name,
            '2',D(0),('REQUEST_FINANCE',),('RETURN',),tuple(sorted(sponsor.information)),
            tuple((key,sponsor.beliefs[key]) for key in KEYS),
            tuple((key,sponsor.priors[key]) for key in KEYS),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(cost),'SYNTHETIC'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,'.39','SYNTHETIC'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'1','SYNTHETIC')))
        sponsor_request=SponsorProspectingRequest('usa:req:'+name,2,name,'usa:opp:'+name,
            'usa:trial:project:'+name,'MOON','REG','LOC',tuple(o.id for o in public),KEYS,cost,D('.39')).validate_protocol()
        sponsor_choice=run_sponsor_prospecting_policy(sponsor_snapshot,sponsor_request,
            'usa:sponsor:decision:'+name).decision.outcome.value
        if sponsor_choice!='INITIATE_PROJECT':
            screened[name]=(sponsor_choice,None,None,None)
            continue
        disclosed=tuple(o.id for o in public if o.question_ref=='VOLATILES_PRESENT')
        if name=='SpaceX' and positive and disclose_private:
            disclosed+= (private.id,)
        request=build_financing_request('usa:finance:'+name,2,name,'usa:trial:project:'+name,cost,'DEVELOPMENT',disclosed)
        belief=fin.beliefs['resource_exists:'+name]
        snapshot=DecisionSnapshot('USA_FINANCIER','PRIVATE_FINANCIER','EARTH:USA','usa:finance:frozen:'+name,
            '2',frozen,('FINANCE',),('RETURN',),tuple(sorted(fin.information)),
            (('resource_exists',belief),),(('resource_exists',D('.5')),),(),(),(),
            tuple(SnapshotFact(key,FactState.KNOWN,value,'TEST_ONLY:AUTHORED_UNDERWRITING') for key,value in UNDERWRITING) +
            (SnapshotFact('capital.STRATEGIC_PRESSURE',FactState.KNOWN,
                          str(mobilization.strategic_pressure),'BUILD8_MOBILIZATION'),))
        execution=run_financier_policy(snapshot,request,manifest,'usa:finance:decision:'+name,allow_test_fixture=True)
        metrics=dict(execution.metrics)
        score=D(metrics['annual_return_proxy']) if execution.decision.outcome.value=='APPROVE' else None
        screened[name]=(execution.decision.outcome.value,score,request,execution.decision)
    # Retain the requests, including those awaiting the next period, in the
    # existing kernel request collection. Submission order is canonical.
    for name in sorted(names):
        if screened[name][2] is not None:
            k.submit_financing_request(screened[name][2])
    approved=sorted((name for name in names if screened[name][0]=='APPROVE'),
        key=lambda name:(-screened[name][1],sha256(f'{SEED}|2|usa:finance:{name}'.encode()).hexdigest()))
    funded=set();remaining=frozen
    for name in approved:
        request=screened[name][2]
        if request.amount<=remaining:
            funded.add(name);remaining-=request.amount
    for name in sorted(funded):
        k.transfer(2,'usa:financier:fund','usa:trial:cash:'+name,cost,TxPurpose.OTHER_INVESTMENT,
                   parent_ids=(screened[name][3].id,))
        k.transition_project_status(2,name,'usa:trial:project:'+name,'DEVELOPMENT',screened[name][3].id)
    results={}
    for name in names:
        outcome,score,request,decision=screened[name]
        state='FUNDED' if name in funded else 'DECLINED' if outcome=='DECLINE' else 'DEFERRED'
        results[name]=(outcome,str(score) if score is not None else None,state,
                       'NEXT_PERIOD' if outcome=='APPROVE' and name not in funded else None,
                       str(mobilization.strategic_pressure))
    assert k.state.accounts['usa:financier:fund'].balance==remaining
    assert sum(k.state.accounts['usa:trial:cash:'+n].balance for n in names)+remaining==budget
    k.assert_invariants()
    return results,k.fingerprint(),str(mobilization.mobilized_cash),str(remaining)
