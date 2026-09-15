import unittest
from src.wayfarer_torch_working_fluid_selection_envelope import build_envelope

class TorchWorkingFluidSelectionEnvelopeTests(unittest.TestCase):
 def test_research_ranking_does_not_select_fluid(self):
  r=build_envelope()
  self.assertEqual(r["leading_research_family"],"LIGHT_HYDROGENIC_OR_HELIUM_CLASS")
  self.assertIsNone(r["selected_working_fluid"])
  self.assertFalse(r["certified"])
 def test_water_reserve_firewall(self):
  r=build_envelope()
  self.assertEqual(r["protected_water_reserve_t"],50.0)
  self.assertFalse(r["normal_remass_may_assume_protected_water"])
 def test_next_step(self):
  self.assertEqual(build_envelope()["qualified_next_step"],"TORCH_LIGHT_REMASS_STORAGE_FEED_AND_NOZZLE_COUPLING_ENVELOPE")

if __name__=="__main__": unittest.main()
