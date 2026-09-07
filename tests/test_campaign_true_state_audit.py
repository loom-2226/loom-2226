from __future__ import annotations

import unittest

import loom_navigator_core as core
from loom.campaign_true_state_audit import CAMPAIGN_TRUE_STATE_AUDIT_CONTRACT, campaign_true_state_matrix


class CampaignTrueStateAuditTests(unittest.TestCase):
    def test_source_defined_canonical_state_coverage(self) -> None:
        state = core._new_state("F-PA-AUDIT", "WAYFARER-AUDIT")
        result = campaign_true_state_matrix(state)
        self.assertEqual(result["contract"], CAMPAIGN_TRUE_STATE_AUDIT_CONTRACT)
        self.assertEqual(result["state_schema"], core.STATE_SCHEMA)
        by_name = {r["requirement"]: r for r in result["simulator_state_matrix"]}
        self.assertEqual(by_name["campaign_clock"]["observed"], "PRESENT")
        self.assertEqual(by_name["mass_remass_cargo"]["observed"], "PRESENT")
        self.assertEqual(by_name["true_position_velocity"]["observed"], "ABSENT")
        self.assertEqual(by_name["attitude_angular_rate"]["observed"], "ABSENT")
        self.assertEqual(by_name["estimated_navigation"]["observed"], "ABSENT")
        self.assertEqual(by_name["traffic_clearance"]["observed"], "ABSENT")
        self.assertEqual(by_name["fault_state"]["observed"], "ABSENT")


if __name__ == "__main__":
    unittest.main()
