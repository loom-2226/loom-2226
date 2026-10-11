"""One fictional ESA BUILD purchase; explicit quotes outrank optional fallbacks."""
import unittest
from decimal import Decimal as D
from .screened_yearly import run_yearly


class ESABuildTrial(unittest.TestCase):
    def test_five_seeds_four_switches(self):
        for seed in (1, 2, 3, 4, 5):
            baseline = None
            for tiers, slots, prices in ((False,False,False), (True,False,False),
                                          (False,True,False), (False,False,True)):
                work, decisions, kernel, occupied = run_yearly(
                    selection='esa_build_quote_trial', seed=seed,
                    tiers=tiers, slots=slots, prices=prices)
                events = {e['kind']:e for e in kernel.event_log if e['kind'].startswith('ESA_')}
                self.assertEqual(len(work), 1)
                self.assertEqual(work[0].category, 'BUILD')
                self.assertEqual(events['ESA_BUILD_QUOTES']['winner'], 'Airbus Defence and Space')
                self.assertEqual(events['ESA_BUILD_QUOTES']['winner_quote'], '0.0240')
                self.assertEqual(events['ESA_BUILD_FINANCING']['committed'], '0.0240')
                self.assertEqual(events['ESA_BUILD_FINANCING']['opening_cash'], '0')
                self.assertEqual(events['ESA_BUILD_DELIVERY']['pre_payment_cash'], '0.0240')
                self.assertEqual(kernel.state.accounts['esa:cash'].balance, D(0))
                self.assertEqual(len([e for e in kernel.event_log if e['kind']=='ESA_BUILD_READINESS']), 1)
                signature = (work, decisions, occupied,
                             tuple((e['kind'],e.get('draw'),e.get('ready')) for e in kernel.event_log
                                   if e['kind'].startswith('ESA_')))
                if baseline is None: baseline = signature
                else: self.assertEqual(signature, baseline)
                kernel.assert_invariants()

if __name__ == '__main__': unittest.main()
