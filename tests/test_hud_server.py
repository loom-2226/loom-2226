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
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("NON-CANON",text); self.assertIn("NOT Navigator targeting authority",text); self.assertIn("Q4 FINITE ATTITUDE",text); self.assertIn("Q5 PURE-ATTITUDE ENERGY",text)
    def test_build_marker(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('content="hud-v0.29-runtime-family-auto"',text); self.assertIn("BUILD hud-v0.29-runtime-family-auto",text)
    def test_optical_moon_and_external_client_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("NASA LRO OPTICAL MOON",text); self.assertIn("hud_v0_15.js",text)
        js=(server.demo_root()/"hud_v0_15.js").read_text(encoding="utf-8"); self.assertIn("SphereGeometry(1737.4",js); self.assertIn("moonOptical",js); self.assertIn("moonTopo",js)
    def test_intercept_and_rendezvous_preview_controls_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("SOLVE INTERCEPT",text); self.assertIn("SOLVE RENDEZVOUS",text); self.assertIn("STANDOFF ALT km",text); self.assertIn("BRAKE",text)
        js=(server.demo_root()/"hud_v0_15.js").read_text(encoding="utf-8"); self.assertIn("intercept-preview.json",js); self.assertIn("rendezvous-preview.json",js); self.assertIn("target_position_error_km",js)
    def test_free_camera_controls_are_presentation_only(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("RESET VIEW",text); self.assertIn("CAM DEFAULT",text)
        js=(server.demo_root()/"hud_v0_15.js").read_text(encoding="utf-8"); self.assertIn("cameraOverride",js); self.assertIn("installCameraGestures",js); self.assertIn("orbitCamera",js); self.assertIn("zoomCamera",js); self.assertIn("resetPerspective",js)
    def test_preview_scrubber_is_non_mutating_presentation(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("PREVIEW TIME",text); self.assertIn("RETURN LIVE",text)
        js=(server.demo_root()/"hud_v0_15.js").read_text(encoding="utf-8"); self.assertIn("previewActive",js); self.assertIn("previewPoint",js); self.assertIn("LIVE STATE UNCHANGED",js); self.assertIn("scrub.oninput",js)
    def test_ship_look_keeps_eye_fixed_and_rotates_view(self):
        js=(server.demo_root()/"hud_v0_17_ship_look.js").read_text(encoding="utf-8"); self.assertIn("SHIP LOOK",js); self.assertIn("SHIP CAMERA EYE DRIFT",js); self.assertIn("camera.position.copy(eye)",js); self.assertIn("camera.lookAt(target)",js); self.assertNotIn("camera.position.add",js)
    def test_ship_offscreen_moon_cue_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('id="moonCue"',text); self.assertIn("mooncue",text)
        js=(server.demo_root()/"hud_v0_17_ship_look.js").read_text(encoding="utf-8"); self.assertIn("MOON",js); self.assertIn("atan2",js); self.assertIn("display='block'",js)
    def test_moon_range_rate_telemetry_is_derived_without_state_mutation(self):
        js=(server.demo_root()/"hud_v0_18_range_rate.js").read_text(encoding="utf-8"); self.assertIn("CLOSING",js); self.assertIn("RECEDING",js); self.assertIn("RADIAL HOLD",js); self.assertIn("relative_to_wayfarer_km",js); self.assertIn("VECTOR",js); self.assertIn("SAMPLED",js); self.assertNotIn("/control",js)
    def test_terminal_quality_panel_is_fail_closed_and_non_commanding(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('id="qualityPanel"',text); self.assertIn("NO CORRECTED RENDEZVOUS SOLUTION LOADED",text)
        js=(server.demo_root()/"hud_v0_20_quality.js").read_text(encoding="utf-8"); self.assertIn("SOLVED_TRANSLATIONAL_FEASIBILITY",js); self.assertIn("Q4 ATT",js); self.assertIn("TORCH OFF DURING SLEW",js); self.assertNotIn("fetch(",js); self.assertNotIn("/control",js)
    def test_terminal_corrector_v2_uses_earth_facing_target_and_bounded_line_search(self):
        py=(server.demo_root().parent/"realtime_flight_qualification.py").read_text(encoding="utf-8"); self.assertIn("EARTH_FACING_STANDOFF",py); self.assertIn("corrector_method",py); self.assertIn("BOUNDED_2D_LINE_SEARCH",py); self.assertIn("corrector_iterations_max",py)
    def test_wayfarer_engineering_state_endpoint_and_panel_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("hud_wayfarer_engineering_state_v01.js",text); self.assertIn("PR96 ENGINEERING CONSUMER",text)
