import unittest

from engineering.experience_one.qualification.e1_navigator_geometry_probe import inventory_leg_geometry


class E1NavigatorGeometryProbeTests(unittest.TestCase):
    def test_inventory_reports_explicit_geometry_paths_without_inventing_samples(self):
        leg = {
            "metric_segment": {
                "distance_km": 123.0,
                "duration_s": 45.0,
                "beta_c": 0.5,
            },
            "arrival": {"epoch_utc": "2226-08-22T09:45:17.864616Z"},
            "terminal_burn": {"delta_v_km_s": 12.0},
        }
        report = inventory_leg_geometry(leg)
        self.assertEqual(report["top_level_keys"], ["arrival", "metric_segment", "terminal_burn"])
        self.assertFalse(report["explicit_spatial_path_present"])
        self.assertEqual(report["explicit_spatial_paths"], [])
        self.assertIn("metric_segment.distance_km", report["physics_scalar_paths"])
        self.assertIn("arrival.epoch_utc", report["temporal_paths"])

    def test_inventory_detects_actual_position_velocity_or_trajectory_fields(self):
        leg = {
            "metric_segment": {
                "trajectory_samples": [
                    {"epoch_utc": "2226-08-22T01:32:00Z", "position_km": [1, 2, 3]},
                    {"epoch_utc": "2226-08-22T02:32:00Z", "position_km": [4, 5, 6]},
                ],
                "collapse_velocity_km_s": [7, 8, 9],
            }
        }
        report = inventory_leg_geometry(leg)
        self.assertTrue(report["explicit_spatial_path_present"])
        self.assertIn("metric_segment.trajectory_samples", report["explicit_spatial_paths"])
        self.assertIn("metric_segment.trajectory_samples[0].position_km", report["explicit_spatial_paths"])
        self.assertIn("metric_segment.collapse_velocity_km_s", report["explicit_spatial_paths"])


if __name__ == "__main__":
    unittest.main()
