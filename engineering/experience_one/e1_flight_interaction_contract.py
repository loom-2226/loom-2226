from __future__ import annotations

"""Provider-neutral Experience One flight interaction contract.

The seam mirrors Navigator's actual authority flow:
1. caller supplies intent only;
2. Navigator produces deterministic comparison candidates;
3. user selects a candidate for final deterministic solve;
4. Navigator produces the final plan and authoritative plan SHA;
5. explicit authorization binds the review, selected candidate number, and final
   Navigator plan SHA;
6. Navigator must revalidate all of that before campaign mutation.

No caller receives calculation, state, planning, or execution authority.
"""

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping, Sequence

INTENT_CONTRACT = "LOOM_E1_FLIGHT_INTENT_V1"
REVIEW_CONTRACT = "LOOM_E1_FLIGHT_REVIEW_V1"
AUTH_CONTRACT = "LOOM_E1_FLIGHT_AUTHORIZATION_V1"
EXECUTION_REQUEST_CONTRACT = "LOOM_E1_NAVIGATOR_EXECUTION_REQUEST_V1"


class IntentOrigin(str, Enum):
    HUMAN = "HUMAN"
    MARA = "MARA"
    NPC = "NPC"
    SYSTEM = "SYSTEM"


@dataclass(frozen=True)
class FlightIntent:
    destination: str
    priority: str
    origin: IntentOrigin
    requested_by: str | None = None

    def __post_init__(self) -> None:
        if not self.destination.strip():
            raise ValueError("destination is required")
        if not self.priority.strip():
            raise ValueError("priority is required")

    def payload(self) -> dict[str, Any]:
        return {
            "contract": INTENT_CONTRACT,
            "destination": self.destination.strip().upper(),
            "priority": self.priority.strip().upper(),
            "origin": self.origin.value,
            "requested_by": self.requested_by,
            "calculation_authority": "ZERO",
            "state_authority": "ZERO",
            "execution_authority": "ZERO",
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "FlightIntent":
        if str(raw.get("contract") or INTENT_CONTRACT) != INTENT_CONTRACT:
            raise ValueError("unsupported flight intent contract")
        return cls(
            destination=str(raw["destination"]),
            priority=str(raw["priority"]),
            origin=IntentOrigin(str(raw["origin"]).upper()),
            requested_by=None if raw.get("requested_by") is None else str(raw["requested_by"]),
        )


@dataclass(frozen=True)
class NavigatorCandidateRef:
    """Reference to one Navigator-produced comparison candidate.

    Only fields Navigator actually owns at comparison time are bound here.
    Mission route/strategy remain in Navigator mission context. A final plan SHA
    does not exist until the selected candidate receives Navigator's final solve.
    """

    plan_number: int
    metric: str
    torch: str

    def __post_init__(self) -> None:
        if self.plan_number <= 0:
            raise ValueError("plan_number must be positive")
        if not self.metric.strip() or not self.torch.strip():
            raise ValueError("candidate metric and torch are required")

    def payload(self) -> dict[str, Any]:
        return {
            "plan_number": self.plan_number,
            "metric": self.metric,
            "torch": self.torch,
        }


@dataclass(frozen=True)
class FlightReview:
    intent: FlightIntent
    candidates: tuple[NavigatorCandidateRef, ...]
    navigator_state_id: str

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("review requires at least one Navigator candidate")
        if len({c.plan_number for c in self.candidates}) != len(self.candidates):
            raise ValueError("candidate plan numbers must be unique")
        if not self.navigator_state_id.strip():
            raise ValueError("navigator_state_id is required")

    def payload(self) -> dict[str, Any]:
        body = {
            "contract": REVIEW_CONTRACT,
            "intent": self.intent.payload(),
            "candidates": [c.payload() for c in self.candidates],
            "navigator_state_id": self.navigator_state_id,
            "planner_authority": "NAVIGATOR",
            "execution_authority": "NONE_REVIEW_ONLY",
            "final_plan_sha_status": "NOT_EARNED_UNTIL_NAVIGATOR_FINAL_SOLVE",
        }
        body["review_sha256"] = canonical_sha256(body)
        return body


@dataclass(frozen=True)
class FlightAuthorization:
    review_sha256: str
    selected_plan_number: int
    finalized_plan_sha256: str
    authorized_by: str
    explicit: bool = True

    def __post_init__(self) -> None:
        if not self.explicit:
            raise ValueError("flight authorization must be explicit")
        if self.selected_plan_number <= 0:
            raise ValueError("selected_plan_number must be positive")
        digest = self.finalized_plan_sha256.lower().strip()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("finalized_plan_sha256 must be a 64-character hex digest")
        if not self.authorized_by.strip():
            raise ValueError("authorized_by is required")

    def payload(self) -> dict[str, Any]:
        return {
            "contract": AUTH_CONTRACT,
            "review_sha256": self.review_sha256.lower(),
            "selected_plan_number": self.selected_plan_number,
            "finalized_plan_sha256": self.finalized_plan_sha256.lower(),
            "authorized_by": self.authorized_by,
            "explicit": True,
            "execution_authority": "REQUEST_ONLY_NAVIGATOR_MUST_REVALIDATE",
        }


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_review(
    intent: FlightIntent,
    navigator_candidates: Sequence[NavigatorCandidateRef],
    navigator_state_id: str,
) -> FlightReview:
    """Package deterministic Navigator comparison output for review only."""
    return FlightReview(intent, tuple(navigator_candidates), navigator_state_id)


def build_navigator_execution_request(
    review: FlightReview,
    authorization: FlightAuthorization,
    current_navigator_state_id: str,
    current_finalized_plan_sha256: str,
) -> dict[str, Any]:
    """Bind authorization to reviewed options and Navigator's final solved plan.

    The result is still only a request. Navigator must revalidate its current
    campaign state, final plan identity, and execution rules before mutation.
    """
    review_payload = review.payload()
    expected_review_sha = review_payload["review_sha256"]
    if authorization.review_sha256.lower() != expected_review_sha:
        raise ValueError("authorization review hash does not match reviewed payload")
    if current_navigator_state_id != review.navigator_state_id:
        raise ValueError("Navigator state changed after review")

    by_number = {c.plan_number: c for c in review.candidates}
    selected = by_number.get(authorization.selected_plan_number)
    if selected is None:
        raise ValueError("authorized plan number was not present in review")

    current_plan_sha = current_finalized_plan_sha256.lower().strip()
    if authorization.finalized_plan_sha256.lower() != current_plan_sha:
        raise ValueError("authorized final plan hash does not match current Navigator final plan")

    return {
        "contract": EXECUTION_REQUEST_CONTRACT,
        "navigator_state_id": review.navigator_state_id,
        "selected_plan_number": selected.plan_number,
        "finalized_plan_sha256": current_plan_sha,
        "review_sha256": expected_review_sha,
        "authorized_by": authorization.authorized_by,
        "authorization_explicit": True,
        "planner_authority": "NAVIGATOR",
        "execution_authority": "NAVIGATOR_ONLY",
        "caller_calculation_authority": "ZERO",
        "caller_state_authority": "ZERO",
        "requires_navigator_revalidation": True,
    }
