import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_compound_geometric_admissibility_model_form.py"
spec = importlib.util.spec_from_file_location("e1_compound_geometric_admissibility_model_form", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestCompoundGeometricAdmissibilityModelForm(unittest.TestCase):
    def test_earned_endpoint_is_preserved_without_policy_binding(self):
        report = mod.qualify_compound_geometric_admissibility_model_form()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["body"], "NEPTUNE")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26085.768742)
        self.assertFalse(report["endpoint"]["endpoint_moved_or_resolved_again"])
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertFalse(report["runtime_policy_bound"])

    def test_model_form_is_typed_evidence_vector_not_scalar_score(self):
        report = mod.qualify_compound_geometric_admissibility_model_form()
        model = report["compound_model_form"]
        self.assertEqual(model["representation"], "TYPED_EVIDENCE_VECTOR_WITH_UNCERTAINTY_LEDGER")
        self.assertFalse(model["scalar_score_defined"])
        self.assertFalse(model["weights_defined"])
        self.assertFalse(model["admissible_boolean_defined"])
        self.assertNotIn("score", report)

    def test_qualified_independent_terms_are_preserved_as_evidence_axes(self):
        report = mod.qualify_compound_geometric_admissibility_model_form()
        axes = report["evidence_axes"]
        self.assertEqual(axes["local_geometry"]["status"], "QUALIFIED")
        self.assertEqual(axes["local_geometry"]["reference_model"], "AXISYMMETRIC_MONOPOLE_PLUS_MEASURED_J2_WEAK_FIELD_TIDAL_ENVELOPE")
        self.assertEqual(axes["local_geometry"]["tidal_frobenius_norm_s2_inv"]["min"], 9.253496458704657e-07)
        self.assertEqual(axes["local_geometry"]["tidal_frobenius_norm_s2_inv"]["max"], 9.524433883120696e-07)
        self.assertEqual(axes["local_stress_energy"]["status"], "QUALIFIED_MATERIALITY_SCREEN")
        self.assertEqual(axes["local_stress_energy"]["decision"], "LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY")

    def test_unresolved_axes_remain_explicit_and_cannot_be_silently_zeroed(self):
        report = mod.qualify_compound_geometric_admissibility_model_form()
        axes = report["evidence_axes"]
        for key in ("causal_structure", "domain_size", "loom_coherence", "lattice_coherence"):
            self.assertEqual(axes[key]["status"], "UNRESOLVED")
            self.assertFalse(axes[key]["treated_as_zero"])
        self.assertFalse(report["uncertainty_ledger"]["unknown_axes_treated_as_zero"])
        self.assertFalse(report["uncertainty_ledger"]["cross_axis_compensation_assumed"])

    def test_authority_boundary_and_next_step_are_explicit(self):
        report = mod.qualify_compound_geometric_admissibility_model_form()
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertEqual(report["decision"], "COMPOUND_GA_MODEL_FORM_QUALIFIED_AS_PARTIALLY_RESOLVED_EVIDENCE_VECTOR_NO_DECISION_RULE")
        self.assertEqual(report["qualified_next_step"], "QUALIFY_REMAINING_COMPOUND_GA_AXES_BEFORE_ANY_ADMISSIBILITY_DECISION_RULE")
        self.assertIn("causal_structure", report["blocking_unresolved_axes"])
        self.assertIn("domain_size", report["blocking_unresolved_axes"])
        self.assertIn("loom_coherence", report["blocking_unresolved_axes"])
        self.assertIn("lattice_coherence", report["blocking_unresolved_axes"])


if __name__ == "__main__":
    unittest.main()
