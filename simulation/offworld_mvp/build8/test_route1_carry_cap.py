"""Optional Route 1 carry-cap experiment, 2026-2029."""
import unittest
from decimal import Decimal as D
from .route1_gate2 import run_gate2
from .route1_gate1 import DEFAULT_PRICE, PROJECTS

class CarryCapTest(unittest.TestCase):
    def test_caps_and_control(self):
        for share in (D('.10'),D('.25')):
            control,k0=run_gate2(share)
            again,k1=run_gate2(share,carry_cap=None)
            self.assertEqual(control,again)
            self.assertEqual(k0.fingerprint(),k1.fingerprint())
            for cap in (0,1,2):
                with self.subTest(share=share,cap=cap):
                    rows,k=run_gate2(share,carry_cap=cap)
                    self.assertEqual(len(rows),44)
                    self.assertEqual({r['year'] for r in rows},
                                     {2026,2027,2028,2029})
                    for r in rows:
                        pre=D(r['cash_before_lapse'])
                        lapsed=D(r['lapsed_amount'])
                        post=D(r['cash_after_lapse'])
                        self.assertLessEqual(abs(pre-lapsed-post),D('1e-24'))
                        self.assertLessEqual(post,cap*DEFAULT_PRICE[PROJECTS[r['sponsor']][1]])
                    sink=k.state.accounts['route1:earth:carry_lapse'].balance
                    self.assertLessEqual(abs(sink-sum(
                        (D(r['lapsed_amount']) for r in rows),D(0))),D('1e-24'))
                    self.assertEqual(len({r['sponsor'] for r in rows if r['disbursement']}),
                                     sum(bool(r['disbursement']) for r in rows))
                    k.assert_invariants()
