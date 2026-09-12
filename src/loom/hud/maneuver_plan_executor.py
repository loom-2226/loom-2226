from __future__ import annotations

"""Deterministic execution boundary for typed maneuver plans.

Plans have no authority by themselves. Only plans explicitly marked for execution
may cross this boundary, and every command still executes through the shared
flight-command executor against the same live qualification state.
"""

from typing import Any

from loom.hud.flight_command_contract import (
    CommandKind,
    ManeuverPlan,
    PlanExecutionPolicy,
)
from loom.hud.flight_command_executor import execute_flight_command

CONTRACT = "LOOM_MANEUVER_PLAN_EXECUTION_RECEIPT_V1"
SUPPORTED_COMMAND_KINDS = {CommandKind.COAST, CommandKind.TORCH_BURN}


def _validate_plan_for_execution(plan: ManeuverPlan) -> None:
    if plan.execution_policy is not PlanExecutionPolicy.EXPLICIT_EXECUTION:
        raise ValueError("maneuver plan requires EXPLICIT_EXECUTION policy")
    unsupported = [c.kind.value for c in plan.commands if c.kind not in SUPPORTED_COMMAND_KINDS]
    if unsupported:
        raise ValueError("unsupported maneuver-plan command kinds: " + ", ".join(unsupported))
    for command in plan.commands:
        if command.kind is CommandKind.TORCH_BURN and command.target_direction_inertial is None:
            raise ValueError("planned TORCH_BURN requires target_direction_inertial")


def execute_maneuver_plan(session: Any, plan: ManeuverPlan) -> dict[str, Any]:
    """Execute an explicitly-authorized typed plan in command order.

    Validation occurs before the first mutation so unsupported commands fail
    closed without partially applying a plan. Command origin remains provenance
    only; all mutations pass through execute_flight_command().
    """

    _validate_plan_for_execution(plan)

    start_epoch = session.sim_epoch
    start_remass = float(session.remass_t)
    receipts = []
    for index, command in enumerate(plan.commands):
        receipt = execute_flight_command(session, command)
        receipt = dict(receipt)
        receipt["plan_command_index"] = index
        receipts.append(receipt)

    return {
        "contract": CONTRACT,
        "status": "EXECUTED_QUALIFICATION_ONLY",
        "authority": "DETERMINISTIC_MANEUVER_PLAN_EXECUTOR",
        "plan": plan.payload(),
        "command_receipts": receipts,
        "command_count": len(receipts),
        "start_epoch_utc": start_epoch.isoformat(),
        "end_epoch_utc": session.sim_epoch.isoformat(),
        "start_remass_t": start_remass,
        "end_remass_t": float(session.remass_t),
        "remass_used_t": start_remass - float(session.remass_t),
        "campaign_mutation": False,
        "navigation_grade": False,
        "execution_semantics": "ORDERED_COMMANDS_SHARED_DETERMINISTIC_EXECUTOR",
    }
