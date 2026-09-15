import unittest
from src.wayfarer_torch_source_architecture_breakthrough_trade import build_trade

class TorchSourceArchitectureBreakthroughTradeTests(unittest.TestCase):
 def test_no_architecture_is_certified(self):
  r=build_trade(); self.assertFalse(r["authority"]["source_architecture_certified"]); self.assertFalse(r["authority"]["fuel_cycle_certified"])
 def test_scale_breakthrough_is_explicit(self):
  r=build_trade(); self.assertGreater(r["minimum_ideal_LIMIT_specific_power_MW_kg_if_160t_all_source"],79.0)
  self.assertGreater(r["scale_gap_vs_present_DFD_upper"],50000)
 def test_frc_is_direction_not_winner(self):
  r=build_trade(); self.assertEqual(r["preferred_research_direction"]["status"],"RESEARCH_DIRECTION_ONLY_NOT_COMPONENT_SELECTION")
 def test_alternatives_are_kept_alive(self):
  ids={x["id"] for x in build_trade()["families"]}
  self.assertTrue({"LOW_NEUTRON_FRC_DIRECT_FUSION","PULSED_MAGNETIZED_TARGET_FUSION","GENERIC_ADVANCED_FUSION_SOURCE_WITH_REMASS_HEAT_EXCHANGER","REQUIREMENTS_REDUCTION_OR_MODE_REDESIGN"}.issubset(ids))
 def test_next_step(self):
  self.assertEqual(build_trade()["qualified_next_step"],"TORCH_REQUIREMENTS_VS_SOURCE_MASS_AND_EFFICIENCY_TRADE_SPACE")
if __name__=="__main__": unittest.main()
