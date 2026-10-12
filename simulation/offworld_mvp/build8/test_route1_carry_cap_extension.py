"""2035 bounded continuation; existing 2029 control remains identical."""
import unittest
from decimal import Decimal as D
from .route1_gate2 import run_gate2

class CarryCapExtension(unittest.TestCase):
    def test_bounded_extension(self):
        for share in (D('.10'),D('.25')):
            for cap in (None,0,1,2):
                with self.subTest(share=share,cap=cap):
                    original,k0=run_gate2(share,carry_cap=cap)
                    rows,k=run_gate2(share,carry_cap=cap,end_year=2035)
                    self.assertEqual(rows[:44],original)
                    self.assertEqual(len(rows),110)
                    self.assertEqual({r['year'] for r in rows},set(range(2026,2036)))
                    self.assertEqual(sum(bool(r['disbursement']) for r in rows),
                                     len({r['sponsor'] for r in rows if r['disbursement']}))
                    if cap is not None:
                        self.assertLessEqual(abs(sum((D(r['lapsed_amount']) for r in rows),D(0))-
                                                 k.state.accounts['route1:earth:carry_lapse'].balance),D('1e-24'))
                    k.assert_invariants()
        with self.assertRaises(ValueError):
            run_gate2(end_year=2036)
