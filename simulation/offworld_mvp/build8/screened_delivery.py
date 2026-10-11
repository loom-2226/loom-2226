"""Build 8 research trial: real Sponsor/financier policies, constrained clearing.

All opportunity, underwriting, belief and funding inputs remain authored.
A deferred approved request is reconsidered next year, without a new policy.
"""
from decimal import Decimal as D
from hashlib import sha256
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind, ActionKind, BODY_MATERIAL_FAMILIES
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.prospecting import SponsorProspectingRequest
from offworld_kernel.policy_runner import run_sponsor_prospecting_policy, run_financier_policy
from offworld_kernel.financing_protocol import build_financing_request
from offworld_kernel.policies.manifest import test_only_manifest
from .four_usa_financier import UNDERWRITING, SEED
from .opening import build_country_opening, EARTH_V4_ROOT
from .deliverable_chain import OPERATORS
from .competitive_delivery import SCALE, Work

SPONSORS = ('Interlune', 'Axiom')
# Differing authored information value expresses distinct investment motives.
MOTIVES = {'Interlune': ('RESOURCE_RETURN', D('2.00')),
           'Axiom': ('LUNAR_INFRASTRUCTURE', D('2.20'))}


def run_screened(order=SPONSORS, root=EARTH_V4_ROOT, failure=None):
    if set(order) != set(SPONSORS) or len(order) != 2:
        raise ValueError('expected Interlune and Axiom')
    k,h,capacities,_ = build_country_opening(root)
    mobilization=k.mobilize_country_capital(1,'USA',capacities['USA',2026],D(1),
        h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
    amount=sum((SCALE*OPERATORS[c][1]*(1+OPERATORS[c][2]) for c in ('BUILD','LAND')),D(0))
    # A finite 2.00-unit fund can clear one 1.525-unit project under the
    # existing 80% concentration limit. Remaining USA capital stays upstream.
    fund=D('2.00')
    if fund < amount or fund >= 2*amount or fund > mobilization.mobilized_cash:
        raise ValueError('authored financing envelope inconsistent')
    k.add_account('screen:fund','USA_SCREENED_FINANCIER','EARTH:USA',AccountKind.FUNDS)
    k.transfer(1,'b8_funds:USA','screen:fund',fund,TxPurpose.OTHER_INVESTMENT,
               parent_ids=(mobilization.transaction_id,))
    k.add_agent(AgentState('SCREEN_FINANCIER',AgentKind.PRIVATE_FINANCIER,'EARTH:USA',
                           'screen:fund',{'FINANCE'},('RETURN',),priors={'resource_exists:'+f+'_PRESENT':D('.5') for f in BODY_MATERIAL_FAMILIES}))
    keys=tuple('BODY:MOON:'+f+'_PRESENT' for f in BODY_MATERIAL_FAMILIES)
    public,_,_=k.explore_paid(1,'PUB','','','earth_supplier',D(0),channel='REMOTE',
        public=False,false_positive=D(0),false_negative=D(0),update_belief=False,
        body_id='MOON',question_ref='BODY_MATERIAL_CHARACTERIZATION',
        body_truth={family:True for family in BODY_MATERIAL_FAMILIES})
    observation_ids=tuple(o.id for o in public)
    for obs in public:
        k.publish_observation(1,'PUB',obs.id,'SCREENED_FINANCIER_DISCLOSURE',
            (('SCREEN_FINANCIER','resource_exists:'+obs.question_ref,D('.8'),D('.2')),))
    requests={}; sponsor_decisions={}; screenings={}
    for name in sorted(SPONSORS):
        motive,info=MOTIVES[name]
        k.add_account('screen:sponsor:'+name,name,'EARTH:USA',AccountKind.FUNDS)
        k.add_node('screen:moon:'+name,NodeKind.OFFWORLD)
        k.add_account('screen:cash:'+name,name,'screen:moon:'+name,AccountKind.PROJECT_CASH)
        k.add_project('screen:project:'+name,'screen:moon:'+name,'screen:cash:'+name,{name:D(1)})
        k.add_agent(AgentState(name,AgentKind.PRIVATE_SPONSOR,'EARTH:USA',
            'screen:sponsor:'+name,{'REQUEST_FINANCE','DEVELOP'},("RETURN",motive),
            beliefs={key:D('.8') for key in keys},priors={key:D('.5') for key in keys}))
        for obs in public:
            key='BODY:MOON:'+obs.question_ref
            k.publish_observation(1,'PUB',obs.id,'SCREENED_SPONSOR_DISCLOSURE',
                ((name,key,D('.8'),D('.2')),))
        req=SponsorProspectingRequest('screen:opportunity:'+name,1,name,'screen:op:'+name,
            'screen:project:'+name,'MOON','REG','LOC',observation_ids,keys,amount,info).validate_protocol()
        snap=DecisionSnapshot(name,'PRIVATE_SPONSOR','EARTH:USA','screen:sponsor:snapshot:'+name,
            '1',D(0),('REQUEST_FINANCE',),("RETURN",motive),observation_ids,tuple((key,D('.8')) for key in keys),
            tuple((key,D('.5')) for key in keys),(),(),(),(
                SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,str(amount),'AUTHORED'),
                SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,str(info),'AUTHORED'),
                SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,'2.00','AUTHORED')))
        sd=run_sponsor_prospecting_policy(snap,req,'screen:sponsor:decision:'+name).decision
        sponsor_decisions[name]=sd
        if sd.outcome.value!='INITIATE_PROJECT':
            continue
        financing=build_financing_request('screen:finance:'+name,1,name,
            'screen:project:'+name,amount,'DEVELOPMENT',observation_ids)
        requests[name]=financing
        k.submit_financing_request(financing)
    frozen=k.state.accounts['screen:fund'].balance
    manifest=test_only_manifest()
    for name,req in sorted(requests.items()):
        motive,info=MOTIVES[name]
        # Frozen underwriting snapshots before any allocation.
        snap=DecisionSnapshot('SCREEN_FINANCIER','PRIVATE_FINANCIER','EARTH:USA',
            'screen:finance:snapshot:'+name,'1',frozen,('FINANCE',),('RETURN',),observation_ids,
            (('resource_exists',D('.85') if name=='Interlune' else D('.75')),),(('resource_exists',D('.5')),),(),(),(),
            tuple(SnapshotFact(key,FactState.KNOWN,value,'TEST_ONLY:AUTHORED_UNDERWRITING')
                  for key,value in UNDERWRITING)+
            (SnapshotFact('capital.STRATEGIC_PRESSURE',FactState.KNOWN,'0','BUILD8_MOBILIZATION'),))
        execution=run_financier_policy(snap,req,manifest,'screen:finance:decision:'+name,
                                       allow_test_fixture=True)
        score=D(dict(execution.metrics)['annual_return_proxy']) if execution.decision.outcome.value=='APPROVE' else None
        screenings[name]=(execution.decision,score)
    ranked=sorted((n for n,(d,s) in screenings.items() if d.outcome.value=='APPROVE'),
                  key=lambda n:(-screenings[n][1],sha256(f'{SEED}|1|screen:finance:{n}'.encode()).hexdigest()))
    approvals={}; pending=set(ranked); work=[]; occupied={}; ready={}
    # Approved but not financed is a visible, persistent queue state.
    for name in ranked:
        k.audit('BUILD8_FINANCE_SCREEN',2026,sponsor=name,decision=screenings[name][0].id,
                score=screenings[name][1],outcome='APPROVED_AWAITING_CLEARING')
    for year in (2026,2027):
        # 2027 financing is additional mobilized country capital, not minted money.
        if year==2027 and pending:
            extra=k.mobilize_country_capital(2,'USA',capacities['USA',2027],D(1),
                h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
            topup=min(amount,k.state.accounts['b8_funds:USA'].balance)
            k.transfer(2,'b8_funds:USA','screen:fund',topup,TxPurpose.OTHER_INVESTMENT,
                       parent_ids=(extra.transaction_id,))
        for name in ranked:
            if name not in pending or k.state.accounts['screen:fund'].balance<amount:
                continue
            decision,score=screenings[name]
            # Decision is the existing screened policy decision, not a fabricated approval.
            k.financing_decisions[decision.id]=decision
            k.event(year-2025,'SCREEN_FINANCIER',ActionKind.FINANCE,'APPROVED',
                    (decision.id,decision.request_id,str(score)))
            k.transfer(year-2025,'screen:fund','screen:sponsor:'+name,amount,
                       TxPurpose.OTHER_INVESTMENT,parent_ids=(decision.id,))
            k.add_commitment('screen:commit:'+name,name,'screen:project:'+name,amount)
            k.disburse(year-2025,'screen:commit:'+name,'screen:sponsor:'+name,amount)
            k.transition_project_status(year-2025,name,'screen:project:'+name,'DEVELOPMENT',
                                        sponsor_decisions[name].id)
            approvals[name]=year
            k.audit('BUILD8_FINANCE_CLEARING',year,sponsor=name,decision=decision.id,
                    outcome='FUNDED',amount=amount)
            ready[name]=year
            pending.remove(name)
        for name in sorted(pending):
            k.audit('BUILD8_FINANCE_CLEARING',year,sponsor=name,
                    decision=screenings[name][0].id,outcome='DEFERRED_INSUFFICIENT_CASH',
                    amount=amount)
    for category in ('BUILD','LAND'):
        operator=OPERATORS[category][0]
        k.add_account('screen:revenue:'+category,operator,'EARTH:USA',AccountKind.SUPPLIER)
        k.add_account('screen:expense:'+category,operator+' COST','EARTH:USA',AccountKind.SUPPLIER)
    # Deterministic earliest-ready scheduler, with policy ranking on contention.
    rank={name:i for i,name in enumerate(ranked)}
    delivered={name:{'COMMISSION:'+name} for name in approvals}
    stages={name:0 for name in approvals}
    while any(stage<2 for stage in stages.values()):
        name=min((n for n in stages if stages[n]<2),key=lambda n:(ready[n],rank[n]))
        index=stages[name]; category=('BUILD','LAND')[index]
        consumed=('COMMISSION:' if index==0 else 'BUILT:')+name
        if consumed not in delivered[name]:
            work.append(Work(name,category,ready[name],ready[name],'BLOCKED_UPSTREAM',consumed,None,D(0),D(0),D(0)))
            stages[name]=2
            continue
        _,base,markup,duration,slots=OPERATORS[category]
        start=ready[name]
        while any(occupied.get((category,y),0)>=slots for y in range(start,start+duration)):
            start+=1
        finish=start+duration
        for y in range(start,finish): occupied[category,y]=occupied.get((category,y),0)+1
        cost=base*SCALE;price=cost*(1+markup)
        tx=k.transfer(finish-2025,'screen:cash:'+name,'screen:revenue:'+category,
            price,TxPurpose.CAPEX,parent_ids=(screenings[name][0].id,consumed))
        k.transfer(finish-2025,'screen:revenue:'+category,'screen:expense:'+category,
            cost,TxPurpose.OTHER_INVESTMENT,parent_ids=(tx.id,))
        outcome='FAILED' if failure==(name,category) else 'DELIVERED'
        produced=(('BUILT:' if index==0 else 'ON_MOON:')+name) if outcome=='DELIVERED' else None
        if produced: delivered[name].add(produced)
        k.audit('BUILD8_SCREENED_DELIVERY',finish,project=name,category=category,
            outcome=outcome,consumed=consumed,produced=produced or '',revenue=price,cost=cost,profit=price-cost)
        work.append(Work(name,category,start,finish,outcome,consumed,produced,price,cost,price-cost))
        ready[name]=finish;stages[name]+=1
    k.assert_invariants()
    return (tuple(sorted(work,key=lambda w:(w.start,rank[w.project],w.category))),
            tuple((n,sponsor_decisions[n].outcome.value,
                   screenings[n][0].outcome.value if n in screenings else 'NOT_REQUESTED',
                   str(screenings[n][1]) if n in screenings else '',approvals.get(n)) for n in SPONSORS),
            k,occupied)
