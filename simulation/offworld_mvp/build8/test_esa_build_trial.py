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

    def test_quote_removal_makes_price_switch_observable(self):
        for seed in (1,2,3,4,5):
            results = []
            for prices in (False, True):
                work, _, kernel, _ = run_yearly(
                    selection='esa_build_quote_trial', seed=seed, prices=prices,
                    remove_quote='Airbus Defence and Space')
                quote = next(e for e in kernel.event_log if e['kind']=='ESA_BUILD_QUOTES')
                readiness = next(e for e in kernel.event_log if e['kind']=='ESA_BUILD_READINESS')
                results.append((quote, readiness, work))
            self.assertEqual(results[0][0]['winner'], 'Thales Alenia Space')
            self.assertEqual(results[0][0]['winner_quote'], '0.0270')
            self.assertEqual(results[0][0]['offered_quotes'], {'Thales Alenia Space':'0.0270'})
            self.assertEqual(results[1][0]['winner'], 'Airbus Defence and Space')
            self.assertEqual(D(results[1][0]['winner_quote']), D('.0255'))
            self.assertTrue(results[1][0]['price_fallback_used'])
            self.assertEqual(results[0][1]['draw'], results[1][1]['draw'])
            self.assertEqual(results[0][2][0].start, results[1][2][0].start)
            self.assertEqual(results[0][2][0].finish, results[1][2][0].finish)
            self.assertEqual(results[0][2][0].revenue, D('.0270'))
            self.assertEqual(results[1][2][0].revenue, D('.0255'))

if __name__ == '__main__': unittest.main()
