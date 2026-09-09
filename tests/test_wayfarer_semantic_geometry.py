from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from governed_ship_synthesis import build_wayfarer_governed_synthesis  # noqa: E402
from semantic_geometry import (  # noqa: E402
    MUTABILITY_CONSTRAINED_ENVELOPE,
    MUTABILITY_PROXY_ONLY,
    MUTABILITY_STYLE_ONLY,
    SEMANTIC_CLASS_ADMITTED_ENVELOPE,
    SEMANTIC_CLASS_SOURCE_NODE_PROXY,
    SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS,
    SEMANTIC_GEOMETRY_AUTHORITY,
    STATUS_STRUCTURAL_UNQUALIFIED,
    SemanticGeometryError,
    build_semantic_geometry,
    canonical_json,
    geometry_hash,
    validate_semantic_geometry,
)


class WayfarerSemanticGeometryTests(unittest.TestCase):
    def source(self):
        return build_wayfarer_governed_synthesis(2226)

    def semantic(self):
        source = self.source()
        return source, build_semantic_geometry(source)

    def test_semantic_sidecar_maps_every_existing_primitive_one_to_one(self):
        source, semantic = self.semantic()
        self.assertEqual(len(semantic.objects), len(source.geometry.primitives))
        self.assertEqual(
            tuple(row.primitive_id for row in semantic.objects),
            tuple(row.primitive_id for row in source.geometry.primitives),
        )
        self.assertEqual(semantic.source_governed_package_hash, source.package_hash)
        self.assertEqual(semantic.source_geometry_hash, geometry_hash(source))
        self.assertEqual(semantic.source_design_candidate_hash, source.design_state.candidate_source_hash)

    def test_admitted_regions_preserve_engineering_envelope_identity_without_guessing_system(self):
        source, semantic = self.semantic()
        rows = [row for row in semantic.objects if row.semantic_class == SEMANTIC_CLASS_ADMITTED_ENVELOPE]
        self.assertEqual(len(rows), len(source.packaging.regions))
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(row.geometry_role, "ENGINEERING_ENVELOPE")
            self.assertEqual(row.visual_mutability, MUTABILITY_CONSTRAINED_ENVELOPE)
            self.assertEqual(row.engineering_status, "ADMITTED_GEOMETRY_SOURCE")
            self.assertEqual(row.system_id, "OPEN_NOT_CLASSIFIED_BY_R1")
            self.assertTrue(row.source_component_id)
            self.assertEqual(row.authority_status, SEMANTIC_GEOMETRY_AUTHORITY)

    def test_structural_semantics_remain_explicitly_unqualified(self):
        source, semantic = self.semantic()
        rows = [row for row in semantic.objects if row.semantic_class == SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS]
        self.assertEqual(len(rows), len(source.structure.members))
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(row.visual_mutability, MUTABILITY_STYLE_ONLY)
            self.assertEqual(row.engineering_status, STATUS_STRUCTURAL_UNQUALIFIED)
            self.assertEqual(row.system_id, "OPEN_NOT_CLASSIFIED_BY_R1")
            self.assertNotEqual(row.engineering_status, "PASS")

    def test_source_node_proxies_do_not_silently_acquire_volume(self):
        source, semantic = self.semantic()
        rows = [row for row in semantic.objects if row.semantic_class == SEMANTIC_CLASS_SOURCE_NODE_PROXY]
        self.assertEqual(len(rows), len(source.design_state.nodes))
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertEqual(row.visual_mutability, MUTABILITY_PROXY_ONLY)
            self.assertEqual(row.geometry_role, "SOURCE_LOCATION_PROXY")
            self.assertEqual(row.system_id, "OPEN_NOT_CLASSIFIED_BY_R1")
        for item in source.packaging.open_items:
            self.assertIn(item, semantic.open_semantic_items)
        self.assertIn("SYSTEM_CLASSIFICATION_OPEN_NOT_DERIVED_BY_R1", semantic.open_semantic_items)
        self.assertIn("AI_VISUAL_REALIZATION_NON_AUTHORITATIVE", semantic.open_semantic_items)

    def test_r1_does_not_guess_subsystem_classification_from_geometry_or_names(self):
        _, semantic = self.semantic()
        self.assertTrue(semantic.objects)
        self.assertTrue(all(row.system_id == "OPEN_NOT_CLASSIFIED_BY_R1" for row in semantic.objects))
        admitted_classes = {
            SEMANTIC_CLASS_ADMITTED_ENVELOPE,
            SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS,
            SEMANTIC_CLASS_SOURCE_NODE_PROXY,
        }
        self.assertTrue(all(row.semantic_class in admitted_classes for row in semantic.objects))

    def test_semantic_package_is_deterministic_and_does_not_mutate_source(self):
        source = self.source()
        before = source
        a = build_semantic_geometry(source)
        b = build_semantic_geometry(source)
        self.assertEqual(source, before)
        self.assertEqual(source.package_hash, before.package_hash)
        self.assertEqual(a, b)
        self.assertEqual(a.package_hash, b.package_hash)
        self.assertEqual(canonical_json(a, source), canonical_json(b, source))
        self.assertEqual(len(a.package_hash), 64)

    def test_semantic_authority_escalation_and_mapping_corruption_fail_closed(self):
        source, semantic = self.semantic()
        bad_authority = replace(semantic, authority_status="ENGINEERING_AUTHORITY")
        with self.assertRaises(SemanticGeometryError):
            validate_semantic_geometry(bad_authority, source)

        reversed_objects = tuple(reversed(semantic.objects))
        corrupted_order = replace(semantic, objects=reversed_objects)
        with self.assertRaises(SemanticGeometryError):
            validate_semantic_geometry(corrupted_order, source)

        structural_index = next(
            i for i, row in enumerate(semantic.objects)
            if row.semantic_class == SEMANTIC_CLASS_STRUCTURAL_HYPOTHESIS
        )
        bad_row = replace(semantic.objects[structural_index], engineering_status="PASS")
        bad_objects = list(semantic.objects)
        bad_objects[structural_index] = bad_row
        bad_structural_claim = replace(semantic, objects=tuple(bad_objects))
        with self.assertRaises(SemanticGeometryError):
            validate_semantic_geometry(bad_structural_claim, source)

    def test_semantic_sidecar_cannot_claim_frozen_authority(self):
        source, semantic = self.semantic()
        for mutation in (
            replace(semantic, flight_dynamics_authority=True),
            replace(semantic, canon_changed=True),
            replace(semantic, production_shipclasses_changed=True),
        ):
            with self.assertRaises(SemanticGeometryError):
                validate_semantic_geometry(mutation, source)


if __name__ == "__main__":
    unittest.main()
