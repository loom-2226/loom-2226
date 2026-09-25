from __future__ import annotations

"""Read Navigator-owned destination and priority registries without executing it."""

import ast
from functools import lru_cache
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NAVIGATOR_SOURCE = REPO_ROOT / "src" / "loom_navigator_core.py"


def _token(value: str) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


@lru_cache(maxsize=8)
def load_navigator_registry(source_path: Path = DEFAULT_NAVIGATOR_SOURCE) -> tuple[dict[str, str], set[str]]:
    path = Path(source_path).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name in {"DEST_ALIASES", "PRIORITIES"}:
            values[name] = ast.literal_eval(node.value)
    aliases = values.get("DEST_ALIASES")
    priorities = values.get("PRIORITIES")
    if not isinstance(aliases, dict) or not aliases:
        raise RuntimeError("Navigator DEST_ALIASES registry not found")
    if not isinstance(priorities, set) or not priorities:
        raise RuntimeError("Navigator PRIORITIES registry not found")
    normalized_aliases = {_token(str(k)): _token(str(v)) for k, v in aliases.items()}
    normalized_priorities = {_token(str(v)) for v in priorities}
    return normalized_aliases, normalized_priorities


def resolve_destination(value: str, *, source_path: Path = DEFAULT_NAVIGATOR_SOURCE) -> str:
    aliases, _ = load_navigator_registry(Path(source_path))
    token = _token(value)
    canonical = aliases.get(token)
    if canonical is None:
        raise ValueError(f"Mara returned destination not supported by Navigator: {value!r}")
    return canonical


def resolve_priority(value: str, *, source_path: Path = DEFAULT_NAVIGATOR_SOURCE) -> str:
    _, priorities = load_navigator_registry(Path(source_path))
    token = _token(value)
    # Natural-language display phrasing remains a boundary concern; the accepted
    # canonical value still has to exist in Navigator's authoritative registry.
    if token.endswith("_PROFILE"):
        token = token[:-8]
    if token not in priorities:
        raise ValueError(f"Mara returned priority not supported by Navigator: {value!r}")
    return token


def navigator_destination_aliases(*, source_path: Path = DEFAULT_NAVIGATOR_SOURCE) -> Mapping[str, str]:
    aliases, _ = load_navigator_registry(Path(source_path))
    return dict(aliases)
