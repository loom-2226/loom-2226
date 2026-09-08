from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

import wayfarer_s1_solver as solver  # noqa: E402


class WayfarerS1SolverTests(unittest.TestCase):
    def test_same_seed_same_candidate_and_payload(self):
        a = solver.solve(2226)
        b = solver.solve(2226)
        self.assertEqual(a.candidate.candidate_id, b.candidate.candidate_id)
        self.assertEqual(solver.canonical_json(a), solver.canonical_json(b))

    def test_solver_makes_real_placement_decisions(self):
        result = solver.solve(2226)
        transforms = {
            row.instance_id: row.transform.translation_m
            for row in result.candidate.component_instances
        }
        tank_x = {
            point.centroid_m[0]
            for point in result.candidate.point_masses
            if point.source_id.startswith("normal_remass_tank_")
        }
        self.assertEqual(len(tank_x), 1)
        selected = (transforms["relational_plant"][0], transforms["planetary_launch"][0], next(iter(tank_x)))
        self.assertNotEqual(selected, (26.0, 21.8, 25.0))
        self.assertGreater(result.examined_count, 1)
        self.assertGreater(result.legal_count, 0)

    def test_selected_candidate_passes_s1_gate_without_authority_promotion(self):
        result = solver.solve(2226)
        payload = solver.result_payload(result)
        self.assertEqual(payload["PROCEDURAL_LAYOUT_FEASIBILITY"], "PASS")
        self.assertEqual(payload["mass_kg"], 1_158_500.0)
        self.assertEqual(payload["store_decomposition_kg"]["normal_remass"], 250_000.0)
        self.assertEqual(payload["store_decomposition_kg"]["protected_water"], 50_000.0)
        self.assertFalse(payload["flight_dynamics_authority"])
        self.assertFalse(payload["wayfarer_flight_inertia_qualified"])
        self.assertFalse(payload["canon_changed"])
        self.assertFalse(payload["production_shipclasses_changed"])
        self.assertFalse(payload["surrogate_full_inertia_used"])
        self.assertTrue(all(row["passed"] for row in payload["hard_constraints"]))
        self.assertEqual(len(payload["objective_vector"]), 7)
        self.assertGreater(payload["unresolved_inertia_mass_fraction"], 0.89)

    def test_output_retains_required_provenance_and_physical_surfaces(self):
        payload = solver.result_payload(solver.solve(2226))
        self.assertTrue(payload["input_hashes"])
        self.assertTrue(payload["provenance_map"])
        self.assertEqual(len(payload["admitted_equivalent_bodies"]), 2)
        self.assertEqual(len(payload["tank_point_mass_decomposition"]), 4)
        self.assertEqual(len(payload["abstract_placement_keep_out_objects"]), 4)
        self.assertEqual(len(payload["parallel_axis_tensor_kg_m2"]), 3)
        self.assertEqual(len(payload["candidate_aggregate_tensor_kg_m2"]), 3)
        json.dumps(payload, allow_nan=False)

    def test_grid_does_not_contain_hand_authored_launch_station(self):
        launch = next(v for v in solver.S1_VARIABLES if v.variable_id == "launch_x_m")
        from physical_design_search import variable_values
        self.assertNotIn(21.8, variable_values(launch))


if __name__ == "__main__":
    unittest.main(verbosity=2)
