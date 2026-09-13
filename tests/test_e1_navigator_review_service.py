import json
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.e1_navigator_review_service import (
    NavigatorReviewService,
    build_review_bundle,
)


class E1NavigatorReviewServiceTests(unittest.TestCase):
    def setUp(self):
        self.intent = FlightIntent(
            destination="NEPTUNE_SYSTEM",
            priority="BALANCED",
            origin=IntentOrigin.MARA,
            requested_by="MARA",
        )
        self.candidates = [
            {
                "metric": "HARD",
                "torch": "CRUISE",
                "total_s": 8.222 * 3600,
                "remass_used_t": 13.396758,
                "arrival_remass_t": 236.603242,
                "thermal": "SUSTAINABLE",
            },
            {
                "metric": "HARD",
                "torch": "ECON",
                "total_s": 9.675 * 3600,
                "remass_used_t": 8.948,
                "arrival_remass_t": 241.052,
                "thermal": "SUSTAINABLE",
            },
        ]

    def _root(self, td):
        root = Path(td)
        (root / "LOOM_STATE_V1.json").write_text(json.dumps({
            "state_id": "S000001-test",
            "epoch_utc": "2226-08-22T01:32:00Z",
            "location_token": "CERES",
            "ship": {"name": "WAYFARER", "remass_t": 250.0, "wet_mass_t": 1158.5},
        }), encoding="utf-8")
        (root / "LOOM_CAMPAIGN_HISTORY.jsonl.gz").write_bytes(b"history-fixture")
        return root

    def test_bundle_preserves_navigator_values_and_typed_review_authority(self):
        bundle = build_review_bundle(self.intent, "S000001-test", self.candidates)
        review = bundle["review"]
        self.assertEqual(review["planner_authority"], "NAVIGATOR")
        self.assertEqual(review["execution_authority"], "NONE_REVIEW_ONLY")
        self.assertEqual(len(review["candidates"]), 2)
        display = bundle["candidate_display"]
        self.assertEqual(display[0]["plan_number"], 1)
        self.assertEqual(display[0]["total_s"], self.candidates[0]["total_s"])
        self.assertEqual(display[0]["remass_used_t"], 13.396758)
        self.assertEqual(display[0]["arrival_remass_t"], 236.603242)
        self.assertEqual(display[0]["thermal"], "SUSTAINABLE")
        self.assertEqual(bundle["calculation_authority"], "NAVIGATOR_ONLY")
        self.assertEqual(bundle["campaign_mutation"], "NONE")

    def test_service_keeps_source_campaign_bit_identical(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            service = NavigatorReviewService(
                candidate_source=lambda _root, _intent, _state: list(self.candidates)
            )
            before = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            bundle = service.generate(root, self.intent)
            after = {p.name: p.read_bytes() for p in root.iterdir() if p.is_file()}
            self.assertEqual(before, after)
            self.assertTrue(bundle["source_campaign_unchanged_pass"])
            self.assertEqual(bundle["review"]["navigator_state_id"], "S000001-test")

    def test_service_fails_closed_if_candidate_source_mutates_campaign(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)

            def mutating_source(candidate_root, _intent, _state):
                state_path = candidate_root / "LOOM_STATE_V1.json"
                state_path.write_text("{}", encoding="utf-8")
                return list(self.candidates)

            service = NavigatorReviewService(candidate_source=mutating_source)
            with self.assertRaisesRegex(RuntimeError, "SOURCE CAMPAIGN MUTATED"):
                service.generate(root, self.intent)

    def test_destination_equal_current_location_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root(td)
            same = FlightIntent("CERES", "BALANCED", IntentOrigin.MARA, "MARA")
            service = NavigatorReviewService(
                candidate_source=lambda _root, _intent, _state: list(self.candidates)
            )
            with self.assertRaisesRegex(ValueError, "destination equals current location"):
                service.generate(root, same)


if __name__ == "__main__":
    unittest.main()
