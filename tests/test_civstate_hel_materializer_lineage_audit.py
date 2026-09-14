import unittest

from engineering.civstate.hel_materializer_lineage_audit import summarize_lineage


class HelMaterializerLineageAuditTests(unittest.TestCase):
    def test_exact_lineage_clone_is_reported_not_declared_defect(self):
        nodes = {
            "NODE:HEL-03": {
                "subject": {"subject_class": "INFRASTRUCTURE_NODE", "parent_subject_id": "ZONE:084"},
                "infrastructure_derivation_id": "DERIV:MATERIALIZER2226",
                "influence_signature": (
                    ("ACTOR:A", "OPERATIONS", 0.9, "PRIMARY", "COMMON_BASIS", "DERIV:GAMEPLAY2226"),
                ),
            },
            "NODE:HEL-10": {
                "subject": {"subject_class": "INFRASTRUCTURE_NODE", "parent_subject_id": "ZONE:084"},
                "infrastructure_derivation_id": "DERIV:MATERIALIZER2226",
                "influence_signature": (
                    ("ACTOR:A", "OPERATIONS", 0.9, "PRIMARY", "COMMON_BASIS", "DERIV:GAMEPLAY2226"),
                ),
            },
        }
        report = summarize_lineage(nodes, [("NODE:HEL-03", "NODE:HEL-10")])
        result = report["pair_results"][0]
        self.assertTrue(result["same_subject_metadata"])
        self.assertTrue(result["same_infrastructure_derivation"])
        self.assertTrue(result["same_influence_signature"])
        self.assertEqual(result["classification"], "EXACT_INSPECTED_LINEAGE_CLONE")
        self.assertEqual(report["mutation_authority"], "ZERO")

    def test_shared_derivation_but_distinct_edges_is_not_exact_clone(self):
        nodes = {
            "NODE:HEL-04": {
                "subject": {"subject_class": "INFRASTRUCTURE_NODE", "parent_subject_id": "ZONE:084"},
                "infrastructure_derivation_id": "DERIV:MATERIALIZER2226",
                "influence_signature": (("ACTOR:A", "OPERATIONS", 0.9, None, None, "DERIV:GAMEPLAY2226"),),
            },
            "NODE:HEL-06": {
                "subject": {"subject_class": "INFRASTRUCTURE_NODE", "parent_subject_id": "ZONE:084"},
                "infrastructure_derivation_id": "DERIV:MATERIALIZER2226",
                "influence_signature": (("ACTOR:B", "OPERATIONS", 0.9, None, None, "DERIV:GAMEPLAY2226"),),
            },
        }
        report = summarize_lineage(nodes, [("NODE:HEL-04", "NODE:HEL-06")])
        result = report["pair_results"][0]
        self.assertTrue(result["same_infrastructure_derivation"])
        self.assertFalse(result["same_influence_signature"])
        self.assertEqual(result["classification"], "SHARED_DERIVATION_DISTINCT_INSPECTED_LINEAGE")


if __name__ == "__main__":
    unittest.main()
