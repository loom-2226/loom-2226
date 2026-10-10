import unittest
from decimal import Decimal
from pathlib import Path
from simulation.offworld_mvp.build8.two_country_trial import run_two_country_trial

ROOT = Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(), 'promoted Earth v4 local baseline not available')
class TwoCountryTrialTests(unittest.TestCase):
    def test_country_scoped_kernel_transactions_replay(self):
        first=run_two_country_trial(ROOT)
        second=run_two_country_trial(ROOT)
        self.assertEqual(first,second)
        self.assertEqual([row['country'] for row in first],['USA','AUS'])
        self.assertEqual(Decimal(first[0]['mobilized']),Decimal('4.958025335469291'))
        self.assertEqual(Decimal(first[1]['mobilized']),Decimal('0.412288545182134'))

if __name__ == '__main__':
    unittest.main()
