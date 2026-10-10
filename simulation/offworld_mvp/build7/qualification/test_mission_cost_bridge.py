import csv
import tempfile
import unittest
from decimal import Decimal as D
from pathlib import Path

from simulation.offworld_mvp.build7.exploration_choice import choose_remote_characterization
from simulation.offworld_mvp.build7.mission_costs import (
    INPUT, MissionCostLookup, REMOTE_EXPLORATION_MISSION_TYPE,
    policy_cost_assertion, public_mission_cost,
)
from simulation.offworld_mvp.build7.opportunities import derive_mission_candidates, load_visible_inputs


class MissionCostBridgeTests(unittest.TestCase):
    def test_full_input_normalization_and_no_trajectory(self):
        lookup=MissionCostLookup()
        self.assertEqual(len(lookup.rows),5400)
        cost=lookup.lookup(2026,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE)
        self.assertIsNotNone(cost)
        self.assertEqual(cost.model_currency,cost.usd_millions/D(1000))
        self.assertEqual(cost.source_sha256,lookup.source_sha256)
        self.assertIsNone(lookup.lookup(2026,'DACTYL','FLYBY'))
        self.assertIsNone(public_mission_cost(2026,'MISSING_BODY',REMOTE_EXPLORATION_MISSION_TYPE))

    def test_duplicate_key_is_rejected_and_missing_row_is_unavailable(self):
        with INPUT.open(newline='') as source:
            reader=csv.DictReader(source);fields=reader.fieldnames;rows=list(reader)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'costs.csv'
            with path.open('w',newline='') as output:
                writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader();writer.writerows(rows[:1])
            self.assertIsNone(MissionCostLookup(path).lookup(2027,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE))
            with path.open('a',newline='') as output:
                writer=csv.DictWriter(output,fieldnames=fields);writer.writerow(rows[0])
            with self.assertRaisesRegex(ValueError,'duplicate mission cost key'):
                MissionCostLookup(path)

    def test_year_and_candidate_budget_use_cost_not_flat_proxy(self):
        with self.assertRaisesRegex(ValueError,'year outside'):
            public_mission_cost(2036,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE)
        catalog,screen=load_visible_inputs()
        candidates=derive_mission_candidates(actor_id='PUB',capabilities={'EXPLORE'},
            calendar_year=2026,public_bodies=catalog['bodies'],accessibility_rows=screen['rows'])
        selected_cost=public_mission_cost(2026,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE)
        self.assertIsNotNone(selected_cost)
        costs={candidate.candidate_id:(selected_cost.model_currency if candidate.destination_body_id=='AMUN' else D('1000'))
            for candidate in candidates}
        choice=choose_remote_characterization(candidates=candidates,characterized_bodies=(),
            public_balance=selected_cost.model_currency,cost_for_candidate=lambda c:costs[c.candidate_id],
            decision_key='COST-DECISION')
        self.assertEqual(choice.body_id,'AMUN')
        self.assertEqual(choice.cost,selected_cost.model_currency)

    def test_existing_policy_fact_contract_carries_exact_selected_cost(self):
        cost=public_mission_cost(2026,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE)
        bound=policy_cost_assertion(cost,scenario_id='scenario',year=2026,body_id='AMUN',
            source_sha256=cost.source_sha256,source_ref=cost.source_ref)
        unavailable=policy_cost_assertion(None,scenario_id='scenario',year=2026,
            body_id='DACTYL',source_sha256=cost.source_sha256,
            source_ref='BUILD7_MISSION_COST:2026:DACTYL:ORBITAL_RECON')
        self.assertEqual((bound.assertion_id,bound.concept,bound.unit),
            ('BUILD7_MISSION_COST:2026:AMUN:ORBITAL_RECON','exploration.REMOTE_COST','MODEL_CURRENCY'))
        self.assertEqual(D(bound.value),cost.model_currency)
        self.assertEqual(bound.transformation_version,'USD_MILLIONS_DIV_1000')
        self.assertEqual(bound.source_hashes,(cost.source_sha256,))
        self.assertIn(('empirical_exchange_rate','NOT_CLAIMED'),bound.exception_flags)
        self.assertIsNone(unavailable.value)
        self.assertEqual(unavailable.reason_code,'NO_TRAJECTORY')

    def test_public_policy_authorizes_exact_selected_body_fact_cost(self):
        from offworld_kernel.policy import build_decision_snapshot
        from offworld_kernel.exploration_protocol import build_exploration_request
        from offworld_kernel.policy_runner import run_public_explorer_policy
        from simulation.offworld_mvp.build7.generated_campaign import _build_kernel, load_config
        from simulation.offworld_mvp.build7.runtime_flow import policy_inputs, snapshot_facts

        world={'scenario_id':'00000000-0000-0000-0000-000000000001',
            'scenario_key':'COST_BRIDGE_POLICY_TEST','body_count':90,
            'sealed_world_digest':'0'*64}
        kernel,_=_build_kernel(None,load_config(),world_seed='COST-BRIDGE',world=world)
        cost=public_mission_cost(2026,'AMUN',REMOTE_EXPLORATION_MISSION_TYPE)
        receipts=policy_inputs(kernel,'PUB','1',('exploration.REMOTE_COST',),
            {'exploration.REMOTE_COST':'AMUN'})
        facts=snapshot_facts(kernel,receipts)
        snapshot=build_decision_snapshot(kernel,'PUB','1',D(1),facts,admission_receipts=receipts)
        request=build_exploration_request('COST-BRIDGE-POLICY',1,'','','REMOTE',
            body_id='AMUN',question_ref='BODY_MATERIAL_CHARACTERIZATION')
        result=run_public_explorer_policy(snapshot,request,'COST-BRIDGE-POLICY-KEY')
        self.assertEqual(result.decision.authorized_cost,cost.model_currency)


if __name__=='__main__':unittest.main()
