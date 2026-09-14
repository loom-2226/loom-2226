import unittest

from engineering.civstate.hel_differentiator_input_inventory import summarize_field_variation


class HelDifferentiatorInputInventoryTests(unittest.TestCase):
    def test_constant_and_varying_fields_are_separated(self):
        rows = [
            {"node_subject_id": "NODE:HEL-01", "a": 1, "b": 2, "derivation_id": "D1"},
            {"node_subject_id": "NODE:HEL-02", "a": 1, "b": 3, "derivation_id": "D1"},
        ]
        out = summarize_field_variation("example", rows, identity_fields={"node_subject_id"})
        self.assertEqual(out["varying_fields"], ["b"])
        self.assertEqual(out["constant_fields"], ["a", "derivation_id"])
        self.assertEqual(out["identity_fields_excluded"], ["node_subject_id"])

    def test_missing_values_do_not_create_fake_variation_when_all_missing(self):
        rows = [
            {"node_subject_id": "NODE:HEL-01", "a": None},
            {"node_subject_id": "NODE:HEL-02", "a": None},
        ]
        out = summarize_field_variation("example", rows, identity_fields={"node_subject_id"})
        self.assertEqual(out["varying_fields"], [])
        self.assertEqual(out["constant_fields"], ["a"])

    def test_inventory_has_no_mutation_authority(self):
        rows = [{"node_subject_id": "NODE:HEL-01", "a": 1}]
        out = summarize_field_variation("example", rows, identity_fields={"node_subject_id"})
        self.assertEqual(out["mutation_authority"], "ZERO")
        self.assertEqual(out["allocator_design_authority"], "ZERO")


if __name__ == "__main__":
    unittest.main()
