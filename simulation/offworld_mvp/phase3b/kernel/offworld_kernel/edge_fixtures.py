from decimal import Decimal as D

from .build3 import RunIdentity
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind, TxPurpose
from .mvp_state import RuntimeObjectClass, SystemState
from .runtime import ScheduledSimulationRuntime
from .scheduler import CouplingSpec, Phase, ScheduledEvent

def staged_multiyear_wip_fixture():
    rid=RunIdentity('STAGED_WIP','v1','SYNTH_STAGED_WIP','BUILD4_MVP_METHODOLOGY_R1',())
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('project','SPN','OFF:T1',AccountKind.PROJECT_CASH,D('100'))
    k.add_account('supplier','SUP','OFF:T1',AccountKind.SUPPLIER,D('0'))
    k.add_project('P','OFF:T1','project',{'SPN':D('1')})
    k.create_wip('W','P','OFF:T1')
    k.set_supply_capacity('OFF:T1',2,D('100')); k.set_supply_capacity('OFF:T1',3,D('100'))
    k.add_system(SystemState('BUILD_SYSTEM','MULTIYEAR_CONSTRUCTION',{'accounts','transactions','wip','assets'}))
    k.add_system(SystemState('DEP_SYSTEM','PERIOD_END_DEPRECIATION',{'assets'}))
    k.scheduler.register_coupling(CouplingSpec(
        'BUILD_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('accounts','transactions','wip','assets'),('project','supply'),('accounts','transactions','wip','assets'),
        'MILESTONE',Phase.OPERATIONS))
    k.scheduler.register_coupling(CouplingSpec(
        'DEP_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('assets',),('assets',),('assets',),'ANNUAL',Phase.DEPRECIATION_AMORTIZATION))
    for eid,t,action,amount in [
        ('spend-y2',D('2'), 'SPEND','20'),
        ('spend-y3',D('3'), 'SPEND','30'),
        ('commission-y4',D('4'),'COMMISSION','0')]:
        k.scheduler.schedule(ScheduledEvent(eid,t,Phase.OPERATIONS,0,eid,'BUILD_SYSTEM',
                                            payload=(('action',action),('amount',amount))))
    k.scheduler.schedule(ScheduledEvent('depreciate-y5',D('5'),Phase.DEPRECIATION_AMORTIZATION,0,
                                        'depreciate-y5','DEP_SYSTEM',payload=(('rate','0.10'),)))
    states=[]
    rt=ScheduledSimulationRuntime(k)
    def build_handler(kernel,e):
        p=dict(e.payload)
        if p['action']=='SPEND':
            kernel.add_wip_expenditure(int(e.effective_time),'W','supplier',D(p['amount']),('OFF:T1',))
        else:
            kernel.commission_wip(int(e.effective_time),'W','A',D('50'))
        states.append((e.event_id,str(kernel.wip['W'].accumulated_cost),str(kernel.wip['W'].commissioned),
                       str(kernel.state.assets['A'].book_value) if 'A' in kernel.state.assets else None))
        return e.event_id
    def dep_handler(kernel,e):
        kernel.depreciate(int(e.effective_time),'A',D(dict(e.payload)['rate']))
        states.append((e.event_id,str(kernel.wip['W'].accumulated_cost),str(kernel.wip['W'].commissioned),
                       str(kernel.state.assets['A'].book_value)))
        return e.event_id
    rt.register_handler('BUILD_SYSTEM',build_handler); rt.register_handler('DEP_SYSTEM',dep_handler)
    rt.seal(); result=rt.run()
    return k,result,tuple(states)

def genuine_multirate_fixture():
    rid=RunIdentity('MULTIRATE','v1','SYNTH_MULTIRATE','BUILD4_MVP_METHODOLOGY_R1',())
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH); k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('fin','FIN','EARTH:X',AccountKind.FUNDS,D('10'))
    k.add_account('project','P','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_project('P','OFF:T1','project',{'FIN':D('1')})
    k.add_commitment('C','FIN','P',D('4'))
    for sid,ptype,state in [
      ('EARTH_SYSTEM','ANNUAL_EARTH_INPUT',set()),
      ('MISSION_SYSTEM','DAY_SCALE_MISSION',set()),
      ('FINANCE_SYSTEM','QUARTERLY_FINANCE',{'accounts','transactions','commitments'})]:
        k.add_system(SystemState(sid,ptype,state))
    k.scheduler.register_coupling(CouplingSpec('EARTH_SYSTEM','v1',RuntimeObjectClass.SYSTEM,(),('accounts',),(),
                                               'ANNUAL',Phase.EXOGENOUS_INPUTS,(('time','SIM_YEAR'),)))
    k.scheduler.register_coupling(CouplingSpec('MISSION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,(),('accounts',),(),
                                               'DAY_SCALE',Phase.OBSERVATION,(('time','SIM_YEAR_FRACTION'),)))
    k.scheduler.register_coupling(CouplingSpec('FINANCE_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
                                               ('accounts','transactions','commitments'),('accounts','commitments'),
                                               ('accounts','transactions','commitments'),'QUARTERLY',
                                               Phase.COMMITMENT_DISBURSEMENT,(('time','SIM_YEAR_FRACTION'),)))
    events=[
      ScheduledEvent('mission-day30',D('0.0821917808219178'),Phase.OBSERVATION,0,'m30','MISSION_SYSTEM'),
      ScheduledEvent('finance-q1',D('0.25'),Phase.COMMITMENT_DISBURSEMENT,0,'q1','FINANCE_SYSTEM'),
      ScheduledEvent('finance-q2',D('0.50'),Phase.COMMITMENT_DISBURSEMENT,0,'q2','FINANCE_SYSTEM'),
      ScheduledEvent('mission-day200',D('0.5479452054794521'),Phase.OBSERVATION,0,'m200','MISSION_SYSTEM'),
      ScheduledEvent('finance-q3',D('0.75'),Phase.COMMITMENT_DISBURSEMENT,0,'q3','FINANCE_SYSTEM'),
      ScheduledEvent('finance-q4',D('1.0'),Phase.COMMITMENT_DISBURSEMENT,0,'q4','FINANCE_SYSTEM'),
      ScheduledEvent('mission-day365',D('1.0'),Phase.OBSERVATION,0,'m365','MISSION_SYSTEM'),
      ScheduledEvent('earth-annual',D('1.0'),Phase.EXOGENOUS_INPUTS,0,'annual','EARTH_SYSTEM')]
    for e in reversed(events): k.scheduler.schedule(e)
    observations=[]
    rt=ScheduledSimulationRuntime(k)
    def earth(kernel,e):
        observations.append((e.event_id,str(kernel.state.accounts['project'].balance)))
        return kernel.state.accounts['project'].balance
    def mission(kernel,e):
        observations.append((e.event_id,str(kernel.state.accounts['project'].balance)))
        return kernel.state.accounts['project'].balance
    def finance(kernel,e):
        kernel.disburse(1,'C','fin',D('1'))
        observations.append((e.event_id,str(kernel.state.accounts['project'].balance)))
        return kernel.state.accounts['project'].balance
    rt.register_handler('EARTH_SYSTEM',earth); rt.register_handler('MISSION_SYSTEM',mission); rt.register_handler('FINANCE_SYSTEM',finance)
    rt.seal(); result=rt.run()
    return k,result,tuple(observations)
