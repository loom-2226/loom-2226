import unittest

from loom.hud.flight_command_contract import (
    CommandKind,
    CommandOrigin,
    FlightCommand,
    ManeuverPlan,
    PlanExecutionPolicy,
)


class FlightCommandContractTests(unittest.TestCase):
    def test_manual_and_llm_commands_share_identical_execution_authority(self):
        manual = FlightCommand(CommandKind.TORCH_BURN, CommandOrigin.MANUAL, duration_s=30, torch_mode="CRUISE")
        llm = FlightCommand(CommandKind.TORCH_BURN, CommandOrigin.LLM, duration_s=30, torch_mode="CRUISE", requested_by="MARA")
        self.assertEqual(manual.payload()["execution_authority"], llm.payload()["execution_authority"])
        self.assertEqual(manual.payload()["execution_authority"], "NONE_UNTIL_DETERMINISTIC_EXECUTOR_ACCEPTS")

    def test_plan_is_nonexecuting_until_explicit_boundary(self):
        plan = ManeuverPlan(
            commands=(FlightCommand(CommandKind.COAST, CommandOrigin.SYSTEM, duration_s=60),),
            objective="hold current trajectory",
            planner="TEST",
        )
        payload = plan.payload()
        self.assertEqual(payload["execution_authority"], "NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY")
        self.assertEqual(payload["execution_policy"], "REVIEW_REQUIRED")

    def test_plan_round_trip_preserves_order_provenance_and_policy(self):
        plan = ManeuverPlan(
            commands=(
                FlightCommand(CommandKind.COAST, CommandOrigin.LLM, duration_s=120, requested_by="MARA"),
                FlightCommand(
                    CommandKind.TORCH_BURN,
                    CommandOrigin.LLM,
                    duration_s=5,
                    torch_mode="CRUISE",
                    target_direction_inertial=(0.0, 1.0, 0.0),
                    requested_by="MARA",
                ),
            ),
            objective="raise apoapsis after coast",
            planner="NAVIGATOR",
            execution_policy=PlanExecutionPolicy.EXPLICIT_EXECUTION,
        )
        restored = ManeuverPlan.from_mapping(plan.payload())
        self.assertEqual(restored, plan)
        self.assertEqual([c.kind for c in restored.commands], [CommandKind.COAST, CommandKind.TORCH_BURN])
        self.assertTrue(all(c.origin is CommandOrigin.LLM for c in restored.commands))

    def test_invalid_burn_fails_closed(self):
        with self.assertRaises(ValueError):
            FlightCommand(CommandKind.TORCH_BURN, CommandOrigin.LLM, duration_s=0, torch_mode="CRUISE")
        with self.assertRaises(ValueError):
            FlightCommand(CommandKind.TORCH_BURN, CommandOrigin.MANUAL, duration_s=10)

    def test_rotate_requires_nonzero_vector(self):
        with self.assertRaises(ValueError):
            FlightCommand(CommandKind.ROTATE_TO_VECTOR, CommandOrigin.NPC, target_direction_inertial=(0, 0, 0))


if __name__ == "__main__":
    unittest.main()
