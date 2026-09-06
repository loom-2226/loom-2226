from __future__ import annotations

"""Faithful research reconstruction of the surviving 28 Aug 2026 RQO-1 source.

This module reproduces the recovered mechanics and diagnostics, but is not claimed
as a byte-identical archival copy of the original File Library object.
"""

import itertools
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
from scipy.optimize import linprog

RNG_SEED = 2226


def lazy_rw_measure(G: nx.Graph, node, idle_mass: float = 0.5) -> Dict:
    neighbors = list(G.neighbors(node))
    if not neighbors:
        return {node: 1.0}
    m = {node: idle_mass}
    share = (1.0 - idle_mass) / len(neighbors)
    for nb in neighbors:
        m[nb] = m.get(nb, 0.0) + share
    return m


def wasserstein1(mu: Dict, nu: Dict, dist: Dict[Tuple, float]) -> float:
    support_a = list(mu.keys())
    support_b = list(nu.keys())
    na, nb = len(support_a), len(support_b)
    c = np.array([dist[(a, b)] for a in support_a for b in support_b])
    A_eq = []
    b_eq = []
    for i in range(na):
        row = np.zeros(na * nb)
        row[i * nb:(i + 1) * nb] = 1.0
        A_eq.append(row)
        b_eq.append(mu[support_a[i]])
    for j in range(nb):
        row = np.zeros(na * nb)
        row[j::nb] = 1.0
        A_eq.append(row)
        b_eq.append(nu[support_b[j]])
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method="highs")
    if not res.success:
        raise RuntimeError(f"Wasserstein LP failed: {res.message}")
    return float(res.fun)


def ollivier_ricci_edge(G: nx.Graph, sp_cache: Dict, i, j, idle_mass: float = 0.5) -> float:
    mu, nu = lazy_rw_measure(G, i, idle_mass), lazy_rw_measure(G, j, idle_mass)
    support = set(mu) | set(nu)
    dist = {}
    for a in support:
        for b in support:
            dist[(a, b)] = sp_cache.get((a, b), sp_cache.get((b, a)))
            if dist[(a, b)] is None:
                dist[(a, b)] = nx.shortest_path_length(G, a, b)
    d_ij = sp_cache.get((i, j), 1.0) or 1.0
    return 1.0 - wasserstein1(mu, nu, dist) / d_ij


def curvature_sum(G: nx.Graph, max_edges: int | None = None) -> float:
    edges = list(G.edges())
    if max_edges and len(edges) > max_edges:
        edges = random.sample(edges, max_edges)
    all_pairs = dict(nx.all_pairs_shortest_path_length(G))
    sp_flat = {(u, v): l for u, d in all_pairs.items() for v, l in d.items()}
    total = sum(ollivier_ricci_edge(G, sp_flat, i, j) for i, j in edges)
    scale = len(G.edges()) / max(1, len(edges))
    return total * scale


@dataclass
class ActionParams:
    alpha: float = 0.0
    beta: float = 0.0
    curvature_sample_edges: int = 60


def action(G: nx.Graph, p: ActionParams) -> float:
    S = 0.0
    if p.alpha != 0.0:
        S += p.alpha * curvature_sum(G, max_edges=p.curvature_sample_edges)
    if p.beta != 0.0:
        triangles = sum(nx.triangles(G).values()) / 3
        S += -p.beta * triangles
    return S


def double_edge_swap_proposal(G: nx.Graph, rng: random.Random):
    G2 = G.copy()
    edges = list(G2.edges())
    for _ in range(20):
        (a, b), (c, d) = rng.sample(edges, 2)
        if len({a, b, c, d}) < 4:
            continue
        if G2.has_edge(a, d) or G2.has_edge(c, b):
            continue
        G2.remove_edge(a, b)
        G2.remove_edge(c, d)
        G2.add_edge(a, d)
        G2.add_edge(c, b)
        if nx.is_connected(G2):
            return G2
        G2 = G.copy()
    return None


def run_mcmc(N: int, avg_degree: int, p: ActionParams, n_steps: int,
             temperature: float = 1.0, seed: int = RNG_SEED) -> Tuple[nx.Graph, List[float]]:
    rng = random.Random(seed)
    random.seed(seed)
    G = nx.random_regular_graph(avg_degree, N, seed=seed)
    S_current = action(G, p)
    trace = [S_current]
    for _ in range(n_steps):
        G_prop = double_edge_swap_proposal(G, rng)
        if G_prop is None:
            trace.append(S_current)
            continue
        S_prop = action(G_prop, p)
        dS = S_prop - S_current
        if dS <= 0 or rng.random() < math.exp(-dS / max(temperature, 1e-9)):
            G, S_current = G_prop, S_prop
        trace.append(S_current)
    return G, trace


def spectral_dimension(G: nx.Graph, sigmas: List[int] | None = None) -> Dict[int, float]:
    if sigmas is None:
        sigmas = [1, 2, 4, 8, 16, 32]
    A = nx.to_numpy_array(G)
    deg = A.sum(axis=1)
    P = A / deg[:, None]
    rng = random.Random(RNG_SEED)
    sample = rng.sample(list(range(len(G))), min(30, len(G)))
    Pk = np.eye(len(G))
    return_probs = {}
    for step in range(1, max(sigmas) + 1):
        Pk = Pk @ P
        if step in sigmas:
            return_probs[step] = float(np.mean([Pk[i, i] for i in sample]))
    ds = {}
    keys = sorted(return_probs)
    for a, b in zip(keys[:-1], keys[1:]):
        if return_probs[a] > 0 and return_probs[b] > 0:
            ds[b] = -2 * (math.log(return_probs[b]) - math.log(return_probs[a])) / (math.log(b) - math.log(a))
    return ds


def volume_growth_dimension(G: nx.Graph, max_r: int = 6) -> Dict[int, float]:
    rng = random.Random(RNG_SEED)
    sample = rng.sample(list(G.nodes()), min(15, len(G)))
    growth = {r: [] for r in range(1, max_r + 1)}
    for n in sample:
        lengths = nx.single_source_shortest_path_length(G, n, cutoff=max_r)
        for r in range(1, max_r + 1):
            growth[r].append(sum(1 for d in lengths.values() if d <= r))
    avg = {r: np.mean(v) for r, v in growth.items() if v}
    d_H = {}
    rs = sorted(avg)
    for a, b in zip(rs[:-1], rs[1:]):
        if avg[a] > 0 and avg[b] > 0 and b > a:
            d_H[b] = (math.log(avg[b]) - math.log(avg[a])) / (math.log(b) - math.log(a))
    return d_H


def diagnostics(G: nx.Graph) -> Dict:
    degs = [d for _, d in G.degree()]
    N = G.number_of_nodes()
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigvals = np.sort(np.linalg.eigvalsh(L))
    return {
        "N": N,
        "degree_mean": float(np.mean(degs)),
        "degree_var": float(np.var(degs)),
        "avg_shortest_path": nx.average_shortest_path_length(G),
        "log_N": math.log(N),
        "diameter": nx.diameter(G),
        "spectral_gap": float(eigvals[1]),
        "avg_clustering": nx.average_clustering(G),
        "triangle_count": sum(nx.triangles(G).values()) // 3,
        "spectral_dimension": spectral_dimension(G),
        "hausdorff_dimension": volume_growth_dimension(G),
        "curvature_mean_sampled": curvature_sum(G, max_edges=60) / min(60, G.number_of_edges()),
    }


def run_scan(N: int = 200, avg_degree: int = 4, n_steps: int = 400,
             alphas: List[float] | None = None, betas: List[float] | None = None,
             seeds: List[int] | None = None) -> List[Dict]:
    alphas = [0.0, 0.5, 1.0, 2.0] if alphas is None else alphas
    betas = [0.0, 0.5, 1.0, 2.0] if betas is None else betas
    seeds = [2226, 2227, 2228] if seeds is None else seeds
    results = []
    for alpha, beta in itertools.product(alphas, betas):
        for seed in seeds:
            p = ActionParams(alpha=alpha, beta=beta)
            G_final, trace = run_mcmc(N, avg_degree, p, n_steps, seed=seed)
            diag = diagnostics(G_final)
            diag.update({"alpha": alpha, "beta": beta, "seed": seed, "final_action": trace[-1]})
            results.append(diag)
    return results


def pass_fail_verdict(results: List[Dict], expander_log_ratio: float = 1.3) -> Dict:
    by_cell = {}
    for r in results:
        by_cell.setdefault((r["alpha"], r["beta"]), []).append(r)
    candidates = [key for key, runs in by_cell.items()
                  if all(run["avg_shortest_path"] > expander_log_ratio * run["log_N"] for run in runs)]
    broad = len(candidates) >= 3
    return {
        "non_expander_cells": candidates,
        "n_cells_tested": len(by_cell),
        "broad_region_found": broad,
        "verdict": "PASS (candidate broad non-expander phase — proceed to RQO-2)"
        if broad else "FAIL (expander soup persists, or only an isolated point escapes it)",
    }
