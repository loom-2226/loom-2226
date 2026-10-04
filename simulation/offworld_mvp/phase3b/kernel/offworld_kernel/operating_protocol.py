from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_OPERATING_REQUIRED_BELIEF_KEYS,
    BUILD5_OPERATING_REQUIRED_FACT_KEYS,
    BUILD5_OPERATING_REQUIRED_PRIOR_KEYS,
    OperatingCycleDecision,
    OperatingCycleDecisionOutcome,
    OperatingCycleReasonCode,
    OperatingCycleRequest,
)
from .policy import DecisionSnapshot, FactState

OPERATING_PROTOCOL_VERSION='BUILD5_OPERATING_CYCLE_PROTOCOL_0_1'

def build_operating_cycle_request(request_id,year,project_id,resource_id,asset_id,
                                  observation_id,currency_unit='MODEL_CURRENCY',
                                  quantity_unit='MODEL_RESOURCE_UNIT_BY_FAMILY'):
    return OperatingCycleRequest(
        str(request_id),int(year),str(project_id),str(resource_id),str(asset_id),
        str(observation_id),BUILD5_OPERATING_REQUIRED_FACT_KEYS,
        BUILD5_OPERATING_REQUIRED_BELIEF_KEYS,BUILD5_OPERATING_REQUIRED_PRIOR_KEYS,
        str(currency_unit),str(quantity_unit),'OPERATING_CYCLE_REQUEST_V1'
    ).validate_protocol()

def required_unknown_operating_inputs(request:OperatingCycleRequest,
                                      snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    beliefs=dict(snapshot.beliefs)
    for key in request.required_belief_keys:
        if key not in beliefs: unknown.append(f'belief.{key}')
    priors=dict(snapshot.priors)
    for key in request.required_prior_keys:
        if key not in priors: unknown.append(f'prior.{key}')
    return tuple(sorted(unknown))

def build_operating_cycle_decision(decision_id,request,actor_id,outcome,reason_code,
                                   reason,snapshot,policy_version,
                                   requested_financing=D('0'),
                                   planned_quantity=D('0'),
                                   authorized_opex=D('0')):
    outcome=OperatingCycleDecisionOutcome(outcome)
    reason_code=OperatingCycleReasonCode(reason_code)
    unknowns=required_unknown_operating_inputs(request,snapshot)
    if unknowns and outcome!=OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown operating inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when operating inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return OperatingCycleDecision(
        str(decision_id),request.id,str(actor_id),outcome,D(requested_financing),
        D(planned_quantity),D(authorized_opex),str(reason),reason_code,unknowns,
        snapshot_ref,str(policy_version),'OPERATING_CYCLE_DECISION_V1'
    ).validate_protocol(request)
