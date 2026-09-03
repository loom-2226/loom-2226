#!/usr/bin/env python3
"""Inspect frozen RC6.1 flight payload for authoritative trajectory-bearing fields."""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path
from collections.abc import Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import NavigationContext, LegacyNavigationService
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate


def unpack_payload(value):
    if not isinstance(value, (bytes, bytearray)) or len(value) < 4:
        raise TypeError("packed flight payload required")
    n = struct.unpack_from("<I", value, 0)[0]
    meta = json.loads(bytes(value[4:4+n]).decode("utf-8"))
    return meta, bytes(value[4+n:])


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    service = LegacyNavigationService(loom_navigator.load_core())
    bundle = discover_runtime_bundles(root)[0]
    rows = history_records(bundle.history)
    commit, _arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])
    base = NavigationContext(campaign_state=state, runtime_root=bundle.root)
    nav = service._sequence_h(base)
    normalized = nav.validate_and_normalize_mission(mission)
    acquisition = nav.run_acquisition(normalized, bundle.cache, offline=True, refresh=False)
    request, candidate = make_request_and_candidate(commit, normalized, mission, state)
    context = NavigationContext(campaign_state=state, acquisition=acquisition, cache_dir=bundle.cache, b1_package=bundle.b1, runtime_root=bundle.root)
    plan = service.compile_flight(request, candidate, context)
    payload = plan.payload["payloads"]["flightSolutionsPayload"]
    meta, binary = unpack_payload(payload)
    sol = meta["route_plans"]["L1"]["solutions"]["HARD|CRUISE"]
    print("CODEC", meta["_flight_binary_codec"])
    print("TIMELINE", json.dumps({k:v for k,v in sol["timeline"].items() if k not in {"local_screen_by_projection","local_screen_by_view","local_depth_by_view","solar_screen_by_projection","solar_screen_by_view"}}, sort_keys=True)[:6000])
    table = meta["_flight_binary_blocks"][sol["timeline"]["samples"]["$bin"]]
    print("TABLE rows", table["rows"], "cols", table["cols"])
    fields = meta["timeline_contract"]["field_index"]
    inverse = {v:k for k,v in fields.items()}
    for idx in range(min(39, len(table["columns"]))):
        desc = table["columns"][idx]
        print("COLUMN", idx, inverse.get(idx), json.dumps(desc, sort_keys=True))
        series = desc.get("series") if isinstance(desc, dict) else None
        if series:
            off = series["data_offset"]; size = series["data_bytes"]
            print("  DATA_HEX", binary[off:off+min(size,48)].hex())
            if series.get("presence_bytes"):
                po=series["presence_offset"]; ps=series["presence_bytes"]
                print("  PRESENCE_HEX", binary[po:po+ps].hex())
    print("VALIDATION", json.dumps(plan.payload["validation"]["sequence_b"]["payload_audits"][3]["timeline_validation"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
