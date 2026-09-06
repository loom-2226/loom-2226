from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from loom.spatial.http import install_spatial_state_endpoint


class _FakeSource:
    def snapshot(self, *args, **kwargs):
        return {"contract": "LOOM_SPATIAL_STATE_SNAPSHOT_V1", "states": []}


class _FakeHandler:
    def __init__(self, path: str):
        self.path = path
        self.sent = None
        self.fell_through = False

    def _send(self, code, content_type, body):
        self.sent = (code, content_type, body)

    def do_GET(self):
        self.fell_through = True


class _FakeSolar:
    SolarHandler = _FakeHandler


class SpatialHTTPViewerTest(unittest.TestCase):
    def test_serves_3d_view_and_script_and_preserves_fallback(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "solar3d.html").write_text("<html>LOOM 3D</html>", encoding="utf-8")
            (root / "solar3d.js").write_text("fetch('/spatial-state.json')", encoding="utf-8")
            install_spatial_state_endpoint(
                _FakeSolar,
                source=_FakeSource(),
                scene_epoch_utc="2226-06-15T09:59:34Z",
                campaign_revision=9,
                campaign_epoch_utc="2226-06-15T09:59:34.811247Z",
                epoch_source="CAMPAIGN_CLOCK",
                web_root=root,
            )

            page = _FakeHandler("/3d")
            page.do_GET()
            self.assertEqual(page.sent[0], 200)
            self.assertEqual(page.sent[1], "text/html; charset=utf-8")
            self.assertIn(b"LOOM 3D", page.sent[2])

            script = _FakeHandler("/3d.js")
            script.do_GET()
            self.assertEqual(script.sent[0], 200)
            self.assertEqual(script.sent[1], "application/javascript; charset=utf-8")
            self.assertIn(b"/spatial-state.json", script.sent[2])

            api = _FakeHandler("/spatial-state.json")
            api.do_GET()
            self.assertEqual(api.sent[0], 200)
            self.assertIn(b"LOOM_SPATIAL_STATE_SNAPSHOT_V1", api.sent[2])

            other = _FakeHandler("/existing-route")
            other.do_GET()
            self.assertTrue(other.fell_through)

    def test_checked_in_viewer_consumes_typed_read_only_fields(self):
        root = Path(__file__).resolve().parents[1]
        js = (root / "web" / "solar3d.js").read_text(encoding="utf-8")
        for token in ("/spatial-state.json", "position_km", "velocity_km_s", "navigation_grade", "state_class"):
            self.assertIn(token, js)
        self.assertNotIn("fetch('/commit", js)
        self.assertNotIn("fetch('/execute", js)


if __name__ == "__main__":
    unittest.main()
