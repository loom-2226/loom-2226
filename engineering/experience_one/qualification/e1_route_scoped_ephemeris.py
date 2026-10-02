#!/usr/bin/env python3
from __future__ import annotations

"""Bounded E1 adapter for route-scoped Sequence H ephemeris acquisition.

This adapter does not calculate, propagate, interpolate, cache, or source ephemerides.
It leaves Sequence H's authoritative acquisition machinery intact and narrows only
its pre-network acquisition plan to dependencies actually named by the normalized
route. The current E1 execution path exposes DIRECT_NAVIGATION only; gravity-assist
and precision-collapse execution remain disabled and therefore add no dependencies.

The adapter is deliberately installed onto a loaded Sequence H core module rather
than creating a second ephemeris implementation. Unsupported route-object kinds fail
closed.
"""

from typing import Any, Callable


SUPPORTED_ROUTE_KINDS = {"base", "local_direct_parent"}


def required_route_dependencies(core: Any, normalized_mission: dict) -> tuple[set[str], set[tuple[str, str]]]:
    route = normalized_mission.get("route")
    if not isinstance(route, list) or len(route) < 2:
        raise RuntimeError("route-scoped acquisition requires a normalized route with at least two tokens")

    required_base: set[str] = set()
    required_local: set[tuple[str, str]] = set()
    for token in route:
        rr = core.ROUTE_OBJECTS.get(token)
        if not isinstance(rr, dict):
            raise RuntimeError(f"route-scoped acquisition cannot resolve route token {token!r}")
        kind = rr.get("kind")
        if kind not in SUPPORTED_ROUTE_KINDS:
            raise RuntimeError(f"route-scoped acquisition does not support route kind {kind!r} for {token!r}")
        base_id = rr.get("base_id")
        if not base_id:
            raise RuntimeError(f"route token {token!r} has no base_id")
        required_base.add(str(base_id))
        if kind == "local_direct_parent":
            local_id = rr.get("local_id")
            if not local_id:
                raise RuntimeError(f"local route token {token!r} has no local_id")
            required_local.add((str(base_id), str(local_id)))
    return required_base, required_local


def install_route_scoped_acquisition(core: Any) -> None:
    """Install an idempotent plan filter on a loaded Sequence H core module."""
    if getattr(core, "_loom_e1_route_scope_installed", False):
        return

    original: Callable[[dict], list[dict]] = core.build_acquisition_plan

    def build_route_scoped_acquisition_plan(normalized_mission: dict) -> list[dict]:
        full_plan = original(normalized_mission)
        required_base, required_local = required_route_dependencies(core, normalized_mission)
        scoped: list[dict] = []
        observed_base: set[str] = set()
        observed_local: set[tuple[str, str]] = set()

        for item in full_plan:
            scope = item.get("scope")
            if scope == "BASE" and str(item.get("id")) in required_base:
                scoped.append(item)
                observed_base.add(str(item.get("id")))
            elif scope == "LOCAL":
                key = (str(item.get("system_id")), str(item.get("id")))
                if key in required_local:
                    scoped.append(item)
                    observed_local.add(key)

        missing_base = required_base - observed_base
        missing_local = required_local - observed_local
        if missing_base or missing_local:
            raise RuntimeError(
                "route-scoped acquisition plan missing required dependencies: "
                f"base={sorted(missing_base)} local={sorted(missing_local)}"
            )
        if not scoped:
            raise RuntimeError("route-scoped acquisition produced an empty plan")

        print(
            "EPHEMERIS SCOPE         ROUTE_REQUIRED_ONLY / "
            f"{len(scoped)} of {len(full_plan)} acquisition dependencies"
        )
        return scoped

    core._loom_e1_original_build_acquisition_plan = original
    core.build_acquisition_plan = build_route_scoped_acquisition_plan
    core._loom_e1_route_scope_installed = True
