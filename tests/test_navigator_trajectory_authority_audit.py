from __future__ import annotations

import unittest

from loom.navigator_trajectory_authority_audit import (
    NAVIGATOR_TRAJECTORY_AUDIT_CONTRACT,
    SEQUENCE_B_SAMPLE_FIELDS,
    navigator_trajectory_authority_audit,
)


class NavigatorTrajectoryAuthorityAuditTests(unittest.TestCase):
    def test_current_sequence_b_telemetry_boundary(self) -> None:
        result = navigator_trajectory_authority_audit()
        self.assertEqual(result["contract"], NAVIGATOR_TRAJECTORY_AUDIT_CONTRACT)
        self.assertEqual(result["sequence_b_sample_field_count"], len(SEQUENCE_B_SAMPLE_FIELDS))
        self.assertEqual(len(SEQUENCE_B_SAMPLE_FIELDS), 25)

        for field in (
            "ordinary_pos_x_km", "ordinary_pos_y_km", "ordinary_pos_z_km",
            "ordinary_vel_x_km_s", "ordinary_vel_y_km_s", "ordinary_vel_z_km_s",
            "ordinary_accel_g", "target_range_km", "target_delta_v_km_s",
            "wet_mass_t", "remass_remaining_t", "thermal_state_code",
        ):
            self.assertIn(field, result["field_classification"])

        needs = {row["need"]: row for row in result["simulator_need_matrix"]}
        self.assertEqual(needs["ordinary_position_3d"]["status"], "PRESENT_WHERE_SEQUENCE_B_DECLARES_ORDINARY_OCCUPANCY")
        self.assertEqual(needs["ordinary_velocity_3d"]["status"], "PRESENT_WHERE_SEQUENCE_B_DECLARES_ORDINARY_OCCUPANCY")
        self.assertEqual(needs["metric_relational_state"]["status"], "PRESENT_NO_ORDINARY_OCCUPANCY")
        self.assertEqual(needs["acceleration_vector"]["status"], "MISSING")
        self.assertEqual(needs["attitude_orientation"]["status"], "MISSING")
        self.assertEqual(needs["navigation_uncertainty_covariance"]["status"], "MISSING")
        self.assertEqual(needs["estimated_navigation_state"]["status"], "MISSING")
        self.assertEqual(needs["thermal_quantitative_state"]["status"], "MISSING")
        self.assertEqual(needs["power_state"]["status"], "MISSING")
        self.assertEqual(needs["docking_proximity_state"]["status"], "MISSING")

        boundary = result["authority_boundaries"]
        self.assertEqual(boundary["metric_ordinary_occupancy"], "PROHIBITED_NO_INVENTED_XYZ")
        self.assertEqual(boundary["extrapolation"], "PROHIBITED")
        self.assertEqual(boundary["visual_sampling"], "VISUALIZATION_ONLY")
        self.assertEqual(boundary["campaign_mutation"], "NONE")


if __name__ == "__main__":
    unittest.main()
