import unittest
from dataclasses import replace

from offworld_kernel.build5_fixture import financing_request, standalone_snapshot, synthetic_policy_manifest
from offworld_kernel.mvp_state import FinancingDecisionOutcome
from offworld_kernel.policy_runner import (
    assert_policy_source_safe,
    run_financier_policy,
    run_hostile_access_probe,
)

class Build5PolicyRunnerTests(unittest.TestCase):
    def test_supported_runner_blocks_hostile_access_clock_io_environment_and_hidden_state(self):
        snap=standalone_snapshot()
        result,fp=run_hostile_access_probe(snap)
        leaks={k:v for k,v in result.items() if v=='LEAK'}
        self.assertEqual(leaks,{})
        self.assertTrue(fp)
        for key in (
            'filesystem','network','wall_clock','system_random','environment',
            'input:world_seed','input:hidden_state','input:kernel','input:scheduler','input:resources'):
            self.assertEqual(result[key],'BLOCKED')

    def test_static_policy_source_gate_rejects_forbidden_import_and_io(self):
        with self.assertRaisesRegex(ValueError,'forbidden policy import'):
            assert_policy_source_safe(b'import os\ndef evaluate(): return os.environ\n')
        with self.assertRaisesRegex(ValueError,'forbidden policy call'):
            assert_policy_source_safe(b'def evaluate(): return open("x")\n')

    def test_identical_serialized_inputs_replay_identical_decision(self):
        snap=standalone_snapshot()
        q=financing_request()
        m=synthetic_policy_manifest()
        a=run_financier_policy(snap,q,m,'K',allow_test_fixture=True)
        b=run_financier_policy(snap,q,m,'K',allow_test_fixture=True)
        self.assertEqual(a.decision,b.decision)
        self.assertEqual(a.policy_version,b.policy_version)
        self.assertEqual(a.parameter_manifest_hash,b.parameter_manifest_hash)
        self.assertEqual(a.worker_fingerprint,b.worker_fingerprint)

    def test_hidden_world_labels_cannot_change_decision_when_snapshot_is_identical(self):
        snap=standalone_snapshot()
        q=financing_request()
        m=synthetic_policy_manifest()
        decisions={}
        for hidden_world in ('NULL','SPARSE','RICH'):
            decisions[hidden_world]=run_financier_policy(
                snap,q,m,'SAME-KEY',allow_test_fixture=True).decision
        self.assertEqual(decisions['NULL'],decisions['SPARSE'])
        self.assertEqual(decisions['SPARSE'],decisions['RICH'])

    def test_missing_belief_and_prior_force_blocked_unknown_without_worker(self):
        q=financing_request()
        m=synthetic_policy_manifest()
        no_belief=replace(standalone_snapshot(),beliefs=())
        a=run_financier_policy(no_belief,q,m,'K',allow_test_fixture=True)
        self.assertEqual(a.decision.outcome,FinancingDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertIn('belief.resource_exists',a.decision.unknown_input_keys)
        self.assertEqual(a.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

        no_prior=replace(standalone_snapshot(),priors=())
        b=run_financier_policy(no_prior,q,m,'K',allow_test_fixture=True)
        self.assertEqual(b.decision.outcome,FinancingDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertIn('prior.resource_exists',b.decision.unknown_input_keys)

    def test_test_fixture_manifest_cannot_run_without_explicit_test_override(self):
        with self.assertRaisesRegex(ValueError,'not authorized'):
            run_financier_policy(
                standalone_snapshot(),financing_request(),synthetic_policy_manifest(),'K')

if __name__=='__main__':
    unittest.main()
