"""Opportunity identity coverage, without preferred bodies or investment histories."""
import os
import unittest
from dataclasses import replace
from decimal import Decimal as D
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import patch

from offworld_kernel import policy_runner as workers
from offworld_kernel.mvp_state import BodyRemoteObservation, BODY_MATERIAL_QUESTIONS
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from simulation.offworld_mvp.build7 import generated_campaign as campaign
from simulation.offworld_mvp.build7 import runtime_flow as flow


class AnnualOpportunityTests(unittest.TestCase):
    def visible_fixture(self, seed):
        catalog,_=campaign._load_solar_catalog()
        bodies=sorted((row['semantic_key'] for row in catalog['bodies']),
            key=lambda body:sha256((seed+'|'+body).encode()).hexdigest())[:2]
        actor=SimpleNamespace(information=set(),beliefs={},priors={})
        observations={}
        for body in bodies:
            for question in BODY_MATERIAL_QUESTIONS:
                oid=body+':'+question
                observations[oid]=BodyRemoteObservation(oid,1,'PUB',body,question,
                    'REMOTE','POSITIVE',False)
                actor.information.add(oid)
                key='BODY:'+body+':'+question
                actor.beliefs[key]=D('.8');actor.priors[key]=D('.5')
        # A value-only view: candidate construction has no WORLD payload to read.
        kernel=SimpleNamespace(agents={'SPN':actor},observations=observations,
                               state=SimpleNamespace(projects={}))
        history={'prospecting_scenario':campaign.load_prospecting_scenario()}
        return kernel,history,bodies

    def snapshot(self,k,*,capital='100',status='EXPLORING'):
        actor=k.agents['SPN']
        facts=tuple(SnapshotFact(key,FactState.KNOWN,value,'CONTROLLED_VISIBLE_FIXTURE')
            for key,value in (('project.STATUS',status),
                ('study.CURRENT_MATURITY','REMOTE_CHARACTERIZED'),
                ('portfolio.AVAILABLE_CAPITAL','20'),('capital.AVAILABLE_F',capital)))
        return DecisionSnapshot('SPN','PRIVATE_SPONSOR','EARTH:USA','GAPS','2',D(0),
            ('REQUEST_FINANCE',),('RETURN',),tuple(sorted(actor.information)),
            tuple(sorted(actor.beliefs.items())),tuple(sorted(actor.priors.items())),
            (),(),(),facts)

    def test_all_visible_regions_except_existing_project_identity_reach_policy(self):
        for seed in ('GAP-IDENTITY-A','GAP-IDENTITY-B','GAP-IDENTITY-C'):
            with self.subTest(seed=seed):
                k,h,bodies=self.visible_fixture(seed)
                occupied=campaign.derive_world_prospecting_opportunities(k,h,2027,bodies[0])[0]
                pid='PROSPECT:'+occupied.body_key+':'+occupied.region_key
                k.state.projects[pid]=object()
                for year in (2027,2032):
                    request=campaign._annual_sponsor_opportunity_request(k,h,year,pid)
                    self.assertEqual(request.existing_project_id,pid)
                    expected={o.opportunity_id for body in bodies
                        for o in campaign.derive_world_prospecting_opportunities(k,h,year,body)
                        if 'PROSPECT:'+body+':'+o.region_key!=pid}
                    self.assertEqual({c.opportunity_id for c in request.candidates},expected)
                    self.assertEqual(len(request.candidates),19)
                    self.assertEqual(sum(c.body_key==bodies[0] for c in request.candidates),9)
                    snapshot=self.snapshot(k)
                    first=workers.run_sponsor_opportunity_policy(snapshot,request,'KEY')
                    self.assertIn(first.decision.selected_opportunity_id,expected)
                    permuted=replace(request,candidates=tuple(reversed(request.candidates)))
                    second=workers.run_sponsor_opportunity_policy(snapshot,permuted,'KEY')
                    self.assertEqual(first.decision.selected_opportunity_id,
                                     second.decision.selected_opportunity_id)
                original=campaign._annual_sponsor_opportunity_request(k,h,2032,pid)
                k.observations=dict(reversed(tuple(k.observations.items())))
                derive=campaign.derive_world_prospecting_opportunities
                with patch.object(campaign,'derive_world_prospecting_opportunities',
                        side_effect=lambda *a:tuple(reversed(derive(*a)))):
                    self.assertEqual(original,
                        campaign._annual_sponsor_opportunity_request(k,h,2032,pid))

    def test_information_and_financing_are_policy_inputs_not_conductor_filters(self):
        k,h,bodies=self.visible_fixture('GAP-VISIBLE-STATE')
        actor=k.agents['SPN']
        request=campaign._annual_sponsor_opportunity_request(k,h,2028,'EXISTING')
        self.assertEqual(len(request.candidates),20)
        for capital,status,outcome in (('0','EXPLORING','RETAIN_PROJECT'),
                                      ('0','ABANDONED','WAIT')):
            result=workers.run_sponsor_opportunity_policy(
                self.snapshot(k,capital=capital,status=status),request,'KEY')
            self.assertEqual(result.decision.outcome.value,outcome)
        actor.beliefs=dict(actor.priors)
        nonpositive=campaign._annual_sponsor_opportunity_request(k,h,2028,'EXISTING')
        self.assertEqual(len(nonpositive.candidates),20)
        self.assertTrue(all(c.commercial_opportunity==0 for c in nonpositive.candidates))
        result=workers.run_sponsor_opportunity_policy(self.snapshot(k,status='ABANDONED'),
            nonpositive,'KEY')
        self.assertEqual(result.decision.outcome.value,'WAIT')
        actor.information={oid for oid in actor.information if not oid.startswith(bodies[1]+':')}
        visible=campaign._annual_sponsor_opportunity_request(k,h,2028,'EXISTING')
        self.assertEqual({c.body_key for c in visible.candidates},{bodies[0]})
        self.assertEqual(len(visible.candidates),10)


@unittest.skipUnless(os.getenv('PGSERVICEFILE'),'governed persistence service required')
class GeneratedRegionInvestmentTests(unittest.TestCase):
    def test_generated_same_body_alternatives_authorization_accounting_and_replay(self):
        """Bounded scheduling fixture; no synthetic observations or authorization.

        These independent seeds are not chosen for an outcome. Refusal is valid.
        The historical campaign separately exercises normal annual scheduling.
        """
        import psycopg
        for seed in ('BUILD7-FINAL-GAPS-A','BUILD7-FINAL-GAPS-B'):
            with self.subTest(seed=seed):
                opened=campaign.start_world_run(reference_service='reference_reader',
                    science_writer_service='science_writer',world_writer_service='world_writer',
                    runtime_service='runtime',world_seed=seed)
                run_id=opened['run_id']

                def execute():
                    k,h,_,opening=campaign.run_world_prospecting_initiation(
                        reference_service='reference_reader',runtime_service='runtime',
                        run_id=run_id,_return_runtime=True)
                    if 'project_id' not in opening:
                        return k,h,{'opening':opening.get('prospecting_decision'),'annual':None}
                    pid=opening['project_id'];binding=h['named_binding']
                    before_cash=k.state.accounts[k.state.projects[pid].cash_account_id].balance
                    before_capital=dict(k.capital_coupling['USA'])
                    count=len(k.state.projects)
                    campaign._record_empty_year(k,h,2027)
                    flow.system_epoch(k,h,'initialize_region_study','2',
                        (2,pid,opening['prospecting_location_id']),
                        decision_refs=(h['prospecting_decision_ref'],))
                    request=campaign._annual_sponsor_opportunity_request(k,h,2027,pid)
                    self.assertEqual(len(request.candidates),9)
                    self.assertEqual({c.body_key for c in request.candidates},
                                     {opening['selected_body_id']})
                    decision,_=flow.policy_epoch(k,h,'GAP_SPONSOR_OPPORTUNITY','SPN','2',
                        request,request.required_fact_keys,workers.run_sponsor_opportunity_policy,
                        workers.sponsor_opportunity_policy_version())
                    creation=None;investment=None
                    if decision.outcome.value=='CONSIDER_PROSPECTING':
                        candidate=next(c for c in request.candidates
                            if c.opportunity_id==decision.selected_opportunity_id)
                        investment,creation=campaign._execute_annual_prospecting_investment(
                            k,h,2027,candidate,'runtime',binding)
                    amount=D(0) if creation is None else investment.amount
                    self.assertEqual(len(k.state.projects),count+int(creation is not None))
                    self.assertEqual(k.capital_coupling['USA']['F'],before_capital['F']-amount)
                    self.assertEqual(k.capital_coupling['USA']['X'],before_capital['X']+amount)
                    self.assertEqual(k.state.accounts['sponsor_funds'].balance,
                                     k.capital_coupling['USA']['F'])
                    self.assertEqual(k.state.accounts[k.state.projects[pid].cash_account_id].balance,
                                     before_cash)
                    self.assertEqual(len(k.state.commitments),len(k.country_capital_disbursement_records))
                    self.assertEqual(sum(r.amount for r in k.country_capital_disbursement_records),
                                     k.capital_coupling['USA']['X'])
                    if creation is not None:
                        self.assertNotEqual(creation.project_id,pid)
                        self.assertEqual(k.state.accounts[k.state.projects[creation.project_id].cash_account_id].balance,amount)
                    self.assertFalse(k.resources)
                    campaign._record_empty_year(k,h,2028)
                    later=campaign._annual_sponsor_opportunity_request(k,h,2028,pid)
                    self.assertEqual(len(later.candidates),10-len(k.state.projects))
                    later_decision,_=flow.policy_epoch(k,h,'GAP_LATER_OPPORTUNITY','SPN','3',
                        later,later.required_fact_keys,workers.run_sponsor_opportunity_policy,
                        workers.sponsor_opportunity_policy_version())
                    return k,h,dict(opening=opening['prospecting_decision'],
                        annual=decision.outcome.value,
                        investment=None if investment is None else investment.outcome.value,
                        projects=tuple(sorted(k.state.projects)),
                        capital=dict(k.capital_coupling['USA']),later=later_decision.outcome.value)

                def counts():
                    with psycopg.connect(service='runtime') as conn:
                        return tuple(conn.execute('SELECT count(*) FROM '+table+' WHERE run_id=%s',
                            (run_id,)).fetchone()[0] for table in ('wa_run.project',
                            'wa_run.project_location','wa_run.observation','wa_info.belief'))

                k,h,first=execute();before=counts()
                _,replayed,replay=execute()
                self.assertEqual(first,replay)
                self.assertTrue(all(status=='ALREADY_MATCHED' for _,status in replayed['epoch_commits']))
                self.assertEqual(counts(),before)
                print('GENERIC_GAP_EVIDENCE',seed,run_id,first,
                      'replay_epochs',len(replayed['epoch_commits']),flush=True)


if __name__=='__main__':unittest.main()
