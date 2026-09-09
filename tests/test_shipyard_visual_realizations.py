import tempfile
import unittest
from pathlib import Path

from design_ledger import DesignLedger
from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_realization_handoff import build_library_realization_packet
from shipyard_visual_library import add_glb_asset
from shipyard_visual_realizations import REALIZATION_AUTHORITY, list_realizations, load_realization, store_realization


class VisualRealizationStoreTests(unittest.TestCase):
    def test_round_trip_binds_source_and_packet(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "ledger.sqlite3"
            with DesignLedger(db):
                pass
            source = build_wayfarer_governed_synthesis()
            semantic = build_semantic_geometry(source)
            glb, manifest = build_semantic_glb(source, semantic)
            asset = add_glb_asset(
                db, glb, display_name="Wayfarer — Governed Semantic", ship_name="Wayfarer",
                artifact_class="GOVERNED_SEMANTIC",
                source_candidate_id=manifest.get("source_design_candidate_id"),
                source_candidate_hash=manifest.get("source_design_candidate_hash"),
            )
            packet = build_library_realization_packet(asset, "ASTERIA")
            image = b"\x89PNG\r\n\x1a\nLOOM_TEST_IMAGE"
            stored = store_realization(
                db, source_asset_id=asset.asset_id, yard_id="ASTERIA",
                packet_hash=packet["packet_hash"], display_name="asteria-test.png",
                mime_type="image/png", payload=image,
            )
            self.assertEqual(stored.payload, image)
            self.assertEqual(stored.source_glb_sha256, asset.sha256)
            self.assertEqual(stored.packet_hash, packet["packet_hash"])
            self.assertEqual(stored.authority_status, REALIZATION_AUTHORITY)
            rows = list_realizations(db, asset.asset_id)
            self.assertEqual(len(rows), 1)
            self.assertEqual(load_realization(db, stored.realization_id).image_sha256, stored.image_sha256)


if __name__ == "__main__":
    unittest.main()
