from __future__ import annotations

"""Command-line runner for the preregistered corrected-curvature convergence check."""

import json

from .cli import DEFAULT_OUTPUT, dependency_status, git_sha
from .curvature_convergence import run_curvature_convergence


def main() -> int:
    if dependency_status() != 0:
        return 2
    payload = run_curvature_convergence()
    payload["git_sha"] = git_sha()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "rqo1_corrected_curvature_convergence.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print("OUTPUT:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
