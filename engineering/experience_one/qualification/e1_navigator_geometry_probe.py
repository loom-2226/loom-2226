#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 probe for spatial geometry actually exposed by Navigator.

The purpose is discovery, not route invention. This runs the real Ceres→Neptune
candidate path against Navigator SOURCE-010 and inventories the selected solved-leg
payload for explicit spatial state and, separately, any explicit metric occupancy
path. A collapse state is not treated as a trajectory. If Navigator says metric
transit is relational displacement rather than ordinary-space occupancy, the probe
preserves that semantic boundary and does not synthesize a straight line.
"""

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import loom_navigator_core as campaign

DEPARTURE = "2226-08-22T01:32:00Z"
EARNED_ARRIVAL = "2226-08-22T09:45:17.864616Z"

_SPATIAL_TERMS = (
    "position",
    "velocity",
    "trajectory",
    "path",
    "sample",
    "state_vector",
    "collapse_point",
    "collapse_state",
    "coordinate",
)
_OCCUPANCY_TERMS = ("trajectory", "path", "sample")
_PHYSICS_SCALAR_TERMS = (
    "distance",
    "duration",
    "beta",
    "delta_v",
    "speed",
    "accel",
    "burn",
    "remass",
    "mass",
    "power",
    "thrust",
)
_TEMPORAL_TERMS = ("epoch", "time")


def _walk(value: Any, path: str = ""):
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{path}.{key}" if path else str(key)
            yield child, value[key]
            yield from _walk(value[key], child)
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            child = f"{path}[{index}]"
            yield child, item
            yield from _walk(item, child)


def inventory_leg_geometry(leg: dict[str, Any]) -> dict[str, Any]:
    """Inventory explicit spatial state separately from metric occupancy geometry."""
    explicit: list[str] = []
    occupancy: list[str] = []
    physics: list[str] = []
    temporal: list[str] = []
    for path, value in _walk(leg):
        leaf = path.rsplit(".", 1)[-1].lower()
        leaf = leaf.split("[", 1)[0]
        if any(term in leaf for term in _SPATIAL_TERMS):
            explicit.append(path)
        if path.startswith("metric_segment.") and any(term in leaf for term in _OCCUPANCY_TERMS):
            occupancy.append(path)
        if not isinstance(value, (dict, list, tuple)) and any(term in leaf for term in _PHYSICS_SCALAR_TERMS):
            physics.append(path)
        if not isinstance(value, (dict, list, tuple)) and any(term in leaf for term in _TEMPORAL_TERMS):
            temporal.append(path)
    semantics = str((leg.get("metric_segment") or {}).get("semantics") or "")
    return {
        "top_level_keys": sorted(leg),
        "explicit_spatial_state_present": bool(explicit),
        "explicit_spatial_paths": sorted(set(explicit)),
        "metric_occupancy_path_present": bool(occupancy),
        "metric_occupancy_paths": sorted(set(occupancy)),
        "metric_segment_semantics": semantics,
        "physics_scalar_paths": sorted(set(physics)),
        "temporal_paths": sorted(set(temporal)),
    }


def _route_scoped_acquisition(nav: Any, normalized: dict[str, Any], cache: Path) -> tuple[dict[str, Any], set[str]]:
    _, _, trace = nav.acquisition_window(normalized)
    full_plan = nav.build_acquisition_plan(normalized)
    required_ids = {nav.ROUTE_OBJECTS[token]["base_id"] for token in normalized["route"]}
    if required_ids != {"CE", "NE"}:
        raise RuntimeError(f"unexpected E1 base dependencies: {sorted(required_ids)}")
    route_plan = [
        item for item in full_plan
        if item["scope"] == "BASE" and item["id"] in required_ids
    ]
    if {item["id"] for item in route_plan} != required_ids:
        raise RuntimeError("Navigator acquisition plan did not expose both E1 base dependencies")

    session = nav.build_session()
    entries = []
    hits = fetched = total_cache = total_raw = 0
    t0 = time.perf_counter()
    for item in route_plan:
        req = item["request"]
        r = nav.fetch_or_cache(req, cache, session, offline=False, refresh=False)
        hits += int(r["status"] == "CACHE_HIT")
        fetched += int(r["status"] == "FETCHED")
        total_cache += int(r.get("cache_bytes", 0))
        total_raw += int(r.get("raw_archive_bytes", 0))
        entries.append({
            **{k: v for k, v in item.items() if k != "request"},
            "request": req.canonical(),
            **r,
        })

    acquisition = {
        "schema": "LOOM_NAV_EPHEMERIS_ACQUISITION_INDEX_v1",
        "workflow_version": nav.WORKFLOW_VERSION,
        "test_id": normalized["test_id"],
        "epoch_utc": normalized["epoch_utc"],
        "policy": nav.EPHEMERIS_POLICY,
        "window_trace": trace,
        "request_count": len(route_plan),
        "cache_hits": hits,
        "fetched": fetched,
        "direct_unavailable": 0,
        "cache_bytes_touched": total_cache,
        "raw_archive_bytes_written": total_raw,
        "elapsed_seconds": round(time.perf_counter() - t0, 6),
        "entries": entries,
        "authority": {
            "source": "SOURCE-010",
            "derived_scientific_values_in_cache": False,
            "llm_calculation_authority": "ZERO",
        },
    }
    return acquisition, required_ids


def _next_action(inventory: dict[str, Any]) -> str:
    if inventory["metric_occupancy_path_present"]:
        return "PROMOTE_EXPLICIT_NAVIGATOR_METRIC_OCCUPANCY_SAMPLES_TO_HYDRATION"
    if inventory["metric_segment_semantics"] == "RELATIONAL_DISPLACEMENT_NOT_ORDINARY_SPACE_OCCUPANCY":
        return "PROMOTE_COLLAPSE_STATE_AND_REVIEW_METRIC_DOMAIN_CHECKER_SEMANTICS"
    if inventory["explicit_spatial_state_present"]:
        return "DEFINE_MINIMAL_NAVIGATOR_METRIC_OCCUPANCY_SEAM_OR_NON_OCCUPANCY_DOMAIN_RULE"
    return "DEFINE_MINIMAL_NAVIGATOR_SPATIAL_OUTPUT_SEAM_FROM_EXISTING_SOLVER_INTERNALS"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-e1-geometry-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        cache = root / "cache"
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": "E1_NAVIGATOR_GEOMETRY_PROBE",
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "ship": "WAYFARER_BASELINE",
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
        acquisition, required_ids = _route_scoped_acquisition(nav, normalized, cache)
        state = campaign._new_state("E1-GEOMETRY-PROBE", "WAYFARER-E1")
        candidates = campaign._candidate_plans(
            nav,
            normalized,
            acquisition,
            cache,
            state,
            "BALANCED",
        )
        if not candidates:
            raise RuntimeError("Navigator returned no E1 candidates")
        selected = candidates[0]
        leg = selected.get("leg")
        if not isinstance(leg, dict):
            raise RuntimeError("selected Navigator candidate has no solved leg payload")
        inventory = inventory_leg_geometry(leg)
        arrival = str(selected.get("arrival_epoch_utc") or leg.get("arrival", {}).get("epoch_utc") or "")
        result = {
            "schema": "LOOM_E1_NAVIGATOR_GEOMETRY_PROBE_V2",
            "status": "PASS",
            "authority_note": "READ_ONLY_NAVIGATOR_OUTPUT_INSPECTION_NO_ROUTE_INVENTION_NO_CAMPAIGN_MUTATION_LLM_AUTHORITY_ZERO",
            "source_authority": acquisition["authority"]["source"],
            "acquisition_dependency_ids": sorted(required_ids),
            "route": normalized["route"],
            "departure_epoch_utc": normalized["epoch_utc"],
            "earned_arrival_epoch_utc": EARNED_ARRIVAL,
            "selected_candidate": {
                "candidate_id": selected.get("candidate_id"),
                "metric_mode": selected.get("metric_mode") or leg.get("metric_mode"),
                "ordinary_mode": selected.get("ordinary_mode") or leg.get("torch_mode"),
                "total_duration_s": selected.get("total_duration_s", selected.get("total_s")),
                "total_remass_t": selected.get("total_remass_t", selected.get("remass_used_t")),
                "arrival_epoch_utc": arrival,
                "arrival_matches_earned_e1": arrival == EARNED_ARRIVAL,
            },
            "geometry_inventory": inventory,
            "solved_leg": leg,
            "next_action": _next_action(inventory),
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
