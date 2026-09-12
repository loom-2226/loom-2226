import threading
import unittest
from datetime import datetime, timezone

from loom.hud.maneuver_plan_review import validate_maneuver_plan_review


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
        raise AssertionError("review validation must not advance or mutate live state")


def review_payload(direction="PROGRADE", policy="REVIEW_REQUIRED", target=None):
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


class ManeuverPlanReviewTests(unittest.TestCase):
    def test_review_validates_against_current_state_without_mutation(self):
        session = FakeSession()
        before = (session.sim_epoch, session.ship_position, session.ship_velocity, session.remass_t, session.nose_direction)
        receipt = validate_maneuver_plan_review(session, review_payload("PROGRADE"))
        after = (session.sim_epoch, session.ship_position, session.ship_velocity, session.remass_t, session.nose_direction)
        self.assertEqual(before, after)
        self.assertEqual(receipt["contract"], "LOOM_MANEUVER_PLAN_REVIEW_RECEIPT_V1")
        self.assertEqual(receipt["status"], "VALIDATED_REVIEW_ONLY")
        self.assertEqual(receipt["authority"], "NONE_UNTIL_EXPLICIT_EXECUTION_BOUNDARY")
        self.assertFalse(receipt["mutates_live_qualification_state"])
        self.assertEqual(receipt["direction_status"], "RESOLVABLE_FROM_CURRENT_LIVE_STATE")
        self.assertFalse(receipt["target_vector_exposed"])

    def test_review_rejects_execution_policy(self):
        with self.assertRaises(ValueError):
            validate_maneuver_plan_review(FakeSession(), review_payload(policy="EXPLICIT_EXECUTION"))

    def test_review_rejects_browser_supplied_inertial_vector(self):
        with self.assertRaises(ValueError):
            validate_maneuver_plan_review(FakeSession(), review_payload(target=[1.0, 0.0, 0.0]))

    def test_review_rejects_unknown_direction(self):
        with self.assertRaises(ValueError):
            validate_maneuver_plan_review(FakeSession(), review_payload("SIDEWAYS"))


if __name__ == "__main__":
    unittest.main()
