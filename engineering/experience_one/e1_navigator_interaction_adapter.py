from __future__ import annotations

"""Bounded adapter between E1 typed interaction and Navigator-owned flight output.

This module deliberately performs no flight calculation, ephemeris work, state
mutation, persistence, or execution. It only packages already-produced Navigator
candidate plans for review and verifies that an explicit authorization still
matches the current Navigator state and selected plan identity.
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


def candidate_ref_from_navigator(plan_number: int, raw: Mapping[str, Any]) -> NavigatorCandidateRef:
    """Create a nonauthoritative reference to an existing Navigator candidate.

    No candidate values are derived here. All identity fields must already be
    present in Navigator output, including the authoritative plan SHA.
    """
    return NavigatorCandidateRef(
        plan_number=int(plan_number),
        plan_sha256=_required_text(raw, "plan_sha256"),
        route=_required_text(raw, "route"),
        strategy=_required_text(raw, "strategy"),
        metric=_required_text(raw, "metric"),
        torch=_required_text(raw, "torch"),
    )


def review_from_navigator_output(
    intent: FlightIntent,
    navigator_state_id: str,
    navigator_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Package Navigator-produced candidates into an E1 review payload."""
    refs = tuple(
        candidate_ref_from_navigator(index, candidate)
        for index, candidate in enumerate(navigator_candidates, start=1)
    )
    return build_review(intent, refs, navigator_state_id).payload()


def authorized_request_for_current_navigator_state(
    intent: FlightIntent,
    navigator_state_id: str,
    navigator_candidates: Sequence[Mapping[str, Any]],
    authorization: FlightAuthorization,
) -> dict[str, Any]:
    """Rebuild review from current Navigator output, then bind authorization.

    This fail-closes if state, candidate ordering, or candidate plan hashes have
    changed since review. Returned data is still only a request; Navigator alone
    may decide whether it remains executable and mutate campaign state.
    """
    refs = tuple(
        candidate_ref_from_navigator(index, candidate)
        for index, candidate in enumerate(navigator_candidates, start=1)
    )
    review = build_review(intent, refs, navigator_state_id)
    return build_navigator_execution_request(review, authorization)
