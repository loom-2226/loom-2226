from __future__ import annotations

"""Bounded Experience One HUD interaction session.

The session stores only ephemeral interaction artifacts. It owns no calculation,
campaign state, or execution authority; Navigator alone may execute/mutate.
"""

from copy import deepcopy
from typing import Any, Callable, Mapping
from engineering.experience_one.e1_flight_interaction_contract import FlightAuthorization, FlightIntent


class MaraIntentSession:
    def __init__(self, interpreter: Callable[[str], FlightIntent]) -> None:
        self._interpreter=interpreter; self._current=None; self._review=None; self._finalization=None; self._authorization=None; self._execution=None

    def capture(self, user_text: str) -> dict:
        text=str(user_text or "").strip()
        if not text: raise ValueError("flight intent text is required")
        payload=self._interpreter(text).payload()
        for field in ("calculation_authority","state_authority","execution_authority"):
            if payload.get(field)!="ZERO": raise ValueError(f"intent crossed {field.replace('_authority','')}-authority boundary")
        self._current=dict(payload); self._review=self._finalization=self._authorization=self._execution=None
        return dict(self._current)

    def current(self): return None if self._current is None else dict(self._current)

    def store_review(self, bundle: Mapping[str,Any]) -> dict:
        if self._current is None: raise ValueError("typed flight intent is required before Navigator review")
        review=bundle.get("review")
        if str(bundle.get("planner_authority"))!="NAVIGATOR" or str(bundle.get("execution_authority"))!="NONE_REVIEW_ONLY" or str(bundle.get("campaign_mutation"))!="NONE": raise ValueError("Navigator review crossed authority boundary")
        if not isinstance(review,Mapping) or str(review.get("planner_authority"))!="NAVIGATOR" or str(review.get("execution_authority"))!="NONE_REVIEW_ONLY": raise ValueError("typed review crossed authority boundary")
        self._review=deepcopy(dict(bundle)); self._finalization=self._authorization=self._execution=None; return deepcopy(self._review)

    def current_review(self): return None if self._review is None else deepcopy(self._review)

    def store_finalization(self,bundle:Mapping[str,Any])->dict:
        if self._review is None: raise ValueError("Navigator review is required before finalization")
        review=self._review.get("review") or {}
        if str(bundle.get("review_sha256"))!=str(review.get("review_sha256")): raise ValueError("finalization review hash does not match current review")
        if str(bundle.get("navigator_state_id"))!=str(review.get("navigator_state_id")): raise ValueError("finalization state does not match current review")
        if str(bundle.get("planner_authority"))!="NAVIGATOR" or str(bundle.get("execution_authority"))!="NONE_FINALIZED_NOT_AUTHORIZED" or str(bundle.get("campaign_mutation"))!="NONE": raise ValueError("finalization crossed authority boundary")
        self._finalization=deepcopy(dict(bundle)); self._authorization=self._execution=None; return deepcopy(self._finalization)

    def current_finalization(self): return None if self._finalization is None else deepcopy(self._finalization)

    def authorize(self,authorized_by:str="HUMAN_PIXEL")->dict:
        if self._finalization is None: raise ValueError("finalized Navigator plan is required before authorization")
        self._authorization=FlightAuthorization(review_sha256=str(self._finalization["review_sha256"]),selected_plan_number=int(self._finalization["selected_plan_number"]),finalized_plan_sha256=str(self._finalization["finalized_plan_sha256"]),authorized_by=authorized_by,explicit=True).payload()
        self._execution=None; return dict(self._authorization)

    def current_authorization(self): return None if self._authorization is None else dict(self._authorization)

    def store_execution(self,result:Mapping[str,Any])->dict:
        if self._authorization is None: raise ValueError("explicit authorization is required before execution result")
        if str(result.get("execution_authority"))!="NAVIGATOR" or result.get("campaign_mutated_by_navigator") is not True: raise ValueError("execution result lacks Navigator authority")
        self._execution=deepcopy(dict(result)); return deepcopy(self._execution)

    def current_execution(self): return None if self._execution is None else deepcopy(self._execution)
