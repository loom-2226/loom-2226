from __future__ import annotations
from decimal import Decimal as D
from .mvp_state import (
    BUILD5_REQUIRED_UNDERWRITING_KEYS,
    FinancingDecision,
    FinancingDecisionOutcome,
    FinancingReasonCode,
    FinancingRequest,
)

FINANCING_PROTOCOL_VERSION='BUILD5_FINANCING_PROTOCOL_0_1'

def build_financing_request(request_id,year,sponsor_id,project_id,amount,stage,
                            disclosed_observation_ids=(),currency_unit='MODEL_CURRENCY'):
    return FinancingRequest(
        str(request_id),int(year),str(sponsor_id),str(project_id),D(amount),str(stage),
        tuple(disclosed_observation_ids),BUILD5_REQUIRED_UNDERWRITING_KEYS,
        str(currency_unit),'FINANCING_REQUEST_V1').validate_protocol()

def build_financing_decision(decision_id,request:FinancingRequest,financier_id,outcome,
                             reason_code,reason,input_snapshot_ref,policy_version,
                             amount=D('0'),instrument='',unknown_input_keys=()):
    outcome=FinancingDecisionOutcome(outcome)
    reason_code=FinancingReasonCode(reason_code)
    approved=(outcome==FinancingDecisionOutcome.APPROVE)
    decision=FinancingDecision(
        str(decision_id),request.id,str(financier_id),approved,D(amount),str(instrument),str(reason),
        outcome,reason_code,tuple(unknown_input_keys),str(input_snapshot_ref),str(policy_version),
        'FINANCING_DECISION_V1')
    return decision.validate_protocol(request)
