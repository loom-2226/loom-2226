#!/usr/bin/env python3
from __future__ import annotations

"""Read-only E1 probe: resolve earned Ceres/Neptune epochs from Navigator SOURCE-010.

This exercises Navigator's own route-scoped acquisition, canonical dependency index,
axis qualification and route-row loader. It does not mutate campaign state or solve,
authorize, or execute a flight.
"""

import json
import sys
import tempfile
import time
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import loom_navigator_core as campaign
from src.loom_navigator_source010_state import NavigatorSource010StateResolver

DEPARTURE = "2226-08-22T01:32:00Z"
ARRIVAL = "2226-08-22T09:45:17.864616Z"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-e1-source010-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        cache = root / "cache"
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": "E1_SOURCE010_STATE_PROBE",
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "ship": "WAYFARER_BASELINE",
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
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

        canonical, axis_validation = nav.build_canonical_dependency_index(acquisition, cache)
        if axis_validation.get("status") != "PASS":
            raise RuntimeError(f"Navigator axis qualification failed: {axis_validation}")

        rr0 = {"request": "CERES", **nav.ROUTE_OBJECTS["CERES"]}
        rr1 = {"request": "NEPTUNE_SYSTEM", **nav.ROUTE_OBJECTS["NEPTUNE_SYSTEM"]}
        ceres_rows, ceres_deps = nav._route_rows_from_canonical(rr0, canonical, cache)
        neptune_rows, neptune_deps = nav._route_rows_from_canonical(rr1, canonical, cache)
        consumed_ids = {d["id"] for d in ceres_deps + neptune_deps}
        if consumed_ids != required_ids:
            raise RuntimeError(f"unexpected route-row dependencies: {sorted(consumed_ids)}")

        resolver = NavigatorSource010StateResolver(
            route_rows={"CERES": ceres_rows, "NEPTUNE": neptune_rows},
            time_axis=canonical["time_axis"],
            axis_qualification=axis_validation["status"],
            source_authority=acquisition["authority"]["source"],
        )
        states = [
            resolver.resolve("CERES", DEPARTURE),
            resolver.resolve("NEPTUNE", ARRIVAL),
        ]
        result = {
            "schema": "LOOM_E1_SOURCE010_STATE_PROBE_V1",
            "status": "PASS",
            "route": normalized["route"],
            "earned_departure_epoch_utc": DEPARTURE,
            "earned_arrival_epoch_utc": ARRIVAL,
            "source_authority": acquisition["authority"]["source"],
            "axis_qualification": axis_validation["status"],
            "acquisition_dependency_ids": sorted(required_ids),
            "request_count": len(route_plan),
            "cache_hits": hits,
            "fetched": fetched,
            "states": [
                {
                    "entity_id": s.entity_id,
                    "epoch_utc": s.epoch_utc,
                    "position_km": list(s.position_km),
                    "velocity_km_s": list(s.velocity_km_s),
                    "reference_frame": s.reference_frame,
                    "navigation_grade": s.navigation_grade,
                    "provenance": dict(s.provenance),
                }
                for s in states
            ],
            "next_action": "CONNECT_E1_ROUTE_SAMPLES_TO_DOMAIN_HYDRATION",
            "authority_note": "READ_ONLY_NO_CAMPAIGN_MUTATION_NO_FLIGHT_EXECUTION_LLM_AUTHORITY_ZERO",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
