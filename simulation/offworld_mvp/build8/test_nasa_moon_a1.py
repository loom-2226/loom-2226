"""Experimental NASA-to-Moon A1 handoff checks; frozen 6C unchanged."""
import unittest
from decimal import Decimal as D
from .nasa_moon_a1 import run, LABEL
from .route1_gate1 import run_gate1

class NasaMoonA1Test(unittest.TestCase):
    def test_conserved_handoff_and_replay(self):
        nasa,earth,k=run()
        nasa2,earth2,k2=run()
        self.assertEqual(nasa,nasa2)
        self.assertEqual(earth.fingerprint(),earth2.fingerprint())
        self.assertEqual(k.fingerprint(),k2.fingerprint())
        self.assertEqual(nasa['policy'],'APPROVE')
        self.assertEqual(nasa['reason'],'APPROVED_POLICY_RULE')
        self.assertEqual(D(nasa['opening'])-D(nasa['closing']),D('.350'))
        self.assertEqual(set(k.project_activities),{'MOON-A1-SURFACE'})
        self.assertEqual(sum((r.amount for r in k.project_activity_expense_records),D(0)),D(35))
        a=k.project_activities['MOON-A1-SURFACE']
        self.assertEqual(a.authorized_at,D('2026.25'))
        self.assertEqual(a.actual_start,D('2027.50'))
        self.assertEqual(a.actual_completion,D('2029.00'))
        self.assertEqual(k.state.accounts['study_supplier'].balance,D(35))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D(0))
        self.assertEqual(len(k.project_activity_information_records),1)
        self.assertEqual(k.project_activity_information_records[0].admitted_at,D('2029.01'))
        self.assertEqual(len(k.project_study_review_records),1)
        self.assertNotIn('MOON-A2-ASSESS',k.project_activities)
        k.assert_methodology_invariants()
        baseline,_=run_gate1(D('.25'),scenario='B')
        self.assertEqual(D(next(x for x in baseline if x['sponsor']=='NASA')['authored_price']),D('.150'))

if __name__=='__main__': unittest.main()
