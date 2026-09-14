import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "engineering" / "civstate" / "hel_parent_pool_audit.py"
spec = importlib.util.spec_from_file_location("hel_parent_pool_audit", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ParentPoolAuditTests(unittest.TestCase):
    def test_residual_only_when_semantics_are_comparable(self):
        result = mod.compare_pool(100.0, 60.0, comparable=True)
        self.assertEqual(result["status"], "COMPARABLE")
        self.assertAlmostEqual(result["residual"], 40.0)

        unresolved = mod.compare_pool(100.0, 60.0, comparable=False)
        self.assertEqual(unresolved["status"], "SEMANTICS_UNRESOLVED")
        self.assertIsNone(unresolved["residual"])

    def test_no_negative_residual_is_silently_accepted(self):
        result = mod.compare_pool(50.0, 60.0, comparable=True)
        self.assertEqual(result["status"], "OVERALLOCATED_OR_SEMANTIC_MISMATCH")
        self.assertAlmostEqual(result["residual"], -10.0)

    def test_candidate_driver_expansion_excludes_downstream_tables(self):
        candidates = mod.filter_additional_driver_tables([
            "civ_asset_state",
            "civ_transport_flow",
            "civ_node_texture_overlay",
            "civ_place_dna",
            "civ_social_state",
            "civ_governance_profile",
        ])
        self.assertIn("civ_asset_state", candidates)
        self.assertIn("civ_transport_flow", candidates)
        self.assertIn("civ_governance_profile", candidates)
        self.assertNotIn("civ_node_texture_overlay", candidates)
        self.assertNotIn("civ_place_dna", candidates)
        self.assertNotIn("civ_social_state", candidates)


if __name__ == "__main__":
    unittest.main()
