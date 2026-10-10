import unittest
from decimal import Decimal
from pathlib import Path
from .ten_year_trial import run_ten_year_trial

ROOT = Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(), 'promoted Earth v4 local inputs absent')
class TenYearTrialTests(unittest.TestCase):
    def test_active_and_no_opportunity(self):
        active, provenance = run_ten_year_trial(ROOT, True)
        inactive, _ = run_ten_year_trial(ROOT, False)
        self.assertEqual(set(active), set(range(2026, 2036)))
        self.assertEqual(active[2026], Decimal('25.10396510558080532339'))
        self.assertEqual(active[2035], Decimal('31.82503536427524189931'))
        self.assertTrue(all(value == 0 for value in inactive.values()))
        self.assertEqual(provenance['standing'], 'MODELED_INVESTMENT_CAPACITY_NOT_SPENDABLE_CASH')
