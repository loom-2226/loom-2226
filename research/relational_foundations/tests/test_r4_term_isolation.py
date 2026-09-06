from __future__ import annotations

import unittest

from research.relational_foundations.src.r4_term_isolation import (
    R4Config,
    action_cells,
    classify_term_isolation,
)


class R4TermIsolationTests(unittest.TestCase):
    def test_action_cells_have_expected_matched_families(self):
        cells = action_cells(R4Config(strengths=(0.5, 1.0)))
        keys = {(c["family"], c["strength"], c["alpha"], c["beta"]) for c in cells}
        self.assertEqual(len(cells), 7)
        self.assertIn(("null", 0.0, 0.0, 0.0), keys)
        self.assertIn(("curvature_only", 0.5, 0.5, 0.0), keys)
        self.assertIn(("triangle_only", 0.5, 0.0, 0.5), keys)
        self.assertIn(("combined", 1.0, 1.0, 1.0), keys)

    def test_classifier_marks_only_all_seed_crossing_cell_candidate(self):
        rows = []
        for seed, ratio in ((1, 0.75), (2, 0.76)):
            rows.append({
                "family": "null", "strength": 0.0, "seed": seed,
                "path_over_logN": ratio, "spectral_gap": 0.20,
                "triangle_count": 2, "curvature_mean_sampled": -0.2,
            })
        for seed, ratio in ((1, 1.40), (2, 1.35)):
            rows.append({
                "family": "triangle_only", "strength": 1.0, "seed": seed,
                "path_over_logN": ratio, "spectral_gap": 0.05,
                "triangle_count": 20, "curvature_mean_sampled": 0.1,
            })
        for seed, ratio in ((1, 1.40), (2, 1.20)):
            rows.append({
                "family": "curvature_only", "strength": 1.0, "seed": seed,
                "path_over_logN": ratio, "spectral_gap": 0.08,
                "triangle_count": 5, "curvature_mean_sampled": 0.2,
            })
        for seed, ratio in ((1, 1.45), (2, 1.42)):
            rows.append({
                "family": "combined", "strength": 1.0, "seed": seed,
                "path_over_logN": ratio, "spectral_gap": 0.04,
                "triangle_count": 22, "curvature_mean_sampled": 0.25,
            })

        result = classify_term_isolation(rows, threshold=1.3)
        self.assertEqual(result["category"], "PROVISIONAL CANDIDATE")
        candidates = {(x["family"], x["strength"]) for x in result["provisional_candidate_cells"]}
        self.assertIn(("triangle_only", 1.0), candidates)
        self.assertIn(("combined", 1.0), candidates)
        self.assertNotIn(("curvature_only", 1.0), candidates)
        self.assertTrue(result["matched_ablation"][0]["combined_exceeds_both_components_on_path_ratio"])

    def test_classifier_requires_null(self):
        with self.assertRaises(ValueError):
            classify_term_isolation([{
                "family": "combined", "strength": 1.0,
                "path_over_logN": 1.4, "spectral_gap": 0.1,
                "triangle_count": 1, "curvature_mean_sampled": 0.0,
            }])


if __name__ == "__main__":
    unittest.main()
