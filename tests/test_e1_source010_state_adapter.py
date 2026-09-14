import unittest

from src.loom_navigator_source010_state import (
    AU_KM,
    DAY_S,
    NavigatorSource010StateError,
    NavigatorSource010StateResolver,
)
from src.loom_spatial_state_authority import CANONICAL_FRAME


class E1Source010StateAdapterTests(unittest.TestCase):
    def setUp(self):
        self.axis = {
            "start_utc": "2226-08-22T00:00:00Z",
            "step_seconds": 3600.0,
        }
        # Navigator route-row shape:
        # [source_time, x_AU, y_AU, z_AU, vx_AU_day, vy_AU_day, vz_AU_day]
        # Constant 1 AU/day x velocity gives exact Hermite interpolation.
        v = 1.0
        self.rows = {
            "CERES": (
                (0.0, 0.0, 0.0, 0.0, v, 0.0, 0.0),
                (1.0, 1.0 / 24.0, 0.0, 0.0, v, 0.0, 0.0),
                (2.0, 2.0 / 24.0, 0.0, 0.0, v, 0.0, 0.0),
            )
        }

    def resolver(self, **kwargs):
        return NavigatorSource010StateResolver(
            route_rows=self.rows,
            time_axis=self.axis,
            axis_qualification="PASS",
            source_authority="SOURCE-010",
            **kwargs,
        )

    def test_exact_grid_state_converts_units_and_is_navigation_grade(self):
        state = self.resolver().resolve("CERES", "2226-08-22T01:00:00Z")
        self.assertEqual(state.reference_frame, CANONICAL_FRAME)
        self.assertTrue(state.navigation_grade)
        self.assertAlmostEqual(state.position_km[0], AU_KM / 24.0, places=6)
        self.assertAlmostEqual(state.velocity_km_s[0], AU_KM / DAY_S, places=9)
        self.assertEqual(state.provenance["state_source"], "NAVIGATOR_SOURCE_010_ROUTE_ROWS")
        self.assertEqual(state.provenance["axis_qualification"], "PASS")

    def test_between_grid_points_uses_position_velocity_interpolation(self):
        state = self.resolver().resolve("CERES", "2226-08-22T01:30:00Z")
        self.assertAlmostEqual(state.position_km[0], AU_KM * (1.5 / 24.0), places=5)
        self.assertAlmostEqual(state.velocity_km_s[0], AU_KM / DAY_S, places=8)
        self.assertEqual(state.provenance["interpolation"], "CUBIC_HERMITE_FROM_NAVIGATOR_ROWS")

    def test_outside_acquired_axis_fails_closed(self):
        with self.assertRaises(NavigatorSource010StateError):
            self.resolver().resolve("CERES", "2226-08-21T23:59:59Z")
        with self.assertRaises(NavigatorSource010StateError):
            self.resolver().resolve("CERES", "2226-08-22T02:00:01Z")

    def test_unknown_entity_fails_closed(self):
        with self.assertRaises(NavigatorSource010StateError):
            self.resolver().resolve("NEPTUNE", "2226-08-22T01:00:00Z")

    def test_nonqualified_axis_cannot_be_promoted(self):
        with self.assertRaises(NavigatorSource010StateError):
            NavigatorSource010StateResolver(
                route_rows=self.rows,
                time_axis=self.axis,
                axis_qualification="FAIL",
                source_authority="SOURCE-010",
            )

    def test_non_source010_rows_cannot_be_promoted(self):
        with self.assertRaises(NavigatorSource010StateError):
            NavigatorSource010StateResolver(
                route_rows=self.rows,
                time_axis=self.axis,
                axis_qualification="PASS",
                source_authority="OTHER",
            )


if __name__ == "__main__":
    unittest.main()
