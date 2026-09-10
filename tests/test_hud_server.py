import tempfile
import unittest
from pathlib import Path
from loom.hud import server

class HudServerTests(unittest.TestCase):
    def test_checked_in_default_qualification_page_exists(self):
        page=server.validate_assets(); self.assertTrue(page.is_file()); self.assertEqual(page.name,"earth_moon_qualification.html")
    def test_missing_demo_page_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError): server.validate_assets(Path(tmp))
    def test_default_port_is_valid(self): self.assertGreaterEqual(server.DEFAULT_PORT,1); self.assertLessEqual(server.DEFAULT_PORT,65535)
    def test_page_is_responsive(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("@media(orientation:portrait)",text); self.assertIn("viewport-fit=cover",text)
    def test_authority_boundary_visible(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("QUALIFICATION_ONLY",text); self.assertIn("NOT Navigator targeting authority",text)
    def test_build_marker(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('content="hud-v0.12-intercept"',text); self.assertIn("BUILD hud-v0.12-intercept",text)
    def test_optical_moon_and_external_client_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("NASA LRO OPTICAL MOON",text); self.assertIn("hud_v0_12.js",text)
        js=(server.demo_root()/"hud_v0_12.js").read_text(encoding="utf-8"); self.assertIn("SphereGeometry(1737.4",js); self.assertIn("moonOptical",js); self.assertIn("moonTopo.visible=false",js)
    def test_intercept_preview_controls_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("SOLVE INTERCEPT",text); self.assertIn("PROPAGATE",text)
        js=(server.demo_root()/"hud_v0_12.js").read_text(encoding="utf-8"); self.assertIn("intercept-preview.json",js); self.assertIn("relative_speed_km_s",js)
    def test_server_endpoints(self):
        self.assertEqual(server.LIVE_ENDPOINT,"/flight-view.json"); self.assertEqual(server.EARTH_MOON_ENDPOINT,"/earth-moon-qualification.json"); self.assertEqual(server.REALTIME_ENDPOINT,"/qualification-flight.json"); self.assertEqual(server.TRAJECTORY_PREVIEW_ENDPOINT,"/qualification-flight/trajectory-preview.json"); self.assertEqual(server.INTERCEPT_PREVIEW_ENDPOINT,"/qualification-flight/intercept-preview.json")

if __name__=="__main__": unittest.main()
