#!/usr/bin/env python3
"""Phase-2 Gate A qualifier against a frozen Pixel runtime archive.

The qualifier never invents a mission. It locates the frozen campaign history,
selects the newest completed flight, reconstructs its replay request and
campaign departure state, then reruns the deterministic solve through the new
LegacyNavigationService facade. Preserved content-addressed ephemeris cache
entries are authoritative and never refreshed; if the archive omitted an entry,
GitHub may fill only the missing request from the same authoritative provider.
The resulting canonical runtime SHA must equal the SHA recorded by the frozen
FLIGHT_ARRIVED ledger entry.
"""
from __future__ import annotations

import argparse, gzip, json, re, sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from loom.navigation.contracts import NavigationContext, NavigationRequest, RouteCandidate
from loom.navigation.service import LegacyNavigationService
import loom_navigator

HEX64 = re.compile(r"^[0-9a-fA-F]{64}(?:\..+)?$")


def find_one(root: Path, names: tuple[str, ...]) -> Path:
    for name in names:
        hits = list(root.rglob(name))
        if hits:
            return hits[0]
    raise RuntimeError(f"missing required runtime artifact: {names}")


def find_sequence_h_cache(root: Path) -> Path:
    named = [p for p in root.rglob("LOOM_Navigator_Cache_v1") if p.is_dir()]
    if named:
        scored = []
        for cache in named:
            n = sum(1 for p in cache.rglob("*") if p.is_file() and HEX64.match(p.name))
            scored.append((n, cache))
        scored.sort(reverse=True, key=lambda item: item[0])
        for n, cache in scored:
            print(f"CACHE ROOT CANDIDATE: {n:5d}  {cache}")
        if scored[0][0] > 0:
            print("SELECTED CACHE ROOT:", scored[0][1])
            return scored[0][1]
    roots: Counter[Path] = Counter()
    for p in root.rglob("*"):
        if not (p.is_file() and HEX64.match(p.name)):
            continue
        parts = p.parts
        if "ephemeris" in parts:
            i = parts.index("ephemeris")
            if i > 0:
                roots[Path(*parts[:i])] += 1
    if not roots:
        raise RuntimeError("no content-addressed Sequence-H cache found in frozen runtime")
    cache, count = roots.most_common(1)[0]
    print("INFERRED CACHE ROOT:", cache, "entries=", count)
    return cache


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


def acquisition_with_missing_fill(nav, normalized, cache: Path):
    before = {p.resolve() for p in cache.rglob("*") if p.is_file()}
    try:
        acq = nav.run_acquisition(normalized, cache, offline=True, refresh=False)
        print("EPHEMERIS ACQUISITION: frozen cache complete")
        return acq, []
    except Exception as exc:
        if "offline cache miss" not in str(exc):
            raise
        print("EPHEMERIS ACQUISITION: frozen cache incomplete")
        print("FIRST CACHE MISS:", exc)
        print("FILL POLICY: provider access enabled, refresh=False; preserved entries are not replaced")
        acq = nav.run_acquisition(normalized, cache, offline=False, refresh=False)
        after = {p.resolve() for p in cache.rglob("*") if p.is_file()}
        added = sorted(after - before)
        print("CACHE ENTRIES ADDED:", len(added))
        for p in added:
            print("  +", p.relative_to(cache))
        return acq, added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("runtime_root")
    args = ap.parse_args()
    root = Path(args.runtime_root).resolve()

    hist = find_one(root, ("LOOM_CAMPAIGN_HISTORY.jsonl.gz", "LOOM_CAMPAIGN_HISTORY.jsonl"))
    b1 = find_one(root, ("LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip",))
    cache = find_sequence_h_cache(root)
    rows = history_records(hist)
    commit, arrived = newest_completed_flight(rows)
    replay = commit["details"]["replay"]
    mission = dict(replay["mission_request"])
    state = dict(replay["departure_state_snapshot"])

    core = loom_navigator.load_core()
    service = LegacyNavigationService(core)
    nav = service._sequence_h(NavigationContext(campaign_state=state, runtime_root=root))

    normalized = nav.validate_and_normalize_mission(mission)
    acquisition, added = acquisition_with_missing_fill(nav, normalized, cache)

    route = normalized["route"]
    requested = dict(normalized.get("requested_modes") or mission.get("requested_modes") or {})
    candidate = RouteCandidate(
        route_id=str(commit.get("flight_id") or "frozen-replay"),
        origin=route[0], destination=route[1],
        departure_epoch=state.get("epoch_utc"),
        payload={"metric": requested.get("metric"), "torch": requested.get("torch")},
    )
    req = NavigationRequest(route[0], route[1], requested_modes=requested, payload=mission)
    ctx = NavigationContext(
        campaign_state=state, acquisition=acquisition, cache_dir=cache,
        b1_package=b1, runtime_root=root,
    )
    plan = service.compile_flight(req, candidate, ctx)
    got = plan.payload["determinism"]["canonical_runtime_sha256"]
    expected = arrived["details"]["runtime_sha256"]
    if got != expected:
        raise RuntimeError(f"Gate A runtime hash mismatch: expected={expected} got={got}; filled_entries={len(added)}")

    print("PHASE2_GATE_A_REPLAY=PASS")
    print("flight_id=", commit.get("flight_id"))
    print("route=", route)
    print("runtime_sha256=", got)
    print("provider_filled_entries=", len(added))
    print("history=", hist)
    print("cache=", cache)
    print("b1=", b1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
