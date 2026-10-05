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
        k,h=make_kernel(overrides={'f':'0'})
        with self.assertRaisesRegex(InvariantError,'RESOURCE'):system_epoch(k,h,'add_commitment','1',('ZERO','PUB','EXP',D(10)))
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
    def test_F12_all_A1_A9_each_epoch(self):
        for world in ('NULL','SPARSE','RICH'):
            k,h=baseline(world);self.assertTrue(h['audits']);self.assertTrue(all(all(row.values()) for row in h['audits']))
    def test_F13_finite_cohort_bound(self):
        k,h=make_kernel(overrides={'N':'348178046'})
        with self.assertRaisesRegex(InvariantError,'population bound'):k.begin_decision_epoch('F13','F13')
    def test_F14_population_conserved(self):
        for world in ('SPARSE','RICH'):
            k,h=baseline(world);self.assertEqual(k.population.total(),1000);self.assertEqual(k.population.offworld['OFF:T1'],10);self.assertFalse(any(k.population.in_transit.values()))
    def test_F15_resource_conserved_and_second_output_distinguishes(self):
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
    def test_information_driven_decisions_and_distinct_times(self):
        s,sh=baseline('SPARSE');r,rh=baseline('RICH')
        for label in ('REMOTE','SURFACE','PUBLICATION','SPONSOR','DEV_FINANCE','DEVELOP','FIRST_OPERATING','SALE'):
            self.assertEqual(sh['snapshots'][label],rh['snapshots'][label]);self.assertEqual(sh['policies'][label],rh['policies'][label])
        delayed=[e for e in r.causal_envelopes if e.action=='execute_development_stage']
        self.assertTrue(all(D(e.decision_time)==D(5)<D(e.realized_time) for e in delayed));self.assertTrue(any(e.source_times for e in r.causal_envelopes))

    def test_F06_forged_OPEX_record_not_admitted(self):
        from offworld_kernel.causal_trace import archive
        from offworld_kernel.scheduler import ScheduledEvent,Phase
        k,h=baseline('RICH');d=h['policies']['FIRST_OPERATING:funded'].decision
        ref=next(ref for ref,(_,did,_) in k._boundary_decisions.items() if did==d.id)
        event=ScheduledEvent('F06',D(14),Phase.OPERATIONS,0,'SPN','SYS:resolve_operating_extraction')
        k._boundary_event_context=(event,(),(ref,))
        try:
            rec=replace(k.operating_cost_records[0],transaction_id='FORGED')
            with self.assertRaisesRegex(InvariantError,'LINEAGE'):k._boundary_preflight('resolve_operating_extraction',k.resolve_operating_extraction,(9,'SPN',h['requests']['FIRST_OPERATING:funded'],d,rec),{})
        finally:k._boundary_event_context=None
    def test_F08_unqualified_transport(self):
        k,h=run_case('RICH',{'technology_qualified':'FALSE'});self.assertFalse(k.passenger_transport_departures);self.assertEqual(k.population.offworld['OFF:T1'],0)
    def test_F09_missing_transport(self):
        k,h=run_case('RICH',{'relationship_registered':'FALSE'});self.assertFalse(k.passenger_transport_departures);self.assertEqual(k.population.offworld['OFF:T1'],0)
    def test_L08_buyer_block_has_no_financial_resource_delta(self):
        k,h=run_case('RICH',{'B':'0'});self.assertIn('AFFORDABILITY',h['blocked']);e=k.causal_envelopes[-1]
        self.assertEqual(e.prior_state,e.new_state);self.assertEqual(k.state.accounts['earth_market'].balance,D(0));self.assertEqual(k.colonies['OFF:T1'].resource_inventory,D(5))
