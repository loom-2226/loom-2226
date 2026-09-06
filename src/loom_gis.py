#!/usr/bin/env python3
"""LOOM converged GIS launcher — Phase 6 / Stage C spatial convergence.

Runs the known-good Solar GIS with Navigator route planning and canonical
campaign execution. Runtime roots are resolved once; no filesystem archaeology
or cwd probing is used to discover campaign authority.

Stage C rule: unless an explicit ``--epoch`` query override is supplied, the
live GIS scene is evaluated at the canonical campaign clock epoch. The browser
therefore cannot quietly drift onto the Solar GIS legacy fixture date.
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
from loom.campaign.clock import LegacyCampaignClockService
from loom.gis import build_navigation_overlay, install_navigation_overlay
from loom.gis.navigation_overlay import load_route_layer
from loom.gis.flight_planning import GISFlightPlanningSession
from loom.gis.flight_planning_http import install_flight_planning
from loom.navigation import NavigationContext
from loom.navigation.service import LegacyNavigationService
from loom.runtime import RuntimeRoots, export_runtime_environment, resolve_runtime_roots


def _default_active_route(roots: RuntimeRoots) -> Path | None:
    env = os.environ.get("LOOM_ROUTE_LAYER")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    candidates.extend([
        roots.campaign_root / "state" / "LOOM_ACTIVE_ROUTE_LAYER.json",
        roots.campaign_root / "LOOM_ACTIVE_ROUTE_LAYER.json",
    ])
    for path in candidates:
        if path.is_file():
            return path
    return None


def _install_unified_context_drawer() -> None:
    """Install the shared NAV/ATLAS shell without changing Navigator or Atlas truth."""
    script_path = SRC / "loom" / "gis" / "flight_planning_unified_drawer.js"
    if not script_path.is_file():
        return
    marker = "/* LOOM_UNIFIED_NAV_ATLAS_DRAWER_V1 */"
    if marker in solar_gis.CLIENT_JS:
        return
    solar_gis.CLIENT_JS += "\n" + marker + "\n" + script_path.read_text(encoding="utf-8") + "\n"


def _navigator_runtime_paths(roots: RuntimeRoots) -> tuple[Path, Path]:
    """Return explicit Sequence-H and Navigator cache locations for the root topology.

    Legacy/combined layouts keep both under APP_ROOT. The migrated split layout
    keeps Sequence-H under APP_ROOT and cache under the sibling LOOM/cache tree.
    """
    app_root = roots.app_root
    if roots.campaign_root == app_root:
        cache_root = app_root
    else:
        cache_root = app_root.parent / "cache"
    return app_root / "LOOM_Navigator_Internal_SequenceH", cache_root / "LOOM_Navigator_Cache_v1"


def _install_planning_and_execution(roots: RuntimeRoots, *, offline: bool) -> GISFlightPlanningSession:
    """Bind Phase-6 planning to explicit APP and CAMPAIGN authorities."""
    app_root = roots.app_root
    campaign_root = roots.campaign_root
    state_path = campaign_root / "LOOM_STATE_V1.json"
    sequence_h, cache = _navigator_runtime_paths(roots)
    b1_matches = sorted(app_root.glob("LOOM_Navigator_Visual_Design_B1_LOCKED_Package*.zip"))

    if not state_path.is_file():
        raise RuntimeError(f"campaign state not found: {state_path}")
    if not sequence_h.exists():
        raise RuntimeError(f"Navigator Sequence-H runtime not found: {sequence_h}")
    if not cache.exists():
        raise RuntimeError(f"Navigator cache not found: {cache}")
    if not b1_matches:
        raise RuntimeError(f"locked B1 package not found under {app_root}")

    state = json.loads(state_path.read_text(encoding="utf-8"))
    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    campaign = LegacyCampaignExecutionService(core)
    context = NavigationContext(
        campaign_state=state,
        cache_dir=cache,
        b1_package=b1_matches[0],
        runtime_root=app_root,
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
    """Return whether the delegated Solar GIS argv contains an explicit epoch."""
    for index, arg in enumerate(args):
        if arg == "--epoch":
            return index + 1 < len(args)
        if arg.startswith("--epoch="):
            return True
    return False


def _bind_live_scene_epoch(rest: list[str], roots: RuntimeRoots) -> tuple[list[str], str, str]:
    """Bind live scene time to campaign authority unless caller requested query time.

    Returns ``(argv, epoch, source)``. An explicit epoch is a non-authoritative
    simulation/query cursor; omission means the canonical campaign epoch.
    """
    delegated = list(rest)
    if _has_epoch_argument(delegated):
        if "--epoch" in delegated:
            epoch = delegated[delegated.index("--epoch") + 1]
        else:
            epoch = next(arg.split("=", 1)[1] for arg in delegated if arg.startswith("--epoch="))
        return delegated, str(epoch), "EXPLICIT_QUERY"
    clock = LegacyCampaignClockService(roots.campaign_root).now()
    return ["--epoch", clock.epoch_utc, *delegated], clock.epoch_utc, "CAMPAIGN_CLOCK"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--nav-route", type=Path)
    ap.add_argument("--nav-alt", type=Path, action="append", default=[])
    ap.add_argument("--nav-history", type=Path, action="append", default=[])
    ap.add_argument("--nav-overlay-info", action="store_true")
    # Compatibility alias: historically this selected the combined runtime root.
    # During convergence it selects APP_ROOT; CAMPAIGN_ROOT remains independently
    # overridable through LOOM_CAMPAIGN_ROOT.
    ap.add_argument("--nav-runtime-root", type=Path)
    ap.add_argument("--nav-planning-offline", action="store_true")
    ap.add_argument("--no-flight-planning", action="store_true")
    args, rest = ap.parse_known_args(argv)

    roots = resolve_runtime_roots(app_root=args.nav_runtime_root)
    export_runtime_environment(roots)
    rest, scene_epoch, scene_epoch_source = _bind_live_scene_epoch(list(rest), roots)

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
        print(json.dumps(out, indent=2))
        return 0

    print("APP ROOT     ", roots.app_root, f"[{roots.app_source}]")
    print("DATA ROOT    ", roots.data_root, f"[{roots.data_source}]")
    print("CAMPAIGN ROOT", roots.campaign_root, f"[{roots.campaign_source}]")
    print("SCENE EPOCH  ", scene_epoch, f"[{scene_epoch_source}]")
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
