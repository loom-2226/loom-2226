from __future__ import annotations
from dataclasses import replace
from decimal import Decimal as D

from .build3 import RunIdentity
from .financing_protocol import build_financing_request
from .methodology import MethodologyHardenedBuild4Kernel
from .model import AccountKind, NodeKind
from .mvp_state import AgentKind, AgentState, RuntimeObjectClass, SystemState
from .policy import DecisionSnapshot, build_decision_snapshot
from .policies.financier_v1 import posterior_from_signal
from .policies.manifest import test_only_manifest
from .scheduler import CouplingSpec, Phase, ScheduledEvent
from .underwriting import (
    UnderwritingInputKind,
    mvp_validation_underwriting_table,
    underwriting_snapshot_facts,
)

def synthetic_policy_manifest():
    return test_only_manifest()

def financing_request(amount='60',observations=('OBS-1',)):
    return build_financing_request('REQ-1',1,'SPN','P',D(amount),'DEVELOPMENT',observations)

def standalone_snapshot(belief='0.50',prior='0.20',account='100',
                        observations=('OBS-1',),price=None,development=None,opex=None):
    facts=list(underwriting_snapshot_facts(
        mvp_validation_underwriting_table(),'GENERIC_RESOURCE_PROJECT_MVP',1))
    overrides={
        'underwriting.PRICE':price,
        'underwriting.DEVELOPMENT_CAPEX':development,
        'underwriting.OPERATING_COST':opex,
    }
    for i,f in enumerate(facts):
        if f.key in overrides and overrides[f.key] is not None:
            facts[i]=replace(f,value=str(overrides[f.key]),source_ref=f.source_ref+':COUNTERFACTUAL')
    return DecisionSnapshot(
        agent_id='FIN',
        agent_kind='PRIVATE_FINANCIER',
        node_id='EARTH:X',
        period_key='1',
        effective_time='1',
        account_balance=D(account),
        capabilities=('FINANCE',),
        objectives=('RETURN',),
        information_refs=tuple(observations),
        beliefs=(('resource_exists',D(belief)),),
        priors=(('resource_exists',D(prior)),),
        asset_refs=(),
        resource_holdings=(),
        claim_holdings=(),
        admitted_facts=tuple(facts),
    )

def snapshot_from_signal(signal,prior='0.20',**kwargs):
    m=synthetic_policy_manifest()
    posterior=posterior_from_signal(
        D(prior),signal,
        m.parameter('agent_detection_rate').value,
        m.parameter('agent_false_positive_rate').value)
    obs='OBS-POS' if signal=='POSITIVE' else 'OBS-NEG'
    return standalone_snapshot(str(posterior),prior=prior,observations=(obs,),**kwargs),obs

def scheduled_financier_kernel(belief='0.50',prior='0.20'):
    manifest=synthetic_policy_manifest()
    table=mvp_validation_underwriting_table()
    rid=RunIdentity(
        'BUILD5_TEST001','v1','SYNTH_BUILD5_TEST001','BUILD5_FINANCIER_TEST001',
        (('policy_manifest_hash',manifest.parameter_manifest_hash()),
         ('underwriting_table_hash',table.fingerprint())))
    k=MethodologyHardenedBuild4Kernel(rid)
    k.add_node('EARTH:X',NodeKind.EARTH)
    k.add_node('OFF:T1',NodeKind.OFFWORLD)
    k.add_account('fin_funds','FIN','EARTH:X',AccountKind.FUNDS,D('100'))
    k.add_account('project_cash','SPN','OFF:T1',AccountKind.PROJECT_CASH,D('0'))
    k.add_project('P','OFF:T1','project_cash',{'SPN':D('1')})
    agent=AgentState(
        'FIN',AgentKind.PRIVATE_FINANCIER,'EARTH:X','fin_funds',
        capabilities={'FINANCE'},objectives=('RETURN',))
    agent.information.add('OBS-1')
    agent.beliefs['resource_exists']=D(belief)
    agent.priors['resource_exists']=D(prior)
    k.add_agent(agent)
    k.add_system(SystemState('DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()))
    k.add_system(SystemState('FINANCE_EXECUTOR','FINANCE_EXECUTION',{'accounts','transactions','commitments'}))
    k.scheduler.register_coupling(CouplingSpec(
        'DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
        (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
    k.scheduler.register_coupling(CouplingSpec(
        'FINANCE_EXECUTOR','v1',RuntimeObjectClass.SYSTEM,
        ('accounts','transactions','commitments'),('decision',),
        ('accounts','transactions','commitments'),'EVENT',Phase.COMMITMENT_DISBURSEMENT))
    facts=underwriting_snapshot_facts(table,'GENERIC_RESOURCE_PROJECT_MVP',1)
    snapshot=build_decision_snapshot(k,'FIN','1',D('1'),facts)
    snap_ref=k.scheduler.open_decision_window('1',snapshot.fingerprint())
    k.scheduler.schedule(ScheduledEvent(
        'financier-decision',D('1'),Phase.DECISION_WINDOW,0,'FIN','DECISION_ORCHESTRATOR',
        snapshot_ref=snap_ref))
    k.scheduler.schedule(ScheduledEvent(
        'finance-execute',D('1'),Phase.COMMITMENT_DISBURSEMENT,0,'FINANCE','FINANCE_EXECUTOR',
        parent_ids=('financier-decision',)))
    return k,snapshot,manifest,table
