import unittest

from engineering.civprop.contracts.timeline_causal_input_v0_3 import (
    REQUIRED_RULES, load_timeline_causal_input, timeline_lane, timeline_seed_events,
)


class TimelineCausalInputV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = load_timeline_causal_input(database="loom_dev")

    def test_validated_full_timeline_loaded(self):
        self.assertEqual(self.a.snapshot_state, "VALIDATED")
        self.assertEqual(len(self.a.milestones), 43)
        self.assertEqual({r["rule_key"] for r in self.a.interpretation_rules}, REQUIRED_RULES)

    def test_2026_2226_seeds_include_late_timeline(self):
        e = timeline_seed_events(self.a, start_year=2026, end_year=2226)
        ids = {x["payload"]["milestone_id"] for x in e}
        self.assertNotIn("SCI-2017-1I", ids)
        self.assertIn("TRN-MOD-HEAVY", ids)
        self.assertIn("TRN-MOD-NEP", ids)
        self.assertIn("SPEC-MOD-TORCH", ids)
        self.assertIn("TRN-2223-LOOM-CREW", ids)
        self.assertIn("SCI-2226-KITE", ids)
        self.assertEqual(len(e), 42)

    def test_every_seed_is_no_unlock(self):
        for e in timeline_seed_events(self.a, start_year=2026, end_year=2226):
            p=e["payload"]
            self.assertEqual(p["actor_capability_effect"], "NONE_WITHOUT_SEPARATE_ACTOR_STATE_EVENT")
            self.assertEqual(p["installed_capacity_effect"], "NONE_WITHOUT_SEPARATE_COMMISSIONED_ASSET")
            self.assertEqual(p["actor_access_effect"], "NONE_WITHOUT_SEPARATE_ACCESS_ADOPTION_STATE")
            self.assertEqual(p["physical_service_effect"], "NONE_WITHOUT_SEPARATE_ENGINEERING_QUALIFICATION")

    def test_lane_records_anchor_without_mutating_capability(self):
        state={
            "actor_capabilities":{"NASA":{"NEP":"UNKNOWN"}},
            "installed_capacity":{"NEP":None},
            "transport_services":{},
        }
        patch,children=timeline_lane(2050,state,{
            "milestone_id":"TRN-MOD-NEP",
            "authority_class":"PROVISIONAL_SIMULATION_SCAFFOLD",
            "epistemic_status":"AUTHOR_SCENARIO_MODERATE",
        })
        self.assertEqual(children,())
        self.assertEqual(set(patch),{"timeline_milestones_reached"})
        self.assertEqual(state["actor_capabilities"]["NASA"]["NEP"],"UNKNOWN")
        self.assertIsNone(state["installed_capacity"]["NEP"])
        self.assertEqual(state["transport_services"],{})

    def test_authority_classes_preserved(self):
        rows={x["milestone_id"]:x for x in self.a.milestones}
        self.assertEqual(rows["TRN-2100-TORCH-EMERGE"]["authority_class"],"GOVERNING_CANON")
        self.assertEqual(rows["TRN-MOD-NEP"]["epistemic_status"],"AUTHOR_SCENARIO_MODERATE")
        self.assertEqual(rows["SPEC-MOD-TORCH"]["epistemic_status"],"SPECULATIVE_FICTION")


if __name__ == "__main__":
    unittest.main()
