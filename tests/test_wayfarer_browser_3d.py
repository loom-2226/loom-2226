from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_browser_3d import (  # noqa: E402
    BROWSER_3D_AUTHORITY,
    build_run001_browser_3d,
    write_browser_3d,
)

RAW = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"


class WayfarerBrowser3DTests(unittest.TestCase):
    def raw(self) -> str:
        return RAW.read_text(encoding="utf-8")

    def test_run001_is_self_contained_android_browser_evidence(self):
        package = build_run001_browser_3d(self.raw())
        self.assertEqual(package.parent_candidate_id, "CAND-5719E3F3251DE6E25FDF")
        self.assertEqual(package.child_candidate_id, "CAND-MUT-CB6ACB18C6768B2E0EF9")
        self.assertEqual(package.authority_status, BROWSER_3D_AUTHORITY)
        self.assertFalse(package.flight_dynamics_authority)
        self.assertFalse(package.canon_changed)
        self.assertFalse(package.production_shipclasses_changed)
        self.assertIn("getContext('webgl'", package.html)
        self.assertIn("touch-action:none", package.html)
        self.assertIn("touchmove", package.html)
        self.assertIn("pointermove", package.html)
        self.assertNotIn("http://", package.html)
        self.assertNotIn("https://", package.html)
        self.assertNotIn("three.min.js", package.html)
        self.assertNotIn("Blender", package.html)

    def test_real_designer_delta_is_embedded_in_3d_geometry(self):
        html = build_run001_browser_3d(self.raw()).html
        self.assertIn('"id":"planetary_launch"', html)
        self.assertIn('"translation_m":[21.75,0.0,5.2]', html)
        self.assertIn('"translation_m":[21.9,0.0,5.2]', html)
        self.assertIn("PARENT", html)
        self.assertIn("CHILD", html)
        self.assertIn("OVERLAY", html)

    def test_package_is_byte_deterministic(self):
        a = build_run001_browser_3d(self.raw())
        b = build_run001_browser_3d(self.raw())
        self.assertEqual(a, b)
        self.assertEqual(a.html_sha256, b.html_sha256)

    def test_writer_materializes_single_file_mobile_viewer_and_manifest(self):
        package = build_run001_browser_3d(self.raw())
        with tempfile.TemporaryDirectory() as td:
            written = write_browser_3d(package, Path(td))
            self.assertEqual(written["wayfarer_shipyard_3d.html"], package.html_sha256)
            html = (Path(td) / "wayfarer_shipyard_3d.html").read_text(encoding="utf-8")
            self.assertEqual(html, package.html)
            self.assertTrue((Path(td) / "browser_3d_manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
