from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL,
    ExplorationDecision,
    ExplorationDecisionOutcome,
    ExplorationReasonCode,
    ExplorationRequest,
)
from .policy import DecisionSnapshot, FactState

EXPLORATION_PROTOCOL_VERSION='BUILD5_PUBLIC_EXPLORATION_PROTOCOL_0_1'

def build_exploration_request(request_id,year,project_id,resource_id,channel='REMOTE',
                              currency_unit='MODEL_CURRENCY',prerequisite_observation_id='',
                              body_id='',question_ref=''):
    channel=str(channel)
    facts=BUILD5_PUBLIC_EXPLORATION_REQUIRED_FACT_KEYS_BY_CHANNEL[channel]
    version=('EXPLORATION_REQUEST_BODY_V1' if body_id else
             'EXPLORATION_REQUEST_V1' if channel=='REMOTE' else 'EXPLORATION_REQUEST_V2')
    return ExplorationRequest(
        id=str(request_id),year=int(year),project_id=str(project_id),
        resource_id=str(resource_id),channel=channel,
        required_fact_keys=tuple(facts),
        prerequisite_observation_id=str(prerequisite_observation_id),
        currency_unit=str(currency_unit),request_version=version,
        body_id=str(body_id),question_ref=str(question_ref)).validate_protocol()

def required_unknown_exploration_inputs(request:ExplorationRequest,snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))

def build_exploration_decision(decision_id,request:ExplorationRequest,actor_id,outcome,
                               reason_code,reason,snapshot:DecisionSnapshot,policy_version,
                               authorized_cost=D('0')):
    outcome=ExplorationDecisionOutcome(outcome)
    reason_code=ExplorationReasonCode(reason_code)
    unknowns=required_unknown_exploration_inputs(request,snapshot)
    if unknowns and outcome!=ExplorationDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown exploration inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==ExplorationDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when exploration inputs are known')
    authorized=(outcome==ExplorationDecisionOutcome.AUTHORIZE)
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    decision=ExplorationDecision(
        str(decision_id),request.id,str(actor_id),authorized,D(authorized_cost),request.channel,
        str(reason),outcome,reason_code,unknowns,snapshot_ref,str(policy_version),
        'EXPLORATION_DECISION_V1')
    return decision.validate_protocol(request)
