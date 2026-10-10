"""Disposable two-epoch USA Sponsor scarcity episode. In-memory, non-governed.

Sponsors choose using common public costs and distinct authored objective rankings.
Conductor assigns executors; supplier payment is a transfer, not physical delivery.
"""
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening
from .sponsor_trial_setup import (SPONSORS,OPTIONS,EXECUTORS,HOMES,RANKS,episode_setup)


def episode(identical=False,seed=0):
    k,h,capacities,envelope,rec=episode_setup()
    prices=dict(OPTIONS); ranks={s:('HEAVY','MEDIUM','LIGHT') if identical else RANKS[s] for s in SPONSORS}
    # Seed only changes order, never hidden beliefs or economic inputs.
    import random
    order=list(SPONSORS);random.Random(seed).shuffle(order)
    history=[]
    for epoch in (1,2):
        if epoch==2:
            new=k.mobilize_country_capital(2,'USA',capacities['USA',2027],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
            assert new.mobilized_cash>=envelope
            k.transfer(2,'b8_funds:USA','episode:budget',envelope,TxPurpose.OTHER_INVESTMENT)
        for sponsor in order:
            affordable=[choice for choice in ranks[sponsor] if prices[choice]<=k.state.accounts['episode:budget'].balance]
            chosen=affordable[0] if affordable else None
            preferred=ranks[sponsor][0]
            if chosen is None:
                history.append((epoch,sponsor,preferred,'WAIT',str(k.state.accounts['episode:budget'].balance)))
                continue
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
    return tuple(history),str(k.state.accounts['episode:budget'].balance),k.fingerprint()

if __name__=='__main__':
    for seed in range(4):
        a=episode(seed=seed);assert a==episode(seed=seed)
        print('DIFFERENT',seed,a[0], 'LEFT',a[1])
    for seed in range(4):
        a=episode(identical=True,seed=seed);assert a==episode(identical=True,seed=seed)
        print('IDENTICAL',seed,a[0], 'LEFT',a[1])
