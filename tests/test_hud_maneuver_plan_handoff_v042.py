import threading
import unittest
from datetime import datetime, timezone

from loom.hud.flight_command_contract import PlanExecutionPolicy
from loom.hud.maneuver_plan_handoff import build_explicit_execution_plan_from_review


class FakeSession:
    TORCH_CARDS = {"CRUISE": {}}

    def __init__(self):
        self.lock = threading.RLock()
        self.status = "RUNNING"
        self.sim_epoch = datetime(2026, 9, 12, tzinfo=timezone.utc)
        self.ship_position = (6778.137, 0.0, 0.0)
        self.ship_velocity = (0.0, 7.6686, 0.0)
        self.nose_direction = (0.0, 1.0, 0.0)
        self.remass_t = 250.0
        self.wet_mass_t = 1158.5
        self.torch_mode = "CRUISE"
        self.torch_active = False

    def _advance_locked(self):
        raise AssertionError("review-to-execution handoff must not advance state")


def review_payload(direction="RADIAL_OUT", target=None, policy="REVIEW_REQUIRED"):
    return {
        "contract": "LOOM_MANEUVER_PLAN_V1",
        "objective": f"Review {direction} qualification burn",
        "planner": "HUD_MANUAL_REVIEW",
        "execution_policy": policy,
        "commands": [
            {
                "contract": "LOOM_FLIGHT_COMMAND_V1",
                "kind": "TORCH_BURN",
                "origin": "MANUAL",
                "duration_s": 5.0,
                "torch_mode": "CRUISE",
                "target_direction_inertial": target,
                "requested_by": "HUD_MANUAL_REVIEW",
            }
        ],
        "review_context": {
            "direction_reference": direction,
            "direction_basis": "CURRENT_LIVE_EARTH_CENTERED_ORBITAL_FRAME_AT_EXECUTION",
        },
    }


class ManeuverPlanHandoffTests(unittest.TestCase):
    def test_server_resolves_vector_and_upgrades_policy_only_after_review(self):
        session = FakeSession()
        before = (session.sim_epoch, session.ship_position, session.ship_velocity, session.remass_t)
        plan = build_explicit_execution_plan_from_review(session, review_payload())
        after = (session.sim_epoch, session.ship_position, session.ship_velocity, session.remass_t)

        self.assertEqual(before, after)
        self.assertIs(plan.execution_policy, PlanExecutionPolicy.EXPLICIT_EXECUTION)
        self.assertEqual(plan.commands[0].target_direction_inertial, (1.0, 0.0, 0.0))
        self.assertEqual(plan.commands[0].origin.value, "MANUAL")
        self.assertEqual(plan.commands[0].requested_by, "HUD_MANUAL_REVIEW")

    def test_browser_vector_still_fails_closed(self):
        with self.assertRaises(ValueError):
            build_explicit_execution_plan_from_review(
                FakeSession(), review_payload(target=[1.0, 0.0, 0.0])
            )

    def test_browser_cannot_submit_explicit_execution_policy(self):
        with self.assertRaises(ValueError):
            build_explicit_execution_plan_from_review(
                FakeSession(), review_payload(policy="EXPLICIT_EXECUTION")
            )


if __name__ == "__main__":
    unittest.main()
