import math
import unittest

from src.wayfarer_metric_node_array import build_metric_node_array


class WayfarerMetricNodeArrayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = build_metric_node_array()

    def test_exact_governing_node_count(self):
        self.assertEqual(self.result["node_count"], 208)
        self.assertEqual(len(self.result["nodes"]), 208)
        self.assertEqual(self.result["layout"]["axial_rings"], 13)
        self.assertEqual(self.result["layout"]["nodes_per_ring"], 16)

    def test_metric_scope_does_not_claim_loom_design(self):
        scope = self.result["scope"]
        self.assertTrue(scope["metric_design_baseline"])
        self.assertFalse(scope["loom_design_certified"])
        self.assertFalse(scope["rcs_geometry_defined_by_this_array"])
        self.assertFalse(scope["torch_geometry_defined_by_this_array"])

    def test_coordinates_are_deterministic_and_unique(self):
        ids = [node["id"] for node in self.result["nodes"]]
        self.assertEqual(len(ids), len(set(ids)))
        xyz = []
        for node in self.result["nodes"]:
            p = node["position_m"]
            self.assertTrue(all(math.isfinite(float(p[k])) for k in ("x", "y", "z")))
            xyz.append((round(p["x"], 9), round(p["y"], 9), round(p["z"], 9)))
        self.assertEqual(len(xyz), len(set(xyz)))

    def test_ring_geometry_is_regular(self):
        grouped = {}
        for node in self.result["nodes"]:
            grouped.setdefault(node["ring_index"], []).append(node)
        self.assertEqual(len(grouped), 13)
        for ring_index, nodes in grouped.items():
            self.assertEqual(len(nodes), 16)
            xs = {round(n["position_m"]["x"], 9) for n in nodes}
            radii = {
                round(math.hypot(n["position_m"]["y"], n["position_m"]["z"]), 9)
                for n in nodes
            }
            self.assertEqual(len(xs), 1)
            self.assertEqual(len(radii), 1)

    def test_axial_ring_centers_span_full_ship_without_endpoint_nodes(self):
        xs = sorted({round(n["position_m"]["x"], 9) for n in self.result["nodes"]})
        self.assertEqual(len(xs), 13)
        self.assertGreater(xs[0], 0.0)
        self.assertLess(xs[-1], 57.0)
        expected_pitch = 57.0 / 13.0
        self.assertAlmostEqual(xs[0], expected_pitch / 2.0, places=8)
        self.assertAlmostEqual(xs[-1], 57.0 - expected_pitch / 2.0, places=8)

    def test_support_radius_tracks_axial_structure(self):
        rings = self.result["rings"]
        by_group = {}
        for ring in rings:
            by_group.setdefault(ring["support_group"], []).append(ring)
        self.assertIn("pressure_hull", by_group)
        self.assertIn("main_structure", by_group)
        self.assertIn("shadow_shield", by_group)
        self.assertIn("reactor_torch_structure", by_group)
        self.assertIn("magnetic_nozzle_support", by_group)
        for ring in rings:
            self.assertGreater(ring["support_radius_m"], 0.0)

    def test_provenance_marks_layout_as_design_baseline(self):
        self.assertEqual(self.result["provenance"]["placement_status"], "DESIGN_BASELINE")
        self.assertEqual(self.result["provenance"]["node_count_status"], "CANON")
        self.assertFalse(self.result["authority"]["certifies_metric_domain_boundary"])
        self.assertFalse(self.result["authority"]["certifies_domain_membership"])


if __name__ == "__main__":
    unittest.main()
