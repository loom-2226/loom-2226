"""Non-authoritative Build 8 probe: source-specific capital, distinct Sponsor choices.

Not a World Authority admitted policy run. No canon, no qualification.
"""
from .opening import EARTH_V4_ROOT
from decimal import Decimal as D
from pathlib import Path
from offworld_kernel.model import AccountKind, NodeKind, TxPurpose
from offworld_kernel.mvp_state import AgentState, AgentKind
from .opening import build_country_opening

ROOT=EARTH_V4_ROOT

def run(root=ROOT):
    k,h,capacity,_=build_country_opening(root)
    sponsors=(('SPN','USA','STRATEGIC'),('B8_COMMERCIAL','AUS','COMMERCIAL'))
    results=[]
    for sponsor,country,motive in sponsors:
        if sponsor!='SPN':
            account='b8_agent:'+sponsor
            k.add_account(account,sponsor,'EARTH:'+country,AccountKind.FUNDS,D(0))
            k.add_agent(AgentState(sponsor,AgentKind.PRIVATE_SPONSOR,'EARTH:'+country,account,{'INITIATE_PROSPECTING'},(motive,)))
        rec=k.mobilize_country_capital(1,country,capacity[country,2026],D(1),h['prospecting_scenario'],f'b8_source:{country}',f'b8_funds:{country}')
        origin=f'b8_funds:{country}'
        dest=f'b8_sourcebacked:{sponsor}:{country}'
        k.add_account(dest,sponsor,'EARTH:'+country,AccountKind.FUNDS,D(0))
        allocated=rec.mobilized_cash / D(2)
        alloc=k.transfer(1,origin,dest,allocated,TxPurpose.OTHER_INVESTMENT,parent_ids=(rec.transaction_id,'B8_AUTHORED_UNADMITTED_PREFERENCE'))
        assert k.capital_coupling[country]['F']==k.state.accounts[origin].balance+k.state.accounts[dest].balance
        assert k.capital_coupling[country]['X']==0
        # Same visible candidates, differing explicit experimental objectives.
        options=(('POLAR_VOLATILES',D('0.1'),D('5'),D('1')),('EQUATORIAL_METALS',D('0.1'),D('1'),D('5')))
        selected=max(options,key=lambda x: x[2] if motive=='STRATEGIC' else x[3])
        project=f'B8:{sponsor}:{selected[0]}'
        amount=selected[1]
        if allocated < amount:
            results.append((sponsor,country,motive,'WAIT',str(allocated)))
            continue
        node=f'OFF:{project}'
        cash=f'cash:{project}'
        k.add_node(node,NodeKind.OFFWORLD)
        k.add_account(cash,sponsor,node,AccountKind.PROJECT_CASH,D(0))
        k.add_project(project,node,cash,{sponsor:D(1)})
        cid=f'COMMIT:{project}:{country}'
        k.add_commitment(cid,sponsor,project,amount)
        tx=k.disburse(1,cid,dest,amount)
        k.capital_coupling[country]['F']-=amount
        k.capital_coupling[country]['X']+=amount
        assert k.capital_coupling[country]['F']==k.state.accounts[origin].balance+k.state.accounts[dest].balance
        assert k.capital_coupling[country]['X']==amount
        results.append((sponsor,country,motive,selected[0],str(amount),alloc.id,tx.id))
    k.assert_invariants()
    return tuple(results),k.fingerprint()

if __name__=='__main__':
    a=run();b=run();assert a==b,(a,b)
    print('DETERMINISTIC_PASS',a,flush=True)
