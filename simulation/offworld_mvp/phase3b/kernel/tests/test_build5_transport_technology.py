import unittest
from decimal import Decimal as D

from offworld_kernel.accounting import AccountingIdentityAuditor, AccountingPeriodSnapshot
from offworld_kernel.build5_transport_technology_fixture import (
    BASELINE_CAPABILITY,
    IMPROVED_CAPABILITY,
    RESEARCH_TECHNOLOGY_REF,
    RESEARCH_TRANSPORT_REF,
    transport_technology_kernel,
    transport_settlement_request,
    transport_settlement_snapshot,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import Asset, AssetKind
from offworld_kernel.mvp_state import ColonyState, RuntimeObjectClass
from offworld_kernel.policy_runner import (
    public_settlement_transport_contract_hash,
    public_settlement_transport_policy_version,
    run_public_settlement_transport_policy,
)
from offworld_kernel.provenance import ReplayProvenance
from offworld_kernel.runtime import ScheduledSimulationRuntime
from offworld_kernel.scheduler import CouplingSpec, Phase, ScheduledEvent
from offworld_kernel.transport import (
    TechnologyCapabilityState,
    TransportRelationship,
    TransportSettlementDecisionOutcome,
    TransportSettlementReasonCode,
)
from tests import test_build5_operating_extraction as operating_tests
from tests import test_build5_project_lifecycle as lifecycle_tests
from tests import test_build5_sale_market as market_tests
from tests import test_build5_settlement as settlement_tests
from tests import test_build5_sponsor_operator as sponsor_tests
from tests import test_build5_surplus_distribution as surplus_tests


class Build5TransportTechnologyTests(unittest.TestCase):
    def reach_infrastructure(self,universe_id='RICH_PUBLIC_3',stock='20',**kw):
        k,h=transport_technology_kernel(universe_id,stock,**kw)

        s=sponsor_tests.Build5SponsorOperatorTests()
        s.publication_epoch(k,h,chain_id='CHAIN-TRANSPORT-012A')
        s.sponsor_epoch(k,h,'EPOCH-2-SPONSOR-FINANCE','SPREQ-012A-DEV-FIN',3)
        s.finance_epoch(k,h)
        s.sponsor_epoch(k,h,'EPOCH-4-SPONSOR-DEVELOP','SPREQ-012A-DEVELOP',5)

        l=lifecycle_tests.Build5ProjectLifecycleTests()
        l.lifecycle_epoch(k,h,'EPOCH-5-CONSTRUCTION')

        o=operating_tests.Build5OperatingExtractionTests()
        o.operating_request_epoch(k,h)
        o.operating_finance_epoch(k,h)
        o.operate_epoch(k,h)

        m=market_tests.Build5SaleMarketTests()
        m.sale_epoch(k,h)

        d=surplus_tests.Build5SurplusDistributionTests()
        d.distribution_epoch(k,h)

        settlement_tests.Build5SettlementTests().infrastructure_epoch(k,h)
        return k,h

    def transport_epoch(self,k,h,unknown_transport_key=None):
        snapshot=transport_settlement_snapshot(
            k,h,'TRANSPORT-SETTLEMENT-12','12',
            unknown_transport_key=unknown_transport_key)
        request=transport_settlement_request(h)
        h['transport_settlement_snapshot']=snapshot
        h['transport_settlement_request']=request

        k.begin_decision_epoch('EPOCH-12-TRANSPORT-SETTLEMENT-DEPARTURE')
        k.scheduler.register_coupling(CouplingSpec(
            'TRANSPORT_SETTLEMENT_DECISION_ORCHESTRATOR','v1',
            RuntimeObjectClass.SYSTEM,(),('agent_snapshot','transport_service'),(),
            'EVENT',Phase.DECISION_WINDOW))
        k.scheduler.register_coupling(CouplingSpec(
            'PASSENGER_TRANSPORT_DEPARTURE_SYSTEM','v1',
            RuntimeObjectClass.SYSTEM,
            ('accounts','transactions','colonies','population',
             'passenger_transport_departures','events'),
            ('transport_settlement_decision','technology_state',
             'transport_relationship','population','habitat_headroom'),
            ('accounts','transactions','colonies','population',
             'passenger_transport_departures','events'),
            'EVENT',Phase.OPERATIONS))

        ref=k.scheduler.open_decision_window(
            snapshot.period_key,snapshot.fingerprint())
        k.scheduler.schedule(ScheduledEvent(
            'transport-e12-decision',D('12'),Phase.DECISION_WINDOW,0,'PUB',
            'TRANSPORT_SETTLEMENT_DECISION_ORCHESTRATOR',snapshot_ref=ref))
        k.scheduler.schedule(ScheduledEvent(
            'transport-e12-departure',D('12'),Phase.OPERATIONS,0,
            'PASSENGER-DEPARTURE','PASSENGER_TRANSPORT_DEPARTURE_SYSTEM',
            parent_ids=('transport-e12-decision',)))

        policy_id=(
            'POLICY:'+public_settlement_transport_policy_version()
            +':CONTRACT:'+public_settlement_transport_contract_hash())
        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'TECHNOLOGY_STATE:'+h['transport_technology_state'].fingerprint(),
                'TRANSPORT_RELATIONSHIP:'+h['transport_relationship'].fingerprint(),
                'RESEARCH_ADVISORY_TRANSPORT:'+RESEARCH_TRANSPORT_REF,
                'RESEARCH_ADVISORY_TECHNOLOGY:'+RESEARCH_TECHNOLOGY_REF,
            ),
            policy_manifest_ids=(policy_id,))
        rt=ScheduledSimulationRuntime(k,prov)

        def policy(ctx):
            r=run_public_settlement_transport_policy(
                ctx.snapshot,request,ctx.decision_key)
            h['transport_settlement_policy']=r
            d=r.decision
            return '|'.join((
                d.id,d.outcome.value,d.reason_code.value,
                str(d.authorized_residents),str(d.support_amount),
                str(d.transport_amount),str(d.departure_time),str(d.arrival_time)))

        def departure(kernel,event):
            d=h['transport_settlement_policy'].decision
            if d.outcome!=TransportSettlementDecisionOutcome.AUTHORIZE:
                return 'NO_TRANSPORT_DEPARTURE:'+d.outcome.value
            rec=kernel.execute_transport_settlement_departure(
                'PUB',request,d,parent_ids=(event.event_id,))
            h['passenger_transport_departure']=rec
            return '|'.join((
                rec.departure_id,str(rec.passengers),
                str(rec.transport_amount),str(rec.arrival_time)))

        rt.register_policy_handler(
            'transport-e12-decision','PUB',snapshot,
            'TRANSPORT-SETTLEMENT-KEY-012A',policy)
        rt.register_handler('PASSENGER_TRANSPORT_DEPARTURE_SYSTEM',departure)
        before=AccountingPeriodSnapshot.capture(k,12)
        rt.seal()
        result=rt.run()
        h['transport_departure_result']=result
        h['transport_departure_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def arrival_epoch(self,k,h):
        dep=h['passenger_transport_departure']
        k.begin_decision_epoch('EPOCH-13-PASSENGER-ARRIVAL')
        k.scheduler.register_coupling(CouplingSpec(
            'PASSENGER_TRANSPORT_ARRIVAL_SYSTEM','v1',
            RuntimeObjectClass.SYSTEM,
            ('colonies','population','passenger_transport_arrivals',
             'settlement_stage_records','events'),
            ('passenger_transport_departure','population','colony_state'),
            ('colonies','population','passenger_transport_arrivals',
             'settlement_stage_records','events'),
            'EVENT',Phase.OPERATIONS))
        k.scheduler.schedule(ScheduledEvent(
            'transport-e13-arrival',D(dep.arrival_time),Phase.OPERATIONS,0,
            'PASSENGER-ARRIVAL','PASSENGER_TRANSPORT_ARRIVAL_SYSTEM',
            parent_ids=(dep.departure_event_id,)))

        prov=ReplayProvenance.from_kernel(
            k,
            table_manifest_ids=(
                'TECHNOLOGY_STATE:'+h['transport_technology_state'].fingerprint(),
                'TRANSPORT_RELATIONSHIP:'+h['transport_relationship'].fingerprint(),
            ),
            policy_manifest_ids=('NO_POLICY_THIS_EPOCH',))
        rt=ScheduledSimulationRuntime(k,prov)

        def arrival(kernel,event):
            rec=kernel.execute_passenger_transport_arrival(
                event.effective_time,dep.departure_id,
                parent_ids=(event.event_id,))
            h['passenger_transport_arrival']=rec
            return '|'.join((
                rec.departure_id,str(rec.passengers),
                str(rec.arrival_time),rec.stage_event_id))

        rt.register_handler('PASSENGER_TRANSPORT_ARRIVAL_SYSTEM',arrival)
        before=AccountingPeriodSnapshot.capture(k,int(D(dep.arrival_time)))
        rt.seal()
        result=rt.run()
        h['transport_arrival_result']=result
        h['transport_arrival_checks']=AccountingIdentityAuditor(k,before).check_all()
        return result

    def full_case(self,universe_id='RICH_PUBLIC_3',stock='20',**kw):
        k,h=self.reach_infrastructure(universe_id,stock,**kw)
        self.transport_epoch(k,h)
        if 'passenger_transport_departure' in h:
            self.arrival_epoch(k,h)
        return k,h

    def test_rich_transport_gated_settlement_arrives_and_conserves_population(self):
        k,h=self.full_case()
        d=h['transport_settlement_policy'].decision
        dep=h['passenger_transport_departure']
        arr=h['passenger_transport_arrival']
        c=k.colonies['OFF:T1']

        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.AUTHORIZE)
        self.assertEqual(d.authorized_residents,10)
        self.assertEqual(d.support_amount,D('10'))
        self.assertEqual(d.transport_amount,D('20'))
        self.assertEqual(dep.departure_time,D('12'))
        self.assertEqual(dep.arrival_time,D('13'))
        self.assertEqual(arr.arrival_time,D('13'))
        self.assertEqual(k.population.earth,990)
        self.assertEqual(k.population.offworld['OFF:T1'],10)
        self.assertEqual(k.population.in_transit,{})
        self.assertEqual(k.population.total(),1000)
        self.assertEqual(c.population,10)
        self.assertEqual(c.stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual(k.state.accounts['settlement_support'].balance,D('10'))
        self.assertEqual(k.state.accounts['transport_provider'].balance,D('20'))
        self.assertEqual(k.state.accounts['public_funds'].balance,D('60'))
        self.assertEqual(len(k.decision_epoch_records),13)

    def test_departure_holds_population_in_transit_until_arrival(self):
        k,h=self.reach_infrastructure()
        self.transport_epoch(k,h)
        dep=h['passenger_transport_departure']
        self.assertEqual(k.population.earth,990)
        self.assertEqual(k.population.offworld['OFF:T1'],0)
        self.assertEqual(k.population.in_transit,{dep.departure_id:10})
        self.assertEqual(k.population.total(),1000)
        self.assertEqual(k.colonies['OFF:T1'].stage,'EXTRACTION_ENCLAVE')
        self.arrival_epoch(k,h)
        self.assertEqual(k.population.in_transit,{})
        self.assertEqual(k.population.offworld['OFF:T1'],10)

    def test_sparse_has_same_transport_decision_and_can_settle(self):
        rk,rh=self.full_case('RICH_PUBLIC_3','20')
        sk,sh=self.full_case('SPARSE_PUBLIC_1','3')
        rd=rh['transport_settlement_policy'].decision
        sd=sh['transport_settlement_policy'].decision
        self.assertEqual(
            (rd.outcome,rd.reason_code,rd.authorized_residents,
             rd.support_amount,rd.transport_amount,rd.arrival_time),
            (sd.outcome,sd.reason_code,sd.authorized_residents,
             sd.support_amount,sd.transport_amount,sd.arrival_time))
        self.assertEqual(sk.colonies['OFF:T1'].stage,'DEPENDENT_SETTLEMENT')
        self.assertEqual(sk.population.total(),1000)

    def test_null_transport_availability_does_not_bootstrap_settlement(self):
        k,h=self.full_case('NULL_FP_1','0')
        d=h['transport_settlement_policy'].decision
        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,TransportSettlementReasonCode.HABITAT_CAPACITY_LIMIT)
        self.assertNotIn('passenger_transport_departure',h)
        self.assertEqual(k.population.earth,1000)
        self.assertEqual(k.population.offworld['OFF:T1'],0)
        self.assertEqual(k.population.in_transit,{})
        self.assertEqual(k.colonies['OFF:T1'].stage,'EXTRACTION_ENCLAVE')

    def test_missing_required_technology_capability_blocks_service(self):
        k,h=self.reach_infrastructure(technology_qualified=False)
        q=k.transport_qualification(
            h['transport_technology_state'].id,
            h['transport_relationship'].id,D('12'))
        self.assertFalse(q.available)
        self.assertEqual(q.reason,'REQUIRED_CAPABILITY_NOT_QUALIFIED')
        self.transport_epoch(k,h)
        d=h['transport_settlement_policy'].decision
        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,TransportSettlementReasonCode.TRANSPORT_UNAVAILABLE)
        self.assertNotIn('passenger_transport_departure',h)

    def test_missing_transport_relationship_blocks_unknown_not_guess(self):
        k,h=self.reach_infrastructure(register_relationship=False)
        self.transport_epoch(k,h)
        r=h['transport_settlement_policy']
        self.assertEqual(r.decision.outcome,TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertTrue({
            'transport.CAPACITY','transport.COST_PER_PASSENGER',
            'transport.TRAVEL_TIME','transport.ENERGY_PER_PASSENGER',
            'transport.LOSS_RISK',
        }.issubset(set(r.decision.unknown_input_keys)))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')
        self.assertNotIn('passenger_transport_departure',h)

    def test_capacity_limit_is_all_or_defer(self):
        k,h=self.reach_infrastructure(transport_capacity=6)
        self.transport_epoch(k,h)
        d=h['transport_settlement_policy'].decision
        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,TransportSettlementReasonCode.TRANSPORT_CAPACITY_LIMIT)
        self.assertEqual(k.population.earth,1000)
        self.assertEqual(k.population.in_transit,{})

    def test_insufficient_funding_includes_transport_and_support_separately(self):
        k,h=self.reach_infrastructure(public_balance='20')
        self.transport_epoch(k,h)
        d=h['transport_settlement_policy'].decision
        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,TransportSettlementReasonCode.INSUFFICIENT_PUBLIC_FUNDS)
        self.assertEqual(d.support_amount,D('0'))
        self.assertEqual(d.transport_amount,D('0'))
        self.assertNotIn('passenger_transport_departure',h)

    def test_nonzero_loss_risk_is_not_silently_simulated(self):
        k,h=self.reach_infrastructure(loss_risk='0.01')
        self.transport_epoch(k,h)
        d=h['transport_settlement_policy'].decision
        self.assertEqual(d.outcome,TransportSettlementDecisionOutcome.DEFER)
        self.assertEqual(d.reason_code,TransportSettlementReasonCode.LOSS_RISK_UNSUPPORTED)
        self.assertEqual(k.population.total(),1000)

    def test_unknown_required_transport_input_blocks_before_worker(self):
        k,h=self.reach_infrastructure()
        self.transport_epoch(k,h,unknown_transport_key='transport.ENERGY_PER_PASSENGER')
        r=h['transport_settlement_policy']
        self.assertEqual(r.decision.outcome,TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN)
        self.assertEqual(r.decision.unknown_input_keys,('transport.ENERGY_PER_PASSENGER',))
        self.assertEqual(r.sandbox_mode,'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    def test_five_transport_dimensions_are_separate_snapshot_facts(self):
        k,h=self.reach_infrastructure()
        snap=transport_settlement_snapshot(k,h,'DIMENSIONS','12')
        facts={f.key:f.value for f in snap.admitted_facts}
        self.assertEqual(facts['transport.COST_PER_PASSENGER'],'2')
        self.assertEqual(facts['transport.TRAVEL_TIME'],'1')
        self.assertEqual(facts['transport.ENERGY_PER_PASSENGER'],'3')
        self.assertEqual(facts['transport.LOSS_RISK'],'0')
        self.assertEqual(facts['transport.CAPACITY'],'10')
        self.assertEqual(len({
            'transport.COST_PER_PASSENGER','transport.TRAVEL_TIME',
            'transport.ENERGY_PER_PASSENGER','transport.LOSS_RISK',
            'transport.CAPACITY'}),5)

    def test_policy_evaluation_alone_mutates_no_world_state(self):
        k,h=self.reach_infrastructure()
        snap=transport_settlement_snapshot(k,h,'NO-MUTATE','12')
        req=transport_settlement_request(h)
        before=(
            k.population.earth,dict(k.population.offworld),dict(k.population.in_transit),
            k.state.accounts['public_funds'].balance,
            k.state.accounts['settlement_support'].balance,
            k.state.accounts['transport_provider'].balance,
            k.colonies['OFF:T1'].external_subsidy,
        )
        r=run_public_settlement_transport_policy(snap,req,'NO-MUTATE')
        self.assertEqual(r.decision.outcome,TransportSettlementDecisionOutcome.AUTHORIZE)
        after=(
            k.population.earth,dict(k.population.offworld),dict(k.population.in_transit),
            k.state.accounts['public_funds'].balance,
            k.state.accounts['settlement_support'].balance,
            k.state.accounts['transport_provider'].balance,
            k.colonies['OFF:T1'].external_subsidy,
        )
        self.assertEqual(before,after)

    def test_transport_and_technology_registration_alone_change_no_population_or_accounts(self):
        k,h=transport_technology_kernel()
        before=(
            k.population.total(),
            tuple(sorted((a.id,str(a.balance)) for a in k.state.accounts.values())),
        )
        improved=TechnologyCapabilityState(
            'TECH-IMPROVED',D('12'),D('20'),(IMPROVED_CAPABILITY,),
            'TEST_ONLY:IMPROVED','TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
        k.register_technology_capability_state(improved)
        rel=TransportRelationship(
            'TR-IMPROVED','EARTH:X','OFF:T1',D('12'),D('20'),
            IMPROVED_CAPABILITY,D('1'),D('0.5'),D('2'),D('0'),20,
            'PASSENGER','TEST_ONLY:IMPROVED',
            'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
        k.register_transport_relationship(rel)
        after=(
            k.population.total(),
            tuple(sorted((a.id,str(a.balance)) for a in k.state.accounts.values())),
        )
        self.assertEqual(before,after)
        q=k.transport_qualification(improved.id,rel.id,D('12'))
        self.assertTrue(q.available)
        self.assertEqual((rel.cost_per_passenger,rel.travel_time,
                          rel.energy_per_passenger,rel.capacity),
                         (D('1'),D('0.5'),D('2'),20))

    def test_wrong_direction_relationship_is_rejected(self):
        k,h=transport_technology_kernel()
        reverse=TransportRelationship(
            'TR-REVERSE','OFF:T1','EARTH:X',D('12'),D('20'),
            BASELINE_CAPABILITY,D('2'),D('1'),D('3'),D('0'),10,
            'PASSENGER','TEST_ONLY:REVERSE',
            'TEST_ONLY_NOT_CALIBRATED_NOT_POLICY_BASELINE').validate()
        with self.assertRaisesRegex(InvariantError,'EARTH -> OFFWORLD'):
            k.register_transport_relationship(reverse)

    def test_hidden_resource_truth_cannot_change_identical_transport_policy_input(self):
        results=[]
        for uid,stock in (('RICH_PUBLIC_3','20'),('NULL_FP_1','0')):
            k,h=transport_technology_kernel(uid,stock)
            k.colonies['OFF:T1']=ColonyState(
                'OFF:T1',population=0,productive_capital=D('60'),
                infrastructure=D('10'),habitat_capacity=10,
                production_capacity=D('5'),stage='EXTRACTION_ENCLAVE')
            snap=transport_settlement_snapshot(k,h,'IDENTICAL-ADMITTED','12')
            req=transport_settlement_request(h)
            result=run_public_settlement_transport_policy(snap,req,'SAME-KEY')
            results.append((
                result.decision.outcome,result.decision.reason_code,
                result.decision.authorized_residents,result.decision.support_amount,
                result.decision.transport_amount,result.decision.arrival_time,
                result.decision.id))
        self.assertEqual(results[0],results[1])

    def test_departure_uses_distinct_public_subsidy_and_transport_payment(self):
        k,h=self.reach_infrastructure()
        self.transport_epoch(k,h)
        dep=h['passenger_transport_departure']
        support=next(t for t in k.state.transactions if t.id==dep.support_transaction_id)
        transport=next(t for t in k.state.transactions if t.id==dep.transport_transaction_id)
        self.assertEqual(support.purpose.value,'PUBLIC_SUBSIDY')
        self.assertEqual(transport.purpose.value,'TRANSPORT_PAYMENT')
        self.assertEqual(support.amount,D('10'))
        self.assertEqual(transport.amount,D('20'))

    def test_duplicate_departure_and_arrival_are_rejected(self):
        k,h=transport_technology_kernel()
        k.colonies['OFF:T1']=ColonyState(
            'OFF:T1',population=0,productive_capital=D('60'),
            infrastructure=D('10'),habitat_capacity=10,
            production_capacity=D('5'),stage='EXTRACTION_ENCLAVE')
        k.state.assets['HOSTILE-PRODUCTIVE']=Asset(
            'HOSTILE-PRODUCTIVE','HOSTILE-PROJECT','OFF:T1',
            AssetKind.PRODUCTIVE,D('60'),D('5'))
        snap=transport_settlement_snapshot(k,h,'DIRECT','12')
        req=transport_settlement_request(h)
        d=run_public_settlement_transport_policy(snap,req,'DIRECT').decision
        dep=k.execute_transport_settlement_departure('PUB',req,d)
        with self.assertRaisesRegex(InvariantError,'already departed'):
            k.execute_transport_settlement_departure('PUB',req,d)
        k.execute_passenger_transport_arrival(dep.arrival_time,dep.departure_id)
        with self.assertRaisesRegex(InvariantError,'already arrived'):
            k.execute_passenger_transport_arrival(dep.arrival_time,dep.departure_id)

    def test_technology_relationship_and_in_transit_tampering_are_epoch_detectable(self):
        k,h=self.reach_infrastructure()
        self.transport_epoch(k,h)
        dep=h['passenger_transport_departure']

        original=h['transport_technology_state']
        k.technology_capability_states[original.id]=TechnologyCapabilityState(
            original.id,original.effective_from,original.effective_to,(),
            original.source_ref,original.epistemic_status,original.state_version)
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-TECH')

        # Restore exact technology state so the next hostile mutation isolates transit state.
        k.technology_capability_states[original.id]=original
        k.population.in_transit[dep.departure_id]+=1
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-TRANSIT')

    def test_transport_relationship_tampering_is_epoch_detectable(self):
        k,h=self.reach_infrastructure()
        self.transport_epoch(k,h)
        rel=h['transport_relationship']
        k.transport_relationships[rel.id]=TransportRelationship(
            rel.id,rel.origin_node_id,rel.destination_node_id,
            rel.effective_from,rel.effective_to,rel.required_capability_id,
            D('999'),rel.travel_time,rel.energy_per_passenger,rel.loss_risk,
            rel.capacity,rel.passenger_class,rel.source_ref,
            rel.epistemic_status,rel.relationship_version)
        with self.assertRaisesRegex(InvariantError,'tampered between decision epochs'):
            k.begin_decision_epoch('TAMPER-RELATIONSHIP')

    def test_transport_epochs_preserve_A1_A9(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            _,h=self.full_case(uid,stock)
            self.assertEqual(
                tuple(sorted(h['transport_departure_checks'])),
                ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))
            if 'transport_arrival_checks' in h:
                self.assertEqual(
                    tuple(sorted(h['transport_arrival_checks'])),
                    ('A1','A2','A3','A4','A5','A6','A7','A8','A9'))

    def test_transport_chain_replays_exactly(self):
        for uid,stock in (
            ('RICH_PUBLIC_3','20'),
            ('SPARSE_PUBLIC_1','3'),
            ('NULL_FP_1','0'),
        ):
            ak,ah=self.full_case(uid,stock)
            bk,bh=self.full_case(uid,stock)
            self.assertEqual(tuple(ak.decision_epoch_records),tuple(bk.decision_epoch_records))
            self.assertEqual(
                ah['transport_settlement_policy'].decision,
                bh['transport_settlement_policy'].decision)
            self.assertEqual(
                ak.passenger_transport_departures,
                bk.passenger_transport_departures)
            self.assertEqual(
                ak.passenger_transport_arrivals,
                bk.passenger_transport_arrivals)
            self.assertEqual(ak.methodology_fingerprint(),bk.methodology_fingerprint())


if __name__=='__main__':
    unittest.main()
