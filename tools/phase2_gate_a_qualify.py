#!/usr/bin/env python3
"""Phase-2 Gate A qualifier against a frozen Pixel runtime archive.

The qualifier never invents a mission. It locates the frozen campaign history,
selects the newest completed flight, reconstructs its replay request and
campaign departure state, then reruns the deterministic solve through the new
LegacyNavigationService facade. The resulting canonical runtime SHA must equal
the SHA recorded by the frozen FLIGHT_ARRIVED ledger entry.
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
    """Find the preserved content-addressed Sequence-H cache, not any generic cache dir."""
    counts: Counter[Path] = Counter()
    for p in root.rglob("*"):
        if p.is_file() and HEX64.match(p.name):
            counts[p.parent] += 1
    if not counts:
        raise RuntimeError("no content-addressed Sequence-H cache found in frozen runtime")
    ranked = counts.most_common()
    cache, count = ranked[0]
    print("CACHE CANDIDATES:")
    for path, n in ranked[:10]:
        print(f"  {n:5d}  {path}")
    print("SELECTED CACHE:", cache, "entries=", count)
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
    acquisition = nav.run_acquisition(normalized, cache, offline=True, refresh=False)

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
        raise RuntimeError(f"Gate A runtime hash mismatch: expected={expected} got={got}")

    print("PHASE2_GATE_A_REPLAY=PASS")
    print("flight_id=", commit.get("flight_id"))
    print("route=", route)
    print("runtime_sha256=", got)
    print("history=", hist)
    print("cache=", cache)
    print("b1=", b1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
