import math
import unittest

from src.wayfarer_recovered_rcs_candidate import build_recovered_rcs_candidate


class RecoveredRcsCandidateTests(unittest.TestCase):
    def setUp(self):
        self.result = build_recovered_rcs_candidate()

    def test_recovery_is_explicitly_non_canon_and_traceable(self):
        self.assertEqual(self.result["status"], "ENGINEERING_CANDIDATE_NON_CANON")
        self.assertEqual(self.result["provenance"]["source_pr"], 96)
        self.assertEqual(
            self.result["provenance"]["source_validation_head"],
            "5aecbd98fd27063c5d5e7b4b352cc19e74f31627",
        )
        self.assertFalse(self.result["authority"]["flight_dynamics_authority"])
        self.assertFalse(self.result["authority"]["canon_changed"])

    def test_mount_layout_recovers_four_bands_and_sixteen_hardpoints(self):
        self.assertEqual(self.result["mount_count"], 16)
        self.assertEqual([b["x_center_m"] for b in self.result["bands"]], [6.5, 18.5, 36.5, 44.5])
        self.assertEqual(self.result["bands"][0]["azimuths_deg"], [0.0, 90.0, 180.0, 270.0])
        self.assertEqual(self.result["bands"][1]["azimuths_deg"], [45.0, 135.0, 225.0, 315.0])
        self.assertEqual(self.result["bands"][2]["azimuths_deg"], [45.0, 135.0, 225.0, 315.0])
        self.assertEqual(self.result["bands"][3]["azimuths_deg"], [0.0, 90.0, 180.0, 270.0])

    def test_current_geometry_clearance_screen_passes_without_inventing_plume_cone(self):
        screen = self.result["current_geometry_screen"]
        self.assertTrue(screen["hardpoint_point_clearance_pass"])
        self.assertTrue(screen["launch_bay_point_clearance_pass"])
        self.assertTrue(screen["docking_collar_point_clearance_pass"])
        self.assertTrue(screen["radiator_root_azimuth_separation_pass"])
        self.assertEqual(screen["finite_plume_cone_status"], "OPEN_NOT_INVENTED")

    def test_inertia_and_final_control_authority_remain_fail_closed(self):
        dynamics = self.result["dynamics_status"]
        self.assertEqual(dynamics["full_wayfarer_inertia"], "WAYFARER_INERTIA_OPEN_NOT_QUALIFIED")
        self.assertEqual(dynamics["old_q4_torque_targets_role"], "RECOVERED_SCREENING_TARGETS_NOT_CURRENT_FLIGHT_AUTHORITY")
        self.assertFalse(dynamics["closed_loop_gnc_qualified"])
        self.assertFalse(dynamics["structural_mount_loads_qualified"])


if __name__ == "__main__":
    unittest.main()
