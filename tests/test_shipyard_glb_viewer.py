from __future__ import annotations

import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_glb_viewer import VIEWER_AUTHORITY, inspect_glb, parse_glb, viewer_html


class ShipyardGLBViewerTests(unittest.TestCase):
    def test_current_governed_semantic_glb_is_consumable(self):
        source = build_wayfarer_governed_synthesis()
        semantic = build_semantic_geometry(source)
        glb, _ = build_semantic_glb(source, semantic)
        info = inspect_glb(glb)
        self.assertEqual(info["viewer_authority"], VIEWER_AUTHORITY)
        self.assertEqual(info["mesh_count"], len(semantic.objects))
        self.assertEqual(info["semantic_node_count"], len(semantic.objects))
        self.assertEqual(info["asset_extras"]["source_semantic_package_hash"], semantic.package_hash)

    def test_generic_legacy_glb_without_semantic_extras_is_allowed(self):
        doc = b'{"asset":{"version":"2.0","generator":"LEGACY_VISUAL_FIXTURE"},"nodes":[],"meshes":[]}'
        doc += b" " * ((-len(doc)) % 4)
        bin_chunk = b"\x00\x00\x00\x00"
        total = 12 + 8 + len(doc) + 8 + len(bin_chunk)
        glb = struct.pack("<4sII", b"glTF", 2, total) + struct.pack("<II", len(doc), 0x4E4F534A) + doc + struct.pack("<II", len(bin_chunk), 0x004E4942) + bin_chunk
        info = inspect_glb(glb)
        self.assertEqual(info["generator"], "LEGACY_VISUAL_FIXTURE")
        self.assertEqual(info["semantic_node_count"], 0)

    def test_invalid_glb_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_glb(b"not a glb")

    def test_viewer_is_offline_glb_native_and_diagnostic(self):
        html = viewer_html()
        self.assertIn("fetch('/model.glb'", html)
        self.assertIn("GLB VIEWER ERROR", html)
        self.assertIn("semantic_object_id", html)
        self.assertNotIn("https://", html)
        self.assertNotIn("three.js", html.lower())


if __name__ == "__main__":
    unittest.main()
