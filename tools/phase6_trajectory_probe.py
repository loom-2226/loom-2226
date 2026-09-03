#!/usr/bin/env python3
"""Inspect frozen RC6.1 flight payload for authoritative trajectory-bearing fields."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections.abc import Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from loom.navigation import NavigationContext, LegacyNavigationService
import loom_navigator
from phase2_gate_a_qualify import discover_runtime_bundles, history_records, newest_completed_flight, make_request_and_candidate

KEY_HINTS = ("traj", "path", "position", "checkpoint", "sample", "state", "vector", "geometry", "timeline", "interpol")


def short(value, limit=5000):
    return json.dumps(value, default=str, sort_keys=True)[:limit]


def walk(value, prefix="", depth=0):
    if depth > 9:
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            p = f"{prefix}.{key}" if prefix else str(key)
            low = str(key).lower()
            if any(h in low for h in KEY_HINTS):
                kind = type(child).__name__
                size = len(child) if isinstance(child, (Mapping, Sequence)) and not isinstance(child, (str, bytes, bytearray)) else None
                print(f"FIELD {p} type={kind} size={size}")
                if isinstance(child, (list, tuple)) and child:
                    print("  SAMPLE", short(child[:3], 2400))
                elif isinstance(child, Mapping):
                    print("  MAP", short(child, 4000))
            walk(child, p, depth + 1)
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value[:12]):
            walk(child, f"{prefix}[{i}]", depth + 1)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    service = LegacyNavigationService(loom_navigator.load_core())
    bundles = discover_runtime_bundles(root)
    if not bundles:
        raise RuntimeError("no frozen runtime bundle")
    bundle = bundles[0]
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
    packed = dict(plan.payload)
    print("=== TOP LEVEL ===")
    print("PAYLOAD KEYS", sorted(packed.keys()))
    print("RUNTIME KEYS", sorted((packed.get("runtime") or {}).keys()))
    print("PAYLOADS TYPE", type(packed.get("payloads")).__name__)
    if isinstance(packed.get("payloads"), Mapping):
        print("PAYLOADS KEYS", sorted(map(str, packed["payloads"].keys())))
    elif isinstance(packed.get("payloads"), (list, tuple)):
        print("PAYLOADS COUNT", len(packed["payloads"]))
        for i, row in enumerate(packed["payloads"][:10]):
            print(f"PAYLOAD[{i}]", short(row, 3500))
    print("=== RUNTIME FLIGHT TRAJECTORY CAPABILITY PROBE ===")
    walk(packed)
    validation = packed.get("validation") or {}
    seq_a = validation.get("sequence_a") or {}
    print("=== SEQUENCE A INTERPOLATION ===")
    print(short(seq_a.get("interpolation"), 10000))
    seq_b = validation.get("sequence_b") or {}
    print("=== SEQUENCE B AUTHORITY ===")
    print(short(seq_b.get("authority"), 5000))
    print("=== SEQUENCE B PAYLOAD AUDITS ===")
    print(short(seq_b.get("payload_audits"), 12000))
    print("=== END PROBE ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
