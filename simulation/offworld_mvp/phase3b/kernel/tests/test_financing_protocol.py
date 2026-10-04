import unittest
from decimal import Decimal as D

from offworld_kernel.financing_protocol import (
    FINANCING_PROTOCOL_VERSION,
    build_financing_decision,
    build_financing_request,
    required_unknown_inputs,
)
from offworld_kernel.mvp_state import (
    BUILD5_REQUIRED_UNDERWRITING_KEYS,
    BUILD5_REQUIRED_BELIEF_KEYS,
    BUILD5_REQUIRED_PRIOR_KEYS,
    FinancingDecisionOutcome,
    FinancingReasonCode,
)
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.underwriting import mvp_validation_underwriting_table, underwriting_snapshot_facts

class FinancingProtocolTests(unittest.TestCase):
    def request(self):
        return build_financing_request('REQ-1',1,'SPN','P',D('60'),'DEVELOPMENT',('OBS-1',))

    def snapshot(self, missing_underwriting=(), include_belief=True, include_prior=True):
        facts=list(underwriting_snapshot_facts(
            mvp_validation_underwriting_table(),'GENERIC_RESOURCE_PROJECT_MVP',1))
        facts=[f for f in facts if f.key not in set(missing_underwriting)]
        return DecisionSnapshot(
            agent_id='FIN',
            agent_kind='PRIVATE_FINANCIER',
            node_id='EARTH:X',
            period_key='1',
            effective_time='1',
            account_balance=D('100'),
            capabilities=('FINANCE',),
            objectives=('RETURN',),
            information_refs=('OBS-1',),
            beliefs=(('resource_exists',D('0.7')),) if include_belief else (),
            priors=(('resource_exists',D('0.2')),) if include_prior else (),
            asset_refs=(),
            resource_holdings=(),
            claim_holdings=(),
            admitted_facts=tuple(facts),
        )

    def test_request_requires_exact_decision_input_contract(self):
        q=self.request()
        self.assertEqual(q.required_underwriting_keys,BUILD5_REQUIRED_UNDERWRITING_KEYS)
        self.assertEqual(q.required_belief_keys,BUILD5_REQUIRED_BELIEF_KEYS)
        self.assertEqual(q.required_prior_keys,BUILD5_REQUIRED_PRIOR_KEYS)
        self.assertEqual(q.currency_unit,'MODEL_CURRENCY')
        self.assertEqual(q.request_version,'FINANCING_REQUEST_V1')

    def test_reason_code_register_contains_required_build5_controls(self):
        values={x.value for x in FinancingReasonCode}
        self.assertTrue({'CEILING','CONCENTRATION','BELOW_RETURN',
                         'BLOCKED_REQUIRED_INPUT_UNKNOWN'}.issubset(values))

    def test_approve_protocol(self):
        q=self.request(); snap=self.snapshot()
        d=build_financing_decision(
            'DEC-1',q,'FIN',FinancingDecisionOutcome.APPROVE,
            FinancingReasonCode.APPROVED_POLICY_RULE,'threshold met',
            snap,'FINANCIER_POLICY_V1',
            amount=D('50'),instrument='EQUITY')
        self.assertTrue(d.approved)
        self.assertEqual(d.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(d.amount,D('50'))
        self.assertEqual(d.unknown_input_keys,())

    def test_nonapprove_outcomes_cannot_fund_when_inputs_known(self):
        q=self.request(); snap=self.snapshot()
        for outcome,reason in (
            (FinancingDecisionOutcome.REJECT,FinancingReasonCode.BELOW_RETURN),
            (FinancingDecisionOutcome.DEFER,FinancingReasonCode.DEFER_MORE_INFORMATION)):
            with self.subTest(outcome=outcome):
                d=build_financing_decision(
                    'DEC-'+outcome.value,q,'FIN',outcome,reason,'not now',
                    snap,'FINANCIER_POLICY_V1')
                self.assertFalse(d.approved); self.assertEqual(d.amount,D('0'))

    def test_required_unknown_underwriting_forces_blocked_unknown(self):
        q=self.request(); snap=self.snapshot(missing_underwriting=('underwriting.OPERATING_COST',))
        self.assertEqual(required_unknown_inputs(q,snap),('underwriting.OPERATING_COST',))
        d=build_financing_decision(
            'DEC-U',q,'FIN',FinancingDecisionOutcome.BLOCKED_UNKNOWN,
            FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,'opex unavailable',
            snap,'FINANCIER_POLICY_V1')
        self.assertFalse(d.approved)
        self.assertEqual(d.outcome,FinancingDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(d.unknown_input_keys,('underwriting.OPERATING_COST',))

    def test_unknown_belief_forces_blocked_unknown(self):
        q=self.request(); snap=self.snapshot(include_belief=False)
        self.assertEqual(required_unknown_inputs(q,snap),('belief.resource_exists',))
        with self.assertRaisesRegex(ValueError,'must produce BLOCKED_UNKNOWN'):
            build_financing_decision(
                'DEC-X',q,'FIN',FinancingDecisionOutcome.REJECT,
                FinancingReasonCode.BELOW_RETURN,'reject',
                snap,'FINANCIER_POLICY_V1')
        d=build_financing_decision(
            'DEC-B',q,'FIN',FinancingDecisionOutcome.BLOCKED_UNKNOWN,
            FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,'belief unavailable',
            snap,'FINANCIER_POLICY_V1')
        self.assertEqual(d.unknown_input_keys,('belief.resource_exists',))

    def test_unknown_prior_forces_blocked_unknown(self):
        q=self.request(); snap=self.snapshot(include_prior=False)
        self.assertEqual(required_unknown_inputs(q,snap),('prior.resource_exists',))
        d=build_financing_decision(
            'DEC-P',q,'FIN',FinancingDecisionOutcome.BLOCKED_UNKNOWN,
            FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,'prior unavailable',
            snap,'FINANCIER_POLICY_V1')
        self.assertEqual(d.unknown_input_keys,('prior.resource_exists',))

    def test_blocked_unknown_not_allowed_when_dependencies_known(self):
        q=self.request(); snap=self.snapshot()
        with self.assertRaisesRegex(ValueError,'not allowed when all required decision inputs are known'):
            build_financing_decision(
                'DEC-X',q,'FIN',FinancingDecisionOutcome.BLOCKED_UNKNOWN,
                FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,'no reason',
                snap,'FINANCIER_POLICY_V1')

    def test_approval_cannot_exceed_request(self):
        q=self.request(); snap=self.snapshot()
        with self.assertRaisesRegex(ValueError,'exceeds request'):
            build_financing_decision(
                'DEC-X',q,'FIN',FinancingDecisionOutcome.APPROVE,
                FinancingReasonCode.APPROVED_POLICY_RULE,'approve',
                snap,'FINANCIER_POLICY_V1',
                amount=D('61'),instrument='EQUITY')

if __name__=='__main__':
    unittest.main()
