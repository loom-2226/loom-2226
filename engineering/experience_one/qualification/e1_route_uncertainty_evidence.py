#!/usr/bin/env python3
from __future__ import annotations

"""Qualify E1 route uncertainty from existing Navigator SOURCE-010 state lineage.

This module does not invent a numeric covariance or error bound. It qualifies the
existing navigation-grade SOURCE-010 uncertainty/provenance record as route-level
uncertainty evidence only when source, axis qualification, navigation grade and
uncertainty lineage are all explicit.
"""

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engineering.experience_one.qualification import e1_navigator_geometry_probe as nav_probe
from src import loom_navigator_core as campaign
from src.loom_navigator_source010_state import NavigatorSource010StateResolver

SCHEMA = "LOOM_E1_ROUTE_UNCERTAINTY_EVIDENCE_V1"
DEPARTURE = "2226-08-22T01:32:00Z"
ARRIVAL = "2226-08-22T09:45:17.864616Z"


def build_static_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "required": [
            "navigation_grade",
            "source_authority=SOURCE-010",
            "axis_qualification=PASS",
            "uncertainty_lineage",
        ],
        "evidence_class": "QUALITATIVE_NAVIGATION_GRADE_LINEAGE_UNCERTAINTY",
        "numeric_covariance_available": False,
        "numeric_covariance_claimed": False,
        "authority": {
            "creates_numeric_error_bound": False,
            "certifies_loom_coherence": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def classify_route_uncertainty(states: list[dict[str, Any]]) -> dict[str, Any]:
    invalid: set[str] = set()
    if not states:
        invalid.add("states")

    sources: set[str] = set()
    axes: set[str] = set()
    interpolations: set[str] = set()
    qualifications: set[str] = set()

    for state in states:
        if state.get("navigation_grade") is not True:
            invalid.add("navigation_grade")
        provenance = state.get("provenance") or {}
        uncertainty = state.get("uncertainty") or {}
        source = str(provenance.get("source_authority") or "")
        axis = str(provenance.get("axis_qualification") or "")
        qualification = str(uncertainty.get("qualification") or "")
        if source != "SOURCE-010":
            invalid.add("source_authority")
        if axis.upper() != "PASS":
            invalid.add("axis_qualification")
        if qualification != "INHERITS_NAVIGATOR_SOURCE_010_AND_AXIS_QUALIFICATION":
            invalid.add("uncertainty_lineage")
        if source:
            sources.add(source)
        if axis:
            axes.add(axis)
        if qualification:
            qualifications.add(qualification)
        interpolation = provenance.get("interpolation")
        if interpolation:
            interpolations.add(str(interpolation))

    qualified = not invalid
    return {
        **build_static_contract(),
        "status": "PASS",
        "source_authority": "SOURCE-010" if sources == {"SOURCE-010"} else sorted(sources),
        "axis_qualification": "PASS" if {a.upper() for a in axes} == {"PASS"} else sorted(axes),
        "state_count": len(states),
        "interpolation_classes": sorted(interpolations),
        "uncertainty_qualifications": sorted(qualifications),
        "missing_or_invalid": sorted(invalid),
        "disposition": (
            "QUALIFIED_ROUTE_UNCERTAINTY_EVIDENCE"
            if qualified
            else "INDETERMINATE_NOT_CERTIFIABLE"
        ),
        "interpretation": (
            "SOURCE010_NAVIGATION_GRADE_LINEAGE_UNCERTAINTY_QUALIFIED_NO_NUMERIC_COVARIANCE_CLAIMED"
            if qualified
            else "ROUTE_UNCERTAINTY_LINEAGE_INCOMPLETE_OR_NOT_NAVIGATION_GRADE"
        ),
    }


def acquire_live_route_uncertainty() -> dict[str, Any]:
    """Resolve E1 endpoint states through qualified Navigator SOURCE-010 lineage."""
    with tempfile.TemporaryDirectory(prefix="loom-e1-route-uncertainty-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        cache = root / "cache"
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": "E1_ROUTE_UNCERTAINTY_EVIDENCE",
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ["CERES", "NEPTUNE_SYSTEM"],
            "ship": "WAYFARER_BASELINE",
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
        acquisition, required_ids = nav_probe._route_scoped_acquisition(nav, normalized, cache)
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
        resolved = [
            resolver.resolve("CERES", DEPARTURE),
            resolver.resolve("NEPTUNE", ARRIVAL),
        ]
        states = [
            {
                "entity_id": s.entity_id,
                "epoch_utc": s.epoch_utc,
                "navigation_grade": s.navigation_grade,
                "provenance": dict(s.provenance),
                "uncertainty": dict(s.uncertainty),
            }
            for s in resolved
        ]
        report = classify_route_uncertainty(states)
        report["states"] = states
        report["route"] = normalized["route"]
        report["acquisition_dependency_ids"] = sorted(required_ids)
        return report


def main() -> int:
    report = acquire_live_route_uncertainty()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
