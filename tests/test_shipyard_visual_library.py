from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "qualification" / "synthesis"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from design_ledger import DesignLedger
from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_visual_library import (
    VisualLibraryError,
    add_glb_asset,
    list_assets,
    load_asset,
)


class VisualLibraryTests(unittest.TestCase):
    def make_db(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "ledger.sqlite3"
        with DesignLedger(path):
            pass
        return td, path

    def semantic_glb(self):
        source = build_wayfarer_governed_synthesis()
        semantic = build_semantic_geometry(source)
        return source, semantic, build_semantic_glb(source, semantic)

    def test_governed_asset_round_trip_and_catalog(self):
        td, db = self.make_db()
        self.addCleanup(td.cleanup)
        source, semantic, (glb, manifest) = self.semantic_glb()
        asset = add_glb_asset(
            db, glb, display_name="Wayfarer — Governed Semantic", ship_name="Wayfarer",
            artifact_class="GOVERNED_SEMANTIC",
            source_candidate_id=manifest["source_design_candidate_id"],
            source_candidate_hash=manifest["source_design_candidate_hash"],
        )
        self.assertEqual(asset.payload, glb)
        self.assertEqual(asset.semantic_node_count, manifest["object_count"])
        rows = list_assets(db)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["asset_id"], asset.asset_id)
        self.assertEqual(load_asset(db, asset.asset_id).payload, glb)

    def test_visual_reference_is_non_authoritative(self):
        td, db = self.make_db()
        self.addCleanup(td.cleanup)
        _, _, (glb, _) = self.semantic_glb()
        asset = add_glb_asset(
            db, glb, display_name="Wayfarer — Visual Reference", ship_name="Wayfarer",
            artifact_class="VISUAL_REFERENCE",
        )
        self.assertEqual(asset.authority_status, "NON_AUTHORITATIVE_VISUAL_REFERENCE_ONLY")

    def test_duplicate_payload_is_idempotent_within_class(self):
        td, db = self.make_db()
        self.addCleanup(td.cleanup)
        _, _, (glb, _) = self.semantic_glb()
        a = add_glb_asset(db, glb, display_name="A", ship_name="Wayfarer", artifact_class="VISUAL_REFERENCE")
        b = add_glb_asset(db, glb, display_name="B", ship_name="Wayfarer", artifact_class="VISUAL_REFERENCE")
        self.assertEqual(a.asset_id, b.asset_id)
        self.assertEqual(len(list_assets(db)), 1)
        self.assertEqual(list_assets(db)[0]["display_name"], "B")

    def test_refuses_non_loom_sqlite(self):
        td = tempfile.TemporaryDirectory(); self.addCleanup(td.cleanup)
        db = Path(td.name) / "notloom.sqlite3"
        sqlite3.connect(db).close()
        _, _, (glb, _) = self.semantic_glb()
        with self.assertRaises(VisualLibraryError):
            add_glb_asset(db, glb, display_name="X", ship_name="X", artifact_class="EXTERNAL_FIXTURE")

    def test_detects_blob_corruption(self):
        td, db = self.make_db(); self.addCleanup(td.cleanup)
        _, _, (glb, _) = self.semantic_glb()
        asset = add_glb_asset(db, glb, display_name="X", ship_name="X", artifact_class="EXTERNAL_FIXTURE")
        con = sqlite3.connect(db)
        con.execute("UPDATE visual_library_asset SET payload=? WHERE asset_id=?", (sqlite3.Binary(b"broken"), asset.asset_id))
        con.commit(); con.close()
        with self.assertRaises(VisualLibraryError):
            load_asset(db, asset.asset_id)


if __name__ == "__main__":
    unittest.main()
