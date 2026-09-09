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
from minimum_spatial_validation import (  # noqa: E402
    CHECK_OPEN,
    CHECK_PASS,
    CHECK_REVIEW,
    DECLARED_CLEARANCE,
    DEPLOYMENT_INTERFERENCE,
    DOCKING_ACCESS,
    OPEN_HANDLING,
    PAIRWISE_OVERLAP,
    READINESS_BLOCKED,
    SPATIAL_VALIDATION_AUTHORITY,
    THRUST_PLUME,
    MinimumSpatialValidationError,
    build_minimum_spatial_validation,
    canonical_json,
    validate_minimum_spatial_validation,
)
from semantic_geometry import build_semantic_geometry  # noqa: E402


class WayfarerMinimumSpatialValidationR2Tests(unittest.TestCase):
    def packages(self):
        source = build_wayfarer_governed_synthesis(2226)
        semantic = build_semantic_geometry(source)
        r2 = build_minimum_spatial_validation(source, semantic)
        return source, semantic, r2

    def test_r2_is_derived_only_and_never_escalates_authority(self):
        source, semantic, r2 = self.packages()
        self.assertEqual(r2.authority_status, SPATIAL_VALIDATION_AUTHORITY)
        self.assertFalse(r2.flight_dynamics_authority)
        self.assertFalse(r2.structural_qualification)
        self.assertFalse(r2.canon_changed)
        self.assertFalse(r2.production_shipclasses_changed)
        self.assertFalse(r2.design_state_mutated)
        self.assertEqual(r2.source_design_candidate_id, source.design_state.candidate_id)
        self.assertEqual(r2.source_governed_package_hash, source.package_hash)
        self.assertEqual(r2.source_semantic_package_hash, semantic.package_hash)

    def test_pairwise_screen_covers_only_admitted_packaging_envelopes(self):
        source, semantic, r2 = self.packages()
        pair_checks = [row for row in r2.checks if row.check_type == PAIRWISE_OVERLAP]
        n = len(source.packaging.regions)
        self.assertEqual(len(pair_checks), n * (n - 1) // 2)
        admitted_semantic_ids = {
            row.semantic_object_id
            for row in semantic.objects
            if row.semantic_class == "ADMITTED_SPATIAL_ENVELOPE"
        }
        for row in pair_checks:
            self.assertEqual(len(row.subject_ids), 2)
            self.assertTrue(set(row.subject_ids).issubset(admitted_semantic_ids))
            self.assertIn(row.status, {CHECK_PASS, CHECK_REVIEW})

    def test_missing_rules_remain_explicit_open_not_fabricated_passes(self):
        _, _, r2 = self.packages()
        open_types = {
            row.check_type
            for row in r2.checks
            if row.status == CHECK_OPEN
        }
        self.assertTrue(
            {DECLARED_CLEARANCE, DEPLOYMENT_INTERFERENCE, THRUST_PLUME, DOCKING_ACCESS}.issubset(open_types)
        )
        self.assertEqual(r2.readiness_status, READINESS_BLOCKED)
        self.assertFalse(r2.visual_realization_ready)

    def test_open_semantic_items_are_preserved_exactly(self):
        _, semantic, r2 = self.packages()
        self.assertEqual(r2.preserved_open_items, semantic.open_semantic_items)
        rows = [row for row in r2.checks if row.check_type == OPEN_HANDLING]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].status, CHECK_PASS)

    def test_r2_and_json_are_deterministic(self):
        source_a, semantic_a, r2_a = self.packages()
        source_b, semantic_b, r2_b = self.packages()
        self.assertEqual(r2_a, r2_b)
        self.assertEqual(r2_a.package_hash, r2_b.package_hash)
        self.assertEqual(canonical_json(r2_a, source_a, semantic_a), canonical_json(r2_b, source_b, semantic_b))
        self.assertEqual(len(r2_a.package_hash), 64)

    def test_authority_and_open_item_tampering_fail_closed(self):
        source, semantic, r2 = self.packages()
        bad = replace(r2, flight_dynamics_authority=True)
        with self.assertRaises(MinimumSpatialValidationError):
            validate_minimum_spatial_validation(bad, source, semantic)
        bad2 = replace(r2, preserved_open_items=())
        with self.assertRaises(MinimumSpatialValidationError):
            validate_minimum_spatial_validation(bad2, source, semantic)

    def test_false_ready_claim_fails_closed(self):
        source, semantic, r2 = self.packages()
        bad = replace(
            r2,
            readiness_status="READY_FOR_NON_AUTHORITATIVE_VISUAL_REALIZATION",
            visual_realization_ready=True,
        )
        with self.assertRaises(MinimumSpatialValidationError):
            validate_minimum_spatial_validation(bad, source, semantic)


if __name__ == "__main__":
    unittest.main()
