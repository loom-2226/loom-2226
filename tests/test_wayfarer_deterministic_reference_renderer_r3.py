from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from deterministic_reference_renderer import (  # noqa: E402
    HANDOFF_BLOCKED,
    REFERENCE_RENDER_AUTHORITY,
    DeterministicReferenceRenderError,
    build_reference_render_package,
    canonical_manifest_json,
    standard_reference_cameras,
    validate_reference_render_package,
)
from governed_ship_synthesis import build_wayfarer_governed_synthesis, canonical_json as governed_json  # noqa: E402
from minimum_spatial_validation import build_minimum_spatial_validation  # noqa: E402
from semantic_geometry import build_semantic_geometry  # noqa: E402
from spatial_rule_contract import build_wayfarer_spatial_rule_contract  # noqa: E402
from spatial_validation_with_rules import build_spatial_validation_with_rules  # noqa: E402


class WayfarerDeterministicReferenceRendererR3Tests(unittest.TestCase):
    def packages(self):
        source = build_wayfarer_governed_synthesis(2226)
        semantic = build_semantic_geometry(source)
        r2 = build_minimum_spatial_validation(source, semantic)
        rules = build_wayfarer_spatial_rule_contract(source, semantic)
        r2a = build_spatial_validation_with_rules(source, semantic, r2=r2, rules=rules)
        r3 = build_reference_render_package(source, semantic, r2, rules, r2a)
        return source, semantic, r2, rules, r2a, r3

    def test_canonical_camera_set_and_artifact_coverage(self):
        *_, r3 = self.packages()
        cameras = standard_reference_cameras()
        self.assertEqual(len(cameras), 9)
        self.assertEqual(r3.cameras, cameras)
        self.assertEqual(tuple(a.view_id for a in r3.artifacts), tuple(c.view_id for c in cameras))
        self.assertEqual(
            tuple(c.view_id for c in cameras),
            (
                "FORE_PORT_3Q", "FORE_STARBOARD_3Q", "AFT_PORT_3Q", "AFT_STARBOARD_3Q",
                "PORT", "STARBOARD", "TOP", "FORE", "AFT",
            ),
        )

    def test_reference_evidence_is_emitted_while_visual_handoff_is_blocked(self):
        _, _, _, _, r2a, r3 = self.packages()
        self.assertFalse(r2a.visual_realization_ready)
        self.assertFalse(r3.visual_realization_ready)
        self.assertEqual(r3.visual_realization_handoff_status, HANDOFF_BLOCKED)
        self.assertEqual(len(r3.artifacts), 9)
        self.assertTrue(all(a.content for a in r3.artifacts))
        self.assertTrue(all("AI-HANDOFF=BLOCKED" in a.content for a in r3.artifacts))

    def test_svg_contains_semantic_identity_and_reference_authority(self):
        _, semantic, _, _, _, r3 = self.packages()
        svg = r3.artifacts[0].content
        self.assertIn(REFERENCE_RENDER_AUTHORITY, svg)
        self.assertIn("data-semantic-id=", svg)
        self.assertIn("data-semantic-class=", svg)
        self.assertIn(semantic.objects[0].semantic_object_id, svg)
        self.assertIn("NOT STRUCTURAL QUALIFICATION", svg)

    def test_render_output_and_manifest_are_deterministic(self):
        a = self.packages()[-1]
        b = self.packages()[-1]
        self.assertEqual(a, b)
        self.assertEqual(a.package_hash, b.package_hash)
        self.assertEqual([x.content_sha256 for x in a.artifacts], [x.content_sha256 for x in b.artifacts])
        self.assertEqual(canonical_manifest_json(a), canonical_manifest_json(b))
        self.assertEqual(len(a.package_hash), 64)

    def test_renderer_does_not_mutate_governed_design_state(self):
        source, semantic, r2, rules, r2a, _ = self.packages()
        before = governed_json(source)
        build_reference_render_package(source, semantic, r2, rules, r2a)
        after = governed_json(source)
        self.assertEqual(before, after)

    def test_source_hash_tampering_fails_closed(self):
        source, semantic, r2, rules, r2a, r3 = self.packages()
        bad = replace(r3, source_r2a_package_hash="0" * 64)
        with self.assertRaises(DeterministicReferenceRenderError):
            validate_reference_render_package(bad, source, semantic, r2, rules, r2a)

    def test_authority_escalation_fails_closed(self):
        source, semantic, r2, rules, r2a, r3 = self.packages()
        bad = replace(r3, structural_qualification=True)
        with self.assertRaises(DeterministicReferenceRenderError):
            validate_reference_render_package(bad, source, semantic, r2, rules, r2a)

    def test_artifact_content_tampering_fails_closed(self):
        source, semantic, r2, rules, r2a, r3 = self.packages()
        first = replace(r3.artifacts[0], content=r3.artifacts[0].content + "<!-- tamper -->\n")
        bad = replace(r3, artifacts=(first,) + r3.artifacts[1:])
        with self.assertRaises(DeterministicReferenceRenderError):
            validate_reference_render_package(bad, source, semantic, r2, rules, r2a)


if __name__ == "__main__":
    unittest.main()
