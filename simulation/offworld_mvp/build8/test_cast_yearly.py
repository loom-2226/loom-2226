"""One genuine cast-selected country/sponsor/executor replay beyond USA."""
import unittest
from .screened_yearly import run_yearly
from .yearly_selections import select
from .named_sponsor_trial import ROUTES

class CastYearlyTests(unittest.TestCase):
    def test_japan_cast_participation(self):
        chosen = select('japan_lunar')
        self.assertEqual(chosen['country'], 'JPN')
        for name in chosen['sponsors']:
            self.assertIn('JPN', ROUTES[name][1])  # existing authored funding participation
        work, decisions, kernel, occupied = run_yearly(selection='japan_lunar')
        self.assertEqual({r[0] for r in decisions}, {'Axiom', 'ispace'})
        self.assertEqual({r[1] for r in decisions}, {'INITIATE_PROJECT'})
        self.assertEqual({r[2] for r in decisions}, {'APPROVE'})
        self.assertEqual({r[4] for r in decisions}, {2026, 2027})
        self.assertEqual(len(work), 4)
        self.assertEqual({w.category for w in work}, {'BUILD', 'LAND'})
        self.assertEqual({w.outcome for w in work}, {'DELIVERED'})
        self.assertEqual([w.start for w in work], [2026, 2027, 2028, 2029])
        self.assertEqual([w.finish for w in work], [2028, 2029, 2030, 2031])
        self.assertEqual([r[0] for r in kernel.build8_knowledge],
                         sorted(r[0] for r in kernel.build8_knowledge))
        self.assertTrue(occupied)
        self.assertEqual(kernel.state.accounts['screen:fund'].node_id, 'EARTH:JPN')
        self.assertEqual(kernel.state.accounts['screen:revenue:BUILD'].owner_id,
                         'Thales Alenia Space')
        self.assertEqual(kernel.state.accounts['screen:revenue:LAND'].owner_id, 'ispace')
        self.assertEqual(kernel.fingerprint(), run_yearly(selection='japan_lunar')[2].fingerprint())
        kernel.assert_invariants()

    def test_internal_delivery_is_only_flagged_for_japan_self_delivery(self):
        from .test_yearly_acceptance import OPTIONS
        _, _, japan, _ = run_yearly(selection='japan_lunar')
        flags = [event for event in japan.event_log
                 if event['kind'] == 'BUILD8_INTERNAL_DELIVERY']
        self.assertEqual(len(flags), 1)
        self.assertEqual({key: flags[0][key] for key in
                          ('year','project','category','sponsor','executor',
                           'transaction_id','amount')},
                         {'year':2030,'project':'ispace','category':'LAND',
                          'sponsor':'ispace','executor':'ispace',
                          'transaction_id':'tx-000056','amount':'0.450000'})
        for scenario, options in OPTIONS.items():
            with self.subTest(scenario=scenario):
                _, _, kernel, _ = run_yearly(**options)
                self.assertFalse([event for event in kernel.event_log
                                  if event['kind'] == 'BUILD8_INTERNAL_DELIVERY'])

    def test_invalid_cast_role_is_rejected(self):
        from .yearly_selections import SELECTIONS
        original = SELECTIONS['japan_lunar']
        try:
            SELECTIONS['japan_lunar'] = {**original, 'executors': {'BUILD':'NASA','LAND':'ispace'}}
            with self.assertRaises(ValueError):
                run_yearly(selection='japan_lunar')
        finally:
            SELECTIONS['japan_lunar'] = original

if __name__ == '__main__': unittest.main()
