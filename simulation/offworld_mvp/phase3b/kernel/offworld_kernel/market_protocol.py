from __future__ import annotations
from decimal import Decimal as D

from .mvp_state import (
    BUILD5_SALE_REQUIRED_FACT_KEYS,
    SaleDecision,
    SaleDecisionOutcome,
    SaleDecisionRequest,
    SaleReasonCode,
)
from .policy import DecisionSnapshot, FactState

SALE_PROTOCOL_VERSION='BUILD5_SALE_DECISION_PROTOCOL_0_1'

def build_sale_decision_request(request_id,year,project_id,resource_id,
                                market_state_id,observation_id,
                                currency_unit='MODEL_CURRENCY',
                                quantity_unit='MODEL_RESOURCE_UNIT_BY_FAMILY'):
    return SaleDecisionRequest(
        str(request_id),int(year),str(project_id),str(resource_id),
        str(market_state_id),str(observation_id),
        BUILD5_SALE_REQUIRED_FACT_KEYS,str(currency_unit),str(quantity_unit),
        'SALE_DECISION_REQUEST_V1').validate_protocol()

def required_unknown_sale_inputs(request:SaleDecisionRequest,
                                 snapshot:DecisionSnapshot):
    request.validate_protocol()
    facts={f.key:f for f in snapshot.admitted_facts}
    unknown=[]
    for key in request.required_fact_keys:
        fact=facts.get(key)
        if fact is None or fact.state!=FactState.KNOWN or fact.value is None:
            unknown.append(key)
    return tuple(sorted(unknown))

def build_sale_decision(decision_id,request,actor_id,outcome,reason_code,
                        reason,snapshot,policy_version,offered_quantity=D('0')):
    outcome=SaleDecisionOutcome(outcome)
    reason_code=SaleReasonCode(reason_code)
    unknowns=required_unknown_sale_inputs(request,snapshot)
    if unknowns and outcome!=SaleDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('required unknown sale inputs must produce BLOCKED_UNKNOWN')
    if not unknowns and outcome==SaleDecisionOutcome.BLOCKED_UNKNOWN:
        raise ValueError('BLOCKED_UNKNOWN not allowed when sale inputs are known')
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    return SaleDecision(
        str(decision_id),request.id,str(actor_id),outcome,D(offered_quantity),
        str(reason),reason_code,unknowns,snapshot_ref,str(policy_version),
        'SALE_DECISION_V1').validate_protocol(request)
