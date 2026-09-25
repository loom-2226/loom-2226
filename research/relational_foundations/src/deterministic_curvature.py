from __future__ import annotations

"""Deterministic full-curvature comparator qualification for Relational Foundations.

This module is isolated from the historical RQO-1 reconstruction. It deliberately
uses the recovered curvature helper with max_edges=None so the corrected action is
a deterministic function of graph state rather than a sampled estimator.
"""

import math
import random
from dataclasses import dataclass
from statistics import mean
from typing import Dict, List, Sequence

import networkx as nx
import numpy as np

from .rqo1_reconstruction import curvature_sum, double_edge_swap_proposal


@dataclass(frozen=True)
class DeterministicCurvatureConfig:
    N: int = 40
    avg_degree: int = 4
    seeds: tuple[int, ...] = (2226, 2227, 2228, 2229)
    proposals: int = 200
    burn_in: int = 40
    sample_every: int = 5
    strength: float = 1.0
    temperature: float = 1.0
    rhat_max: float = 1.10
    ess_min: float = 40.0


def full_curvature_action(G: nx.Graph, alpha: float = 1.0) -> float:
    if alpha < 0:
        raise ValueError("alpha must be non-negative; corrected sign is encoded explicitly")
    if alpha == 0.0:
        return 0.0
    return -float(alpha) * float(curvature_sum(G, max_edges=None))


def _graph_metrics(G: nx.Graph) -> Dict[str, float]:
    n = G.number_of_nodes()
    L = nx.normalized_laplacian_matrix(G).toarray()
    eigvals = np.sort(np.linalg.eigvalsh(L))
    avg_path = float(nx.average_shortest_path_length(G))
    return {
        "avg_shortest_path": avg_path,
        "log_N": math.log(n),
        "path_over_logN": avg_path / math.log(n),
        "spectral_gap": float(eigvals[1]),
        "diameter": float(nx.diameter(G)),
        "avg_clustering": float(nx.average_clustering(G)),
        "triangle_count": float(sum(nx.triangles(G).values()) / 3.0),
    }


def _split_rhat(chains: Sequence[Sequence[float]]) -> float | None:
    if len(chains) < 2:
        return None
    min_len = min(len(c) for c in chains)
    half = min_len // 2
    if half < 2:
        return None
    split = []
    for chain in chains:
        vals = np.asarray(chain[: 2 * half], dtype=float)
        split.append(vals[:half])
        split.append(vals[half:])
    arr = np.vstack(split)
    n = arr.shape[1]
    chain_means = arr.mean(axis=1)
    chain_variances = arr.var(axis=1, ddof=1)
    within = float(chain_variances.mean())
    between = float(n * chain_means.var(ddof=1))
    if within == 0.0:
        return 1.0 if between == 0.0 else None
    var_hat = ((n - 1.0) / n) * within + between / n
    return float(math.sqrt(max(var_hat / within, 0.0)))


def _ess(chains: Sequence[Sequence[float]]) -> float | None:
    if not chains:
        return None
    n = min(len(c) for c in chains)
    m = len(chains)
    if n < 4:
        return None
    arr = np.vstack([np.asarray(c[:n], dtype=float) for c in chains])
    centered = arr - arr.mean(axis=1, keepdims=True)
    variances = np.mean(centered * centered, axis=1)
    if np.all(variances == 0.0):
        return float(m * n)

    correlations: List[float] = []
    for lag in range(1, n):
        lag_values: List[float] = []
        for row, variance in zip(centered, variances):
            if variance <= 0.0:
                continue
            lag_values.append(float(np.mean(row[:-lag] * row[lag:]) / variance))
        if not lag_values:
            break
        correlations.append(float(np.mean(lag_values)))

    positive_sum = 0.0
    for i in range(0, len(correlations), 2):
        pair_sum = sum(correlations[i:i + 2])
        if pair_sum <= 0.0:
            break
        positive_sum += pair_sum
    tau = max(1.0, 1.0 + 2.0 * positive_sum)
    return float(min(m * n, (m * n) / tau))


def _run_chain(
    config: DeterministicCurvatureConfig,
    seed: int,
    convention: str,
) -> Dict:
    if convention not in ("null", "deterministic_corrected_curvature"):
        raise ValueError("unsupported convention")

    rng = random.Random(seed)
    G = nx.random_regular_graph(config.avg_degree, config.N, seed=seed)
    alpha = 0.0 if convention == "null" else config.strength
    S_current = full_curvature_action(G, alpha=alpha)
    accepted = 0
    valid = 0
    samples = {"action": [], "path_over_logN": [], "spectral_gap": []}

    for step in range(1, config.proposals + 1):
        G_prop = double_edge_swap_proposal(G, rng)
        if G_prop is not None:
            valid += 1
            S_prop = full_curvature_action(G_prop, alpha=alpha)
            dS = S_prop - S_current
            if dS <= 0.0 or rng.random() < math.exp(-dS / max(config.temperature, 1e-9)):
                G = G_prop
                S_current = S_prop
                accepted += 1

        if step > config.burn_in and (step - config.burn_in) % config.sample_every == 0:
            d = _graph_metrics(G)
            samples["action"].append(float(S_current))
            samples["path_over_logN"].append(float(d["path_over_logN"]))
            samples["spectral_gap"].append(float(d["spectral_gap"]))

    return {
        "seed": seed,
        "convention": convention,
        "accepted_moves": accepted,
        "valid_proposals": valid,
        "acceptance_fraction": accepted / valid if valid else 0.0,
        "samples": samples,
        "final_metrics": _graph_metrics(G),
        "final_action": float(S_current),
        "degree_invariant": all(d == config.avg_degree for _, d in G.degree()),
        "connected_invariant": nx.is_connected(G),
    }


def _mixing_summary(rows: List[Dict], config: DeterministicCurvatureConfig) -> Dict:
    corrected = [
        r for r in rows if r["convention"] == "deterministic_corrected_curvature"
    ]
    observables: Dict[str, Dict] = {}
    passes = True
    for key in ("action", "path_over_logN", "spectral_gap"):
        chains = [r["samples"][key] for r in corrected]
        min_samples = min((len(c) for c in chains), default=0)
        rhat = _split_rhat(chains)
        ess = _ess(chains)
        key_pass = (
            min_samples >= 30
            and rhat is not None
            and rhat <= config.rhat_max
            and ess is not None
            and ess >= config.ess_min
        )
        passes = passes and key_pass
        observables[key] = {
            "min_samples_per_chain": min_samples,
            "split_rhat": rhat,
            "pooled_ess": ess,
            "passes": key_pass,
        }

    valid_ok = all(r["valid_proposals"] > 0 for r in corrected)
    passes = passes and valid_ok
    return {
        "observables": observables,
        "all_chains_have_valid_proposals": valid_ok,
        "passes": passes,
    }


def classify_deterministic_curvature(
    rows: List[Dict],
    config: DeterministicCurvatureConfig,
) -> Dict:
    if not rows:
        raise ValueError("rows must not be empty")
    if not all(r["degree_invariant"] and r["connected_invariant"] for r in rows):
        return {
            "verdict": "IMPLEMENTATION_OR_DETERMINISM_FAILURE",
            "mixing": None,
        }

    mixing = _mixing_summary(rows, config)
    null_rows = [r for r in rows if r["convention"] == "null"]
    corrected_rows = [
        r for r in rows if r["convention"] == "deterministic_corrected_curvature"
    ]
    if not null_rows or not corrected_rows:
        raise ValueError("matched null and corrected rows required")

    def pooled(cell_rows: List[Dict], key: str) -> float:
        return mean(x for r in cell_rows for x in r["samples"][key])

    null_path = pooled(null_rows, "path_over_logN")
    corrected_path = pooled(corrected_rows, "path_over_logN")
    null_gap = pooled(null_rows, "spectral_gap")
    corrected_gap = pooled(corrected_rows, "spectral_gap")
    direction = corrected_path > null_path and corrected_gap < null_gap

    if not mixing["passes"]:
        verdict = "INCONCLUSIVE_MIXING"
    else:
        verdict = (
            "QUALIFIED_DIRECTION_PERSISTS"
            if direction
            else "QUALIFIED_DIRECTION_DOES_NOT_PERSIST"
        )

    return {
        "verdict": verdict,
        "mixing": mixing,
        "directional_comparison": {
            "mean_null_path_over_logN": null_path,
            "mean_corrected_path_over_logN": corrected_path,
            "corrected_minus_null_path_over_logN": corrected_path - null_path,
            "mean_null_spectral_gap": null_gap,
            "mean_corrected_spectral_gap": corrected_gap,
            "corrected_minus_null_spectral_gap": corrected_gap - null_gap,
            "direction_reproduced": direction,
        },
        "equilibrium_phase_claim_authorized": False,
        "stage_a_comparator_authorized": verdict == "QUALIFIED_DIRECTION_PERSISTS",
    }


def determinism_contract(config: DeterministicCurvatureConfig) -> Dict:
    G = nx.random_regular_graph(config.avg_degree, config.N, seed=config.seeds[0])
    random.seed(1)
    action_a = full_curvature_action(G, alpha=config.strength)
    random.seed(999999)
    action_b = full_curvature_action(G, alpha=config.strength)
    expected = -config.strength * curvature_sum(G, max_edges=None)
    tol = 1e-12
    passes = abs(action_a - action_b) <= tol and abs(action_a - expected) <= tol
    return {
        "same_graph_same_action": abs(action_a - action_b) <= tol,
        "independent_of_global_random_state": abs(action_a - action_b) <= tol,
        "matches_full_historical_helper": abs(action_a - expected) <= tol,
        "passes": passes,
        "action_a": float(action_a),
        "action_b": float(action_b),
        "expected": float(expected),
    }


def run_deterministic_curvature(
    config: DeterministicCurvatureConfig = DeterministicCurvatureConfig(),
) -> Dict:
    if config.N <= config.avg_degree or (config.N * config.avg_degree) % 2:
        raise ValueError("invalid random-regular configuration")
    if config.burn_in >= config.proposals:
        raise ValueError("burn_in must be smaller than proposals")
    if config.sample_every <= 0:
        raise ValueError("sample_every must be positive")

    contract = determinism_contract(config)
    if not contract["passes"]:
        return {
            "kind": "deterministic_corrected_curvature_comparator",
            "config": config.__dict__,
            "determinism_contract": contract,
            "results": [],
            "classification": {
                "verdict": "IMPLEMENTATION_OR_DETERMINISM_FAILURE"
            },
        }

    rows: List[Dict] = []
    for convention in ("null", "deterministic_corrected_curvature"):
        for seed in config.seeds:
            rows.append(_run_chain(config, seed, convention))

    return {
        "kind": "deterministic_corrected_curvature_comparator",
        "epistemic_status": "D-PROVISIONAL comparator qualification",
        "config": {
            "N": config.N,
            "avg_degree": config.avg_degree,
            "seeds": list(config.seeds),
            "proposals": config.proposals,
            "burn_in": config.burn_in,
            "sample_every": config.sample_every,
            "strength": config.strength,
            "temperature": config.temperature,
            "rhat_max": config.rhat_max,
            "ess_min": config.ess_min,
            "curvature_action": "-alpha * curvature_sum(G, max_edges=None)",
            "curvature_sampling_in_action": False,
            "matter_terms_added": False,
            "historical_reconstruction_modified": False,
        },
        "determinism_contract": contract,
        "results": rows,
        "classification": classify_deterministic_curvature(rows, config),
    }
