import math
from pathlib import Path
import unittest
from unittest.mock import patch

from loom.hud.orbital_state import EARTH_RADIUS_KM
from loom.hud.realtime_flight_qualification import RealtimeFlightQualification


class HudOrbitalSandboxTests(unittest.TestCase):
    def _session_shell(self):
        s = object.__new__(RealtimeFlightQualification)
        s.earth_mu = 398600.4418
        s.earth_mu_source = "TEST"
        s.lock = __import__("threading").RLock()
        s.time_scale = 0.0
        s.torch_mode = "CRUISE"
        s.torch_active = False
        s.status = "RUNNING"
        s.last_wall = 0.0
        return s

    def test_earth_orbit_initializer_is_a_real_circular_state(self):
        s = self._session_shell()
        result = s.initialize_earth_circular_orbit(altitude_km=400.0, inclination_deg=0.0)
        r = math.sqrt(sum(x * x for x in s.ship_position))
        v = math.sqrt(sum(x * x for x in s.ship_velocity))
        self.assertAlmostEqual(r, EARTH_RADIUS_KM + 400.0, places=6)
        self.assertAlmostEqual(v, math.sqrt(s.earth_mu / r), places=6)
        self.assertEqual(result["sandbox_state"], "EARTH_CIRCULAR_ORBIT")
        self.assertFalse(result["campaign_mutation"])

    def test_snapshot_publishes_derived_orbital_state(self):
        source = Path("src/loom/hud/realtime_flight_qualification.py").read_text(encoding="utf-8")
        self.assertIn('"orbital_state": earth_orbital_state(', source)
        self.assertIn('self.ship_position', source)
        self.assertIn('self.ship_velocity', source)
        self.assertIn('self.earth_mu', source)

    def test_control_endpoint_exposes_explicit_non_campaign_orbit_initializer(self):
        source = Path("src/loom/hud/server.py").read_text(encoding="utf-8")
        self.assertIn('INITIALIZE_EARTH_ORBIT', source)
        self.assertIn('initialize_earth_circular_orbit', source)

    def test_orbital_hud_consumes_live_payload_without_fetch_or_control_authority(self):
        source = Path("src/loom/hud/demo/hud_orbital_state_v01.js").read_text(encoding="utf-8")
        self.assertIn("loom-live-qualification", source)
        self.assertIn("orbital_state", source)
        self.assertNotIn("fetch(", source)
        self.assertNotIn("qualification-flight/control", source)

    def test_hud_has_explicit_earth_orbit_sandbox_control(self):
        html = Path("src/loom/hud/demo/earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn('id="earthOrbit400"', html)
        self.assertIn('hud_orbital_state_v01.js', html)
        self.assertIn('hud_orbital_control_v01.js', html)


if __name__ == "__main__":
    unittest.main()
