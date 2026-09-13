from __future__ import annotations

"""Bounded Experience One HUD interaction session.

The session stores only the last typed flight intent and the last Navigator review
bundle in memory. It has no campaign write path, no planning authority, no
authorization authority, and no execution authority. The injected interpreter is
expected to be the already-audited Mara/OpenAI intent adapter in production use.
"""

from copy import deepcopy
from typing import Any, Callable, Mapping

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent


class MaraIntentSession:
    def __init__(self, interpreter: Callable[[str], FlightIntent]) -> None:
        self._interpreter = interpreter
        self._current: dict | None = None
        self._review: dict | None = None

    def capture(self, user_text: str) -> dict:
        text = str(user_text or "").strip()
        if not text:
            raise ValueError("flight intent text is required")
        intent = self._interpreter(text)
        payload = intent.payload()
        if payload.get("calculation_authority") != "ZERO":
            raise ValueError("intent crossed calculation-authority boundary")
        if payload.get("state_authority") != "ZERO":
            raise ValueError("intent crossed state-authority boundary")
        if payload.get("execution_authority") != "ZERO":
            raise ValueError("intent crossed execution-authority boundary")
        self._current = dict(payload)
        self._review = None
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
        if planner != "NAVIGATOR":
            raise ValueError("review planner authority must be NAVIGATOR")
        if execution != "NONE_REVIEW_ONLY":
            raise ValueError("review must not carry execution authority")
        if mutation != "NONE":
            raise ValueError("review must not mutate campaign state")
        if not isinstance(review, Mapping):
            raise ValueError("review bundle missing typed Navigator review")
        if str(review.get("planner_authority") or "") != "NAVIGATOR":
            raise ValueError("typed review planner authority must be NAVIGATOR")
        if str(review.get("execution_authority") or "") != "NONE_REVIEW_ONLY":
            raise ValueError("typed review crossed execution-authority boundary")
        self._review = deepcopy(dict(bundle))
        return deepcopy(self._review)

    def current_review(self) -> dict | None:
        return None if self._review is None else deepcopy(self._review)
