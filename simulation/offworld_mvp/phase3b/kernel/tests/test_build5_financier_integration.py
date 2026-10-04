import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_fixture import financing_request, scheduled_financier_kernel
from offworld_kernel.mvp_state import FinancingDecisionOutcome
from offworld_kernel.policy_runner import run_financier_policy
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime

class Build5FinancierIntegrationTests(unittest.TestCase):
    def run_case(self,belief='0.50'):
        k,snapshot,manifest,table=scheduled_financier_kernel(belief=belief)
        q=financing_request()
        table_id=f'UNDERWRITING:{table.table_id}:{table.version}:{table.fingerprint()}'
        policy_id=(
            'POLICY:'+manifest.policy_version_hash(
                (__import__('pathlib').Path(__file__).resolve().parents[1]/
                 'offworld_kernel'/'policies'/'financier_v1.py').read_bytes())
            +':PARAMS:'+manifest.parameter_manifest_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=(table_id,),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)
        holder={}
        before=AccountingPeriodSnapshot.capture(k,1)

        def policy(ctx):
            result=run_financier_policy(
                ctx.snapshot,q,manifest,ctx.decision_key,allow_test_fixture=True)
            holder['policy_result']=result
            d=result.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,result.policy_version))

        def execute(kernel,event):
            d=holder['policy_result'].decision
            if d.outcome==FinancingDecisionOutcome.APPROVE:
                kernel.add_commitment('C-B5','FIN','P',d.amount)
                kernel.disburse(1,'C-B5','fin_funds',d.amount)
                return 'FUNDED:'+str(d.amount)
            return 'NO_FUNDING:'+d.outcome.value

        rt.register_policy_handler('financier-decision','FIN',snapshot,'DECISION-KEY-1',policy)
        rt.register_handler('FINANCE_EXECUTOR',execute)
        rt.seal()
        result=rt.run()
        checks=AccountingIdentityAuditor(k,before).check_all()
        return k,result,holder['policy_result'],checks

    def test_approved_policy_decision_finances_only_in_later_scheduled_transition(self):
        k,result,policy_result,checks=self.run_case('0.50')
        self.assertEqual(policy_result.decision.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('40'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('60'))
        self.assertEqual(k.state.commitments['C-B5'].disbursed,D('60'))
        self.assertEqual(tuple(sorted(checks)),('A1','A2','A3','A4','A5','A6','A7','A8','A9'))
        self.assertTrue(result.policy_manifest_ids[0].startswith('POLICY:'))
        self.assertTrue(result.table_manifest_ids[0].startswith('UNDERWRITING:'))
        self.assertEqual(
            result.execution_log,
            ('financier-decision','finance-execute'))

    def test_rejected_policy_decision_creates_no_financing_state(self):
        k,result,policy_result,checks=self.run_case('0.05')
        self.assertEqual(policy_result.decision.outcome,FinancingDecisionOutcome.REJECT)
        self.assertEqual(k.state.accounts['fin_funds'].balance,D('100'))
        self.assertEqual(k.state.accounts['project_cash'].balance,D('0'))
        self.assertNotIn('C-B5',k.state.commitments)
        self.assertEqual(tuple(sorted(checks)),('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_integrated_policy_run_replays(self):
        a=self.run_case('0.50')
        b=self.run_case('0.50')
        self.assertEqual(a[1].result_fingerprint,b[1].result_fingerprint)
        self.assertEqual(a[2].decision,b[2].decision)
        self.assertEqual(a[2].policy_version,b[2].policy_version)

if __name__=='__main__':
    unittest.main()
