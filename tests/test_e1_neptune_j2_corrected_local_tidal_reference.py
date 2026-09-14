import importlib.util
import math
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_neptune_j2_corrected_local_tidal_reference.py"
spec = importlib.util.spec_from_file_location("e1_neptune_j2_corrected_local_tidal_reference", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestNeptuneJ2CorrectedLocalTidalReference(unittest.TestCase):
    def test_endpoint_is_preserved(self):
        report = mod.qualify_j2_corrected_local_tidal_reference()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["body"], "NEPTUNE")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26085.768742)
        self.assertEqual(report["endpoint"]["endpoint_status"], "EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY")

    def test_orientation_envelope_matches_earned_j2_reference(self):
        report = mod.qualify_j2_corrected_local_tidal_reference()
        env = report["j2_corrected_tidal_reference"]["orientation_envelope"]
        self.assertEqual(env["orientation_policy"], "FULL_COLATITUDE_SWEEP_NO_ENDPOINT_LATITUDE_ASSUMED")
        self.assertEqual(env["samples"], 721)
        self.assertTrue(math.isclose(env["tidal_frobenius_norm_s2_inv"]["min"], 9.253649957398604e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(env["tidal_frobenius_norm_s2_inv"]["max"], 9.524357073448463e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(env["fractional_change_from_monopole_norm"]["min"], -0.01912717850717327, rel_tol=0.0, abs_tol=1e-15))
        self.assertTrue(math.isclose(env["fractional_change_from_monopole_norm"]["max"], 0.009567364072288642, rel_tol=0.0, abs_tol=1e-15))

    def test_principal_tidal_eigenvalue_envelope_is_trace_free(self):
        report = mod.qualify_j2_corrected_local_tidal_reference()
        principal = report["j2_corrected_tidal_reference"]["orientation_envelope"]["principal_tidal_eigenvalues_s2_inv"]
        self.assertTrue(math.isclose(principal["most_negative"]["min"], -3.906704817595004e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(principal["most_negative"]["max"], -3.7777867756589795e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(principal["middle"]["min"], -3.8698710913275684e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(principal["middle"]["max"], -3.7777867756589795e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(principal["most_positive"]["min"], 7.555573551317959e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(principal["most_positive"]["max"], 7.776575908922572e-07, rel_tol=0.0, abs_tol=1e-18))
        self.assertLess(report["j2_corrected_tidal_reference"]["max_abs_trace_s2_inv"], 1e-20)

    def test_source_uncertainty_is_propagated_without_collapsing_orientation(self):
        report = mod.qualify_j2_corrected_local_tidal_reference()
        uncertainty = report["source_uncertainty_envelope"]
        self.assertEqual(uncertainty["scope"], "PUBLISHED_J2_1SIGMA_ONLY_NOT_2226_MODEL_EVOLUTION")
        self.assertEqual(uncertainty["orientation_policy"], "FULL_COLATITUDE_SWEEP_FOR_EACH_J2_BOUND")
        self.assertFalse(uncertainty["2226_gravity_field_evolution_treated_as_zero"])
        self.assertFalse(report["j2_corrected_tidal_reference"]["single_endpoint_orientation_claimed"])

    def test_authority_boundary_remains_zero(self):
        report = mod.qualify_j2_corrected_local_tidal_reference()
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertEqual(report["qualified_next_step"], "ASSESS_LOCAL_STRESS_ENERGY_MATTER_DENSITY_RELEVANCE_BEFORE_COMPOUND_GEOMETRIC_ADMISSIBILITY")
        self.assertIn("unmeasured_j6_and_higher_zonal_harmonics", report["preserved_unresolved"])
        self.assertIn("endpoint_planetographic_latitude_and_orientation", report["preserved_unresolved"])


if __name__ == "__main__":
    unittest.main()
