from __future__ import annotations

"""Command-line runner for deterministic full-curvature comparator qualification."""

import json

from .cli import DEFAULT_OUTPUT, dependency_status, git_sha
from .deterministic_curvature import run_deterministic_curvature


def main() -> int:
    if dependency_status() != 0:
        return 2
    payload = run_deterministic_curvature()
    payload["git_sha"] = git_sha()
    DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
    out = DEFAULT_OUTPUT / "rqo1_deterministic_curvature_comparator.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print("OUTPUT:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
