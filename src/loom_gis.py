#!/usr/bin/env python3
"""Unified LOOM GIS/Navigator runtime wrapper."""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

HERE = Path(__file__).resolve().parent
APP_ROOT_GUESS = HERE.parent
SRC_ROOT = APP_ROOT_GUESS / "src"
for candidate in (HERE, SRC_ROOT):
    text = str(candidate)
    if text not in sys.path:
        sys.path.insert(0, text)

import loom_solar_gis as solar_gis
from loom.runtime import resolve_runtime_roots, export_runtime_environment, RuntimeRoots
from loom.campaign.clock import LegacyCampaignClockService
from loom.gis.navigation_overlay import (
    build_navigation_overlay,
    install_navigation_overlay,
    load_route_layer,
)
from loom.gis.flight_planning import (
    GISFlightPlanningSession,
    install_flight_planning,
)
from loom.navigation.service import NavigationService
from loom.navigation.context import NavigationContext
from loom.campaign.execution import CampaignExecutionService
from loom.spatial.sqlite_source import SQLiteSpatialStateSource
from loom.spatial.http import install_spatial_state_endpoint


def _default_active_route(roots: RuntimeRoots) -> Path | None:
    candidates = [
        roots.app_root / "runtime" / "nav_route_active.json",
        roots.app_root / "nav_route_active.json",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _install_unified_context_drawer() -> None:
    """Placeholder hook retained for legacy UI compatibility."""
    return None


def _find_b1_package(app_root: Path) -> list[Path]:
    patterns = ["*B1*.json", "*b1*.json"]
    found: list[Path] = []
    for pattern in patterns:
        found.extend(app_root.rglob(pattern))
    return sorted({p.resolve() for p in found if p.is_file()})


def _install_planning_and_execution(roots: RuntimeRoots, *, offline: bool) -> GISFlightPlanningSession:
    service = NavigationService()
    campaign = CampaignExecutionService(roots.campaign_root)
    state = campaign.load_current_state()
    cache = roots.app_root / "cache" / "navigator"
    cache.mkdir(parents=True, exist_ok=True)
    b1_matches = _find_b1_package(roots.app_root)
    if not b1_matches:
        raise RuntimeError("Navigator B1 package not found under APP_ROOT")
    context = NavigationContext(
        campaign_state=state,
        cache_dir=cache,
        b1_package=b1_matches[0],
        runtime_root=roots.app_root,
    )
    session = GISFlightPlanningSession(
        service,
        context,
        offline=offline,
        campaign_execution_service=campaign,
    )
    install_flight_planning(solar_gis, session)
    _install_unified_context_drawer()
    return session


def _has_epoch_argument(args: list[str]) -> bool:
    for index, arg in enumerate(args):
        if arg == "--epoch":
            return index + 1 < len(args)
        if arg.startswith("--epoch="):
            return True
    return False


def _bind_live_scene_epoch(rest: list[str], roots: RuntimeRoots) -> tuple[list[str], str, str]:
    """Bind live scene time to campaign authority unless caller requested query time."""
    delegated = list(rest)
    if _has_epoch_argument(delegated):
        if "--epoch" in delegated:
            epoch = delegated[delegated.index("--epoch") + 1]
        else:
            epoch = next(arg.split("=", 1)[1] for arg in delegated if arg.startswith("--epoch="))
        return delegated, str(epoch), "EXPLICIT_QUERY"
    clock = LegacyCampaignClockService(roots.campaign_root).now()
    return ["--epoch", clock.epoch_utc, *delegated], clock.epoch_utc, "CAMPAIGN_CLOCK"


def _option_value(args: list[str], name: str) -> str | None:
    for index, arg in enumerate(args):
        if arg == name and index + 1 < len(args):
            return args[index + 1]
        if arg.startswith(name + "="):
            return arg.split("=", 1)[1]
    return None


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

    roots = resolve_runtime_roots(app_root=args.nav_runtime_root)
    export_runtime_environment(roots)
    rest, scene_epoch, scene_epoch_source = _bind_live_scene_epoch(list(rest), roots)
    campaign_clock = LegacyCampaignClockService(roots.campaign_root).now()

    spatial_db = Path(_option_value(rest, "--db") or (roots.data_root / "LOOM_2226.sqlite3")).expanduser().resolve()
    install_spatial_state_endpoint(
        solar_gis,
        source=SQLiteSpatialStateSource(spatial_db),
        scene_epoch_utc=scene_epoch,
        campaign_revision=campaign_clock.revision,
        campaign_epoch_utc=campaign_clock.epoch_utc,
        epoch_source=scene_epoch_source,
        web_root=roots.app_root / "web",
    )

    active_path = args.nav_route or _default_active_route(roots)
    active = load_route_layer(active_path) if active_path else None
    alternates = [load_route_layer(p) for p in args.nav_alt]
    history = [load_route_layer(p) for p in args.nav_history]
    overlay = build_navigation_overlay(active, alternates, history)
    install_navigation_overlay(solar_gis, overlay)

    planning = None
    if not args.no_flight_planning:
        try:
            planning = _install_planning_and_execution(roots, offline=args.nav_planning_offline)
        except Exception as exc:
            print("FLIGHT PLAN   unavailable ·", f"{type(exc).__name__}: {exc}")

    if args.nav_overlay_info:
        if args.no_flight_planning:
            out = overlay.to_dict()
        else:
            out = {"navigation_overlay": overlay.to_dict(), "flight_planning": planning.state().to_dict() if planning else None}
        out["runtime_roots"] = roots.to_dict()
        out["scene_epoch"] = {"epoch_utc": scene_epoch, "source": scene_epoch_source}
        out["spatial_state"] = {"endpoint": "/spatial-state.json", "viewer": "/3d", "database": str(spatial_db)}
        print(json.dumps(out, indent=2))
        return 0

    print("APP ROOT     ", roots.app_root, f"[{roots.app_source}]")
    print("DATA ROOT    ", roots.data_root, f"[{roots.data_source}]")
    print("CAMPAIGN ROOT", roots.campaign_root, f"[{roots.campaign_source}]")
    print("SCENE EPOCH  ", scene_epoch, f"[{scene_epoch_source}]")
    print("SPATIAL API  ", "/spatial-state.json", "·", spatial_db)
    print("SPATIAL 3D   ", "/3d", "· qualification view")
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
