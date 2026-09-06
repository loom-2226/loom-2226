from __future__ import annotations

import unittest

from research.relational_foundations.src.r3_null_scaling import R3Config, classify_null_scaling


class R3NullScalingTests(unittest.TestCase):
    def test_default_config_is_null_only(self):
        cfg = R3Config()
        self.assertEqual(cfg.sizes, (40, 80, 160))
        self.assertEqual(cfg.seeds, (2226, 2227, 2228))
        self.assertEqual(cfg.avg_degree, 4)
        self.assertEqual(cfg.steps_per_node, 5)
        self.assertEqual(cfg.expander_log_ratio, 1.3)

    def test_classifier_reproduces_expander_failure_when_all_runs_below_gate(self):
        rows = [
            {"N": 40, "avg_shortest_path": 2.7, "log_N": 3.69, "spectral_gap": 0.16},
            {"N": 40, "avg_shortest_path": 2.8, "log_N": 3.69, "spectral_gap": 0.17},
            {"N": 80, "avg_shortest_path": 3.2, "log_N": 4.38, "spectral_gap": 0.15},
            {"N": 80, "avg_shortest_path": 3.3, "log_N": 4.38, "spectral_gap": 0.16},
        ]
        verdict = classify_null_scaling(rows, threshold=1.3)
        self.assertTrue(verdict["all_sizes_expander_like_by_historical_gate"])
        self.assertIn("AUIF NULL FAILURE REPRODUCED", verdict["interpretation"])
        self.assertIn("not an RQO-1 verdict", verdict["scientific_scope"])

    def test_classifier_flags_gate_crossing(self):
        rows = [
            {"N": 40, "avg_shortest_path": 5.0, "log_N": 3.69, "spectral_gap": 0.03},
        ]
        verdict = classify_null_scaling(rows, threshold=1.3)
        self.assertFalse(verdict["all_sizes_expander_like_by_historical_gate"])
        self.assertIn("NOT CLEANLY REPRODUCED", verdict["interpretation"])


if __name__ == "__main__":
    unittest.main()
