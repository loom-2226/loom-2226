import unittest
from pathlib import Path

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.e1_navigator_execution_service import NavigatorExecutionService


class NavigatorExecutionServiceTests(unittest.TestCase):
    def setUp(self):
        self.intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")
        self.review = {"review": {"review_sha256": "a" * 64, "navigator_state_id": "S1"}}
        self.finalization = {
            "review_sha256": "a" * 64,
            "navigator_state_id": "S1",
            "selected_plan_number": 1,
            "finalized_plan_sha256": "b" * 64,
        }
        self.authorization = {
            "contract": "LOOM_E1_FLIGHT_AUTHORIZATION_V1",
            "review_sha256": "a" * 64,
            "selected_plan_number": 1,
            "finalized_plan_sha256": "b" * 64,
            "authorized_by": "HUMAN_PIXEL",
            "explicit": True,
            "execution_authority": "REQUEST_ONLY_NAVIGATOR_MUST_REVALIDATE",
        }

    def test_service_returns_navigator_execution_result(self):
        def source(root, intent, review, finalization, authorization):
            return {"state_id": "S2", "location_token": "NEPTUNE_SYSTEM", "epoch_utc": "2226-08-22T09:45:17Z", "flight_id": "F000001", "execution_request": {"contract": "LOOM_E1_NAVIGATOR_EXECUTION_REQUEST_V1"}}
        result = NavigatorExecutionService(source=source).execute(Path("/tmp/x"), self.intent, self.review, self.finalization, self.authorization)
        self.assertEqual("NAVIGATOR", result["execution_authority"])
        self.assertEqual("NEPTUNE_SYSTEM", result["location_token"])
        self.assertTrue(result["campaign_mutated_by_navigator"])

    def test_stale_authorization_fails_before_source(self):
        called = False
        def source(*args):
            nonlocal called; called = True; return {}
        bad = dict(self.authorization); bad["finalized_plan_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "final plan"):
            NavigatorExecutionService(source=source).execute(Path("/tmp/x"), self.intent, self.review, self.finalization, bad)
        self.assertFalse(called)

    def test_non_explicit_authorization_fails_closed(self):
        bad = dict(self.authorization); bad["explicit"] = False
        with self.assertRaisesRegex(ValueError, "explicit"):
            NavigatorExecutionService(source=lambda *a: {},).execute(Path("/tmp/x"), self.intent, self.review, self.finalization, bad)


if __name__ == "__main__":
    unittest.main()
