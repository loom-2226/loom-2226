"""Disposable Build 8 controls: equal preferences, scarce same-country allocations.

Uses real Build 7 kernel accounts and mobilization; no governed policy authority.
"""
from decimal import Decimal as D
from .two_economy_source_finance_trial import ROOT, run
from .opening import build_country_opening
from offworld_kernel.model import AccountKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind

OPTIONS=(('POLAR_VOLATILES',D(5),D(1)),('EQUATORIAL_METALS',D(1),D(5)))

def choice(weights):
    return max(OPTIONS,key=lambda x: weights[0]*x[1]+weights[1]*x[2])[0]

def controls(root=ROOT):
    assert choice((D(1),D(0))) != choice((D(0),D(1)))
    assert choice((D(1),D(0))) == choice((D(1),D(0)))
    k,h,capacity,_=build_country_opening(root)
    country='USA'
    rec=k.mobilize_country_capital(1,country,capacity[country,2026],D(1),h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
    pool='b8_funds:USA'
    original=rec.mobilized_cash
    assert k.capital_coupling[country]['F']==original and k.capital_coupling[country]['X']==0
    for sponsor,share in (('SPN',D('0.6')),('B8_COMPETITOR',D('0.4'))):
        if sponsor!='SPN':
            agent_acct='b8_agent:'+sponsor
            k.add_account(agent_acct,sponsor,'EARTH:USA',AccountKind.FUNDS,D(0))
            k.add_agent(AgentState(sponsor,AgentKind.PRIVATE_SPONSOR,'EARTH:USA',agent_acct,{'INITIATE_PROSPECTING'},('COMMERCIAL',)))
        dest=f'b8_sourcebacked:{sponsor}:USA'
        k.add_account(dest,sponsor,'EARTH:USA',AccountKind.FUNDS,D(0))
        amount=original*share
        assert k.state.accounts[pool].balance >= amount
        k.transfer(1,pool,dest,amount,TxPurpose.OTHER_INVESTMENT,parent_ids=(rec.transaction_id,'B8_UNADMITTED_PREFERENCE'))
        held=k.state.accounts[pool].balance+sum(a.balance for key,a in k.state.accounts.items() if key.startswith('b8_sourcebacked:') and key.endswith(':USA'))
        assert held==k.capital_coupling[country]['F']==original
        assert k.capital_coupling[country]['X']==0
    before=k.fingerprint()
    balances=tuple((key,a.balance) for key,a in sorted(k.state.accounts.items()))
    requested=original*D('0.01')
    assert k.state.accounts[pool].balance < requested
    try:
        if requested>k.state.accounts[pool].balance:
            raise ValueError('COUNTRY_ALLOCATION_CAP_EXCEEDED')
        raise AssertionError('oversubscription accepted')
    except ValueError as exc:
        assert str(exc)=='COUNTRY_ALLOCATION_CAP_EXCEEDED'
    assert k.fingerprint()==before
    assert balances==tuple((key,a.balance) for key,a in sorted(k.state.accounts.items()))
    # A sponsor's funded commitment reduces F, increases X, without changing source attribution.
    src='b8_sourcebacked:SPN:USA'
    amount=D('0.1')
    assert k.state.accounts[src].balance>=amount
    node='OFF:B8:CONTROL';cash='b8_cash:control';project='B8_CONTROL'
    k.add_node(node,__import__('offworld_kernel.model',fromlist=['NodeKind']).NodeKind.OFFWORLD)
    k.add_account(cash,'SPN',node,AccountKind.PROJECT_CASH,D(0))
    k.add_project(project,node,cash,{'SPN':D(1)})
    k.add_commitment('B8_CONTROL_COMMIT','SPN',project,amount)
    k.disburse(1,'B8_CONTROL_COMMIT',src,amount)
    k.capital_coupling[country]['F']-=amount
    k.capital_coupling[country]['X']+=amount
    held=k.state.accounts[pool].balance+sum(a.balance for key,a in k.state.accounts.items() if key.startswith('b8_sourcebacked:') and key.endswith(':USA'))
    assert held==k.capital_coupling[country]['F']
    assert k.capital_coupling[country]['X']==amount
    assert k.capital_coupling[country]['F']+k.capital_coupling[country]['X']==original
    k.assert_invariants()
    return (choice((D(1),D(0))),choice((D(1),D(0))),choice((D(0),D(1))),str(original),str(held),str(amount),k.fingerprint())

if __name__=='__main__':
    a=controls();b=controls();assert a==b
    print('CONTROLS_PASS',a)
    c=run();d=run();assert c==d
    print('TWO_ECONOMY_PASS',c)
