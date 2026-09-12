#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 empirical operator-location query over Navigator campaign state.

Reads LOOM_STATE_V1.json, projects the bounded read-only operator context, and emits
a compact evidence artifact for the acceptance question "Where am I?". No model call,
no world/canon merge, and no mutation occur here.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.loom_campaign_operator_context import project_campaign_operator_context

DEFAULT_STATE = Path("/storage/emulated/0/Download/LOOM_TEST/LOOM_STATE_V1.json")
DEFAULT_OUT = Path("/storage/emulated/0/Download/E1_1_OPERATOR_LOCATION_RESULT.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    state_path = args.state.expanduser()
    raw = state_path.read_bytes()
    state = json.loads(raw.decode("utf-8"))
    context = project_campaign_operator_context(state)
    loc = context["operator_context"]["current_location"]
    ship = context["operator_context"]["ship"]

    result = {
        "schema": "LOOM_E1_1_OPERATOR_LOCATION_RESULT_V1",
        "question": "Where am I?",
        "answer_packet": {
            "ship_name": ship["ship_name"],
            "location_token": loc["location_token"],
            "epoch_utc": loc["epoch_utc"],
            "kinematic_status": loc["kinematic_status"],
        },
        "operator_context": context,
        "source": {
            "path": str(state_path),
            "file_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "pass_criteria": {
            "location_from_navigator_location_token": loc["location_token"] == state.get("location_token"),
            "epoch_from_navigator_state": loc["epoch_utc"] == state.get("epoch_utc"),
            "kinematic_status_from_navigator_state": loc["kinematic_status"] == (state.get("kinematic_boundary") or {}).get("status"),
            "model_authority_zero": context["authority_policy"]["model_state_authority"] == "ZERO",
            "world_context_not_merged": context["authority_policy"]["world_context_merged"] is False,
        },
    }
    result["all_pass"] = all(result["pass_criteria"].values())

    out = args.out.expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("schema:", result["schema"])
    print("ship:", result["answer_packet"]["ship_name"])
    print("location_token:", result["answer_packet"]["location_token"])
    print("epoch_utc:", result["answer_packet"]["epoch_utc"])
    print("kinematic_status:", result["answer_packet"]["kinematic_status"])
    print("all_pass:", result["all_pass"])
    print("out:", out)
    return 0 if result["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
