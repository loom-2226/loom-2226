from __future__ import annotations
from decimal import Decimal as D
from .mvp_state import (
    BUILD5_REQUIRED_UNDERWRITING_KEYS,
    BUILD5_REQUIRED_BELIEF_KEYS,
    BUILD5_REQUIRED_PRIOR_KEYS,
    FinancingDecision,
    FinancingDecisionOutcome,
    FinancingReasonCode,
    FinancingRequest,
)
from .policy import DecisionSnapshot, FactState

FINANCING_PROTOCOL_VERSION='BUILD5_FINANCING_PROTOCOL_0_2'

def build_financing_request(request_id,year,sponsor_id,project_id,amount,stage,
                            disclosed_observation_ids=(),currency_unit='MODEL_CURRENCY'):
    return FinancingRequest(
        str(request_id),int(year),str(sponsor_id),str(project_id),D(amount),str(stage),
        tuple(disclosed_observation_ids),
        BUILD5_REQUIRED_UNDERWRITING_KEYS,
        BUILD5_REQUIRED_BELIEF_KEYS,
        BUILD5_REQUIRED_PRIOR_KEYS,
        str(currency_unit),'FINANCING_REQUEST_V1').validate_protocol()

def required_unknown_inputs(request:FinancingRequest,snapshot:DecisionSnapshot):
    request.validate_protocol()
    unknown=[]
    facts={f.key:f for f in snapshot.admitted_facts}
    for key in request.required_underwriting_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    beliefs=dict(snapshot.beliefs)
    for key in request.required_belief_keys:
        if key not in beliefs:
            unknown.append(f'belief.{key}')
    priors=dict(snapshot.priors)
    for key in request.required_prior_keys:
        if key not in priors:
            unknown.append(f'prior.{key}')
    return tuple(sorted(unknown))

def build_financing_decision(decision_id,request:FinancingRequest,financier_id,outcome,
                             reason_code,reason,snapshot:DecisionSnapshot,policy_version,
                             amount=D('0'),instrument=''):
    outcome=FinancingDecisionOutcome(outcome)
    reason_code=FinancingReasonCode(reason_code)
    unknowns=required_unknown_inputs(request,snapshot)
    if unknowns and outcome!=FinancingDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown beliefs/priors/underwriting inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==FinancingDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when all required decision inputs are known')
    approved=(outcome==FinancingDecisionOutcome.APPROVE)
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    decision=FinancingDecision(
        str(decision_id),request.id,str(financier_id),approved,D(amount),str(instrument),str(reason),
        outcome,reason_code,unknowns,snapshot_ref,str(policy_version),
        'FINANCING_DECISION_V1')
    return decision.validate_protocol(request)
