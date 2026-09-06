import json
import struct
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from loom.navigation import FlightPlan, RouteCandidate
from loom.navigation.trajectory_payload import find_sequence_b_payload, promote_sequence_b_payload


def packed_header() -> bytes:
    meta = {
        "payload_version": "3.0-SEQUENCE-B",
        "_flight_binary_codec": "FLIGHT_DELTA2_VARINT53_V1",
        "route_plans": {"R": {"solutions": {"HARD|CRUISE": {"timeline": {}}}}},
        "_flight_binary_blocks": {},
        "timeline_contract": {"field_index": {}},
    }
    raw = json.dumps(meta, separators=(",", ":")).encode("utf-8")
    return struct.pack("<I", len(raw)) + raw


class SequenceBPayloadPromotionTest(unittest.TestCase):
    def candidate(self):
        return RouteCandidate(route_id="R1", origin="CERES", destination="MARS")

    def test_finds_payload_without_relying_on_legacy_key(self):
        raw = packed_header()
        nested = {"artifacts": [{"opaque": memoryview(raw)}]}
        self.assertEqual(find_sequence_b_payload(nested), raw)

    def test_ignores_arbitrary_bytes(self):
        self.assertIsNone(find_sequence_b_payload({"payloads": {"x": b"not-a-flight-payload"}}))

    def test_promotes_exact_binary_into_canonical_adapter_location(self):
        raw = packed_header()
        plan = FlightPlan(
            flight_id="F1",
            candidate=self.candidate(),
            payload={"payloads": {"other": b"x"}, "artifacts": {"sequence_b": bytearray(raw)}},
        )
        promoted = promote_sequence_b_payload(plan)
        self.assertEqual(promoted.payload["payloads"]["flightSolutionsPayload"], raw)
        self.assertEqual(promoted.payload["payloads"]["other"], b"x")
        self.assertNotIn("flightSolutionsPayload", plan.payload["payloads"])

    def test_existing_valid_canonical_payload_is_preserved(self):
        raw = packed_header()
        plan = FlightPlan(
            flight_id="F1",
            candidate=self.candidate(),
            payload={"payloads": {"flightSolutionsPayload": raw}},
        )
        self.assertIs(promote_sequence_b_payload(plan), plan)


if __name__ == "__main__":
    unittest.main()
