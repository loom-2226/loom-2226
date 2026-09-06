from __future__ import annotations

"""Bounded sign-sensitivity test for the recovered RQO-1 curvature term.

Historical reconstruction remains untouched. This module compares the recovered
+alpha*kappa convention against a clearly labeled experimental -alpha*kappa
variant under otherwise matched smoke-scale conditions.
"""

import math
import random
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List

from .rqo1_reconstruction import curvature_sum, diagnostics, double_edge_swap_proposal
import networkx as nx


@dataclass(frozen=True)
class SignTestConfig:
    N: int = 40
    avg_degree: int = 4
    n_steps: int = 30
    seeds: tuple[int, ...] = (2226, 2227)
    strengths: tuple[float, ...] = (0.5, 1.0)
    curvature_sample_edges: int = 20
    expander_log_ratio: float = 1.3
    temperature: float = 1.0


def signed_curvature_action(G: nx.Graph, alpha: float, sign: int, max_edges: int) -> float:
    if sign not in (-1, 1):
        raise ValueError("sign must be +1 (historical) or -1 (experimental corrected-sign)")
    if alpha == 0.0:
        return 0.0
    return float(sign) * alpha * curvature_sum(G, max_edges=max_edges)


def run_signed_mcmc(
    N: int,
    avg_degree: int,
    alpha: float,
    sign: int,
    n_steps: int,
    curvature_sample_edges: int,
    temperature: float,
    seed: int,
):
    rng = random.Random(seed)
    random.seed(seed)
    G = nx.random_regular_graph(avg_degree, N, seed=seed)
    S_current = signed_curvature_action(G, alpha, sign, curvature_sample_edges)
    trace = [S_current]

    for _ in range(n_steps):
        G_prop = double_edge_swap_proposal(G, rng)
        if G_prop is None:
            trace.append(S_current)
            continue
        S_prop = signed_curvature_action(G_prop, alpha, sign, curvature_sample_edges)
        dS = S_prop - S_current
        if dS <= 0 or rng.random() < math.exp(-dS / max(temperature, 1e-9)):
            G, S_current = G_prop, S_prop
        trace.append(S_current)
    return G, trace


def classify_sign_test(results: List[Dict], threshold: float = 1.3) -> Dict:
    if not results:
        raise ValueError("results must not be empty")

    by_cell: Dict[tuple[str, float], List[Dict]] = {}
    for row in results:
        by_cell.setdefault((str(row["convention"]), float(row["strength"])), []).append(row)

    summaries = []
    for (convention, strength), rows in sorted(by_cell.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        ratios = [float(r["path_over_logN"]) for r in rows]
        gaps = [float(r["spectral_gap"]) for r in rows]
        curv = [float(r["curvature_mean_sampled_historical_field"]) for r in rows]
        summaries.append({
            "convention": convention,
            "strength": strength,
            "n_runs": len(rows),
            "mean_path_over_logN": mean(ratios),
            "mean_spectral_gap": mean(gaps),
            "mean_historical_curvature_field": mean(curv),
            "all_seeds_cross_historical_nonexpander_gate": all(r > threshold for r in ratios),
        })

    index = {(s["convention"], s["strength"]): s for s in summaries}
    matched = []
    corrected_candidates = []
    strengths = sorted({s for c, s in by_cell if c != "null"})
    for strength in strengths:
        hist = index.get(("historical_plus", strength))
        corr = index.get(("experimental_minus", strength))
        if not hist or not corr:
            continue
        row = {
            "strength": strength,
            "corrected_minus_historical_path_ratio": (
                corr["mean_path_over_logN"] - hist["mean_path_over_logN"]
            ),
            "corrected_minus_historical_spectral_gap": (
                corr["mean_spectral_gap"] - hist["mean_spectral_gap"]
            ),
            "corrected_has_longer_paths_and_smaller_gap": (
                corr["mean_path_over_logN"] > hist["mean_path_over_logN"]
                and corr["mean_spectral_gap"] < hist["mean_spectral_gap"]
            ),
            "corrected_crosses_gate_all_seeds": corr["all_seeds_cross_historical_nonexpander_gate"],
        }
        matched.append(row)
        if row["corrected_crosses_gate_all_seeds"]:
            corrected_candidates.append({"strength": strength})

    return {
        "threshold_path_over_logN": threshold,
        "cell_summaries": summaries,
        "matched_sign_comparisons": matched,
        "corrected_sign_provisional_candidates": corrected_candidates,
        "category": "CORRECTED-SIGN CANDIDATE" if corrected_candidates else "NO CORRECTED-SIGN GATE CROSSING",
        "scientific_scope": (
            "Sign-sensitivity experiment only. Historical implementation is unchanged; "
            "no RQO-1 verdict and no claim of emergent geometry."
        ),
    }


def run_sign_test(config: SignTestConfig = SignTestConfig()) -> Dict:
    if config.N <= config.avg_degree or (config.N * config.avg_degree) % 2:
        raise ValueError(f"invalid random-regular configuration N={config.N}, degree={config.avg_degree}")

    results: List[Dict] = []
    cells = [{"convention": "null", "strength": 0.0, "alpha": 0.0, "sign": 1}]
    for strength in config.strengths:
        cells.extend([
            {"convention": "historical_plus", "strength": strength, "alpha": strength, "sign": 1},
            {"convention": "experimental_minus", "strength": strength, "alpha": strength, "sign": -1},
        ])

    for cell in cells:
        for seed in config.seeds:
            graph, trace = run_signed_mcmc(
                N=config.N,
                avg_degree=config.avg_degree,
                alpha=float(cell["alpha"]),
                sign=int(cell["sign"]),
                n_steps=config.n_steps,
                curvature_sample_edges=config.curvature_sample_edges,
                temperature=config.temperature,
                seed=seed,
            )
            d = diagnostics(graph)
            results.append({
                "convention": cell["convention"],
                "strength": cell["strength"],
                "alpha": cell["alpha"],
                "curvature_action_sign": cell["sign"],
                "seed": seed,
                "N": config.N,
                "n_steps": config.n_steps,
                "curvature_sample_edges_in_action": config.curvature_sample_edges,
                "avg_shortest_path": d["avg_shortest_path"],
                "log_N": d["log_N"],
                "path_over_logN": d["avg_shortest_path"] / d["log_N"],
                "diameter": d["diameter"],
                "spectral_gap": d["spectral_gap"],
                "avg_clustering": d["avg_clustering"],
                "triangle_count": d["triangle_count"],
                "curvature_mean_sampled_historical_field": d["curvature_mean_sampled"],
                "final_action": trace[-1],
            })

    return {
        "kind": "rqo1_curvature_sign_sensitivity",
        "config": {
            "N": config.N,
            "avg_degree": config.avg_degree,
            "n_steps": config.n_steps,
            "seeds": list(config.seeds),
            "strengths": list(config.strengths),
            "curvature_sample_edges_in_action": config.curvature_sample_edges,
            "expander_log_ratio": config.expander_log_ratio,
            "historical_action": "+alpha * curvature_sum",
            "experimental_action": "-alpha * curvature_sum",
        },
        "cells": cells,
        "results": results,
        "classification": classify_sign_test(results, config.expander_log_ratio),
    }
