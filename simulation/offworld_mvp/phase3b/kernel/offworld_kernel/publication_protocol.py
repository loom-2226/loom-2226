from __future__ import annotations
from hashlib import sha256

from .mvp_state import (
    PublicationDecision,
    PublicationDecisionOutcome,
    PublicationReasonCode,
    PublicationRequest,
)
from .policy import DecisionSnapshot

PUBLICATION_PROTOCOL_VERSION='BUILD5_PUBLICATION_PROTOCOL_0_1'

def build_publication_request(request_id,year,observation_id,audience='PUBLIC_FINANCIERS'):
    return PublicationRequest(
        str(request_id),int(year),str(observation_id),str(audience),
        'PUBLICATION_REQUEST_V1').validate_protocol()

def build_publication_decision(decision_id,request:PublicationRequest,actor_id,outcome,
                               reason_code,reason,snapshot:DecisionSnapshot,policy_version):
    outcome=PublicationDecisionOutcome(outcome)
    reason_code=PublicationReasonCode(reason_code)
    snapshot_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
    decision=PublicationDecision(
        str(decision_id),request.id,str(actor_id),
        outcome==PublicationDecisionOutcome.PUBLISH,
        str(reason),outcome,reason_code,snapshot_ref,str(policy_version),
        'PUBLICATION_DECISION_V1')
    return decision.validate_protocol(request)
