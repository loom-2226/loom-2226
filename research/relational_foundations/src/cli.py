from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

LANE = Path(__file__).resolve().parents[1]
REPO = LANE.parents[1]
DEFAULT_OUTPUT = Path(
    os.environ.get(
        "LOOM_RF_OUTPUT",
        "/storage/emulated/0/Documents/LOOM_RESEARCH/relational_foundations"
        if "com.termux" in os.environ.get("PREFIX", "")
        else str(Path.home() / "Documents" / "LOOM_RESEARCH" / "relational_foundations"),
    )
)
REQUIRED = [
    LANE / "README.md",
    LANE / "HISTORICAL_RECONSTRUCTION_v0.1.md",
    LANE / "RQO1_RECOVERY_PROTOCOL_v0.1.md",
    LANE / "RQO1_HISTORICAL_SOURCE_NOTE_v0.1.md",
    LANE / "TERMUX_DEVOPS_WORKFLOW_v0.1.md",
]
FORBIDDEN_IMPORT_PREFIXES = ("src", "deploy", "web", "geometry", "engineering")
RQO1_DEPS = ("networkx", "numpy", "scipy")


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "UNKNOWN"


def status() -> int:
    payload = {
        "lane": "relational_foundations",
        "status": "NON-CANON / NON-RUNTIME",
        "repo": str(REPO),
        "git_sha": git_sha(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "output_root": str(DEFAULT_OUTPUT),
    }
    print(json.dumps(payload, indent=2))
    return 0


def dependency_status() -> int:
    found = {name: importlib.util.find_spec(name) is not None for name in RQO1_DEPS}
    payload = {
        "kind": "rqo1_dependency_status",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "dependencies": found,
        "requirements": str((LANE / "requirements-rqo1.txt").relative_to(REPO)),
        "ready": all(found.values()),
    }
    print(json.dumps(payload, indent=2))
    return 0 if payload["ready"] else 2


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def validate() -> int:
    failures: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing required research artifact: {path.relative_to(REPO)}")
    for py in (LANE / "src").rglob("*.py"):
        try:
            imports = _imports(py)
        except SyntaxError as exc:
            failures.append(f"syntax error in {py.relative_to(REPO)}: {exc}")
            continue
        for name in imports:
            if name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                failures.append(f"forbidden production/runtime import {name!r} in {py.relative_to(REPO)}")
    if failures:
        print("LOOM RF VALIDATION: FAIL")
        for item in failures:
            print(" -", item)
        return 1
    print("LOOM RF VALIDATION: PASS")
    print("Research lane is structurally isolated from Navigator/GIS runtime imports.")
    return 0


def infrastructure_smoke() -> int:
    seed = 2226
    n = 12
    edges = [(i, (i + 1) % n) for i in range(n)]
    adjacency = {i: set() for i in range(n)}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)
    degree_vector = [len(adjacency[i]) for i in range(n)]
    result = {
        "kind": "infrastructure_smoke_not_rqo1",
        "seed": seed,
        "nodes": n,
        "edges": len(edges),
        "degree_vector": degree_vector,
        "degree_sum": sum(degree_vector),
        "git_sha": git_sha(),
    }
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "infrastructure_smoke.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print("OUTPUT:", out)
    return 0 if result["degree_sum"] == 2 * result["edges"] else 1


def controls() -> int:
    if dependency_status() != 0:
        return 2
    from .diagnostic_controls import qualify_controls
    payload = qualify_controls(n=100, degree=4, seed=2226)
    payload["git_sha"] = git_sha()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "diagnostic_controls.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print("OUTPUT:", out)
    return 0 if payload["passed"] else 1


def rqo1_smoke() -> int:
    if dependency_status() != 0:
        return 2
    from .rqo1_reconstruction import pass_fail_verdict, run_scan

    declared_cells = [(0.0, 0.0), (0.0, 0.5)]
    results = []
    for alpha, beta in declared_cells:
        results.extend(run_scan(N=40, avg_degree=4, n_steps=30,
                                alphas=[alpha], betas=[beta], seeds=[2226]))
    verdict = pass_fail_verdict(results)
    payload = {
        "kind": "rqo1_protocol_class_smoke_reconstruction",
        "historical_exact_cells_known": False,
        "declared_reconstruction_cells": declared_cells,
        "N": 40,
        "avg_degree": 4,
        "n_steps": 30,
        "seeds": [2226],
        "results": results,
        "verdict": verdict,
        "git_sha": git_sha(),
    }
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "rqo1_smoke_reconstruction.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print("OUTPUT:", out)
    return 0


def r3_null() -> int:
    if dependency_status() != 0:
        return 2
    from .r3_null_scaling import run_r3

    payload = run_r3()
    payload["git_sha"] = git_sha()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "r3_auif_null_increasing_n.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print("OUTPUT:", out)
    return 0


def r4_isolate() -> int:
    if dependency_status() != 0:
        return 2
    from .r4_term_isolation import run_r4

    payload = run_r4()
    payload["git_sha"] = git_sha()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "r4_recovered_term_isolation.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print("OUTPUT:", out)
    return 0


def run_tests() -> int:
    return subprocess.call([
        sys.executable, "-m", "unittest", "discover",
        "-s", str(LANE / "tests"), "-p", "test_*.py"
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="loomrf", description="LOOM relational-foundations research operations")
    parser.add_argument("command", choices=["status", "validate", "deps", "test", "smoke", "controls", "rqo1-smoke", "r3-null", "r4-isolate"])
    args = parser.parse_args(argv)
    return {
        "status": status,
        "validate": validate,
        "deps": dependency_status,
        "test": run_tests,
        "smoke": infrastructure_smoke,
        "controls": controls,
        "rqo1-smoke": rqo1_smoke,
        "r3-null": r3_null,
        "r4-isolate": r4_isolate,
    }[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
