#!/usr/bin/env python3
from __future__ import annotations

"""Experience One E1.0 Spike A — deterministic multi-route feasibility harness.

This is bounded spike code. It must not mutate campaign state and it must not be
promoted into production merely because it works.

The harness reuses the preserved Navigator authority in ``src/loom_navigator_core.py``
and its embedded, hash-verified Sequence H core. It requires an existing LOOM phone/runtime
root containing the campaign state, locked B1 package and ephemeris cache. It does not call
the campaign setup or flight-commit paths.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from typing import Any, Iterable

CAMPAIGN_FILES = (
    "LOOM_STATE_V1.json",
    "LOOM_STATE_V1.bak",
    "LOOM_CAMPAIGN_HISTORY.jsonl.gz",
)
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_REPO = SCRIPT_PATH.parents[3]
ANDROID_ROOT = Path("/storage/emulated/0/Download")
DEFAULT_ROOT = ANDROID_ROOT if ANDROID_ROOT.exists() else Path.cwd()


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def campaign_hashes(root: Path) -> dict[str, str | None]:
    return {name: sha256_file(root / name) for name in CAMPAIGN_FILES}


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate_public_view(candidate: dict[str, Any]) -> dict[str, Any]:
    """Reduce a raw candidate to stable spike evidence fields."""
    fields = (
        "metric", "torch", "total_s", "remass_used_t", "arrival_remass_t",
        "thermal", "arrival_epoch_utc", "delta_v_km_s", "metric_distance_km",
        "metric_duration_s", "metric_beta_c", "metric_effective_speed_km_s",
        "ordinary_departure_speed_km_s", "torch_burn_s", "ve_km_s",
        "jet_power_TW", "thrust_MN", "mdot_kg_s", "initial_accel_g",
        "final_accel_g", "balanced_policy_score",
    )
    return {k: candidate[k] for k in fields if k in candidate}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def materially_distinct(candidates: Iterable[dict[str, Any]]) -> bool:
    return len({(c.get("metric"), c.get("torch")) for c in candidates}) >= 2


def build_mission(wrapper: Any, nav: Any, state: dict[str, Any], origin: str, destination: str,
                  metric: str = "FAST", torch: str = "CRUISE", test_id: str = "E1-0-SPIKE-A") -> dict[str, Any]:
    local_text = wrapper._melbourne_local_for_utc(nav, state["epoch_utc"])
    mission = {
        "schema": "LOOM_NAV_REQUEST_v1",
        "test_id": test_id,
        "epoch": {"local": local_text, "timezone": "Australia/Melbourne"},
        "route": [origin, destination],
        "ship": "WAYFARER_BASELINE",
        "requested_modes": {"metric": metric, "torch": torch},
        "notes": "Experience One E1.0 Spike A; read-only deterministic candidate enumeration.",
    }
    normalized = nav.validate_and_normalize_mission(mission)
    normalized["_campaign_initial_state"] = {
        "state_id": state["state_id"],
        "state_sha256": state["state_sha256"],
        "wet_mass_t": state["ship"]["wet_mass_t"],
        "remass_t": state["ship"]["remass_t"],
    }
    return normalized


def validate_candidate(nav: Any, wrapper: Any, state: dict[str, Any], acq: Any, cache: Path,
                       b1: Path, origin: str, destination: str, candidate: dict[str, Any], index: int) -> dict[str, Any]:
    normalized = build_mission(
        wrapper, nav, state, origin, destination,
        metric=str(candidate["metric"]), torch=str(candidate["torch"]),
        test_id=f"E1-0-SPIKE-A-CAND-{index:02d}",
    )
    runtime, _payloads, _html, validation, det = nav.target_determinism_gate(normalized, acq, cache, b1)
    leg = runtime["flight"]["legs"][-1]
    actual = (leg["metric_mode"], leg["torch_mode"])
    expected = (candidate["metric"], candidate["torch"])
    if actual != expected:
        raise RuntimeError(f"candidate validation mode mismatch: expected={expected}, actual={actual}")
    return {
        "metric": candidate["metric"],
        "torch": candidate["torch"],
        "canonical_runtime_sha256": det.get("canonical_runtime_sha256"),
        "solver_model": leg.get("solver_model"),
        "solver_version": leg.get("solver_version"),
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                   help=f"Existing LOOM runtime root (default: {DEFAULT_ROOT})")
    p.add_argument("--repo", type=Path, default=DEFAULT_REPO,
                   help=f"LOOM repository checkout root (default: {DEFAULT_REPO})")
    p.add_argument("--origin", default="CERES")
    p.add_argument("--destination", default="NEPTUNE_SYSTEM")
    p.add_argument("--priority", default="BALANCED", choices=("FASTEST", "REMASS", "CONSERVATIVE", "BALANCED"))
    p.add_argument("--allow-online-acquisition", action="store_true",
                   help="Allow existing Navigator acquisition to fill missing cache data; campaign state still must remain unchanged")
    p.add_argument("--max-validate", type=int, default=8,
                   help="Maximum ranked candidates to independently pass through target_determinism_gate")
    p.add_argument("--out", type=Path, default=None,
                   help="Evidence JSON path (default: <root>/E1_0_SPIKE_A_MULTIROUTE_RESULT.json)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    repo = args.repo.expanduser().resolve()
    out = args.out.expanduser().resolve() if args.out else root / "E1_0_SPIKE_A_MULTIROUTE_RESULT.json"
    wrapper_path = repo / "src" / "loom_navigator_core.py"
    state_path = root / "LOOM_STATE_V1.json"
    if not wrapper_path.exists():
        raise SystemExit(f"Navigator wrapper not found: {wrapper_path}")
    if not state_path.exists():
        raise SystemExit(f"Existing campaign state required; refusing to create one: {state_path}")

    before = campaign_hashes(root)
    wrapper = load_module(wrapper_path, "loom_e1_spike_a_wrapper")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    wrapper._validate_state(state)
    cache = root / "LOOM_Navigator_Cache_v1"

    with tempfile.TemporaryDirectory(prefix="loom_e1_spike_a_core_") as td:
        nav = wrapper._load_core(Path(td))
        b1 = nav.find_b1_package(root, nav.EXPECTED_B1_PACKAGE)
        if not b1 or not b1.exists():
            raise SystemExit("Locked B1 package not found in supplied runtime root")
        nav.validate_b1_package(b1)

        origin = wrapper._resolve_dest(args.origin)
        destination = wrapper._resolve_dest(args.destination)
        if origin == destination:
            raise SystemExit("origin equals destination")

        normalized = build_mission(wrapper, nav, state, origin, destination)
        acq = nav.run_acquisition(normalized, cache, offline=not args.allow_online_acquisition, refresh=False)
        first_raw = wrapper._candidate_plans(nav, normalized, acq, cache, state, args.priority)
        second_raw = wrapper._candidate_plans(nav, normalized, acq, cache, state, args.priority)
        first = [candidate_public_view(c) for c in first_raw]
        second = [candidate_public_view(c) for c in second_raw]
        first_fp = fingerprint(first)
        second_fp = fingerprint(second)
        deterministic_rerun = first == second and first_fp == second_fp
        distinct = materially_distinct(first)

        validations = [
            validate_candidate(nav, wrapper, state, acq, cache, b1, origin, destination, candidate, i)
            for i, candidate in enumerate(first_raw[: max(0, args.max_validate)], 1)
        ]

    after = campaign_hashes(root)
    campaign_unchanged = before == after
    result = {
        "schema": "LOOM_E1_0_SPIKE_A_MULTIROUTE_RESULT_V1",
        "authority": "SPIKE_EVIDENCE_ONLY_NON_PRODUCTION",
        "repo_wrapper": str(wrapper_path),
        "wrapper_core_sha256": getattr(wrapper, "CORE_SHA", None),
        "root": str(root),
        "state_id": state.get("state_id"),
        "state_sha256": state.get("state_sha256"),
        "epoch_utc": state.get("epoch_utc"),
        "origin": origin,
        "destination": destination,
        "priority": args.priority,
        "acquisition_mode": "ONLINE_ALLOWED_REFRESH_FALSE" if args.allow_online_acquisition else "OFFLINE_CACHE_ONLY",
        "candidate_count": len(first),
        "materially_distinct_metric_torch_pairs": distinct,
        "candidate_fingerprint_run_1": first_fp,
        "candidate_fingerprint_run_2": second_fp,
        "deterministic_rerun_exact": deterministic_rerun,
        "independently_validated_count": len(validations),
        "candidates": first,
        "candidate_validations": validations,
        "campaign_hashes_before": before,
        "campaign_hashes_after": after,
        "campaign_files_unchanged": campaign_unchanged,
        "spike_pass_conditions": {
            "at_least_two_candidates": len(first) >= 2,
            "materially_distinct_candidates": distinct,
            "deterministic_rerun": deterministic_rerun,
            "all_emitted_candidates_validated": len(validations) == min(len(first), max(0, args.max_validate)),
            "campaign_state_unchanged": campaign_unchanged,
        },
    }
    result["spike_observation_pass"] = all(result["spike_pass_conditions"].values())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"\nEVIDENCE WRITTEN: {out}")

    if not campaign_unchanged:
        raise SystemExit("FAIL CLOSED: campaign files changed during read-only Spike A")
    if len(first) < 2 or not distinct or not deterministic_rerun:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
