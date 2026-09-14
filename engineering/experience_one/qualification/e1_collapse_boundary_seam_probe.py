#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 diagnostic: locate Navigator's collapse-boundary solver seam.

This probe does not change collapse physics. It loads the governed Navigator core,
inspects the actual `_solve_leg` implementation and directly referenced local
helpers, and reports only source excerpts relevant to metric/collapse/boundary/
terminal-burn geometry. The goal is to identify the smallest internal seam where a
candidate forced collapse radius experiment can be implemented without inventing a
parallel flight solver.
"""

import inspect
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import loom_navigator_core as campaign

RELEVANT_TERMS = (
    "collapse",
    "metric",
    "distance",
    "range",
    "arrival",
    "terminal",
    "burn",
    "position",
    "velocity",
    "interpol",
    "state",
    "epoch",
    "beta",
    "ramp",
    "root",
)


def extract_relevant_source_lines(source: str, context: int = 1) -> list[str]:
    lines = source.splitlines()
    keep: set[int] = set()
    for i, line in enumerate(lines):
        low = line.lower()
        if any(term in low for term in RELEVANT_TERMS):
            for j in range(max(0, i - context), min(len(lines), i + context + 1)):
                keep.add(j)
    return [f"{i + 1:04d}: {lines[i]}" for i in sorted(keep)]


def referenced_local_helpers(fn: Any, namespace: dict[str, Any]) -> list[str]:
    names = getattr(getattr(fn, "__code__", None), "co_names", ())
    out: list[str] = []
    for name in names:
        value = namespace.get(name)
        if callable(value) and getattr(value, "__module__", None) == getattr(fn, "__module__", None):
            out.append(name)
    return sorted(set(out))


def _describe_callable(fn: Any) -> dict[str, Any]:
    try:
        source = inspect.getsource(fn)
        source_error = None
    except Exception as exc:  # diagnostic only
        source = ""
        source_error = f"{type(exc).__name__}: {exc}"
    try:
        signature = str(inspect.signature(fn))
    except Exception as exc:  # diagnostic only
        signature = f"UNAVAILABLE: {type(exc).__name__}: {exc}"
    return {
        "name": getattr(fn, "__name__", "UNKNOWN"),
        "signature": signature,
        "source_file": inspect.getsourcefile(fn),
        "first_line": getattr(getattr(fn, "__code__", None), "co_firstlineno", None),
        "co_names": list(getattr(getattr(fn, "__code__", None), "co_names", ())),
        "relevant_source_lines": extract_relevant_source_lines(source),
        "source_error": source_error,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-e1-collapse-seam-") as td:
        nav = campaign._load_core(Path(td) / "core")
        solve = getattr(nav, "_solve_leg", None)
        if solve is None or not callable(solve):
            raise RuntimeError("Navigator core does not expose callable _solve_leg")

        namespace = vars(nav)
        helper_names = referenced_local_helpers(solve, namespace)
        helpers = []
        for name in helper_names:
            fn = namespace[name]
            desc = _describe_callable(fn)
            if desc["relevant_source_lines"]:
                helpers.append(desc)

        solve_desc = _describe_callable(solve)
        result = {
            "schema": "LOOM_E1_COLLAPSE_BOUNDARY_SEAM_PROBE_V1",
            "status": "PASS",
            "solver_model_expected": "NAV-V1-A",
            "solve_leg": solve_desc,
            "referenced_local_helpers": helpers,
            "candidate_helper_names": [h["name"] for h in helpers],
            "next_action": "IMPLEMENT_FORCED_COLLAPSE_RADIUS_EXPERIMENT_AT_IDENTIFIED_NAVIGATOR_SEAM",
            "authority_note": "READ_ONLY_SOURCE_INTROSPECTION_NO_PHYSICS_CHANGE_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
