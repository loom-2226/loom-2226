from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_browser_3d_pixel_fix import (  # noqa: E402
    PIXEL_FIX_VERSION,
    build_run001_browser_3d_pixel_fix,
)

RAW = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"


class WayfarerBrowser3DPixelFixTests(unittest.TestCase):
    def package(self):
        return build_run001_browser_3d_pixel_fix(RAW.read_text(encoding="utf-8"))

    def test_column_major_matrix_multiply_is_used(self):
        html = self.package().html
        self.assertIn("r[col*4+row]+=a[k*4+row]*b[col*4+k]", html)
        self.assertNotIn("r[i*4+j]+=a[i*4+k]*b[k*4+j]", html)

    def test_pixel_diagnostics_are_visible_and_offline(self):
        package = self.package()
        self.assertEqual(package.version, PIXEL_FIX_VERSION)
        self.assertIn("WebGL context OK", package.html)
        self.assertIn("PIXEL STARTUP FAIL", package.html)
        self.assertIn("PROGRAM LINK FAIL", package.html)
        self.assertIn("shader bindings unavailable", package.html)
        self.assertIn("experimental-webgl", package.html)
        self.assertNotIn("http://", package.html)
        self.assertNotIn("https://", package.html)
        self.assertFalse(package.flight_dynamics_authority)
        self.assertFalse(package.canon_changed)
        self.assertFalse(package.production_shipclasses_changed)

    def test_real_parent_child_geometry_is_preserved(self):
        html = self.package().html
        self.assertIn('"candidate_id":"CAND-5719E3F3251DE6E25FDF"', html)
        self.assertIn('"candidate_id":"CAND-MUT-CB6ACB18C6768B2E0EF9"', html)
        self.assertIn('"translation_m":[21.75,0.0,5.2]', html)
        self.assertIn('"translation_m":[21.9,0.0,5.2]', html)

    def test_replay_is_byte_deterministic(self):
        a = self.package()
        b = self.package()
        self.assertEqual(a.html_sha256, b.html_sha256)
        self.assertEqual(a.html, b.html)


if __name__ == "__main__":
    unittest.main()
