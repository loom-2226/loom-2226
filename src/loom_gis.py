#!/usr/bin/env python3
"""LOOM converged GIS launcher — Phase 6.

Runs the known-good Solar GIS with Navigator route planning and canonical
campaign execution. Navigator owns flight truth; campaign services own
persistence; GIS owns interaction and presentation.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import loom_solar_gis as solar_gis
import loom_navigator
from loom.campaign import LegacyCampaignExecutionService
from loom.gis import build_navigation_overlay, install_navigation_overlay
from loom.gis.navigation_overlay import load_route_layer
from loom.gis.flight_planning import GISFlightPlanningSession
from loom.gis.flight_planning_http import install_flight_planning
from loom.navigation import NavigationContext
from loom.navigation.service import LegacyNavigationService


def _default_active_route() -> Path | None:
    env = os.environ.get("LOOM_ROUTE_LAYER")
    candidates = []
    if env:
        candidates.append(Path(env))
    loom_home = os.environ.get("LOOM_HOME")
    if loom_home:
        candidates.extend([
            Path(loom_home) / "state" / "LOOM_ACTIVE_ROUTE_LAYER.json",
            Path(loom_home) / "LOOM_ACTIVE_ROUTE_LAYER.json",
        ])
    for path in candidates:
        if path.exists():
            return path
    return None


def _planning_runtime_root(explicit: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if explicit:
        candidates.append(explicit)
    if os.environ.get("LOOM_HOME"):
        candidates.append(Path(os.environ["LOOM_HOME"]))
    candidates.extend([Path.cwd(), Path.cwd() / "LOOM_TEST", Path("/storage/emulated/0/Download/LOOM_TEST")])
    seen = set()
    for raw in candidates:
        try:
            root = raw.expanduser().resolve()
        except Exception:
            continue
        if str(root) in seen:
            continue
        seen.add(str(root))
        if (root / "LOOM_STATE_V1.json").is_file() and (root / "LOOM_Navigator_Internal_SequenceH").exists():
            return root
    return None


def _install_planning_and_execution(runtime_root: Path, *, offline: bool) -> GISFlightPlanningSession:
    state_path = runtime_root / "LOOM_STATE_V1.json"
    cache = runtime_root / "LOOM_Navigator_Cache_v1"
    b1_matches = sorted(runtime_root.glob("LOOM_Navigator_Visual_Design_B1_LOCKED_Package*.zip"))
    if not state_path.is_file():
        raise RuntimeError(f"campaign state not found: {state_path}")
    if not cache.exists():
        raise RuntimeError(f"Navigator cache not found: {cache}")
    if not b1_matches:
        raise RuntimeError(f"locked B1 package not found under {runtime_root}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    os.environ["LOOM_HOME"] = str(runtime_root)
    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    campaign = LegacyCampaignExecutionService(core)
    context = NavigationContext(
        campaign_state=state,
        cache_dir=cache,
        b1_package=b1_matches[0],
        runtime_root=runtime_root,
    )
    session = GISFlightPlanningSession(
        service,
        context,
        offline=offline,
        campaign_execution_service=campaign,
    )
    install_flight_planning(solar_gis, session)
    return session


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--nav-route", type=Path)
    ap.add_argument("--nav-alt", type=Path, action="append", default=[])
    ap.add_argument("--nav-history", type=Path, action="append", default=[])
    ap.add_argument("--nav-overlay-info", action="store_true")
    ap.add_argument("--nav-runtime-root", type=Path)
    ap.add_argument("--nav-planning-offline", action="store_true")
    ap.add_argument("--no-flight-planning", action="store_true")
    args, rest = ap.parse_known_args(argv)

    active_path = args.nav_route or _default_active_route()
    active = load_route_layer(active_path) if active_path else None
    alternates = [load_route_layer(p) for p in args.nav_alt]
    history = [load_route_layer(p) for p in args.nav_history]
    overlay = build_navigation_overlay(active, alternates, history)
    install_navigation_overlay(solar_gis, overlay)

    planning = None
    if not args.no_flight_planning:
        runtime_root = _planning_runtime_root(args.nav_runtime_root)
        if runtime_root:
            try:
                planning = _install_planning_and_execution(runtime_root, offline=args.nav_planning_offline)
            except Exception as exc:
                print("FLIGHT PLAN   unavailable ·", f"{type(exc).__name__}: {exc}")
        else:
            print("FLIGHT PLAN   unavailable · no coherent Navigator campaign runtime found")

    if args.nav_overlay_info:
        if args.no_flight_planning:
            out = overlay.to_dict()
        else:
            out = {"navigation_overlay": overlay.to_dict(), "flight_planning": planning.state().to_dict() if planning else None}
        print(json.dumps(out, indent=2))
        return 0

    if active_path:
        print("NAV ROUTE    ", active_path)
        print("NAV CONTRACT ", active.contract)
        print("NAV ROUTE SHA", active.sha256())
    else:
        print("NAV ROUTE     none supplied · GIS navigation controls remain available")
    print("NAV OVERLAY  ", overlay.contract)
    if planning:
        state = planning.state()
        print("FLIGHT PLAN  ", state.contract, "· origin", planning.origin, "·", "OFFLINE" if planning.offline else "CACHE/PROVIDER")
        print("CAMPAIGN EXEC", "ENABLED" if state.execution_available else "DISABLED")
    return solar_gis.main(rest)


if __name__ == "__main__":
    raise SystemExit(main())
