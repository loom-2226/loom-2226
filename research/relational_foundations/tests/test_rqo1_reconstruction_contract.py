from __future__ import annotations

import ast
import unittest
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
SRC = LANE / "src" / "rqo1_reconstruction.py"


class Rqo1ReconstructionContractTests(unittest.TestCase):
    def test_reconstruction_source_parses(self):
        ast.parse(SRC.read_text(encoding="utf-8"), filename=str(SRC))

    def test_recovered_contract_is_present(self):
        text = SRC.read_text(encoding="utf-8")
        for token in (
            "class ActionParams",
            "alpha * curvature_sum",
            "-p.beta * triangles",
            "nx.random_regular_graph",
            "double_edge_swap_proposal",
            "spectral_dimension",
            "volume_growth_dimension",
            "expander_log_ratio: float = 1.3",
            "len(candidates) >= 3",
        ):
            self.assertIn(token, text)

    def test_no_target_geometry_terms_in_candidate_dynamics(self):
        text = SRC.read_text(encoding="utf-8").lower()
        for forbidden in ("euclidean_distance", "target_lattice", "target_dimension", "x_coord", "y_coord", "z_coord"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
