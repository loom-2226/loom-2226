from __future__ import annotations

import json
import struct
import unittest

from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import SEMANTIC_GLB_AUTHORITY, SEMANTIC_GLB_VERSION, build_semantic_glb


def parse_glb(data: bytes):
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or total != len(data):
        raise AssertionError("invalid GLB header")
    off = 12
    chunks = []
    while off < len(data):
        length, ctype = struct.unpack_from("<II", data, off)
        off += 8
        payload = data[off:off + length]
        off += length
        chunks.append((ctype, payload))
    if len(chunks) != 2 or chunks[0][0] != 0x4E4F534A or chunks[1][0] != 0x004E4942:
        raise AssertionError("unexpected GLB chunks")
    return json.loads(chunks[0][1].decode("utf-8").rstrip(" \x00")), chunks[1][1]


class SemanticGLBTests(unittest.TestCase):
    def setUp(self):
        self.source = build_wayfarer_governed_synthesis()
        self.semantic = build_semantic_geometry(self.source)

    def test_deterministic_binary_and_manifest(self):
        a_glb, a_manifest = build_semantic_glb(self.source, self.semantic)
        b_glb, b_manifest = build_semantic_glb(self.source, self.semantic)
        self.assertEqual(a_glb, b_glb)
        self.assertEqual(a_manifest, b_manifest)
        self.assertEqual(a_manifest["version"], SEMANTIC_GLB_VERSION)
        self.assertEqual(a_manifest["authority_status"], SEMANTIC_GLB_AUTHORITY)
        self.assertFalse(a_manifest["flight_dynamics_authority"])
        self.assertFalse(a_manifest["canon_changed"])
        self.assertFalse(a_manifest["production_shipclasses_changed"])

    def test_one_node_per_semantic_object_with_extras(self):
        glb, manifest = build_semantic_glb(self.source, self.semantic)
        doc, binary = parse_glb(glb)
        self.assertEqual(doc["asset"]["version"], "2.0")
        self.assertEqual(doc["asset"]["generator"], SEMANTIC_GLB_VERSION)
        self.assertEqual(len(doc["nodes"]), len(self.semantic.objects))
        self.assertEqual(len(doc["meshes"]), len(self.semantic.objects))
        self.assertEqual(manifest["object_count"], len(self.semantic.objects))
        self.assertEqual(doc["buffers"][0]["byteLength"], sum(v["byteLength"] for v in doc["bufferViews"]))
        self.assertGreater(len(binary), 0)
        for node, sem in zip(doc["nodes"], self.semantic.objects):
            extras = node["extras"]
            self.assertEqual(extras["semantic_object_id"], sem.semantic_object_id)
            self.assertEqual(extras["primitive_id"], sem.primitive_id)
            self.assertEqual(extras["semantic_class"], sem.semantic_class)
            self.assertEqual(extras["engineering_status"], sem.engineering_status)
            self.assertEqual(extras["authority_status"], sem.authority_status)

    def test_glb_asset_binds_to_governed_and_semantic_hashes(self):
        glb, _ = build_semantic_glb(self.source, self.semantic)
        doc, _ = parse_glb(glb)
        extras = doc["asset"]["extras"]
        self.assertEqual(extras["source_governed_package_hash"], self.source.package_hash)
        self.assertEqual(extras["source_semantic_package_hash"], self.semantic.package_hash)
        self.assertFalse(extras["flight_dynamics_authority"])


if __name__ == "__main__":
    unittest.main()
