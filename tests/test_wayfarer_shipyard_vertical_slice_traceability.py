from __future__ import annotations

import sys
import unittest
from pathlib import Path

SYNTH = Path(__file__).resolve().parents[1] / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_shipyard_vertical_slice import run  # noqa: E402


class WayfarerShipyardVerticalSliceTraceabilityTests(unittest.TestCase):
    def test_evidence_and_critique_are_hash_linked(self):
        row = run(2226)
        self.assertEqual(row["critic_authority"], "CRITIQUE_ONLY")
        self.assertEqual(row["child_evaluation_hash"], row["critic_evaluation_hash"])
        self.assertEqual(row["critic_institution_context_hash"], "WAYFARER_VERTICAL_SLICE_FIXTURE_CONTEXT")
        self.assertEqual(len(row["evidence_package_hash"]), 64)
        self.assertFalse(row["flight_dynamics_authority"])
        self.assertFalse(row["canon_changed"])
        self.assertFalse(row["production_shipclasses_changed"])


if __name__ == "__main__":
    unittest.main()
