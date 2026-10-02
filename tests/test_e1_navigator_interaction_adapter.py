import unittest

from engineering.experience_one.e1_flight_interaction_contract import (
    FlightAuthorization,
    FlightIntent,
    IntentOrigin,
    NavigatorCandidateRef,
    build_review,
)
from engineering.experience_one.e1_navigator_interaction_adapter import (
    authorized_request_for_finalized_navigator_plan,
    review_from_navigator_output,
)


PLAN_A = {
    "metric": "HARD",
    "torch": "CRUISE",
}
PLAN_B = {
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

    def _authorization(self, plan_sha="a" * 64):
        review = build_review(
            self.intent,
            (
                NavigatorCandidateRef(1, "HARD", "CRUISE"),
                NavigatorCandidateRef(2, "HARD", "ECON"),
            ),
            self.state_id,
        )
        return FlightAuthorization(
            review.payload()["review_sha256"], 1, plan_sha, "KT", explicit=True
        )

    def test_review_packages_existing_navigator_output_without_execution_authority(self):
        payload = review_from_navigator_output(self.intent, self.state_id, [PLAN_A, PLAN_B])
        self.assertEqual(payload["planner_authority"], "NAVIGATOR")
        self.assertEqual(payload["execution_authority"], "NONE_REVIEW_ONLY")
        self.assertEqual(payload["candidates"][0], {"plan_number": 1, "metric": "HARD", "torch": "CRUISE"})
        self.assertNotIn("plan_sha256", payload["candidates"][0])

    def test_authorization_binds_final_navigator_sha_after_candidate_selection(self):
        plan_sha = "a" * 64
        request = authorized_request_for_finalized_navigator_plan(
            self.intent,
            self.state_id,
            [PLAN_A, PLAN_B],
            self._authorization(plan_sha),
            current_navigator_state_id=self.state_id,
            current_finalized_plan_sha256=plan_sha,
        )
        self.assertEqual(request["execution_authority"], "NAVIGATOR_ONLY")
        self.assertTrue(request["requires_navigator_revalidation"])
        self.assertEqual(request["finalized_plan_sha256"], plan_sha)

    def test_state_change_after_review_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "state changed"):
            authorized_request_for_finalized_navigator_plan(
                self.intent,
                self.state_id,
                [PLAN_A, PLAN_B],
                self._authorization(),
                current_navigator_state_id="S000002-changed",
                current_finalized_plan_sha256="a" * 64,
            )

    def test_candidate_set_change_after_review_fails_closed(self):
        changed = dict(PLAN_A)
        changed["metric"] = "FAST"
        with self.assertRaisesRegex(ValueError, "review hash"):
            authorized_request_for_finalized_navigator_plan(
                self.intent,
                self.state_id,
                [changed, PLAN_B],
                self._authorization(),
                current_navigator_state_id=self.state_id,
                current_finalized_plan_sha256="a" * 64,
            )

    def test_final_plan_hash_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "final plan hash"):
            authorized_request_for_finalized_navigator_plan(
                self.intent,
                self.state_id,
                [PLAN_A, PLAN_B],
                self._authorization("a" * 64),
                current_navigator_state_id=self.state_id,
                current_finalized_plan_sha256="b" * 64,
            )

    def test_missing_navigator_candidate_field_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "torch"):
            review_from_navigator_output(self.intent, self.state_id, [{"metric": "HARD"}])


if __name__ == "__main__":
    unittest.main()
