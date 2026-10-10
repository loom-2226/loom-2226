from .opening import EARTH_V4_ROOT
import unittest
from decimal import Decimal
from pathlib import Path
from .finite_capital_trial import run_finite_capital_trial

ROOT=EARTH_V4_ROOT

@unittest.skipUnless(ROOT.exists(),'promoted Earth v4 local baseline absent')
class FiniteCapitalTrialTests(unittest.TestCase):
    def test_first_proposal_funds_second_waits_and_replays(self):
        first,capital,spent=run_finite_capital_trial(ROOT)
        self.assertEqual((first,capital,spent),run_finite_capital_trial(ROOT))
        self.assertEqual([r[1] for r in first],['INITIATE_PROJECT','WAIT'])
        self.assertEqual(Decimal(spent),Decimal(3))
        self.assertEqual(Decimal(first[-1][-1]),Decimal(capital)-Decimal(spent))
