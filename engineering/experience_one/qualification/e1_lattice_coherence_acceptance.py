#!/usr/bin/env python3
from __future__ import annotations

"""Axis-local E1 lattice-coherence acceptance classifier.

This classifier inventories the committed E1 Navigator candidate for vessel/domain
formation evidence required by the compound GA contract. Missing evidence remains
indeterminate rather than being promoted to failure or success. It creates no new
hardware values, margins, thresholds, runtime policy, or campaign state.
"""

import argparse
import json
from typing import Any

from engineering.experience_one.qualification import e1_ga_evidence_adapter as adapter

SCHEMA = "LOOM_E1_LATTICE_COHERENCE_ACCEPTANCE_V1"
AXIS = "lattice_coherence"


def _paths(payload: dict[str, Any]) -> list[str]:
    return adapter.inventory_payload(payload)["paths"]


def _matches(paths: list[str], groups: list[tuple[str, ...]]) -> list[str]:
    return adapter._any_matching(paths, groups)


def build_static_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "axis": AXIS,
        "required_evidence": [
            "committed_configuration_identity",
            "domain_membership_and_attachment_state",
            "formation_and_integrity_state",
            "hardware_condition",
            "thermal_margin",
            "bank_margin",
            "source_provenance",
        ],
        "decision_rule": {
            "all_required_groups_present": "SATISFIED",
            "one_or_more_required_groups_missing": "INDETERMINATE_NOT_CERTIFIABLE",
            "missing_evidence_is_not_hard_fail": True,
            "no_cross_axis_compensation": True,
            "field_presence_does_not_create_physical_margin": True,
        },
        "authority": {
            "certifies_lattice_coherence_only": True,
            "certifies_loom_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def classify_lattice_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    paths = _paths(payload)
    mission = payload.get("mission") or {}
    candidate = payload.get("candidate") or {}
    source = payload.get("source_authority")

    config: list[str] = []
    if mission.get("ship"):
        config.append("mission.ship")
    config.extend(_matches(paths, [
        ("configuration_id",),
        ("mass_state",),
        ("node_topology",),
        ("hull", "lattice"),
    ]))

    membership = _matches(paths, [
        ("domain_membership",),
        ("attachment_state",),
    ])
    formation = _matches(paths, [
        ("formation_state",),
        ("integrity_state",),
        ("formation", "integrity"),
    ])
    hardware = _matches(paths, [
        ("hardware_condition",),
        ("hardware_damage",),
        ("damage_state",),
    ])
    thermal = _matches(paths, [
        ("thermal_margin",),
        ("thermal", "margin"),
    ])
    bank = _matches(paths, [
        ("bank_margin",),
        ("bank", "margin"),
    ])
    provenance = ["source_authority"] if source else []

    groups = {
        "committed_configuration_identity": config,
        "domain_membership_and_attachment_state": membership,
        "formation_and_integrity_state": formation,
        "hardware_condition": hardware,
        "thermal_margin": thermal,
        "bank_margin": bank,
        "source_provenance": provenance,
    }
    missing = sorted(name for name, evidence in groups.items() if not evidence)

    return {
        **build_static_contract(),
        "status": "PASS",
        "ship": mission.get("ship"),
        "candidate_id": candidate.get("candidate_id"),
        "source_authority": source,
        "evidence": {name: sorted(set(values)) for name, values in groups.items()},
        "missing_required_evidence": missing,
        "disposition": "SATISFIED" if not missing else "INDETERMINATE_NOT_CERTIFIABLE",
        "hard_fail": False,
        "interpretation": (
            "LATTICE_COHERENCE_EVIDENCE_SATISFIED_AXIS_LOCAL_ONLY"
            if not missing
            else "LATTICE_COHERENCE_EVIDENCE_INCOMPLETE_MISSING_EVIDENCE_IS_NOT_PHYSICAL_FAILURE"
        ),
    }


def governed_summary_lines(report: dict[str, Any]) -> list[str]:
    missing = sorted(str(item) for item in (report.get("missing_required_evidence") or []))
    return [
        f"QUALIFICATION_AXIS={report.get('axis', AXIS)}",
        f"QUALIFICATION_DISPOSITION={report.get('disposition', 'NOT_EVALUATED')}",
        "QUALIFICATION_MISSING_REQUIRED_EVIDENCE=" + (",".join(missing) if missing else "NONE"),
    ]


def build_live_report() -> dict[str, Any]:
    return classify_lattice_evidence(adapter.acquire_live_e1_payload())


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
