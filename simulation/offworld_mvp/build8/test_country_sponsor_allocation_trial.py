import unittest
from decimal import Decimal as D
from pathlib import Path
from .country_sponsor_allocation_trial import run_allocation

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'Earth v4 absent')
class AllocationTrialTests(unittest.TestCase):
    def test_explicit_allocation_preserves_capital_and_replay(self):
        a=run_allocation(ROOT)
        self.assertEqual(a[1], '2')
        self.assertEqual(a[3], '0')
        self.assertEqual(D(a[0])+D(a[1]),D(a[2]))
        self.assertEqual(a,run_allocation(ROOT))

    def test_cannot_overallocate(self):
        with self.assertRaises(ValueError):
            run_allocation(ROOT,D('999'))
