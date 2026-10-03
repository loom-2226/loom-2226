from .build4 import *
from .mvp_state import AgentState,AgentKind,ScenarioResource,ColonyState,PopulationLedger
from .model import *

def build4_base(uid='BUILD4'):
    rid=RunIdentity(uid,'v1','SYNTHETIC_BUILD4_INPUT_v1','PHASE3B_BUILD4_v1',
        (('depreciation','0.10'),('knowledge_amortization','0.20'),('allocation_fraction','0.10')))
    k=Build4Kernel(rid)
    for n,kind in [('EARTH:X',NodeKind.EARTH),('EARTH:Y',NodeKind.EARTH),('OFF:T1',NodeKind.OFFWORLD)]: k.add_node(n,kind)
    for aid,owner,node,kind,balance in [
      ('fin1','F1','EARTH:X',AccountKind.FUNDS,'500'),('fin2','F2','EARTH:Y',AccountKind.FUNDS,'500'),
      ('p1cash','P1','OFF:T1',AccountKind.PROJECT_CASH,'0'),('p2cash','P2','OFF:T1',AccountKind.PROJECT_CASH,'0'),
      ('local_vehicle','LV','OFF:T1',AccountKind.FUNDS,'0'),('local_supplier','LS','OFF:T1',AccountKind.SUPPLIER,'0'),
      ('earth_supplier','ES','EARTH:X',AccountKind.SUPPLIER,'0'),('boundary','MKT','EARTH:X',AccountKind.EARTH_BOUNDARY,'0')]:
        k.add_account(aid,owner,node,kind,D(balance))
    k.add_project('P1','OFF:T1','p1cash',{'F1':D('0.5'),'F2':D('0.5')})
    k.add_project('P2','OFF:T1','p2cash',{'F1':D('1')})
    k.set_supply_capacity('OFF:T1',1,D('50')); k.set_supply_capacity('OFF:T1',2,D('50'))
    k.set_resource_constraint('EARTH:X',1,D('1000'),D('0.10'))
    return k

def hard_accounting_fixture():
    k=build4_base('HARD')
    k.add_commitment('C1','F1','P1',D('60')); k.disburse(1,'C1','fin1',D('60'))
    # Cash deliberately held across year boundary before construction spending.
    held_year1=k.state.accounts['p1cash'].balance
    k.create_wip('W1','P1','OFF:T1')
    k.add_wip_expenditure(2,'W1','local_supplier',D('25'),('EARTH:X',))
    k.add_wip_expenditure(2,'W1','local_supplier',D('25'),('EARTH:X',))
    k.commission_wip(3,'W1','A1',D('50')); dep=k.depreciate(4,'A1',D('0.10'))
    k.state.assets['K1']=Asset('K1','P1','OFF:T1',AssetKind.KNOWLEDGE,D('10')); amort=k.amortize_knowledge(4,'K1',D('0.20'))
    k.create_carry_reservation('R1','EARTH:X','P1',D('40'),1,3); outstanding_y1=k.carry_reservations['R1'].outstanding
    k.spend_carry_reservation(2,'R1',D('15')); k.lapse_carry_reservation(3,'R1')
    k.assert_build4_invariants(); return k,held_year1,dep,amort,outstanding_y1

def many_to_many_fixture():
    k=build4_base('MANY')
    # Two financiers syndicate P1.
    k.add_commitment('S1','F1','P1',D('30')); k.add_commitment('S2','F2','P1',D('30'))
    k.disburse(1,'S1','fin1',D('30')); k.disburse(1,'S2','fin2',D('30'))
    # P1 and P2 compete for a 100-unit synthetic Earth resource ceiling.
    k.reserve_earth_supply('EARTH:X',1,D('70'))
    blocked=False
    try: k.reserve_earth_supply('EARTH:X',1,D('40'))
    except InvariantError: blocked=True
    k.add_commitment('P2C','F1','P2',D('50')); k.lapse_commitment(1,'P2C',D('20'))
    k.assert_build4_invariants(); return k,blocked

def ownership_fixture():
    k=build4_base('OWNERS')
    # Local vehicle receives 60/40 contributions; beneficial claims follow contributors.
    k.transfer(1,'fin1','local_vehicle',D('60'),TxPurpose.LOCAL_REINVESTMENT)
    k.transfer(1,'fin2','local_vehicle',D('40'),TxPurpose.LOCAL_REINVESTMENT)
    k.register_vehicle_ownership('LV',[('F1',D('60'),'EARTH:X'),('F2',D('40'),'EARTH:Y')])
    k.distribute_vehicle_to_owners(2,'LV','local_vehicle',{'F1':'fin1','F2':'fin2'},D('50'))
    k.assert_build4_invariants(); return k

def boundary_fixture():
    k=build4_base('BOUNDARY')
    k.state.accounts['p1cash'].balance=D('0')
    k.boundary_purchase(1,'boundary','p1cash',D('100'),'RES',D('5'))
    k.consume_market_resource(2,'EARTH:X','RES',D('2'))
    k.assert_build4_invariants(); return k

def property_sequence(seed=2226,steps=250):
    import random
    k=build4_base('PROP'); rng=random.Random(seed)
    accounts=['fin1','fin2','p1cash','p2cash','local_vehicle','local_supplier','earth_supplier']
    initial=sum((k.state.accounts[a].balance for a in accounts),D('0'))
    # Two open commitments give the generator non-transaction state to exercise.
    k.add_commitment('G1','F1','P1',D('80')); k.add_commitment('G2','F2','P2',D('80'))
    for step in range(1,steps+1):
        choices=['transfer']
        open_c=[x for x in k.state.commitments.values() if x.outstanding>D('0')]
        if open_c: choices+=['commitment']
        action=rng.choice(choices)
        if action=='commitment':
            cm=rng.choice(open_c); src='fin1' if cm.financier_id=='F1' else 'fin2'
            max_amt=min(cm.outstanding,k.state.accounts[src].balance,D('5'))
            if max_amt>=D('1') and rng.random()<0.7:
                k.disburse(step,cm.id,src,D(rng.randint(1,int(max_amt))))
            else:
                k.lapse_commitment(step,cm.id,min(cm.outstanding,D('1')))
        else:
            sources=[a for a in accounts if k.state.accounts[a].balance>D('0')]
            src=rng.choice(sources); dst=rng.choice([a for a in accounts if a!=src])
            max_amt=min(k.state.accounts[src].balance,D('5'))
            amount=D(rng.randint(1,int(max_amt))) if max_amt>=1 else max_amt
            k.transfer(step,src,dst,amount,TxPurpose.OPEX)
        k.assert_build4_invariants()
        assert sum((k.state.accounts[a].balance for a in accounts),D('0'))==initial
    return k
