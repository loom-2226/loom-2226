from __future__ import annotations

"""R3 — increasing-N reproduction of the AUIF null / expander baseline.

This experiment intentionally uses alpha=0 and beta=0. It asks only whether the
coordinate-free finite-degree null ensemble remains expander-like as N increases.
It does not test a locality-generating action and cannot produce an RQO-1 PASS.
"""

import math
from dataclasses import dataclass
from statistics import mean
from typing import Dict, Iterable, List

from .rqo1_reconstruction import ActionParams, diagnostics, run_mcmc


@dataclass(frozen=True)
class R3Config:
    sizes: tuple[int, ...] = (40, 80, 160)
    seeds: tuple[int, ...] = (2226, 2227, 2228)
    avg_degree: int = 4
    steps_per_node: int = 5
    expander_log_ratio: float = 1.3


def classify_null_scaling(results: List[Dict], threshold: float = 1.3) -> Dict:
    if not results:
        raise ValueError("results must not be empty")

    by_n: Dict[int, List[Dict]] = {}
    for row in results:
        by_n.setdefault(int(row["N"]), []).append(row)

    size_summary = []
    for n in sorted(by_n):
        rows = by_n[n]
        ratios = [float(r["avg_shortest_path"]) / float(r["log_N"]) for r in rows]
        gaps = [float(r["spectral_gap"]) for r in rows]
        size_summary.append({
            "N": n,
            "n_runs": len(rows),
            "mean_path_over_logN": mean(ratios),
            "max_path_over_logN": max(ratios),
            "mean_spectral_gap": mean(gaps),
            "all_runs_below_nonexpander_gate": all(x <= threshold for x in ratios),
        })

    all_below = all(item["all_runs_below_nonexpander_gate"] for item in size_summary)
    return {
        "threshold_path_over_logN": threshold,
        "sizes": size_summary,
        "all_sizes_expander_like_by_historical_gate": all_below,
        "interpretation": (
            "AUIF NULL FAILURE REPRODUCED: null ensemble remains expander-like across tested sizes."
            if all_below
            else "AUIF NULL FAILURE NOT CLEANLY REPRODUCED: at least one run crosses the historical non-expander gate."
        ),
        "scientific_scope": "R3 null reproduction only; this is not an RQO-1 verdict.",
    }


def run_r3(config: R3Config = R3Config()) -> Dict:
    results: List[Dict] = []
    p = ActionParams(alpha=0.0, beta=0.0)

    for n in config.sizes:
        if n <= config.avg_degree or (n * config.avg_degree) % 2:
            raise ValueError(f"invalid random-regular configuration N={n}, degree={config.avg_degree}")
        steps = n * config.steps_per_node
        for seed in config.seeds:
            graph, trace = run_mcmc(
                N=n,
                avg_degree=config.avg_degree,
                p=p,
                n_steps=steps,
                seed=seed,
            )
            d = diagnostics(graph)
            results.append({
                "N": n,
                "degree_mean": d["degree_mean"],
                "degree_var": d["degree_var"],
                "avg_shortest_path": d["avg_shortest_path"],
                "log_N": d["log_N"],
                "path_over_logN": d["avg_shortest_path"] / d["log_N"],
                "diameter": d["diameter"],
                "spectral_gap": d["spectral_gap"],
                "avg_clustering": d["avg_clustering"],
                "triangle_count": d["triangle_count"],
                "seed": seed,
                "n_steps": steps,
                "alpha": 0.0,
                "beta": 0.0,
                "final_action": trace[-1],
            })

    return {
        "kind": "r3_auif_null_increasing_n",
        "config": {
            "sizes": list(config.sizes),
            "seeds": list(config.seeds),
            "avg_degree": config.avg_degree,
            "steps_per_node": config.steps_per_node,
            "alpha": 0.0,
            "beta": 0.0,
            "expander_log_ratio": config.expander_log_ratio,
        },
        "results": results,
        "classification": classify_null_scaling(results, config.expander_log_ratio),
    }
