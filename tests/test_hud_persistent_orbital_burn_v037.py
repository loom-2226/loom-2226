import math
import threading
import unittest
from datetime import datetime, timezone

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
        self.time_scale = 1.0
        self.status = "RUNNING"
        self.last_wall = 0.0
        self.steps = []

    def _advance_locked(self):
        pass

    def _step(self, dt):
        self.steps.append((dt, self.torch_active, self.torch_mode, self.nose_direction))
        if self.torch_active:
            # deterministic fake thrust response for executor tests only
            accel = 0.00980665
            self.ship_velocity = tuple(
                self.ship_velocity[i] + self.nose_direction[i] * accel * dt
                for i in range(3)
            )
            used_t = min(self.remass_t, 0.001 * dt)
            self.remass_t -= used_t
            self.wet_mass_t -= used_t
        self.sim_epoch = datetime.fromtimestamp(self.sim_epoch.timestamp() + dt, tz=timezone.utc)


class PersistentOrbitalBurnV037Tests(unittest.TestCase):
    def test_prograde_burn_mutates_same_live_state_through_typed_command(self):
        s = _Session()
        before_speed = math.sqrt(sum(v * v for v in s.ship_velocity))
        receipt = execute_velocity_aligned_burn(
            s, direction="PROGRADE", duration_s=5.0, torch_mode="CRUISE", requested_by="HUD"
        )
        after_speed = math.sqrt(sum(v * v for v in s.ship_velocity))
        self.assertEqual(receipt["contract"], "LOOM_FLIGHT_EXECUTION_RECEIPT_V1")
        self.assertEqual(receipt["command"]["contract"], "LOOM_FLIGHT_COMMAND_V1")
        self.assertEqual(receipt["command"]["origin"], "MANUAL")
        self.assertEqual(receipt["direction_reference"], "PROGRADE")
        self.assertTrue(receipt["mutates_live_qualification_state"])
        self.assertFalse(receipt["campaign_mutation"])
        self.assertGreater(after_speed, before_speed)
        self.assertLess(s.remass_t, 250.0)
        self.assertFalse(s.torch_active)

    def test_retrograde_burn_uses_q4_finite_attitude_time_before_thrust(self):
        s = _Session()
        receipt = execute_velocity_aligned_burn(
            s, direction="RETROGRADE", duration_s=5.0, torch_mode="CRUISE", requested_by="HUD"
        )
        self.assertGreater(receipt["attitude_transition"]["transition_time_s"], 0.0)
        self.assertAlmostEqual(receipt["attitude_transition"]["angle_deg"], 180.0, places=6)
        first_thrust_index = next(i for i, row in enumerate(s.steps) if row[1])
        self.assertGreater(first_thrust_index, 0)
        self.assertEqual(s.nose_direction, (0.0, -1.0, 0.0))

    def test_executor_rejects_zero_speed_and_unbounded_burns(self):
        s = _Session()
        s.ship_velocity = (0.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            execute_velocity_aligned_burn(s, direction="PROGRADE", duration_s=5.0, torch_mode="CRUISE")
        s.ship_velocity = (0.0, 7.6, 0.0)
        with self.assertRaises(ValueError):
            execute_velocity_aligned_burn(s, direction="PROGRADE", duration_s=61.0, torch_mode="CRUISE")
        with self.assertRaises(ValueError):
            execute_velocity_aligned_burn(s, direction="SIDEWAYS", duration_s=5.0, torch_mode="CRUISE")


if __name__ == "__main__":
    unittest.main()
