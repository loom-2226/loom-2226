import unittest

from engineering.experience_one.e1_flight_interaction_contract import (
    FlightIntent,
    IntentOrigin,
    NavigatorCandidateRef,
    build_review,
)
from engineering.experience_one.e1_hud_presenter import (
    build_hud_payload,
    render_hud_html,
)


class E1HUDPresenterTests(unittest.TestCase):
    def setUp(self):
        self.state = {
            "state_id": "S000002-test",
            "epoch_utc": "2226-08-22T09:45:17.864616Z",
            "location_token": "NEPTUNE_SYSTEM",
            "ship": {
                "name": "WAYFARER",
                "remass_t": 236.603241561,
                "wet_mass_t": 1145.103241561,
            },
            "kinematic_boundary": {"status": "BODY_RENDEZVOUS"},
        }
        intent = FlightIntent(
            destination="NEPTUNE_SYSTEM",
            priority="BALANCED",
            origin=IntentOrigin.MARA,
            requested_by="MARA",
        )
        self.intent_payload = intent.payload()
        self.review = build_review(
            intent,
            (
                NavigatorCandidateRef(1, "HARD", "CRUISE"),
                NavigatorCandidateRef(2, "SOFT", "ECONOMY"),
            ),
            "S000001-origin",
        )

    def test_payload_is_read_only_and_grounded_in_campaign_state(self):
        payload = build_hud_payload(self.state)
        self.assertEqual(payload["schema"], "LOOM_E1_HUD_PRESENTATION_V1")
        self.assertEqual(payload["campaign"]["location_token"], "NEPTUNE_SYSTEM")
        self.assertEqual(payload["campaign"]["epoch_utc"], "2226-08-22T09:45:17.864616Z")
        self.assertEqual(payload["campaign"]["state_id"], "S000002-test")
        self.assertEqual(payload["campaign"]["state_authority"], "NAVIGATOR_CAMPAIGN_READ_ONLY")
        self.assertEqual(payload["browser_authority"], "PRESENTATION_ONLY")
        self.assertEqual(payload["calculation_authority"], "ZERO")
        self.assertEqual(payload["execution_authority"], "ZERO")

    def test_neptune_orientation_is_minimal_and_does_not_invent_local_geometry(self):
        payload = build_hud_payload(self.state)
        orientation = payload["orientation"]
        self.assertTrue(orientation["grounded"])
        self.assertEqual(orientation["location_token"], "NEPTUNE_SYSTEM")
        self.assertEqual(orientation["local_geometry_status"], "NOT_CLAIMED")
        self.assertIn("NEPTUNE_SYSTEM", orientation["summary"])
        self.assertIn(self.state["epoch_utc"], orientation["summary"])

    def test_typed_mara_intent_is_presented_without_authority_promotion(self):
        payload = build_hud_payload(self.state, intent=self.intent_payload)
        shown = payload["flight_intent"]
        self.assertEqual(shown["destination"], "NEPTUNE_SYSTEM")
        self.assertEqual(shown["priority"], "BALANCED")
        self.assertEqual(shown["origin"], "MARA")
        self.assertEqual(shown["calculation_authority"], "ZERO")
        self.assertEqual(shown["state_authority"], "ZERO")
        self.assertEqual(shown["execution_authority"], "ZERO")
        self.assertEqual(payload["execution_authority"], "ZERO")

    def test_review_is_presented_without_execution_authority(self):
        payload = build_hud_payload(self.state, review=self.review)
        review = payload["flight_review"]
        self.assertEqual(review["planner_authority"], "NAVIGATOR")
        self.assertEqual(review["execution_authority"], "NONE_REVIEW_ONLY")
        self.assertEqual(len(review["candidates"]), 2)
        self.assertEqual(payload["execution_authority"], "ZERO")

    def test_html_exposes_orientation_intent_form_and_explicit_authority_labels(self):
        html = render_hud_html(build_hud_payload(
            self.state,
            intent=self.intent_payload,
            review=self.review,
        ))
        self.assertIn("WAYFARER", html)
        self.assertIn("NEPTUNE_SYSTEM", html)
        self.assertIn("Navigator", html)
        self.assertIn("Mara", html)
        self.assertIn("flight-intent-form", html)
        self.assertIn("/intent.json", html)
        self.assertIn("PRESENTATION ONLY", html)
        self.assertIn("REVIEW ONLY", html)


if __name__ == "__main__":
    unittest.main()
