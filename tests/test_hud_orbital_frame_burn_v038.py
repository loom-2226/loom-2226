import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

from loom.hud.flight_command_executor import execute_velocity_aligned_burn


class _Session:
    def __init__(self):
        self.lock = threading.RLock()
        self.sim_epoch = datetime(2026, 9, 12, 0, 0, tzinfo=timezone.utc)
        self.ship_position = (6778.137, 0.0, 0.0)
        self.ship_velocity = (0.0, 7.668558, 0.0)
        self.nose_direction = (0.0, 1.0, 0.0)
        self.torch_active = False
        self.torch_mode = "CRUISE"
        self.remass_t = 250.0
        self.wet_mass_t = 1158.5
        self.status = "RUNNING"
        self.last_wall = 0.0
        self.steps = []

    def _advance_locked(self):
        pass

    def _step(self, dt):
        self.steps.append((dt, self.torch_active, self.nose_direction))
        if self.torch_active:
            accel = 0.00980665
            self.ship_velocity = tuple(
                self.ship_velocity[i] + self.nose_direction[i] * accel * dt
                for i in range(3)
            )
            used_t = min(self.remass_t, 0.001 * dt)
            self.remass_t -= used_t
            self.wet_mass_t -= used_t
        self.sim_epoch = datetime.fromtimestamp(self.sim_epoch.timestamp() + dt, tz=timezone.utc)


class OrbitalFrameBurnV038Tests(unittest.TestCase):
    def _execute(self, direction):
        s = _Session()
        receipt = execute_velocity_aligned_burn(
            s,
            direction=direction,
            duration_s=1.0,
            torch_mode="CRUISE",
            requested_by="HUD",
        )
        return s, receipt

    def test_radial_out_and_in_resolve_from_current_position(self):
        out_session, out_receipt = self._execute("RADIAL_OUT")
        in_session, in_receipt = self._execute("RADIAL_IN")
        self.assertEqual(out_receipt["direction_reference"], "RADIAL_OUT")
        self.assertEqual(in_receipt["direction_reference"], "RADIAL_IN")
        self.assertEqual(tuple(out_receipt["command"]["target_direction_inertial"]), (1.0, 0.0, 0.0))
        self.assertEqual(tuple(in_receipt["command"]["target_direction_inertial"]), (-1.0, 0.0, 0.0))
        self.assertGreater(out_session.ship_velocity[0], 0.0)
        self.assertLess(in_session.ship_velocity[0], 0.0)

    def test_normal_and_antinormal_resolve_from_orbital_angular_momentum(self):
        normal_session, normal_receipt = self._execute("NORMAL")
        anti_session, anti_receipt = self._execute("ANTINORMAL")
        self.assertEqual(tuple(normal_receipt["command"]["target_direction_inertial"]), (0.0, 0.0, 1.0))
        self.assertEqual(tuple(anti_receipt["command"]["target_direction_inertial"]), (0.0, 0.0, -1.0))
        self.assertGreater(normal_session.ship_velocity[2], 0.0)
        self.assertLess(anti_session.ship_velocity[2], 0.0)

    def test_all_six_manual_orbital_directions_share_typed_execution_boundary(self):
        for direction in ("PROGRADE", "RETROGRADE", "RADIAL_OUT", "RADIAL_IN", "NORMAL", "ANTINORMAL"):
            with self.subTest(direction=direction):
                session, receipt = self._execute(direction)
                self.assertEqual(receipt["contract"], "LOOM_FLIGHT_EXECUTION_RECEIPT_V1")
                self.assertEqual(receipt["command"]["contract"], "LOOM_FLIGHT_COMMAND_V1")
                self.assertEqual(receipt["command"]["origin"], "MANUAL")
                self.assertEqual(receipt["direction_basis"], "CURRENT_LIVE_EARTH_CENTERED_ORBITAL_FRAME")
                self.assertLess(session.remass_t, 250.0)
                self.assertFalse(session.torch_active)

    def test_normal_burn_fails_closed_without_orbital_plane(self):
        s = _Session()
        s.ship_position = (6778.137, 0.0, 0.0)
        s.ship_velocity = (7.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            execute_velocity_aligned_burn(
                s,
                direction="NORMAL",
                duration_s=1.0,
                torch_mode="CRUISE",
            )

    def test_mobile_runtime_exposes_compact_non_tangential_control(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "src/loom/hud/demo/hud_orbital_burn_v01.js").read_text(encoding="utf-8")
        self.assertIn("orbitalBurnDirection", script)
        self.assertIn("BURN VECTOR", script)
        for direction in ("RADIAL_OUT", "RADIAL_IN", "NORMAL", "ANTINORMAL"):
            self.assertIn(direction, script)


if __name__ == "__main__":
    unittest.main()
