import math
from pathlib import Path
import unittest

from loom.hud.predicted_path import build_predicted_path


class _Session:
    def __init__(self):
        from datetime import datetime, timezone
        self.sim_epoch = datetime(2026, 9, 11, 22, 0, tzinfo=timezone.utc)
        self.ship_position = (6778.137, 0.0, 0.0)
        self.ship_velocity = (0.0, math.sqrt(398600.4418 / 6778.137), 0.0)
        self.nose_direction = (1.0, 0.0, 0.0)
        self.status = "RUNNING"
        self.torch_active = False
        self.torch_mode = "CRUISE"
        self.remass_t = 250.0
        self.wet_mass_t = 1158.5
        self.lock = __import__("threading").RLock()
        self._mu = 398600.4418

    def _gravity(self, epoch, position):
        r = math.sqrt(sum(float(x) * float(x) for x in position))
        return tuple(-self._mu * float(x) / (r ** 3) for x in position)


class HudPredictedPathV034Tests(unittest.TestCase):
    def test_prediction_is_ballistic_read_only_and_deterministic(self):
        s = _Session()
        before = (s.sim_epoch, s.ship_position, s.ship_velocity, s.remass_t, s.wet_mass_t)
        a = build_predicted_path(s, horizon_s=1200.0, sample_s=60.0)
        b = build_predicted_path(s, horizon_s=1200.0, sample_s=60.0)
        self.assertEqual(a, b)
        self.assertEqual(before, (s.sim_epoch, s.ship_position, s.ship_velocity, s.remass_t, s.wet_mass_t))
        self.assertEqual(a["contract"], "LOOM_PREDICTED_PATH_V1")
        self.assertEqual(a["assumption"], "BALLISTIC_COAST_CURRENT_STATE")
        self.assertFalse(a["navigation_grade"])
        self.assertFalse(a["mutates_live_state"])
        self.assertGreater(len(a["points"]), 2)
        self.assertEqual(a["points"][0]["position_earth_centered_km"], list(s.ship_position))

    def test_prediction_carries_start_motion_and_attitude_cues(self):
        s = _Session()
        p = build_predicted_path(s, horizon_s=1200.0, sample_s=60.0)
        self.assertEqual(p["start_nose_direction_inertial"], [1.0, 0.0, 0.0])
        self.assertAlmostEqual(p["start_speed_km_s"], math.sqrt(398600.4418 / 6778.137), places=9)
        self.assertEqual(p["motion_cue"], "VELOCITY_DOMINATED")
        self.assertGreater(p["body_velocity_angle_deg"], 80.0)
        self.assertTrue(p["show_body_axis_cue"])

        s.nose_direction = (0.0, 1.0, 0.0)
        aligned = build_predicted_path(s, horizon_s=120.0, sample_s=60.0)
        self.assertLess(aligned["body_velocity_angle_deg"], 1.0)
        self.assertFalse(aligned["show_body_axis_cue"])

        s.ship_velocity = (0.0, 0.0, 0.0)
        q = build_predicted_path(s, horizon_s=120.0, sample_s=60.0)
        self.assertEqual(q["motion_cue"], "GRAVITY_DOMINATED_NEAR_ZERO_SPEED")
        self.assertIsNone(q["body_velocity_angle_deg"])
        self.assertTrue(q["show_body_axis_cue"])

    def test_prediction_curves_under_gravity_not_velocity_vector(self):
        s = _Session()
        p = build_predicted_path(s, horizon_s=1200.0, sample_s=120.0)
        end = p["points"][-1]["position_earth_centered_km"]
        linear_end = [s.ship_position[i] + s.ship_velocity[i] * 1200.0 for i in range(3)]
        self.assertGreater(abs(end[0] - linear_end[0]), 100.0)

    def test_prediction_horizon_is_bounded(self):
        s = _Session()
        with self.assertRaises(ValueError):
            build_predicted_path(s, horizon_s=0.0)
        with self.assertRaises(ValueError):
            build_predicted_path(s, horizon_s=8 * 86400.0)
        with self.assertRaises(ValueError):
            build_predicted_path(s, horizon_s=3600.0, sample_s=1.0)

    def test_browser_toggle_renders_server_path_without_orbital_math(self):
        source = Path("src/loom/hud/demo/hud_predicted_path_v01.js").read_text(encoding="utf-8")
        self.assertIn("PREDICTED PATH", source)
        self.assertIn("predicted-path.json", source)
        self.assertIn("loom-live-qualification", source)
        self.assertIn("position_earth_centered_km", source)
        self.assertIn("PREDICTED_PATH_FUTURE_DIRECTION", source)
        self.assertIn("PREDICTED_PATH_START_VELOCITY", source)
        self.assertIn("PREDICTED_PATH_BODY_NOSE", source)
        self.assertIn("GRAVITY-DOMINATED PATH", source)
        self.assertIn("cueWorldLengthForPixels", source)
        self.assertIn("CUE_PIXELS", source)
        self.assertIn("show_body_axis_cue", source)
        self.assertNotIn("extent*.08", source)
        self.assertNotIn("398600", source)
        self.assertNotIn("sqrt(", source)
        self.assertNotIn("qualification-flight/control", source)

    def test_hud_exposes_predicted_path_toggle_and_build_marker(self):
        html = Path("src/loom/hud/demo/earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn('content="hud-v0.37-persistent-orbital-burn"', html)
        self.assertIn('id="predictedPathToggle"', html)
        self.assertIn("hud_predicted_path_v01.js", html)

    def test_server_exposes_read_only_predicted_path_endpoint(self):
        source = Path("src/loom/hud/server.py").read_text(encoding="utf-8")
        self.assertIn("PREDICTED_PATH_ENDPOINT", source)
        self.assertIn('"/qualification-flight/predicted-path.json"', source)
        self.assertIn("build_predicted_path", source)


if __name__ == "__main__":
    unittest.main()
