from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_SURPLUS_REQUIRED_FACT_KEYS,
    SurplusDistributionDecision,
    SurplusDistributionDecisionOutcome,
    SurplusDistributionReasonCode,
    SurplusDistributionRequest,
)
from .policy import DecisionSnapshot, FactState

SURPLUS_DISTRIBUTION_PROTOCOL_VERSION='BUILD5_SURPLUS_DISTRIBUTION_PROTOCOL_0_1'

def build_surplus_distribution_request(request_id,year,project_id,claim_id,
                                       currency_unit='MODEL_CURRENCY'):
    return SurplusDistributionRequest(
        str(request_id),int(year),str(project_id),str(claim_id),
        BUILD5_SURPLUS_REQUIRED_FACT_KEYS,str(currency_unit),
        'SURPLUS_DISTRIBUTION_REQUEST_V1').validate_protocol()

def required_unknown_surplus_inputs(request:SurplusDistributionRequest,
                                    snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))

def build_surplus_distribution_decision(
        decision_id,request,actor_id,outcome,reason_code,reason,
        snapshot,policy_version,reserve=D('0'),financier_return=D('0'),
        local_reinvestment=D('0'),owner_distribution=D('0')):
    outcome=SurplusDistributionDecisionOutcome(outcome)
    reason_code=SurplusDistributionReasonCode(reason_code)
    unknowns=required_unknown_surplus_inputs(request,snapshot)
    if unknowns and outcome!=SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown distribution inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when distribution inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return SurplusDistributionDecision(
        str(decision_id),request.id,str(actor_id),outcome,D(reserve),D(financier_return),
        D(local_reinvestment),D(owner_distribution),str(reason),reason_code,
        unknowns,snapshot_ref,str(policy_version),
        'SURPLUS_DISTRIBUTION_DECISION_V1').validate_protocol(request)
