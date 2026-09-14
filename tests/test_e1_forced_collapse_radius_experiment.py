import math
import unittest

from engineering.experience_one.qualification.e1_forced_collapse_radius_experiment import (
    candidate_neptune_radii_km,
    bracketed_bisect,
)


class E1ForcedCollapseRadiusExperimentTests(unittest.TestCase):
    def test_candidate_radii_are_positive_and_ordered(self):
        radii = candidate_neptune_radii_km()
        self.assertEqual([r["id"] for r in radii], ["HALF_HILL_PERIAPSIS", "LAPLACE_SOI", "HILL_PERIAPSIS"])
        vals = [r["radius_km"] for r in radii]
        self.assertTrue(all(v > 0 for v in vals))
        self.assertLess(vals[0], vals[1])
        self.assertLess(vals[1], vals[2])

    def test_bracketed_bisect_solves_monotone_root(self):
        root = bracketed_bisect(lambda x: x * x - 9.0, 0.0, 10.0, tol=1e-10)
        self.assertTrue(math.isclose(root, 3.0, rel_tol=0.0, abs_tol=1e-8))

    def test_bracketed_bisect_rejects_unbracketed_root(self):
        with self.assertRaises(ValueError):
            bracketed_bisect(lambda x: x * x + 1.0, -1.0, 1.0)


if __name__ == "__main__":
    unittest.main()
