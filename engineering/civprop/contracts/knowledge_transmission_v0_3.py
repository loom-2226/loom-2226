"""Phase 8 knowledge publication and transmission.
NON_CANON / MACHINERY TEST ONLY.
"""
from dataclasses import dataclass

CHANNELS=frozenset({"PUBLICATION","SALE","CONTRACT","LEAK","TREATY_FILING"})
LAGS=frozenset({"L0","L1","L2","L3"})
VISIBILITIES=frozenset({"PRIVATE","COUNTERPARTY","PUBLIC"})

@dataclass(frozen=True)
class InformationTransmissionV03:
    transmission_id: str
    source_actor_id: str
    recipient_actor_id: str
    claim_id: str
    channel: str
    lag_class: str
    visibility: str
    released_year: int
    delivery_status: str
    authority_class: str="SIMULATED_INFORMATION_TRANSMISSION"

@dataclass(frozen=True)
class ReceivedClaimV03:
    recipient_actor_id: str
    claim: object
    source_actor_id: str
    transmission_id: str
    received_year: int
    authority_class: str="ACTOR_VISIBLE_TRANSMITTED_CLAIM"

def transmit_claim(*,claim,source_actor_id,recipient_actor_id,channel,lag_class,
                   visibility,released_year,delivery_authorized):
    if claim.actor_id != source_actor_id:
        raise ValueError("SOURCE_ACTOR_DOES_NOT_OWN_CLAIM")
    if channel not in CHANNELS: raise ValueError("UNDECLARED_INFORMATION_CHANNEL")
    if lag_class not in LAGS: raise ValueError("UNKNOWN_LAG_CLASS")
    if visibility not in VISIBILITIES: raise ValueError("UNKNOWN_VISIBILITY")
    status="RELEASED_PENDING_LAG" if delivery_authorized else "BLOCKED"
    return InformationTransmissionV03(
        f"tx:{source_actor_id}:{recipient_actor_id}:{claim.claim_id}:{released_year}",
        source_actor_id,recipient_actor_id,claim.claim_id,channel,lag_class,
        visibility,released_year,status)

def receive_claim(*,transmission,claim,lag_satisfied,received_year):
    if transmission.claim_id != claim.claim_id: raise ValueError("CLAIM_MISMATCH")
    if transmission.delivery_status != "RELEASED_PENDING_LAG":
        raise PermissionError("TRANSMISSION_NOT_RELEASED")
    if not lag_satisfied: raise PermissionError("LAG_NOT_SATISFIED")
    if received_year < transmission.released_year:
        raise ValueError("RECEIVED_BEFORE_RELEASE")
    return ReceivedClaimV03(transmission.recipient_actor_id,claim,
        transmission.source_actor_id,transmission.transmission_id,received_year)
