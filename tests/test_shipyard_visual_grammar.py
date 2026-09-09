from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYN = ROOT / "qualification" / "synthesis"
if str(SYN) not in sys.path:
    sys.path.insert(0, str(SYN))

from governed_ship_synthesis import build_wayfarer_governed_synthesis
from semantic_geometry import build_semantic_geometry
from semantic_glb import build_semantic_glb
from shipyard_visual_grammar import (
    GRAMMARS,
    GRAMMAR_AUTHORITY,
    PACKET_AUTHORITY,
    ShipyardVisualGrammarError,
    build_realization_packet,
    canonical_packet_json,
    grammar_hash,
)


class ShipyardVisualGrammarTests(unittest.TestCase):
    def setUp(self):
        source = build_wayfarer_governed_synthesis()
        semantic = build_semantic_geometry(source)
        _, self.manifest = build_semantic_glb(source, semantic)

    def test_four_yards_are_structured_and_distinct(self):
        self.assertEqual(set(GRAMMARS), {"ASTERIA", "KELDRIN", "SHIKARI", "TASCHEN"})
        hashes = {grammar_hash(g) for g in GRAMMARS.values()}
        self.assertEqual(len(hashes), 4)
        for grammar in GRAMMARS.values():
            self.assertEqual(grammar.authority_status, GRAMMAR_AUTHORITY)
            self.assertTrue(grammar.fabrication_context)
            self.assertTrue(grammar.structural_doctrine)
            self.assertTrue(grammar.maintenance_doctrine)
            self.assertTrue(grammar.prohibited_interpretations)

    def test_packets_bind_same_engineering_glb_to_different_yards(self):
        packets = [build_realization_packet(self.manifest, yard) for yard in sorted(GRAMMARS)]
        self.assertEqual({p.source_glb_sha256 for p in packets}, {self.manifest["glb_sha256"]})
        self.assertEqual(len({p.grammar_hash for p in packets}), 4)
        self.assertEqual(len({p.packet_hash for p in packets}), 4)
        for p in packets:
            self.assertEqual(p.authority_status, PACKET_AUTHORITY)
            self.assertFalse(p.visual_realization_authoritative)
            self.assertFalse(p.may_backpropagate_engineering_claims)
            self.assertIn("Preserve constrained component identity", p.realization_instruction)
            self.assertIn("Generated detail is visualization, not engineering evidence", p.realization_instruction)
            self.assertTrue(canonical_packet_json(p))

    def test_authority_escalation_fails_closed(self):
        bad = dict(self.manifest)
        bad["flight_dynamics_authority"] = True
        with self.assertRaises(ShipyardVisualGrammarError):
            build_realization_packet(bad, "ASTERIA")
        with self.assertRaises(ShipyardVisualGrammarError):
            build_realization_packet(self.manifest, "UNKNOWN")

    def test_yards_are_doctrine_not_one_word_style_prompts(self):
        for yard, grammar in GRAMMARS.items():
            packet = build_realization_packet(self.manifest, yard)
            self.assertGreater(len(packet.realization_instruction.splitlines()), 15)
            self.assertNotEqual(packet.realization_instruction.strip(), yard)


if __name__ == "__main__":
    unittest.main()
