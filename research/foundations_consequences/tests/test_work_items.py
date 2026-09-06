import unittest

from research.foundations_consequences.src.work_items import (
    evidence_traffic_warning,
    validate_work_item,
)


class WorkItemValidationTests(unittest.TestCase):
    def _good_item(self):
        return {
            "id": "S4.1",
            "title": "Protected identity formalization",
            "lane": "EMPIRICAL_MATHEMATICAL",
            "state": "PROBE",
            "epistemic_class": "O",
            "epistemic_hazard": "HIGH",
            "scores": {
                "scientific_leverage": 4,
                "speculative_reach": 5,
                "canon_leverage": 5,
                "world_yield": 5,
                "play_yield": 5,
                "rabbit_hole_joy": 5,
            },
        }

    def test_valid_item_passes(self):
        result = validate_work_item(self._good_item())
        self.assertTrue(result.ok)
        self.assertEqual(result.errors, ())

    def test_bad_score_fails(self):
        item = self._good_item()
        item["scores"]["scientific_leverage"] = 7
        result = validate_work_item(item)
        self.assertFalse(result.ok)
        self.assertIn("score scientific_leverage must be integer 0..5", result.errors)

    def test_fiction_to_science_warns(self):
        warnings = evidence_traffic_warning(
            "CIVILIZATIONAL_FICTIONAL",
            "EMPIRICAL_MATHEMATICAL",
            ["interesting synthetic personhood scenario"],
        )
        self.assertTrue(warnings)

    def test_canon_fit_warns(self):
        warnings = evidence_traffic_warning(
            "SPECULATIVE_SYNTHETIC",
            "EMPIRICAL_MATHEMATICAL",
            ["excellent canon fit"],
        )
        self.assertIn("canon compatibility is not scientific evidence", warnings)


if __name__ == "__main__":
    unittest.main()
