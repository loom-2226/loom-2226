#!/usr/bin/env python3
from __future__ import annotations

"""Validated Pixel entrypoint for the E1 forced-collapse-radius experiment.

The original experiment logic remains in e1_forced_collapse_radius_experiment.py.
This entrypoint exists because Navigator constrains mission test_id length; it uses a
qualified short test id while preserving the exact diagnostic solver path.
"""

import json
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import loom_navigator_core as campaign
from engineering.experience_one.qualification import e1_forced_collapse_radius_experiment as exp

TEST_ID = "E1_FORCED_RADIUS_EXPERIMENT"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="loom-e1-forced-radius-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": TEST_ID,
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "ship": "WAYFARER_BASELINE",
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
        cache = root / "cache"
        acquisition, required_ids = exp._route_scoped_acquisition(nav, normalized, cache)
        canonical, axis_validation = nav.build_canonical_dependency_index(acquisition, cache)
        if axis_validation.get("status") != "PASS":
            raise RuntimeError(f"canonical axis qualification failed: {axis_validation}")

        origin, dest = normalized["route"]
        rr0 = {"request": origin, **nav.ROUTE_OBJECTS[origin]}
        rr1 = {"request": dest, **nav.ROUTE_OBJECTS[dest]}
        rows0, _ = nav._route_rows_from_canonical(rr0, canonical, cache)
        rows1, _ = nav._route_rows_from_canonical(rr1, canonical, cache)
        departure = nav._dt(normalized["epoch_utc"])
        state = campaign._new_state("E1-FORCED-RADIUS", "WAYFARER-E1")
        wet = float(state["ship"]["wet_mass_t"])

        baseline = nav._solve_leg(origin, dest, departure, rows0, rows1, canonical["time_axis"], "HARD", "CRUISE", wet)
        collapse_epoch = nav._dt(baseline["metric_segment"]["collapse_epoch_utc"])
        center = nav._pos_km(nav._state_primary(rows1, collapse_epoch, canonical["time_axis"]))
        baseline_radius = nav._vnorm(nav._vsub(baseline["metric_segment"]["collapse_position_km_j2000_ecliptic"], center))
        axis_limit_s = exp._axis_limit_seconds(nav, canonical["time_axis"], rows1, departure)

        cases = []
        for candidate in exp.candidate_neptune_radii_km():
            case = exp.forced_radius_case(
                nav,
                departure,
                rows0,
                rows1,
                canonical["time_axis"],
                "HARD",
                "CRUISE",
                wet,
                float(candidate["radius_km"]),
            )
            cases.append({**candidate, **case})

        result = {
            "schema": "LOOM_E1_FORCED_COLLAPSE_RADIUS_EXPERIMENT_V1",
            "status": "PASS",
            "route": normalized["route"],
            "test_id": normalized["test_id"],
            "source_authority": acquisition["authority"]["source"],
            "axis_qualification": axis_validation["status"],
            "acquisition_dependency_ids": sorted(required_ids),
            "model": "NAV-V1-A_DIAGNOSTIC_EXTENSION_COAST_THEN_EXISTING_TERMINAL_BURN",
            "model_note": "No runtime physics mutation. Coast extension preserves NAV-V1-A ordinary velocity memory and existing terminal burn; candidate radii are diagnostic only.",
            "source010_axis_seconds_after_departure": axis_limit_s,
            "baseline": {
                "collapse_radius_km": baseline_radius,
                "collapse_epoch_utc": baseline["metric_segment"]["collapse_epoch_utc"],
                "arrival_epoch_utc": baseline["arrival"]["epoch_utc"],
                "arrival_matches_earned_e1": baseline["arrival"]["epoch_utc"] == exp.EARNED_ARRIVAL,
                "ordinary_local_duration_s": baseline["terminal_burn"]["burn_s"],
                "delta_v_km_s": baseline["terminal_burn"]["delta_v_km_s"],
                "remass_used_t": baseline["terminal_burn"]["remass_used_t"],
            },
            "candidate_radii_provenance": "DIAGNOSTIC_STANDARD_HILL_LAPLACE_FORMULAE_NOT_RUNTIME_AUTHORITY_NOT_ADOPTED_POLICY",
            "cases": cases,
            "authority_note": "READ_ONLY_DIAGNOSTIC_NO_CAMPAIGN_MUTATION_NO_RUNTIME_POLICY_CHANGE_LLM_AUTHORITY_ZERO",
            "next_action": "INTERPRET_RADIUS_FEASIBILITY_BEFORE_ANY_METRIC_DOMAIN_POLICY_ADOPTION",
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
