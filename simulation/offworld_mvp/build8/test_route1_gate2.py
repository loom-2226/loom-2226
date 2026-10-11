"""Gate 2 2027-2029 opt-in continuation regression."""
import unittest
from decimal import Decimal as D
from .route1_gate2 import run_gate2
from .route1_gate1 import run_gate1, CEILINGS

class Gate2Acceptance(unittest.TestCase):
    def test_four_year_ledger_and_no_repeat_service(self):
        for share in (D('.10'),D('.25')):
            with self.subTest(share=share):
                rows,k=run_gate2(share)
                again,k2=run_gate2(share)
                self.assertEqual(rows,again)
                self.assertEqual(k.fingerprint(),k2.fingerprint())
                self.assertEqual(len(rows),44)
                baseline,_=run_gate1(share,scenario='B')
                self.assertEqual([(r['sponsor'],r['policy'],r['reason'],r['status'],
                                   r['opening'],r['closing']) for r in rows if r['year']==2026],
                                 [(r['sponsor'],r['policy'],r['reason'],r['status'],
                                   r['opening'],r['closing']) for r in baseline])
                for sponsor in CEILINGS:
                    entries=[r for r in rows if r['sponsor']==sponsor]
                    self.assertEqual(sum(bool(r['disbursement']) for r in entries),
                                     min(1,sum(bool(r['commitment']) for r in entries)))
                    self.assertEqual(sum(bool(r['disbursement']) for r in entries),
                                     sum(bool(r['commitment']) for r in entries))
                    for i,r in enumerate(entries):
                        if i:
                            self.assertEqual(D(r['opening']),D(entries[i-1]['closing']))
                        self.assertLessEqual(abs(
                            D(r['closing'])-D(r['opening'])-
                            D(r.get('allocated','0'))+
                            (D(r['authored_price']) if r['disbursement'] else D(0))),D('1e-24'))
                    if any(r['disbursement'] for r in entries):
                        year=next(r['year'] for r in entries if r['disbursement'])
                        self.assertTrue(all(r['reason']=='ALREADY_PURCHASED'
                                            for r in entries if r['year']>year))
                self.assertEqual({r['year'] for r in rows},{2026,2027,2028,2029})
                k.assert_invariants()

if __name__=='__main__':
    unittest.main()
