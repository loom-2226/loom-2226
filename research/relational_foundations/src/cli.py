from __future__ import annotations

import argparse
import ast
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
    LANE / "TERMUX_DEVOPS_WORKFLOW_v0.1.md",
]
FORBIDDEN_IMPORT_PREFIXES = ("src", "deploy", "web", "geometry", "engineering")


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
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
            failures.append(
                f"missing required research artifact: {path.relative_to(REPO)}"
            )
    for py in (LANE / "src").rglob("*.py"):
        try:
            imports = _imports(py)
        except SyntaxError as exc:
            failures.append(f"syntax error in {py.relative_to(REPO)}: {exc}")
            continue
        for name in imports:
            if name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                failures.append(
                    f"forbidden production/runtime import {name!r} in {py.relative_to(REPO)}"
                )
    if failures:
        print("LOOM RF VALIDATION: FAIL")
        for item in failures:
            print(" -", item)
        return 1
    print("LOOM RF VALIDATION: PASS")
    print("Research lane is structurally isolated from Navigator/GIS runtime imports.")
    return 0


def infrastructure_smoke() -> int:
    # Deliberately NOT the historical RQO-1 physics run. This verifies deterministic
    # research execution, provenance and output handling using only the stdlib.
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


def run_tests() -> int:
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(LANE / "tests"),
            "-p",
            "test_*.py",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="loomrf", description="LOOM relational-foundations research operations"
    )
    parser.add_argument("command", choices=["status", "validate", "test", "smoke"])
    args = parser.parse_args(argv)
    return {
        "status": status,
        "validate": validate,
        "test": run_tests,
        "smoke": infrastructure_smoke,
    }[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
