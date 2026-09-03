#!/usr/bin/env python3
"""Qualify LOOM_ROUTE_LAYER_V1 against the frozen Pixel runtime.

The qualifier re-solves the same coherent frozen flight used by Gate A using
only archived Sequence-H ephemeris. It then proves the GIS route contract maps
real Navigator phase anchors and engineering state without changing physics,
mutating campaign state, adding presentation instructions or inventing a
sampled trajectory that RC6.1 does not provide.
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import GEOMETRY_MODE, NavigationContext, LegacyNavigationService, ROUTE_LAYER_VERSION
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate

FORBIDDEN_DISPLAY_KEYS = {
    "color", "colour", "icon", "stroke", "fill", "opacity",
    "line_width", "linewidth", "symbol", "css", "style", "symbology",
}
FORBIDDEN_INVENTED_GEOMETRY_KEYS = {"points", "polyline", "sampled_track", "samples"}


def assert_display_agnostic(value, path="route"):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_DISPLAY_KEYS:
                raise RuntimeError(f"display instruction leaked into route contract at {path}.{key}")
            assert_display_agnostic(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            assert_display_agnostic(child, f"{path}[{i}]")


def qualify_bundle(service, bundle):
    rows = history_records(bundle.history)
    commit, arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])

    base = NavigationContext(campaign_state=state, runtime_root=bundle.root)
    nav = service._sequence_h(base)
    normalized = nav.validate_and_normalize_mission(mission)
    try:
        acquisition = nav.run_acquisition(normalized, bundle.cache, offline=True, refresh=False)
    except Exception as exc:
        print("REJECT BUNDLE offline acquisition:", bundle.root, exc)
        return None

    request, candidate = make_request_and_candidate(commit, normalized, mission, state)
    context = NavigationContext(
        campaign_state=state,
        acquisition=acquisition,
        cache_dir=bundle.cache,
        b1_package=bundle.b1,
        runtime_root=bundle.root,
    )
    before = copy.deepcopy(dict(context.campaign_state))
    plan = service.compile_flight(request, candidate, context)
    layer = service.get_route_layer(plan, context)
    after = dict(context.campaign_state)

    if before != after:
        raise RuntimeError("route-layer adapter mutated canonical campaign state")
    if layer.contract != ROUTE_LAYER_VERSION:
        raise RuntimeError(f"wrong route contract {layer.contract}")
    if layer.payload.get("geometry_mode") != GEOMETRY_MODE:
        raise RuntimeError("route-layer geometry authority mode is missing or incorrect")
    if layer.flight_id != plan.flight_id:
        raise RuntimeError("route-layer flight identity does not match solved plan")
    if layer.origin != normalized["route"][0] or layer.destination != normalized["route"][1]:
        raise RuntimeError("route-layer endpoints do not match normalized mission")
    if layer.departure_epoch != state.get("epoch_utc"):
        raise RuntimeError("route-layer departure epoch is not canonical campaign epoch")

    flight = service.get_flight_geometry(plan)
    expected_arrival = flight.get("final_epoch_utc") or flight.get("arrival_epoch_utc")
    if expected_arrival and layer.arrival_epoch != expected_arrival:
        raise RuntimeError("route-layer arrival epoch differs from authoritative runtime")
    if layer.current_vehicle_state != state:
        raise RuntimeError("route-layer current_vehicle_state differs from departure snapshot")
    if layer.arrival_state.get("location") != normalized["route"][1]:
        raise RuntimeError("route-layer arrival_state destination mismatch")
    if expected_arrival and layer.arrival_state.get("epoch_utc") != expected_arrival:
        raise RuntimeError("route-layer arrival_state epoch mismatch")

    source_legs = [leg for leg in flight.get("legs") or [] if isinstance(leg, dict)]
    if not source_legs:
        raise RuntimeError("frozen runtime has no authoritative legs")
    source_leg = source_legs[0]
    source_metric = source_leg.get("metric_segment") or {}
    source_terminal = source_leg.get("terminal_burn") or {}
    source_arrival = source_leg.get("arrival") or {}

    types = [segment.type for segment in layer.segments]
    if "UNSPECIFIED" in types:
        raise RuntimeError("real Sequence-H leg degraded to UNSPECIFIED route segment")
    if source_metric and "METRIC" not in types:
        raise RuntimeError("metric_segment was not promoted into route contract")
    if source_terminal and "TERMINAL_BURN" not in types:
        raise RuntimeError("terminal_burn was not promoted into route contract")

    if source_metric:
        metric = next(segment for segment in layer.segments if segment.type == "METRIC")
        collapse = source_metric.get("collapse_position_km_j2000_ecliptic")
        if collapse is not None and metric.end_position.get("position_km") != collapse:
            raise RuntimeError("metric collapse position differs from authoritative Sequence-H anchor")
        if metric.end_epoch != source_metric.get("collapse_epoch_utc"):
            raise RuntimeError("metric collapse epoch differs from authoritative Sequence-H epoch")
        if collapse is not None and metric.geometry.get("collapse_position_km") != collapse:
            raise RuntimeError("metric geometry omitted authoritative collapse anchor")

    if source_terminal:
        terminal = next(segment for segment in layer.segments if segment.type == "TERMINAL_BURN")
        if terminal.velocity.get("delta_v_km_s") != source_terminal.get("delta_v_km_s"):
            raise RuntimeError("terminal delta-v differs from authoritative Sequence-H value")
        if terminal.acceleration.get("initial_accel_g") != source_terminal.get("initial_accel_g"):
            raise RuntimeError("terminal initial acceleration differs from authoritative Sequence-H value")
        if terminal.acceleration.get("final_accel_g") != source_terminal.get("final_accel_g"):
            raise RuntimeError("terminal final acceleration differs from authoritative Sequence-H value")
        if terminal.end_epoch != source_arrival.get("epoch_utc"):
            raise RuntimeError("terminal segment end epoch differs from authoritative arrival")

    for segment in layer.segments:
        leaked = FORBIDDEN_INVENTED_GEOMETRY_KEYS.intersection(segment.geometry.keys())
        if leaked:
            raise RuntimeError(f"route contract invented sampled geometry fields: {sorted(leaked)}")

    bodies = {(b.body_id, b.role) for b in layer.bodies}
    if (normalized["route"][0], "ORIGIN") not in bodies or (normalized["route"][1], "DESTINATION") not in bodies:
        raise RuntimeError("route-layer body references omit origin/destination semantics")

    assert_display_agnostic(layer.to_dict())
    if layer.sha256() != service.get_route_layer(plan, context).sha256():
        raise RuntimeError("route-layer canonical serialization is nondeterministic")

    runtime_sha = plan.payload["determinism"]["canonical_runtime_sha256"]
    if runtime_sha != arrived["details"]["runtime_sha256"]:
        raise RuntimeError("Phase 3 qualification changed authoritative Navigator result")

    return {
        "bundle": bundle,
        "flight_id": plan.flight_id,
        "route": normalized["route"],
        "segment_types": types,
        "waypoints": len(layer.waypoints),
        "maneuvers": len(layer.maneuvers),
        "runtime_sha": runtime_sha,
        "route_layer_sha": layer.sha256(),
        "departure_epoch": layer.departure_epoch,
        "arrival_epoch": layer.arrival_epoch,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime_root")
    args = ap.parse_args()
    root = Path(args.runtime_root).resolve()

    service = LegacyNavigationService(loom_navigator.load_core())
    result = None
    for bundle in discover_runtime_bundles(root):
        try:
            result = qualify_bundle(service, bundle)
        except Exception as exc:
            print("REJECT BUNDLE:", bundle.root, repr(exc))
            result = None
        if result:
            break
    if result is None:
        raise RuntimeError("Phase 3 found no coherent frozen bundle satisfying LOOM_ROUTE_LAYER_V1")

    print("PHASE3_ROUTE_LAYER_V1=PASS")
    print("EPHEMERIS_MODE=FROZEN_OFFLINE_ONLY")
    print("GEOMETRY_MODE=", GEOMETRY_MODE)
    print("SAMPLED_TRACK=NOT_EXPOSED_BY_RC6_1")
    print("contract=", ROUTE_LAYER_VERSION)
    print("flight_id=", result["flight_id"])
    print("route=", result["route"])
    print("segment_types=", result["segment_types"])
    print("waypoints=", result["waypoints"])
    print("maneuvers=", result["maneuvers"])
    print("departure_epoch=", result["departure_epoch"])
    print("arrival_epoch=", result["arrival_epoch"])
    print("runtime_sha256=", result["runtime_sha"])
    print("route_layer_sha256=", result["route_layer_sha"])
    print("runtime_bundle_root=", result["bundle"].root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
