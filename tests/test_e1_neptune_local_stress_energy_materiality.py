import importlib.util
import math
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_neptune_local_stress_energy_materiality.py"
spec = importlib.util.spec_from_file_location("e1_neptune_local_stress_energy_materiality", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestNeptuneLocalStressEnergyMateriality(unittest.TestCase):
    def test_earned_endpoint_and_j2_reference_are_preserved(self):
        report = mod.qualify_local_stress_energy_materiality()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["body"], "NEPTUNE")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26085.768742)
        self.assertFalse(report["endpoint"]["endpoint_moved_or_resolved_again"])
        self.assertTrue(math.isclose(report["qualified_local_geometry_reference"]["minimum_j2_corrected_tidal_frobenius_s2_inv"], 9.253496458704657e-07, rel_tol=0.0, abs_tol=1e-18))

    def test_observational_atmosphere_proxy_is_far_below_one_percent_materiality(self):
        report = mod.qualify_local_stress_energy_materiality()
        atmosphere = report["observational_screens"]["upper_atmosphere_proxy"]
        self.assertEqual(atmosphere["pressure_pa"], 1.1e-4)
        self.assertEqual(atmosphere["temperature_k"], 550.0)
        self.assertTrue(math.isclose(atmosphere["h2_number_density_m3"], 1.448594103207984e16, rel_tol=0.0, abs_tol=1e4))
        self.assertTrue(math.isclose(atmosphere["h2_mass_density_kg_m3"], 4.848611051758991e-11, rel_tol=0.0, abs_tol=1e-22))
        self.assertLess(atmosphere["ricci_to_tidal_materiality_ratio"], 1e-12)
        self.assertFalse(atmosphere["material_at_one_percent_resolution"])

    def test_required_source_strength_for_one_percent_is_explicit(self):
        report = mod.qualify_local_stress_energy_materiality()
        required = report["one_percent_materiality_requirements"]
        self.assertTrue(math.isclose(required["equivalent_mass_density_kg_m3"], 5.516457539690285, rel_tol=0.0, abs_tol=1e-12))
        self.assertTrue(math.isclose(required["h2_pressure_at_550k_pa"], 12515137.281341452, rel_tol=0.0, abs_tol=1e-6))
        self.assertTrue(math.isclose(required["magnetic_field_tesla"], 1116273.905608525, rel_tol=0.0, abs_tol=1e-6))
        self.assertEqual(required["materiality_resolution_fraction"], 0.01)

    def test_magnetic_and_plasma_observational_screens_are_non_material(self):
        report = mod.qualify_local_stress_energy_materiality()
        magnetic = report["observational_screens"]["magnetic_field_proxy"]
        plasma = report["observational_screens"]["plasma_proxy"]
        self.assertEqual(magnetic["field_gauss"], 0.14)
        self.assertLess(magnetic["ricci_to_tidal_materiality_ratio"], 1e-22)
        self.assertFalse(magnetic["material_at_one_percent_resolution"])
        self.assertEqual(plasma["number_density_cm3"], 1.0)
        self.assertEqual(plasma["particle_energy_kev"], 100.0)
        self.assertLess(plasma["ricci_to_tidal_materiality_ratio"], 1e-26)
        self.assertFalse(plasma["material_at_one_percent_resolution"])

    def test_uncertainty_and_authority_boundaries_are_preserved(self):
        report = mod.qualify_local_stress_energy_materiality()
        self.assertFalse(report["uncertainty"]["2226_neptune_atmosphere_treated_as_known"])
        self.assertFalse(report["uncertainty"]["2226_neptune_magnetosphere_treated_as_known"])
        self.assertFalse(report["uncertainty"]["loom_specific_em_metric_coupling_assumed"])
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertEqual(report["decision"], "LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY")
        self.assertEqual(report["qualified_next_step"], "ASSESS_COMPOUND_GEOMETRIC_ADMISSIBILITY_MODEL_FORM_WITHOUT_BINDING_RUNTIME_POLICY")
        self.assertIn("2226_local_atmospheric_state", report["preserved_unresolved"])
        self.assertIn("em_to_metric_coupling", report["preserved_unresolved"])


if __name__ == "__main__":
    unittest.main()
