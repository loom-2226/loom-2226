#!/usr/bin/env python3
from __future__ import annotations

"""Conservative adapter from existing E1/Navigator evidence into GA evidence packages.

This module does not certify geometric admissibility. It inventories existing
qualified references and operational Navigator payloads, and reports whether the
minimum evidence contract is present, partial, absent, or present without the
acceptance authority required by the GA decision rule.
"""

import argparse
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

SCHEMA = "LOOM_E1_GA_EVIDENCE_ADAPTER_V1"
ROUTE = ["CERES", "NEPTUNE_SYSTEM"]
SHIP = "WAYFARER_BASELINE"


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


def inventory_payload(payload: Any) -> dict[str, Any]:
    paths = []
    scalar_paths = []
    for path, value in _walk(payload):
        paths.append(path)
        if not isinstance(value, (dict, list, tuple)):
            scalar_paths.append(path)
    return {
        "paths": sorted(set(paths)),
        "scalar_paths": sorted(set(scalar_paths)),
    }


def _matching(paths: list[str], *tokens: str) -> list[str]:
    lowered = [(path, path.lower()) for path in paths]
    return sorted(path for path, low in lowered if all(token.lower() in low for token in tokens))


def _any_matching(paths: list[str], token_groups: list[tuple[str, ...]]) -> list[str]:
    found: set[str] = set()
    for group in token_groups:
        found.update(_matching(paths, *group))
    return sorted(found)


def _field(state: str, evidence: list[str] | None = None, note: str = "") -> dict[str, Any]:
    return {
        "state": state,
        "evidence": sorted(set(evidence or [])),
        "note": note,
    }


def build_static_evidence_report() -> dict[str, Any]:
    """Report what is already earned without inspecting a fresh Navigator payload."""
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "decision": "GA_EVIDENCE_ADAPTER_QUALIFIED_RUNTIME_PAYLOAD_INSPECTION_STILL_REQUIRED",
        "blocked_axes": [
            "causal_structure",
            "domain_size",
            "lattice_coherence",
            "local_geometry",
            "loom_coherence",
        ],
        "packages": {
            "endpoint_domain_physical_compatibility": {
                "fields": {
                    "committed_configuration_identity": _field(
                        "PRESENT_BUT_NOT_CERTIFICATION_AUTHORITY",
                        ["mission.ship=WAYFARER_BASELINE"],
                        "Ship identity exists, but the full certified configuration tuple is not yet exposed as a GA acceptance artifact.",
                    ),
                    "translation_domain_geometry_or_certification_envelope": _field(
                        "MISSING",
                        note="No governed numeric translation-domain geometry/certification envelope has been qualified for the committed E1 configuration.",
                    ),
                    "qualified_local_geometry_compatibility_result": _field(
                        "PRESENT_BUT_NOT_ACCEPTANCE_AUTHORITY",
                        ["J2_CORRECTED_LOCAL_TIDAL_REFERENCE_QUALIFIED"],
                        "Qualified local geometry reference exists; compatibility across a certified translation domain is not yet earned.",
                    ),
                    "qualified_causal_compatibility_result_or_equivalent_invariant": _field(
                        "PRESENT_BUT_NOT_ACCEPTANCE_AUTHORITY",
                        ["STANDARD_GR_CAUSAL_PATHOLOGY_NOT_MATERIAL_AT_E1_NEPTUNE_ENDPOINT"],
                        "Standard-GR endpoint screen exists; Loom-specific metric-domain causal compatibility is not yet earned.",
                    ),
                    "uncertainty_and_provenance": _field(
                        "PRESENT_QUALIFIED_SUPPORT",
                        [
                            "E1_NEPTUNE_J2_CORRECTED_LOCAL_TIDAL_REFERENCE_V1",
                            "LOOM_E1_NEPTUNE_CAUSAL_STRUCTURE_MATERIALITY_V1",
                        ],
                        "Qualified reference artifacts preserve uncertainty/provenance, but they do not close the acceptance axes by themselves.",
                    ),
                }
            },
            "route_vessel_coherence": {
                "fields": {
                    "route_solution_identity_and_direction": _field(
                        "PRESENT_OPERATIONAL_EVIDENCE",
                        ["route=CERES->NEPTUNE_SYSTEM", "Navigator selected candidate_id"],
                    ),
                    "route_evidence_destination_state_and_momentum_mapping": _field("RUNTIME_INSPECTION_REQUIRED"),
                    "route_burden_and_uncertainty": _field("RUNTIME_INSPECTION_REQUIRED"),
                    "configuration_identity_and_domain_membership": _field("RUNTIME_INSPECTION_REQUIRED"),
                    "formation_and_integrity_state": _field("RUNTIME_INSPECTION_REQUIRED"),
                    "hardware_thermal_and_bank_margins": _field("RUNTIME_INSPECTION_REQUIRED"),
                    "certification_disposition": _field(
                        "MISSING",
                        note="No existing E1 artifact found that may be promoted automatically to a GA certification disposition.",
                    ),
                }
            },
        },
        "evidence_policy": {
            "package_level_shortcut_to_admissible_allowed": False,
            "cross_axis_compensation_allowed": False,
            "missing_axis_evidence_treated_as_satisfied": False,
            "same_committed_configuration_required_across_packages": True,
            "operational_field_presence_equals_certification_authority": False,
        },
        "authority": {
            "runtime_policy_mutation": "ZERO",
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
            "certifies_ga_outcome": False,
        },
    }


def classify_runtime_payload(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inventory = inventory_payload(payload)
    paths = inventory["paths"]

    route_id = _any_matching(paths, [("candidate_id",), ("route",)])
    destination = _any_matching(paths, [("arrival",), ("destination",), ("collapse_state",)])
    momentum = _any_matching(paths, [("momentum",), ("velocity",)])
    route_burden = _any_matching(paths, [("burden",), ("beta",), ("duration",), ("remass",)])
    uncertainty = _any_matching(paths, [("uncertainty",), ("sigma",), ("error",)])
    config = _any_matching(paths, [("ship",), ("configuration",), ("mass_state",), ("node_topology",), ("hull", "lattice")])
    membership = _any_matching(paths, [("domain_membership",), ("attachment_state",), ("membership",)])
    formation = _any_matching(paths, [("formation",), ("integrity",)])
    hardware = _any_matching(paths, [("hardware",), ("damage",), ("thermal",), ("bank",), ("lattice", "margin")])
    certification = _any_matching(paths, [("certif",), ("admissib",), ("recommendation",), ("disposition",)])
    domain_geometry = _any_matching(paths, [("domain", "radius"), ("domain", "geometry"), ("translation", "domain"), ("domain_membership",)])

    def combined_state(first: list[str], second: list[str]) -> str:
        if first and second:
            return "PRESENT_OPERATIONAL_EVIDENCE"
        if first or second:
            return "PARTIAL_OPERATIONAL_EVIDENCE"
        return "MISSING"

    return {
        "route_solution_identity_and_direction": _field(
            "PRESENT_OPERATIONAL_EVIDENCE" if route_id else "MISSING", route_id
        ),
        "route_evidence_destination_state_and_momentum_mapping": _field(
            combined_state(destination, momentum), destination + momentum
        ),
        "route_burden_and_uncertainty": _field(
            combined_state(route_burden, uncertainty), route_burden + uncertainty
        ),
        "configuration_identity_and_domain_membership": _field(
            combined_state(config, membership), config + membership
        ),
        "formation_and_integrity_state": _field(
            "PRESENT_OPERATIONAL_EVIDENCE" if formation else "MISSING", formation
        ),
        "hardware_thermal_and_bank_margins": _field(
            "PRESENT_OPERATIONAL_EVIDENCE" if hardware else "MISSING", hardware
        ),
        "certification_disposition": _field(
            "PRESENT_BUT_REQUIRES_AUTHORITY_REVIEW" if certification else "MISSING", certification,
            "Text/field presence is not promoted automatically to GA certification authority.",
        ),
        "translation_domain_geometry_or_certification_envelope": _field(
            "PRESENT_BUT_REQUIRES_AUTHORITY_REVIEW" if domain_geometry else "MISSING", domain_geometry,
            "Operational domain fields, if present, are not automatically a governed certification envelope.",
        ),
    }


def acquire_live_e1_payload() -> dict[str, Any]:
    """Read-only acquisition of the current E1 Navigator solved candidate."""
    with tempfile.TemporaryDirectory(prefix="loom-e1-ga-adapter-") as td:
        root = Path(td)
        nav = campaign._load_core(root / "core")
        cache = root / "cache"
        mission = {
            "schema": nav.MISSION_SCHEMA,
            "test_id": "E1_GA_EVIDENCE_ADAPTER",
            "epoch": {"local": "2226-08-22T01:32:00", "timezone": "UTC", "fold": 0},
            "route": ROUTE,
            "ship": SHIP,
            "requested_modes": {"metric": "HARD", "torch": "CRUISE"},
        }
        normalized = nav.validate_and_normalize_mission(mission)
        acquisition, _ = nav_probe._route_scoped_acquisition(nav, normalized, cache)
        state = campaign._new_state("E1-GA-EVIDENCE-ADAPTER", "WAYFARER-E1")
        candidates = campaign._candidate_plans(nav, normalized, acquisition, cache, state, "BALANCED")
        if not candidates:
            raise RuntimeError("Navigator returned no E1 candidates")
        selected = candidates[0]
        return {
            "mission": mission,
            "normalized_route": normalized.get("route"),
            "candidate": selected,
            "leg": selected.get("leg") or {},
            "source_authority": acquisition.get("authority", {}).get("source"),
        }


def build_live_evidence_report() -> dict[str, Any]:
    report = build_static_evidence_report()
    payload = acquire_live_e1_payload()
    runtime = classify_runtime_payload(payload)
    package_b = report["packages"]["route_vessel_coherence"]["fields"]
    for key in list(package_b):
        if key in runtime:
            package_b[key] = runtime[key]
    package_a = report["packages"]["endpoint_domain_physical_compatibility"]["fields"]
    package_a["translation_domain_geometry_or_certification_envelope"] = runtime[
        "translation_domain_geometry_or_certification_envelope"
    ]
    report["runtime_inventory"] = {
        "source_authority": payload.get("source_authority"),
        "payload": inventory_payload(payload),
    }
    report["decision"] = "LIVE_E1_GA_EVIDENCE_INVENTORY_COMPLETE_NO_AUTOMATIC_CERTIFICATION_PROMOTION"
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="inspect a fresh read-only E1 Navigator solved candidate")
    args = parser.parse_args()
    report = build_live_evidence_report() if args.live else build_static_evidence_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
