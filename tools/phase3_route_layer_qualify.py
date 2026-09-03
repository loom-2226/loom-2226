#!/usr/bin/env python3
"""Qualify LOOM_ROUTE_LAYER_V1 against the frozen Pixel runtime.

This test re-solves the same coherent frozen flight used by Gate A, entirely
from archived Sequence-H ephemeris, then builds the GIS-facing route contract.
It proves the adapter preserves route identity, authoritative epochs/state and
determinism without mutating campaign state or introducing display semantics.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import NavigationContext, LegacyNavigationService, ROUTE_LAYER_VERSION
import loom_navigator
from phase2_gate_a_qualify import (
    discover_runtime_bundles,
    history_records,
    newest_completed_flight,
    make_request_and_candidate,
)

FORBIDDEN_DISPLAY_KEYS = {
    "color", "colour", "icon", "stroke", "fill", "opacity",
    "line_width", "linewidth", "symbol", "css", "style", "symbology",
}


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

    context0 = NavigationContext(campaign_state=state, runtime_root=bundle.root)
    nav = service._sequence_h(context0)
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
    if not layer.segments:
        raise RuntimeError("route-layer exposes no authoritative flight segments")
    if layer.current_vehicle_state != state:
        raise RuntimeError("route-layer current_vehicle_state differs from departure snapshot")
    if layer.arrival_state.get("location") != normalized["route"][1]:
        raise RuntimeError("route-layer arrival_state destination mismatch")
    if expected_arrival and layer.arrival_state.get("epoch_utc") != expected_arrival:
        raise RuntimeError("route-layer arrival_state epoch mismatch")

    bodies = {(b.body_id, b.role) for b in layer.bodies}
    if (normalized["route"][0], "ORIGIN") not in bodies or (normalized["route"][1], "DESTINATION") not in bodies:
        raise RuntimeError("route-layer body references omit origin/destination semantics")

    wire = layer.to_dict()
    assert_display_agnostic(wire)
    if layer.sha256() != service.get_route_layer(plan, context).sha256():
        raise RuntimeError("route-layer canonical serialization is nondeterministic")

    runtime_sha = plan.payload["determinism"]["canonical_runtime_sha256"]
    expected_runtime_sha = arrived["details"]["runtime_sha256"]
    if runtime_sha != expected_runtime_sha:
        raise RuntimeError("Phase 3 qualification changed authoritative Navigator result")

    return {
        "bundle": bundle,
        "flight_id": plan.flight_id,
        "route": normalized["route"],
        "segments": len(layer.segments),
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
    archive_root = Path(args.runtime_root).resolve()

    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    result = None
    for bundle in discover_runtime_bundles(archive_root):
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
    print("contract=", ROUTE_LAYER_VERSION)
    print("flight_id=", result["flight_id"])
    print("route=", result["route"])
    print("segments=", result["segments"])
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
