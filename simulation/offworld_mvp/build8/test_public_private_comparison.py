import unittest
from decimal import Decimal as D
from pathlib import Path
from .public_private_comparison import run_public_private_comparison

ROOT=Path('/home/ubuntu/loom_earth_2026_2035/earth_long_run_economic_baseline_v4_2026_09_24')

@unittest.skipUnless(ROOT.exists(),'promoted Earth v4 baseline absent')
class PublicPrivateComparisonTests(unittest.TestCase):
    def test_pressure_and_commercial_activation_are_independent(self):
        results=run_public_private_comparison(ROOT)
        zero=results[False,False]
        public=results[False,True]
        private=results[True,False]
        both=results[True,True]
        self.assertEqual((zero['public_total'],zero['private_total']),(D(0),D(0)))
        self.assertGreater(public['public_total'],0)
        self.assertEqual(public['private_total'],0)
        self.assertEqual(private['public_total'],0)
        self.assertGreater(private['private_total'],0)
        self.assertEqual(both['public_total'],public['public_total'])
        self.assertEqual(both['private_total'],private['private_total'])
        self.assertFalse(public['public_country_affordable'])
        self.assertTrue(public['public_aggregate_affordable'])
        self.assertEqual(results,run_public_private_comparison(ROOT))

    def test_zero_public_share_never_mints_public_capital(self):
        results=run_public_private_comparison(ROOT,public_share=D(0))
        self.assertEqual(results[False,True]['public_total'],0)

    def test_reject_double_counted_allocation(self):
        with self.assertRaises(ValueError):
            run_public_private_comparison(ROOT,public_share=D('.8'),private_share=D('.8'))
