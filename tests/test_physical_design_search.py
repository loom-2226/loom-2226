from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNTHESIS = ROOT / "qualification" / "synthesis"
if str(SYNTHESIS) not in sys.path:
    sys.path.insert(0, str(SYNTHESIS))

from physical_design_core import (  # noqa: E402
    CandidateDesign,
    DesignVariable,
    EvaluationResult,
    HardConstraintResult,
    ObjectiveTerm,
    PhysicalDesignError,
)
from physical_design_search import DeterministicGridSearch, SearchError, variable_values  # noqa: E402


class PhysicalDesignSearchTests(unittest.TestCase):
    def _solver(self, *, reject_all: bool = False):
        variables = (
            DesignVariable("x", 0.0, 2.0, 1.0, "m"),
            DesignVariable("y", 0.0, 1.0, 1.0, "m"),
        )

        def builder(candidate_id, seed, values):
            return CandidateDesign(
                candidate_id=candidate_id,
                seed=seed,
                component_types=(),
                component_instances=(),
                point_masses=(),
                solver_version="generic-test-v1",
                provenance_map={"x": str(values["x"]), "y": str(values["y"])},
            )

        def evaluator(candidate):
            x = float(candidate.provenance_map["x"])
            y = float(candidate.provenance_map["y"])
            if reject_all or (x == 0.0 and y == 0.0):
                raise PhysicalDesignError("hostile reject")
            return EvaluationResult(
                candidate_id=candidate.candidate_id,
                mass_kg=1.0,
                center_of_mass_m=(x, y, 0.0),
                parallel_axis_tensor_kg_m2=((0.0, 0.0, 0.0),) * 3,
                admitted_centroidal_tensor_kg_m2=((0.0, 0.0, 0.0),) * 3,
                candidate_aggregate_tensor_kg_m2=((0.0, 0.0, 0.0),) * 3,
                unresolved_inertia_mass_fraction=1.0,
                hard_constraints=(HardConstraintResult("LEGAL", True, "fixture"),),
                objective_vector=(
                    ObjectiveTerm("J1", abs(x - 1.0), "m", "target x=1"),
                    ObjectiveTerm("J2", y, "m", "prefer low y"),
                ),
                flight_dynamics_authority=False,
                authority_label="TEST",
            )

        return DeterministicGridSearch(
            solver_version="generic-test-v1",
            variables=variables,
            candidate_builder=builder,
            evaluator=evaluator,
        )

    def test_same_seed_reproduces_selected_candidate(self):
        solver = self._solver()
        a = solver.solve(2226)
        b = solver.solve(2226)
        self.assertEqual(a.candidate.candidate_id, b.candidate.candidate_id)
        self.assertEqual(a.evaluation.objective_vector, b.evaluation.objective_vector)
        self.assertEqual(a.examined_count, 6)
        self.assertEqual(a.legal_count, 5)

    def test_lexicographic_objectives_are_visible_and_select_candidate(self):
        result = self._solver().solve(7)
        self.assertEqual(result.evaluation.center_of_mass_m[:2], (1.0, 0.0))
        self.assertEqual(result.selector, "LEXICOGRAPHIC_OBJECTIVE_VECTOR_THEN_SEEDED_STABLE_HASH")

    def test_no_legal_candidate_fails_closed(self):
        with self.assertRaises(SearchError):
            self._solver(reject_all=True).solve(1)

    def test_invalid_grid_fails_closed(self):
        with self.assertRaises(SearchError):
            variable_values(DesignVariable("bad", 0.0, 1.0, 0.0, "m"))
        with self.assertRaises(SearchError):
            variable_values(DesignVariable("bad", 2.0, 1.0, 1.0, "m"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
