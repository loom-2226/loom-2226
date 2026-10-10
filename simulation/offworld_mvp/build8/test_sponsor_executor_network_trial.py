"""Build 8 Experiment B: an award must not masquerade as physical delivery."""
import unittest
from pathlib import Path
from decimal import Decimal as D
from .sponsor_executor_network_trial import run_network

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'Earth v4 baseline absent')
class SponsorExecutorNetworkTests(unittest.TestCase):
    def test_awards_hold_cash_until_physical_plan(self):
        rows,revenue,fingerprint=run_network(ROOT)
        awards=[r for r in rows if r['outcome']=='AWARDED_PENDING_PLAN']
        self.assertEqual([r['sponsor'] for r in awards],['CNSA','ISRO','ESA'])
        self.assertEqual(len(rows),20)
        self.assertEqual(len(awards),3)
        self.assertTrue(all(v==str(D(0)) for v in revenue.values()))
        self.assertEqual(sum(D(r['cost']) for r in awards),D('.090'))
        self.assertEqual((rows,revenue,fingerprint),run_network(ROOT))
