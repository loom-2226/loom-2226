from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_browser_3d import build_run001_browser_3d  # noqa: E402

RAW = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"


class WayfarerBrowser3DExportTests(unittest.TestCase):
    def test_export_materialized_browser_3d_payload(self):
        raw = RAW.read_text(encoding="utf-8")
        package = build_run001_browser_3d(raw)
        encoded = base64.b64encode(package.html.encode("utf-8")).decode("ascii")
        print(f"LOOM_BROWSER_3D_B64::wayfarer_shipyard_3d.html::{package.html_sha256}::{encoded}")
        self.assertTrue(encoded)


if __name__ == "__main__":
    unittest.main()
