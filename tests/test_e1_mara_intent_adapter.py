import json
import tempfile
import unittest
from pathlib import Path

from engineering.experience_one.e1_flight_interaction_contract import IntentOrigin
from engineering.experience_one.e1_mara_intent_adapter import (
    OpenAIMaraIntentAdapter,
    parse_mara_intent_json,
)


class E1MaraIntentAdapterTests(unittest.TestCase):
    def test_parse_returns_typed_mara_intent_with_zero_authority(self):
        intent = parse_mara_intent_json('{"destination":"NEPTUNE_SYSTEM","priority":"BALANCED"}')
        self.assertEqual(intent.origin, IntentOrigin.MARA)
        self.assertEqual(intent.destination, "NEPTUNE_SYSTEM")
        self.assertEqual(intent.priority, "BALANCED")
        payload = intent.payload()
        self.assertEqual(payload["calculation_authority"], "ZERO")
        self.assertEqual(payload["state_authority"], "ZERO")
        self.assertEqual(payload["execution_authority"], "ZERO")

    def test_parse_normalizes_bounded_destination_and_priority_aliases(self):
        for raw in (
            '{"destination":"Neptune","priority":"balanced"}',
            '{"destination":"NEPTUNE_SYSTEM","priority":"balanced profile"}',
            '{"destination":"NEPTUNE","priority":"balanced_profile"}',
        ):
            intent = parse_mara_intent_json(raw)
            self.assertEqual(intent.destination, "NEPTUNE_SYSTEM")
            self.assertEqual(intent.priority, "BALANCED")

    def test_parse_rejects_unknown_destination_alias(self):
        with self.assertRaises(ValueError):
            parse_mara_intent_json('{"destination":"Somewhere mysterious","priority":"BALANCED"}')

    def test_parse_rejects_unknown_priority_alias(self):
        with self.assertRaises(ValueError):
            parse_mara_intent_json('{"destination":"NEPTUNE_SYSTEM","priority":"YOLO"}')

    def test_parse_rejects_extra_authority_or_plan_fields(self):
        for raw in (
            '{"destination":"NEPTUNE_SYSTEM","priority":"BALANCED","plan":1}',
            '{"destination":"NEPTUNE_SYSTEM","priority":"BALANCED","execute":true}',
            '{"destination":"NEPTUNE_SYSTEM","priority":"BALANCED","state_id":"S1"}',
        ):
            with self.assertRaises(ValueError):
                parse_mara_intent_json(raw)

    def test_provider_call_is_audited_and_returns_typed_intent(self):
        calls = []
        def provider(payload):
            calls.append(payload)
            return {
                "response": {"output_text": '{"destination":"NEPTUNE","priority":"balanced profile"}'},
                "http_status": 200,
                "latency_s": 0.1,
            }

        with tempfile.TemporaryDirectory() as td:
            audit_path = Path(td) / "audit.jsonl"
            adapter = OpenAIMaraIntentAdapter(
                api_key="test-key-not-real",
                audit_path=audit_path,
                model="test-model",
                provider_call=provider,
            )
            intent = adapter.interpret("Take us to Neptune, balanced profile.")
            self.assertEqual(intent.destination, "NEPTUNE_SYSTEM")
            self.assertEqual(intent.priority, "BALANCED")
            self.assertEqual(len(calls), 1)
            rows = [json.loads(x) for x in audit_path.read_text(encoding="utf-8").splitlines() if x.strip()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["stage"], "e1.mara.intent")
            self.assertNotIn("test-key-not-real", audit_path.read_text(encoding="utf-8"))

    def test_provider_output_with_plan_authority_fails_closed_but_is_still_audited(self):
        def provider(payload):
            return {
                "response": {"output_text": '{"destination":"NEPTUNE_SYSTEM","priority":"BALANCED","plan":1}'},
                "http_status": 200,
                "latency_s": 0.1,
            }
        with tempfile.TemporaryDirectory() as td:
            audit_path = Path(td) / "audit.jsonl"
            adapter = OpenAIMaraIntentAdapter(
                api_key="test-key-not-real",
                audit_path=audit_path,
                model="test-model",
                provider_call=provider,
            )
            with self.assertRaises(ValueError):
                adapter.interpret("Pick a plan and fly us to Neptune")
            self.assertTrue(audit_path.exists())


if __name__ == "__main__":
    unittest.main()
