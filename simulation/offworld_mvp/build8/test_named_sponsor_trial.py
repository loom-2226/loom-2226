import unittest
from pathlib import Path
from decimal import Decimal as D
from .named_sponsor_trial import run_named_sponsors

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'Earth v4 baseline absent')
class NamedSponsorTrialTests(unittest.TestCase):
    def test_six_sponsors_finite_and_replayable(self):
        rows,fingerprint=run_named_sponsors(ROOT)
        self.assertEqual([r['sponsor'] for r in rows],
                         ['NASA','CNSA','ESA','SpaceX','Axiom','ispace'])
        self.assertTrue(all(D(r['opening']) >= D(r['closing']) >= 0 for r in rows))
        self.assertEqual((rows,fingerprint),run_named_sponsors(ROOT))
