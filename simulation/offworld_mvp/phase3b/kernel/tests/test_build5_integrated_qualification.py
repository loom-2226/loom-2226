import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_surface_prospecting_fixture import test007a_surface_model
from offworld_kernel.build5_transport_technology_fixture import transport_technology_kernel
from offworld_kernel.mvp_state import (
    PublicationDecisionOutcome,
    RuntimeObjectClass,
    SponsorProjectDecisionOutcome,
    SystemState,
)
from offworld_kernel.policy import DecisionSnapshot, build_decision_snapshot
from offworld_kernel.policy_runner import (
    public_publisher_contract_hash,
    public_publisher_policy_version,
    run_public_publisher_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.publication_protocol import build_publication_request
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_repeated_enterprise as enterprise_tests
from tests import test_build5_sale_market as market_tests
from tests import test_build5_settlement as settlement_tests
from tests import test_build5_sponsor_operator as sponsor_tests
from tests import test_build5_surface_prospecting as surface_tests
from tests import test_build5_surplus_distribution as surplus_tests
from tests import test_build5_transport_technology as transport_tests


class Build5IntegratedQualificationTests(unittest.TestCase):
    CASES=(
        ('RICH','RICH_PUBLIC_3','20'),
        ('SPARSE','SPARSE_PUBLIC_1','3'),
        ('NULL','NULL_SURFACE_1','0'),
    )

    def base(self,universe_id,stock):
        k,h=transport_technology_kernel(universe_id,stock)
        h['inherited_initialization_observation_id']=h['obs'].id

        # All authority required by the integrated chain is admitted before the
        # first governed decision epoch. No object-graph mutation is permitted later.
        k.agents['PUB'].capabilities.add('SURFACE_PROSPECT')
        k.agents['SPN'].capabilities.add('CLOSE_PROJECT')
        for system in (
            SystemState('PUBLIC_DECISION_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
            SystemState(
                'PUBLIC_FINANCE_EXECUTOR','PUBLIC_EXPLORATION_FINANCE',
                {'accounts','commitments','resource_constraints'}),
            SystemState(
                'REMOTE_OBSERVATION_SYSTEM','REMOTE_OBSERVATION',
                {'accounts','transactions','assets','observations','agent_information','agent_beliefs',
                 'earth_impact','resource_constraints','events'}),
            SystemState(
                'SURFACE_PROSPECTING_SYSTEM','SURFACE_PROSPECTING',
                {'accounts','transactions','assets','observations','agent_information',
                 'earth_impact','resource_constraints','events','surface_prospecting_records'}),
            SystemState(
                'SURFACE_INFORMATION_UPDATE_SYSTEM','OBSERVATION_INFORMATION_UPDATE',
                {'agent_beliefs','events','observation_belief_update_records'}),
            SystemState('ENTERPRISE_REVIEW_ORCHESTRATOR','DECISION_ORCHESTRATION',set()),
            SystemState(
                'ENTERPRISE_REVIEW_EXECUTOR','ENTERPRISE_LIFECYCLE_REVIEW',
                {'projects','events','enterprise_review_records'}),
        ):
            k.add_system(system)

        # Declared Test-only supply envelopes for the additional qualified epochs.
        k.set_resource_constraint('EARTH:X',2,D('1000'),D('0.10'))
        k.set_resource_constraint('EARTH:X',14,D('1000'),D('0.10'))
        k.set_resource_constraint('EARTH:X',15,D('1000'),D('0.10'))
        h['model']=test007a_surface_model()
        h['remote_cost']=D('10')
        h['surface_cost']=D('25')
        h['reference_lineage_before']=k.run_identity.input_snapshot_id
        h['reference_fcf_before']=tuple(sorted(
            (node,year,str(c.reference_fcf))
            for (node,year),c in k.resource_constraints.items()))
        return k,h

    def publication_epoch(self,k,h):
        obs=h['surface_observation']
        h['obs']=obs
        request=build_publication_request(
            'PUBREQ-INTEGRATED-SURFACE',2,obs.id,'PUBLIC_FINANCIERS')
        snapshot=build_decision_snapshot(k,'PUB','PUBLISH-SURFACE-2.5',D('2.5'),())
        h['integrated_publication_request']=request
        h['integrated_publication_snapshot']=snapshot

        k.begin_decision_epoch('EPOCH-3-PUBLISH-SURFACE')
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLICATION_DECISION_ORCHESTRATOR','v1',RuntimeObjectClass.SYSTEM,
            (),('agent_snapshot',),(),'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PUBLICATION_SYSTEM','v1',RuntimeObjectClass.SYSTEM,
            ('public_information','agent_information','agent_beliefs','events'),
            ('publication_decision','observation','publisher_information'),
            ('public_information','agent_information','agent_beliefs','events'),
            'EVENT',Phase.INFORMATION_UPDATE,perspective='WORLD_SIM'))

        ref=k.scheduler.open_decision_window(snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'integrated-publication-decision',D('2.5'),Phase.DECISION_WINDOW,0,'PUB',
            'PUBLICATION_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'integrated-publication-transfer',D('2.6'),Phase.INFORMATION_UPDATE,0,'PUBINFO',
            'PUBLICATION_SYSTEM',parent_ids=('integrated-publication-decision',)))

        policy_id=(
            'POLICY:'+public_publisher_policy_version()
            +':CONTRACT:'+public_publisher_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,table_manifest_ids=('NO_EXTERNAL_TABLES',),policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_publisher_policy(ctx.snapshot,request,ctx.decision_key)
            h['integrated_publication_policy']=r
            d=r.decision
            return '|'.join((d.id,d.outcome.value,d.reason_code.value,r.policy_version))

        def publish(kernel,event):
            d=h['integrated_publication_policy'].decision
            if d.outcome!=PublicationDecisionOutcome.PUBLISH:
                return 'NO_PUBLICATION:'+d.outcome.value
            det=h['manifest'].parameter('agent_detection_rate').value
            fp=h['manifest'].parameter('agent_false_positive_rate').value
            artifact=kernel.publish_observation(
                2,'PUB',obs.id,request.audience,
                (('FIN','resource_exists',det,fp),('SPN','resource_exists',det,fp)))
            h['artifact']=artifact
            return '|'.join(('PUBLISHED',artifact.id,artifact.signal,*artifact.recipient_ids))

        rt.register_policy_handler(
            'integrated-publication-decision','PUB',snapshot,'INTEGRATED-PUBLICATION-KEY',policy)
        rt.register_handler('PUBLICATION_SYSTEM',publish)
        before=AccountingPeriodSnapshot.capture(k,2)
        rt.seal()
        result=rt.run()
        h['integrated_publication_result']=result
        h['integrated_publication_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def run_case(self,label,universe_id,stock):
        k,h=self.base(universe_id,stock)
        surface=surface_tests.Build5SurfaceProspectingTests()
        sponsor=sponsor_tests.Build5SponsorOperatorTests()
        lifecycle=lifecycle_tests.Build5ProjectLifecycleTests()
        operating=operating_tests.Build5OperatingExtractionTests()
        market=market_tests.Build5SaleMarketTests()
        surplus=surplus_tests.Build5SurplusDistributionTests()
        settlement=settlement_tests.Build5SettlementTests()
        transport=transport_tests.Build5TransportTechnologyTests()
        enterprise=enterprise_tests.Build5RepeatedEnterpriseTests()

        surface.remote_epoch(k,h,chain_id='CHAIN-INTEGRATED-QUALIFICATION-R1')
        surface.surface_epoch(k,h)
        self.publication_epoch(k,h)
        sponsor.sponsor_epoch(
            k,h,'EPOCH-4-SPONSOR-FINANCE','SPREQ-IQ-DEV-FIN',3)

        first_sponsor=h['EPOCH-4-SPONSOR-FINANCE_policy'].decision
        if first_sponsor.outcome==SponsorProjectDecisionOutcome.ABANDON:
            h['integrated_terminal_branch']='ABANDON_AFTER_SURFACE_INFORMATION'
            self.assertEqual(k.state.projects['P'].status,'ABANDONED')
            k.assert_methodology_invariants()
            return k,h

        self.assertEqual(first_sponsor.outcome,SponsorProjectDecisionOutcome.REQUEST_FINANCE)
        sponsor.finance_epoch(k,h)
        sponsor.sponsor_epoch(
            k,h,'EPOCH-6-SPONSOR-DEVELOP','SPREQ-IQ-DEVELOP',5)
        lifecycle.lifecycle_epoch(k,h,'EPOCH-7-CONSTRUCTION')
        operating.operating_request_epoch(k,h)
        operating.operating_finance_epoch(k,h)
        operating.operate_epoch(k,h)
        market.sale_epoch(k,h)
        surplus.distribution_epoch(k,h)
        settlement.infrastructure_epoch(k,h)
        transport.transport_epoch(k,h)
        if 'passenger_transport_departure' in h:
            transport.arrival_epoch(k,h)

        # The first extraction happened before settlement; review it after the
        # transport/arrival slice so one persistent chain proves coexistence.
        enterprise.review_epoch(k,h,h['extraction_record'],2,13)
        if k.state.projects['P'].status=='OPERATING':
            enterprise.operating_cycle_epoch(k,h,2,14)
            enterprise.review_epoch(k,h,h['extraction_2'],3,14)

        if label=='RICH' and k.state.projects['P'].status=='OPERATING':
            enterprise.recap_request_epoch(k,h,15)
            enterprise.recap_finance_epoch(k,h,15)

        h['integrated_terminal_branch']='FULL_DOWNSTREAM_CHAIN'
        k.assert_methodology_invariants()
        return k,h

    @staticmethod
    def assert_all_epoch_audits(testcase,h):
        audits={k:v for k,v in h.items() if k.endswith('_checks') and isinstance(v,dict)}
        testcase.assertGreaterEqual(len(audits),3)
        for key,checks in audits.items():
            testcase.assertEqual(tuple(checks),tuple(f'A{i}' for i in range(1,10)),key)
            testcase.assertTrue(all(checks.values()),key)

    @staticmethod
    def shadow_totals(k):
        keys=(
            'capital_diverted_to_offworld','capital_returned_to_earth',
            'offworld_purchases_from_earth','earth_purchases_from_offworld',
            'qualifying_supplied_expenditure','terrestrial_fcf_delta',
            'migration_from_earth','returning_population',
        )
        out={key:D('0') for key in keys}
        for year in range(0,21):
            shadow=k.earth_shadow_at(year)
            for key in keys:
                out[key]+=D(str(shadow[key]))
        return out

    @staticmethod
    def semantic_summary(k,h):
        colony=k.colonies.get('OFF:T1')
        shadow=Build5IntegratedQualificationTests.shadow_totals(k)
        return {
            'project_status':k.state.projects['P'].status,
            'remote_signal':h['remote_observation'].signal,
            'surface_signal':h['surface_observation'].signal,
            'surface_posterior':str(h['surface_belief_update'].posterior),
            'sponsor_belief':str(k.agents['SPN'].beliefs['resource_exists']),
            'outputs':tuple(str(r.actual_extracted) for r in k.extraction_resolution_records),
            'reviews':tuple(r.outcome.value for r in k.enterprise_review_records),
            'stage':None if colony is None else colony.stage,
            'earth_population':k.population.earth,
            'offworld_population':k.population.offworld.get('OFF:T1',0),
            'in_transit':tuple(sorted(k.population.in_transit.items())),
            'total_population':k.population.total(),
            'project_cash':str(k.state.accounts['project_cash'].balance),
            'financier_cash':str(k.state.accounts['fin_funds'].balance),
            'public_cash':str(k.state.accounts['public_funds'].balance),
            'resource_remaining':str(k.resources['RES'].remaining),
            'transport_departures':len(k.passenger_transport_departures),
            'transport_arrivals':len(k.passenger_transport_arrivals),
            'epoch_count':len(k.decision_epoch_records),
            'transaction_count':len(k.state.transactions),
            'shadow':tuple((key,str(value)) for key,value in sorted(shadow.items())),
            'terminal_branch':h['integrated_terminal_branch'],
            'methodology_fingerprint':k.methodology_fingerprint(),
            'epoch_results':tuple(r.result_fingerprint for r in k.decision_epoch_records),
        }

    def test_integrated_null_sparse_rich_qualification(self):
        cases={label:self.run_case(label,uid,stock) for label,uid,stock in self.CASES}
        rh,rhctx=cases['RICH']; sk,shctx=cases['SPARSE']; nk,nhctx=cases['NULL']

        # Same admitted pre-distinguishing decision state produces the same choices.
        self.assertEqual(rhctx['remote_policy'].decision,shctx['remote_policy'].decision)
        self.assertEqual(rhctx['remote_policy'].decision,nhctx['remote_policy'].decision)
        self.assertEqual(rhctx['remote_observation'].signal,'POSITIVE')
        self.assertEqual(shctx['remote_observation'].signal,'POSITIVE')
        self.assertEqual(nhctx['remote_observation'].signal,'POSITIVE')
        self.assertEqual(rhctx['surface_snapshot'],shctx['surface_snapshot'])
        self.assertEqual(rhctx['surface_snapshot'],nhctx['surface_snapshot'])
        self.assertEqual(rhctx['surface_policy'].decision,shctx['surface_policy'].decision)
        self.assertEqual(rhctx['surface_policy'].decision,nhctx['surface_policy'].decision)

        # WORLD_SIM surface information is the first distinguishing information here.
        self.assertEqual(rhctx['surface_observation'].signal,'POSITIVE')
        self.assertEqual(shctx['surface_observation'].signal,'POSITIVE')
        self.assertEqual(nhctx['surface_observation'].signal,'NEGATIVE')
        self.assertGreater(rhctx['surface_belief_update'].posterior,D('0.50'))
        self.assertGreater(shctx['surface_belief_update'].posterior,D('0.50'))
        self.assertLess(nhctx['surface_belief_update'].posterior,D('0.50'))

        # Downstream development lineage uses the autonomous SURFACE result, not
        # the inherited initialization observation from the historical fixture.
        for _,h in cases.values():
            surface_id=h['surface_observation'].id
            self.assertNotEqual(surface_id,h['inherited_initialization_observation_id'])
            self.assertEqual(h['artifact'].source_observation_id,surface_id)
            self.assertEqual(h['obs'].id,surface_id)
            self.assertEqual(
                h['EPOCH-4-SPONSOR-FINANCE_request'].observation_id,surface_id)

        rich_first=rhctx['EPOCH-4-SPONSOR-FINANCE_policy'].decision
        sparse_first=shctx['EPOCH-4-SPONSOR-FINANCE_policy'].decision
        null_first=nhctx['EPOCH-4-SPONSOR-FINANCE_policy'].decision
        self.assertEqual(rich_first,sparse_first)
        self.assertEqual(rich_first.outcome,SponsorProjectDecisionOutcome.REQUEST_FINANCE)
        self.assertEqual(rich_first.requested_financing,D('60'))
        self.assertEqual(null_first.outcome,SponsorProjectDecisionOutcome.ABANDON)
        self.assertEqual(nk.state.projects['P'].status,'ABANDONED')
        self.assertEqual(nhctx['integrated_terminal_branch'],'ABANDON_AFTER_SURFACE_INFORMATION')
        self.assertEqual(nk.extraction_resolution_records,[])
        self.assertEqual(nk.population.total(),1000)
        self.assertEqual(nk.population.offworld.get('OFF:T1',0),0)
        self.assertEqual(nk.passenger_transport_departures,[])

        # RICH completes settlement, repeats successfully, then recapitalizes.
        self.assertEqual(rh.state.projects['P'].status,'OPERATING')
        self.assertEqual([r.actual_extracted for r in rh.extraction_resolution_records],[D('5'),D('5')])
        self.assertEqual([r.outcome.value for r in rh.enterprise_review_records],['CONTINUE','CONTINUE'])
        self.assertEqual(rh.colonies['OFF:T1'].stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual((rh.population.earth,rh.population.offworld['OFF:T1'],rh.population.total()),(990,10,1000))
        self.assertEqual(rh.population.in_transit,{})
        self.assertEqual(len(rh.passenger_transport_departures),1)
        self.assertEqual(len(rh.passenger_transport_arrivals),1)
        self.assertEqual(rh.state.accounts['project_cash'].balance,D('20'))
        self.assertEqual(rhctx['recap_operating_policy'].decision.requested_financing,D('20'))
        self.assertEqual(rhctx['recap_financier_policy'].decision.amount,D('20'))
        self.assertEqual(rh.resources['RES'].remaining,D('10'))

        # SPARSE forms the same dependent settlement, then exhausts and closes.
        self.assertEqual(sk.state.projects['P'].status,'CLOSED')
        self.assertEqual([r.actual_extracted for r in sk.extraction_resolution_records],[D('3'),D('0')])
        self.assertEqual([r.outcome.value for r in sk.enterprise_review_records],['CONTINUE','CLOSE'])
        self.assertEqual(sk.colonies['OFF:T1'].stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual((sk.population.earth,sk.population.offworld['OFF:T1'],sk.population.total()),(990,10,1000))
        self.assertEqual(sk.population.in_transit,{})
        self.assertEqual(len(sk.passenger_transport_departures),1)
        self.assertEqual(len(sk.passenger_transport_arrivals),1)
        self.assertEqual(sk.resources['RES'].remaining,D('0'))
        self.assertEqual(sk.state.accounts['project_cash'].balance,D('0'))

        # Every executed epoch that carries the A1-A9 auditor remained clean.
        for _,h in cases.values():
            self.assert_all_epoch_audits(self,h)

        # Decision snapshots never acquire direct hidden-world handles.
        forbidden_fact_keys={'resource.REMAINING','scenario.RESOURCE_TRUTH','universe.ID','world.SEED'}
        for _,h in cases.values():
            for value in h.values():
                if isinstance(value,DecisionSnapshot):
                    self.assertFalse(forbidden_fact_keys & {f.key for f in value.admitted_facts})
                    for attr in ('kernel','scheduler','resources','run_identity','universe_id','world_seed'):
                        self.assertFalse(hasattr(value,attr),attr)

        # Earth reference lineage is immutable while the same realized flows
        # populate the Test 013 shadow channels.
        for k,h in cases.values():
            self.assertEqual(k.run_identity.input_snapshot_id,h['reference_lineage_before'])
            current=tuple(sorted(
                (node,year,str(c.reference_fcf))
                for (node,year),c in k.resource_constraints.items()))
            self.assertEqual(current,h['reference_fcf_before'])
        rich_shadow=self.shadow_totals(rh); sparse_shadow=self.shadow_totals(sk); null_shadow=self.shadow_totals(nk)
        self.assertGreater(rich_shadow['capital_returned_to_earth'],0)
        self.assertGreater(sparse_shadow['capital_returned_to_earth'],0)
        self.assertEqual(null_shadow['capital_returned_to_earth'],0)
        self.assertGreater(rich_shadow['earth_purchases_from_offworld'],0)
        self.assertGreater(sparse_shadow['earth_purchases_from_offworld'],0)
        self.assertEqual(null_shadow['earth_purchases_from_offworld'],0)
        self.assertEqual(rich_shadow['migration_from_earth'],D('10'))
        self.assertEqual(sparse_shadow['migration_from_earth'],D('10'))
        self.assertEqual(null_shadow['migration_from_earth'],D('0'))
        self.assertEqual(rich_shadow['returning_population'],D('0'))
        self.assertEqual(sparse_shadow['returning_population'],D('0'))
        self.assertEqual(null_shadow['returning_population'],D('0'))

    def test_integrated_semantic_replay_is_deterministic(self):
        for label,uid,stock in self.CASES:
            k1,h1=self.run_case(label,uid,stock)
            k2,h2=self.run_case(label,uid,stock)
            self.assertEqual(self.semantic_summary(k1,h1),self.semantic_summary(k2,h2),label)


if __name__=='__main__':
    unittest.main()
