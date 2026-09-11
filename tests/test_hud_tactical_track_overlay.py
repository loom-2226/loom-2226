import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "src" / "loom" / "hud" / "demo"


class HudTacticalTrackOverlayTests(unittest.TestCase):
    def test_overlay_reuses_existing_live_hud(self):
        html = (DEMO / "earth_moon_qualification.html").read_text(encoding="utf-8")
        self.assertIn('id="world"', html)
        self.assertIn('id="tacticalTrack"', html)
        self.assertIn("hud_tactical_track_v01.js", html)
        self.assertNotIn("tactical-track.html", html)

    def test_overlay_consumes_live_event_without_own_api_call(self):
        js = (DEMO / "hud_tactical_track_v01.js").read_text(encoding="utf-8")
        self.assertIn("loom-live-qualification", js)
        self.assertIn("relative_to_wayfarer_km", js)
        self.assertIn("velocity_earth_centered_km_s", js)
        self.assertIn("RANGE", js)
        self.assertIn("RANGE RATE", js)
        self.assertIn("REL SPEED", js)
        self.assertIn("UNCERTAINTY NOT PROVIDED", js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("/control", js)

    def test_existing_live_fetch_hook_publishes_payload(self):
        js = (DEMO / "hud_v0_18_range_rate.js").read_text(encoding="utf-8")
        self.assertIn("loom-live-qualification", js)
        self.assertIn("__loomLiveQualification", js)

    def test_family_profiles_make_tactical_track_primary_only_in_tactical_modes(self):
        js = (DEMO / "hud_family_profiles_v01.js").read_text(encoding="utf-8")
        self.assertIn("tacticalTrack", js)
        self.assertIn("primary('telemetry','flight','time','tacticalTrack')", js)
        self.assertIn("secondary('planning','rendezvous','scrub','quality','navPlan','assurance')", js)


if __name__ == "__main__":
    unittest.main()
