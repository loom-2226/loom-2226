"""Opt-in result-triggered, not result-priced; RECONSTRUCTION, NOT CONTINUATION."""
import unittest
from decimal import Decimal as D
from .nasa_moon_a2 import run

class NasaMoonA2Test(unittest.TestCase):
    def test_two_carry_settings_and_replay(self):
        for cap in (None,1):
            rows,earth,a1,a2,decision,evidence=run(cap)
            rows2,earth2,a1b,a2b,decision2,evidence2=run(cap)
            self.assertEqual(rows,rows2)
            self.assertEqual((earth.fingerprint(),a1.fingerprint(),a2.fingerprint()),
                             (earth2.fingerprint(),a1b.fingerprint(),a2b.fingerprint()))
            self.assertEqual(decision['policy'],'APPROVE')
            self.assertEqual(decision['reason'],'APPROVED_POLICY_RULE')
            self.assertEqual(D(decision['available'])-D(decision['closing']),D('.300'))
            nasa=[r for r in rows if r['sponsor']=='NASA']
            self.assertEqual(len([r for r in nasa if r['disbursement']]),2)
            self.assertEqual([r['year'] for r in nasa if r['disbursement']],[2026,2029])
            self.assertEqual(D(nasa[0]['authored_price']),D('.350'))
            self.assertEqual(next(r for r in nasa if r['year']==2030)['reason'],'ALREADY_PURCHASED')
            self.assertEqual(evidence['standing'],'SUPPORTS_ADVANCE')
            self.assertEqual(evidence['review_at'],'2029.02')
            self.assertEqual(set(a1.project_activities),{'MOON-A1-SURFACE'})
            self.assertEqual(set(a2.project_activities),{'MOON-A2-ASSESS'})
            self.assertEqual(sum(r.amount for r in a1.project_activity_expense_records),D(35))
            self.assertEqual(sum(r.amount for r in a2.project_activity_expense_records),D(30))
            self.assertEqual(a1.project_study_result_records[0].standing.value,'SUPPORTS_ADVANCE')
            self.assertEqual(a2.project_study_result_records[0].standing.value,'INSUFFICIENT')
            self.assertEqual(a2.project_activities['MOON-A2-ASSESS'].actual_completion,D('2030.60'))
            self.assertEqual(a2.event_log[0]['kind'],'RECONSTRUCTION, NOT CONTINUATION')
            self.assertEqual(a2.event_log[0]['funding_transaction'],decision['disbursement'])
            self.assertEqual(a2.event_log[0]['a1_result_ref'],evidence['result_ref'])
            self.assertEqual(a2.event_log[0]['a1_fingerprint'],a1.fingerprint())
            self.assertEqual(a2.state.accounts['sponsor_funds'].balance,D(0))
            self.assertEqual(sum(r.amount for r in a1.project_activity_expense_records)+
                             sum(r.amount for r in a2.project_activity_expense_records),D(65))
            a1.assert_methodology_invariants();a2.assert_methodology_invariants()
