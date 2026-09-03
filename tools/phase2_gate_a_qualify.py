#!/usr/bin/env python3
"""Phase-2 Gate A qualifier against a frozen Pixel runtime archive.

The qualifier never invents a mission. It locates the frozen campaign history,
selects the newest completed flight, reconstructs its replay request and
campaign departure state, then reruns the deterministic solve through the new
LegacyNavigationService facade.

When an archive contains duplicate Sequence-H cache roots, the qualifier selects
one by actual offline replay success, never by directory naming alone. Preserved
cache entries are never refreshed. Only if no frozen cache can satisfy the
recorded mission may the final candidate cache fill missing requests from the
same authoritative provider with refresh=False.

Gate A requires both:
1. the service-path canonical runtime SHA equals the frozen FLIGHT_ARRIVED SHA;
2. the extracted non-persisting execute_flight() arrival state equals the exact
   frozen state_after_snapshot recorded by the history ledger.
"""
from __future__ import annotations

import argparse, gzip, json, re, sys
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

HEX64 = re.compile(r"^[0-9a-fA-F]{64}(?:\..+)?$")


def find_one(root: Path, names: tuple[str, ...]) -> Path:
    for name in names:
        hits = list(root.rglob(name))
        if hits:
            return hits[0]
    raise RuntimeError(f"missing required runtime artifact: {names}")


def sequence_h_cache_candidates(root: Path) -> list[Path]:
    named = [p for p in root.rglob("LOOM_Navigator_Cache_v1") if p.is_dir()]
    scored: list[tuple[int, Path]] = []
    for cache in named:
        n = sum(1 for p in cache.rglob("*") if p.is_file() and HEX64.match(p.name))
        if n:
            scored.append((n, cache))
    scored.sort(key=lambda item: (-item[0], str(item[1])))
    if not scored:
        raise RuntimeError("no content-addressed Sequence-H cache found in frozen runtime")
    print("CACHE ROOT CANDIDATES:")
    for n, cache in scored:
        print(f"  {n:5d}  {cache}")
    return [cache for _, cache in scored]


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


def select_acquisition(nav, normalized, caches: list[Path]):
    """Prefer a cache that can replay the whole mission completely offline."""
    misses: list[tuple[Path, Exception]] = []
    for cache in caches:
        try:
            acq = nav.run_acquisition(normalized, cache, offline=True, refresh=False)
            print("SELECTED CACHE ROOT:", cache)
            print("EPHEMERIS ACQUISITION: frozen cache complete")
            return acq, cache, []
        except Exception as exc:
            if "offline cache miss" not in str(exc):
                raise
            misses.append((cache, exc))
            print("CACHE REJECTED (offline miss):", cache)
            print("  ", exc)

    # Conservative fallback for an incompletely archived cache: fill only missing
    # requests, never refresh any preserved entry. Gate A reports the exact count.
    cache, first_miss = misses[0]
    before = {p.resolve() for p in cache.rglob("*") if p.is_file()}
    print("NO FROZEN CACHE ROOT SATISFIED FULL REPLAY")
    print("FALLBACK CACHE:", cache)
    print("FIRST CACHE MISS:", first_miss)
    print("FILL POLICY: provider access enabled, refresh=False; preserved entries are not replaced")
    acq = nav.run_acquisition(normalized, cache, offline=False, refresh=False)
    after = {p.resolve() for p in cache.rglob("*") if p.is_file()}
    added = sorted(after - before)
    print("CACHE ENTRIES ADDED:", len(added))
    for p in added:
        print("  +", p.relative_to(cache))
    return acq, cache, added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime_root")
    args = ap.parse_args()
    root = Path(args.runtime_root).resolve()

    hist = find_one(root, ("LOOM_CAMPAIGN_HISTORY.jsonl.gz", "LOOM_CAMPAIGN_HISTORY.jsonl"))
    b1 = find_one(root, ("LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip",))
    caches = sequence_h_cache_candidates(root)
    rows = history_records(hist)
    commit, arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])

    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    base_context = NavigationContext(campaign_state=state, runtime_root=root)
    nav = service._sequence_h(base_context)

    normalized = nav.validate_and_normalize_mission(mission)
    acquisition, cache, added = select_acquisition(nav, normalized, caches)

    route = normalized["route"]
    requested = dict(normalized.get("requested_modes") or mission.get("requested_modes") or {})
    candidate = RouteCandidate(
        route_id=str(commit.get("flight_id") or "frozen-replay"),
        origin=route[0],
        destination=route[1],
        departure_epoch=state.get("epoch_utc"),
        payload={"metric": requested.get("metric"), "torch": requested.get("torch")},
    )
    req = NavigationRequest(route[0], route[1], requested_modes=requested, payload=mission)
    ctx = NavigationContext(
        campaign_state=state,
        acquisition=acquisition,
        cache_dir=cache,
        b1_package=b1,
        runtime_root=root,
    )

    plan = service.compile_flight(req, candidate, ctx)
    got_runtime_sha = plan.payload["determinism"]["canonical_runtime_sha256"]
    expected_runtime_sha = arrived["details"]["runtime_sha256"]
    if got_runtime_sha != expected_runtime_sha:
        raise RuntimeError(
            "Gate A runtime hash mismatch: "
            f"expected={expected_runtime_sha} got={got_runtime_sha}; filled_entries={len(added)}"
        )

    expected_state = arrived.get("state_after_snapshot")
    if not isinstance(expected_state, dict):
        raise RuntimeError("frozen FLIGHT_ARRIVED record has no state_after_snapshot")

    # Replay the frozen committed identity and plan hash. compile_flight is a pure
    # solver and does not allocate the campaign ledger's flight ID; that identity
    # belongs to the recorded FLIGHT_COMMITTED event.
    replay_payload = dict(plan.payload)
    replay_payload["plan_sha256"] = commit["details"].get("plan_sha256")
    replay_plan = FlightPlan(
        flight_id=str(commit["flight_id"]),
        candidate=plan.candidate,
        segments=plan.segments,
        arrival_state=plan.arrival_state,
        payload=replay_payload,
    )
    execution = service.execute_flight(replay_plan, ctx)
    got_state = dict(execution.final_state)
    if got_state != expected_state:
        canon = getattr(core, "_canon")
        sha_bytes = getattr(core, "_sha_bytes")
        raise RuntimeError(
            "Gate A execution-state mismatch: "
            f"expected_sha={sha_bytes(canon(expected_state))} got_sha={sha_bytes(canon(got_state))}"
        )

    print("PHASE2_GATE_A_REPLAY=PASS")
    print("PHASE2_GATE_A_EXECUTION_STATE=PASS")
    print("flight_id=", commit.get("flight_id"))
    print("route=", route)
    print("runtime_sha256=", got_runtime_sha)
    print("arrival_state_sha256=", expected_state.get("state_sha256"))
    print("provider_filled_entries=", len(added))
    print("history=", hist)
    print("cache=", cache)
    print("b1=", b1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
