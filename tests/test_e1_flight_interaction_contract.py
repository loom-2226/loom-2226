import unittest

from engineering.experience_one.e1_flight_interaction_contract import (
    FlightAuthorization,
    FlightIntent,
    IntentOrigin,
    NavigatorCandidateRef,
    build_navigator_execution_request,
    build_review,
)


class E1FlightInteractionContractTests(unittest.TestCase):
    def _candidate(self, number: int = 1, digest: str = "a" * 64) -> NavigatorCandidateRef:
        return NavigatorCandidateRef(
            plan_number=number,
            plan_sha256=digest,
            route="CERES>NEPTUNE_SYSTEM",
            strategy="DIRECT_NAVIGATION",
            metric="HARD",
            torch="CRUISE",
        )

    def test_human_and_mara_have_identical_zero_authority(self):
        human = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.HUMAN, "KT")
        mara = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")
        for key in ("calculation_authority", "state_authority", "execution_authority"):
            self.assertEqual(human.payload()[key], mara.payload()[key])
            self.assertEqual(human.payload()[key], "ZERO")

    def test_review_is_nonexecuting_and_binds_navigator_state(self):
        intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")
        review = build_review(intent, [self._candidate()], "S000001-test")
        payload = review.payload()
        self.assertEqual(payload["planner_authority"], "NAVIGATOR")
        self.assertEqual(payload["execution_authority"], "NONE_REVIEW_ONLY")
        self.assertEqual(payload["navigator_state_id"], "S000001-test")
        self.assertEqual(len(payload["review_sha256"]), 64)

    def test_explicit_authorization_yields_request_not_execution(self):
        intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.HUMAN, "KT")
        candidate = self._candidate()
        review = build_review(intent, [candidate], "S000001-test")
        auth = FlightAuthorization(
            review_sha256=review.payload()["review_sha256"],
            selected_plan_number=1,
            selected_plan_sha256=candidate.plan_sha256,
            authorized_by="KT",
        )
        request = build_navigator_execution_request(review, auth)
        self.assertEqual(request["execution_authority"], "NAVIGATOR_ONLY")
        self.assertTrue(request["requires_navigator_revalidation"])
        self.assertEqual(request["caller_calculation_authority"], "ZERO")
        self.assertEqual(request["caller_state_authority"], "ZERO")

    def test_authorization_fails_closed_on_review_hash_mismatch(self):
        intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.HUMAN, "KT")
        candidate = self._candidate()
        review = build_review(intent, [candidate], "S000001-test")
        auth = FlightAuthorization("b" * 64, 1, candidate.plan_sha256, "KT")
        with self.assertRaises(ValueError):
            build_navigator_execution_request(review, auth)

    def test_authorization_fails_closed_on_plan_hash_mismatch(self):
        intent = FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.HUMAN, "KT")
        candidate = self._candidate()
        review = build_review(intent, [candidate], "S000001-test")
        auth = FlightAuthorization(review.payload()["review_sha256"], 1, "c" * 64, "KT")
        with self.assertRaises(ValueError):
            build_navigator_execution_request(review, auth)

    def test_implicit_authorization_is_rejected(self):
        with self.assertRaises(ValueError):
            FlightAuthorization("a" * 64, 1, "b" * 64, "KT", explicit=False)


if __name__ == "__main__":
    unittest.main()
