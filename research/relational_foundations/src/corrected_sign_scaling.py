from __future__ import annotations

"""Bounded scaling follow-up for the corrected RQO-1 curvature sign.

This module does not modify the historical reconstruction. It compares the null,
recovered historical +alpha curvature sign, and experimental -alpha curvature
sign at N=40 and N=80 with longer chains and three seeds.
"""

from dataclasses import dataclass
from statistics import mean
from typing import Dict, List

from .rqo1_reconstruction import diagnostics
from .sign_sensitivity import run_signed_mcmc


@dataclass(frozen=True)
class CorrectedSignScalingConfig:
    sizes: tuple[int, ...] = (40, 80)
    seeds: tuple[int, ...] = (2226, 2227, 2228)
    avg_degree: int = 4
    steps_per_node: int = 2
    strength: float = 1.0
    curvature_sample_edges: int = 20
    expander_log_ratio: float = 1.3
    temperature: float = 1.0


def classify_corrected_sign_scaling(results: List[Dict], threshold: float = 1.3) -> Dict:
    if not results:
        raise ValueError("results must not be empty")

    by_cell: Dict[tuple[int, str], List[Dict]] = {}
    for row in results:
        by_cell.setdefault((int(row["N"]), str(row["convention"])), []).append(row)

    summaries: List[Dict] = []
    for (n, convention), rows in sorted(by_cell.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        ratios = [float(r["path_over_logN"]) for r in rows]
        gaps = [float(r["spectral_gap"]) for r in rows]
        summaries.append({
            "N": n,
            "convention": convention,
            "n_runs": len(rows),
            "mean_path_over_logN": mean(ratios),
            "mean_spectral_gap": mean(gaps),
            "mean_diameter": mean(float(r["diameter"]) for r in rows),
            "mean_triangle_count": mean(float(r["triangle_count"]) for r in rows),
            "all_seeds_cross_historical_nonexpander_gate": all(x > threshold for x in ratios),
        })

    index = {(int(s["N"]), str(s["convention"])): s for s in summaries}
    size_comparisons: List[Dict] = []
    for n in sorted({int(r["N"]) for r in results}):
        null = index.get((n, "null"))
        hist = index.get((n, "historical_plus"))
        corr = index.get((n, "experimental_minus"))
        if not null or not hist or not corr:
            raise ValueError(f"missing matched cell at N={n}")
        size_comparisons.append({
            "N": n,
            "corrected_minus_historical_path_ratio": (
                corr["mean_path_over_logN"] - hist["mean_path_over_logN"]
            ),
            "corrected_minus_historical_spectral_gap": (
                corr["mean_spectral_gap"] - hist["mean_spectral_gap"]
            ),
            "corrected_has_longer_paths_and_smaller_gap_than_historical": (
                corr["mean_path_over_logN"] > hist["mean_path_over_logN"]
                and corr["mean_spectral_gap"] < hist["mean_spectral_gap"]
            ),
            "corrected_minus_null_path_ratio": (
                corr["mean_path_over_logN"] - null["mean_path_over_logN"]
            ),
            "corrected_minus_null_spectral_gap": (
                corr["mean_spectral_gap"] - null["mean_spectral_gap"]
            ),
            "corrected_has_longer_paths_and_smaller_gap_than_null": (
                corr["mean_path_over_logN"] > null["mean_path_over_logN"]
                and corr["mean_spectral_gap"] < null["mean_spectral_gap"]
            ),
            "corrected_crosses_gate_all_seeds": corr["all_seeds_cross_historical_nonexpander_gate"],
        })

    sign_persists = all(
        row["corrected_has_longer_paths_and_smaller_gap_than_historical"]
        for row in size_comparisons
    )
    beats_null = all(
        row["corrected_has_longer_paths_and_smaller_gap_than_null"]
        for row in size_comparisons
    )
    gate_all = all(row["corrected_crosses_gate_all_seeds"] for row in size_comparisons)

    return {
        "threshold_path_over_logN": threshold,
        "cell_summaries": summaries,
        "size_comparisons": size_comparisons,
        "sign_direction_persists_all_sizes": sign_persists,
        "corrected_beats_null_directionally_all_sizes": beats_null,
        "corrected_crosses_gate_all_sizes_all_seeds": gate_all,
        "category": (
            "PROVISIONAL NON-EXPANDER CANDIDATE"
            if gate_all
            else "NO CORRECTED-SIGN GATE CROSSING"
        ),
        "interpretation": (
            "Corrected-sign scaling follow-up only. Persistence versus the historical sign tests the sign effect; "
            "performance versus the null tests whether the corrected sign itself generates a locality-like movement. "
            "No result here is an RQO-1 PASS or evidence of emergent geometry."
        ),
    }


def run_corrected_sign_scaling(
    config: CorrectedSignScalingConfig = CorrectedSignScalingConfig(),
) -> Dict:
    results: List[Dict] = []
    cells = (
        {"convention": "null", "alpha": 0.0, "sign": 1},
        {"convention": "historical_plus", "alpha": config.strength, "sign": 1},
        {"convention": "experimental_minus", "alpha": config.strength, "sign": -1},
    )

    for n in config.sizes:
        if n <= config.avg_degree or (n * config.avg_degree) % 2:
            raise ValueError(f"invalid random-regular configuration N={n}, degree={config.avg_degree}")
        steps = n * config.steps_per_node
        for cell in cells:
            for seed in config.seeds:
                graph, trace = run_signed_mcmc(
                    N=n,
                    avg_degree=config.avg_degree,
                    alpha=float(cell["alpha"]),
                    sign=int(cell["sign"]),
                    n_steps=steps,
                    curvature_sample_edges=config.curvature_sample_edges,
                    temperature=config.temperature,
                    seed=seed,
                )
                d = diagnostics(graph)
                results.append({
                    "N": n,
                    "convention": cell["convention"],
                    "alpha": cell["alpha"],
                    "curvature_action_sign": cell["sign"],
                    "seed": seed,
                    "n_steps": steps,
                    "degree_mean": d["degree_mean"],
                    "degree_var": d["degree_var"],
                    "avg_shortest_path": d["avg_shortest_path"],
                    "log_N": d["log_N"],
                    "path_over_logN": d["avg_shortest_path"] / d["log_N"],
                    "diameter": d["diameter"],
                    "spectral_gap": d["spectral_gap"],
                    "avg_clustering": d["avg_clustering"],
                    "triangle_count": d["triangle_count"],
                    "curvature_sample_edges_in_action": config.curvature_sample_edges,
                    "final_action": trace[-1],
                })

    return {
        "kind": "rqo1_corrected_sign_scaling",
        "config": {
            "sizes": list(config.sizes),
            "seeds": list(config.seeds),
            "avg_degree": config.avg_degree,
            "steps_per_node": config.steps_per_node,
            "strength": config.strength,
            "curvature_sample_edges_in_action": config.curvature_sample_edges,
            "expander_log_ratio": config.expander_log_ratio,
            "historical_action": "+alpha * curvature_sum",
            "experimental_action": "-alpha * curvature_sum",
            "new_action_terms_added": False,
        },
        "results": results,
        "classification": classify_corrected_sign_scaling(results, config.expander_log_ratio),
    }
