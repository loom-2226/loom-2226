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
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('content="hud-v0.36-screen-space-path-cues"',text); self.assertIn("BUILD hud-v0.36-screen-space-path-cues",text)
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
    def test_ship_offscreen_moon_cue_present(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('id="moonCue"',text)
        js=(server.demo_root()/"hud_v0_15.js").read_text(encoding="utf-8"); self.assertIn("updateMoonCue",js); self.assertIn("camera.matrixWorldInverse",js)
    def test_moon_growth_checkpoints_are_geometry_derived(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("hud_v0_16_arrival_check.js",text)
        js=(server.demo_root()/"hud_v0_16_arrival_check.js").read_text(encoding="utf-8"); self.assertIn("Math.atan2(1737.4,range)",js); self.assertIn("button('ARRIVAL',100)",js); self.assertIn("dispatchEvent(new Event('input'",js); self.assertIn("camera.value='SHIP'",js)
    def test_ship_look_keeps_eye_fixed_and_rotates_view(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("hud_v0_17_renderer_hook.js",text); self.assertIn("hud_v0_17_ship_look.js",text)
        pre=(server.demo_root()/"hud_v0_17_renderer_hook.js").read_text(encoding="utf-8"); post=(server.demo_root()/"hud_v0_17_ship_look.js").read_text(encoding="utf-8")
        self.assertIn("__loomBeforeRender",pre); self.assertIn("camera.position.set(0,0,0)",post); self.assertIn("rotateShipLook",post); self.assertIn("stopImmediatePropagation",post); self.assertIn("CAM USER / SHIP LOOK",post); self.assertIn("camera.fov=shipFov",post)
    def test_moon_range_rate_telemetry_is_derived_without_state_mutation(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn("hud_v0_18_range_rate.js",text)
        js=(server.demo_root()/"hud_v0_18_range_rate.js").read_text(encoding="utf-8")
        self.assertIn("moon.velocity_earth_centered_km_s",js); self.assertIn("wayfarer.velocity_earth_centered_km_s",js); self.assertIn("CLOSING",js); self.assertIn("RECEDING",js); self.assertIn("SAMPLED",js); self.assertNotIn("control",js)
    def test_terminal_quality_panel_is_fail_closed_and_non_commanding(self):
        text=server.validate_assets().read_text(encoding="utf-8"); self.assertIn('id="qualityPanel"',text); self.assertIn("hud_v0_20_quality_hook.js",text); self.assertIn("hud_v0_20_quality.js",text)
        hook=(server.demo_root()/"hud_v0_20_quality_hook.js").read_text(encoding="utf-8")
        panel=(server.demo_root()/"hud_v0_20_quality.js").read_text(encoding="utf-8")
        self.assertIn("rendezvous-preview.json",hook); self.assertIn("__loomRendezvousQuality",hook)
        self.assertIn("SOLVED_TRANSLATIONAL_FEASIBILITY",panel); self.assertIn("NOT SOLVED",panel)
        self.assertIn("MIN CLEAR",panel); self.assertIn("REMASS",panel); self.assertIn("REL V",panel); self.assertIn("Q4 ATT",panel); self.assertIn("TORCH OFF DURING SLEW",panel); self.assertNotIn("ATTITUDE TRANSITION UNQUALIFIED",panel); self.assertNotIn("/control",panel)
    def test_terminal_corrector_v2_uses_earth_facing_target_and_bounded_line_search(self):
        source=(server.repo_root()/"src"/"loom"/"hud"/"rendezvous_qualification.py").read_text(encoding="utf-8")
        self.assertIn("EARTH_FACING_MOON_RADIAL_QUALIFICATION_POINT",source)
        self.assertIn("LINE_SEARCH_SCALES",source)
        self.assertNotIn('"EARTH_TO_MOON_OUTWARD_RADIAL_QUALIFICATION_POINT"',source)
    def test_wayfarer_engineering_state_endpoint_and_panel_present(self):
        self.assertEqual(server.WAYFARER_ENGINEERING_ENDPOINT,"/wayfarer-engineering-state.json")
        text=server.validate_assets().read_text(encoding="utf-8")
        self.assertIn("hud_wayfarer_engineering_state_v01.js",text)
        self.assertIn("typed HUD StateDatum payload",text)
        self.assertIn("Protected water remains separate",text)
        js=(server.demo_root()/"hud_wayfarer_engineering_state_v01.js").read_text(encoding="utf-8")
        self.assertIn("LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1",js)
        self.assertIn("q(fs.primary)",js)
        self.assertIn("CERTIFIED",js)
        self.assertNotIn("mode_cards",js)
        self.assertNotIn("candidate_effective_area_m2",js)
        self.assertNotIn("/control",js)
    def test_freeze_record_exists_and_preserves_rotational_firewall(self):
        freeze=server.repo_root()/"engineering"/"hud"/"LOCAL_FLIGHT_QUALIFICATION_FREEZE_2026-09-11.md"
        self.assertTrue(freeze.is_file())
        text=freeze.read_text(encoding="utf-8")
        self.assertIn("ATTITUDE / ROTATIONAL AUTHORITY NOT INCLUDED",text)
        self.assertIn("Import only through governed engineering authority",text)
    def test_server_endpoints(self):
        self.assertEqual(server.LIVE_ENDPOINT,"/flight-view.json"); self.assertEqual(server.EARTH_MOON_ENDPOINT,"/earth-moon-qualification.json"); self.assertEqual(server.REALTIME_ENDPOINT,"/qualification-flight.json"); self.assertEqual(server.PREDICTED_PATH_ENDPOINT,"/qualification-flight/predicted-path.json"); self.assertEqual(server.TRAJECTORY_PREVIEW_ENDPOINT,"/qualification-flight/trajectory-preview.json"); self.assertEqual(server.INTERCEPT_PREVIEW_ENDPOINT,"/qualification-flight/intercept-preview.json"); self.assertEqual(server.RENDEZVOUS_PREVIEW_ENDPOINT,"/qualification-flight/rendezvous-preview.json"); self.assertEqual(server.WAYFARER_ENGINEERING_ENDPOINT,"/wayfarer-engineering-state.json")

if __name__=="__main__": unittest.main()
