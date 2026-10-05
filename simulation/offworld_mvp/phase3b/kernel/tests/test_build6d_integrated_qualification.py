import unittest
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'build6/qualification'))
from build6d_fixture import make_kernel,policy_inputs,system_epoch,run_case
from offworld_kernel.boundary import *
from offworld_kernel.causal_trace import *
from offworld_kernel.kernel import InvariantError
from offworld_kernel.policy import build_decision_snapshot,SnapshotFact


from functools import lru_cache
@lru_cache(maxsize=3)
def baseline(world):return run_case(world)
class IntegratedQualificationTests(unittest.TestCase):
    def test_F01_zero_allocation_blocks_before_finance(self):
        k,h=run_case('RICH',{'f':'0'})
        self.assertIn('RESOURCE',h['blocked'])
        self.assertFalse(k.state.transactions);self.assertFalse(k.state.commitments)
    def test_F02_zero_public_cannot_observe(self):
        k,h=run_case('RICH',{'P':'0'});self.assertFalse(k.observations);self.assertFalse(k.state.transactions)
    def test_F03_zero_financier_cannot_construct(self):
        k,h=run_case('RICH',{'F':'0'});self.assertNotIn('MINE-P',k.state.assets);self.assertFalse(k.development_stage_records)
    def test_F04_zero_resource_does_not_create_output(self):
        k,h=baseline('NULL');self.assertEqual(k.state.projects['P'].status,'ABANDONED');self.assertFalse(k.market_clearing_records);self.assertEqual(k.population.offworld['OFF:T1'],0)
    def test_F05_finite_buyer_blocks_atomically(self):
        k,h=run_case('RICH',{'B':'0'})
        self.assertEqual(len(k.market_clearing_records),0)
    def test_F07_stage2_supply_failure(self):
        k,h=run_case('RICH',{'f.7':'0.000004'});self.assertEqual(k.state.projects['P'].status,'FAILED');self.assertNotIn('MINE-P',k.state.assets)
    def test_F11_all_A1_A9_each_epoch(self):
        for world in ('NULL','SPARSE','RICH'):
            k,h=baseline(world);self.assertTrue(h['audits']);self.assertTrue(all(all(row.values()) for row in h['audits']))
    def test_E07_finite_cohort_bound(self):
        k,h=make_kernel(overrides={'N':'348178046'})
        with self.assertRaisesRegex(InvariantError,'population bound'):k.begin_decision_epoch('F13','F13')
    def test_F13_population_conserved(self):
        for world in ('SPARSE','RICH'):
            k,h=baseline(world);self.assertEqual(k.population.total(),1000);self.assertEqual(k.population.offworld['OFF:T1'],10);self.assertFalse(any(k.population.in_transit.values()))
    def test_R03_resource_conserved_and_second_output_distinguishes(self):
        s,sh=baseline('SPARSE');r,rh=baseline('RICH')
        self.assertEqual(sh['first_output'].actual_extracted,D(3));self.assertEqual(sh['second_output'].actual_extracted,D(0));self.assertEqual(s.state.projects['P'].status,'CLOSED')
        self.assertEqual(rh['first_output'].actual_extracted,D(5));self.assertEqual(rh['second_output'].actual_extracted,D(5));self.assertEqual(r.resources['RES'].remaining,D(10));self.assertEqual(r.state.projects['P'].status,'OPERATING')
        self.assertEqual(len(s.market_clearing_records),1);self.assertEqual(len(r.market_clearing_records),1)
    def test_F16_no_real_truth_promotion(self):
        for world in ('NULL','SPARSE','RICH'):
            k,h=baseline(world);q=ConsumptionRequest('REAL','GENESIS','QUALIFICATION','RES','R_RESERVE','SITE:OFF:T1','SIM_TIME','14','14','REAL','','GOVERNANCE','','ADMITTED','MODEL_RESOURCE_UNIT_BY_FAMILY','PHYSICAL_STATE');self.assertEqual(admit_for_use(k,q)[0].value_state,FactState.UNKNOWN)
    def test_R09_exact_replay(self):
        k,h=baseline('NULL');again,ah=run_case('NULL');self.assertEqual([r.result_fingerprint for r in h['results']],[r.result_fingerprint for r in ah['results']]);self.assertEqual(validate_trace(k.causal_envelopes,k.causal_artifacts),validate_trace(again.causal_envelopes,again.causal_artifacts))
    def test_L01_six_reconstruction_witnesses(self):
        k,h=baseline('RICH');out=reconstruct(k.causal_envelopes,k.causal_artifacts,k.causal_envelopes[-1].envelope_id,perspective='GOVERNANCE',actor_id='AUDIT')
        self.assertEqual(out['status'],'COMPLETE');self.assertEqual(len(out['envelopes']),len(k.causal_envelopes))
        actions={e.action for e in k.causal_envelopes}
        for action in ('disburse','execute_passenger_transport_arrival','resolve_operating_extraction','surface_prospect_paid','update_agent_belief_from_observation','POLICY_EVALUATION'):self.assertIn(action,actions)
        for e in k.causal_envelopes:self.assertEqual(e.envelope_hash,e.digest())
    def test_R03_information_driven_decisions_and_distinct_times(self):
        s,sh=baseline('SPARSE');r,rh=baseline('RICH')
        for label in ('REMOTE','SURFACE','PUBLICATION','SPONSOR','DEV_FINANCE','DEVELOP','FIRST_OPERATING','SALE'):
            self.assertEqual(sh['snapshots'][label],rh['snapshots'][label]);self.assertEqual(sh['policies'][label],rh['policies'][label])
        delayed=[e for e in r.causal_envelopes if e.action=='execute_development_stage']
        self.assertTrue(all(D(e.decision_time)==D(e.authorization_time)==D(5)<D(e.realized_time) for e in delayed));self.assertTrue(any(e.source_times for e in r.causal_envelopes))

    def test_F06_forged_OPEX_record_not_admitted(self):
        from offworld_kernel.causal_trace import archive
        from offworld_kernel.scheduler import ScheduledEvent,Phase
        k,h=baseline('RICH');d=h['policies']['FIRST_OPERATING:funded'].decision
        ref=next(ref for ref,(_,did,_) in k._boundary_decisions.items() if did==d.id)
        event=ScheduledEvent('F06',D(14),Phase.OPERATIONS,0,'SPN','SYS:resolve_operating_extraction')
        k._boundary_event_context=(event,(),(ref,))
        try:
            rec=replace(k.operating_cost_records[0],transaction_id='FORGED')
            with self.assertRaisesRegex(InvariantError,'LINEAGE'):k._boundary_preflight('resolve_operating_extraction',type(k).resolve_operating_extraction.__get__(k),(9,'SPN',h['requests']['FIRST_OPERATING:funded'],d,rec),{})
        finally:k._boundary_event_context=None
    def test_F08_unqualified_transport(self):
        k,h=run_case('RICH',{'technology_qualified':'FALSE'});self.assertFalse(k.passenger_transport_departures);self.assertEqual(k.population.offworld['OFF:T1'],0)
    def test_F08_missing_transport(self):
        k,h=run_case('RICH',{'relationship_registered':'FALSE'});self.assertFalse(k.passenger_transport_departures);self.assertEqual(k.population.offworld['OFF:T1'],0)
    def test_L08_buyer_block_has_no_financial_resource_delta(self):
        k,h=run_case('RICH',{'B':'0'});self.assertIn('AFFORDABILITY',h['blocked']);e=k.causal_envelopes[-1]
        self.assertEqual(e.prior_state,e.new_state);self.assertEqual(k.state.accounts['earth_market'].balance,D(0));self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D(5))

    def test_closed_epistemic_causal_loop_has_explicit_output_observation(self):
        import json
        k,h=baseline('RICH')
        admissions=[e for e in k.causal_envelopes if e.action=='admit_realized_output_observation']
        self.assertEqual(len(admissions),2);self.assertTrue(all(e.actor_id=='SPN' for e in admissions))
        refs=[e for e in k.causal_envelopes if e.action=='POLICY_EVALUATION' and e.scheduled_event_id=='SECOND_REVIEW:decision'][0].information_refs
        reports=[json.loads(k.causal_artifacts[ref][1])['fields'] for ref in refs]
        report=next(x for x in reports if x['concept']['value']=='cycle.ACTUAL_OUTPUT')
        self.assertEqual(report['proposition_kind']['value'],'OBSERVATION');self.assertEqual(report['epistemic_mode']['value'],'REALIZED_OUTPUT_OBSERVATION')
        self.assertEqual(report['transformation_ref']['value'],'OWN_REALIZED_OUTPUT_REPORT_V1');self.assertEqual(report['value']['value'],'5')
        self.assertFalse(any('resource_before' in f.key or 'resource_after' in f.key for f in h['snapshots']['SECOND_REVIEW'].admitted_facts))
    def test_F04_no_deposit_same_positive_sponsor_information(self):
        null,nh=run_case('NULL',{'surface_fp':'0.15'});rich,rh=run_case('RICH',{'surface_fp':'0.15'})
        for label in ('SPONSOR','DEV_FINANCE','DEVELOP','FIRST_OPERATING','FIRST_OPERATING:finance','FIRST_OPERATING:funded'):
            self.assertEqual(nh['snapshots'][label],rh['snapshots'][label]);self.assertEqual(nh['policies'][label],rh['policies'][label])
        self.assertEqual(nh['first_output'].actual_extracted,D(0));self.assertFalse(null.market_clearing_records);self.assertEqual(null.state.projects['P'].status,'CLOSED')
        self.assertEqual(null.population.offworld['OFF:T1'],0);self.assertTrue(null.operating_cost_records)

    def test_F09_truth_mutation_between_epochs_rejected(self):
        from offworld_kernel.exploration_protocol import build_exploration_request
        from offworld_kernel.policy_runner import run_public_explorer_policy,public_explorer_policy_version
        from build6d_fixture import policy_epoch
        k,h=make_kernel();policy_epoch(k,h,'F09','PUB','1',build_exploration_request('F09',1,'EXP','RES'),('exploration.REMOTE_COST',),run_public_explorer_policy,public_explorer_policy_version())
        k.resources['RES'].remaining=D(19)
        with self.assertRaisesRegex(InvariantError,'tampered'):k.begin_decision_epoch('NEXT')
    def test_F10_direct_agent_mutation_guard(self):
        k,h=make_kernel();k.begin_decision_epoch('F10','F10');before=k._boundary_projection()
        with self.assertRaisesRegex(InvariantError,'direct mutation'):k.transition_project_status(1,'SPN','P','DEVELOPMENT')
        self.assertEqual(k._boundary_projection(),before)
    def test_F12_insufficient_migration_origin_headroom_cash(self):
        from offworld_kernel.policy_runner import run_public_settlement_transport_policy
        # Reuse admitted baseline state only as an immutable worker snapshot;
        # no historical or cached kernel is mutated.
        k,h=baseline('RICH');snapshot=h['snapshots']['TRANSPORT'];request=h['requests']['TRANSPORT']
        for key,value in (('population.EARTH_AVAILABLE','0'),('settlement.HABITAT_HEADROOM','0')):
            facts=tuple(replace(f,value=value) if f.key==key else f for f in snapshot.admitted_facts)
            result=run_public_settlement_transport_policy(replace(snapshot,admitted_facts=facts),request,'F12')
            self.assertNotEqual(result.decision.outcome.value,'AUTHORIZE')
        result=run_public_settlement_transport_policy(replace(snapshot,account_balance=D(0)),request,'F12_CASH')
        self.assertNotEqual(result.decision.outcome.value,'AUTHORIZE')
        low,lh=run_case('RICH',{'N':'9'});self.assertFalse(low.passenger_transport_departures);self.assertFalse(low.passenger_transport_arrivals);self.assertEqual(low.population.total(),9)
    def test_F13_in_transit_and_duplicate_arrival(self):
        k,h=baseline('RICH');departure=k.passenger_transport_departures[0];arrival=k.passenger_transport_arrivals[0]
        self.assertEqual(departure.passengers,10);self.assertEqual(arrival.passengers,10)
        e=next(e for e in k.causal_envelopes if e.action=='execute_transport_settlement_departure')
        import json
        row=next(json.loads(payload) for domain,path,payload in e.new_state if path=='population')
        fields=row['fields'];self.assertEqual(fields['earth']['value'],990)
        self.assertEqual(sum(v['value'] for _,v in fields['in_transit']['entries']),10)
        # Native duplicate-arrival validation is exercised before any mutation.
        from offworld_kernel.methodology import MethodologyHardenedBuild4Kernel
        prior=k._boundary_projection()
        with self.assertRaisesRegex(InvariantError,'already'):MethodologyHardenedBuild4Kernel.execute_passenger_transport_arrival(k,departure.arrival_time,departure.departure_id)
        self.assertEqual(k._boundary_projection(),prior)
    def test_F14_cross_resource_and_project_rejected(self):
        from offworld_kernel.market_protocol import build_sale_decision_request
        from offworld_kernel.policy_runner import run_sponsor_sale_policy
        k,h=baseline('RICH');snapshot=h['snapshots']['SALE'];request=h['requests']['SALE']
        # Protocol requests are exact; a decision for another request cannot
        # authorize extraction/sale even if numeric amounts happen to match.
        wrong=replace(request,id='CROSS',resource_id='OTHER')
        with self.assertRaises((ValueError,InvariantError)):h['policies']['SALE'].decision.validate_protocol(wrong)
        m,unused=make_kernel();q=policy_inputs(m,'SPN','10',('project.CASH_BALANCE',))[-1].consumption_request
        with self.assertRaisesRegex(InvariantError,'SCOPE'):admit_for_use(m,replace(q,scope='PROJECT:OTHER'))

    def test_F14_same_request_id_wrong_resource_is_blocked(self):
        from offworld_kernel.scheduler import ScheduledEvent,Phase
        k,h=baseline('RICH');decision=h['policies']['SALE'].decision
        ref=next(ref for ref,(_,did,_) in k._boundary_decisions.items() if did==decision.id)
        wrong=replace(h['requests']['SALE'],resource_id='OTHER')
        k._boundary_event_context=(ScheduledEvent('CROSS',D(10),Phase.OPERATIONS,0,'SPN','SYS:clear_market_sale'),(),(ref,))
        before=k._boundary_projection()
        try:
            with self.assertRaisesRegex(InvariantError,'executor request'):
                k._boundary_preflight('clear_market_sale',type(k).clear_market_sale.__get__(k),(10,'SPN',wrong,decision),{})
        finally:k._boundary_event_context=None
        self.assertEqual(k._boundary_projection(),before)
