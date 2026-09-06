from __future__ import annotations

"""Bounded longer-chain check for the corrected-curvature RQO-1 follow-up.

This module intentionally preserves the sampled-curvature action behavior used by
previous corrected-sign experiments. It therefore measures trajectory stability,
not rigorous equilibrium of a deterministic Boltzmann target.
"""

import math
import random
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, List

import networkx as nx
import numpy as np

from .rqo1_reconstruction import double_edge_swap_proposal
from .sign_sensitivity import signed_curvature_action


@dataclass(frozen=True)
class CurvatureConvergenceConfig:
    N: int = 80
    avg_degree: int = 4
    seeds: tuple[int, ...] = (2226, 2227, 2228)
    checkpoints: tuple[int, ...] = (160, 400, 800)
    strength: float = 1.0
    curvature_sample_edges: int = 20
    temperature: float = 1.0
    expander_log_ratio: float = 1.3


def _graph_metrics(G: nx.Graph) -> Dict[str, float]:
    n = G.number_of_nodes()
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigvals = np.sort(np.linalg.eigvalsh(L))
    avg_path = float(nx.average_shortest_path_length(G))
    return {
        "avg_shortest_path": avg_path,
        "log_N": math.log(n),
        "path_over_logN": avg_path / math.log(n),
        "diameter": float(nx.diameter(G)),
        "spectral_gap": float(eigvals[1]),
        "avg_clustering": float(nx.average_clustering(G)),
        "triangle_count": float(sum(nx.triangles(G).values()) / 3.0),
    }


def _lag1_autocorrelation(values: List[float]) -> float | None:
    if len(values) < 3:
        return None
    x = np.asarray(values[:-1], dtype=float)
    y = np.asarray(values[1:], dtype=float)
    if float(np.std(x)) == 0.0 or float(np.std(y)) == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def _run_checkpoint_chain(
    *,
    config: CurvatureConvergenceConfig,
    seed: int,
    convention: str,
) -> List[Dict]:
    if convention not in ("null", "experimental_minus"):
        raise ValueError("convention must be 'null' or 'experimental_minus'")

    rng = random.Random(seed)
    random.seed(seed)
    G = nx.random_regular_graph(config.avg_degree, config.N, seed=seed)

    alpha = 0.0 if convention == "null" else config.strength
    sign = -1 if convention == "experimental_minus" else 1
    S_current = signed_curvature_action(
        G,
        alpha=alpha,
        sign=sign,
        max_edges=config.curvature_sample_edges,
    )

    max_steps = max(config.checkpoints)
    checkpoints = set(config.checkpoints)
    snapshots: Dict[int, nx.Graph] = {}
    checkpoint_state: Dict[int, Dict] = {}
    action_trace: List[float] = [S_current]
    accepted = 0
    valid_proposals = 0

    for step in range(1, max_steps + 1):
        G_prop = double_edge_swap_proposal(G, rng)
        if G_prop is not None:
            valid_proposals += 1
            S_prop = signed_curvature_action(
                G_prop,
                alpha=alpha,
                sign=sign,
                max_edges=config.curvature_sample_edges,
            )
            dS = S_prop - S_current
            if dS <= 0.0 or rng.random() < math.exp(-dS / max(config.temperature, 1e-9)):
                G = G_prop
                S_current = S_prop
                accepted += 1
        action_trace.append(S_current)

        if step in checkpoints:
            snapshots[step] = G.copy()
            checkpoint_state[step] = {
                "accepted_moves": accepted,
                "valid_proposals": valid_proposals,
                "acceptance_fraction": (
                    accepted / valid_proposals if valid_proposals else 0.0
                ),
                "sampled_current_action": float(S_current),
            }

    # Diagnostics are deliberately evaluated only after the full chain finishes,
    # so they cannot consume RNG state and alter later proposals/acceptance.
    rows: List[Dict] = []
    previous = 0
    for checkpoint in config.checkpoints:
        segment = action_trace[previous + 1: checkpoint + 1]
        if not segment:
            segment = [action_trace[checkpoint]]
        metrics = _graph_metrics(snapshots[checkpoint])
        state = checkpoint_state[checkpoint]
        rows.append({
            "N": config.N,
            "degree": config.avg_degree,
            "seed": seed,
            "convention": convention,
            "alpha": alpha,
            "curvature_action_sign": sign,
            "checkpoint_steps": checkpoint,
            "checkpoint_steps_per_node": checkpoint / config.N,
            **metrics,
            **state,
            "interval_action_mean": float(mean(segment)),
            "interval_action_std": float(pstdev(segment)) if len(segment) > 1 else 0.0,
            "interval_action_lag1_autocorrelation": _lag1_autocorrelation(segment),
            "crosses_historical_path_gate": metrics["path_over_logN"] > config.expander_log_ratio,
        })
        previous = checkpoint
    return rows


def classify_curvature_convergence(results: List[Dict]) -> Dict:
    if not results:
        raise ValueError("results must not be empty")

    checkpoints = sorted({int(r["checkpoint_steps"]) for r in results})
    comparisons: List[Dict] = []
    for checkpoint in checkpoints:
        null_rows = [
            r for r in results
            if int(r["checkpoint_steps"]) == checkpoint and r["convention"] == "null"
        ]
        corrected_rows = [
            r for r in results
            if int(r["checkpoint_steps"]) == checkpoint
            and r["convention"] == "experimental_minus"
        ]
        if not null_rows or not corrected_rows:
            raise ValueError(f"missing matched rows at checkpoint {checkpoint}")

        null_path = mean(float(r["path_over_logN"]) for r in null_rows)
        corr_path = mean(float(r["path_over_logN"]) for r in corrected_rows)
        null_gap = mean(float(r["spectral_gap"]) for r in null_rows)
        corr_gap = mean(float(r["spectral_gap"]) for r in corrected_rows)
        directional = corr_path > null_path and corr_gap < null_gap
        comparisons.append({
            "checkpoint_steps": checkpoint,
            "mean_null_path_over_logN": null_path,
            "mean_corrected_path_over_logN": corr_path,
            "corrected_minus_null_path_over_logN": corr_path - null_path,
            "mean_null_spectral_gap": null_gap,
            "mean_corrected_spectral_gap": corr_gap,
            "corrected_minus_null_spectral_gap": corr_gap - null_gap,
            "directionally_locality_like_vs_null": directional,
            "all_corrected_seeds_cross_historical_gate": all(
                bool(r["crosses_historical_path_gate"]) for r in corrected_rows
            ),
            "mean_corrected_acceptance_fraction": mean(
                float(r["acceptance_fraction"]) for r in corrected_rows
            ),
        })

    persists = all(c["directionally_locality_like_vs_null"] for c in comparisons)
    return {
        "checkpoint_comparisons": comparisons,
        "directional_effect_persists_all_checkpoints": persists,
        "category": (
            "DIRECTIONAL EFFECT PERSISTS THROUGH 10N"
            if persists
            else "DIRECTIONAL EFFECT NOT STABLE"
        ),
        "sampled_action_is_stochastic": True,
        "equilibrium_claim_authorized": False,
        "interpretation": (
            "This is a longer-trajectory stability check under the same sampled-curvature "
            "implementation used by the corrected-sign program. Persistence does not establish "
            "equilibrium because the sampled action is not a deterministic function of graph state."
        ),
    }


def run_curvature_convergence(
    config: CurvatureConvergenceConfig = CurvatureConvergenceConfig(),
) -> Dict:
    if config.N <= config.avg_degree or (config.N * config.avg_degree) % 2:
        raise ValueError(
            f"invalid random-regular configuration N={config.N}, degree={config.avg_degree}"
        )
    if tuple(sorted(config.checkpoints)) != config.checkpoints:
        raise ValueError("checkpoints must be strictly increasing")
    if config.checkpoints[0] <= 0:
        raise ValueError("checkpoints must be positive")

    results: List[Dict] = []
    for convention in ("null", "experimental_minus"):
        for seed in config.seeds:
            results.extend(
                _run_checkpoint_chain(config=config, seed=seed, convention=convention)
            )

    return {
        "kind": "rqo1_corrected_curvature_convergence",
        "config": {
            "N": config.N,
            "avg_degree": config.avg_degree,
            "seeds": list(config.seeds),
            "checkpoints": list(config.checkpoints),
            "strength": config.strength,
            "curvature_sample_edges_in_action": config.curvature_sample_edges,
            "temperature": config.temperature,
            "historical_reference_gate_path_over_logN": config.expander_log_ratio,
            "cells": ["null", "experimental_minus"],
            "experimental_action": "-alpha * curvature_sum",
            "new_action_terms_added": False,
            "historical_reconstruction_modified": False,
            "checkpoint_diagnostics_during_chain": False,
        },
        "results": results,
        "classification": classify_curvature_convergence(results),
    }
