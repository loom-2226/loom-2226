import unittest
from decimal import Decimal
from pathlib import Path
from .country_capital_input import load_investment_capacity
from .two_country_trial import run_two_country_trial

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'Earth v4 local inputs absent')
class EightyCountryTrialTests(unittest.TestCase):
    def test_country_transfers(self):
        capacities,_=load_investment_capacity(ROOT)
        countries=tuple(sorted({c for c,y in capacities}))
        self.assertEqual(len(countries),80)
        for year in (2026,2031,2035):
            rows=run_two_country_trial(ROOT,countries,year)
            self.assertEqual(len(rows),80)
            self.assertEqual(len({r['transaction_id'] for r in rows}),80)
            self.assertEqual(rows,run_two_country_trial(ROOT,countries,year))
            self.assertTrue(all(Decimal(r['mobilized'])>=0 for r in rows))

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            run_two_country_trial(ROOT,('USA','USA'))
