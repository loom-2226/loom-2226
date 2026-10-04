import unittest
from dataclasses import replace
from types import SimpleNamespace
from decimal import Decimal as D

from offworld_kernel.build5_fixture import (
    financing_request,
    snapshot_from_signal,
    standalone_snapshot,
    synthetic_policy_manifest,
)
from offworld_kernel.mvp_state import FinancingDecisionOutcome, FinancingReasonCode
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.policy_validation import (
    adequacy_from_pairs,
    ensemble_report,
    perturbed_manifest,
    rank,
)

class Build5FinancierBehaviorTests(unittest.TestCase):
    def run_policy(self,snapshot,request=None,manifest=None,key='K'):
        return run_financier_policy(
            snapshot,
            request or financing_request(),
            manifest or synthetic_policy_manifest(),
            key,
            allow_test_fixture=True).decision

    def test_favorable_observation_raises_belief_and_changes_decision(self):
        positive,pos_id=snapshot_from_signal('POSITIVE')
        negative,neg_id=snapshot_from_signal('NEGATIVE')
        self.assertGreater(dict(positive.beliefs)['resource_exists'],
                           dict(negative.beliefs)['resource_exists'])
        pos=self.run_policy(positive,financing_request(observations=(pos_id,)))
        neg=self.run_policy(negative,financing_request(observations=(neg_id,)))
        self.assertEqual(pos.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(neg.outcome,FinancingDecisionOutcome.REJECT)
        self.assertTrue(adequacy_from_pairs((('observation',neg,pos),)).passed)

    def test_price_capex_and_opex_metamorphic_monotonicity(self):
        base='0.12'
        price_bad=self.run_policy(standalone_snapshot(belief=base,price='15'))
        price_good=self.run_policy(standalone_snapshot(belief=base,price='25'))
        capex_bad=self.run_policy(standalone_snapshot(belief=base,development='100'))
        capex_good=self.run_policy(standalone_snapshot(belief=base,development='30'))
        opex_bad=self.run_policy(standalone_snapshot(belief=base,opex='10'))
        opex_good=self.run_policy(standalone_snapshot(belief=base,opex='2'))
        report=adequacy_from_pairs((
            ('higher_price',price_bad,price_good),
            ('lower_capex',capex_bad,capex_good),
            ('lower_opex',opex_bad,opex_good),
        ))
        self.assertTrue(report.weak_monotonicity_passed)
        self.assertTrue(report.discrimination_passed)
        for worse,better in ((price_bad,price_good),(capex_bad,capex_good),(opex_bad,opex_good)):
            self.assertLessEqual(rank(worse.outcome),rank(better.outcome))

    def test_constant_policy_negative_controls_fail_behavioral_adequacy(self):
        approve=SimpleNamespace(outcome=FinancingDecisionOutcome.APPROVE)
        reject=SimpleNamespace(outcome=FinancingDecisionOutcome.REJECT)
        self.assertFalse(adequacy_from_pairs((('x',approve,approve),)).passed)
        self.assertFalse(adequacy_from_pairs((('x',reject,reject),)).passed)

    def test_reason_code_branches(self):
        ceiling=self.run_policy(standalone_snapshot(),financing_request(amount='110'))
        self.assertEqual(ceiling.reason_code,FinancingReasonCode.CEILING)

        concentration=self.run_policy(standalone_snapshot(),financing_request(amount='90'))
        self.assertEqual(concentration.reason_code,FinancingReasonCode.CONCENTRATION)

        deferred=self.run_policy(
            standalone_snapshot(observations=()),
            financing_request(observations=()))
        self.assertEqual(deferred.outcome,FinancingDecisionOutcome.DEFER)
        self.assertEqual(deferred.reason_code,FinancingReasonCode.DEFER_MORE_INFORMATION)

        below=self.run_policy(standalone_snapshot(belief='0.05'))
        self.assertEqual(below.reason_code,FinancingReasonCode.BELOW_RETURN)

    def test_parameter_ensemble_reports_blocked_and_flip_shares(self):
        base_manifest=synthetic_policy_manifest()
        high_hurdle=perturbed_manifest(base_manifest,'hurdle_rate',1)

        near=standalone_snapshot(belief='0.11')
        robust=standalone_snapshot(belief='0.50')
        blocked=replace(standalone_snapshot(belief='0.50'),priors=())

        near_base=self.run_policy(near,manifest=base_manifest)
        robust_base=self.run_policy(robust,manifest=base_manifest)
        blocked_base=self.run_policy(blocked,manifest=base_manifest)
        near_pert=self.run_policy(near,manifest=high_hurdle)
        robust_pert=self.run_policy(robust,manifest=high_hurdle)

        self.assertNotEqual(near_base.outcome,near_pert.outcome)
        self.assertEqual(robust_base.outcome,robust_pert.outcome)

        report=ensemble_report(
            (near_base,robust_base,blocked_base),
            {'hurdle_rate':((near_base,near_pert),(robust_base,robust_pert))})
        self.assertEqual(report.total_requests,3)
        self.assertEqual(report.blocked_requests,1)
        self.assertEqual(report.comparable_pairs,2)
        self.assertEqual(report.decision_flips,1)
        self.assertEqual(report.decision_flip_share,D('0.5'))
        self.assertEqual(dict(report.flip_share_by_parameter)['hurdle_rate'],'0.5')

if __name__=='__main__':
    unittest.main()
