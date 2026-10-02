import json
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.e1_navigator_finalization_service import (
    NavigatorFinalizationService,
    build_finalization_bundle,
)


class E1NavigatorFinalizationServiceTests(unittest.TestCase):
    def setUp(self):
        self.intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")
        self.review_bundle = {
            "review": {
                "contract": "LOOM_E1_FLIGHT_REVIEW_V1",
                "intent": self.intent.payload(),
                "navigator_state_id": "S1",
                "planner_authority": "NAVIGATOR",
                "execution_authority": "NONE_REVIEW_ONLY",
                "final_plan_sha_status": "NOT_EARNED_UNTIL_NAVIGATOR_FINAL_SOLVE",
                "review_sha256": "r" * 64,
                "candidates": [
                    {"plan_number": 1, "metric": "HARD", "torch": "CRUISE"},
                    {"plan_number": 2, "metric": "HARD", "torch": "ECON"},
                ],
            },
            "candidate_display": [],
            "planner_authority": "NAVIGATOR",
            "execution_authority": "NONE_REVIEW_ONLY",
            "campaign_mutation": "NONE",
        }

    def test_bundle_binds_selected_candidate_and_final_plan_sha(self):
        plan = {"flight_id": "F000001", "route": "CERES>NEPTUNE_SYSTEM", "metric": "HARD", "torch": "CRUISE"}
        bundle = build_finalization_bundle(self.review_bundle, 1, plan, "a" * 64)
        self.assertEqual(bundle["selected_plan_number"], 1)
        self.assertEqual(bundle["finalized_plan_sha256"], "a" * 64)
        self.assertEqual(bundle["navigator_state_id"], "S1")
        self.assertEqual(bundle["execution_authority"], "NONE_FINALIZED_NOT_AUTHORIZED")
        self.assertEqual(bundle["campaign_mutation"], "NONE")

    def test_selected_candidate_must_exist(self):
        with self.assertRaises(ValueError):
            build_finalization_bundle(self.review_bundle, 7, {}, "a" * 64)

    def test_service_preserves_source_campaign(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "LOOM_STATE_V1.json").write_text(json.dumps({
                "state_id": "S1", "location_token": "CERES", "epoch_utc": "2226-08-22T01:32:00Z",
                "ship": {"name": "WAYFARER", "remass_t": 250, "wet_mass_t": 1158.5},
            }), encoding="utf-8")
            before = (root / "LOOM_STATE_V1.json").read_bytes()
            source = lambda r, i, rb, n: ({"flight_id": "F000001", "metric": "HARD", "torch": "CRUISE"}, "b" * 64)
            bundle = NavigatorFinalizationService(source).finalize(root, self.intent, self.review_bundle, 1)
            after = (root / "LOOM_STATE_V1.json").read_bytes()
            self.assertEqual(before, after)
            self.assertTrue(bundle["source_campaign_unchanged_pass"])
            self.assertEqual(bundle["finalized_plan_sha256"], "b" * 64)


if __name__ == "__main__":
    unittest.main()
