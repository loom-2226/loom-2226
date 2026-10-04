from __future__ import annotations
from decimal import Decimal as D

from .build3 import RunIdentity
from .exploration_protocol import build_exploration_request
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, ScenarioResource, SystemState
from .policy import FactState, SnapshotFact, build_decision_snapshot
from .surface_prospecting import SurfaceProspectingModel


def test007a_surface_model():
    return SurfaceProspectingModel(
        model_id='SURFACE_PRESENCE_MODEL_TEST007A_V1',
        world_false_positive=D('0.05'),
        world_false_negative=D('0.05'),
        agent_detection_rate=D('0.95'),
        agent_false_positive_rate=D('0.05'),
        remote_world_false_positive_reference=D('0.20'),
        remote_world_false_negative_reference=D('0.20'),
        epistemic_status='TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE',
        source_ref='BUILD5_IMPLEMENTATION_AUTHORIZATION_007_SURFACE_PROSPECTING_TEST007A',
    ).validate()


def surface_prospecting_kernel(universe_id='RICH_PUBLIC_3',stock='20',balance='100',
                               remote_cost='10',surface_cost='25',
                               surface_capability=True):
    model=test007a_surface_model()
    rid=RunIdentity(
        universe_id,'v1','SYNTH_BUILD5_SURFACE_TEST007A','BUILD5_SURFACE_PROSPECTING_TEST007A',
        (
            ('remote_observation_false_positive','0.20'),
            ('remote_observation_false_negative','0.20'),
            ('remote_observation_cost',str(remote_cost)),
            ('surface_observation_false_positive',str(model.world_false_positive)),
            ('surface_observation_false_negative',str(model.world_false_negative)),
            ('surface_agent_detection_rate',str(model.agent_detection_rate)),
            ('surface_agent_false_positive_rate',str(model.agent_false_positive_rate)),
            ('surface_prospecting_cost',str(surface_cost)),
            ('surface_model_fingerprint',model.fingerprint()),
        ))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('public_funds','PUB','EARTH:X',AccountKind.FUNDS,D(balance))
    k.add_account('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,D('0'))
    k.add_account('explore_cash','EXP','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_project('EXP','OFF:T1','explore_cash',{'PUB':D('1')})

    capabilities={'EXPLORE'}
    if surface_capability:
        capabilities.add('SURFACE_PROSPECT')
    agent=AgentState(
        'PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',
        capabilities=capabilities,objectives=('PUBLIC_INFORMATION',),
        decision_policy='PUBLIC_EXPLORER_V1')
    agent.beliefs['RES']=D('0.20')
    agent.priors['RES']=D('0.20')
    k.add_agent(agent)

    q=D(stock)
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',q,q,q,q))
    k.set_resource_constraint('EARTH:X',1,D('1000'),D('0.10'))
    k.set_resource_constraint('EARTH:X',2,D('1000'),D('0.10'))

    for system in (
        SystemState('PUBLIC_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
        SystemState(
            'PUBLIC_FINANCE_EXECUTOR','PUBLIC_EXPLORATION_FINANCE',
            {'accounts','commitments','resource_constraints'}),
        SystemState(
            'REMOTE_OBSERVATION_SYSTEM','REMOTE_OBSERVATION',
            {'accounts','transactions','assets','observations','agent_information','agent_beliefs',
             'earth_impact','resource_constraints','events'}),
        SystemState(
            'SURFACE_PROSPECTING_SYSTEM','SURFACE_PROSPECTING',
            {'accounts','transactions','assets','observations','agent_information',
             'earth_impact','resource_constraints','events','surface_prospecting_records'}),
        SystemState(
            'SURFACE_INFORMATION_UPDATE_SYSTEM','OBSERVATION_INFORMATION_UPDATE',
            {'agent_beliefs','events','observation_belief_update_records'}),
    ):
        k.add_system(system)

    return k,model,D(remote_cost),D(surface_cost)


def remote_snapshot_and_request(k,remote_cost,period_key='REMOTE-1',effective_time='1'):
    request=build_exploration_request('XREQ-007A-REMOTE',1,'EXP','RES','REMOTE')
    fact=SnapshotFact(
        'exploration.REMOTE_COST',FactState.KNOWN,str(remote_cost),
        'TEST_ONLY:BUILD5_TEST007A_REMOTE_COST')
    return build_decision_snapshot(k,'PUB',period_key,D(effective_time),(fact,)),request


def surface_snapshot_and_request(k,surface_cost,prior_observation_id,
                                 period_key='SURFACE-2',effective_time='2',
                                 cost_known=True,request_id='XREQ-007A-SURFACE'):
    request=build_exploration_request(
        request_id,2,'EXP','RES','SURFACE',
        prerequisite_observation_id=prior_observation_id)
    fact=SnapshotFact(
        'exploration.SURFACE_COST',
        FactState.KNOWN if cost_known else FactState.UNKNOWN,
        str(surface_cost) if cost_known else None,
        'TEST_ONLY:BUILD5_TEST007A_SURFACE_COST')
    return build_decision_snapshot(
        k,'PUB',period_key,D(effective_time),(fact,)),request
