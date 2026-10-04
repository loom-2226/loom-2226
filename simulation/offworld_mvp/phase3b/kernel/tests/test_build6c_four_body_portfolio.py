import copy
import json
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path

from offworld_kernel.build6c_four_body_fixture import (
    four_body_portfolio_kernel,
    body_terminal_report,
)
from offworld_kernel.kernel import InvariantError
from offworld_kernel.model import AssetKind, NodeKind
from offworld_kernel.named_portfolio import load_build6c_scenario, default_build6c_scenario_path
from offworld_kernel.project_activity import (
    ProjectActivityStatus,
    SponsorPortfolioDecisionOutcome,
    SponsorPortfolioReasonCode,
)
from offworld_kernel.project_study import (
    ProjectStudyMaturity,
    ProjectStudyResultStanding,
    ProjectStudyReviewOutcome,
)
import tests.test_build6b_staged_prospecting as build6b_tests


class Build6CFourBodyPortfolioTests(unittest.TestCase):
    def helper(self):
        h=build6b_tests.Build6BStagedProspectingTests()
        h.CHAIN='CHAIN-BUILD6C-001A'
        return h

    def authorize_ranked_set(self,h,k,trace,epoch_prefix,effective_time,candidates,count,first=False):
        last=None
        for i in range(count):
            r=h.portfolio_epoch(
                k,f'{epoch_prefix}-{i+1}',str(effective_time),tuple(candidates),
                f'Q-{epoch_prefix}-{i+1}',first=(first and i==0))
            trace.append(('DECIDE',str(effective_time),r['policy'].decision.outcome.value,
                          r['policy'].decision.selected_activity_id,
                          r['policy'].decision.reason_code.value))
            last=r
        return last

    def complete_review(self,h,k,scenario,trace,activity_id,complete,admit,review):
        spec=scenario.activity(activity_id)
        trace.append(('COMPLETE',str(complete),activity_id,spec.result_standing.value))
        h.complete_and_admit_epoch(
            k,f'E-COMP-{activity_id}',activity_id,str(complete),str(admit),
            spec.result_standing)
        trace.append(('ADMIT',str(admit),activity_id,f'INFO:{activity_id}:RESULT'))
        r=h.review_epoch(k,f'E-REVIEW-{activity_id}',activity_id,str(review))
        trace.append(('REVIEW',str(review),activity_id,r['policy'].decision.outcome.value))
        return r

    def run_canonical(self,reverse_candidates=False):
        h=self.helper()
        k,scenario=four_body_portfolio_kernel()
        trace=[]

        initial=[
            'BENNU-A1-RESOURCE',
            'MARS-A1-REMOTE',
            'MOON-A1-SURFACE',
            'CERES-A1-SURFACE',
        ]
        if reverse_candidates:
            initial=list(reversed(initial))

        self.authorize_ranked_set(
            h,k,trace,'E-AUTH-INITIAL','2026.25',initial,4,first=True)

        self.assertEqual(
            k.project_activities['MOON-A1-SURFACE'].status,
            ProjectActivityStatus.WAITING_WINDOW)
        self.assertEqual(
            k.project_activities['CERES-A1-SURFACE'].status,
            ProjectActivityStatus.WAITING_WINDOW)
        self.assertEqual(k.project_activity_available_capital('SPN'),D('80'))

        h.start_and_spend_epoch(k,'E-START-BENNU-A1','BENNU-A1-RESOURCE','2026.25')
        trace.append(('START_SPEND','2026.25','BENNU-A1-RESOURCE','15'))
        h.start_and_spend_epoch(k,'E-START-MARS-A1','MARS-A1-REMOTE','2026.25')
        trace.append(('START_SPEND','2026.25','MARS-A1-REMOTE','20'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('185'))
        self.assertEqual(k.project_activity_available_capital('SPN'),D('80'))

        self.complete_review(
            h,k,scenario,trace,'BENNU-A1-RESOURCE','2027.00','2027.01','2027.02')
        self.assertEqual(
            k.project_study_states['PROJ:BENNU:HYDRATED_CARBONACEOUS'].maturity,
            ProjectStudyMaturity.RESOURCE_ASSESSMENT)

        r=h.portfolio_epoch(
            k,'E-AUTH-BENNU-A2','2027.10',('BENNU-A2-CONCEPT',),'Q-BENNU-A2')
        trace.append(('DECIDE','2027.10',r['policy'].decision.outcome.value,
                      r['policy'].decision.selected_activity_id,
                      r['policy'].decision.reason_code.value))
        h.start_and_spend_epoch(k,'E-START-BENNU-A2','BENNU-A2-CONCEPT','2027.10')
        trace.append(('START_SPEND','2027.10','BENNU-A2-CONCEPT','25'))

        h.start_and_spend_epoch(k,'E-START-MOON-A1','MOON-A1-SURFACE','2027.50')
        trace.append(('START_SPEND','2027.50','MOON-A1-SURFACE','35'))
        self.assertEqual(k.project_activity_available_capital('SPN'),D('55'))

        self.complete_review(
            h,k,scenario,trace,'MARS-A1-REMOTE','2027.75','2027.76','2027.77')
        self.assertEqual(
            k.project_study_states['PROJ:MARS:WATER_ISRU'].maturity,
            ProjectStudyMaturity.REMOTE_CHARACTERIZED)

        r=h.portfolio_epoch(
            k,'E-MARS-A2-DEFER-1','2027.78',('MARS-A2-SURFACE',),'Q-MARS-A2-D1')
        trace.append(('DECIDE','2027.78',r['policy'].decision.outcome.value,'',
                      r['policy'].decision.reason_code.value))
        self.assertEqual(r['policy'].decision.outcome,SponsorPortfolioDecisionOutcome.DEFER)
        self.assertEqual(
            r['policy'].decision.reason_code,
            SponsorPortfolioReasonCode.INSUFFICIENT_AVAILABLE_CAPITAL)
        self.assertEqual(
            k.project_activities['MARS-A2-SURFACE'].status,
            ProjectActivityStatus.PROPOSED)

        self.complete_review(
            h,k,scenario,trace,'BENNU-A2-CONCEPT','2028.10','2028.11','2028.12')
        self.assertEqual(
            k.project_study_states['PROJ:BENNU:HYDRATED_CARBONACEOUS'].maturity,
            ProjectStudyMaturity.RESOURCE_ASSESSMENT)

        h.start_and_spend_epoch(k,'E-START-CERES-A1','CERES-A1-SURFACE','2028.50')
        trace.append(('START_SPEND','2028.50','CERES-A1-SURFACE','70'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('55'))
        self.assertEqual(k.project_activity_available_capital('SPN'),D('55'))

        self.complete_review(
            h,k,scenario,trace,'MOON-A1-SURFACE','2029.00','2029.01','2029.02')
        self.assertEqual(
            k.project_study_states['PROJ:MOON:POLAR_VOLATILES'].maturity,
            ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED)

        r=h.portfolio_epoch(
            k,'E-AUTH-MOON-A2','2029.10',('MOON-A2-ASSESS',),'Q-MOON-A2')
        trace.append(('DECIDE','2029.10',r['policy'].decision.outcome.value,
                      r['policy'].decision.selected_activity_id,
                      r['policy'].decision.reason_code.value))
        h.start_and_spend_epoch(k,'E-START-MOON-A2','MOON-A2-ASSESS','2029.10')
        trace.append(('START_SPEND','2029.10','MOON-A2-ASSESS','30'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('25'))

        r=h.portfolio_epoch(
            k,'E-MARS-A2-DEFER-2','2030.50',('MARS-A2-SURFACE',),'Q-MARS-A2-D2')
        trace.append(('DECIDE','2030.50',r['policy'].decision.outcome.value,'',
                      r['policy'].decision.reason_code.value))
        self.assertEqual(r['policy'].decision.outcome,SponsorPortfolioDecisionOutcome.DEFER)
        self.assertEqual(
            r['policy'].decision.reason_code,
            SponsorPortfolioReasonCode.INSUFFICIENT_AVAILABLE_CAPITAL)

        self.complete_review(
            h,k,scenario,trace,'MOON-A2-ASSESS','2030.60','2030.61','2030.62')
        self.assertEqual(
            k.project_study_states['PROJ:MOON:POLAR_VOLATILES'].maturity,
            ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED)

        self.complete_review(
            h,k,scenario,trace,'CERES-A1-SURFACE','2034.50','2034.51','2034.52')
        self.assertEqual(
            k.project_study_states['PROJ:CERES:VOLATILES'].maturity,
            ProjectStudyMaturity.SURFACE_OR_SAMPLE_CHARACTERIZED)

        r=h.portfolio_epoch(
            k,'E-AUTH-CERES-A2','2034.60',('CERES-A2-ASSESS',),'Q-CERES-A2')
        trace.append(('DECIDE','2034.60',r['policy'].decision.outcome.value,
                      r['policy'].decision.selected_activity_id,
                      r['policy'].decision.reason_code.value))
        h.start_and_spend_epoch(k,'E-START-CERES-A2','CERES-A2-ASSESS','2034.60')
        trace.append(('START_SPEND','2034.60','CERES-A2-ASSESS','25'))
        self.assertEqual(k.state.accounts['sponsor_funds'].balance,D('0'))

        self.complete_review(
            h,k,scenario,trace,'CERES-A2-ASSESS','2035.60','2035.61','2035.62')
        self.assertEqual(
            k.project_study_states['PROJ:CERES:VOLATILES'].maturity,
            ProjectStudyMaturity.RESOURCE_ASSESSMENT)

        k.assert_methodology_invariants()
        return k,scenario,tuple(trace),body_terminal_report(k,scenario)

    def test_canonical_four_body_portfolio_and_replay(self):
        k1,s1,t1,r1=self.run_canonical()
        k2,s2,t2,r2=self.run_canonical()
        self.assertEqual(s1.scenario_sha256,s2.scenario_sha256)
        self.assertEqual(t1,t2)
        self.assertEqual(r1,r2)
        self.assertEqual(
            k1.decision_epoch_state_fingerprint(),
            k2.decision_epoch_state_fingerprint())

        self.assertEqual(k1.state.accounts['sponsor_funds'].balance,D('0'))
        self.assertEqual(k1.state.accounts['study_supplier'].balance,D('220'))
        self.assertEqual(k1.project_activity_available_capital('SPN'),D('0'))
        self.assertEqual(len(k1.state.transactions),14)
        self.assertEqual(len(k1.project_activity_expense_records),7)
        self.assertEqual(sum((r.amount for r in k1.project_activity_expense_records),D('0')),D('220'))
        knowledge=[a for a in k1.state.assets.values() if a.kind==AssetKind.KNOWLEDGE]
        self.assertEqual(len(knowledge),7)
        self.assertEqual(sum((a.book_value for a in knowledge),D('0')),D('220'))

        by_body={r['body_id']:r for r in r1}
        self.assertEqual(by_body['BENNU']['study_maturity'],'RESOURCE_ASSESSMENT')
        self.assertEqual(by_body['MARS']['study_maturity'],'REMOTE_CHARACTERIZED')
        self.assertEqual(by_body['MOON']['study_maturity'],'SURFACE_OR_SAMPLE_CHARACTERIZED')
        self.assertEqual(by_body['CERES']['study_maturity'],'RESOURCE_ASSESSMENT')
        self.assertTrue(all(r['project_status']=='EXPLORING' for r in r1))
        self.assertIn(
            ('MARS-A2-SURFACE','PROPOSED'),
            by_body['MARS']['activities'])

    def test_initial_candidate_order_does_not_change_history(self):
        k1,s1,t1,r1=self.run_canonical(reverse_candidates=False)
        k2,s2,t2,r2=self.run_canonical(reverse_candidates=True)
        self.assertEqual(r1,r2)
        self.assertEqual(
            k1.decision_epoch_state_fingerprint(),
            k2.decision_epoch_state_fingerprint())

    def test_2026_evidence_packet_is_pinned_and_scope_limited(self):
        k,scenario=four_body_portfolio_kernel()
        self.assertEqual(
            scenario.scenario_sha256,
            'be4de46ef8182949e99dd119f794eca9190edc7de0568f59a03a7cd05867e502')
        self.assertEqual(set(k.body_portfolio_bindings),{'MOON','MARS','CERES','BENNU'})
        expected=set()
        for binding in scenario.body_bindings:
            expected.update(binding.evidence_ids)
        self.assertTrue(expected<=k.agents['SPN'].information)
        self.assertEqual(set(k.named_body_evidence_records),expected)
        raw=json.loads(default_build6c_scenario_path().read_text())
        forbidden={'opening_inventory','opening_stock','recoverable_tonnage','reserve_tonnage','ore_grade'}
        for body in raw['bodies']:
            for evidence in body['evidence']:
                self.assertTrue(forbidden.isdisjoint({str(k).lower() for k in evidence}))
        for rec in k.named_body_evidence_records.values():
            self.assertTrue(rec.admitted_claim)
        self.assertIn('PRESENT_UNQUANTIFIED',
                      {r.abundance_semantics for r in k.named_body_evidence_records.values()})
        self.assertIn('UNKNOWN',
                      {r.abundance_semantics for r in k.named_body_evidence_records.values()})

    def test_source_blob_tamper_is_rejected(self):
        data=json.loads(default_build6c_scenario_path().read_text())
        data=copy.deepcopy(data)
        data['authority']['campaign_assertions_blob']='0'*40
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'scenario.json'
            p.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'pinned source blob drift'):
                load_build6c_scenario(p)

    def test_one_earth_economy_and_no_technology_unlock_state(self):
        k,_=four_body_portfolio_kernel()
        earth_nodes=[n for n in k.state.nodes.values() if n.kind==NodeKind.EARTH]
        offworld=[n for n in k.state.nodes.values() if n.kind==NodeKind.OFFWORLD]
        self.assertEqual([n.id for n in earth_nodes],['EARTH:X'])
        self.assertEqual({n.id for n in offworld},
                         {'SOL:MOON','SOL:MARS','SOL:CERES','SOL:BENNU'})
        self.assertEqual(k.technology_capability_states,{})
        self.assertEqual(k.transport_relationships,{})

    def test_body_project_bindings_are_distinct_and_consistent(self):
        k,scenario=four_body_portfolio_kernel()
        for binding in scenario.body_bindings:
            self.assertEqual(k.state.projects[binding.project_id].node_id,binding.node_id)
            self.assertEqual(
                k.project_study_states[binding.project_id].maturity,
                binding.opening_maturity)
            for evidence_id in binding.evidence_ids:
                rec=k.named_body_evidence_records[evidence_id]
                self.assertEqual(rec.body_id,binding.body_id)
                self.assertEqual(rec.project_id,binding.project_id)

    def test_calendar_horizon_and_body_specific_waits(self):
        k,scenario,trace,_=self.run_canonical()
        times=[]
        times.extend(r.effective_time for r in k.project_activity_transition_records)
        times.extend(r.admitted_at for r in k.project_activity_information_records)
        times.extend(r.effective_time for r in k.project_study_review_records)
        self.assertTrue(times)
        self.assertGreaterEqual(min(times),scenario.horizon_start)
        self.assertLessEqual(max(times),scenario.horizon_end)
        moon=k.project_activities['MOON-A1-SURFACE']
        ceres=k.project_activities['CERES-A1-SURFACE']
        self.assertEqual(moon.authorized_at,D('2026.25'))
        self.assertEqual(moon.actual_start,D('2027.50'))
        self.assertEqual(ceres.authorized_at,D('2026.25'))
        self.assertEqual(ceres.actual_start,D('2028.50'))
        self.assertGreater(ceres.actual_completion,moon.actual_completion)

    def test_mars_surface_campaign_is_capital_blocked_not_truth_blocked(self):
        k,scenario,trace,_=self.run_canonical()
        defers=[
            x for x in trace
            if x[0]=='DECIDE' and x[2]=='DEFER'
            and x[4]=='INSUFFICIENT_AVAILABLE_CAPITAL'
        ]
        self.assertEqual([x[1] for x in defers],['2027.78','2030.50'])
        self.assertEqual(
            k.project_activities['MARS-A2-SURFACE'].status,
            ProjectActivityStatus.PROPOSED)
        self.assertEqual(
            k.project_study_states['PROJ:MARS:WATER_ISRU'].maturity,
            ProjectStudyMaturity.REMOTE_CHARACTERIZED)
        # No resource hidden truth is required to produce this deferral.
        self.assertEqual(k.resources,{})


if __name__=='__main__':
    unittest.main()
