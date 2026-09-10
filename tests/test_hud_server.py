import tempfile
import unittest
from pathlib import Path
from loom.hud import server

class HudServerTests(unittest.TestCase):
    def test_checked_in_default_qualification_page_exists(self):
        page=server.validate_assets(); self.assertTrue(page.is_file()); self.assertEqual(page.name,"earth_moon_qualification_v011.html")
    def test_missing_demo_page_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError): server.validate_assets(Path(tmp))
    def test_default_port_is_valid(self): self.assertGreaterEqual(server.DEFAULT_PORT,1); self.assertLessEqual(server.DEFAULT_PORT,65535)
    def test_page_is_responsive(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("@media(orientation:portrait)",text); self.assertIn("orientationchange",text); self.assertIn("resize",text)
    def test_authority_boundary_visible(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("QUALIFICATION_ONLY",text); self.assertIn("NOT Navigator targeting",text); self.assertIn("ATTITUDE FIXED / NO ROTATION",text)
    def test_build_marker(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('content="hud-v0.11-moon-visible"',text); self.assertIn("BUILD hud-v0.11-moon-visible",text)
    def test_moon_transform_and_sensor_visibility_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("multiplyScalar(-scale)",text); self.assertIn("makeSensorVisible",text); self.assertIn("MeshBasicMaterial",text); self.assertIn("frustumCulled=false",text)
    def test_moon_diagnostics_and_derived_limb_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("MOON BRG",text); self.assertIn("MOON DIAM",text); self.assertIn("GLB R",text); self.assertIn("moonring",text); self.assertIn("sensorOverlay",text)
    def test_trajectory_preview_controls_and_framing_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('value="TRAJECTORY"',text); self.assertIn("trajectory-preview.json",text); self.assertIn("CALCULATE",text); self.assertIn("trajectoryScene",text); self.assertIn("MOON PATH",text)
    def test_server_endpoints(self):
        self.assertEqual(server.LIVE_ENDPOINT,"/flight-view.json"); self.assertEqual(server.EARTH_MOON_ENDPOINT,"/earth-moon-qualification.json"); self.assertEqual(server.REALTIME_ENDPOINT,"/qualification-flight.json"); self.assertEqual(server.TRAJECTORY_PREVIEW_ENDPOINT,"/qualification-flight/trajectory-preview.json")

if __name__=="__main__": unittest.main()
