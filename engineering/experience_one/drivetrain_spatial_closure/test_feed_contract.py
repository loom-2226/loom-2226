"""Run: python -m unittest engineering.experience_one.drivetrain_spatial_closure.test_feed_contract"""
import copy
import unittest
from engineering.experience_one.drivetrain_spatial_closure.feed_contract import FeedInventory, verify_source_contract, verify_live_sources

MODES = ('ECON', 'CRUISE', 'EXPEDITE', 'FAST', 'HARD', 'LIMIT')
BASE = {'status': 'PASS', 'vehicle_interfaces': {'primary_torch_count': 1, 'dry_mass_excluding_working_fluid_water_t': 858.5, 'working_fluid_water_inventory_t': 300, 'reference_wet_mass_t': 1158.5, 'normal_remass_allowance_t': 250, 'protected_water_reserve_t': 50, 'post_normal_remass_reference_mass_t': 908.5, 'torch_and_high_metric_thermal_field_states_mutually_exclusive': True}, 'exhaust_velocity_cards_km_s': dict.fromkeys(MODES, 300)}
PERF = {'status': 'PASS', 'normal_remass_envelope': {'reference_wet_mass_t': 1158.5, 'normal_remass_available_t': 250, 'protected_water_reserve_t': 50, 'post_normal_remass_reference_mass_t': 908.5, 'constant_card_full_normal_remass_burn': {m: {'normal_remass_consumed_t': 250, 'protected_water_consumed_t': 0, 'final_mass_t': 908.5} for m in MODES}}, 'operating_cards': {m: {'exhaust_velocity_km_s': 300, 'exhaust_velocity_m_s': 300000, 'initial_thrust_N_at_reference_wet_mass': f * 300000, 'initial_mass_flow_kg_s_at_reference_wet_mass': f} for m, f in zip(MODES, (1, 2, 5, 10, 50, 250))}}

class FeedContractTests(unittest.TestCase):
    def test_valid_fixture(self):
        self.assertEqual(verify_source_contract(BASE, PERF)['status'], 'PASS')

    def test_reserve_immutable(self):
        inventory = FeedInventory(250, 50, 100).consume_external(100).consume_normal(250)
        self.assertEqual((inventory.normal_t, inventory.protected_t, inventory.external_t), (0, 50, 0))

    def test_overdraw_rejected(self):
        with self.assertRaises(ValueError):
            FeedInventory(250, 50).consume_normal(251)

    def test_bad_turndown_rejected(self):
        performance = copy.deepcopy(PERF)
        performance['operating_cards']['LIMIT']['initial_mass_flow_kg_s'] = 249
        performance['operating_cards']['LIMIT']['initial_thrust_N_at_reference_wet_mass'] = 249 * 300000
        with self.assertRaises(ValueError):
            verify_source_contract(BASE, performance)

    def test_reserve_burn_rejected(self):
        performance = copy.deepcopy(PERF)
        performance['normal_remass_envelope']['constant_card_full_normal_remass_burn']['ECON']['protected_water_consumed_t'] = 1
        with self.assertRaises(ValueError):
            verify_source_contract(BASE, performance)

    def test_metric_exclusion_rejected(self):
        baseline = copy.deepcopy(BASE)
        baseline['vehicle_interfaces']['torch_and_high_metric_thermal_field_states_mutually_exclusive'] = False
        with self.assertRaises(ValueError):
            verify_source_contract(baseline, PERF)

    def test_live_source_builders(self):
        self.assertEqual(verify_live_sources()['status'], 'PASS')

if __name__ == '__main__':
    unittest.main()
