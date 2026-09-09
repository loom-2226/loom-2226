from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from design_ledger import DesignLedger
from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_realization_handoff import HANDOFF_AUTHORITY, build_library_realization_packet, canonical_packet_json
from shipyard_visual_library import add_glb_asset


class ShipyardRealizationHandoffTests(unittest.TestCase):
    def _asset(self):
        td = tempfile.TemporaryDirectory()
        db = Path(td.name) / "ledger.sqlite3"
        with DesignLedger(db):
            pass
        source = build_wayfarer_governed_synthesis()
        semantic = build_semantic_geometry(source)
        glb, manifest = build_semantic_glb(source, semantic)
        asset = add_glb_asset(
            db,
            glb,
            display_name="Wayfarer — Governed Semantic",
            ship_name="Wayfarer",
            artifact_class="GOVERNED_SEMANTIC",
            source_candidate_id=manifest.get("source_design_candidate_id"),
            source_candidate_hash=manifest.get("source_design_candidate_hash"),
        )
        return td, asset

    def test_all_yards_generate_deterministic_packets(self):
        td, asset = self._asset()
        try:
            hashes = set()
            for yard in ("ASTERIA", "KELDRIN", "SHIKARI", "TASCHEN"):
                a = build_library_realization_packet(asset, yard)
                b = build_library_realization_packet(asset, yard)
                self.assertEqual(a["packet_hash"], b["packet_hash"])
                self.assertEqual(a["authority_status"], HANDOFF_AUTHORITY)
                self.assertFalse(a["visual_realization_authoritative"])
                self.assertFalse(a["may_backpropagate_engineering_claims"])
                self.assertGreaterEqual(len(a["component_map"]), 1)
                self.assertEqual(len(a["reference_views"]), 7)
                canonical_packet_json(a)
                hashes.add(a["packet_hash"])
            self.assertEqual(len(hashes), 4)
        finally:
            td.cleanup()

    def test_component_map_preserves_explicit_semantics(self):
        td, asset = self._asset()
        try:
            packet = build_library_realization_packet(asset, "ASTERIA")
            self.assertTrue(any(x["classification_basis"] == "EXPLICIT_SEMANTIC_EXTRAS" for x in packet["component_map"]))
            self.assertTrue(any(x["inferred_component_class"] != "OTHER" for x in packet["component_map"]))
        finally:
            td.cleanup()

    def test_unknown_yard_fails_closed(self):
        td, asset = self._asset()
        try:
            with self.assertRaises(ValueError):
                build_library_realization_packet(asset, "UNKNOWN")
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
