import math
from pathlib import Path
import unittest

from loom.hud.orbital_state import EARTH_RADIUS_KM, earth_orbital_state, earth_orbit_visualization


class HudOrbitPresentationV032Tests(unittest.TestCase):
    MU = 398600.4418

    def test_surface_intersecting_osculating_state_is_not_presented_as_operational_orbit(self):
        state = earth_orbital_state((190000.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.MU)
        self.assertEqual(state["classification"], "DEGENERATE_RADIAL")
        self.assertEqual(state["presentation_regime"], "FREE_FLIGHT_OSCULATING")
        self.assertFalse(state["operational_orbit"])

    def test_circular_400km_state_is_presented_as_operational_orbit(self):
        r = EARTH_RADIUS_KM + 400.0
        v = math.sqrt(self.MU / r)
        state = earth_orbital_state((r, 0.0, 0.0), (0.0, v, 0.0), self.MU)
        self.assertEqual(state["presentation_regime"], "EARTH_ORBIT")
        self.assertTrue(state["operational_orbit"])

    def test_orbit_visualization_is_server_derived_and_closed(self):
        r = EARTH_RADIUS_KM + 400.0
        v = math.sqrt(self.MU / r)
        visual = earth_orbit_visualization((r, 0.0, 0.0), (0.0, v, 0.0), self.MU, samples=72)
        self.assertTrue(visual["available"])
        self.assertEqual(visual["authority"], "QUALIFICATION_DERIVED_PRESENTATION_GEOMETRY")
        self.assertEqual(len(visual["points_earth_centered_km"]), 73)
        self.assertEqual(visual["points_earth_centered_km"][0], visual["points_earth_centered_km"][-1])

    def test_orbit_visualization_carries_current_position_and_server_derived_prograde(self):
        r = EARTH_RADIUS_KM + 400.0
        v = math.sqrt(self.MU / r)
        visual = earth_orbit_visualization((r, 0.0, 0.0), (0.0, v, 0.0), self.MU, samples=72)
        self.assertEqual(visual["current_position_earth_centered_km"], [r, 0.0, 0.0])
        self.assertEqual(visual["prograde_unit_earth_centered"], [0.0, 1.0, 0.0])
        self.assertEqual(visual["direction_authority"], "SERVER_DERIVED_FROM_LIVE_VELOCITY")

    def test_non_operational_state_has_no_orbit_visualization(self):
        visual = earth_orbit_visualization((190000.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.MU)
        self.assertFalse(visual["available"])
        self.assertEqual(visual["points_earth_centered_km"], [])
        self.assertIsNone(visual["current_position_earth_centered_km"])
        self.assertIsNone(visual["prograde_unit_earth_centered"])

    def test_orbit_overlay_consumes_live_event_without_fetch_or_control(self):
        source = Path("src/loom/hud/demo/hud_orbit_view_v02.js").read_text(encoding="utf-8")
        self.assertIn("loom-live-qualification", source)
        self.assertIn("orbit_visualization", source)
        self.assertIn("ORBIT OVERVIEW", source)
        self.assertNotIn("fetch(", source)
        self.assertNotIn("qualification-flight/control", source)

    def test_orbit_view_draws_path_ship_position_and_direction_from_server_payload(self):
        source = Path("src/loom/hud/demo/hud_orbit_view_v02.js").read_text(encoding="utf-8")
        self.assertIn("LOOM_ORBIT_PATH_PRESENTATION", source)
        self.assertIn("SHIP_POSITION_PRESENTATION_MARKER", source)
        self.assertIn("PROGRADE_PRESENTATION_CUE", source)
        self.assertIn("current_position_earth_centered_km", source)
        self.assertIn("prograde_unit_earth_centered", source)
        self.assertNotIn("Math.sqrt(mu", source)

    def test_orbit_overview_camera_frames_complete_ring_with_margin(self):
        source = Path("src/loom/hud/demo/hud_orbit_view_v02.js").read_text(encoding="utf-8")
        self.assertIn("ORBIT OVERVIEW FIT", source)
        self.assertIn("extent*3.25", source)

    def test_html_exposes_orbit_overview_without_replacing_existing_deck(self):
        html = Path("src/loom/hud/demo/earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn('<option value="ORBIT">ORBIT</option>', html)
        self.assertIn("hud_orbit_view_v02.js", html)
        self.assertIn('id="world"', html)
        self.assertIn("SOLVE RENDEZVOUS", html)


if __name__ == "__main__":
    unittest.main()
