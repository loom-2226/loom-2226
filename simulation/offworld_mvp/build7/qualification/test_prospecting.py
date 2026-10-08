import unittest
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path

from offworld_kernel.mvp_state import BodyRemoteObservation, BODY_MATERIAL_QUESTIONS
from offworld_kernel.policy import DecisionSnapshot, SnapshotFact, FactState
from offworld_kernel.prospecting import (
    ProspectingRegion, SponsorProspectingRequest, SponsorProspectingOutcome,
    derive_mobilization, derive_prospecting_opportunities, choose_equivalent_region,
    build_prospecting_decision,
)
from offworld_kernel import policy_runner as workers
from simulation.offworld_mvp.build7.generated_campaign import (
    _build_kernel, derive_world_prospecting_opportunities, load_config,
    load_prospecting_scenario,
)
from loom_world_authority import store


class Increment4ProspectingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenario=load_prospecting_scenario()
        cls.world=dict(scenario_id='00000000-0000-0000-0000-000000000001',
            scenario_key='BUILD7_I4_UNIT',body_count=90,sealed_world_digest='0'*64)

    def regions(self,body='TEST_BODY'):
        regions=[]
        for n in range(1,11):
            key,location_id=store.prospecting_region_identity(body,n)
            regions.append(ProspectingRegion(body,key,str(location_id),n))
        return tuple(regions)

    def observations(self,body='TEST_BODY'):
        return tuple(BodyRemoteObservation('OBS-'+str(n),1,'PUB',body,question,
            'REMOTE','POSITIVE' if n==1 else 'NEGATIVE',False)
            for n,question in enumerate(BODY_MATERIAL_QUESTIONS,1))

    def opportunities(self,body='TEST_BODY'):
        keys=tuple('BODY:'+body+':'+question for question in BODY_MATERIAL_QUESTIONS)
        beliefs={key:(D('.8') if n==0 else D('.2')) for n,key in enumerate(keys)}
        priors={key:D('.5') for key in keys}
        return derive_prospecting_opportunities(actor_id='SPN',calendar_year=2026,
            body_key=body,regions=self.regions(body),observations=self.observations(body),
            beliefs=beliefs,priors=priors,scenario=self.scenario)

    def snapshot(self,opportunity,*,available='100',belief='0.8',prior='0.5',
                 include_information=True):
        facts=(
            SnapshotFact('prospecting.REQUIRED_CAPITAL',FactState.KNOWN,
                         str(opportunity.required_capital),'SCENARIO'),
            SnapshotFact('prospecting.INFORMATION_VALUE',FactState.KNOWN,
                         str(opportunity.prospective_information_value),'SCENARIO'),
            SnapshotFact('capital.AVAILABLE_F',FactState.KNOWN,available,'CAPITAL'),
        )
        beliefs=tuple((key,D(belief)) for key in opportunity.belief_keys)
        priors=tuple((key,D(prior)) for key in opportunity.belief_keys)
        return DecisionSnapshot('SPN','PRIVATE_SPONSOR','EARTH:USA','I4','1',D(0),
            ('REQUEST_FINANCE',),('RETURN',),
            opportunity.observation_ids if include_information else (),beliefs,priors,
            (),(),(),facts)

    def request(self,opportunity):
        return SponsorProspectingRequest('REQ',1,'SPN',opportunity.opportunity_id,
            'PROJECT',opportunity.body_key,opportunity.region_key,
            opportunity.location_id,opportunity.observation_ids,
            opportunity.belief_keys,opportunity.required_capital,
            opportunity.prospective_information_value).validate_protocol()

    def test_ten_uniform_regions_and_order_independent_tie_break(self):
        regions=self.regions()
        self.assertEqual(len(regions),10)
        self.assertEqual(tuple(r.ordinal for r in regions),tuple(range(1,11)))
        self.assertEqual(regions,self.regions())
        opportunities=self.opportunities()
        self.assertEqual(choose_equivalent_region(opportunities,'KEY'),
                         choose_equivalent_region(reversed(opportunities),'KEY'))
        source=Path(store.__file__).read_text()
        for name in ('CERES','MARS','BENNU','LUNA','CABEU'):
            self.assertNotIn("'"+name+"'",source[source.index('def prospecting_region_identity'):])

    def test_capital_function_is_bounded_and_commercial_strategic_inputs_are_distinct(self):
        zero=derive_mobilization(investment_proxy=D('5000000000000'),
            commercial_opportunity=D(0),scenario=self.scenario)
        commercial=derive_mobilization(investment_proxy=D('5000000000000'),
            commercial_opportunity=D(1),scenario=self.scenario)
        strategic_scenario=replace(self.scenario,base_salience=D(1))
        strategic=derive_mobilization(investment_proxy=D('5000000000000'),
            commercial_opportunity=D(0),scenario=strategic_scenario)
        self.assertEqual(zero[2:],(D(0),D(0)))
        self.assertGreater(commercial[3],0);self.assertGreater(strategic[3],0)
        self.assertLessEqual(commercial[2],self.scenario.m_max)
        self.assertLessEqual(strategic[2],strategic_scenario.m_max)

    def test_visible_evidence_drives_policy_and_unknown_waits_without_project(self):
        opportunity=self.opportunities()[0];request=self.request(opportunity)
        result=workers.run_sponsor_prospecting_policy(
            self.snapshot(opportunity),request,'KEY')
        self.assertEqual(result.decision.outcome,SponsorProspectingOutcome.INITIATE_PROJECT)
        wait=workers.run_sponsor_prospecting_policy(
            self.snapshot(opportunity,available='0'),request,'KEY')
        self.assertEqual(wait.decision.outcome,SponsorProspectingOutcome.WAIT)
        decline=workers.run_sponsor_prospecting_policy(
            self.snapshot(opportunity,belief='0.5'),request,'KEY')
        self.assertEqual(decline.decision.outcome,SponsorProspectingOutcome.DECLINE)
        blocked=workers.run_sponsor_prospecting_policy(
            self.snapshot(opportunity,include_information=False),request,'KEY')
        self.assertEqual(blocked.decision.outcome,SponsorProspectingOutcome.BLOCKED_UNKNOWN)

    def test_hidden_truth_has_no_policy_or_opportunity_input(self):
        opportunity=self.opportunities()[0];request=self.request(opportunity)
        snapshot=self.snapshot(opportunity)
        first=workers.run_sponsor_prospecting_policy(snapshot,request,'SAME')
        second=workers.run_sponsor_prospecting_policy(snapshot,request,'SAME')
        self.assertEqual(first,second)
        self.assertFalse(any('truth' in field for field in request.__dataclass_fields__))
        self.assertFalse(any('truth' in field for field in opportunity.__dataclass_fields__))

        world_a={**self.world,'sealed_world_digest':'0'*64}
        world_b={**self.world,'sealed_world_digest':'f'*64}
        kernel_a,history_a=_build_kernel(None,load_config(),world_seed='HIDDEN-A',world=world_a)
        kernel_b,history_b=_build_kernel(None,load_config(),world_seed='HIDDEN-B',world=world_b)
        body=history_a['visible_solar_bodies'][0]['semantic_key']
        for kernel in (kernel_a,kernel_b):
            keys=tuple('BODY:'+body+':'+question for question in BODY_MATERIAL_QUESTIONS)
            for n,(question,key) in enumerate(zip(BODY_MATERIAL_QUESTIONS,keys),1):
                obs=BodyRemoteObservation('VISIBLE-OBS-'+str(n),1,'PUB',body,question,
                    'REMOTE','POSITIVE' if n==1 else 'NEGATIVE',False)
                kernel.observations[obs.id]=obs
                kernel.agents['SPN'].information.add(obs.id)
                kernel.agents['SPN'].beliefs[key]=D('.8') if n==1 else D('.2')
        self.assertEqual(
            derive_world_prospecting_opportunities(kernel_a,history_a,2026,body),
            derive_world_prospecting_opportunities(kernel_b,history_b,2026,body))

    def test_sponsor_updates_its_own_body_belief_from_public_evidence(self):
        kernel,_=_build_kernel(None,load_config(),world_seed='I4-PUBLICATION',world=self.world)
        body='PUBLIC_BODY_FIXTURE';question=BODY_MATERIAL_QUESTIONS[0]
        key='BODY:'+body+':'+question
        observation=BodyRemoteObservation('PUBLIC-BODY-OBS',1,'PUB',body,question,
            'REMOTE','POSITIVE',False)
        kernel.observations[observation.id]=observation
        kernel.agents['PUB'].information.add(observation.id)
        kernel.agents['PUB'].beliefs[key]=D('.9')
        kernel.agents['SPN'].priors[key]=D('.2')
        artifact=kernel.publish_observation(1,'PUB',observation.id,'PUBLIC_FINANCIERS',
            (('SPN',key,D('.8'),D('.2')),))
        self.assertEqual(kernel.agents['SPN'].beliefs[key],D('.5'))
        self.assertNotEqual(kernel.agents['SPN'].beliefs[key],kernel.agents['PUB'].beliefs[key])
        self.assertIn(observation.id,kernel.agents['SPN'].information)
        self.assertIn(artifact.id,kernel.agents['SPN'].information)

    def test_authorized_project_creation_and_disbursement_reconcile(self):
        kernel,history=_build_kernel(None,load_config(),world_seed='I4-UNIT',world=self.world)
        opportunity=self.opportunities()[0];request=self.request(opportunity)
        snapshot=self.snapshot(opportunity)
        version=workers.sponsor_prospecting_policy_version()
        decision=build_prospecting_decision('DEC',request,snapshot,
            SponsorProspectingOutcome.INITIATE_PROJECT,
            'POSITIVE_CHARACTERIZATION_FUNDED','fixture authorization',version)
        investment=next(a for a in kernel.boundary_manifest.assertions
            if a.subject_id=='USA' and a.concept=='investment' and a.valid_from=='2026')
        mobilized=kernel.mobilize_country_capital(1,'USA',D(investment.value),D(1),
            history['prospecting_scenario'],'earth_capital_source','sponsor_funds')
        source_before=kernel.state.accounts['sponsor_funds'].balance
        creation=kernel.create_prospecting_project(1,'SPN',request,decision,
            'OFF:TEST_BODY:REGION','prospect_cash')
        kernel.add_commitment('COMMIT','SPN',creation.project_id,decision.amount)
        self.assertEqual(kernel.capital_coupling['USA']['F'],mobilized.mobilized_cash)
        self.assertEqual(kernel.state.accounts['prospect_cash'].balance,D(0))
        disbursement=kernel.disburse_country_capital(
            1,'USA','COMMIT','sponsor_funds',decision.amount,request,decision)
        self.assertEqual(kernel.state.accounts['sponsor_funds'].balance,
                         source_before-decision.amount)
        self.assertEqual(kernel.state.accounts['prospect_cash'].balance,decision.amount)
        self.assertEqual(kernel.capital_coupling['USA']['F'],
                         mobilized.mobilized_cash-decision.amount)
        self.assertEqual(kernel.capital_coupling['USA']['X'],decision.amount)
        self.assertEqual(kernel.earth_shadow_at(1)['capital_diverted_to_offworld'],decision.amount)
        self.assertEqual(disbursement.amount,decision.amount)
        self.assertEqual(kernel.state.projects['PROJECT'].status,'EXPLORING')
        self.assertFalse(kernel.resources);self.assertFalse(kernel.state.assets)
        with self.assertRaises(Exception):
            kernel.create_prospecting_project(1,'SPN',request,decision,
                'OFF:TEST_BODY:REGION','prospect_cash')


if __name__=='__main__':unittest.main()
