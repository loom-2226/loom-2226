import unittest

from engineering.experience_one.e1_flight_interaction_contract import FlightIntent, IntentOrigin
from engineering.experience_one.e1_hud_interaction import MaraIntentSession


class E1HUDInteractionTests(unittest.TestCase):
    def test_intent_capture_is_in_memory_and_zero_authority(self):
        calls = []

        def interpret(text: str) -> FlightIntent:
            calls.append(text)
            return FlightIntent(
                destination="NEPTUNE_SYSTEM",
                priority="BALANCED",
                origin=IntentOrigin.MARA,
                requested_by="MARA",
            )

        session = MaraIntentSession(interpret)
        payload = session.capture("Take us to Neptune, balanced profile.")

        self.assertEqual(calls, ["Take us to Neptune, balanced profile."])
        self.assertEqual(payload["contract"], "LOOM_E1_FLIGHT_INTENT_V1")
        self.assertEqual(payload["destination"], "NEPTUNE_SYSTEM")
        self.assertEqual(payload["priority"], "BALANCED")
        self.assertEqual(payload["origin"], "MARA")
        self.assertEqual(payload["calculation_authority"], "ZERO")
        self.assertEqual(payload["state_authority"], "ZERO")
        self.assertEqual(payload["execution_authority"], "ZERO")
        self.assertEqual(session.current(), payload)

    def test_empty_text_fails_closed_without_replacing_prior_intent(self):
        def interpret(text: str) -> FlightIntent:
            return FlightIntent("NEPTUNE_SYSTEM", "BALANCED", IntentOrigin.MARA, "MARA")

        session = MaraIntentSession(interpret)
        first = session.capture("Neptune")
        with self.assertRaises(ValueError):
            session.capture("   ")
        self.assertEqual(session.current(), first)

    def test_interpreter_failure_does_not_create_session_state(self):
        def interpret(text: str) -> FlightIntent:
            raise RuntimeError("provider failed")

        session = MaraIntentSession(interpret)
        with self.assertRaises(RuntimeError):
            session.capture("Neptune")
        self.assertIsNone(session.current())


if __name__ == "__main__":
    unittest.main()
