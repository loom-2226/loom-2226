from __future__ import annotations

import ast
import unittest
from pathlib import Path

from research.relational_foundations.src.corrected_sign_scaling import (
    CorrectedSignScalingConfig,
    classify_corrected_sign_scaling,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "corrected_sign_scaling.py"
PROTOCOL = ROOT / "CORRECTED_SIGN_SCALING_PROTOCOL_v0.1.md"


class CorrectedSignScalingTests(unittest.TestCase):
    def test_module_parses(self):
        ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))

    def test_default_matrix_is_bounded_and_matched(self):
        cfg = CorrectedSignScalingConfig()
        self.assertEqual(cfg.sizes, (40, 80))
        self.assertEqual(cfg.seeds, (2226, 2227, 2228))
        self.assertEqual(cfg.steps_per_node, 2)
        self.assertEqual(cfg.strength, 1.0)
        self.assertEqual(cfg.curvature_sample_edges, 20)

    def test_classifier_distinguishes_historical_null_and_gate(self):
        rows = []
        for n in (40, 80):
            for seed in (1, 2, 3):
                rows.extend([
                    {"N": n, "convention": "null", "seed": seed,
                     "path_over_logN": 0.80, "spectral_gap": 0.20,
                     "diameter": 5, "triangle_count": 5},
                    {"N": n, "convention": "historical_plus", "seed": seed,
                     "path_over_logN": 0.70, "spectral_gap": 0.25,
                     "diameter": 4, "triangle_count": 4},
                    {"N": n, "convention": "experimental_minus", "seed": seed,
                     "path_over_logN": 0.90, "spectral_gap": 0.15,
                     "diameter": 6, "triangle_count": 6},
                ])
        out = classify_corrected_sign_scaling(rows, threshold=1.3)
        self.assertTrue(out["sign_direction_persists_all_sizes"])
        self.assertTrue(out["corrected_beats_null_directionally_all_sizes"])
        self.assertFalse(out["corrected_crosses_gate_all_sizes_all_seeds"])
        self.assertEqual(out["category"], "NO CORRECTED-SIGN GATE CROSSING")

    def test_classifier_requires_all_sizes_for_gate_candidate(self):
        rows = []
        for n in (40, 80):
            corr_ratio = 1.4 if n == 40 else 1.2
            for seed in (1, 2, 3):
                rows.extend([
                    {"N": n, "convention": "null", "seed": seed,
                     "path_over_logN": 0.8, "spectral_gap": 0.2,
                     "diameter": 5, "triangle_count": 5},
                    {"N": n, "convention": "historical_plus", "seed": seed,
                     "path_over_logN": 0.7, "spectral_gap": 0.25,
                     "diameter": 4, "triangle_count": 4},
                    {"N": n, "convention": "experimental_minus", "seed": seed,
                     "path_over_logN": corr_ratio, "spectral_gap": 0.15,
                     "diameter": 6, "triangle_count": 6},
                ])
        out = classify_corrected_sign_scaling(rows, threshold=1.3)
        self.assertFalse(out["corrected_crosses_gate_all_sizes_all_seeds"])

    def test_protocol_hard_stop_and_scope_are_explicit(self):
        text = PROTOCOL.read_text(encoding="utf-8").lower()
        self.assertIn("not an rqo-1 pass", text)
        self.assertIn("no triangle term", text)
        self.assertIn("failure to beat the null", text)


if __name__ == "__main__":
    unittest.main()
