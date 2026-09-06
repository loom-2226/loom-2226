from __future__ import annotations

"""Diagnostic qualification controls for RF-WP0.

These controls are not candidate physics. They test whether the measurement layer can
separate obvious expander-like/null graphs from explicit low-dimensional positive controls.
"""

import math
from typing import Dict

import networkx as nx
import numpy as np


def basic_diagnostics(G: nx.Graph) -> Dict[str, float]:
    n = G.number_of_nodes()
    if not nx.is_connected(G):
        raise ValueError("control graph must be connected")
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigvals = np.sort(np.linalg.eigvalsh(L))
    return {
        "N": n,
        "mean_degree": float(np.mean([d for _, d in G.degree()])),
        "avg_shortest_path": float(nx.average_shortest_path_length(G)),
        "avg_shortest_path_over_logN": float(nx.average_shortest_path_length(G) / math.log(n)),
        "diameter": float(nx.diameter(G)),
        "spectral_gap": float(eigvals[1]),
        "clustering": float(nx.average_clustering(G)),
    }


def make_control_suite(n: int = 100, degree: int = 4, seed: int = 2226) -> Dict[str, nx.Graph]:
    if n < 16:
        raise ValueError("n must be >=16")
    if degree < 2 or degree >= n or (n * degree) % 2:
        raise ValueError("invalid random-regular degree")
    side = int(round(math.sqrt(n)))
    grid_n = side * side
    return {
        "random_regular": nx.random_regular_graph(degree, n, seed=seed),
        "cycle": nx.cycle_graph(n),
        "grid_2d_torus": nx.grid_2d_graph(side, side, periodic=True),
        "small_world": nx.watts_strogatz_graph(n, degree if degree % 2 == 0 else degree + 1, 0.15, seed=seed),
        "grid_size_note": grid_n,
    }


def qualify_controls(n: int = 100, degree: int = 4, seed: int = 2226) -> Dict:
    suite = make_control_suite(n=n, degree=degree, seed=seed)
    note = suite.pop("grid_size_note")
    metrics = {name: basic_diagnostics(graph) for name, graph in suite.items()}
    rr = metrics["random_regular"]
    cyc = metrics["cycle"]
    grid = metrics["grid_2d_torus"]
    checks = {
        "cycle_path_ratio_exceeds_random_regular": cyc["avg_shortest_path_over_logN"] > rr["avg_shortest_path_over_logN"],
        "grid_path_ratio_exceeds_random_regular": grid["avg_shortest_path_over_logN"] > rr["avg_shortest_path_over_logN"],
        "random_regular_gap_exceeds_cycle": rr["spectral_gap"] > cyc["spectral_gap"],
        "random_regular_gap_exceeds_grid": rr["spectral_gap"] > grid["spectral_gap"],
    }
    return {
        "kind": "diagnostic_control_qualification",
        "requested_n": n,
        "grid_control_n": note,
        "degree": degree,
        "seed": seed,
        "metrics": metrics,
        "checks": checks,
        "passed": all(checks.values()),
    }
