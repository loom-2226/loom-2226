from __future__ import annotations

"""Bounded adapter between E1 typed interaction and Navigator-owned flight output.

This module performs no flight calculation, ephemeris work, final plan solve,
state mutation, persistence, or execution. It packages already-produced Navigator
comparison candidates for review, then binds explicit authorization to the final
plan SHA that Navigator earns after candidate selection.
"""

from typing import Any, Mapping, Sequence

from engineering.experience_one.e1_flight_interaction_contract import (
    FlightAuthorization,
    FlightIntent,
    NavigatorCandidateRef,
    build_navigator_execution_request,
    build_review,
)


def _required_text(raw: Mapping[str, Any], key: str) -> str:
    value = str(raw.get(key) or "").strip()
    if not value:
        raise ValueError(f"Navigator candidate missing {key}")
    return value


def candidate_ref_from_navigator(
    plan_number: int,
    raw: Mapping[str, Any],
    *,
    route: str,
    strategy: str = "DIRECT_NAVIGATION",
) -> NavigatorCandidateRef:
    """Create a nonauthoritative reference to an existing Navigator candidate.

    Navigator comparison candidates currently expose metric/torch and quantitative
    comparison fields, while route/strategy are already known from the normalized
    Navigator mission. No final plan SHA exists at this stage and none is invented.
    """
    return NavigatorCandidateRef(
        plan_number=int(plan_number),
        route=str(route),
        strategy=str(strategy),
        metric=_required_text(raw, "metric"),
        torch=_required_text(raw, "torch"),
    )


def review_from_navigator_output(
    intent: FlightIntent,
    navigator_state_id: str,
    navigator_candidates: Sequence[Mapping[str, Any]],
    *,
    route: str,
    strategy: str = "DIRECT_NAVIGATION",
) -> dict[str, Any]:
    """Package Navigator-produced comparison candidates into an E1 review."""
    refs = tuple(
        candidate_ref_from_navigator(index, candidate, route=route, strategy=strategy)
        for index, candidate in enumerate(navigator_candidates, start=1)
    )
    return build_review(intent, refs, navigator_state_id).payload()


def authorized_request_for_finalized_navigator_plan(
    intent: FlightIntent,
    reviewed_navigator_state_id: str,
    navigator_candidates: Sequence[Mapping[str, Any]],
    authorization: FlightAuthorization,
    *,
    route: str,
    current_navigator_state_id: str,
    current_finalized_plan_sha256: str,
    strategy: str = "DIRECT_NAVIGATION",
) -> dict[str, Any]:
    """Rebuild review and bind authorization to Navigator's final solved plan.

    This fails closed if the reviewed state changed, the reviewed candidate set
    changed, the selected candidate disappears, or the final Navigator plan SHA
    differs from the explicitly authorized SHA. The return value remains a
    nonexecuting request to Navigator.
    """
    refs = tuple(
        candidate_ref_from_navigator(index, candidate, route=route, strategy=strategy)
        for index, candidate in enumerate(navigator_candidates, start=1)
    )
    review = build_review(intent, refs, reviewed_navigator_state_id)
    return build_navigator_execution_request(
        review,
        authorization,
        current_navigator_state_id=current_navigator_state_id,
        current_finalized_plan_sha256=current_finalized_plan_sha256,
    )
