"""Route 1 2026-only opt-in acceptance."""
import unittest
from decimal import Decimal as D
from .route1_gate1 import run_gate1, CEILINGS, DEFAULT_PRICE, EVIDENCE_TAG

class Gate1Acceptance(unittest.TestCase):
    def test_isro_b10_approved_service_funds_below_ceiling(self):
        rows,k=run_gate1(D('.10'),scenario='B')
        isro=next(r for r in rows if r['sponsor']=='ISRO')
        self.assertEqual((isro['policy'],isro['reason']),
                         ('APPROVE','APPROVED_POLICY_RULE'))
        self.assertLess(D(isro['opening']),D(isro['authored_ceiling']))
        self.assertGreaterEqual(D(isro['opening']),D(isro['authored_price']))
        self.assertLessEqual(D(isro['authored_price']),D(isro['authored_ceiling']))
        self.assertEqual(isro['status'],'FUNDED_PENDING_EXECUTOR')
        self.assertIsNotNone(isro['commitment'])
        self.assertIsNotNone(isro['disbursement'])
        self.assertEqual(D(isro['opening'])-D(isro['closing']),D('.085'))
        k.assert_invariants()

    def test_both_shares_conserved_replayed_and_authored(self):
        for scenario in ('A','B'):
          for share in (D('.10'),D('.25')):
            with self.subTest(scenario=scenario,share=str(share)):
                rows,k=run_gate1(share,scenario=scenario)
                rows2,k2=run_gate1(share,scenario=scenario)
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
                self.assertEqual(sum(e.get('kind')=='ROUTE1_DISCLOSED_OBSERVATION' for e in k.event_log),11 if scenario=='B' else 0)
                self.assertEqual(len(k.state.commitments),sum(bool(r['commitment']) for r in rows))
                self.assertEqual(sum(t.purpose.value=='DISBURSE' for t in k.state.transactions),sum(bool(r['disbursement']) for r in rows))
                self.assertTrue(all(D(r['opening'])-D(r['closing'])==
                    (D(r['authored_price']) if r['disbursement'] else D(0)) for r in rows))
                k.assert_invariants()

if __name__=='__main__':
    unittest.main()
