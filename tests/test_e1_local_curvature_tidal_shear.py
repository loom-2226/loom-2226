import math
import unittest

from engineering.experience_one.qualification.e1_local_curvature_tidal_shear import (
    C_KM_S,
    local_monopole_geometry,
    qualify_earned_neptune_endpoint,
)


class LocalCurvatureTidalShearTests(unittest.TestCase):
    def test_monopole_geometry_matches_closed_form_reference(self):
        gm = 6_836_529.0
        radius = 26_085.768742
        result = local_monopole_geometry(gm_km3_s2=gm, radius_km=radius)

        lam = gm / radius**3
        self.assertAlmostEqual(result["gravity_acceleration_km_s2"], gm / radius**2, places=15)
        self.assertAlmostEqual(result["tidal_eigenvalues_s2_inv"]["radial"], 2.0 * lam, places=18)
        self.assertAlmostEqual(result["tidal_eigenvalues_s2_inv"]["transverse_1"], -lam, places=18)
        self.assertAlmostEqual(result["tidal_eigenvalues_s2_inv"]["transverse_2"], -lam, places=18)
        self.assertAlmostEqual(sum(result["tidal_eigenvalues_s2_inv"].values()), 0.0, places=18)
        self.assertAlmostEqual(result["tidal_frobenius_norm_s2_inv"], math.sqrt(6.0) * lam, places=18)

        expected_k = 48.0 * gm**2 / (C_KM_S**4 * radius**6)
        self.assertAlmostEqual(result["schwarzschild_kretschmann_km4_inv"], expected_k, places=45)
        self.assertAlmostEqual(result["schwarzschild_sqrt_kretschmann_km2_inv"], math.sqrt(expected_k), places=30)

    def test_earned_endpoint_report_preserves_authority_boundary(self):
        report = qualify_earned_neptune_endpoint()
        self.assertEqual(report["schema"], "LOOM_E1_LOCAL_CURVATURE_TIDAL_SHEAR_V1")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["endpoint"]["body"], "NEPTUNE")
        self.assertEqual(report["endpoint"]["collapse_radius_km"], 26_085.768742)
        self.assertEqual(report["inputs"]["gm_km3_s2"], 6_836_529.0)
        self.assertEqual(report["inputs"]["mean_radius_km"], 24_622.0)
        self.assertAlmostEqual(report["endpoint"]["altitude_above_mean_radius_km"], 1_463.768742, places=6)
        self.assertFalse(report["admissibility_threshold_defined"])
        self.assertEqual(report["runtime_policy_mutation"], "ZERO")
        self.assertEqual(report["llm_calculation_authority"], "ZERO")
        self.assertEqual(report["interpretation"], "LOCAL_GEOMETRY_REFERENCE_QUALIFIED_ADMISSIBILITY_DECISION_NOT_YET_EARNED")

    def test_report_does_not_claim_unqualified_corrections(self):
        report = qualify_earned_neptune_endpoint()
        unresolved = set(report["unresolved_corrections"])
        self.assertIn("neptune_rotation_and_frame_dragging", unresolved)
        self.assertIn("neptune_oblateness_and_higher_multipoles", unresolved)
        self.assertIn("local_stress_energy_matter_density", unresolved)
        self.assertIn("physical_uncertainty_at_2226_endpoint", unresolved)
        self.assertNotIn("admissibility_score", report)
        self.assertNotIn("exclusion_radius_km", report)


if __name__ == "__main__":
    unittest.main()
