import unittest

from engineering.experience_one.qualification.e1_geometric_admissibility_relevance_audit import build_relevance_audit


class GeometricAdmissibilityRelevanceAuditTests(unittest.TestCase):
    def test_audit_preserves_named_canon_families_without_numeric_importance_score(self):
        report = build_relevance_audit()
        self.assertEqual(report["schema"], "LOOM_E1_GEOMETRIC_ADMISSIBILITY_RELEVANCE_AUDIT_V1")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["scoring_authority"], "ZERO")
        families = {row["family"] for row in report["factors"]}
        self.assertTrue({
            "curvature",
            "curvature_gradients_tidal_shear",
            "stress_energy_matter_density",
            "electromagnetic_conditions",
            "causal_structure",
            "domain_size",
            "loom_coherence",
            "lattice_coherence",
            "uncertainty",
        }.issubset(families))

    def test_geometry_and_tidal_terms_are_next_engineering_focus(self):
        report = build_relevance_audit()
        by_family = {row["family"]: row for row in report["factors"]}
        self.assertEqual(by_family["curvature"]["work_priority"], "NEXT_ENGINEERING")
        self.assertEqual(by_family["curvature_gradients_tidal_shear"]["work_priority"], "NEXT_ENGINEERING")
        self.assertEqual(by_family["electromagnetic_conditions"]["work_priority"], "HOLD_UNTIL_COUPLING_IS_EARNED")
        self.assertEqual(by_family["loom_coherence"]["work_priority"], "PHYSICS_BLOCKED")
        self.assertEqual(report["next_action"], "QUALIFY_LOCAL_CURVATURE_AND_TIDAL_SHEAR_AT_THE_EARNED_NEPTUNE_COLLAPSE_ENDPOINT_WITHOUT_DEFINING_A_NEW_THRESHOLD")

    def test_hill_and_soi_are_context_only_not_admissibility_boundaries(self):
        report = build_relevance_audit()
        context = {row["quantity"]: row for row in report["context_only"]}
        self.assertEqual(context["Hill radius"]["admissibility_boundary_authority"], "ZERO")
        self.assertEqual(context["Laplace sphere of influence"]["admissibility_boundary_authority"], "ZERO")

    def test_uncertainty_is_a_decision_gate_not_an_environmental_force(self):
        report = build_relevance_audit()
        by_family = {row["family"]: row for row in report["factors"]}
        self.assertEqual(by_family["uncertainty"]["role"], "EPISTEMIC_DECISION_GATE")


if __name__ == "__main__":
    unittest.main()
