import unittest

from engineering.experience_one.qualification.e1_neptune_rotation_multipole_materiality import (
    LOCAL_GEOMETRY_MATERIALITY_FRACTION,
    measured_zonal_materiality_sweep,
    qualify_neptune_rotation_multipole_materiality,
    rotation_materiality_screen,
)


class NeptuneRotationMultipoleMaterialityTests(unittest.TestCase):
    def test_measured_zonal_sweep_identifies_j2_as_material_and_j4_as_subpercent(self):
        result = measured_zonal_materiality_sweep()

        self.assertEqual(LOCAL_GEOMETRY_MATERIALITY_FRACTION, 0.01)
        self.assertGreaterEqual(result["j2_only"]["max_tidal_tensor_fraction"], 0.01)
        self.assertLess(result["j2_only"]["max_tidal_tensor_fraction"], 0.025)
        self.assertLess(result["j4_only"]["max_tidal_tensor_fraction"], 0.001)
        self.assertTrue(result["j2_only"]["material_at_declared_resolution"])
        self.assertFalse(result["j4_only"]["material_at_declared_resolution"])

    def test_sweep_does_not_assume_an_unqualified_endpoint_latitude(self):
        result = measured_zonal_materiality_sweep()

        self.assertEqual(result["orientation_policy"], "FULL_COLATITUDE_SWEEP_NO_ENDPOINT_LATITUDE_ASSUMED")
        self.assertEqual(result["colatitude_min_deg"], 0.0)
        self.assertEqual(result["colatitude_max_deg"], 180.0)
        self.assertGreater(result["samples"], 180)

    def test_rotation_screen_keeps_frame_dragging_far_below_local_geometry_resolution(self):
        result = rotation_materiality_screen()

        self.assertLess(result["specific_angular_momentum_spin_length_ratio"], 1.0e-5)
        self.assertLess(result["conservative_frame_dragging_curvature_scale_fraction"], 1.0e-4)
        self.assertFalse(result["material_at_declared_resolution"])
        self.assertEqual(result["authority"], "MATERIALITY_SCREEN_NOT_FULL_ROTATING_SPACETIME_SOLUTION")

    def test_source_uncertainty_does_not_flip_j2_or_j4_materiality_classification(self):
        report = qualify_neptune_rotation_multipole_materiality()
        uncertainty = report["source_uncertainty_screen"]

        self.assertTrue(uncertainty["j2_materiality_classification_stable_at_1sigma"])
        self.assertTrue(uncertainty["j4_materiality_classification_stable_at_1sigma"])
        self.assertTrue(uncertainty["rotation_materiality_classification_stable_at_1sigma"])
        self.assertFalse(uncertainty["unmeasured_higher_zonals_treated_as_zero"])

    def test_report_preserves_geometric_admissibility_authority_boundary(self):
        report = qualify_neptune_rotation_multipole_materiality()

        self.assertEqual(report["schema"], "LOOM_E1_NEPTUNE_ROTATION_MULTIPOLE_MATERIALITY_V1")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26_085.768742)
        self.assertEqual(report["decision"], "J2_MATERIAL_INCLUDE_BOUNDED_CORRECTION_FRAME_DRAGGING_AND_J4_NOT_MATERIAL_AT_THIS_STAGE")
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["campaign_state_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertIn("unmeasured_j6_and_higher_zonal_harmonics", report["preserved_unresolved"])
        self.assertNotIn("admissibility_score", report)
        self.assertNotIn("exclusion_radius_km", report)


if __name__ == "__main__":
    unittest.main()
