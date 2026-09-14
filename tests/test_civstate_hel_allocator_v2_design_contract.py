import unittest

from engineering.civstate.hel_allocator_v2_design_contract import (
    build_design_contract,
    validate_candidate_plan,
)


class HelAllocatorV2DesignContractTests(unittest.TestCase):
    def test_contract_separates_upstream_drivers_from_downstream_consequences(self):
        contract = build_design_contract()
        self.assertIn("civ_governance_profile.primary_owner_operator", contract["admissible_upstream_driver_fields"])
        self.assertIn("civ_influence_edge.influence_weight", contract["admissible_upstream_driver_fields"])
        self.assertIn("civ_node_texture_overlay", contract["forbidden_as_allocator_inputs"])
        self.assertIn("civ_social_state", contract["forbidden_as_allocator_inputs"])
        self.assertEqual(contract["name_inference_authority"], "ZERO")
        self.assertEqual(contract["random_jitter_authority"], "ZERO")

    def test_contract_requires_a20_conservation(self):
        contract = build_design_contract()
        self.assertIn("resident_population", contract["hard_conservation_fields"])
        self.assertIn("workforce", contract["hard_conservation_fields"])
        self.assertIn("annual_value_added", contract["hard_conservation_fields"])
        self.assertEqual(contract["conservation_authority"], "LOCKED_CANON_A20")

    def test_candidate_plan_may_refuse_for_insufficient_authoritative_differentiation(self):
        candidate = {
            "uses_display_names": False,
            "uses_random_jitter": False,
            "uses_downstream_fields": False,
            "preserves_hard_totals": True,
            "preserves_residual_accounting": True,
            "pair_driver_distinctness": {
                "NODE:HEL-03|NODE:HEL-10": False,
                "NODE:HEL-04|NODE:HEL-06": False,
                "NODE:HEL-07|NODE:HEL-08": False,
            },
            "forces_pair_uniqueness": False,
        }
        result = validate_candidate_plan(candidate)
        self.assertEqual(result["status"], "PASS_WITH_UNRESOLVED_DIFFERENTIATION")
        self.assertEqual(result["mutation_authority"], "ZERO")

    def test_candidate_plan_rejects_cosmetic_or_nonconserving_diversification(self):
        candidate = {
            "uses_display_names": True,
            "uses_random_jitter": True,
            "uses_downstream_fields": True,
            "preserves_hard_totals": False,
            "preserves_residual_accounting": False,
            "pair_driver_distinctness": {},
            "forces_pair_uniqueness": True,
        }
        result = validate_candidate_plan(candidate)
        self.assertEqual(result["status"], "REJECT")
        self.assertGreaterEqual(len(result["violations"]), 5)


if __name__ == "__main__":
    unittest.main()
