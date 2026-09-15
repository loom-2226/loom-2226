import unittest
from src.wayfarer_torch_light_remass_storage_feed_nozzle import build_envelope, evaluate_storage

class LightRemassEnvelopeTests(unittest.TestCase):
 def test_no_species_selected(self):
  r=build_envelope(); self.assertIsNone(r['candidate_inputs']['species']); self.assertFalse(r['authority']['working_fluid_selected'])
 def test_requirements_preserved(self):
  r=build_envelope(); self.assertEqual(r['requirements']['normal_remass_kg'],250000.0); self.assertEqual(r['requirements']['protected_water_kg'],50000.0); self.assertEqual(r['requirements']['peak_mass_flow_kg_s'],284.025100625)
 def test_explicit_storage_sensitivity(self):
  c=evaluate_storage('explicit_test_species',50.0,0.9); self.assertAlmostEqual(c['required_tank_internal_volume_m3'],250000.0/50.0/0.9); self.assertFalse(c['certified'])
 def test_invalid_utilization_rejected(self):
  with self.assertRaises(ValueError): evaluate_storage('x',50.0,1.1)
 def test_next(self): self.assertEqual(build_envelope()['qualified_next_step'],'TORCH_LIGHT_REMASS_FEED_DYNAMICS_AND_NOZZLE_COUPLING_MODEL')

if __name__=='__main__': unittest.main()
