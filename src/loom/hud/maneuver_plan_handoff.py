from __future__ import annotations

"""Server-side handoff from reviewed local-frame intent to explicit execution.

The browser is never allowed to supply an inertial burn vector. A reviewed
REVIEW_REQUIRED plan is revalidated against current live qualification state,
then deterministic server code resolves the selected local orbital-frame
reference and constructs the EXPLICIT_EXECUTION plan that may cross the shared
maneuver-plan executor.
"""

from typing import Any, Mapping

from loom.hud.flight_command_contract import (
    FlightCommand,
    ManeuverPlan,
    PlanExecutionPolicy,
)
from loom.hud.flight_command_executor import resolve_orbital_burn_target
from loom.hud.maneuver_plan_review import validate_maneuver_plan_review


def build_explicit_execution_plan_from_review(
    session: Any,
    raw_plan: Mapping[str, Any],
) -> ManeuverPlan:
    """Revalidate a reviewed plan and resolve its execution vector server-side.

    This function does not itself execute or mutate spacecraft state. It is the
    deterministic conversion seam immediately before execute_maneuver_plan().
    """

    receipt = validate_maneuver_plan_review(session, raw_plan)
    reviewed_plan = ManeuverPlan.from_mapping(raw_plan)
    reviewed_command = reviewed_plan.commands[0]
    direction = receipt["review_context"]["direction_reference"]

    with session.lock:
        target = resolve_orbital_burn_target(session, direction)

    command = FlightCommand(
        kind=reviewed_command.kind,
        origin=reviewed_command.origin,
        duration_s=reviewed_command.duration_s,
        torch_mode=reviewed_command.torch_mode,
        target_direction_inertial=target,
        requested_by=reviewed_command.requested_by,
    )
    return ManeuverPlan(
        commands=(command,),
        objective=reviewed_plan.objective,
        planner=reviewed_plan.planner,
        execution_policy=PlanExecutionPolicy.EXPLICIT_EXECUTION,
    )
