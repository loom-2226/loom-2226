import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_public_fixture import public_explorer_kernel
from offworld_kernel.mvp_state import ExplorationDecisionOutcome
from offworld_kernel.policy_runner import (
    public_explorer_contract_hash,
    public_explorer_policy_version,
    run_public_explorer_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime

class Build5PublicExplorerIntegrationTests(unittest.TestCase):
    def run_case(self,universe_id,stock):
        k,snapshot,request,fp,fn=public_explorer_kernel(universe_id,stock)
        policy_id=(
            'POLICY:'+public_explorer_policy_version()
            +':CONTRACT:'+public_explorer_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('NO_EXTERNAL_TABLES',),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)
        holder={}
        before=AccountingPeriodSnapshot.capture(k,1)

        def policy(ctx):
            result=run_public_explorer_policy(
                ctx.snapshot,request,ctx.decision_key)
            holder['policy_result']=result
            d=result.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,result.policy_version))

        def finance(kernel,event):
            d=holder['policy_result'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_PUBLIC_EXPLORATION_FINANCE:'+d.outcome.value
            kernel.add_commitment('C-PUB-EXP','PUB','EXP',d.authorized_cost)
            kernel.disburse(1,'C-PUB-EXP','public_funds',d.authorized_cost)
            kernel.reserve_earth_supply('EARTH:X',1,d.authorized_cost)
            return 'PUBLIC_EXPLORATION_FUNDED:'+str(d.authorized_cost)

        def observe(kernel,event):
            d=holder['policy_result'].decision
            if d.outcome!=ExplorationDecisionOutcome.AUTHORIZE:
                return 'NO_REMOTE_OBSERVATION:'+d.outcome.value
            obs,wip,draw=kernel.explore_paid(
                1,'PUB','RES','EXP','earth_supplier',d.authorized_cost,
                'REMOTE',False,fp,fn)
            holder['observation']=obs
            holder['wip']=wip
            holder['draw']=draw
            return '|'.join(('OBSERVED',obs.id,obs.signal,str(draw)))

        rt.register_policy_handler(
            'public-explore-decision','PUB',snapshot,'PUBLIC-DECISION-KEY-1',policy)
        rt.register_handler('PUBLIC_FINANCE_EXECUTOR',finance)
        rt.register_handler('REMOTE_OBSERVATION_SYSTEM',observe)
        rt.seal()
        run_result=rt.run()
        checks=AccountingIdentityAuditor(k,before).check_all()
        return k,run_result,holder,checks

    def test_rich_world_observation_changes_information_not_hidden_resource(self):
        k,result,holder,checks=self.run_case('RICH_PUBLIC_3','20')
        self.assertEqual(holder['policy_result'].decision.outcome,
                         ExplorationDecisionOutcome.AUTHORIZE)
        self.assertEqual(holder['observation'].signal,'POSITIVE')
        self.assertEqual(k.resources['RES'].remaining,D('20'))
        self.assertIn(holder['observation'].id,k.agents['PUB'].information)
        self.assertEqual(k.agents['PUB'].beliefs['RES'],D('0.50'))
        self.assertEqual(k.state.accounts['public_funds'].balance,D('90'))
        self.assertEqual(k.state.accounts['earth_supplier'].balance,D('10'))
        self.assertEqual(k.state.accounts['explore_cash'].balance,D('0'))
        self.assertEqual(tuple(sorted(checks)),('A1','A2','A3','A4','A5','A6','A7','A8','A9'))
        self.assertEqual(result.execution_log,(
            'public-explore-decision','public-explore-finance','public-remote-observation'))

    def test_null_world_can_produce_negative_observation_after_identical_decision(self):
        k,result,holder,checks=self.run_case('NULL_PUBLIC_1','0')
        self.assertEqual(holder['policy_result'].decision.outcome,
                         ExplorationDecisionOutcome.AUTHORIZE)
        self.assertEqual(holder['observation'].signal,'NEGATIVE')
        self.assertEqual(k.resources['RES'].remaining,D('0'))
        self.assertEqual(k.agents['PUB'].beliefs['RES'],D('0.05'))
        self.assertEqual(tuple(sorted(checks)),('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_hidden_worlds_share_pre_observation_policy_but_diverge_after_observation(self):
        rk,_,rh,_=self.run_case('RICH_PUBLIC_3','20')
        nk,_,nh,_=self.run_case('NULL_PUBLIC_1','0')
        self.assertEqual(rh['policy_result'].decision,nh['policy_result'].decision)
        self.assertEqual(rh['policy_result'].worker_fingerprint,
                         nh['policy_result'].worker_fingerprint)
        self.assertNotEqual(rh['observation'].signal,nh['observation'].signal)
        self.assertNotEqual(rk.agents['PUB'].beliefs['RES'],nk.agents['PUB'].beliefs['RES'])

    def test_integrated_public_explorer_replays(self):
        a=self.run_case('RICH_PUBLIC_3','20')
        b=self.run_case('RICH_PUBLIC_3','20')
        self.assertEqual(a[1].result_fingerprint,b[1].result_fingerprint)
        self.assertEqual(a[2]['policy_result'].decision,b[2]['policy_result'].decision)
        self.assertEqual(a[2]['observation'],b[2]['observation'])
        self.assertEqual(a[2]['draw'],b[2]['draw'])

if __name__=='__main__':
    unittest.main()
