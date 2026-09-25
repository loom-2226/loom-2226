"""Run from repository root: python -m unittest discover -s engineering/experience_one/drivetrain_spatial_closure -p 'test_tank_screen.py'."""
import math
import unittest
from tank_screen import Candidate, screen


class TankScreenTests(unittest.TestCase):
    def test_baseline_volume_and_density(self):
        result = screen(Candidate('baseline'), 800, .8)
        expected = 4 * math.pi * 1.5**2 * 14
        self.assertAlmostEqual(result['gross_m3'], expected)
        self.assertAlmostEqual(result['required_density_kg_m3'], 250000/(expected*.8))
        self.assertEqual(result['capacity_screen'], 'PASS')

    def test_capacity_fail_not_hidden(self):
        self.assertEqual(screen(Candidate('baseline'), 600, .8)['capacity_screen'], 'FAIL')

    def test_outward_fairing_not_automatically_allowed(self):
        c = Candidate('expanded', outer_diameter_m=3.4, center_radius_m=2.9)
        self.assertEqual(screen(c, 800, .8)['radial_screen'], 'FAIL')
        self.assertEqual(screen(Candidate('expanded', outer_diameter_m=3.4,
                                          center_radius_m=2.9, shell_allowance_m=.11),
                                800, .8)['radial_screen'], 'PASS')

    def test_protected_reserve_never_claimed(self):
        result = screen(Candidate('baseline'), 800, .8)
        self.assertEqual(result['reserve_50t_storage'], 'HOLD_NOT_ALLOCATED')
        self.assertEqual(result['cabin_shuttle_clearance'], 'HOLD_3D_SWEEP_NOT_RUN')

    def test_invalid_inputs(self):
        for fraction in (0, 1.1):
            with self.assertRaises(ValueError):
                screen(Candidate('bad'), 800, fraction)
        with self.assertRaises(ValueError):
            screen(Candidate('bad', count=3), 800, .8)


if __name__ == '__main__':
    unittest.main()
