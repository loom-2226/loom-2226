#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 Mara Ceres orientation synthesis harness v0.2.

v0.2 fixes only the grounding-path validator defect exposed by the v0.1 Pixel run:
model evidence paths used conventional JSON-style list notation such as
``interesting.items[0]`` while the v0.1 validator accepted only dotted numeric
segments such as ``interesting.items.0``.

This version preserves the exact synthesis authority boundary and prompt. It does
not loosen grounding requirements or change model authority. It accepts both
notations deterministically and fails closed on malformed, negative, or out-of-range
indices.
"""

import importlib.util
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
V01 = HERE / "e1_1_mara_ceres_orientation_synthesis_v01.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v01 = _load(V01, "e1_1_mara_ceres_orientation_synthesis_v01")

# Re-export unchanged experiment contract/helpers.
build_evidence = v01.build_evidence
parse_json_answer = v01.parse_json_answer
SYSTEM = v01.SYSTEM
USER_PROMPT = v01.USER_PROMPT
DEFAULT_PROJECTION = v01.DEFAULT_PROJECTION
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_MARA_CERES_ORIENTATION_SYNTHESIS_V02.json")
DEFAULT_AUDIT = v01.DEFAULT_AUDIT
base = v01.base

_SEGMENT_RE = re.compile(r"^(?P<key>[^\[\]]+)?(?P<indices>(?:\[\d+\])*)$")
_INDEX_RE = re.compile(r"\[(\d+)\]")


def _apply_segment(current: Any, segment: str) -> tuple[bool, Any]:
    if not segment:
        return False, current

    match = _SEGMENT_RE.fullmatch(segment)
    if match is None:
        return False, current

    key = match.group("key")
    if key:
        if isinstance(current, dict):
            if key not in current:
                return False, current
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            idx = int(key)
            if idx >= len(current):
                return False, current
            current = current[idx]
        else:
            return False, current

    for raw_index in _INDEX_RE.findall(match.group("indices")):
        if not isinstance(current, list):
            return False, current
        idx = int(raw_index)
        if idx >= len(current):
            return False, current
        current = current[idx]

    return True, current


def path_exists(value: Any, path: str) -> bool:
    """Resolve deterministic evidence paths in dotted or JSON-style list notation.

    Accepted examples:
    - orient.facts.identity.value.summary
    - interesting.items.0.name
    - interesting.items[0].name
    - interesting.items[0]

    Negative indices, malformed brackets, empty segments, and out-of-range indices
    fail closed.
    """
    if not isinstance(path, str) or not path or path.startswith(".") or path.endswith("."):
        return False

    current = value
    for segment in path.split("."):
        ok, current = _apply_segment(current, segment)
        if not ok:
            return False
    return True


def validate_answer(evidence: dict[str, Any], answer: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if set(answer) != {"answer", "assessment", "evidence_paths"}:
        reasons.append("response_shape_mismatch")
    text = answer.get("answer")
    if not isinstance(text, str) or not text.strip():
        reasons.append("answer_missing")
    if answer.get("assessment") != "SUPPORTED":
        reasons.append("assessment_must_be_supported")
    paths = answer.get("evidence_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
        reasons.append("evidence_paths_invalid")
        paths = []
    bad = [p for p in paths if not path_exists(evidence, p)]
    if bad:
        reasons.append("evidence_path_not_in_packet")
    if not any(p.startswith("orient.") for p in paths):
        reasons.append("orientation_grounding_missing")
    if not any(p.startswith("interesting.") for p in paths):
        reasons.append("interesting_grounding_missing")
    return not reasons, reasons


def main() -> int:
    # Reuse v0.1 execution flow without modifying its historical source. Temporarily
    # substitute the corrected validator and v0.2 output path, then restore globals.
    import sys

    original_validate = v01.validate_answer
    original_default_out = v01.DEFAULT_OUT
    try:
        v01.validate_answer = validate_answer
        v01.DEFAULT_OUT = DEFAULT_OUT
        return v01.main()
    finally:
        v01.validate_answer = original_validate
        v01.DEFAULT_OUT = original_default_out


if __name__ == "__main__":
    raise SystemExit(main())
