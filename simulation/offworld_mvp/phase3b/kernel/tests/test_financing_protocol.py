import unittest
from decimal import Decimal as D

from offworld_kernel.financing_protocol import (
    FINANCING_PROTOCOL_VERSION,
    build_financing_decision,
    build_financing_request,
)
from offworld_kernel.mvp_state import (
    BUILD5_REQUIRED_UNDERWRITING_KEYS,
    FinancingDecisionOutcome,
    FinancingReasonCode,
)

class FinancingProtocolTests(unittest.TestCase):
    def request(self):
        return build_financing_request('REQ-1',1,'SPN','P',D('60'),'DEVELOPMENT',('OBS-1',))

    def test_request_requires_exact_underwriting_contract(self):
        q=self.request()
        self.assertEqual(q.required_underwriting_keys,BUILD5_REQUIRED_UNDERWRITING_KEYS)
        self.assertEqual(q.currency_unit,'MODEL_CURRENCY')
        self.assertEqual(q.request_version,'FINANCING_REQUEST_V1')

    def test_approve_protocol(self):
        q=self.request()
        d=build_financing_decision(
            'DEC-1',q,'FIN',FinancingDecisionOutcome.APPROVE,
            FinancingReasonCode.APPROVED_POLICY_RULE,'threshold met',
            'decision-snapshot:1:abc','FINANCIER_POLICY_V1',
            amount=D('50'),instrument='EQUITY')
        self.assertTrue(d.approved)
        self.assertEqual(d.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(d.amount,D('50'))

    def test_nonapprove_outcomes_cannot_fund(self):
        q=self.request()
        for outcome,reason in (
            (FinancingDecisionOutcome.REJECT,FinancingReasonCode.REJECTED_RETURN),
            (FinancingDecisionOutcome.DEFER,FinancingReasonCode.DEFER_MORE_INFORMATION)):
            with self.subTest(outcome=outcome):
                d=build_financing_decision(
                    'DEC-'+outcome.value,q,'FIN',outcome,reason,'not now',
                    'decision-snapshot:1:abc','FINANCIER_POLICY_V1')
                self.assertFalse(d.approved); self.assertEqual(d.amount,D('0'))

    def test_required_unknown_inputs_force_blocked_unknown(self):
        q=self.request()
        d=build_financing_decision(
            'DEC-U',q,'FIN',FinancingDecisionOutcome.BLOCKED_UNKNOWN,
            FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,'opex unavailable',
            'decision-snapshot:1:abc','FINANCIER_POLICY_V1',
            unknown_input_keys=('underwriting.OPERATING_COST',))
        self.assertFalse(d.approved)
        self.assertEqual(d.outcome,FinancingDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(d.reason_code,FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN)

    def test_unknown_keys_cannot_hide_under_reject_or_defer(self):
        q=self.request()
        with self.assertRaisesRegex(ValueError,'must produce BLOCKED_UNKNOWN'):
            build_financing_decision(
                'DEC-X',q,'FIN',FinancingDecisionOutcome.REJECT,
                FinancingReasonCode.REJECTED_RETURN,'reject',
                'decision-snapshot:1:abc','FINANCIER_POLICY_V1',
                unknown_input_keys=('underwriting.PRICE',))

    def test_approval_cannot_exceed_request(self):
        q=self.request()
        with self.assertRaisesRegex(ValueError,'exceeds request'):
            build_financing_decision(
                'DEC-X',q,'FIN',FinancingDecisionOutcome.APPROVE,
                FinancingReasonCode.APPROVED_POLICY_RULE,'approve',
                'decision-snapshot:1:abc','FINANCIER_POLICY_V1',
                amount=D('61'),instrument='EQUITY')

if __name__=='__main__':
    unittest.main()
