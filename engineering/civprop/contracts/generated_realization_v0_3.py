"""Phase 5 GENERATED_REALIZATION contract for unresolved Solar characterization.

NON_CANON / MACHINERY TEST ONLY. Generated realization is evaluator-only simulated
world state. It is neither empirical authority nor actor knowledge and cannot be
read by actor decision machinery except through an explicit observation transform.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from typing import Optional

REALIZATION_STATES=frozenset({"PRESENT","ABSENT","UNRESOLVED"})

@dataclass(frozen=True)
class GeneratedRealizationV03:
    realization_id: str
    question_id: str
    location_id: str
    material_family: str
    state: str
    generation_key: str
    provenance_refs: tuple[str,...]
    actor_visible: bool=False
    authority_class: str="GENERATED_REALIZATION_NON_EMPIRICAL"

@dataclass(frozen=True)
class GeneratedObservationV03:
    observation_id: str
    question_id: str
    location_id: str
    observed_status: str
    source_realization_id: str
    year: int
    visibility: str="PRIVATE"
    authority_class: str="SIMULATED_OBSERVATION_FROM_GENERATED_REALIZATION"


def generate_realization(*, question_id: str, location_id: str, material_family: str,
                         seed: int, prevalence: Optional[float], provenance_refs: tuple[str,...]) -> GeneratedRealizationV03:
    if not provenance_refs: raise ValueError("generated realization requires provenance")
    if prevalence is None:
        state="UNRESOLVED"
    else:
        p=float(prevalence)
        if not 0 <= p <= 1: raise ValueError("prevalence must be in [0,1]")
        payload=f"{seed}|{question_id}|{location_id}|{material_family}".encode()
        u=int.from_bytes(hashlib.sha256(payload).digest()[:8],"big")/2**64
        state="PRESENT" if u < p else "ABSENT"
    key=hashlib.sha256(f"{seed}|{question_id}".encode()).hexdigest()[:20]
    return GeneratedRealizationV03(f"generated:{question_id}:{key}",question_id,location_id,
        material_family,state,key,tuple(provenance_refs))


def observe_generated_realization(*, realization: GeneratedRealizationV03, observation_id: str,
                                  year: int, authorized: bool) -> GeneratedObservationV03:
    if not authorized: raise PermissionError("actor cannot read evaluator realization directly")
    if realization.state=="UNRESOLVED": observed="UNRESOLVED_WITHOUT_AUTHORIZED_REALIZATION_MODEL"
    elif realization.state=="PRESENT": observed="OBSERVED_PRESENT"
    else: observed="OBSERVED_ABSENT"
    return GeneratedObservationV03(observation_id,realization.question_id,realization.location_id,
        observed,realization.realization_id,int(year))


def actor_view(realization: GeneratedRealizationV03):
    """Hard firewall: evaluator realization has no actor-visible representation."""
    raise PermissionError("GENERATED_REALIZATION_IS_EVALUATOR_ONLY")
