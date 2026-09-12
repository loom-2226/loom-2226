#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 Pixel qualification harness for current-place handoff.

Runs three bounded cases without mutating campaign/canon state:
1. actual live Navigator location -> unsupported must surface honestly;
2. disposable Ceres fixture shifted to 2027 -> temporal mismatch must hard-fail;
3. disposable Ceres 2226 fixture -> positive Canon Context handoff.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loom_campaign_operator_context import project_campaign_operator_context
from loom_current_place_handoff import resolve_current_place_handoff

SCHEMA = "LOOM_E1_1_CURRENT_PLACE_HANDOFF_RESULT_V1"
DEFAULT_FIXTURE = ROOT / "engineering" / "experience_one" / "fixtures" / "E1_1_CERES_OPERATOR_STATE_2226.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return value


def _run_case(name: str, state: dict, world_db: Path, civstate_db: Path, expected: str) -> dict:
    operator = project_campaign_operator_context(state)
    result = resolve_current_place_handoff(operator, world_db, civstate_db)
    return {
        "case": name,
        "expected_status": expected,
        "observed_status": result["status"],
        "pass": result["status"] == expected,
        "human_message": result["human_message"],
        "location": result["current_location"],
        "canon_reference_year": result["canon_reference_year"],
        "canon_context_present": result["canon_context"] is not None,
        "sources_merged": result["authority_policy"]["sources_merged"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-state", type=Path, required=True)
    ap.add_argument("--root", type=Path, required=True, help="LOOM runtime root containing data/")
    ap.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    live = _load(args.live_state)
    fixture = _load(args.fixture)
    if fixture.get("fixture_meta", {}).get("authoritative_campaign_state") is not False:
        raise RuntimeError("Ceres acceptance fixture must be explicitly non-authoritative")

    world_db = args.root / "data" / "LOOM_2226.sqlite3"
    civstate_db = args.root / "data" / "LOOM_2226_CIVSTATE.sqlite3"

    mismatch = deepcopy(fixture)
    mismatch["epoch_utc"] = "2027-06-15T08:57:51Z"
    mismatch["state_id"] = "E1_1_DISPOSABLE_CERES_TEMPORAL_MISMATCH"

    cases = [
        _run_case("live_location_honest_miss", live, world_db, civstate_db, "UNSUPPORTED_ENTITY"),
        _run_case("ceres_2027_temporal_firewall", mismatch, world_db, civstate_db, "TEMPORAL_MISMATCH"),
        _run_case("ceres_2226_positive_control", fixture, world_db, civstate_db, "AVAILABLE"),
    ]

    result = {
        "schema": SCHEMA,
        "cases": cases,
        "all_pass": all(case["pass"] for case in cases),
        "authority": {
            "live_campaign_mutation": False,
            "fixture_campaign_mutation": False,
            "canon_mutation": False,
            "model_call": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("schema:", result["schema"])
    for case in cases:
        print(
            f"{case['case']}: {'PASS' if case['pass'] else 'FAIL'} "
            f"expected={case['expected_status']} observed={case['observed_status']}"
        )
        print("  human_message:", case["human_message"])
    print("all_pass:", result["all_pass"])
    print("out:", args.out)
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
