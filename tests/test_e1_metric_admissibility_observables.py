import math
import unittest

from engineering.experience_one.qualification.e1_metric_admissibility_observables import gravitational_observables


class TestMetricAdmissibilityObservables(unittest.TestCase):
    def test_gravitational_observables_are_diagnostic_scalars(self):
        result = gravitational_observables(mu_km3_s2=100.0, radius_km=10.0)
        self.assertEqual(result["mu_km3_s2"], 100.0)
        self.assertEqual(result["radius_km"], 10.0)
        self.assertTrue(math.isclose(result["acceleration_km_s2"], 1.0))
        self.assertTrue(math.isclose(result["tidal_scale_s2"], 0.1))
        self.assertEqual(result["classification"], "DIAGNOSTIC_OBSERVABLES_ONLY_NOT_ADMISSIBILITY_POLICY")

    def test_rejects_nonphysical_inputs(self):
        for mu, radius in ((0.0, 10.0), (-1.0, 10.0), (1.0, 0.0), (1.0, -2.0)):
            with self.subTest(mu=mu, radius=radius):
                with self.assertRaises(ValueError):
                    gravitational_observables(mu_km3_s2=mu, radius_km=radius)


if __name__ == "__main__":
    unittest.main()
