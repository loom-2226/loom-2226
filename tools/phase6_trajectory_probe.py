#!/usr/bin/env python3
"""Qualify authoritative packed trajectory decoding against frozen Navigator truth."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import NavigationContext, LegacyNavigationService
from loom.navigation.flight_payload import decode_flight_solutions
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate


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
    packed = decode_flight_solutions(payload)
    flight = plan.payload["runtime"]["flight"]
    leg = flight["legs"][0]
    route_plan_id = leg.get("route_plan_id") or flight.get("route_plan_id") or "L1"
    solution_key = f"{leg.get('metric_mode')}|{leg.get('torch_mode')}"
    solution = packed.select_solution(route_plan_id=route_plan_id, solution_key=solution_key)
    timeline = packed.timeline_rows(solution)

    validation = plan.payload["validation"]["sequence_b"]["payload_audits"][3]["timeline_validation"]["L1"]
    assert len(timeline) == validation["sample_count"] == 100, (len(timeline), validation)
    assert [round(float(timeline[i]["sample_index"])) for i in (0, 1, 48, 99)] == [0, 1, 48, 99]
    events = {x["event_id"]: x for x in solution["timeline"]["events"]}
    for event in events.values():
        row = timeline[event["sample_index"]]
        assert abs(float(row["flight_t_s"]) - float(event["t_s"])) <= 0.0011, (event, row["flight_t_s"])

    # Navigator's contract deliberately keeps ordinary position absent throughout
    # Metric transport and exposes it only from collapse into terminal flight.
    ordinary = [
        (row["ordinary_pos_x_km"], row["ordinary_pos_y_km"], row["ordinary_pos_z_km"])
        for row in timeline
    ]
    assert all(all(v is None for v in p) for p in ordinary[:48])
    assert all(all(v is not None for v in p) for p in ordinary[48:])
    assert all(int(round(float(row["position_semantics_code"]))) == 0 for row in timeline[:48])
    assert all(int(round(float(row["position_semantics_code"]))) == 1 for row in timeline[48:])

    print("PHASE6_TRAJECTORY_DECODER=PASS")
    print("route_plan_id=", route_plan_id)
    print("solution_key=", solution_key)
    print("sample_count=", len(timeline))
    print("metric_relational_samples=", 48)
    print("ordinary_3d_samples=", len(timeline) - 48)
    print("first_terminal_xyz_km=", ordinary[48])
    print("arrival_xyz_km=", ordinary[-1])
    print("events=", json.dumps(events, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
