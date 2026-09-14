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
    uncertainty = _matches(paths, [
        ("uncertainty",),
        ("sigma",),
        ("error",),
        ("confidence",),
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
        "missing_required_evidence": missing,
        "disposition": "SATISFIED" if satisfied else "INDETERMINATE_NOT_CERTIFIABLE",
        "hard_fail": False,
        "interpretation": (
            "LOOM_COHERENCE_ROUTE_EVIDENCE_SATISFIED_AXIS_LOCAL_ONLY"
            if satisfied
            else "LOOM_COHERENCE_ROUTE_EVIDENCE_INCOMPLETE_MISSING_EVIDENCE_IS_NOT_PHYSICAL_FAILURE"
        ),
    }


def build_live_report() -> dict[str, Any]:
    return classify_route_evidence(adapter.acquire_live_e1_payload())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    report = build_live_report() if args.live else build_static_contract()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
