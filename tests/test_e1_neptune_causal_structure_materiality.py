import importlib.util
import math
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "qualification" / "e1_neptune_causal_structure_materiality.py"
spec = importlib.util.spec_from_file_location("e1_neptune_causal_structure_materiality", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestNeptuneCausalStructureMateriality(unittest.TestCase):
    def test_earned_endpoint_is_preserved(self):
        report = mod.qualify_neptune_causal_structure_materiality()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["body"], "NEPTUNE")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26085.768742)
        self.assertFalse(report["endpoint"]["endpoint_moved_or_resolved_again"])

    def test_standard_gr_compactness_is_deep_weak_field(self):
        report = mod.qualify_neptune_causal_structure_materiality()
        screen = report["standard_gr_causal_pathology_screen"]
        self.assertTrue(math.isclose(screen["schwarzschild_radius_km"], 0.00015213328750124377, rel_tol=0.0, abs_tol=1e-18))
        self.assertTrue(math.isclose(screen["compactness_2gm_rc2"], 5.8320415628119115e-09, rel_tol=0.0, abs_tol=1e-20))
        self.assertGreater(screen["static_time_coefficient_margin_1_minus_2gm_rc2"], 0.99999999)
        self.assertLess(screen["gravitational_redshift_z"], 1e-8)
        self.assertFalse(screen["horizon_like_behavior_material_at_endpoint"])

    def test_axis_is_bounded_without_claiming_full_spacetime_solution(self):
        report = mod.qualify_neptune_causal_structure_materiality()
        axis = report["compound_ga_axis_update"]
        self.assertEqual(axis["axis"], "causal_structure")
        self.assertEqual(axis["status"], "QUALIFIED_MATERIALITY_SCREEN")
        self.assertEqual(axis["decision"], "STANDARD_GR_CAUSAL_PATHOLOGY_NOT_MATERIAL_AT_E1_NEPTUNE_ENDPOINT_FULL_ROTATING_SPACETIME_REMAINS_UNRESOLVED")
        self.assertFalse(axis["full_rotating_spacetime_solved"])
        self.assertFalse(axis["loom_specific_causal_rule_assumed"])

    def test_authority_boundaries_and_next_step(self):
        report = mod.qualify_neptune_causal_structure_materiality()
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertFalse(report["runtime_policy_bound"])
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertIn("full_rotating_neptune_spacetime", report["preserved_unresolved"])
        self.assertIn("loom_specific_metric_causal_structure", report["preserved_unresolved"])
        self.assertEqual(report["qualified_next_step"], "QUALIFY_COMPOUND_GA_DOMAIN_SIZE_WITHOUT_BINDING_RUNTIME_POLICY")


if __name__ == "__main__":
    unittest.main()
