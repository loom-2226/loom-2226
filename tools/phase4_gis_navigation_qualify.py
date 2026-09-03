#!/usr/bin/env python3
"""Functional qualification for Phase 4 GIS navigation rendering.

Uses the same frozen, offline Ceres->Mars flight as Gate A / Phase 3, converts
its authoritative route layer into GIS-owned render primitives, and proves the
GIS adapter neither mutates campaign state nor fabricates unavailable geometry.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.gis.navigation_overlay import GIS_NAV_OVERLAY_VERSION, build_navigation_overlay
from loom.navigation import NavigationContext, LegacyNavigationService
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate


def solve_frozen_layer(service, bundle):
    rows = history_records(bundle.history)
    commit, arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])
    base = NavigationContext(campaign_state=state, runtime_root=bundle.root)
    nav = service._sequence_h(base)
    normalized = nav.validate_and_normalize_mission(mission)
    acquisition = nav.run_acquisition(normalized, bundle.cache, offline=True, refresh=False)
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
    if dict(context.campaign_state) != before:
        raise RuntimeError("Phase 4 source solve mutated campaign state")
    if plan.payload["determinism"]["canonical_runtime_sha256"] != arrived["details"]["runtime_sha256"]:
        raise RuntimeError("Phase 4 source solve differs from frozen runtime")
    return layer, plan.payload["determinism"]["canonical_runtime_sha256"]


def qualify_layer(layer):
    before = copy.deepcopy(layer.to_dict())
    overlay = build_navigation_overlay(layer)
    if overlay.contract != GIS_NAV_OVERLAY_VERSION:
        raise RuntimeError("wrong GIS navigation overlay contract")
    if overlay.active_route is None:
        raise RuntimeError("active route missing from GIS overlay")
    route = overlay.active_route
    if route.source_sha256 != layer.sha256():
        raise RuntimeError("GIS route source hash does not match LOOM_ROUTE_LAYER_V1")
    if route.origin != layer.origin or route.destination != layer.destination:
        raise RuntimeError("GIS route endpoints differ from Navigator contract")
    if [s.type for s in route.segments] != [s.type for s in layer.segments]:
        raise RuntimeError("GIS phase ordering differs from Navigator contract")
    if layer.to_dict() != before:
        raise RuntimeError("GIS adapter mutated Navigator route contract")

    metric = [s for s in route.segments if s.type == "METRIC"]
    terminal = [s for s in route.segments if s.type == "TERMINAL_BURN"]
    if not metric or not terminal:
        raise RuntimeError("GIS overlay omitted authoritative metric/terminal phases")
    if any(s.geometry_points_j2000_ecliptic_km for s in route.segments):
        raise RuntimeError("GIS adapter invented sampled geometry for frozen RC6.1 route")
    if not any(a.anchor_type == "METRIC_COLLAPSE" for a in route.anchors):
        raise RuntimeError("GIS overlay omitted authoritative metric collapse anchor")
    if not metric[0].style or not terminal[0].style:
        raise RuntimeError("GIS did not assign presentation symbology")
    if "style" in layer.to_dict():
        raise RuntimeError("presentation leaked back into Navigator route contract")
    expected_controls = {
        "ACTIVE_ROUTE", "ALTERNATE_ROUTES", "FLIGHT_PHASES", "MANEUVERS",
        "HISTORICAL_TRACKS", "TRAFFIC_CIVSTATE",
    }
    if not expected_controls.issubset(set(overlay.controls)):
        raise RuntimeError("GIS navigation controls are incomplete")
    return overlay


def launcher_smoke(layer):
    td = Path(tempfile.mkdtemp(prefix="loom_phase4_"))
    route_path = td / "route.json"
    route_path.write_text(json.dumps(layer.to_dict(), indent=2) + "\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(REPO / "src" / "loom_gis.py"), "--nav-route", str(route_path), "--nav-overlay-info", "--no-flight-planning"],
        cwd=str(REPO), text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"loom_gis launcher smoke failed: {proc.stderr}\n{proc.stdout}")
    decoded = json.loads(proc.stdout)
    if decoded.get("contract") != GIS_NAV_OVERLAY_VERSION:
        raise RuntimeError("loom_gis launcher emitted wrong navigation contract")
    if decoded.get("active_route", {}).get("source_sha256") != layer.sha256():
        raise RuntimeError("loom_gis launcher changed active route source identity")
    js = (REPO / "src" / "loom" / "gis" / "navigation_overlay.js").read_text(encoding="utf-8")
    for token in ("ACTIVE", "ALTS", "PHASES", "MANEUVERS", "HISTORY", "TRAFFIC", "/navigation-overlay.json"):
        if token not in js:
            raise RuntimeError(f"GIS renderer missing required control/endpoint token: {token}")
    # Continuous line rendering must remain gated on already-sampled authoritative
    # geometry. This checks executable behavior rather than brittle comment text.
    normalized_js = "".join(js.split())
    if "if(pts.length>=2)navDrawPolyline(pts,seg.style,alpha);" not in normalized_js:
        raise RuntimeError("GIS renderer no longer gates polylines on authoritative sampled geometry")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime_root")
    ap.add_argument("--route-out", type=Path)
    args = ap.parse_args()
    root = Path(args.runtime_root).resolve()
    service = LegacyNavigationService(loom_navigator.load_core())
    result = None
    last_error = None
    for bundle in discover_runtime_bundles(root):
        try:
            layer, runtime_sha = solve_frozen_layer(service, bundle)
            overlay = qualify_layer(layer)
            launcher_smoke(layer)
            result = (bundle, layer, overlay, runtime_sha)
            break
        except Exception as exc:
            last_error = exc
            print("REJECT BUNDLE:", bundle.root, repr(exc))
    if result is None:
        raise RuntimeError(f"Phase 4 found no qualifying frozen runtime bundle: {last_error}")

    bundle, layer, overlay, runtime_sha = result
    if args.route_out:
        args.route_out.parent.mkdir(parents=True, exist_ok=True)
        args.route_out.write_text(json.dumps(layer.to_dict(), indent=2) + "\n", encoding="utf-8")
        print("route_fixture=", args.route_out)
    route = overlay.active_route
    print("PHASE4_GIS_NAVIGATION=PASS")
    print("EPHEMERIS_MODE=FROZEN_OFFLINE_ONLY")
    print("GIS_CONTRACT=", overlay.contract)
    print("SOURCE_CONTRACT=", layer.contract)
    print("flight_id=", route.flight_id)
    print("route=", [route.origin, route.destination])
    print("segment_types=", [x.type for x in route.segments])
    print("geometry_mode=AUTHORITATIVE_PHASE_ANCHORS_ONLY")
    print("sampled_track=NOT_INVENTED")
    print("controls=", list(overlay.controls))
    print("runtime_sha256=", runtime_sha)
    print("route_layer_sha256=", layer.sha256())
    print("runtime_bundle_root=", bundle.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
