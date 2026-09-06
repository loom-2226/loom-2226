from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "sign_sensitivity.py"
AUDIT = ROOT / "RQO1_SOURCE_AUDIT_v0.1.md"
PROTOCOL = ROOT / "SIGN_SENSITIVITY_PROTOCOL_v0.1.md"


class SignSensitivityContractTests(unittest.TestCase):
    def test_module_parses(self):
        ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))

    def test_historical_and_experimental_signs_are_explicit(self):
        text = SRC.read_text(encoding="utf-8")
        self.assertIn('"historical_plus"', text)
        self.assertIn('"experimental_minus"', text)
        self.assertIn('"historical_action": "+alpha * curvature_sum"', text)
        self.assertIn('"experimental_action": "-alpha * curvature_sum"', text)

    def test_experiment_is_small_and_matched(self):
        text = SRC.read_text(encoding="utf-8")
        self.assertIn("N: int = 40", text)
        self.assertIn("n_steps: int = 30", text)
        self.assertIn("seeds: tuple[int, ...] = (2226, 2227)", text)
        self.assertIn("strengths: tuple[float, ...] = (0.5, 1.0)", text)
        self.assertIn("curvature_sample_edges: int = 20", text)

    def test_no_target_geometry_terms(self):
        text = SRC.read_text(encoding="utf-8").lower()
        for forbidden in ("target_lattice", "target_manifold", "euclidean_distance", "coordinates ="):
            self.assertNotIn(forbidden, text)

    def test_audit_and_protocol_mark_new_sign_as_experimental(self):
        audit = AUDIT.read_text(encoding="utf-8")
        protocol = PROTOCOL.read_text(encoding="utf-8").lower()
        # Normalize Markdown emphasis so prose formatting does not break the semantic contract.
        protocol_plain = re.sub(r"[*_`]", "", protocol)
        self.assertIn("new experimental action convention", audit)
        self.assertIn("not historical reproduction", protocol_plain)
        self.assertIn("new hypothesis", protocol_plain)


if __name__ == "__main__":
    unittest.main()
