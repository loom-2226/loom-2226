"""Route 1 2026-only opt-in acceptance."""
import unittest
from decimal import Decimal as D
from .route1_gate1 import run_gate1, CEILINGS, DEFAULT_PRICE, EVIDENCE_TAG

class Gate1Acceptance(unittest.TestCase):
    def test_both_shares_conserved_replayed_and_authored(self):
        for share in (D('.10'),D('.25')):
            with self.subTest(share=str(share)):
                rows,k=run_gate1(share)
                rows2,k2=run_gate1(share)
                self.assertEqual(rows,rows2)
                self.assertEqual(k.fingerprint(),k2.fingerprint())
                self.assertEqual(len(rows),11)
                self.assertEqual(set(r['sponsor'] for r in rows),set(CEILINGS))
                self.assertTrue(all(r['authored_price'] == str(DEFAULT_PRICE[r['category']]) for r in rows))
                self.assertTrue(all(r['status'].startswith(('WAIT_','FUNDED_')) for r in rows))
                self.assertTrue(all(r['status']=='WAIT_CEILING_BELOW_PRICE'
                    for r in rows if D(r['authored_ceiling'])<D(r['authored_price'])))
                self.assertEqual(sum(bool(r['commitment']) for r in rows),
                                 sum(bool(r['disbursement']) for r in rows))
                self.assertTrue(all(t.year==2026 for t in k.state.transactions
                                    if t.source_account.startswith('route1:') or
                                    t.destination_account.startswith('route1:')))
                self.assertEqual(sum(e.get('kind')=='ROUTE1_AUTHORED_EVIDENCE' and e.get('label')==EVIDENCE_TAG for e in k.event_log),11)
                self.assertEqual(sum(e.get('kind')=='ROUTE1_FINANCIER_DECISION' for e in k.event_log),11)
                self.assertEqual(sum(e.get('kind')=='ROUTE1_GATE1_SETTLEMENT' for e in k.event_log),1)
                k.assert_invariants()

if __name__=='__main__':
    unittest.main()
