from __future__ import annotations

import base64
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from wayfarer_visual_evidence import (  # noqa: E402
    VISUAL_EVIDENCE_AUTHORITY,
    build_run001_visual_evidence,
    write_visual_evidence,
)

RAW_PATH = ROOT / "research" / "model_runs" / "wayfarer_2026-09-08_run001" / "designer_raw.json"
EXPECTED_PARENT = "CAND-5719E3F3251DE6E25FDF"
EXPECTED_CHILD = "CAND-MUT-CB6ACB18C6768B2E0EF9"
EXPECTED_RAW_SHA = "ffcd34895be480a5f47506a29613a38fad36001c25728405c868fe0c95da8364"


class WayfarerVisualEvidenceTests(unittest.TestCase):
    def _package(self):
        raw = RAW_PATH.read_text(encoding="utf-8")
        return build_run001_visual_evidence(raw, seed=2226)

    def test_parent_child_use_identical_review_views_and_scale(self):
        package = self._package()
        self.assertEqual(package.parent_candidate_id, EXPECTED_PARENT)
        self.assertEqual(package.child_candidate_id, EXPECTED_CHILD)
        self.assertEqual(package.source_response_sha256, EXPECTED_RAW_SHA)
        self.assertEqual(package.authority_status, VISUAL_EVIDENCE_AUTHORITY)
        self.assertFalse(package.flight_dynamics_authority)
        self.assertFalse(package.canon_changed)
        self.assertFalse(package.production_shipclasses_changed)
        self.assertEqual([row.view_id for row in package.views], ["LONGITUDINAL_XZ", "PLAN_XY"])
        self.assertEqual(len(package.artifacts), 4)
        by_view = {}
        for artifact in package.artifacts:
            by_view.setdefault(artifact.view_id, []).append(artifact)
            self.assertIn("shared bounds:", artifact.content)
            self.assertIn("authority=REVIEW_EVIDENCE_ONLY", artifact.content)
        self.assertEqual({key: len(value) for key, value in by_view.items()}, {"LONGITUDINAL_XZ": 2, "PLAN_XY": 2})
        for view in package.views:
            expected = f"shared bounds: {view.horizontal_axis}=[{view.min_u_m:.3f},{view.max_u_m:.3f}] m; {view.vertical_axis}=[{view.min_v_m:.3f},{view.max_v_m:.3f}] m"
            self.assertTrue(all(expected in artifact.content for artifact in by_view[view.view_id]))

    def test_real_designer_launch_delta_is_visible_in_longitudinal_svg(self):
        package = self._package()
        parent = next(row for row in package.artifacts if row.artifact_id == "parent_longitudinal_xz.svg")
        child = next(row for row in package.artifacts if row.artifact_id == "child_longitudinal_xz.svg")
        self.assertIn("planetary_launch", parent.content)
        self.assertIn("planetary_launch", child.content)
        self.assertNotEqual(parent.content, child.content)
        self.assertNotEqual(parent.sha256, child.sha256)

    def test_package_and_files_are_byte_deterministic(self):
        a = self._package()
        b = self._package()
        self.assertEqual(a, b)
        self.assertEqual(len(a.package_sha256), 64)
        with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
            one = write_visual_evidence(a, Path(td1))
            two = write_visual_evidence(b, Path(td2))
            self.assertEqual(one, two)
            for name in one:
                self.assertEqual((Path(td1) / name).read_bytes(), (Path(td2) / name).read_bytes())

    def test_export_materialized_visual_evidence_payloads(self):
        package = self._package()
        for artifact in package.artifacts:
            encoded = base64.b64encode(artifact.content.encode("utf-8")).decode("ascii")
            print(f"LOOM_VISUAL_ARTIFACT_B64::{artifact.artifact_id}::{artifact.sha256}::{encoded}")
        with tempfile.TemporaryDirectory() as td:
            hashes = write_visual_evidence(package, Path(td))
            manifest = (Path(td) / "visual_evidence_manifest.json").read_text(encoding="utf-8")
            encoded = base64.b64encode(manifest.encode("utf-8")).decode("ascii")
            print(f"LOOM_VISUAL_ARTIFACT_B64::visual_evidence_manifest.json::{hashes['visual_evidence_manifest.json']}::{encoded}")


if __name__ == "__main__":
    unittest.main()
