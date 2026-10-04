from __future__ import annotations
import random
from decimal import Decimal as D

from .accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, AssetKind, NodeKind
from .mvp_state import AgentKind, AgentState, ColonyState, RuntimeObjectClass, ScenarioResource, SystemState
from .runtime import ScheduledSimulationRuntime
from .scheduler import CouplingSpec, Phase, ScheduledEvent

def scheduler_valid_accounting_property_fixture(seed=2226,steps=120):
    rid=RunIdentity('ACCOUNTING_PROPERTY','v1','SYNTH_ACCOUNTING_PROPERTY',
                    'BUILD4_MVP_METHODOLOGY_R1',(('seed',str(seed)),('steps',str(steps))))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
    for aid,owner,node,kind,balance in [
      ('fin','FIN','EARTH:X',AccountKind.FUNDS,'1000'),
      ('project','SPN','OFF:T1',AccountKind.PROJECT_CASH,'100'),
      ('supplier','SUP','OFF:T1',AccountKind.SUPPLIER,'0'),
      ('buyer','BUYER','OFF:T1',AccountKind.FUNDS,'1000'),
      ('earth_owner','OWNER','EARTH:X',AccountKind.FUNDS,'0'),
      ('local_fund','LOCAL','OFF:T1',AccountKind.FUNDS,'0')]:
        k.add_account(aid,owner,node,kind,D(balance))
    k.add_project('P','OFF:T1','project',{'SPN':D('1')})
    k.add_commitment('C','FIN','P',D('300'))
    k.add_agent(AgentState('SPN',AgentKind.PRIVATE_SPONSOR,'OFF:T1','project',{'EXTRACT','SELL'},('RETURN',)))
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',D('500'),D('500'),D('500'),D('500')))
    k.colonies['OFF:T1']=ColonyState('OFF:T1')
    k.create_wip('W','P','OFF:T1')
    for y in range(1,steps+2): k.set_supply_capacity('OFF:T1',y,D('10000'))

    k.add_system(SystemState('PROPERTY_SYSTEM','SCHEDULER_VALID_ACCOUNTING_PROPERTY',
                             {'accounts','transactions','commitments','wip','assets','resources','ownership','surplus'}))
    k.scheduler.register_coupling(CouplingSpec(
        'PROPERTY_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('accounts','transactions','commitments','wip','assets','resources','ownership','surplus'),
        ('all_state',),
        ('accounts','transactions','commitments','wip','assets','resources','ownership','surplus'),
        'GENERATIVE_VALIDATION',Phase.OPERATIONS))
    for i in range(steps):
        k.scheduler.schedule(ScheduledEvent(
            f'prop-{i:04d}',D(i+1),Phase.OPERATIONS,0,f'{i:04d}','PROPERTY_SYSTEM',
            payload=(('step',str(i)),('year',str(i+1)))))

    rng=random.Random(seed)
    actions=[]
    identity_checks=[]
    rt=ScheduledSimulationRuntime(k)

    def handler(kernel,event):
        year=int(dict(event.payload)['year'])
        snap=AccountingPeriodSnapshot.capture(kernel,year)

        valid=['noop']
        commitment=kernel.state.commitments['C']
        if commitment.outstanding>D('0') and kernel.state.accounts['fin'].balance>D('0'): valid.append('disburse')
        if kernel.state.accounts['project'].balance>=D('1') and kernel.wip['W'].commissioned==D('0'): valid.append('wip_spend')
        if kernel.wip['W'].accumulated_cost>D('0') and kernel.wip['W'].commissioned==D('0'): valid.append('commission')
        if 'A' in kernel.state.assets and kernel.state.assets['A'].kind==AssetKind.PRODUCTIVE and kernel.state.assets['A'].book_value>D('0'): valid.append('depreciate')
        if kernel.resources['RES'].remaining>D('0'): valid.append('extract')
        if kernel.colonies['OFF:T1'].resource_inventory>D('0') and kernel.state.accounts['buyer'].balance>=D('2'): valid.append('sell')
        if kernel.state.accounts['project'].balance>=D('3'): valid.append('surplus')
        if commitment.outstanding>D('0'): valid.append('lapse')

        action=rng.choice(valid)
        if action=='disburse':
            amt=min(D(rng.randint(1,5)),commitment.outstanding,kernel.state.accounts['fin'].balance)
            kernel.disburse(year,'C','fin',amt)
        elif action=='wip_spend':
            amt=min(D(rng.randint(1,4)),kernel.state.accounts['project'].balance)
            kernel.add_wip_expenditure(year,'W','supplier',amt,('OFF:T1',))
        elif action=='commission':
            kernel.commission_wip(year,'W','A',D('10'))
        elif action=='depreciate':
            rate=D(rng.choice(['0.01','0.02','0.05']))
            kernel.depreciate(year,'A',rate)
        elif action=='extract':
            q=min(D(rng.randint(1,3)),kernel.resources['RES'].remaining)
            kernel.extract(year,'SPN','RES',q)
        elif action=='sell':
            q=min(D('1'),kernel.colonies['OFF:T1'].resource_inventory)
            kernel.sell(year,'SPN','RES',q,D('2'),'buyer')
        elif action=='surplus':
            kernel.record_surplus_decomposition(
                year,'P',D('3'),reserve=D('1'),
                local_reinvestments=(('local_fund',D('1')),),
                owner_returns=(('earth_owner',D('1')),))
        elif action=='lapse':
            kernel.lapse_commitment(year,'C',min(D('1'),commitment.outstanding))

        actions.append(action)
        checks=AccountingIdentityAuditor(kernel,snap).check_all()
        identity_checks.append((event.event_id,tuple(sorted(checks))))
        return action

    rt.register_handler('PROPERTY_SYSTEM',handler)
    rt.seal()
    result=rt.run()
    return k,result,tuple(actions),tuple(identity_checks)
