#!/usr/bin/env python3
from __future__ import annotations

"""Governed loom-coherence acceptance classifier for the E1 Ceres->Neptune route.

This qualification is intentionally axis-local. It adapts the existing Navigator
solved-candidate payload into the minimum route evidence required by the compound
GA contract. It does not certify lattice coherence, endpoint/domain compatibility,
or overall GA admissibility, and it does not mutate campaign/runtime state.
"""

import argparse
import json
from typing import Any

from engineering.experience_one.qualification import e1_ga_evidence_adapter as adapter
from engineering.experience_one.qualification import e1_route_uncertainty_evidence as route_unc

SCHEMA = "LOOM_E1_ROUTE_COHERENCE_ACCEPTANCE_V1"
AXIS = "loom_coherence"


def _paths(payload: dict[str, Any]) -> list[str]:
    return adapter.inventory_payload(payload)["paths"]


def _matches(paths: list[str], groups: list[tuple[str, ...]]) -> list[str]:
    return adapter._any_matching(paths, groups)


def build_static_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "axis": AXIS,
        "required_evidence": [
            "route_identity_and_direction",
            "destination_state",
            "momentum_mapping_or_equivalent_velocity_state",
            "route_burden",
            "route_uncertainty",
            "source_provenance",
        ],
        "decision_rule": {
            "all_required_groups_present": "SATISFIED",
            "one_or_more_required_groups_missing": "INDETERMINATE_NOT_CERTIFIABLE",
            "missing_evidence_is_not_hard_fail": True,
            "no_cross_axis_compensation": True,
            "qualitative_lineage_uncertainty_requires_governed_qualification": True,
        },
        "authority": {
            "certifies_loom_coherence_only": True,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def classify_route_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    paths = _paths(payload)
    mission = payload.get("mission") or {}
    route = mission.get("route") or payload.get("normalized_route") or []
    candidate = payload.get("candidate") or {}
    source = payload.get("source_authority")

    route_identity = []
    if isinstance(route, list) and len(route) == 2:
        route_identity.append("mission.route")
    if candidate.get("candidate_id"):
        route_identity.append("candidate.candidate_id")

    destination = _matches(paths, [
        ("leg", "arrival"),
        ("leg", "collapse_position"),
        ("leg", "destination"),
    ])
    momentum = _matches(paths, [
        ("momentum_mapping",),
        ("ordinary_velocity_memory", "collapse_velocity"),
        ("leg", "velocity"),
    ])
    burden = _matches(paths, [
        ("candidate", "duration"),
        ("candidate", "remass"),
        ("leg", "distance"),
        ("leg", "beta"),
        ("leg", "duration"),
        ("leg", "remass"),
    ])

    generic_uncertainty_paths = [p for p in paths if not p.startswith("route_uncertainty")]
    uncertainty = _matches(generic_uncertainty_paths, [
        ("uncertainty",),
        ("sigma",),
        ("error",),
        ("confidence",),
    ])
    governed_uncertainty = payload.get("route_uncertainty") or {}
    if governed_uncertainty.get("disposition") == "QUALIFIED_ROUTE_UNCERTAINTY_EVIDENCE":
        uncertainty.extend([
            "route_uncertainty.disposition",
            "route_uncertainty.evidence_class",
            "route_uncertainty.source_authority",
        ])

    provenance = ["source_authority"] if source else []

    groups = {
        "route_identity_and_direction": route_identity,
        "destination_state": destination,
        "momentum_mapping_or_equivalent_velocity_state": momentum,
        "route_burden": burden,
        "route_uncertainty": uncertainty,
        "source_provenance": provenance,
    }
    missing = sorted(name for name, evidence in groups.items() if not evidence)
    satisfied = not missing

    return {
        **build_static_contract(),
        "status": "PASS",
        "route": route,
        "candidate_id": candidate.get("candidate_id"),
        "source_authority": source,
        "evidence": {name: sorted(set(values)) for name, values in groups.items()},
        "route_uncertainty_artifact_disposition": governed_uncertainty.get("disposition"),
        "missing_required_evidence": missing,
        "disposition": "SATISFIED" if satisfied else "INDETERMINATE_NOT_CERTIFIABLE",
        "hard_fail": False,
        "interpretation": (
            "LOOM_COHERENCE_ROUTE_EVIDENCE_SATISFIED_AXIS_LOCAL_ONLY"
            if satisfied
            else "LOOM_COHERENCE_ROUTE_EVIDENCE_INCOMPLETE_MISSING_EVIDENCE_IS_NOT_PHYSICAL_FAILURE"
        ),
    }


def governed_summary_lines(report: dict[str, Any]) -> list[str]:
    missing = report.get("missing_required_evidence") or []
    return [
        f"QUALIFICATION_AXIS={report.get('axis', AXIS)}",
        f"QUALIFICATION_DISPOSITION={report.get('disposition', 'NOT_EVALUATED')}",
        "QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + (",".join(str(item) for item in missing) if missing else "NONE"),
    ]


def build_live_report() -> dict[str, Any]:
    payload = adapter.acquire_live_e1_payload()
    payload["route_uncertainty"] = route_unc.acquire_live_route_uncertainty()
    return classify_route_evidence(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    report = build_live_report() if args.live else build_static_contract()
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.live:
        for line in governed_summary_lines(report):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
