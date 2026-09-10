import math
import unittest

from loom.hud import (
    Vector3,
    edge_indicator_position,
    project_camera_vector,
    project_world_point,
)


class HudProjectionTests(unittest.TestCase):
    def test_known_geometry_neptune_is_seventeen_degrees_off_center(self):
        distance = 1_000_000.0
        angle = math.radians(17.0)
        neptune = Vector3(distance * math.cos(angle), distance * math.sin(angle), 0.0)
        p = project_world_point(
            object_position_inertial=neptune,
            ship_position_inertial=Vector3(0.0, 0.0, 0.0),
            camera_from_inertial_xyzw=(0.0, 0.0, 0.0, 1.0),
            viewport_width_px=1000.0,
            viewport_height_px=600.0,
            fov_y_deg=60.0,
        )
        self.assertTrue(p.in_front)
        self.assertAlmostEqual(p.bearing_deg, 17.0, places=9)
        self.assertAlmostEqual(p.elevation_deg, 0.0, places=9)
        self.assertGreater(p.screen_x, 500.0)

    def test_marker_moves_monotonically_across_viewport(self):
        xs = []
        for bearing_deg in (-10.0, 0.0, 10.0):
            a = math.radians(bearing_deg)
            p = project_world_point(
                object_position_inertial=Vector3(math.cos(a) * 1000.0, math.sin(a) * 1000.0, 0.0),
                ship_position_inertial=Vector3(0.0, 0.0, 0.0),
                camera_from_inertial_xyzw=(0.0, 0.0, 0.0, 1.0),
                viewport_width_px=1000.0,
                viewport_height_px=600.0,
                fov_y_deg=60.0,
            )
            xs.append(p.screen_x)
        self.assertLess(xs[0], xs[1])
        self.assertLess(xs[1], xs[2])

    def test_vertical_fov_controls_on_screen_elevation(self):
        a = math.radians(35.0)
        p = project_camera_vector(
            Vector3(math.cos(a), 0.0, math.sin(a)),
            viewport_width_px=1000.0,
            viewport_height_px=600.0,
            fov_y_deg=60.0,
        )
        self.assertFalse(p.on_screen)
        self.assertAlmostEqual(p.elevation_deg, 35.0, places=9)

    def test_offscreen_indicator_is_clamped_inside_margin(self):
        p = project_camera_vector(
            Vector3(1.0, 10.0, 2.0),
            viewport_width_px=1000.0,
            viewport_height_px=600.0,
            fov_y_deg=60.0,
        )
        self.assertFalse(p.on_screen)
        x, y = edge_indicator_position(
            p,
            viewport_width_px=1000.0,
            viewport_height_px=600.0,
            margin_px=24.0,
        )
        self.assertGreaterEqual(x, 24.0)
        self.assertLessEqual(x, 976.0)
        self.assertGreaterEqual(y, 24.0)
        self.assertLessEqual(y, 576.0)


if __name__ == "__main__":
    unittest.main()
