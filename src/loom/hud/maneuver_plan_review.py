from __future__ import annotations

"""Nonexecuting server-side validation for staged maneuver plans.

The browser may stage a review draft, but only deterministic server code may
interpret it against current live qualification state. This module validates
that a review-required local-orbital-frame burn is structurally valid and that
its direction is resolvable now. It never advances or mutates spacecraft state.
"""

from typing import Any, Mapping

from loom.hud.flight_command_contract import CommandKind, ManeuverPlan, PlanExecutionPolicy
from loom.hud.flight_command_executor import (
    MAX_BURN_S,
    ORBITAL_BURN_DIRECTIONS,
    resolve_orbital_burn_target,
)

CONTRACT = "LOOM_MANEUVER_PLAN_REVIEW_RECEIPT_V1"


def validate_maneuver_plan_review(session: Any, raw_plan: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one staged plan against current state without executing it."""

    if str(raw_plan.get("contract") or "") != "LOOM_MANEUVER_PLAN_V1":
        raise ValueError("review requires LOOM_MANEUVER_PLAN_V1")

    plan = ManeuverPlan.from_mapping(raw_plan)
    if plan.execution_policy is not PlanExecutionPolicy.REVIEW_REQUIRED:
        raise ValueError("review endpoint accepts REVIEW_REQUIRED plans only")
    if len(plan.commands) != 1:
        raise ValueError("qualification review currently supports exactly one command")

    command = plan.commands[0]
    if command.kind is not CommandKind.TORCH_BURN:
        raise ValueError("qualification review currently supports TORCH_BURN only")
    if command.target_direction_inertial is not None:
        raise ValueError("browser review must not supply target_direction_inertial")
    if command.duration_s is None or not (0.0 < float(command.duration_s) <= MAX_BURN_S):
        raise ValueError(f"qualification burn duration must be in (0,{MAX_BURN_S:g}] seconds")

    context = raw_plan.get("review_context") or {}
    direction = str(context.get("direction_reference") or "").upper().strip()
    if direction not in ORBITAL_BURN_DIRECTIONS:
        raise ValueError(
            "direction must be one of " + ", ".join(sorted(ORBITAL_BURN_DIRECTIONS))
        )

    cards = getattr(session, "TORCH_CARDS", None)
    if cards is None:
        from loom.hud.realtime_flight_qualification import TORCH_CARDS
        cards = TORCH_CARDS
    torch_mode = str(command.torch_mode or "").upper().strip()
    if torch_mode not in cards:
        raise ValueError(f"unknown torch mode: {torch_mode}")
    if str(getattr(session, "status", "")) != "RUNNING":
        raise ValueError("qualification session must be RUNNING")
    if float(getattr(session, "remass_t", 0.0)) <= 0.0:
        raise ValueError("normal remass exhausted")

    # Resolve only to prove that the current frame is non-degenerate. Do not
    # return the vector: execution must re-resolve against then-current state.
    with session.lock:
        resolve_orbital_burn_target(session, direction)
        validated_epoch = session.sim_epoch.isoformat()
        remass_t = float(session.remass_t)

    return {
        "contract": CONTRACT,
        "status": "VALIDATED_REVIEW_ONLY",
        "authority": "NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY",
        "plan": plan.payload(),
        "review_context": {
            "direction_reference": direction,
            "direction_basis": "CURRENT_LIVE_EARTH_CENTERED_ORBITAL_FRAME_AT_EXECUTION",
        },
        "direction_status": "RESOLVABLE_FROM_CURRENT_LIVE_STATE",
        "target_vector_exposed": False,
        "validated_against_epoch_utc": validated_epoch,
        "validated_remass_t": remass_t,
        "mutates_live_qualification_state": False,
        "campaign_mutation": False,
        "navigation_grade": False,
        "execution_available_from_this_receipt": False,
    }
