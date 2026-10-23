"""Small contract checks for the opt-in flyby ceiling switch."""
import unittest
from .route1_flyby_price_variant import FlybyCampaign, run_identity


class FlybyCeilingSwitchTests(unittest.TestCase):
    def test_default_is_off(self):
        self.assertFalse(FlybyCampaign().ceilings_enabled)
        self.assertEqual(run_identity(), 'variant_ceilings_off')

    def test_explicit_on(self):
        self.assertTrue(FlybyCampaign(ceilings_enabled=True).ceilings_enabled)
        self.assertEqual(run_identity(True), 'variant_ceilings_on')
        self.assertNotEqual(run_identity(), run_identity(True))


if __name__ == '__main__':
    unittest.main()
