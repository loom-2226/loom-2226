from __future__ import annotations

import ast
import unittest
from pathlib import Path

from research.relational_foundations.src.curvature_convergence import (
    CurvatureConvergenceConfig,
    classify_curvature_convergence,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "curvature_convergence.py"
PROTOCOL = ROOT / "CURVATURE_CONVERGENCE_PROTOCOL_v0.1.md"


class CurvatureConvergenceTests(unittest.TestCase):
    def test_module_parses(self):
        ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))

    def test_frozen_default_matrix(self):
        cfg = CurvatureConvergenceConfig()
        self.assertEqual(cfg.N, 80)
        self.assertEqual(cfg.avg_degree, 4)
        self.assertEqual(cfg.seeds, (2226, 2227, 2228))
        self.assertEqual(cfg.checkpoints, (160, 400, 800))
        self.assertEqual(cfg.strength, 1.0)
        self.assertEqual(cfg.curvature_sample_edges, 20)
        self.assertEqual(cfg.temperature, 1.0)

    def test_classifier_requires_direction_at_every_checkpoint(self):
        rows = []
        for checkpoint in (160, 400, 800):
            for seed in (1, 2, 3):
                rows.append({
                    "checkpoint_steps": checkpoint,
                    "convention": "null",
                    "path_over_logN": 0.76,
                    "spectral_gap": 0.18,
                    "crosses_historical_path_gate": False,
                    "acceptance_fraction": 1.0,
                })
                rows.append({
                    "checkpoint_steps": checkpoint,
                    "convention": "experimental_minus",
                    "path_over_logN": 0.78,
                    "spectral_gap": 0.16,
                    "crosses_historical_path_gate": False,
                    "acceptance_fraction": 0.5,
                })
        out = classify_curvature_convergence(rows)
        self.assertTrue(out["directional_effect_persists_all_checkpoints"])
        self.assertEqual(out["category"], "DIRECTIONAL EFFECT PERSISTS THROUGH 10N")
        self.assertTrue(out["sampled_action_is_stochastic"])
        self.assertFalse(out["equilibrium_claim_authorized"])

        # Reverse one checkpoint only: the whole persistence claim must fail.
        for row in rows:
            if row["checkpoint_steps"] == 800 and row["convention"] == "experimental_minus":
                row["path_over_logN"] = 0.74
        out = classify_curvature_convergence(rows)
        self.assertFalse(out["directional_effect_persists_all_checkpoints"])
        self.assertEqual(out["category"], "DIRECTIONAL EFFECT NOT STABLE")

    def test_protocol_preserves_trajectory_and_forbids_equilibrium_claim(self):
        text = PROTOCOL.read_text(encoding="utf-8").lower()
        self.assertIn("must not be evaluated during the mcmc trajectory", text)
        self.assertIn("does not establish", text)
        self.assertIn("equilibrium", text)
        self.assertIn("sampled action is stochastic", text)
        self.assertIn("no triangle term", text)


if __name__ == "__main__":
    unittest.main()
