import unittest
from src.wayfarer_torch_working_fluid_feed_trade import build_trade, evaluate_candidate

class TorchWorkingFluidFeedTradeTests(unittest.TestCase):
    def test_identity_remains_open(self):
        r=build_trade()
        self.assertIsNone(r["candidate_inputs"]["working_fluid"])
        self.assertIsNone(r["candidate_inputs"]["storage_state"])
        self.assertIsNone(r["candidate_inputs"]["feed_architecture"])

    def test_required_flow_span_is_preserved(self):
        r=build_trade()
        self.assertAlmostEqual(r["requirements"]["mass_flow_kg_s_range"][0],1.1361004025)
        self.assertAlmostEqual(r["requirements"]["mass_flow_kg_s_range"][1],284.025100625)
        self.assertEqual(r["requirements"]["normal_remass_t"],250.0)

    def test_candidate_requires_explicit_properties(self):
        with self.assertRaises(ValueError): evaluate_candidate("hydrogen",None,10.0,100.0)
        c=evaluate_candidate("explicit_test_fluid",20.0,10.0,100.0)
        self.assertEqual(c["status"],"SENSITIVITY_ONLY_EXPLICIT_INPUTS")
        self.assertFalse(c["certified"])

    def test_next_step(self):
        self.assertEqual(build_trade()["qualified_next_step"],"TORCH_WORKING_FLUID_RESEARCH_AND_MATERIAL_COMPATIBILITY_BOUND")

if __name__=="__main__": unittest.main()
