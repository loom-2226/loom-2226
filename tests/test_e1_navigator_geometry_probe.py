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
        self.assertFalse(report["explicit_spatial_state_present"])
        self.assertFalse(report["metric_occupancy_path_present"])
        self.assertEqual(report["explicit_spatial_paths"], [])
        self.assertEqual(report["metric_occupancy_paths"], [])
        self.assertIn("metric_segment.distance_km", report["physics_scalar_paths"])
        self.assertIn("arrival.epoch_utc", report["temporal_paths"])

    def test_collapse_state_is_not_misclassified_as_metric_occupancy_path(self):
        leg = {
            "metric_segment": {
                "semantics": "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY",
                "collapse_epoch_utc": "2226-08-22T09:07:59.475571Z",
                "collapse_position_km_j2000_ecliptic": [1, 2, 3],
            },
            "ordinary_velocity_memory": {
                "collapse_velocity_km_s": [7, 8, 9],
            },
            "engineering_checkpoints": [
                {"epoch_utc": "2226-08-22T09:07:59.475571Z", "fraction": 0.0, "endpoint_range_km": 10.0},
                {"epoch_utc": "2226-08-22T09:45:17.864617Z", "fraction": 1.0, "endpoint_range_km": 0.0},
            ],
        }
        report = inventory_leg_geometry(leg)
        self.assertTrue(report["explicit_spatial_state_present"])
        self.assertFalse(report["metric_occupancy_path_present"])
        self.assertIn("metric_segment.collapse_position_km_j2000_ecliptic", report["explicit_spatial_paths"])
        self.assertEqual(report["metric_occupancy_paths"], [])
        self.assertEqual(report["metric_segment_semantics"], "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY")

    def test_inventory_detects_actual_metric_occupancy_samples_only_when_explicit(self):
        leg = {
            "metric_segment": {
                "semantics": "ORDINARY_SPACE_OCCUPANCY_TEST_FIXTURE",
                "trajectory_samples": [
                    {"epoch_utc": "2226-08-22T01:32:00Z", "position_km": [1, 2, 3]},
                    {"epoch_utc": "2226-08-22T02:32:00Z", "position_km": [4, 5, 6]},
                ],
                "collapse_velocity_km_s": [7, 8, 9],
            }
        }
        report = inventory_leg_geometry(leg)
        self.assertTrue(report["explicit_spatial_state_present"])
        self.assertTrue(report["metric_occupancy_path_present"])
        self.assertIn("metric_segment.trajectory_samples", report["metric_occupancy_paths"])
        self.assertIn("metric_segment.trajectory_samples[0].position_km", report["explicit_spatial_paths"])


if __name__ == "__main__":
    unittest.main()
