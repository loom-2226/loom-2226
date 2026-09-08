from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "qualification" / "synthesis"
if str(SYNTH) not in sys.path:
    sys.path.insert(0, str(SYNTH))

from governed_ship_synthesis import (  # noqa: E402
    DESIGN_STATE_AUTHORITY,
    GEOMETRY_AUTHORITY,
    PACKAGE_AUTHORITY,
    STRUCTURE_AUTHORITY,
    TOPOLOGY_AUTHORITY,
    GovernedSynthesisError,
    build_wayfarer_governed_synthesis,
    canonical_json,
    validate_package,
)
from governed_ship_synthesis_viewer import build_wayfarer_viewer  # noqa: E402


class WayfarerGovernedSynthesisTests(unittest.TestCase):
    def package(self):
        return build_wayfarer_governed_synthesis(2226)

    def test_design_state_is_existing_wayfarer_candidate_not_new_ship_authority(self):
        package = self.package()
        self.assertEqual(package.design_state.candidate_id, "CAND-5719E3F3251DE6E25FDF")
        self.assertEqual(package.design_state.authority_status, DESIGN_STATE_AUTHORITY)
        self.assertEqual(package.authority_status, PACKAGE_AUTHORITY)
        self.assertFalse(package.flight_dynamics_authority)
        self.assertFalse(package.canon_changed)
        self.assertFalse(package.production_shipclasses_changed)
        self.assertEqual(package.design_state.dependency_graph_status, "OPEN_NO_COUPLED_DISCIPLINE_GRAPH_ADMITTED_v0.1")

    def test_two_representations_are_separate_and_topology_is_explicitly_hypothesis_only(self):
        package = self.package()
        self.assertGreater(len(package.design_state.nodes), 0)
        self.assertGreater(len(package.topology.nodes), len(package.design_state.nodes))
        self.assertGreater(len(package.topology.edges), 0)
        self.assertEqual(package.topology.authority_status, TOPOLOGY_AUTHORITY)
        self.assertTrue(all(edge.authority_status == TOPOLOGY_AUTHORITY for edge in package.topology.edges))
        self.assertTrue(any(edge.relation == "SYNTHESIS_BACKBONE_HYPOTHESIS" for edge in package.topology.edges))
        self.assertTrue(any("not a validated load path" in edge.rationale for edge in package.topology.edges))

    def test_packaging_preserves_admitted_envelopes_and_keeps_point_mass_volume_open(self):
        package = self.package()
        self.assertGreater(len(package.packaging.regions), 0)
        self.assertGreater(len(package.packaging.open_items), 0)
        self.assertTrue(all(item.startswith("NO_ADMITTED_VOLUME::") for item in package.packaging.open_items))
        self.assertTrue(all(region.region_kind.startswith("ADMITTED_") for region in package.packaging.regions))

    def test_structural_graph_is_never_structural_qualification(self):
        package = self.package()
        self.assertEqual(package.structure.authority_status, STRUCTURE_AUTHORITY)
        self.assertEqual(package.structure.qualification_status, "NOT_STRUCTURALLY_QUALIFIED")
        self.assertGreater(len(package.structure.members), 0)
        self.assertTrue(all(member.radius_m in (0.10, 0.18) for member in package.structure.members))
        self.assertTrue(all("not" in member.rationale.lower() for member in package.structure.members))

    def test_geometry_is_derived_triangle_mesh_not_authoritative_state(self):
        package = self.package()
        self.assertEqual(package.geometry.authority_status, GEOMETRY_AUTHORITY)
        kinds = {row.primitive_kind for row in package.geometry.primitives}
        self.assertIn("REGION_ENVELOPE", kinds)
        self.assertIn("STRUCTURAL_MEMBER", kinds)
        self.assertIn("SOURCE_NODE", kinds)
        self.assertGreater(len(package.geometry.primitives), len(package.packaging.regions))
        for row in package.geometry.primitives:
            self.assertGreater(len(row.vertices_m), 0)
            self.assertGreater(len(row.triangles), 0)

    def test_package_and_json_are_byte_deterministic(self):
        a = self.package()
        b = self.package()
        self.assertEqual(a, b)
        self.assertEqual(a.package_hash, b.package_hash)
        self.assertEqual(canonical_json(a), canonical_json(b))
        self.assertEqual(len(a.package_hash), 64)

    def test_authority_escalation_fails_closed(self):
        package = self.package()
        bad_structure = replace(package.structure, qualification_status="PASS")
        bad = replace(package, structure=bad_structure)
        with self.assertRaises(GovernedSynthesisError):
            validate_package(bad)
        bad2 = replace(package, flight_dynamics_authority=True)
        with self.assertRaises(GovernedSynthesisError):
            validate_package(bad2)

    def test_viewer_contains_compiled_mesh_and_governance_status(self):
        viewer = build_wayfarer_viewer(2226)
        self.assertIn("WAYFARER — GOVERNED SYNTHESIS v0.1", viewer.html)
        self.assertIn("NOT_STRUCTURALLY_QUALIFIED", viewer.html)
        self.assertIn("OPEN_NO_COUPLED_DISCIPLINE_GRAPH_ADMITTED_v0.1", viewer.html)
        self.assertIn("STRUCTURAL_MEMBER", viewer.html)
        self.assertIn("REGION_ENVELOPE", viewer.html)
        self.assertIn("SOURCE_NODE", viewer.html)
        self.assertNotIn("https://", viewer.html)
        self.assertNotIn("http://", viewer.html)
        self.assertFalse(viewer.flight_dynamics_authority)
        self.assertFalse(viewer.canon_changed)
        self.assertFalse(viewer.production_shipclasses_changed)


if __name__ == "__main__":
    unittest.main()
