import threading
import unittest
from datetime import datetime, timezone

from loom.hud.flight_command_contract import (
    CommandKind,
    CommandOrigin,
    FlightCommand,
    ManeuverPlan,
    PlanExecutionPolicy,
)
from loom.hud.maneuver_plan_executor import execute_maneuver_plan


class _Session:
    def __init__(self):
        self.lock = threading.RLock()
        self.sim_epoch = datetime(2026, 9, 12, 0, 0, tzinfo=timezone.utc)
        self.ship_position = (6778.137, 0.0, 0.0)
        self.ship_velocity = (0.0, 7.668558, 0.0)
        self.nose_direction = (0.0, 1.0, 0.0)
        self.torch_active = False
        self.torch_mode = "CRUISE"
        self.remass_t = 250.0
        self.wet_mass_t = 1158.5
        self.status = "RUNNING"
        self.last_wall = 0.0
        self.steps = []

    def _advance_locked(self):
        pass

    def _step(self, dt):
        self.steps.append((dt, self.torch_active, self.nose_direction))
        if self.torch_active:
            accel = 0.00980665
            self.ship_velocity = tuple(
                self.ship_velocity[i] + self.nose_direction[i] * accel * dt
                for i in range(3)
            )
            used_t = min(self.remass_t, 0.001 * dt)
            self.remass_t -= used_t
            self.wet_mass_t -= used_t
        self.sim_epoch = datetime.fromtimestamp(self.sim_epoch.timestamp() + dt, tz=timezone.utc)


class ManeuverPlanExecutionV039Tests(unittest.TestCase):
    def test_review_required_plan_does_not_execute(self):
        s = _Session()
        plan = ManeuverPlan(
            commands=(
                FlightCommand(CommandKind.COAST, CommandOrigin.LLM, duration_s=10, requested_by="MARA"),
            ),
            objective="coast ten seconds",
            planner="NAVIGATOR",
            execution_policy=PlanExecutionPolicy.REVIEW_REQUIRED,
        )
        with self.assertRaises(ValueError):
            execute_maneuver_plan(s, plan)
        self.assertEqual(s.sim_epoch, datetime(2026, 9, 12, 0, 0, tzinfo=timezone.utc))

    def test_explicit_plan_executes_commands_in_order(self):
        s = _Session()
        plan = ManeuverPlan(
            commands=(
                FlightCommand(CommandKind.COAST, CommandOrigin.LLM, duration_s=10, requested_by="MARA"),
                FlightCommand(
                    CommandKind.TORCH_BURN,
                    CommandOrigin.LLM,
                    duration_s=2,
                    torch_mode="CRUISE",
                    target_direction_inertial=(0.0, 1.0, 0.0),
                    requested_by="MARA",
                ),
            ),
            objective="coast then burn",
            planner="NAVIGATOR",
            execution_policy=PlanExecutionPolicy.EXPLICIT_EXECUTION,
        )
        receipt = execute_maneuver_plan(s, plan)
        self.assertEqual(receipt["contract"], "LOOM_MANEUVER_PLAN_EXECUTION_RECEIPT_V1")
        self.assertEqual([r["command_kind"] for r in receipt["command_receipts"]], ["COAST", "TORCH_BURN"])
        self.assertGreater(s.sim_epoch.timestamp(), datetime(2026, 9, 12, 0, 0, tzinfo=timezone.utc).timestamp() + 11)
        self.assertLess(s.remass_t, 250.0)
        self.assertFalse(s.torch_active)

    def test_plan_executor_rejects_unsupported_command_kind_before_mutation(self):
        s = _Session()
        plan = ManeuverPlan(
            commands=(
                FlightCommand(CommandKind.HOLD_ATTITUDE, CommandOrigin.LLM, requested_by="MARA"),
            ),
            objective="unsupported hold",
            planner="NAVIGATOR",
            execution_policy=PlanExecutionPolicy.EXPLICIT_EXECUTION,
        )
        with self.assertRaises(ValueError):
            execute_maneuver_plan(s, plan)
        self.assertEqual(s.steps, [])


if __name__ == "__main__":
    unittest.main()
