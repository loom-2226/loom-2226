import unittest
from src.wayfarer_torch_remass_nozzle_envelope import build_envelope, evaluate_coupling_candidate

class TorchRemassNozzleEnvelopeTests(unittest.TestCase):
    def test_authority_firewall(self):
        r=build_envelope()
        self.assertEqual(r['status'],'PASS')
        self.assertEqual(r['authority']['claim'],'E1_TORCH_REMASS_COUPLING_AND_MAGNETIC_NOZZLE_EFFICIENCY_ENVELOPE_ONLY')
        self.assertFalse(r['authority']['nozzle_efficiency_certified'])
        self.assertFalse(r['authority']['working_fluid_certified'])
    def test_preserves_six_mode_kinematics(self):
        r=build_envelope()
        self.assertEqual(r['mode_requirements']['ECON']['exhaust_velocity_km_s'],3000.0)
        self.assertEqual(r['mode_requirements']['LIMIT']['exhaust_velocity_km_s'],300.0)
        self.assertGreater(r['mode_requirements']['LIMIT']['mass_flow_kg_s'],r['mode_requirements']['ECON']['mass_flow_kg_s'])
    def test_no_default_coupling_or_nozzle_efficiency(self):
        r=build_envelope()
        self.assertIsNone(r['candidate_inputs']['source_to_remass_coupling_fraction'])
        self.assertIsNone(r['candidate_inputs']['magnetic_nozzle_directed_efficiency'])
        self.assertIsNone(r['candidate_inputs']['working_fluid_identity'])
    def test_explicit_candidate_only_derives_upstream_power(self):
        e=evaluate_coupling_candidate('CRUISE',0.8,0.9)
        self.assertAlmostEqual(e['combined_directed_fraction'],0.72)
        self.assertGreater(e['required_upstream_coupled_power_W'],e['direct_jet_power_W'])
        self.assertFalse(e['upstream_power_is_electrical_load'])
    def test_invalid_efficiency_rejected(self):
        with self.assertRaises(ValueError): evaluate_coupling_candidate('LIMIT',1.01,0.9)
        with self.assertRaises(ValueError): evaluate_coupling_candidate('LIMIT',0.9,0.0)
    def test_next_step_is_physical_plume_clearance(self):
        self.assertEqual(build_envelope()['qualified_next_step'],'TORCH_PHYSICAL_PLUME_AND_EXTERNAL_CLEARANCE_ENVELOPE')

if __name__=='__main__': unittest.main()
