import unittest

from engineering.civstate.hel_texture_audit import summarize_texture_rows


class HelTextureAuditTests(unittest.TestCase):
    def test_duplicate_signatures_are_reported_not_declared_defects(self):
        rows = [
            {
                "node_subject_id": "NODE:HEL-01",
                "mobility_intensity": 0.1,
                "logistics_intensity": 0.2,
                "strategic_intensity": 0.3,
                "activity_pressure": 0.4,
                "actor_fragmentation": 0.8,
                "authority_complexity": 0.6,
                "control_concentration": 0.2,
                "gateway_character": 0.3,
                "frontier_operational_pressure": 0.4,
                "workforce_resident_ratio": 100.0,
                "dominant_texture": "CONTROL_CONCENTRATION",
            },
            {
                "node_subject_id": "NODE:HEL-02",
                "mobility_intensity": 0.1,
                "logistics_intensity": 0.2,
                "strategic_intensity": 0.3,
                "activity_pressure": 0.4,
                "actor_fragmentation": 0.8,
                "authority_complexity": 0.6,
                "control_concentration": 0.2,
                "gateway_character": 0.3,
                "frontier_operational_pressure": 0.4,
                "workforce_resident_ratio": 120.0,
                "dominant_texture": "CONTROL_CONCENTRATION",
            },
        ]
        report = summarize_texture_rows(rows)
        self.assertEqual(report["node_count"], 2)
        self.assertEqual(report["unique_texture_signature_count"], 1)
        self.assertEqual(report["duplicate_signature_group_count"], 1)
        self.assertEqual(report["dominant_texture_counts"], {"CONTROL_CONCENTRATION": 2})
        self.assertEqual(report["interpretation_authority"], "DIAGNOSTIC_ONLY_NO_DEFECT_DECLARATION")

    def test_raw_actor_fragmentation_does_not_invalidate_percentile_dominant_label(self):
        rows = [
            {
                "node_subject_id": "NODE:HEL-01",
                "mobility_intensity": 0.1,
                "logistics_intensity": 0.2,
                "strategic_intensity": 0.3,
                "activity_pressure": 0.4,
                "actor_fragmentation": 0.81,
                "authority_complexity": 0.6,
                "control_concentration": 0.19,
                "gateway_character": 0.3,
                "frontier_operational_pressure": 0.4,
                "workforce_resident_ratio": 112.0,
                "dominant_texture": "CONTROL_CONCENTRATION",
            }
        ]
        report = summarize_texture_rows(rows)
        self.assertEqual(report["dominant_texture_semantics"], "PERCENTILE_PROMINENCE_NOT_RAW_MAXIMUM")
        self.assertFalse(report["raw_value_label_contradiction_inferred"])


if __name__ == "__main__":
    unittest.main()
