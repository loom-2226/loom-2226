#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 read-only campaign-state location diagnostic.

Purpose
-------
Before introducing any Experience Context composition contract, inspect the actual
Navigator-owned LOOM_STATE_V1.json shape on the Pixel and identify which existing
fields can answer the operator question "Where am I?".

This probe is diagnostic only. It does not define a new campaign-state schema, infer
new world facts, mutate state, call a model, or claim location authority. Navigator
remains the authoritative state owner.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_STATE = Path("/storage/emulated/0/Download/LOOM_STATE_V1.json")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_CAMPAIGN_STATE_LOCATION_PROBE.json")

KEY_HINTS = (
    "location",
    "loc",
    "body",
    "position",
    "target",
    "destination",
    "origin",
    "epoch",
    "time",
    "kinematic",
    "flight",
    "ship",
    "wayfarer",
    "state",
)


def _walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{path}.{key}"
            yield from _walk(value[key], child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{path}[{index}]"
            yield from _walk(item, child)
    else:
        yield path, value


def _is_location_candidate(path: str) -> bool:
    low = path.lower()
    return any(hint in low for hint in KEY_HINTS)


def build_probe(state_bytes: bytes, state_path: Path) -> dict[str, Any]:
    state = json.loads(state_bytes.decode("utf-8"))
    if not isinstance(state, dict):
        raise ValueError("campaign state root must be a JSON object")

    scalars = list(_walk(state))
    candidates = [
        {"path": path, "value": value, "value_type": type(value).__name__}
        for path, value in scalars
        if _is_location_candidate(path)
    ]

    return {
        "schema": "LOOM_E1_1_CAMPAIGN_STATE_LOCATION_PROBE_V1",
        "source": {
            "path": str(state_path),
            "sha256": hashlib.sha256(state_bytes).hexdigest(),
            "root_keys": sorted(state.keys()),
            "scalar_count": len(scalars),
        },
        "location_candidate_fields": candidates,
        "authority": {
            "source_authority": "NAVIGATOR_CAMPAIGN_STATE",
            "probe_authority": "NONE",
            "read_only": True,
            "model_call": False,
            "calculation_authority": "NONE",
            "state_authority": "NONE",
            "campaign_mutation": False,
            "canon_mutation": False,
        },
        "diagnostic_question": "Which existing Navigator-owned campaign-state fields can deterministically answer: Where am I?",
        "interpretation_rule": "Do not promote candidate fields to an Experience Context contract until empirical state shape is inspected.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    state_path = args.state.expanduser()
    if not state_path.is_file():
        raise FileNotFoundError(f"campaign state not found: {state_path}")

    raw = state_path.read_bytes()
    result = build_probe(raw, state_path)

    out = args.out.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("schema:", result["schema"])
    print("state_sha256:", result["source"]["sha256"])
    print("root_keys:", result["source"]["root_keys"])
    print("candidate_fields:", len(result["location_candidate_fields"]))
    for item in result["location_candidate_fields"]:
        print(f"{item['path']} = {item['value']!r}")
    print("out:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
