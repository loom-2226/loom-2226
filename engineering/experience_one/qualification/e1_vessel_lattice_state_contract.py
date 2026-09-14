#!/usr/bin/env python3
from __future__ import annotations

"""Typed, non-certifying vessel/domain state contract for E1 lattice coherence.

This module creates no thresholds and invents no hardware values. UNKNOWN is an
explicit governed state. It exists to provide the missing state seam required by
lattice-coherence qualification before any operational values are promoted.
"""

import json
from typing import Any, Mapping

SCHEMA = "LOOM_E1_VESSEL_LATTICE_STATE_CONTRACT_V1"
AXIS = "lattice_coherence"
REQUIRED = [
    "domain_membership_and_attachment_state",
    "formation_and_integrity_state",
    "hardware_condition",
    "thermal_margin",
    "bank_margin",
]


def build_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "axis": AXIS,
        "required_state_groups": REQUIRED,
        "policy": {
            "explicit_unknown_allowed": True,
            "infer_unknown_as_nominal": False,
            "invent_numeric_thresholds": False,
            "cross_axis_compensation_allowed": False,
        },
        "authority": {
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def _known(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip().upper()
    return bool(text) and text not in {"UNKNOWN", "UNRESOLVED", "NOT_AVAILABLE", "NONE"}


def evaluate_state(state: Mapping[str, Any]) -> dict[str, Any]:
    missing = sorted(name for name in REQUIRED if not _known(state.get(name)))
    return {
        **build_contract(),
        "status": "PASS",
        "state": {name: state.get(name, "UNKNOWN") for name in REQUIRED},
        "missing_required_evidence": missing,
        "disposition": "SATISFIED" if not missing else "INDETERMINATE_NOT_CERTIFIABLE",
        "hard_fail": False,
    }


def build_unknown_state() -> dict[str, Any]:
    # Thermal margin is already surfaced by the live lattice classifier. The
    # remaining groups are intentionally UNKNOWN until earned by a later step.
    return evaluate_state({
        "domain_membership_and_attachment_state": "UNKNOWN",
        "formation_and_integrity_state": "UNKNOWN",
        "hardware_condition": "UNKNOWN",
        "thermal_margin": "PRESENT_OPERATIONAL_EVIDENCE",
        "bank_margin": "UNKNOWN",
    })


def main() -> int:
    print(json.dumps(build_unknown_state(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
