import unittest
from dataclasses import replace
from decimal import Decimal as D

from offworld_kernel.build5_public_fixture import public_explorer_kernel
from offworld_kernel.mvp_state import ExplorationDecisionOutcome, ExplorationReasonCode
from offworld_kernel.policy_runner import run_hostile_access_probe, run_public_explorer_policy

class Build5PublicExplorerPolicyTests(unittest.TestCase):
    def test_affordable_public_information_mission_authorizes_remote_observation(self):
        _,snapshot,request,_,_=public_explorer_kernel()
        result=run_public_explorer_policy(snapshot,request,'PUB-KEY-1')
        self.assertEqual(result.decision.outcome,ExplorationDecisionOutcome.AUTHORIZE)
        self.assertEqual(result.decision.reason_code,
                         ExplorationReasonCode.APPROVED_PUBLIC_INFORMATION_MISSION)
        self.assertEqual(result.decision.authorized_cost,D('10'))
        self.assertEqual(result.decision.channel,'REMOTE')

    def test_insufficient_budget_declines(self):
        _,snapshot,request,_,_=public_explorer_kernel(balance='5')
        result=run_public_explorer_policy(snapshot,request,'PUB-KEY-1')
        self.assertEqual(result.decision.outcome,ExplorationDecisionOutcome.DECLINE)
        self.assertEqual(result.decision.reason_code,ExplorationReasonCode.INSUFFICIENT_BUDGET)
        self.assertEqual(result.decision.authorized_cost,D('0'))

    def test_missing_capability_or_objective_declines(self):
        for kwargs in ({'capability':False},{'objective':False}):
            _,snapshot,request,_,_=public_explorer_kernel(**kwargs)
            result=run_public_explorer_policy(snapshot,request,'PUB-KEY-1')
            self.assertEqual(result.decision.outcome,ExplorationDecisionOutcome.DECLINE)
            self.assertEqual(result.decision.reason_code,
                             ExplorationReasonCode.CAPABILITY_OR_OBJECTIVE_BLOCK)

    def test_unknown_cost_blocks_without_worker(self):
        _,snapshot,request,_,_=public_explorer_kernel(cost_known=False)
        result=run_public_explorer_policy(snapshot,request,'PUB-KEY-1')
        self.assertEqual(result.decision.outcome,ExplorationDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(result.decision.reason_code,
                         ExplorationReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN)
        self.assertEqual(result.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
        self.assertEqual(result.decision.unknown_input_keys,('exploration.REMOTE_COST',))

    def test_hidden_null_rich_worlds_cannot_change_pre_observation_decision(self):
        _,null_snapshot,null_request,_,_=public_explorer_kernel('NULL_PUBLIC_1','0')
        _,rich_snapshot,rich_request,_,_=public_explorer_kernel('RICH_PUBLIC_3','20')
        self.assertEqual(null_snapshot,rich_snapshot)
        self.assertEqual(null_request,rich_request)

        null_result=run_public_explorer_policy(null_snapshot,null_request,'SAME-KEY')
        rich_result=run_public_explorer_policy(rich_snapshot,rich_request,'SAME-KEY')
        self.assertEqual(null_result.decision,rich_result.decision)
        self.assertEqual(null_result.worker_fingerprint,rich_result.worker_fingerprint)

    def test_hostile_probe_exposes_no_hidden_runtime_access(self):
        _,snapshot,_,_,_=public_explorer_kernel()
        result,_=run_hostile_access_probe(snapshot)
        leaks={k:v for k,v in result.items() if v=='LEAK'}
        self.assertEqual(leaks,{})

if __name__=='__main__':
    unittest.main()
