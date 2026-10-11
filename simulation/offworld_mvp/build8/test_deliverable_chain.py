"""Build 8 noncanon executable deliverable-chain checks."""
import unittest
from decimal import Decimal as D
from .deliverable_chain import run_chain, BUILD_LAND, LAND_EXTRACT_TRANSPORT, Step, OPERATORS
from .opening import EARTH_V4_ROOT

@unittest.skipUnless(EARTH_V4_ROOT.exists(), 'Earth v4 baseline absent')
class DeliverableChainTests(unittest.TestCase):
    def test_success_and_two_failure_points(self):
        expected = [(['DELIVERED', 'DELIVERED'], {'PAYLOAD_ON_MOON'}, D('6.10')),
                    (['DELIVERED', 'FAILED'], set(), D('6.10')),
                    (['FAILED', 'BLOCKED_UPSTREAM'], set(), D('2.50'))]
        for failure, (statuses, final, spent) in zip((None, 'land', 'build'), expected):
            records, goods, kernel, occupied = run_chain(BUILD_LAND, failure)
            self.assertEqual([r.status for r in records], statuses)
            self.assertTrue(final.issubset(goods))
            self.assertEqual(sum((r.payment for r in records), D(0)), spent)
            self.assertEqual((records, goods, occupied),
                             (lambda r: (r[0], r[1], r[3]))(run_chain(BUILD_LAND, failure)))
            self.assertEqual(records[0].start_year, 2026)
            self.assertEqual(records[0].finish_year, 2028)
            if failure != 'build':
                self.assertEqual(records[1].start_year, 2028)
                self.assertEqual(records[1].finish_year, 2030)
            self.assertEqual(occupied[('BUILD', 2027)], 1)
            self.assertNotIn(('BUILD', 2028), occupied)
            self.assertEqual(len([e for e in kernel.event_log if e['kind'] == 'BUILD8_EXECUTOR_STEP']), 2)
            kernel.assert_invariants()

    def test_different_shape_same_engine(self):
        records, goods, _, occupied = run_chain(LAND_EXTRACT_TRANSPORT)
        self.assertEqual([r.category for r in records], ['LAND', 'EXTRACT', 'TRANSPORT'])
        self.assertEqual([r.status for r in records], ['DELIVERED'] * 3)
        self.assertIn('MATERIAL_TRANSPORTED', goods)
        self.assertEqual(records[-1].finish_year, 2032)
        self.assertEqual(occupied[('EXTRACT', 2029)], 1)

    def test_cannot_skip_dependency_or_double_identify(self):
        with self.assertRaisesRegex(ValueError, 'predecessor'):
            run_chain((BUILD_LAND[0], Step('land', 'LAND', 'WRONG', 'PAYLOAD_ON_MOON')))
        with self.assertRaisesRegex(ValueError, 'duplicate deliverable'):
            run_chain((BUILD_LAND[0], Step('land', 'LAND', 'PAYLOAD_BUILT', 'PAYLOAD_BUILT')))

    def test_six_categories_are_table_driven(self):
        self.assertEqual(set(OPERATORS), {'BUILD', 'LAUNCH', 'LAND', 'TRANSPORT', 'EXTRACT', 'RUN'})
        for category in OPERATORS:
            records, goods, _, _ = run_chain((Step('one', category, 'SPONSOR_COMMISSION', 'RESULT'),))
            self.assertEqual(records[0].status, 'DELIVERED')
            self.assertIn('RESULT', goods)

    def test_multiple_eligible_executors_with_single_selection_preserves_results(self):
        baseline = run_chain(BUILD_LAND)
        actual = run_chain(BUILD_LAND, eligible_executors={
            'BUILD': ('Northrop Grumman', 'CASC'),
            'LAND': ('Firefly Aerospace', 'Astrobotic'),
        })
        self.assertEqual(actual[0], baseline[0])
        self.assertEqual(actual[1], baseline[1])
        self.assertEqual(actual[3], baseline[3])
        self.assertEqual(actual[2].fingerprint(), baseline[2].fingerprint())

    def test_explicit_alternative_selection_and_invalid_choice(self):
        records, _, kernel, _ = run_chain(BUILD_LAND, eligible_executors={
            'BUILD': ('Northrop Grumman', 'CASC'),
            'LAND': ('Firefly Aerospace', 'Astrobotic'),
        }, selected_executors={'BUILD': 'CASC', 'LAND': 'Astrobotic'})
        self.assertEqual([r.executor for r in records], ['CASC', 'Astrobotic'])
        kernel.assert_invariants()
        with self.assertRaises(ValueError):
            run_chain(BUILD_LAND, eligible_executors={'BUILD': ('CASC',)},
                      selected_executors={'BUILD': 'Northrop Grumman'})
