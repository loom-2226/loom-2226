from decimal import Decimal as D
from .build3 import RunIdentity
from .build4 import OwnershipStake
from .ensemble import AxisKind, EnsembleHarness, ExperimentAxis
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, Asset, AssetKind, NodeKind
from .mvp_state import AggregateState, AgentKind, AgentState, ScenarioResource, SystemState
from .scheduler import CouplingSpec, Phase, ScheduledEvent
from .runtime import ScheduledSimulationRuntime
from .mvp_state import RuntimeObjectClass

def scheduled_resolution_fixture():
    rid=RunIdentity('METHOD_SCHED','v1','SYNTH_METHOD_INPUT','BUILD4_MVP_METHODOLOGY_R1',())
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_account('sector_cash','FIRM_SECTOR','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('firm_cash','FIRM_01','EARTH:X',AccountKind.FUNDS,D('0'))
    k.add_aggregate(AggregateState('FIRM_SECTOR','EARTH:X','sector_cash',10,{'A1'},{'R':D('10')},{'VEH':D('1')},['H1']))
    k.ownership_stakes.append(OwnershipStake('VEH','FIRM_SECTOR','EARTH:X',D('1')))
    k.add_system(SystemState('RESOLUTION_SYSTEM','RUNTIME_RESOLUTION',{'aggregate','accounts','agent_registry','resolution'}))
    k.add_system(SystemState('INVARIANT_SYSTEM','CONSERVATION_CHECK',set()))
    k.add_system(SystemState('SNAPSHOT_SYSTEM','SNAPSHOT',set()))

    specs=[
      CouplingSpec('RESOLUTION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('aggregate','accounts','agent_registry','resolution'),('aggregate','accounts'),('aggregate','accounts','agent_registry','resolution'),
        'EVENT',Phase.EXOGENOUS_INPUTS),
      CouplingSpec('INVARIANT_SYSTEM','v1',RuntimeObjectClass.SYSTEM,(),('all_state',),(),
        'ANNUAL',Phase.CONSERVATION_CHECK),
      CouplingSpec('SNAPSHOT_SYSTEM','v1',RuntimeObjectClass.SYSTEM,(),('all_state',),(),
        'ANNUAL',Phase.SNAPSHOT_CLOSE)]
    for s in specs: k.scheduler.register_coupling(s)

    # Insert reverse to prove scheduler owns order.
    k.scheduler.schedule(ScheduledEvent('snapshot',D('1'),Phase.SNAPSHOT_CLOSE,0,'snapshot','SNAPSHOT_SYSTEM'))
    k.scheduler.schedule(ScheduledEvent('check',D('1'),Phase.CONSERVATION_CHECK,0,'check','INVARIANT_SYSTEM'))
    k.scheduler.schedule(ScheduledEvent('resolve',D('1'),Phase.EXOGENOUS_INPUTS,0,'resolve','RESOLUTION_SYSTEM'))

    snapshots=[]
    rt=ScheduledSimulationRuntime(k)

    def resolution_handler(kernel,e):
        agent=AgentState('FIRM_01',AgentKind.PRIVATE_SPONSOR,'EARTH:X','firm_cash')
        return kernel.expose_agent_from_aggregate(1,'FIRM_SECTOR',agent,D('25'),1,('A1',),{'R':D('2')},{'VEH':D('0.25')},('H1',)).resolution_id

    def invariant_handler(kernel,e):
        kernel.assert_methodology_invariants()
        return 'CHECKED'

    def snapshot_handler(kernel,e):
        fp=kernel.methodology_fingerprint()
        snapshots.append(fp)
        return fp

    rt.register_handler('RESOLUTION_SYSTEM',resolution_handler)
    rt.register_handler('INVARIANT_SYSTEM',invariant_handler)
    rt.register_handler('SNAPSHOT_SYSTEM',snapshot_handler)
    rt.seal()
    run_result=rt.run()
    return k,run_result,tuple(snapshots)

def methodology_ensemble_fixture():
    axes=(
      ExperimentAxis('universe',AxisKind.SCENARIO,('NULL','RICH')),
      ExperimentAxis('depreciation',AxisKind.PARAMETER,('0.05','0.10')))
    h=EnsembleHarness('BUILD4_MVP_METHODOLOGY_R1',axes)

    def runner(case):
        coords={name:value for name,kind,value in case.coordinates}
        stock=D('0') if coords['universe']=='NULL' else D('100')
        rate=D(coords['depreciation'])
        rid=RunIdentity(coords['universe'],'v1','SYNTH_ENSEMBLE_INPUT','BUILD4_MVP_METHODOLOGY_R1',
                        (('depreciation',str(rate)),))
        k=MethodologyHardenedBuild4Kernel(rid)
        k.add_node('OFF:T1',NodeKind.OFFWORLD)
        k.state.assets['A1']=Asset('A1','P','OFF:T1',AssetKind.PRODUCTIVE,D('100'))
        k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',stock,stock,stock,stock))
        k.depreciate(1,'A1',rate)
        k.assert_methodology_invariants()
        return k.methodology_fingerprint(),{'universe':coords['universe'],'closing_capital':k.state.assets['A1'].book_value,'remaining_resource':k.resources['RES'].remaining}

    results=h.run(runner)
    return h,results
