from __future__ import annotations

"""Bounded Experience One HUD interaction session.

The session stores only the last typed flight intent in memory. It has no campaign
write path, no Navigator planning authority, no authorization authority, and no
execution authority. The injected interpreter is expected to be the already-audited
Mara/OpenAI intent adapter in production use.
"""

from typing import Callable

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent


class MaraIntentSession:
    def __init__(self, interpreter: Callable[[str], FlightIntent]) -> None:
        self._interpreter = interpreter
        self._current: dict | None = None

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
        return dict(self._current)

    def current(self) -> dict | None:
        return None if self._current is None else dict(self._current)
