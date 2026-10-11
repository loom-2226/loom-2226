"""Cast eligibility is required even when the authored subcontract changes."""
import unittest
from unittest.mock import patch
from .screened_delivery import eligible_subcontract_parties, run_screened
from decimal import Decimal as D


class CastSubcontractSelectionTests(unittest.TestCase):
    def test_existing_prime_and_sub(self):
        self.assertEqual(eligible_subcontract_parties(), ('Northrop Grumman', 'Firefly Aerospace'))

    def test_other_cast_eligible_pair(self):
        with patch('simulation.offworld_mvp.build8.screened_delivery.OPERATORS', {
            'BUILD': ('CASC', 1, 0, 1, 1), 'LAND': ('Astrobotic', 1, 0, 1, 1)
        }):
            self.assertEqual(eligible_subcontract_parties(), ('CASC', 'Astrobotic'))

    def test_ineligible_subcontractor_rejected(self):
        with patch('simulation.offworld_mvp.build8.screened_delivery.OPERATORS', {
            'BUILD': ('Northrop Grumman', 1, 0, 1, 1),
            'LAND': ('Northrop Grumman', 1, 0, 1, 1)
        }):
            with self.assertRaises(ValueError):
                eligible_subcontract_parties()


class AlternateSubcontractFullRunTests(unittest.TestCase):
    """Authored alternative names only; all original money and slot numbers."""
    def run_alternate(self, failed=False, recovered=False):
        return run_screened(subcontract=True, capacity_slots=1,
            sub_failure=failed, resource_on_failure=recovered,
            operator_selection={'BUILD': 'CASC', 'LAND': 'Astrobotic'})

    def test_alternate_success_money_slots_and_private_knowledge(self):
        work, decisions, k, slots = self.run_alternate()
        k.assert_invariants()
        self.assertTrue(all(v <= 1 for v in slots.values()))
        self.assertEqual([w.outcome for w in work], ['DELIVERED'] * 4)
        self.assertEqual([w.revenue for w in work], [D('.625'), D('.625'), D('.9'), D('.9')])
        self.assertEqual([w.cost for w in work], [D('.5'), D('.5'), D('.75'), D('.75')])
        # A sub consumes a LAND slot, so the LAND delivery starts after the
        # sub's reservation instead of overlapping it.
        self.assertEqual(work[2].start, 2029)
        self.assertEqual(work[3].start, 2031)
        self.assertTrue(all(w.profit == w.revenue - w.cost for w in work))
        self.assertEqual(str(k.state.accounts['b8_source:USA'].balance), '-10.020169202983437')  # Existing mobilization source, unchanged from baseline
        knowledge = k.build8_knowledge
        subfacts = [x for x in knowledge if 'subcontract:' in str(x)]
        self.assertEqual(len(subfacts), 4)
        self.assertEqual({x[2] for x in subfacts}, {'CASC', 'Astrobotic'})
        self.assertTrue(all(x[3] == 'DIRECT_CONTRACT' for x in subfacts))
        self.assertFalse(any(x[2] in {'Interlune','Axiom'} for x in subfacts))
        payments = [e for e in k.event_log if e['kind'] == 'BUILD8_SUB_PAYMENT']
        self.assertEqual(len(payments), 2)
        self.assertTrue(all(D(e['amount']) == D('.20') and D(e['withheld']) == 0 for e in payments))

    def test_alternate_failure_propagates_and_holds_back(self):
        work, decisions, k, slots = self.run_alternate(failed=True)
        k.assert_invariants()
        self.assertEqual([w.outcome for w in work],
                         ['FAILED', 'BLOCKED_UPSTREAM', 'FAILED', 'BLOCKED_UPSTREAM'])
        self.assertTrue(all(v <= 1 for v in slots.values()))
        payments = [e for e in k.event_log if e['kind'] == 'BUILD8_SUB_PAYMENT']
        self.assertEqual(len(payments), 2)
        self.assertTrue(all(D(e['quoted']) == D('.20') and D(e['amount']) == D('.18')
                            and D(e['withheld']) == D('.02') for e in payments))
        self.assertEqual(str(k.state.accounts['b8_source:USA'].balance), '-10.020169202983437')  # Existing mobilization source, unchanged from baseline

    def test_alternate_recovery_does_not_accelerate_prime(self):
        work, decisions, k, slots = self.run_alternate(failed=True, recovered=True)
        k.assert_invariants()
        self.assertTrue(all(w.outcome == 'DELIVERED' for w in work))
        self.assertEqual(work[0].finish, 2029)
        self.assertEqual(work[1].finish, 2032)
        self.assertTrue(all(v <= 1 for v in slots.values()))
