#!/usr/bin/env python3
"""LOOM converged GIS launcher — Phase 4.

Runs the known-good Solar GIS with the read-only Navigator route-layer extension.
The underlying GIS monolith remains unchanged for rollback and regression safety.
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
from loom.gis import build_navigation_overlay, install_navigation_overlay
from loom.gis.navigation_overlay import load_route_layer


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--nav-route", type=Path)
    ap.add_argument("--nav-alt", type=Path, action="append", default=[])
    ap.add_argument("--nav-history", type=Path, action="append", default=[])
    ap.add_argument("--nav-overlay-info", action="store_true")
    args, rest = ap.parse_known_args(argv)

    active_path = args.nav_route or _default_active_route()
    active = load_route_layer(active_path) if active_path else None
    alternates = [load_route_layer(p) for p in args.nav_alt]
    history = [load_route_layer(p) for p in args.nav_history]
    overlay = build_navigation_overlay(active, alternates, history)
    install_navigation_overlay(solar_gis, overlay)

    if args.nav_overlay_info:
        print(json.dumps(overlay.to_dict(), indent=2))
        return 0

    if active_path:
        print("NAV ROUTE    ", active_path)
        print("NAV CONTRACT ", active.contract)
        print("NAV ROUTE SHA", active.sha256())
    else:
        print("NAV ROUTE     none supplied · GIS navigation controls remain available")
    print("NAV OVERLAY  ", overlay.contract)
    return solar_gis.main(rest)


if __name__ == "__main__":
    raise SystemExit(main())
