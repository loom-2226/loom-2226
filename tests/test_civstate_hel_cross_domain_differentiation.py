import unittest

from engineering.civstate.hel_cross_domain_differentiation import compare_pair_records


class HelCrossDomainDifferentiationTests(unittest.TestCase):
    def test_identity_fields_do_not_create_false_differences(self):
        left = [{"subject_id": "NODE:HEL-03", "score": 0.5, "derivation_id": "D1"}]
        right = [{"subject_id": "NODE:HEL-10", "score": 0.5, "derivation_id": "D1"}]
        result = compare_pair_records(
            left,
            right,
            {"NODE:HEL-03", "ENTITY:HEL-03"},
            {"NODE:HEL-10", "ENTITY:HEL-10"},
        )
        self.assertEqual(result["classification"], "SAME_AFTER_ID_NORMALIZATION")
        self.assertEqual(result["different_fields"], [])

    def test_non_identity_state_difference_is_reported(self):
        left = [{"node_subject_id": "NODE:HEL-04", "score": 0.5, "role": "A"}]
        right = [{"node_subject_id": "NODE:HEL-06", "score": 0.7, "role": "B"}]
        result = compare_pair_records(
            left,
            right,
            {"NODE:HEL-04", "ENTITY:HEL-04"},
            {"NODE:HEL-06", "ENTITY:HEL-06"},
        )
        self.assertEqual(result["classification"], "DISTINCT_STATE")
        self.assertEqual(result["different_fields"], ["role", "score"])

    def test_missing_side_is_not_treated_as_difference(self):
        result = compare_pair_records(
            [{"subject_id": "NODE:HEL-07", "score": 1.0}],
            [],
            {"NODE:HEL-07", "ENTITY:HEL-07"},
            {"NODE:HEL-08", "ENTITY:HEL-08"},
        )
        self.assertEqual(result["classification"], "MISSING_SIDE")


if __name__ == "__main__":
    unittest.main()
