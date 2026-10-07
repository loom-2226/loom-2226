"""Bounded public choice among visible, still-uncharacterized REMOTE options."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Iterable

from .opportunities import MissionCandidate

QUESTION = 'WATER_BEARING_MATERIAL_PRESENT'


@dataclass(frozen=True)
class ExplorationChoice:
    outcome: str
    candidate_id: str = ''
    body_id: str = ''
    reason: str = ''


def choose_remote_characterization(*, candidates: Iterable[MissionCandidate],
                                   characterized_bodies: Iterable[str], public_balance,
                                   remote_cost, decision_key: str) -> ExplorationChoice:
    """An unresolved body question supplies information need, without a body score."""
    balance=Decimal(public_balance)
    cost=Decimal(remote_cost)
    if not balance.is_finite() or not cost.is_finite() or cost<=0 or balance<cost:
        return ExplorationChoice('WAIT',reason='FINITE_PUBLIC_BUDGET')
    known=frozenset(characterized_bodies)
    seen=set();eligible=[]
    for candidate in candidates:
        if candidate.candidate_id in seen:raise ValueError('duplicate mission candidate')
        seen.add(candidate.candidate_id)
        if (candidate.accessibility_status=='SCREENED' and
                candidate.capability_status=='AVAILABLE' and
                candidate.qualification_state=='PRELIMINARY_COMPARABLE' and
                candidate.destination_body_id not in known):
            eligible.append(candidate)
    if not eligible:return ExplorationChoice('WAIT',reason='NO_UNRESOLVED_SCREENED_OPPORTUNITY')
    # All currently eligible unknown questions have the same admitted
    # information need. This stable tie-break encodes no body preference.
    chosen=min(eligible,key=lambda c:(sha256((decision_key+'|'+c.candidate_id).encode()).hexdigest(),c.candidate_id))
    return ExplorationChoice('SELECT',chosen.candidate_id,chosen.destination_body_id,
                             'UNRESOLVED_BODY_CHARACTERIZATION')
