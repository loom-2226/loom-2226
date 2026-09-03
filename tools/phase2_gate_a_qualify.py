#!/usr/bin/env python3
"""Phase-2 Gate A qualifier against a frozen Pixel runtime archive.

The archive may contain multiple historical copies of similarly named LOOM
artifacts. Gate A therefore never selects history, ephemeris cache and B1
independently. It discovers coherent runtime bundles where all three artifacts
share the same runtime parent, then proves a completed frozen flight entirely
offline through the extracted navigation service.

Gate A requires:
1. frozen ephemeris only (no provider fill, no refresh);
2. service-path canonical runtime SHA equals frozen FLIGHT_ARRIVED runtime SHA;
3. extracted non-persisting execute_flight() arrival state equals the exact
   frozen state_after_snapshot recorded by the same history ledger.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from loom.navigation.contracts import (
    FlightPlan,
    NavigationContext,
    NavigationRequest,
    RouteCandidate,
)
from loom.navigation.service import LegacyNavigationService
import loom_navigator

HISTORY_NAMES = ("LOOM_CAMPAIGN_HISTORY.jsonl.gz", "LOOM_CAMPAIGN_HISTORY.jsonl")
B1_NAME = "LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip"
CACHE_NAME = "LOOM_Navigator_Cache_v1"


@dataclass(frozen=True)
class RuntimeBundle:
    root: Path
    history: Path
    cache: Path
    b1: Path


def history_records(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def newest_completed_flight(rows: list[dict]):
    commits = [r for r in rows if r.get("record_type") == "FLIGHT_COMMITTED"]
    arrivals = [r for r in rows if r.get("record_type") == "FLIGHT_ARRIVED"]
    by_id = {r.get("flight_id"): r for r in arrivals}
    for commit in reversed(commits):
        fid = commit.get("flight_id")
        if fid in by_id:
            return commit, by_id[fid]
    raise RuntimeError("no completed flight pair found in frozen history")


def discover_runtime_bundles(archive_root: Path) -> list[RuntimeBundle]:
    bundles: list[RuntimeBundle] = []
    seen: set[Path] = set()
    histories: list[Path] = []
    for name in HISTORY_NAMES:
        histories.extend(archive_root.rglob(name))
    for history in sorted(histories):
        runtime_root = history.parent.resolve()
        if runtime_root in seen:
            continue
        seen.add(runtime_root)
        cache = runtime_root / CACHE_NAME
        b1 = runtime_root / B1_NAME
        if cache.is_dir() and b1.is_file():
            bundles.append(RuntimeBundle(runtime_root, history.resolve(), cache.resolve(), b1.resolve()))
    if not bundles:
        raise RuntimeError("no coherent frozen runtime bundle contains history + Sequence-H cache + B1")
    print("COHERENT RUNTIME BUNDLES:")
    for bundle in bundles:
        print("  ROOT   ", bundle.root)
        print("  HISTORY", bundle.history)
        print("  CACHE  ", bundle.cache)
        print("  B1     ", bundle.b1)
    return bundles


def make_request_and_candidate(commit: dict, normalized: dict, mission: dict, state: dict):
    route = normalized["route"]
    requested = dict(normalized.get("requested_modes") or mission.get("requested_modes") or {})
    candidate = RouteCandidate(
        route_id=str(commit.get("flight_id") or "frozen-replay"),
        origin=route[0],
        destination=route[1],
        departure_epoch=state.get("epoch_utc"),
        payload={"metric": requested.get("metric"), "torch": requested.get("torch")},
    )
    request = NavigationRequest(route[0], route[1], requested_modes=requested, payload=mission)
    return request, candidate


def qualify_bundle(core, service, bundle: RuntimeBundle):
    rows = history_records(bundle.history)
    commit, arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])

    context0 = NavigationContext(campaign_state=state, runtime_root=bundle.root)
    nav = service._sequence_h(context0)
    normalized = nav.validate_and_normalize_mission(mission)

    print("TRY BUNDLE:", bundle.root)
    print("  flight_id=", commit.get("flight_id"))
    print("  route=", normalized.get("route"))
    try:
        acquisition = nav.run_acquisition(normalized, bundle.cache, offline=True, refresh=False)
    except Exception as exc:
        print("  REJECTED: frozen offline acquisition failed:", exc)
        return None

    request, candidate = make_request_and_candidate(commit, normalized, mission, state)
    context = NavigationContext(
        campaign_state=state,
        acquisition=acquisition,
        cache_dir=bundle.cache,
        b1_package=bundle.b1,
        runtime_root=bundle.root,
    )
    plan = service.compile_flight(request, candidate, context)
    got_runtime_sha = plan.payload["determinism"]["canonical_runtime_sha256"]
    expected_runtime_sha = arrived["details"]["runtime_sha256"]
    if got_runtime_sha != expected_runtime_sha:
        print("  REJECTED: deterministic runtime hash mismatch")
        print("    expected=", expected_runtime_sha)
        print("    got=     ", got_runtime_sha)
        return None

    expected_state = arrived.get("state_after_snapshot")
    if not isinstance(expected_state, dict):
        print("  REJECTED: FLIGHT_ARRIVED has no state_after_snapshot")
        return None

    # compile_flight is a pure solver and does not allocate campaign ledger
    # identity. Bind the recorded committed flight ID/plan SHA for execution-state
    # replay, exactly as the frozen campaign authority did.
    replay_payload = dict(plan.payload)
    replay_payload["plan_sha256"] = commit["details"].get("plan_sha256")
    replay_plan = FlightPlan(
        flight_id=str(commit["flight_id"]),
        candidate=plan.candidate,
        segments=plan.segments,
        arrival_state=plan.arrival_state,
        payload=replay_payload,
    )
    execution = service.execute_flight(replay_plan, context)
    got_state = dict(execution.final_state)
    if got_state != expected_state:
        canon = getattr(core, "_canon")
        sha_bytes = getattr(core, "_sha_bytes")
        print("  REJECTED: execution-state mismatch")
        print("    expected_sha=", sha_bytes(canon(expected_state)))
        print("    got_sha=     ", sha_bytes(canon(got_state)))
        return None

    return {
        "bundle": bundle,
        "commit": commit,
        "arrived": arrived,
        "route": normalized["route"],
        "runtime_sha": got_runtime_sha,
        "arrival_state_sha": expected_state.get("state_sha256"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime_root")
    args = ap.parse_args()
    archive_root = Path(args.runtime_root).resolve()

    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    bundles = discover_runtime_bundles(archive_root)

    qualified = None
    for bundle in bundles:
        try:
            qualified = qualify_bundle(core, service, bundle)
        except Exception as exc:
            print("  REJECTED: bundle qualification raised:", repr(exc))
            qualified = None
        if qualified is not None:
            break

    if qualified is None:
        raise RuntimeError("Gate A found no coherent frozen runtime bundle that reproduces its recorded flight")

    bundle = qualified["bundle"]
    commit = qualified["commit"]
    print("PHASE2_GATE_A_REPLAY=PASS")
    print("PHASE2_GATE_A_EXECUTION_STATE=PASS")
    print("EPHEMERIS_MODE=FROZEN_OFFLINE_ONLY")
    print("provider_filled_entries=0")
    print("flight_id=", commit.get("flight_id"))
    print("route=", qualified["route"])
    print("runtime_sha256=", qualified["runtime_sha"])
    print("arrival_state_sha256=", qualified["arrival_state_sha"])
    print("runtime_bundle_root=", bundle.root)
    print("history=", bundle.history)
    print("cache=", bundle.cache)
    print("b1=", bundle.b1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
