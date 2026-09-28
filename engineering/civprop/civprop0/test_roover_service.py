"""One named Roo-ver service envelope, with no trajectory inference."""
import unittest

from .roover_service import RooVerRequest, assess_roover_service


class RooVerServiceTests(unittest.TestCase):
    def test_manifested_roover_mission_is_conditional(self):
        a = assess_roover_service(RooVerRequest())
        self.assertEqual(a.status, 'CONDITIONAL')
        self.assertEqual(a.actor_access_status, 'USABLE')
        self.assertEqual(a.transport_feasibility, 'UNKNOWN')
        self.assertIn('NASA CLPS CT-4 / Intuitive Machines IM-5', a.matched)
        self.assertIn('exact launch window', a.unresolved)
        self.assertIn('final landing coordinates', a.unresolved)

    def test_available_quantities_are_not_capacity_or_trajectory(self):
        a = assess_roover_service(RooVerRequest())
        q = a.quantities
        self.assertEqual(q['rover_mass_kg_approx'], 20)
        self.assertEqual(q['manifested_suite_mass_kg_approx'], 75)
        self.assertEqual(q['surface_operations_days_expected'], 14)
        self.assertIsNone(q['delivery_capacity_kg'])
        self.assertIsNone(q['delta_v_km_s'])
        self.assertIsNone(q['transfer_duration_days'])

    def test_different_mission_and_date_are_outside_named_path(self):
        for request in (RooVerRequest(mission_id='CIVPROP0_SYNTHETIC'),
                        RooVerRequest(payload_id='OTHER_PAYLOAD'),
                        RooVerRequest(landing_year=2026)):
            a = assess_roover_service(request)
            self.assertEqual(a.status, 'OUT_OF_SCOPE')
            self.assertEqual(a.transport_feasibility, 'UNKNOWN')

    def test_exact_site_is_not_inferred_from_regional_target(self):
        a = assess_roover_service(RooVerRequest(exact_site_id='SYNTHETIC_POLAR_PSR'))
        self.assertEqual(a.status, 'CONDITIONAL')
        self.assertIn('exact landing site match', a.unresolved)

    def test_approximate_mass_does_not_certify_requested_capacity(self):
        a = assess_roover_service(RooVerRequest(payload_mass_kg=30,
                                                required_surface_days=14))
        self.assertEqual(a.status, 'CONDITIONAL')
        self.assertIn('requested payload mass acceptance', a.unresolved)
        self.assertIn('requested surface duration guarantee', a.unresolved)
        with self.assertRaises(ValueError):
            assess_roover_service(RooVerRequest(payload_mass_kg=-1))

    def test_unowned_actor_is_unknown(self):
        a = assess_roover_service(RooVerRequest(actor_id='FLEET_SPACE_TECHNOLOGIES'))
        self.assertEqual(a.status, 'UNKNOWN')

    def test_deterministic_assessment(self):
        self.assertEqual(assess_roover_service(RooVerRequest()),
                         assess_roover_service(RooVerRequest()))


if __name__ == '__main__':
    unittest.main()
