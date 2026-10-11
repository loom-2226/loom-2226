"""Two projects, one capital pool, shared executor slots, stable allocation."""
import unittest
from decimal import Decimal as D
from .competitive_delivery import run_competition, ProjectBid, SCALE
from .opening import EARTH_V4_ROOT

@unittest.skipUnless(EARTH_V4_ROOT.exists(), 'Earth v4 unavailable')
class CompetitiveDeliveryTests(unittest.TestCase):
    def test_shared_world_competition_is_order_independent(self):
        bids = (ProjectBid('A', 'A'), ProjectBid('B', 'B'))
        rows, k, capacity = run_competition(bids)
        shuffled, other, other_capacity = run_competition(tuple(reversed(bids)))
        self.assertEqual(rows, shuffled)
        self.assertEqual(capacity, other_capacity)
        self.assertEqual(k.fingerprint(), other.fingerprint())
        self.assertEqual([(r.project,r.category,r.start,r.finish) for r in rows],
                         [('A','BUILD',2026,2028),('A','LAND',2028,2030),
                          ('B','BUILD',2028,2030),('B','LAND',2030,2032)])
        self.assertTrue(all(r.outcome == 'DELIVERED' for r in rows))
        self.assertEqual(sum((r.revenue for r in rows), D(0)), D('3.05'))
        self.assertEqual(sum((r.cost for r in rows), D(0)), D('2.50'))
        self.assertEqual(sum((r.profit for r in rows), D(0)), D('.55'))
        self.assertEqual(k.state.accounts['comp:executor:BUILD'].balance, D('.25'))
        self.assertEqual(k.state.accounts['comp:executor:LAND'].balance, D('.30'))
        self.assertEqual(k.state.accounts['comp:cash:A'].balance, 0)
        self.assertEqual(k.state.accounts['comp:cash:B'].balance, 0)
        self.assertEqual(k.state.projects['comp:project:A'].status, 'DEVELOPMENT')
        self.assertEqual(k.state.projects['comp:project:B'].status, 'DEVELOPMENT')
        k.assert_invariants()

    def test_failed_build_blocks_landing_and_does_not_reserve_slot(self):
        rows, k, capacity = run_competition(failure=('A','BUILD'))
        a = [r for r in rows if r.project == 'A']
        self.assertEqual([r.outcome for r in a], ['FAILED','BLOCKED_UPSTREAM'])
        self.assertEqual(a[1].revenue, 0)
        self.assertFalse(any(r.produced == 'ON_MOON:A' for r in rows))
        self.assertTrue(any(r.produced == 'ON_MOON:B' for r in rows))
        self.assertEqual(k.state.accounts['comp:cash:A'].balance, D('.90'))
        k.assert_invariants()

    def test_failed_landing_creates_no_delivered_asset(self):
        rows, k, _ = run_competition(failure=('A','LAND'))
        self.assertEqual(next(r.outcome for r in rows if r.project == 'A' and r.category == 'LAND'), 'FAILED')
        self.assertFalse(any(r.produced == 'ON_MOON:A' for r in rows))
        self.assertEqual(k.state.accounts['comp:cash:A'].balance, 0)
        k.assert_invariants()
