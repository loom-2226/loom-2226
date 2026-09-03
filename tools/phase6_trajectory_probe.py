#!/usr/bin/env python3
"""Qualify authoritative packed trajectory decoding against frozen Navigator truth."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections.abc import Mapping

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import NavigationContext, LegacyNavigationService
from loom.navigation.flight_payload import decode_flight_solutions
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate


def bin_refs(value, prefix="geometry"):
    if isinstance(value, Mapping):
        if set(value.keys()) == {"$bin"}:
            print("BINREF", prefix, value["$bin"])
            return
        for k, v in value.items():
            bin_refs(v, f"{prefix}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value[:10]):
            bin_refs(v, f"{prefix}[{i}]")


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
    assert len(timeline) == validation["sample_count"] == 100
    assert [round(float(timeline[i]["sample_index"])) for i in (0,1,48,99)] == [0,1,48,99]
    events = {x["event_id"]: x for x in solution["timeline"]["events"]}
    for event in events.values():
        assert abs(float(timeline[event["sample_index"]]["flight_t_s"]) - float(event["t_s"])) <= .0011

    ordinary = [(r["ordinary_pos_x_km"],r["ordinary_pos_y_km"],r["ordinary_pos_z_km"]) for r in timeline]
    assert all(all(v is None for v in p) for p in ordinary[:48])
    assert all(all(v is not None for v in p) for p in ordinary[48:])

    geom = solution.get("geometry") or {}
    print("GEOMETRY_KEYS", sorted(geom.keys()))
    print("SOLAR_3D", json.dumps(geom.get("solar_3d"), sort_keys=True)[:16000])
    bin_refs(geom)
    blocks = packed.metadata["_flight_binary_blocks"]
    for path, root_geom in (("solar_3d", geom.get("solar_3d")), ("solar", geom.get("solar")), ("solar_true", geom.get("solar_true"))):
        refs=[]
        def collect(v):
            if isinstance(v, Mapping):
                if "$bin" in v: refs.append(v["$bin"])
                else:
                    for x in v.values(): collect(x)
            elif isinstance(v,list):
                for x in v: collect(x)
        collect(root_geom)
        for ref in refs[:20]:
            print("BLOCK", path, ref, json.dumps(blocks[ref], sort_keys=True)[:5000])
            try:
                decoded=packed.block(ref)
                print("DECODED", ref, "rows", len(decoded) if isinstance(decoded,list) else type(decoded).__name__, "sample", json.dumps(decoded[:3] if isinstance(decoded,list) else decoded, default=str)[:4000])
            except Exception as exc:
                print("DECODE_ERROR", ref, repr(exc))

    print("PHASE6_TRAJECTORY_DECODER=PASS")
    print("sample_count=",len(timeline),"ordinary_3d_samples=",len(timeline)-48)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
