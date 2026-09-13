import unittest

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.e1_hud_interaction import MaraIntentSession


class E1HUDInteractionTests(unittest.TestCase):
    def make_session(self):
        return MaraIntentSession(lambda text: FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA"))

    def test_intent_capture_is_in_memory_and_zero_authority(self):
        calls = []
        def interpret(text: str) -> FlightIntent:
            calls.append(text)
            return FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")
        session = MaraIntentSession(interpret)
        payload = session.capture("Take us to Neptune, balanced profile.")
        self.assertEqual(calls, ["Take us to Neptune, balanced profile."])
        self.assertEqual(payload["contract"], "LOOM_E1_FLIGHT_INTENT_V1")
        self.assertEqual(payload["calculation_authority"], "ZERO")
        self.assertEqual(payload["state_authority"], "ZERO")
        self.assertEqual(payload["execution_authority"], "ZERO")
        self.assertIsNone(session.current_review())

    def test_review_bundle_is_in_memory_and_must_remain_review_only(self):
        session = self.make_session(); session.capture("Neptune")
        bundle = {"review": {"contract":"LOOM_E1_FLIGHT_REVIEW_V1","navigator_state_id":"S1","planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","review_sha256":"a"*64,"candidates":[{"plan_number":1,"metric":"HARD","torch":"CRUISE"}]},"candidate_display":[],"planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","campaign_mutation":"NONE"}
        stored=session.store_review(bundle)
        self.assertEqual(stored["planner_authority"],"NAVIGATOR")
        self.assertIsNone(session.current_finalization())

    def test_finalization_then_authorization_is_explicit_and_nonexecuting(self):
        session=self.make_session(); session.capture("Neptune")
        review={"review":{"navigator_state_id":"S1","planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","review_sha256":"a"*64,"candidates":[{"plan_number":1,"metric":"HARD","torch":"CRUISE"}]},"planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","campaign_mutation":"NONE"}
        session.store_review(review)
        finalization={"navigator_state_id":"S1","review_sha256":"a"*64,"selected_plan_number":1,"finalized_plan_sha256":"b"*64,"planner_authority":"NAVIGATOR","execution_authority":"NONE_FINALIZED_NOT_AUTHORIZED","campaign_mutation":"NONE"}
        session.store_finalization(finalization)
        self.assertIsNone(session.current_authorization())
        auth=session.authorize("HUMAN_PIXEL")
        self.assertTrue(auth["explicit"])
        self.assertEqual(auth["authorized_by"],"HUMAN_PIXEL")
        self.assertEqual(auth["execution_authority"],"REQUEST_ONLY_NAVIGATOR_MUST_REVALIDATE")

    def test_authorization_without_finalization_fails_closed(self):
        session=self.make_session(); session.capture("Neptune")
        with self.assertRaises(ValueError): session.authorize()

    def test_new_intent_invalidates_review_finalization_and_authorization(self):
        session=self.make_session(); session.capture("Neptune")
        review={"review":{"navigator_state_id":"S1","planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","review_sha256":"a"*64,"candidates":[{"plan_number":1,"metric":"HARD","torch":"CRUISE"}]},"planner_authority":"NAVIGATOR","execution_authority":"NONE_REVIEW_ONLY","campaign_mutation":"NONE"}
        session.store_review(review)
        finalization={"navigator_state_id":"S1","review_sha256":"a"*64,"selected_plan_number":1,"finalized_plan_sha256":"b"*64,"planner_authority":"NAVIGATOR","execution_authority":"NONE_FINALIZED_NOT_AUTHORIZED","campaign_mutation":"NONE"}
        session.store_finalization(finalization); session.authorize()
        session.capture("Neptune again")
        self.assertIsNone(session.current_review()); self.assertIsNone(session.current_finalization()); self.assertIsNone(session.current_authorization())

    def test_review_with_execution_authority_fails_closed(self):
        session=self.make_session(); session.capture("Neptune")
        with self.assertRaises(ValueError):
            session.store_review({"review":{"planner_authority":"NAVIGATOR","execution_authority":"NAVIGATOR_ONLY"},"planner_authority":"NAVIGATOR","execution_authority":"NAVIGATOR_ONLY","campaign_mutation":"NONE"})

    def test_empty_text_fails_closed_without_replacing_prior_intent(self):
        session=self.make_session(); first=session.capture("Neptune")
        with self.assertRaises(ValueError): session.capture("   ")
        self.assertEqual(session.current(),first)

    def test_interpreter_failure_does_not_create_session_state(self):
        session=MaraIntentSession(lambda text: (_ for _ in ()).throw(RuntimeError("provider failed")))
        with self.assertRaises(RuntimeError): session.capture("Neptune")
        self.assertIsNone(session.current())


if __name__ == "__main__": unittest.main()
