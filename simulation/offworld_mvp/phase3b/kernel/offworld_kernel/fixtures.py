from .kernel import Kernel
from .model import *

def base_kernel():
    k=Kernel()
    for n,kind in [('EARTH:X',NodeKind.EARTH),('EARTH:Y',NodeKind.EARTH),('OFF:C1',NodeKind.OFFWORLD),('OFF:M1',NodeKind.OFFWORLD)]: k.add_node(n,kind)
    k.add_account('earth_x_boundary','EARTH:X','EARTH:X',AccountKind.EARTH_BOUNDARY,D('1000000000'))
    k.add_account('earth_return','earth_owner','EARTH:X',AccountKind.FUNDS,D('0'))
    k.add_account('earth_x_supplier','supplier_x','EARTH:X',AccountKind.SUPPLIER,D('0'))
    k.add_account('earth_y_supplier','supplier_y','EARTH:Y',AccountKind.SUPPLIER,D('0'))
    k.add_account('c1_funds','local_c1','OFF:C1',AccountKind.FUNDS,D('100'))
    k.add_account('c1_supplier','supplier_c1','OFF:C1',AccountKind.SUPPLIER,D('0'))
    k.add_account('m1_supplier','supplier_m1','OFF:M1',AccountKind.SUPPLIER,D('0'))
    return k

def four_route_fixture():
    k=base_kernel()
    routes=[
      ('A','OFF:C1','earth_x_boundary','earth_x_supplier',D('40'),'OFF:C1',1),
      ('B','OFF:C1','c1_funds','c1_supplier',D('20'),'OFF:C1',2),
      ('C','OFF:C1','c1_funds','earth_y_supplier',D('15'),'OFF:C1',3),
      ('D','OFF:M1','c1_funds','c1_supplier',D('10'),'OFF:M1',4)]
    for tag,pnode,funds,supplier,amount,anode,year in routes:
        cash=f'p{tag}_cash'; pid=f'p{tag}'; cid=f'c{tag}'; aid=f'a{tag}'
        k.add_account(cash,pid,pnode,AccountKind.PROJECT_CASH); k.add_project(pid,pnode,cash,{f'owner_{tag}':D('1')})
        k.add_commitment(cid,f'financier_{tag}',pid,amount); k.disburse(year,cid,funds,amount)
        k.spend_capex(year,pid,supplier,amount,aid,anode); k.capitalize(aid,amount)
    k.assert_invariants(); return k

def recursive_fixture(policy,years=50):
    if policy not in {'ENCLAVE','SETTLEMENT'}: raise ValueError(policy)
    k=base_kernel(); k.add_account('mine_cash','mine','OFF:C1',AccountKind.PROJECT_CASH,D('0')); k.add_project('mine','OFF:C1','mine_cash',{'earth_owner':D('1')})
    k.state.assets['seed_mine']=Asset('seed_mine','mine','OFF:C1',AssetKind.PRODUCTIVE,D('100'),D('100'))
    for year in range(1,years+1):
        surplus=k.productive_capital('OFF:C1')*D('0.10')
        k.transfer(year,'earth_x_boundary','mine_cash',surplus,TxPurpose.REVENUE)
        if policy=='ENCLAVE': k.transfer(year,'mine_cash','earth_return',surplus,TxPurpose.RETURN_TO_EARTH)
        else:
            reinvest=surplus*D('0.80'); returned=surplus-reinvest; aid=f'reinvest_{year:03d}'
            k.spend_capex(year,'mine','c1_supplier',reinvest,aid,'OFF:C1',financing_origin_nodes=('OFF:C1',)); k.capitalize(aid,reinvest)
            k.transfer(year,'mine_cash','earth_return',returned,TxPurpose.RETURN_TO_EARTH)
        k.assert_invariants()
    return {'productive_capital':k.productive_capital('OFF:C1'),'earth_returns':k.state.accounts['earth_return'].balance,
            'local_fcf':sum((e.amount for e in k.state.fcf_events if e.asset_node=='OFF:C1'),D('0')),'fingerprint':k.fingerprint()}