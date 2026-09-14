#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from engineering.experience_one.qualification.e1_initial_configuration_state import (
    build_e1_initial_configuration_state,
)
from src.wayfarer_geometry import compile_geometry

SCHEMA = "LOOM_E1_COMMITTED_COMPONENT_GEOMETRY_ENVELOPE_V1"
ROOT = Path(__file__).resolve().parents[3]
SEED_SQL = ROOT / "geometry" / "wayfarer_geometry_seed.sql"


def _aabb(component: dict[str, Any]) -> dict[str, list[float]]:
    cx, cy, cz = (float(v) for v in component["center_m"])
    d = component["dimensions"]
    kind = component["kind"]
    if kind == "box":
        hx, hy, hz = float(d["x_m"]) / 2, float(d["y_m"]) / 2, float(d["z_m"]) / 2
    elif kind == "cylinder_x":
        hx = float(d["length_m"]) / 2
        hy = hz = float(d["diameter_m"]) / 2
    elif kind == "nozzle_x":
        hx = float(d["length_m"]) / 2
        hy = hz = float(d["aperture_diameter_m"]) / 2
    elif kind == "collar_z":
        hx = hy = float(d["diameter_m"]) / 2
        hz = float(d["depth_m"]) / 2
    elif kind == "radiator_placeholder":
        # Deliberately conservative placeholder bound. It is containment input only,
        # not a promotion of OPEN radiator panel geometry to canon.
        hx = float(d["root_length_m"]) / 2
        hy = hz = max(float(d["panel_span_m"]), float(d["panel_chord_m"])) / 2
    else:
        raise ValueError(f"Unsupported geometry primitive for E1 envelope: {kind}")
    return {
        "x": [cx - hx, cx + hx],
        "y": [cy - hy, cy + hy],
        "z": [cz - hz, cz + hz],
    }


def _compile_source_geometry() -> dict[str, Any]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SEED_SQL.read_text(encoding="utf-8"))
        return compile_geometry(conn)
    finally:
        conn.close()


def build_e1_committed_component_geometry_envelope() -> dict[str, Any]:
    geometry = _compile_source_geometry()
    runtime = build_e1_initial_configuration_state().to_evidence()
    authored = runtime["authored_state"]

    selected: list[dict[str, Any]] = []
    for component in geometry["components"]:
        cid = component["id"]
        if cid == "planetary_launch" and authored["launch_attachment_state"] != "DOCKED":
            continue
        item = {
            "id": cid,
            "kind": component["kind"],
            "group": component["group"],
            "status": component["status"],
            "source": component["source"],
            "center_m": component["center_m"],
            "dimensions": component["dimensions"],
            "aabb_m": _aabb(component),
        }
        selected.append(item)

    envelope = {
        axis: [
            min(c["aabb_m"][axis][0] for c in selected),
            max(c["aabb_m"][axis][1] for c in selected),
        ]
        for axis in ("x", "y", "z")
    }
    open_ids = sorted(c["id"] for c in selected if c["status"] == "OPEN")

    return {
        "schema": SCHEMA,
        "status": "PASS",
        "source_geometry_schema": geometry["schema"],
        "source_geometry_schema_version": geometry["schema_version"],
        "source_authority_chain": [
            "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
            "canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md",
            "geometry/wayfarer_geometry_seed.sql",
            "src/wayfarer_geometry.py",
        ],
        "runtime_configuration": {
            "launch_attachment_state": authored["launch_attachment_state"],
            "external_attachment_state": authored["external_attachment_state"],
            "deployable_structure_state": authored["deployable_structure_state"],
        },
        "committed_components": selected,
        "component_count": len(selected),
        "component_geometry_envelope_m": envelope,
        "open_detail_present": bool(open_ids),
        "open_detail_component_ids": open_ids,
        "open_detail_promoted_to_canon": False,
        "sufficient_as_domain_containment_input": True,
        "configuration_policy": {
            "docked_launch_included": authored["launch_attachment_state"] == "DOCKED",
            "free_external_state_adds_no_external_component": authored["external_attachment_state"] == "FREE",
            "stowed_radiator_open_geometry_uses_conservative_placeholder_bound": authored["deployable_structure_state"] == "STOWED",
            "exact_node_placement_required_for_material_component_envelope": False,
            "exact_node_placement_may_be_required_for_field_boundary_solution": True,
        },
        "derivative_artifact_policy": {
            "glb_role": "DERIVATIVE_CONFIRMATION_ONLY",
            "glb_is_geometry_authority": False,
            "generated_json_is_geometry_authority": False,
            "sql_parameter_model_and_compiler_are_geometry_source": True,
        },
        "disposition": "COMMITTED_COMPONENT_GEOMETRY_ENVELOPE_PRESENT_WITH_OPEN_DETAIL_BOUNDED",
        "authority": {
            "certifies_committed_component_geometry_envelope": True,
            "certifies_translation_domain_boundary": False,
            "certifies_domain_membership": False,
            "certifies_domain_size": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def main() -> int:
    result = build_e1_committed_component_geometry_envelope()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("QUALIFICATION_AXIS=committed_component_geometry_envelope")
    print(f"QUALIFICATION_DISPOSITION={result['disposition']}")
    print("QUALIFICATION_MISSING_REQUIRED_EVIDENCE=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
