import unittest
from dataclasses import replace
from decimal import Decimal as D

from simulation.offworld_mvp.build7.exploration_choice import choose_remote_characterization
from simulation.offworld_mvp.build7.opportunities import derive_mission_candidates, load_visible_inputs


class ExplorationChoiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog,screen=load_visible_inputs()
        cls.candidates=derive_mission_candidates(actor_id='PUB',capabilities={'EXPLORE'},
            calendar_year=2026,public_bodies=catalog['bodies'],accessibility_rows=screen['rows'])

    def choose(self,candidates=None,known=(),balance=D(100),key='VISIBLE-CHOICE'):
        return choose_remote_characterization(candidates=self.candidates if candidates is None else candidates,
            characterized_bodies=known,public_balance=balance,
            cost_for_candidate=lambda _candidate:D(10),decision_key=key)

    def test_wait_without_unresolved_eligible_candidate_or_budget(self):
        self.assertEqual(self.choose(()).outcome,'WAIT')
        self.assertEqual(self.choose(balance=D(0)).outcome,'WAIT')
        self.assertEqual(self.choose(known=(c.destination_body_id for c in self.candidates)).outcome,'WAIT')

    def test_one_visible_candidate_is_selected_and_unknown_access_stays_unknown(self):
        screened=next(c for c in self.candidates if c.accessibility_status=='SCREENED')
        unknown=next(c for c in self.candidates if c.accessibility_status=='UNKNOWN')
        self.assertEqual(self.choose((screened,unknown)).body_id,screened.destination_body_id)
        self.assertEqual(self.choose((unknown,)).outcome,'WAIT')
        self.assertEqual(unknown.accessibility_status,'UNKNOWN')

    def test_multiple_candidates_are_order_independent_without_body_score(self):
        a=self.choose()
        self.assertEqual(a,self.choose(reversed(self.candidates)))
        self.assertEqual(a.outcome,'SELECT')
        self.assertIn(a.body_id,{c.destination_body_id for c in self.candidates})

    def test_cheapest_eligible_mission_wins_independent_of_order(self):
        screened=[c for c in self.candidates if c.accessibility_status=='SCREENED'][:3]
        self.assertEqual(len(screened),3)
        costs={screened[0].candidate_id:D('3.794264'),
               screened[1].candidate_id:D('0.614'),
               screened[2].candidate_id:D('1.334')}
        def select(items):
            return choose_remote_characterization(candidates=items,
                characterized_bodies=(),public_balance=D(100),
                cost_for_candidate=lambda c:costs[c.candidate_id],decision_key='CHEAPEST')
        self.assertEqual(select(screened).candidate_id,screened[1].candidate_id)
        self.assertEqual(select(reversed(screened)),select(screened))
        self.assertEqual(select(screened).cost,D('0.614'))

    def test_hidden_truth_twin_and_visible_information_twin(self):
        from simulation.offworld_mvp.build6e.generated_world import (
            _material_family_truth, load_inputs, load_material_policy)
        from simulation.offworld_mvp.build7.generated_campaign import (
            _build_kernel, derive_world_mission_candidates, load_config)
        rows,_=load_inputs();body_key=next(key for key,row in rows.items()
            if row['material_model_applicability']=='SOLID')
        domain='GEN_BODY_'+body_key+'_SITE_1'
        block={'target_mass_kg':D(0)}
        truth_a=_material_family_truth(rows[body_key],block,load_material_policy(),
            'HIDDEN-A',body_key,domain)
        truth_b=_material_family_truth(rows[body_key],block,load_material_policy(),
            'HIDDEN-B',body_key,domain)
        self.assertNotEqual(truth_a,truth_b)
        world=dict(scenario_id='00000000-0000-0000-0000-000000000001',
                   scenario_key='SOLAR_WATER_HIDDEN_TWIN',body_count=90)
        a,ha=_build_kernel(None,load_config(),world_seed='SAME',world={**world,'sealed_world_digest':'0'*64})
        b,hb=_build_kernel(None,load_config(),world_seed='SAME',world={**world,'sealed_world_digest':'f'*64})
        ca=derive_world_mission_candidates(a,ha,2026)
        cb=derive_world_mission_candidates(b,hb,2026)
        self.assertEqual(ca,cb)
        before=self.choose(ca)
        self.assertEqual(before,self.choose(cb))
        after=self.choose(known=(before.body_id,))
        self.assertEqual(after.outcome,'SELECT')
        self.assertNotEqual(after.body_id,before.body_id)

    def test_capability_or_qualification_change_blocks_only_that_candidate(self):
        first=next(c for c in self.candidates if c.accessibility_status=='SCREENED')
        unavailable=replace(first,capability_status='UNAVAILABLE',qualification_state='CAPABILITY_UNAVAILABLE')
        self.assertEqual(self.choose((unavailable,)).outcome,'WAIT')


if __name__=='__main__':unittest.main()
