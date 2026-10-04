from __future__ import annotations
from decimal import Decimal as D

from .accounting import AccountingPeriodSnapshot
from .build3 import RunIdentity
from .financing_protocol import build_financing_request
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, RuntimeObjectClass, ScenarioResource, SystemState
from .policy import build_decision_snapshot
from .policies.manifest import test_only_manifest
from .publication_protocol import build_publication_request
from .scheduler import CouplingSpec, Phase, ScheduledEvent
from .underwriting import mvp_validation_underwriting_table, underwriting_snapshot_facts

def publication_handoff_kernel(universe_id='RICH_PUBLIC_3',stock='20',
                               false_positive='0.20',false_negative='0.20',
                               public_objective=True,publisher_possesses=True):
    manifest=test_only_manifest()
    rid=RunIdentity(
        universe_id,'v1','SYNTH_BUILD5_PUBLICATION_TEST002B','BUILD5_PUBLICATION_FINANCIER_TEST002B',
        (
            ('world_remote_false_positive',str(false_positive)),
            ('world_remote_false_negative',str(false_negative)),
            ('financier_detection_rate',str(manifest.parameter('agent_detection_rate').value)),
            ('financier_false_positive_rate',str(manifest.parameter('agent_false_positive_rate').value)),
        ))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)

    k.add_account('public_funds','PUB','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('fin_funds','FIN','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('sponsor_funds','SPN','EARTH:X',AccountKind.FUNDS,D('0'))
    k.add_account('earth_supplier','SUP','EARTH:X',AccountKind.SUPPLIER,D('0'))
    k.add_account('explore_cash','EXP','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_account('project_cash','SPN','OFF:T1',AccountKind.PROJECT_CASH,D('0'))

    k.add_project('EXP','OFF:T1','explore_cash',{'PUB':D('1')})
    k.add_project('P','OFF:T1','project_cash',{'SPN':D('1')})

    pub=AgentState(
        'PUB',AgentKind.PUBLIC,'EARTH:X','public_funds',
        capabilities={'EXPLORE'},objectives=('PUBLIC_INFORMATION',) if public_objective else (),
        decision_policy='PUBLIC_PUBLISHER_V1')
    pub.beliefs['RES']=D('0.20')
    pub.priors['RES']=D('0.20')
    k.add_agent(pub)

    fin=AgentState(
        'FIN',AgentKind.PRIVATE_FINANCIER,'EARTH:X','fin_funds',
        capabilities={'FINANCE'},objectives=('RETURN',),
        decision_policy='FINANCIER_SCREENING_V1')
    fin.beliefs['resource_exists']=D('0.20')
    fin.priors['resource_exists']=D('0.20')
    k.add_agent(fin)

    k.add_agent(AgentState(
        'SPN',AgentKind.PRIVATE_SPONSOR,'EARTH:X','sponsor_funds',
        capabilities=set(),objectives=('RETURN',)))

    q=D(stock)
    k.add_resource(ScenarioResource('RES','OFF:T1','RESOURCE_X',q,q,q,q))
    k.set_resource_constraint('EARTH:X',1,D('1000'),D('0.10'))

    # Test 002B begins from a legitimate private public-agency observation.
    # The world-side Build-3 observation mechanism generates it before the
    # publication decision. Test 002A separately qualifies the autonomous
    # decision that can lead to this observation.
    k.add_commitment('C-PUB-EXP','PUB','EXP',D('10'))
    k.disburse(1,'C-PUB-EXP','public_funds',D('10'))
    k.reserve_earth_supply('EARTH:X',1,D('10'))
    obs,wip,draw=k.explore_paid(
        1,'PUB','RES','EXP','earth_supplier',D('10'),'REMOTE',False,
        D(false_positive),D(false_negative))
    if not publisher_possesses:
        k.agents['PUB'].information.discard(obs.id)

    k.add_system(SystemState('PUBLICATION_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState(
        'PUBLICATION_SYSTEM','PUBLIC_INFORMATION_TRANSFER',
        {'public_information','agent_information','agent_beliefs','events'}))

    k.scheduler.register_coupling(CouplingSpec(
        'PUBLICATION_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
        (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
    k.scheduler.register_coupling(CouplingSpec(
        'PUBLICATION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
        ('public_information','agent_information','agent_beliefs','events'),
        ('publication_decision','observation','publisher_information'),
        ('public_information','agent_information','agent_beliefs','events'),
        'EVENT',Phase.INFORMATION_UPDATE,perspective='WORLD_SIM'))

    request=build_publication_request('PUBREQ-1',1,obs.id,'PUBLIC_FINANCIERS')
    snapshot=build_decision_snapshot(k,'PUB','1',D('1'),())
    snap_ref=k.scheduler.open_decision_window('1',snapshot.fingerprint())
    k.scheduler.schedule(ScheduledEvent(
        'public-publication-decision',D('1'),Phase.DECISION_WINDOW,0,'PUB',
        'PUBLICATION_DECISION_ORCHESTRATOR',snapshot_ref=snap_ref))
    k.scheduler.schedule(ScheduledEvent(
        'public-information-transfer',D('2'),Phase.INFORMATION_UPDATE,0,'PUBINFO',
        'PUBLICATION_SYSTEM',parent_ids=('public-publication-decision',)))

    before_publication=AccountingPeriodSnapshot.capture(k,1)
    return k,snapshot,request,manifest,obs,wip,draw,before_publication

def financier_snapshot_after_publication(k,obs_id):
    table=mvp_validation_underwriting_table()
    facts=underwriting_snapshot_facts(table,'GENERIC_RESOURCE_PROJECT_MVP',1)
    snapshot=build_decision_snapshot(k,'FIN','1B',D('3'),facts)
    request=build_financing_request('REQ-002B',1,'SPN','P',D('60'),'DEVELOPMENT',(obs_id,))
    return snapshot,request,table
