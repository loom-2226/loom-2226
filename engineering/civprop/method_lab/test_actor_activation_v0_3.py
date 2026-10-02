import json,unittest
from pathlib import Path
from engineering.civprop.method_lab.actor_activation_v0_3 import *

P=Path(__file__).resolve().parents[1]/"candidate_inputs"/"LOOM_GROUP_AGENT_SEED_2026_v0.3.json"

class ActorActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(P) as f: cls.seed=json.load(f)

    def test_all_233_load_dormant_with_unknown_budget(self):
        r=ActorRegistryV03.from_candidate_seed(self.seed)
        self.assertEqual(len(r.states()),233)
        self.assertTrue(all(x.level==ActivationLevel.DORMANT_CANDIDATE for x in r.states()))
        self.assertTrue(all(x.identity.budget_status=="UNKNOWN" for x in r.states()))

    def test_materialized_baseline_loads_functional_capacity_without_activating(self):
        bp=P.parent/"ACTOR_BASELINE_2026_V0_3.json"
        with open(bp) as f: baseline=json.load(f)
        r=ActorRegistryV03.from_actor_baseline(baseline)
        self.assertEqual(len(r.states()),233)
        self.assertEqual(sum(x.identity.functional_2026 for x in r.states()),228)
        self.assertTrue(all(x.level==ActivationLevel.DORMANT_CANDIDATE for x in r.states()))
        self.assertGreater(r.state("CAR_SPACEX").identity.financial_capacity_estimate,0)
        self.assertFalse(r.state("PRO_PLANETARY_RESOURCES").identity.functional_2026)

    def test_trigger_activates_only_category_relevance(self):
        r=ActorRegistryV03.from_candidate_seed(self.seed)
        out=r.mark_relevant(trigger_type="FINANCING_REQUEST",context_id="X",provenance_refs=("TEST",))
        self.assertTrue(out.actor_ids)
        self.assertTrue(all(r.state(x).identity.category=="CAPITAL" for x in out.actor_ids))
        self.assertTrue(all(r.state(x).level==ActivationLevel.RELEVANT for x in out.actor_ids))
        self.assertFalse(any(r.may_emit_consequential_action(x) for x in out.actor_ids))

    def test_relationship_or_identity_does_not_auto_activate(self):
        r=ActorRegistryV03.from_candidate_seed(self.seed)
        self.assertTrue(all(x.level==ActivationLevel.DORMANT_CANDIDATE for x in r.states()))

    def test_dormant_cannot_promote_directly(self):
        r=ActorRegistryV03.from_candidate_seed(self.seed)
        with self.assertRaisesRegex(ValueError,"DORMANT"):
            r.promote(r.states()[0].identity.actor_id,level=ActivationLevel.ACTIVE_TRANSACTIONAL,
                      context_id="X",provenance_refs=("TEST",))

    def test_deterministic_selection_and_demotion(self):
        a=ActorRegistryV03.from_candidate_seed(self.seed); b=ActorRegistryV03.from_candidate_seed(self.seed)
        x=a.mark_relevant(trigger_type="TRANSPORT_REQUIREMENT",context_id="T")
        y=b.mark_relevant(trigger_type="TRANSPORT_REQUIREMENT",context_id="T")
        self.assertEqual(x.actor_ids,y.actor_ids)
        a.demote_context("T")
        self.assertTrue(all(a.state(i).level==ActivationLevel.DORMANT_CANDIDATE for i in x.actor_ids))

if __name__=="__main__": unittest.main()
