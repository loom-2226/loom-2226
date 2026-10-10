"""Disposable two-epoch USA Sponsor scarcity episode. In-memory, non-governed.

Sponsors choose using common public costs and distinct authored objective rankings.
Conductor assigns executors; supplier payment is a transfer, not physical delivery.
"""
from decimal import Decimal as D
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from .opening import build_country_opening
from .sponsor_trial_setup import (SPONSORS,OPTIONS,EXECUTORS,HOMES,RANKS,episode_setup)


def episode(identical=False,seed=0,adapt=True):
    k,h,capacities,envelope,rec=episode_setup()
    prices=dict(OPTIONS); ranks={s:('HEAVY','MEDIUM','LIGHT') if identical else RANKS[s] for s in SPONSORS}
    # Seed only changes order, never hidden beliefs or economic inputs.
    import random
    order=list(SPONSORS);random.Random(seed).shuffle(order)
    history=[]
    outcomes={}
    invested={}
    realized={}
    # Scenario-assumed realized 2026 gross receipts per unit of invested capital.
    # Not an observation or calibration of actual firms.
    realized_multipliers={'Axiom':D('1.35'),'Blue Origin':D('.65'),
                          'Interlune':D('1.15'),'SpaceX':D('1.55')}
    for epoch in (1,2):
        if epoch==2:
            new=k.mobilize_country_capital(2,'USA',capacities['USA',2027],D(1),h['prospecting_scenario'],'b8_source:USA','b8_funds:USA')
            assert new.mobilized_cash>=envelope
            k.transfer(2,'b8_funds:USA','episode:budget',envelope,TxPurpose.OTHER_INVESTMENT)
            # Scenario settlement: externally generated customer revenue, never
            # confused with recycled investment capital or supplier payments.
            k.add_account('episode:customers','CUSTOMERS','EARTH:USA',AccountKind.FUNDS,D(0))
            for sponsor,amount in sorted(invested.items()):
                gross=amount*realized_multipliers[sponsor]
                source='episode:customers:'+sponsor
                k.add_account(source,'CUSTOMERS','EARTH:USA',AccountKind.FUNDS,gross)
                k.transfer(2,source,'episode:funds:'+sponsor,gross,TxPurpose.OTHER_INVESTMENT)
                realized[sponsor]=gross-amount
            # Revenue enters Sponsor accounts; it does not refill public
            # investment capital or assert any physical project completion.

        for sponsor in order:
            # Profit-first: fictional expected gross revenue and risk-adjusted
            # margins, common public information; financing history changes
            # risk appetite, not fabricated sales or project success.
            revenues={'HEAVY':D('.65'),'MEDIUM':D('.39'),'LIGHT':D('.16')}
            # Sponsors differ in return hurdles. No guaranteed payoff is booked.
            hurdle={'Axiom':D('.30'),'Blue Origin':D('.35'),
                    'Interlune':D('.40'),'SpaceX':D('.25')}[sponsor]
            if identical:hurdle=D('.30')
            setback=epoch==2 and adapt and outcomes.get(sponsor) in ('WAIT','DOWNGRADED')
            # Setback increases required return; previous funded projects are
            # not mistaken for realized profit.
            if setback:hurdle+=D('.25')
            if epoch==2 and adapt and sponsor in realized:
                # Loss raises hurdle; profit lowers it. Bounded, authored response.
                roi=realized[sponsor]/invested[sponsor]
                hurdle+=max(D('-.15'),min(D('.30'),-roi*D('.50')))
                hurdle=max(D('0'),hurdle)
            ranking=tuple(sorted(prices,key=lambda c:(
                -(revenues[c]-prices[c]-hurdle*prices[c]),ranks[sponsor].index(c))))
            ranking=tuple(c for c in ranking if revenues[c]-prices[c]>=hurdle*prices[c])
            affordable=[choice for choice in ranking if prices[choice]<=k.state.accounts['episode:budget'].balance]
            chosen=affordable[0] if affordable else None
            preferred=ranking[0] if ranking else 'NO_POSITIVE_RISK_ADJUSTED_RETURN'
            if chosen is None:
                history.append((epoch,sponsor,preferred,'WAIT',str(k.state.accounts['episode:budget'].balance)))
                if epoch==1:outcomes[sponsor]='WAIT'
                continue
            if epoch==1:
                outcomes[sponsor]='DOWNGRADED' if chosen!=preferred else 'FUNDED'
                invested[sponsor]=amount if 'amount' in locals() else prices[chosen]
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
    return tuple(history),str(k.state.accounts['episode:budget'].balance),k.fingerprint(),outcomes,realized

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
            print('RESULT',identical,seed,'REALIZED',adapted[4],'2026',adapted[3],'2027_ADAPTED',adapted[0][4:],'CHANGES',differences,flush=True)
    assert changed>0,'No observable adaptation'
    assert economic_changes>0,'No changes in funding/project outcomes'
    print('ADAPTATION_PASS',changed,'cases with changed decisions;',economic_changes,'with changed project/funding outcomes')
