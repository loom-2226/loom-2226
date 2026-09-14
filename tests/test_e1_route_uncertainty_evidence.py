import unittest

from engineering.experience_one.qualification import e1_route_uncertainty_evidence as route_unc


class E1RouteUncertaintyEvidenceTests(unittest.TestCase):
    def _state(self, *, navigation_grade=True, source="SOURCE-010", axis="PASS"):
        return {
            "entity_id": "NEPTUNE",
            "navigation_grade": navigation_grade,
            "provenance": {
                "source_authority": source,
                "axis_qualification": axis,
                "interpolation": "CUBIC_HERMITE_FROM_NAVIGATOR_ROWS",
            },
            "uncertainty": {
                "qualification": "INHERITS_NAVIGATOR_SOURCE_010_AND_AXIS_QUALIFICATION",
                "additional_ephemeris_model": False,
            },
        }

    def test_navigation_grade_source010_lineage_is_admissible_without_fake_numeric_covariance(self):
        report = route_unc.classify_route_uncertainty([self._state()])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["disposition"], "QUALIFIED_ROUTE_UNCERTAINTY_EVIDENCE")
        self.assertFalse(report["numeric_covariance_available"])
        self.assertFalse(report["numeric_covariance_claimed"])
        self.assertEqual(report["source_authority"], "SOURCE-010")

    def test_non_navigation_grade_state_is_not_qualifiable(self):
        report = route_unc.classify_route_uncertainty([self._state(navigation_grade=False)])
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("navigation_grade", report["missing_or_invalid"])

    def test_wrong_source_or_axis_is_not_qualifiable(self):
        wrong_source = route_unc.classify_route_uncertainty([self._state(source="OTHER")])
        self.assertEqual(wrong_source["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("source_authority", wrong_source["missing_or_invalid"])

        wrong_axis = route_unc.classify_route_uncertainty([self._state(axis="FAIL")])
        self.assertEqual(wrong_axis["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("axis_qualification", wrong_axis["missing_or_invalid"])

    def test_missing_uncertainty_lineage_is_not_qualifiable(self):
        state = self._state()
        state["uncertainty"] = {}
        report = route_unc.classify_route_uncertainty([state])
        self.assertEqual(report["disposition"], "INDETERMINATE_NOT_CERTIFIABLE")
        self.assertIn("uncertainty_lineage", report["missing_or_invalid"])

    def test_authority_guards(self):
        report = route_unc.build_static_contract()
        self.assertFalse(report["authority"]["creates_numeric_error_bound"])
        self.assertFalse(report["authority"]["certifies_lattice_coherence"])
        self.assertFalse(report["authority"]["certifies_overall_ga"])
        self.assertEqual(report["authority"]["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["authority"]["llm_calculation_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
