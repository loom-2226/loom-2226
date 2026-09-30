from __future__ import annotations

import random
import unittest

import networkx as nx

from research.relational_foundations.src.deterministic_curvature import (
    DeterministicCurvatureConfig,
    _ess,
    _split_rhat,
    full_curvature_action,
    run_deterministic_curvature,
)


class DeterministicCurvatureTests(unittest.TestCase):
    def test_full_action_is_independent_of_global_random_state(self):
        graph = nx.random_regular_graph(4, 12, seed=1)
        random.seed(1)
        first = full_curvature_action(graph)
        random.seed(999999)
        second = full_curvature_action(graph)
        self.assertAlmostEqual(first, second, places=12)

    def test_split_rhat_accepts_identical_stationary_chains(self):
        chains = [[0.0, 1.0] * 20 for _ in range(4)]
        rhat = _split_rhat(chains)
        self.assertIsNotNone(rhat)
        self.assertLessEqual(rhat, 1.10)

    def test_split_rhat_rejects_separated_constant_chains(self):
        chains = [[0.0] * 40, [0.0] * 40, [10.0] * 40, [10.0] * 40]
        rhat = _split_rhat(chains)
        self.assertTrue(rhat is None or rhat > 1.10)

    def test_ess_constant_chains_returns_full_sample_count(self):
        self.assertEqual(_ess([[1.0] * 32 for _ in range(4)]), 128.0)

    def test_small_functional_run_preserves_graph_invariants(self):
        config = DeterministicCurvatureConfig(
            N=12,
            avg_degree=4,
            seeds=(1, 2),
            proposals=10,
            burn_in=2,
            sample_every=2,
            ess_min=1.0,
            rhat_max=10.0,
        )
        payload = run_deterministic_curvature(config)
        self.assertTrue(payload["determinism_contract"]["passes"])
        self.assertEqual(len(payload["results"]), 4)
        for row in payload["results"]:
            self.assertTrue(row["degree_invariant"])
            self.assertTrue(row["connected_invariant"])


if __name__ == "__main__":
    unittest.main()
