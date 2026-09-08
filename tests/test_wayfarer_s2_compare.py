from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

import wayfarer_s2_compare as s2  # noqa: E402


class WayfarerS2CompareTests(unittest.TestCase):
    def test_baseline_reproduces_qualified_docked_mass_and_com(self):
        payload = s2.compare(2226)
        self.assertEqual(payload["baseline"]["mass_kg"], 1_158_500.0)
        self.assertEqual(
            payload["baseline"]["center_of_mass_m"],
            [26.676650841605525, 0.0, 0.14812257229175657],
        )

    def test_generated_candidate_matches_closed_s1(self):
        payload = s2.compare(2226)
        self.assertEqual(payload["generated"]["candidate_id"], "CAND-5719E3F3251DE6E25FDF")
        self.assertEqual(payload["generated"]["placement_tuple_m"]["relational_x_m"], 26.0)
        self.assertEqual(payload["generated"]["placement_tuple_m"]["launch_x_m"], 21.75)
        self.assertEqual(payload["generated"]["placement_tuple_m"]["tank_x_m"], 26.5)

    def test_position_deltas_are_real_solver_differences(self):
        payload = s2.compare(2226)
        delta = payload["deltas_generated_minus_baseline"]["placement_m"]
        self.assertEqual(delta["relational_x_m"], 0.0)
        self.assertAlmostEqual(delta["launch_x_m"], -0.05, places=12)
        self.assertEqual(delta["tank_x_m"], 1.5)

    def test_both_layouts_are_legal_under_same_model(self):
        payload = s2.compare(2226)
        for side in ("baseline", "generated"):
            self.assertTrue(all(row["passed"] for row in payload[side]["hard_constraints"]))
        self.assertEqual(payload["deltas_generated_minus_baseline"]["mass_kg"], 0.0)

    def test_full_inertia_and_principal_axes_remain_open(self):
        payload = s2.compare(2226)
        limitations = payload["common_model_limitations"]
        self.assertIn("FULL_WAYFARER_CENTROIDAL_INERTIA_OPEN_NOT_QUALIFIED", limitations)
        self.assertIn("PRINCIPAL_AXES_OPEN_WITHOUT_FULL_INERTIA", limitations)
        self.assertFalse(payload["authority_firewall"]["flight_dynamics_authority"])
        self.assertFalse(payload["authority_firewall"]["wayfarer_flight_inertia_qualified"])
        self.assertFalse(payload["authority_firewall"]["canon_changed"])
        self.assertFalse(payload["authority_firewall"]["production_shipclasses_changed"])

    def test_objective_comparison_preserves_all_visible_terms(self):
        payload = s2.compare(2226)
        rows = payload["deltas_generated_minus_baseline"]["objective_vector"]
        self.assertEqual(len(rows), 7)
        self.assertEqual([row["objective_id"] for row in rows], [
            "J1_TRANSVERSE_COM_OFFSET",
            "J2_LONGITUDINAL_COM_BAND_DEVIATION",
            "J3_ROTATIONAL_CONTROL_BURDEN_SURROGATE",
            "J4_REMASS_FEED_DISTANCE_SURROGATE",
            "J5_MAJOR_POWER_PATH_SURROGATE",
            "J6_PACKAGING_COLLISION_PENALTY",
            "J7_LAUNCH_EXTRACTION_PENALTY",
        ])

    def test_comparison_is_byte_deterministic(self):
        a = s2.canonical_json(2226)
        b = s2.canonical_json(2226)
        self.assertEqual(a, b)
        json.loads(a)


if __name__ == "__main__":
    unittest.main(verbosity=2)
