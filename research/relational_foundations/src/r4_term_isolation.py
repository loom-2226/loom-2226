from __future__ import annotations

"""R4 — isolate the recovered curvature and triangle action terms.

This is a smoke-scale attribution experiment. It does not declare an RQO-1 PASS.
"""

from dataclasses import dataclass
from statistics import mean
from typing import Dict, List

from .rqo1_reconstruction import ActionParams, diagnostics, run_mcmc


@dataclass(frozen=True)
class R4Config:
    N: int = 40
    avg_degree: int = 4
    n_steps: int = 30
    seeds: tuple[int, ...] = (2226, 2227)
    strengths: tuple[float, ...] = (0.5, 1.0)
    curvature_sample_edges: int = 20
    expander_log_ratio: float = 1.3


def action_cells(config: R4Config) -> List[Dict]:
    cells: List[Dict] = [{"family": "null", "strength": 0.0, "alpha": 0.0, "beta": 0.0}]
    for s in config.strengths:
        cells.extend([
            {"family": "curvature_only", "strength": s, "alpha": s, "beta": 0.0},
            {"family": "triangle_only", "strength": s, "alpha": 0.0, "beta": s},
            {"family": "combined", "strength": s, "alpha": s, "beta": s},
        ])
    return cells


def classify_term_isolation(results: List[Dict], threshold: float = 1.3) -> Dict:
    if not results:
        raise ValueError("results must not be empty")

    by_cell: Dict[tuple[str, float], List[Dict]] = {}
    for row in results:
        key = (str(row["family"]), float(row["strength"]))
        by_cell.setdefault(key, []).append(row)

    null_rows = by_cell.get(("null", 0.0))
    if not null_rows:
        raise ValueError("null cell is required")
    null_mean_ratio = mean(float(r["path_over_logN"]) for r in null_rows)
    null_mean_gap = mean(float(r["spectral_gap"]) for r in null_rows)

    summaries = []
    candidate_cells = []
    for (family, strength), rows in sorted(by_cell.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        ratios = [float(r["path_over_logN"]) for r in rows]
        gaps = [float(r["spectral_gap"]) for r in rows]
        triangles = [float(r["triangle_count"]) for r in rows]
        curvatures = [float(r["curvature_mean_sampled"]) for r in rows]
        all_cross = all(x > threshold for x in ratios)
        item = {
            "family": family,
            "strength": strength,
            "n_runs": len(rows),
            "mean_path_over_logN": mean(ratios),
            "delta_path_over_logN_vs_null": mean(ratios) - null_mean_ratio,
            "mean_spectral_gap": mean(gaps),
            "delta_spectral_gap_vs_null": mean(gaps) - null_mean_gap,
            "mean_triangle_count": mean(triangles),
            "mean_curvature_sampled": mean(curvatures),
            "all_seeds_cross_historical_nonexpander_gate": all_cross,
        }
        summaries.append(item)
        if family != "null" and all_cross:
            candidate_cells.append({"family": family, "strength": strength})

    summary_index = {(s["family"], s["strength"]): s for s in summaries}
    matched_ablation = []
    strengths = sorted({strength for family, strength in by_cell if family == "combined"})
    for strength in strengths:
        combined = summary_index.get(("combined", strength))
        curvature = summary_index.get(("curvature_only", strength))
        triangle = summary_index.get(("triangle_only", strength))
        if not (combined and curvature and triangle):
            continue
        matched_ablation.append({
            "strength": strength,
            "combined_minus_curvature_path_ratio": (
                combined["mean_path_over_logN"] - curvature["mean_path_over_logN"]
            ),
            "combined_minus_triangle_path_ratio": (
                combined["mean_path_over_logN"] - triangle["mean_path_over_logN"]
            ),
            "combined_exceeds_both_components_on_path_ratio": (
                combined["mean_path_over_logN"] > curvature["mean_path_over_logN"]
                and combined["mean_path_over_logN"] > triangle["mean_path_over_logN"]
            ),
        })

    if candidate_cells:
        category = "PROVISIONAL CANDIDATE"
        interpretation = (
            "At least one recovered action cell crosses the historical path gate across all R4 seeds. "
            "Freeze that cell and test it at R5; this is not an RQO-1 PASS."
        )
    else:
        category = "NO GATE CROSSING"
        interpretation = (
            "No recovered action cell crosses the historical non-expander path gate across all R4 seeds. "
            "Reported deltas are descriptive only at this smoke scale and must not be treated as a demonstrated term effect."
        )

    return {
        "threshold_path_over_logN": threshold,
        "null_mean_path_over_logN": null_mean_ratio,
        "null_mean_spectral_gap": null_mean_gap,
        "cell_summaries": summaries,
        "matched_ablation": matched_ablation,
        "provisional_candidate_cells": candidate_cells,
        "category": category,
        "interpretation": interpretation,
        "scientific_scope": "R4 smoke-scale term isolation only; no RQO-1 verdict.",
    }


def run_r4(config: R4Config = R4Config()) -> Dict:
    if config.N <= config.avg_degree or (config.N * config.avg_degree) % 2:
        raise ValueError(f"invalid random-regular configuration N={config.N}, degree={config.avg_degree}")

    results: List[Dict] = []
    cells = action_cells(config)

    for cell in cells:
        p = ActionParams(
            alpha=float(cell["alpha"]),
            beta=float(cell["beta"]),
            curvature_sample_edges=config.curvature_sample_edges,
        )
        for seed in config.seeds:
            graph, trace = run_mcmc(
                N=config.N,
                avg_degree=config.avg_degree,
                p=p,
                n_steps=config.n_steps,
                seed=seed,
            )
            d = diagnostics(graph)
            results.append({
                "family": cell["family"],
                "strength": cell["strength"],
                "alpha": cell["alpha"],
                "beta": cell["beta"],
                "seed": seed,
                "N": config.N,
                "n_steps": config.n_steps,
                "curvature_sample_edges_in_action": config.curvature_sample_edges,
                "degree_mean": d["degree_mean"],
                "degree_var": d["degree_var"],
                "avg_shortest_path": d["avg_shortest_path"],
                "log_N": d["log_N"],
                "path_over_logN": d["avg_shortest_path"] / d["log_N"],
                "diameter": d["diameter"],
                "spectral_gap": d["spectral_gap"],
                "avg_clustering": d["avg_clustering"],
                "triangle_count": d["triangle_count"],
                "curvature_mean_sampled": d["curvature_mean_sampled"],
                "final_action": trace[-1],
            })

    return {
        "kind": "r4_recovered_term_isolation",
        "config": {
            "N": config.N,
            "avg_degree": config.avg_degree,
            "n_steps": config.n_steps,
            "seeds": list(config.seeds),
            "strengths": list(config.strengths),
            "curvature_sample_edges_in_action": config.curvature_sample_edges,
            "expander_log_ratio": config.expander_log_ratio,
            "historical_exact_parameter_reproduction": False,
        },
        "cells": cells,
        "results": results,
        "classification": classify_term_isolation(results, config.expander_log_ratio),
    }
