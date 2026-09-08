from __future__ import annotations

import dataclasses
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

ADAPTER_PATH = SYNTHESIS / "wayfarer_s1_adapter.py"
spec = importlib.util.spec_from_file_location("wayfarer_s1_adapter", ADAPTER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load S1 adapter from {ADAPTER_PATH}")
adapter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = adapter
spec.loader.exec_module(adapter)


def valid_candidate():
    return adapter.build_candidate(
        candidate_id="fixture",
        seed=2226,
        relational_x_m=26.0,
        launch_x_m=22.0,
        tank_x_m=25.0,
        solver_version="test",
    )


class WayfarerS1AdapterTests(unittest.TestCase):
    def test_valid_mode_a_candidate_preserves_mass_and_firewall(self):
        result = adapter.evaluate_candidate(valid_candidate())
        self.assertEqual(result.mass_kg, 1_158_500.0)
        self.assertFalse(result.flight_dynamics_authority)
        self.assertEqual(result.authority_label, adapter.S1_AUTHORITY_LABEL)
        self.assertGreater(result.unresolved_inertia_mass_fraction, 0.89)
        self.assertLess(result.unresolved_inertia_mass_fraction, 0.90)
        self.assertTrue(all(c.passed for c in result.hard_constraints))
        self.assertEqual(len(result.objective_vector), 7)

    def test_launch_outside_bay_rejects(self):
        candidate = adapter.build_candidate(
            candidate_id="bad-launch",
            seed=1,
            relational_x_m=26.0,
            launch_x_m=24.0,
            tank_x_m=25.0,
            solver_version="test",
        )
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_tank_quadrature_broken_rejects(self):
        candidate = valid_candidate()
        points = list(candidate.point_masses)
        for i, point in enumerate(points):
            if point.source_id == "normal_remass_tank_1":
                points[i] = dataclasses.replace(point, centroid_m=(25.0, 0.0, 0.0))
                break
        candidate = dataclasses.replace(candidate, point_masses=tuple(points))
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_remass_not_250_t_rejects(self):
        candidate = adapter.build_candidate(
            candidate_id="bad-remass",
            seed=1,
            relational_x_m=26.0,
            launch_x_m=22.0,
            tank_x_m=25.0,
            tank_mass_kg=60_000.0,
            solver_version="test",
        )
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_working_fluid_water_not_300_t_rejects(self):
        candidate = valid_candidate()
        candidate = dataclasses.replace(
            candidate,
            store_decomposition_kg={"normal_remass": 250_000.0, "protected_water": 40_000.0},
        )
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_collision_between_admitted_full_bodies_rejects(self):
        candidate = adapter.build_candidate(
            candidate_id="collision",
            seed=1,
            relational_x_m=26.0,
            launch_x_m=22.0,
            tank_x_m=25.0,
            launch_yz_m=(0.0, 0.0),
            solver_version="test",
        )
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_attempt_to_use_open_geometry_rejects(self):
        candidate = adapter.build_candidate(
            candidate_id="open-geometry",
            seed=1,
            relational_x_m=26.0,
            launch_x_m=22.0,
            tank_x_m=25.0,
            solver_version="test",
            open_geometry_used=("radiator.panel_geometry",),
        )
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(candidate)

    def test_negative_or_nan_mass_fails_closed(self):
        for bad_mass in (-1.0, float("nan")):
            candidate = adapter.build_candidate(
                candidate_id="bad-mass",
                seed=1,
                relational_x_m=26.0,
                launch_x_m=22.0,
                tank_x_m=25.0,
                tank_mass_kg=bad_mass,
                solver_version="test",
            )
            with self.assertRaises(adapter.WayfarerS1Error):
                adapter.evaluate_candidate(candidate)

    def test_flight_authority_request_fails_closed(self):
        with self.assertRaises(adapter.WayfarerS1Error):
            adapter.evaluate_candidate(valid_candidate(), requested_flight_authority=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
