import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor
from offworld_kernel.build5_publication_fixture import (
    financier_snapshot_after_publication,
    publication_handoff_kernel,
)
from offworld_kernel.mvp_state import (
    FinancingDecisionOutcome,
    PublicationDecisionOutcome,
    PublicationReasonCode,
)
from offworld_kernel.policy_runner import (
    public_publisher_contract_hash,
    public_publisher_policy_version,
    run_financier_policy,
    run_hostile_access_probe,
    run_public_publisher_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime

class Build5PublicationFinancierTests(unittest.TestCase):
    def run_publication(self,universe_id='RICH_PUBLIC_3',stock='20',
                        public_objective=True,publisher_possesses=True):
        k,snapshot,request,manifest,obs,wip,draw,before=publication_handoff_kernel(
            universe_id,stock,
            public_objective=public_objective,
            publisher_possesses=publisher_possesses)
        policy_id=(
            'POLICY:'+public_publisher_policy_version()
            +':CONTRACT:'+public_publisher_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('NO_EXTERNAL_TABLES',),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)
        holder={}

        def publisher_policy(ctx):
            result=run_public_publisher_policy(
                ctx.snapshot,request,ctx.decision_key)
            holder['publication_policy']=result
            d=result.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,result.policy_version))

        def publish(kernel,event):
            d=holder['publication_policy'].decision
            if d.outcome!=PublicationDecisionOutcome.PUBLISH:
                return 'NO_PUBLICATION:'+d.outcome.value
            det=manifest.parameter('agent_detection_rate').value
            fp=manifest.parameter('agent_false_positive_rate').value
            artifact=kernel.publish_observation(
                2,'PUB',request.observation_id,request.audience,
                (('FIN','resource_exists',det,fp),))
            holder['artifact']=artifact
            return '|'.join(('PUBLISHED',artifact.id,artifact.source_observation_id,artifact.signal))

        rt.register_policy_handler(
            'public-publication-decision','PUB',snapshot,'PUBLICATION-KEY-1',publisher_policy)
        rt.register_handler('PUBLICATION_SYSTEM',publish)
        rt.seal()
        result=rt.run()
        checks=AccountingIdentityAuditor(k,before).check_all()
        holder['run_result']=result
        holder['checks']=checks
        holder['source_observation']=obs
        holder['source_draw']=draw
        holder['manifest']=manifest
        return k,holder

    def finance_after_publication(self,k,holder):
        snapshot,request,table=financier_snapshot_after_publication(
            k,holder['source_observation'].id)
        result=run_financier_policy(
            snapshot,request,holder['manifest'],'FINANCE-KEY-002B',
            allow_test_fixture=True)
        holder['financier_snapshot']=snapshot
        holder['financing_request']=request
        holder['financier_result']=result
        holder['underwriting_table']=table
        return result

    def test_public_agent_publishes_pos_and_neg_under_open_information_objective(self):
        for universe_id,stock in (('RICH_PUBLIC_3','20'),('NULL_PUBLIC_1','0')):
            k,h=self.run_publication(universe_id,stock)
            d=h['publication_policy'].decision
            self.assertEqual(d.outcome,PublicationDecisionOutcome.PUBLISH)
            self.assertEqual(d.reason_code,PublicationReasonCode.PUBLISH_PUBLIC_INFORMATION)
            self.assertIn('artifact',h)
            self.assertEqual(h['artifact'].source_observation_id,h['source_observation'].id)

    def test_missing_objective_or_observation_possession_withholds(self):
        for kwargs in (
            {'public_objective':False},
            {'publisher_possesses':False},
        ):
            k,h=self.run_publication(**kwargs)
            d=h['publication_policy'].decision
            self.assertEqual(d.outcome,PublicationDecisionOutcome.WITHHOLD)
            self.assertNotIn('artifact',h)
            self.assertNotIn(h['source_observation'].id,k.agents['FIN'].information)

    def test_publication_policy_hostile_probe_has_no_hidden_access(self):
        _,snapshot,_,_,_,_,_,_=publication_handoff_kernel()
        result,_=run_hostile_access_probe(snapshot)
        self.assertEqual({k:v for k,v in result.items() if v=='LEAK'},{})

    def test_publication_transfers_observation_and_lineage_not_hidden_truth(self):
        k,h=self.run_publication('RICH_PUBLIC_3','20')
        artifact=h['artifact']
        obs=h['source_observation']
        self.assertEqual(artifact.publisher_id,'PUB')
        self.assertEqual(artifact.resource_id,'RES')
        self.assertEqual(artifact.signal,obs.signal)
        self.assertEqual(artifact.recipient_ids,('FIN',))
        self.assertFalse(obs.public)
        self.assertIn(obs.id,k.agents['FIN'].information)
        self.assertIn(artifact.id,k.agents['FIN'].information)
        self.assertNotIn('RICH_PUBLIC_3',repr(k.agents['FIN'].information))
        self.assertEqual(k.resources['RES'].remaining,D('20'))
        self.assertEqual(tuple(sorted(h['checks'])),
                         ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_positive_publication_updates_financier_and_approves(self):
        k,h=self.run_publication('RICH_PUBLIC_3','20')
        self.assertEqual(h['source_observation'].signal,'POSITIVE')
        result=self.finance_after_publication(k,h)
        self.assertEqual(dict(h['financier_snapshot'].beliefs)['resource_exists'],D('0.5'))
        self.assertEqual(result.decision.outcome,FinancingDecisionOutcome.APPROVE)

    def test_negative_publication_updates_financier_and_rejects(self):
        k,h=self.run_publication('NULL_PUBLIC_1','0')
        self.assertEqual(h['source_observation'].signal,'NEGATIVE')
        result=self.finance_after_publication(k,h)
        expected=D('0.04')/D('0.68')
        self.assertEqual(dict(h['financier_snapshot'].beliefs)['resource_exists'],expected)
        self.assertEqual(result.decision.outcome,FinancingDecisionOutcome.REJECT)

    def test_same_financier_state_diverges_only_after_published_signal(self):
        rk,rh=self.run_publication('RICH_PUBLIC_3','20')
        nk,nh=self.run_publication('NULL_PUBLIC_1','0')
        r=self.finance_after_publication(rk,rh)
        n=self.finance_after_publication(nk,nh)
        self.assertEqual(rh['publication_policy'].decision,nh['publication_policy'].decision)
        self.assertNotEqual(
            dict(rh['financier_snapshot'].beliefs)['resource_exists'],
            dict(nh['financier_snapshot'].beliefs)['resource_exists'])
        self.assertNotEqual(r.decision.outcome,n.decision.outcome)

    def test_false_positive_null_world_can_rationally_produce_approval(self):
        k,h=self.run_publication('NULL_FP_1','0')
        self.assertEqual(k.resources['RES'].remaining,D('0'))
        self.assertEqual(h['source_observation'].signal,'POSITIVE')
        result=self.finance_after_publication(k,h)
        self.assertEqual(dict(h['financier_snapshot'].beliefs)['resource_exists'],D('0.5'))
        self.assertEqual(result.decision.outcome,FinancingDecisionOutcome.APPROVE)
        self.assertEqual(k.resources['RES'].remaining,D('0'))

    def test_publication_and_financier_response_replay(self):
        ak,ah=self.run_publication('RICH_PUBLIC_3','20')
        bk,bh=self.run_publication('RICH_PUBLIC_3','20')
        ar=self.finance_after_publication(ak,ah)
        br=self.finance_after_publication(bk,bh)
        self.assertEqual(ah['run_result'].result_fingerprint,bh['run_result'].result_fingerprint)
        self.assertEqual(ah['artifact'],bh['artifact'])
        self.assertEqual(ar.decision,br.decision)
        self.assertEqual(ar.worker_fingerprint,br.worker_fingerprint)

if __name__=='__main__':
    unittest.main()
