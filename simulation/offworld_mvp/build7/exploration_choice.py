"""Bounded public choice among visible, still-uncharacterized REMOTE options."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from typing import Iterable

from .opportunities import MissionCandidate

QUESTION = 'BODY_MATERIAL_CHARACTERIZATION'


@dataclass(frozen=True)
class ExplorationChoice:
    outcome: str
    candidate_id: str = ''
    body_id: str = ''
    reason: str = ''
    cost: Decimal | None = None


def choose_remote_characterization(*, candidates: Iterable[MissionCandidate],
                                   characterized_bodies: Iterable[str], public_balance,
                                   cost_for_candidate, decision_key: str) -> ExplorationChoice:
    """An unresolved body question supplies information need, without a body score."""
    balance=Decimal(public_balance)
    if not balance.is_finite() or balance < 0:
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
            cost=cost_for_candidate(candidate)
            if cost is None:
                continue
            cost=Decimal(cost)
            if cost.is_finite() and cost >= 0 and balance >= cost:
                eligible.append((candidate,cost))
    if not eligible:return ExplorationChoice('WAIT',reason='NO_UNRESOLVED_SCREENED_OPPORTUNITY')
    # Equal unresolved information need: minimize actual mission cost first.
    # The deterministic hash only breaks exact cost ties.
    chosen,cost=min(eligible,key=lambda pair:(pair[1],sha256((decision_key+'|'+pair[0].candidate_id).encode()).hexdigest(),pair[0].candidate_id))
    return ExplorationChoice('SELECT',chosen.candidate_id,chosen.destination_body_id,
                             'UNRESOLVED_BODY_CHARACTERIZATION',cost)
