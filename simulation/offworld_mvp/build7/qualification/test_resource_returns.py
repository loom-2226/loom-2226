import unittest
from decimal import Decimal as D
from simulation.offworld_mvp.build7.resource_returns import compare_returns

class ResourceReturnsTests(unittest.TestCase):
    def test_rich_location_changes_profit(self):
        moon=compare_returns(scenario='RICH',body_id='MOON')
        halley=compare_returns(scenario='RICH',body_id='COMET_HALLEY')
        self.assertGreater(moon['net_return'],0)
        self.assertLess(halley['net_return'],0)
    def test_null_stops_and_avoids_cargo(self):
        result=compare_returns(scenario='NULL',body_id='CERES')
        self.assertEqual(result['years'],0)
        self.assertEqual(result['operating_cash_flow'],D(0))
        self.assertEqual(result['mission_cost'],D('1.545482'))
    def test_sparse_still_fails_with_lower_capex_after_transport(self):
        normal=compare_returns(scenario='SPARSE',body_id='MOON')
        cheap=compare_returns(scenario='SPARSE',body_id='MOON',development_capital=0)
        self.assertLess(normal['net_return'],0)
        self.assertLess(cheap['net_return'],0)
        self.assertGreater(cheap['net_return'],normal['net_return'])
    def test_missing_trajectory_is_unknown(self):
        from simulation.offworld_mvp.build7.mission_costs import public_mission_cost
        from simulation.offworld_mvp.build7.mission_costs import MissionCostLookup
        lookup=MissionCostLookup()
        self.assertIsNone(lookup.lookup(2026,'DOES_NOT_EXIST','FLYBY'))
    def test_operating_year_limit(self):
        with self.assertRaises(ValueError):
            compare_returns(scenario='RICH',body_id='MOON',years=11)

if __name__=='__main__':unittest.main()
