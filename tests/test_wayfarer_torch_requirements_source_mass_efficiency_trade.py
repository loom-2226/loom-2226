import unittest
from src.wayfarer_torch_requirements_source_mass_efficiency_trade import build_trade, evaluate_point

class TradeTests(unittest.TestCase):
    def test_future_inputs_are_not_defaulted(self):
        r=build_trade()
        self.assertIsNone(r["future_inputs"]["directed_fraction"])
        self.assertIsNone(r["future_inputs"]["source_specific_power_W_kg"])
        self.assertIsNone(r["future_inputs"]["source_mass_budget_kg"])

    def test_limit_point_math(self):
        p=evaluate_point("LIMIT",0.8,1e8,160000.0)
        self.assertAlmostEqual(p["source_power_W"],12781129528125.0/0.8)
        self.assertAlmostEqual(p["required_source_mass_kg"],p["source_power_W"]/1e8)
        self.assertAlmostEqual(p["required_specific_power_for_mass_budget_W_kg"],p["source_power_W"]/160000.0)
        self.assertFalse(p["certified"])

    def test_mass_budget_is_explicit_not_inherited(self):
        with self.assertRaises(ValueError): evaluate_point("LIMIT",0.8,1e8,None)

    def test_next_step(self):
        self.assertEqual(build_trade()["qualified_next_step"],"TORCH_REQUIREMENTS_REDUCTION_AND_SOURCE_PACKAGING_DECISION_REVIEW")

if __name__=="__main__": unittest.main()
