from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER_PATH = ROOT / "qualification" / "synthesis" / "verify_wayfarer_s0.py"

spec = importlib.util.spec_from_file_location("verify_wayfarer_s0", VERIFIER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load S0 verifier from {VERIFIER_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WayfarerS0SynthesisTests(unittest.TestCase):
    def test_s0_authority_extraction(self):
        result = module.verify()
        self.assertEqual(result["S0_AUTHORITY_EXTRACTION"], "PASS")
        self.assertEqual(result["reference_states"]["DOCKED"]["wet_mass_kg"], 1158500.0)
        self.assertEqual(result["reference_states"]["ABSENT"]["wet_mass_kg"], 1125500.0)
        self.assertFalse(result["flight_dynamics_authority"])
        self.assertFalse(result["canon_changed"])
        self.assertFalse(result["production_shipclasses_changed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
