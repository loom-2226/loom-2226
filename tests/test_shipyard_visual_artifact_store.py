from __future__ import annotations

import hashlib
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "qualification" / "synthesis"
SRC = ROOT / "src"
for p in (SYN, SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from design_ledger import DesignLedger
from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_visual_artifact_store import STORE_AUTHORITY, VisualArtifactStoreError, load_artifact, store_semantic_glb


class VisualArtifactStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "shipyard.sqlite3"
        with DesignLedger(self.db):
            pass
        source = build_wayfarer_governed_synthesis()
        semantic = build_semantic_geometry(source)
        self.glb, self.manifest = build_semantic_glb(source, semantic)

    def tearDown(self):
        self.temp.cleanup()

    def test_whole_glb_round_trip_is_byte_exact(self):
        stored = store_semantic_glb(self.db, self.glb, self.manifest)
        loaded = load_artifact(self.db, stored.artifact_id)
        self.assertEqual(loaded.payload, self.glb)
        self.assertEqual(loaded.artifact_sha256, hashlib.sha256(self.glb).hexdigest())
        self.assertEqual(loaded.authority_status, STORE_AUTHORITY)
        self.assertEqual(loaded.manifest, self.manifest)

    def test_same_glb_is_deterministic_upsert(self):
        first = store_semantic_glb(self.db, self.glb, self.manifest)
        second = store_semantic_glb(self.db, self.glb, self.manifest)
        self.assertEqual(first.artifact_id, second.artifact_id)
        con = sqlite3.connect(self.db)
        try:
            count = con.execute("SELECT COUNT(*) FROM visual_artifact_blob").fetchone()[0]
        finally:
            con.close()
        self.assertEqual(count, 1)

    def test_corruption_is_detected_on_read(self):
        stored = store_semantic_glb(self.db, self.glb, self.manifest)
        con = sqlite3.connect(self.db)
        try:
            con.execute("UPDATE visual_artifact_blob SET payload=? WHERE artifact_id=?", (sqlite3.Binary(b"corrupt"), stored.artifact_id))
            con.commit()
        finally:
            con.close()
        with self.assertRaises(VisualArtifactStoreError):
            load_artifact(self.db, stored.artifact_id)

    def test_non_ledger_sqlite_fails_closed(self):
        bad = Path(self.temp.name) / "not-ledger.sqlite3"
        sqlite3.connect(bad).close()
        with self.assertRaises(VisualArtifactStoreError):
            store_semantic_glb(bad, self.glb, self.manifest)

    def test_authority_escalation_is_rejected(self):
        manifest = dict(self.manifest)
        manifest["flight_dynamics_authority"] = True
        with self.assertRaises(VisualArtifactStoreError):
            store_semantic_glb(self.db, self.glb, manifest)


if __name__ == "__main__":
    unittest.main()
