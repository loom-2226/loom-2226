"""Disposable two-epoch USA Sponsor scarcity episode. In-memory, non-governed.

Sponsors choose using common public costs and distinct authored objective rankings.
Conductor assigns executors; supplier payment is a transfer, not physical delivery.
"""
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening
from .two_economy_source_finance_trial import ROOT

SPONSORS=('Axiom','Blue Origin','Interlune','SpaceX')
# Fictional model-unit cost tiers; same public candidate list for everyone.
OPTIONS=(('HEAVY',D('.40')),('MEDIUM',D('.25')),('LIGHT',D('.10')))
EXECUTORS={'Axiom':'Thales Alenia Space','Blue Origin':'Blue Origin',
           'Interlune':'Northrop Grumman','SpaceX':'SpaceX'}
HOMES={'Thales Alenia Space':'FRA','Blue Origin':'USA',
       'Northrop Grumman':'USA','SpaceX':'USA'}
# Distinct objectives rank different cost tiers first. Identical control overrides these.
RANKS={'Axiom':('LIGHT','MEDIUM','HEAVY'),
       'Blue Origin':('HEAVY','MEDIUM','LIGHT'),
       'Interlune':('MEDIUM','LIGHT','HEAVY'),
       'SpaceX':('HEAVY','LIGHT','MEDIUM')}

def episode(identical=False,seed=0,adapt=True):
    k,h,capacities,_=build_country_opening(ROOT,world_seed='B8_EPISODE_A')
    rec=k.mobilize_country_capital(1,'USA',capacities['USA',2026],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
    # The episode's deliberately scarce envelope is separate from the 80-country trial.
    envelope=D('.60'); assert rec.mobilized_cash>envelope
    k.add_account('episode:budget','EPISODE','EARTH:USA',AccountKind.FUNDS,D(0))
    k.transfer(1,'b8_funds:USA','episode:budget',envelope,TxPurpose.OTHER_INVESTMENT)
    for sponsor in SPONSORS:
        k.add_account('episode:funds:'+sponsor,sponsor,'EARTH:USA',AccountKind.FUNDS,D(0))
    for executor,home in sorted(HOMES.items()):
        node='EARTH:'+home
        if node not in k.state.nodes:k.add_node(node,NodeKind.EARTH)
        k.add_account('episode:revenue:'+executor,executor,node,AccountKind.FUNDS,D(0))
    prices=dict(OPTIONS); ranks={s:('HEAVY','MEDIUM','LIGHT') if identical else RANKS[s] for s in SPONSORS}
    # Seed only changes order, never hidden beliefs or economic inputs.
    import random
    order=list(SPONSORS);random.Random(seed).shuffle(order)
    history=[]
    outcomes={}  # Observed 2026 financing outcomes, not invented project success/failure.
    for epoch in (1,2):
        if epoch==2:
            new=k.mobilize_country_capital(2,'USA',capacities['USA',2027],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
            assert new.mobilized_cash>=envelope
            k.transfer(2,'b8_funds:USA','episode:budget',envelope,TxPurpose.OTHER_INVESTMENT)
        for sponsor in order:
            # Claude adaptation: scarcity/failed financing dampens next year's
            # ambition. Only observed funding outcomes may affect this rule.
            ranking=ranks[sponsor]
            if epoch==2 and adapt and outcomes.get(sponsor) in ('WAIT','DOWNGRADED'):
                ranking=tuple(c for c in ranking if c!='HEAVY') or ranking
                # One-year financing setback: cap the next proposal at LIGHT.
                # This makes the observed financing result affect cash deployment.
                ranking=tuple(c for c in ranking if c=='LIGHT') or ranking
            affordable=[choice for choice in ranking if prices[choice]<=k.state.accounts['episode:budget'].balance]
            chosen=affordable[0] if affordable else None
            preferred=ranking[0]
            if chosen is None:
                history.append((epoch,sponsor,preferred,'WAIT',str(k.state.accounts['episode:budget'].balance)))
                if epoch==1:outcomes[sponsor]='WAIT'
                continue
            if epoch==1:outcomes[sponsor]='DOWNGRADED' if chosen!=preferred else 'FUNDED'
            amount=prices[chosen]
            k.transfer(epoch,'episode:budget','episode:funds:'+sponsor,amount,TxPurpose.OTHER_INVESTMENT)
            node=f'OFF:EPISODE:{epoch}:{sponsor}'
            k.add_node(node,NodeKind.OFFWORLD)
            cash=f'episode:cash:{epoch}:{sponsor}'
            project=f'episode:project:{epoch}:{sponsor}'
            commitment=f'episode:commit:{epoch}:{sponsor}'
            k.add_account(cash,sponsor,node,AccountKind.PROJECT_CASH,D(0))
            k.add_project(project,node,cash,{sponsor:D(1)})
            k.add_commitment(commitment,sponsor,project,amount)
            k.disburse(epoch,commitment,'episode:funds:'+sponsor,amount)
            k.capital_coupling['USA']['F']-=amount
            k.capital_coupling['USA']['X']+=amount
            # Authored conductor supplier assignment; this pays for contracted
            # services, but does not assert delivery or fabricate a physical asset.
            executor=EXECUTORS[sponsor]
            k.transfer(epoch,cash,'episode:revenue:'+executor,amount,TxPurpose.OTHER_INVESTMENT)
            history.append((epoch,sponsor,preferred,chosen,str(amount),executor))
        k.assert_invariants()
    assert k.state.accounts['episode:budget'].balance>=0
    assert k.capital_coupling['USA']['F']+k.capital_coupling['USA']['X']==rec.mobilized_cash+new.mobilized_cash
    return tuple(history),str(k.state.accounts['episode:budget'].balance),k.fingerprint(),outcomes

if __name__=='__main__':
    changed=0
    economic_changes=0
    for identical in (False,True):
        for seed in range(4):
            adapted=episode(identical,seed,True)
            control=episode(identical,seed,False)
            assert adapted==episode(identical,seed,True)
            assert control==episode(identical,seed,False)
            differences=[(a,b) for a,b in zip(adapted[0][4:],control[0][4:]) if a!=b]
            changed+=bool(differences)
            economic_changes+=any(a[3:]!=b[3:] for a,b in differences)
            print('RESULT',identical,seed,'2026',adapted[3],'2027_ADAPTED',adapted[0][4:],'CHANGES',differences,flush=True)
    assert changed>0,'No observable adaptation'
    assert economic_changes>0,'No changes in funding/project outcomes'
    print('ADAPTATION_PASS',changed,'cases with changed decisions;',economic_changes,'with changed project/funding outcomes')
