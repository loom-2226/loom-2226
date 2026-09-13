import unittest

from engineering.experience_one.e1_flight_interaction_contract import (
    FlightAuthorization,
    FlightIntent,
    IntentOrigin,
    NavigatorCandidateRef,
    build_review,
)
from engineering.experience_one.e1_navigator_interaction_adapter import (
    authorized_request_for_current_navigator_state,
    review_from_navigator_output,
)


PLAN_A = {
    "plan_sha256": "a" * 64,
    "route": "CERES>NEPTUNE_SYSTEM",
    "strategy": "DIRECT_NAVIGATION",
    "metric": "HARD",
    "torch": "CRUISE",
}
PLAN_B = {
    "plan_sha256": "b" * 64,
    "route": "CERES>NEPTUNE_SYSTEM",
    "strategy": "DIRECT_NAVIGATION",
    "metric": "HARD",
    "torch": "ECON",
}


class E1NavigatorInteractionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.intent = FlightIntent(
            destination="NEPTUNE_SYSTEM",
            priority="BALANCED",
            origin=IntentOrigin.MARA,
            requested_by="MARA",
        )
        self.state_id = "S000001-test"

    def _authorization(self):
        review = build_review(
            self.intent,
            (
                NavigatorCandidateRef(1, "a" * 64, "CERES>NEPTUNE_SYSTEM", "DIRECT_NAVIGATION", "HARD", "CRUISE"),
                NavigatorCandidateRef(2, "b" * 64, "CERES>NEPTUNE_SYSTEM", "DIRECT_NAVIGATION", "HARD", "ECON"),
            ),
            self.state_id,
        )
        review_sha = review.payload()["review_sha256"]
        return FlightAuthorization(review_sha, 1, "a" * 64, "KT", explicit=True)

    def test_review_packages_existing_navigator_output_without_execution_authority(self):
        payload = review_from_navigator_output(self.intent, self.state_id, [PLAN_A, PLAN_B])
        self.assertEqual(payload["planner_authority"], "NAVIGATOR")
        self.assertEqual(payload["execution_authority"], "NONE_REVIEW_ONLY")
        self.assertEqual(payload["candidates"][0]["plan_sha256"], "a" * 64)
        self.assertEqual(payload["candidates"][1]["plan_sha256"], "b" * 64)

    def test_authorization_rebinds_against_same_current_state_and_candidates(self):
        request = authorized_request_for_current_navigator_state(
            self.intent, self.state_id, [PLAN_A, PLAN_B], self._authorization()
        )
        self.assertEqual(request["execution_authority"], "NAVIGATOR_ONLY")
        self.assertTrue(request["requires_navigator_revalidation"])
        self.assertEqual(request["selected_plan_sha256"], "a" * 64)

    def test_state_change_after_review_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "review hash"):
            authorized_request_for_current_navigator_state(
                self.intent, "S000002-changed", [PLAN_A, PLAN_B], self._authorization()
            )

    def test_candidate_hash_change_after_review_fails_closed(self):
        changed = dict(PLAN_A)
        changed["plan_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "review hash"):
            authorized_request_for_current_navigator_state(
                self.intent, self.state_id, [changed, PLAN_B], self._authorization()
            )

    def test_missing_navigator_plan_sha_fails_closed(self):
        broken = dict(PLAN_A)
        broken.pop("plan_sha256")
        with self.assertRaisesRegex(ValueError, "plan_sha256"):
            review_from_navigator_output(self.intent, self.state_id, [broken])


if __name__ == "__main__":
    unittest.main()
