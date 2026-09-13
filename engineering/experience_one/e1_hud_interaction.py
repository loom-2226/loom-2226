from __future__ import annotations

"""Bounded Experience One HUD interaction session.

The session stores only ephemeral interaction artifacts: typed Mara intent,
Navigator review, Navigator finalization, and explicit human authorization.
It owns no calculation, campaign state, or execution authority.
"""

from copy import deepcopy
from typing import Any, Callable, Mapping

from engineering.experience_one.e1_flight_interaction_contract import FlightAuthorization, FlightIntent


class MaraIntentSession:
    def __init__(self, interpreter: Callable[[str], FlightIntent]) -> None:
        self._interpreter = interpreter
        self._current: dict | None = None
        self._review: dict | None = None
        self._finalization: dict | None = None
        self._authorization: dict | None = None

    def capture(self, user_text: str) -> dict:
        text = str(user_text or "").strip()
        if not text:
            raise ValueError("flight intent text is required")
        intent = self._interpreter(text)
        payload = intent.payload()
        for field in ("calculation_authority", "state_authority", "execution_authority"):
            if payload.get(field) != "ZERO":
                raise ValueError(f"intent crossed {field.replace('_authority','')}-authority boundary")
        self._current = dict(payload)
        self._review = None
        self._finalization = None
        self._authorization = None
        return dict(self._current)

    def current(self) -> dict | None:
        return None if self._current is None else dict(self._current)

    def store_review(self, bundle: Mapping[str, Any]) -> dict:
        if self._current is None:
            raise ValueError("typed flight intent is required before Navigator review")
        planner = str(bundle.get("planner_authority") or "")
        execution = str(bundle.get("execution_authority") or "")
        mutation = str(bundle.get("campaign_mutation") or "")
        review = bundle.get("review")
        if planner != "NAVIGATOR" or execution != "NONE_REVIEW_ONLY" or mutation != "NONE":
            raise ValueError("Navigator review crossed authority boundary")
        if not isinstance(review, Mapping):
            raise ValueError("review bundle missing typed Navigator review")
        if str(review.get("planner_authority") or "") != "NAVIGATOR":
            raise ValueError("typed review planner authority must be NAVIGATOR")
        if str(review.get("execution_authority") or "") != "NONE_REVIEW_ONLY":
            raise ValueError("typed review crossed execution-authority boundary")
        self._review = deepcopy(dict(bundle))
        self._finalization = None
        self._authorization = None
        return deepcopy(self._review)

    def current_review(self) -> dict | None:
        return None if self._review is None else deepcopy(self._review)

    def store_finalization(self, bundle: Mapping[str, Any]) -> dict:
        if self._review is None:
            raise ValueError("Navigator review is required before finalization")
        review = self._review.get("review") or {}
        if str(bundle.get("review_sha256") or "") != str(review.get("review_sha256") or ""):
            raise ValueError("finalization review hash does not match current review")
        if str(bundle.get("navigator_state_id") or "") != str(review.get("navigator_state_id") or ""):
            raise ValueError("finalization state does not match current review")
        if str(bundle.get("planner_authority") or "") != "NAVIGATOR":
            raise ValueError("finalization planner authority must be NAVIGATOR")
        if str(bundle.get("execution_authority") or "") != "NONE_FINALIZED_NOT_AUTHORIZED":
            raise ValueError("finalization must not carry execution authority")
        if str(bundle.get("campaign_mutation") or "") != "NONE":
            raise ValueError("finalization must not mutate campaign state")
        self._finalization = deepcopy(dict(bundle))
        self._authorization = None
        return deepcopy(self._finalization)

    def current_finalization(self) -> dict | None:
        return None if self._finalization is None else deepcopy(self._finalization)

    def authorize(self, authorized_by: str = "HUMAN_PIXEL") -> dict:
        if self._finalization is None:
            raise ValueError("finalized Navigator plan is required before authorization")
        auth = FlightAuthorization(
            review_sha256=str(self._finalization["review_sha256"]),
            selected_plan_number=int(self._finalization["selected_plan_number"]),
            finalized_plan_sha256=str(self._finalization["finalized_plan_sha256"]),
            authorized_by=authorized_by,
            explicit=True,
        ).payload()
        self._authorization = auth
        return dict(auth)

    def current_authorization(self) -> dict | None:
        return None if self._authorization is None else dict(self._authorization)
