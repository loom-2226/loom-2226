"""Build 8 screened funding, deterministic queue, and physical handoffs."""
import unittest
from decimal import Decimal as D
from .screened_delivery import run_screened, SPONSORS
from .opening import EARTH_V4_ROOT

@unittest.skipUnless(EARTH_V4_ROOT.exists(), 'Earth v4 missing')
class ScreenedDeliveryTests(unittest.TestCase):
    def test_policy_rank_defer_retry_and_shuffled_inputs(self):
        rows, decisions, k, capacity = run_screened()
        shuffled, other_decisions, other, other_capacity = run_screened(tuple(reversed(SPONSORS)))
        self.assertEqual((rows,decisions,capacity),(shuffled,other_decisions,other_capacity))
        self.assertEqual(k.fingerprint(),other.fingerprint())
        self.assertEqual([(d[0],d[1],d[2],d[4]) for d in decisions],
            [('Interlune','INITIATE_PROJECT','APPROVE',2026),
             ('Axiom','INITIATE_PROJECT','APPROVE',2027)])
        self.assertGreater(D(decisions[0][3]),D(decisions[1][3]))
        self.assertEqual([(r.project,r.category,r.start,r.finish) for r in rows],
            [('Interlune','BUILD',2026,2028),('Interlune','LAND',2028,2030),
             ('Axiom','BUILD',2028,2030),('Axiom','LAND',2030,2032)])
        self.assertTrue(all(r.outcome=='DELIVERED' for r in rows))
        self.assertEqual(sum((r.revenue for r in rows),D(0)),D('3.05'))
        self.assertEqual(sum((r.cost for r in rows),D(0)),D('2.50'))
        self.assertEqual(sum((r.profit for r in rows),D(0)),D('.55'))
        self.assertEqual(k.state.accounts['screen:revenue:BUILD'].balance,D('.25'))
        self.assertEqual(k.state.accounts['screen:revenue:LAND'].balance,D('.30'))
        self.assertEqual(len(k.financing_decisions),2)
        k.assert_invariants()

    def test_failed_build_blocks_landing_and_preserves_cash(self):
        rows,_,k,_=run_screened(failure=('Interlune','BUILD'))
        first=[r for r in rows if r.project=='Interlune']
        self.assertEqual([r.outcome for r in first],['FAILED','BLOCKED_UPSTREAM'])
        self.assertFalse(any(r.produced=='ON_MOON:Interlune' for r in rows))
        self.assertEqual(k.state.accounts['screen:cash:Interlune'].balance,D('.90'))
        k.assert_invariants()

    def test_failed_landing_is_not_delivery(self):
        rows,_,k,_=run_screened(failure=('Interlune','LAND'))
        self.assertEqual(next(r.outcome for r in rows if r.project=='Interlune' and r.category=='LAND'),'FAILED')
        self.assertFalse(any(r.produced=='ON_MOON:Interlune' for r in rows))
        k.assert_invariants()
