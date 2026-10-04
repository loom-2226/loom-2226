from __future__ import annotations
from decimal import Decimal as D

from .build3 import RunIdentity
from .exploration_protocol import build_exploration_request
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, RuntimeObjectClass, ScenarioResource, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .scheduler import CouplingSpec, Phase, ScheduledEvent

def public_explorer_kernel(universe_id='RICH_PUBLIC_1',stock='20',balance='100',
                           cost='10',false_positive='0.20',false_negative='0.20',
                           objective=True,capability=True,cost_known=True):
    rid=RunIdentity(
        universe_id,'v1','SYNTH_BUILD5_PUBLIC_TEST002A','BUILD5_PUBLIC_EXPLORER_TEST002A',
        (
            ('remote_observation_false_positive',str(false_positive)),
            ('remote_observation_false_negative',str(false_negative)),
            ('remote_observation_cost',str(cost)),
        ))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('public_funds','PUB','EARTH:X',AccountKind.FUNDS,D(balance))
    k.add_account('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,D('0'))
    k.add_account('explore_cash','EXP','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_project('EXP','OFF:T1','explore_cash',{'PUB':D('1')})

    capabilities={'EXPLORE'} if capability else set()
    objectives=('PUBLIC_INFORMATION',) if objective else ()
    agent=AgentState(
        'PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',
        capabilities=capabilities,objectives=objectives,
        decision_policy='PUBLIC_EXPLORER_V1')
    agent.beliefs['RES']=D('0.20')
    agent.priors['RES']=D('0.20')
    k.add_agent(agent)

    q=D(stock)
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',q,q,q,q))
    k.set_resource_constraint('EARTH:X',1,D('1000'),D('0.10'))

    k.add_system(SystemState('PUBLIC_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState(
        'PUBLIC_FINANCE_EXECUTOR','PUBLIC_EXPLORATION_FINANCE',
        {'accounts','commitments','resource_constraints'}))
    k.add_system(SystemState(
        'REMOTE_OBSERVATION_SYSTEM','REMOTE_OBSERVATION',
        {'accounts','transactions','assets','observations','agent_information','agent_beliefs',
         'earth_impact','resource_constraints','events'}))

    k.scheduler.register_coupling(CouplingSpec(
        'PUBLIC_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
        (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
    k.scheduler.register_coupling(CouplingSpec(
        'PUBLIC_FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
        ('accounts','commitments','resource_constraints'),('exploration_decision',),
        ('accounts','commitments','resource_constraints'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))
    k.scheduler.register_coupling(CouplingSpec(
        'REMOTE_OBSERVATION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('accounts','transactions','assets','observations','agent_information','agent_beliefs',
         'earth_impact','resource_constraints','events'),
        ('exploration_decision','scenario_resource'),
        ('accounts','transactions','assets','observations','agent_information','agent_beliefs',
         'earth_impact','resource_constraints','events'),
        'EVENT',Phase.OPERATIONS,perspective='WORLD_SIM'))

    request=build_exploration_request('XREQ-1',1,'EXP','RES','REMOTE')
    fact=SnapshotFact(
        'exploration.REMOTE_COST',
        FactState.KNOWN if cost_known else FactState.UNKNOWN,
        str(cost) if cost_known else None,
        'TEST_ONLY:BUILD5_TEST002A_REMOTE_COST')
    snapshot=build_decision_snapshot(k,'PUB','1',D('1'),(fact,))
    snap_ref=k.scheduler.open_decision_window('1',snapshot.fingerprint())

    k.scheduler.schedule(ScheduledEvent(
        'public-explore-decision',D('1'),Phase.DECISION_WINDOW,0,'PUB',
        'PUBLIC_DECISION_ORCHESTRATOR',snapshot_ref=snap_ref))
    k.scheduler.schedule(ScheduledEvent(
        'public-explore-finance',D('1'),Phase.COMMITMENT_DISBURSEMENT,0,'PUB-FINANCE',
        'PUBLIC_FINANCE_EXECUTOR',parent_ids=('public-explore-decision',)))
    k.scheduler.schedule(ScheduledEvent(
        'public-remote-observation',D('1'),Phase.OPERATIONS,0,'PUB-OBS',
        'REMOTE_OBSERVATION_SYSTEM',
        parent_ids=('public-explore-decision','public-explore-finance')))

    return k,snapshot,request,D(false_positive),D(false_negative)
