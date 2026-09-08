from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_browser_3d_js_syntax_fix import (  # noqa: E402
    JS_SYNTAX_FIX_VERSION,
    build_run001_browser_3d_js_syntax_fix,
)

RAW = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"


class WayfarerBrowser3DJavaScriptSyntaxFixTests(unittest.TestCase):
    def package(self):
        return build_run001_browser_3d_js_syntax_fix(RAW.read_text(encoding="utf-8"))

    def test_literal_newlines_inside_hud_js_string_are_removed(self):
        package = self.package()
        self.assertEqual(package.version, JS_SYNTAX_FIX_VERSION)
        self.assertNotIn("candidate_id)+'\nTouch/drag", package.html)
        self.assertIn("candidate_id)+'\\nTouch/drag", package.html)
        self.assertIn("zoom\\n'+D.authority_status", package.html)

    def test_node_parses_emitted_application_javascript(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("node not available in local test environment")
        package = self.package()
        scripts = re.findall(r"<script(?:[^>]*)>(.*?)</script>", package.html, re.S)
        self.assertEqual(len(scripts), 2)
        app_js = scripts[1]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "wayfarer_app.js"
            path.write_text(app_js, encoding="utf-8")
            proc = subprocess.run([node, "--check", str(path)], text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)

    def test_frozen_candidate_identity_and_authority_are_unchanged(self):
        package = self.package()
        self.assertEqual(package.parent_candidate_id, "CAND-5719E3F3251DE6E25FDF")
        self.assertEqual(package.child_candidate_id, "CAND-MUT-CB6ACB18C6768B2E0EF9")
        self.assertFalse(package.flight_dynamics_authority)
        self.assertFalse(package.canon_changed)
        self.assertFalse(package.production_shipclasses_changed)

    def test_replay_is_byte_deterministic(self):
        a = self.package()
        b = self.package()
        self.assertEqual(a.html_sha256, b.html_sha256)
        self.assertEqual(a.html, b.html)


if __name__ == "__main__":
    unittest.main()
