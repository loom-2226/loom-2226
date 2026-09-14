from __future__ import annotations

import json
import math
from typing import Any, Dict, List

SHIP_LENGTH_M = 57.0
AXIAL_RINGS = 13
NODES_PER_RING = 16
NODE_COUNT = AXIAL_RINGS * NODES_PER_RING


def _support_profile(x_m: float) -> Dict[str, Any]:
    """Return the structural support radius used for the metric-node design baseline.

    The profile follows the current deterministic Wayfarer engineering geometry rather
    than a single imaginary cylinder. Values are design-baseline geometry inputs and do
    not certify a metric field boundary.
    """
    if x_m < 14.0:
        return {"support_group": "pressure_hull", "support_radius_m": 4.3}
    if x_m < 38.0:
        return {"support_group": "main_structure", "support_radius_m": 4.5}
    if x_m < 43.0:
        return {"support_group": "shadow_shield", "support_radius_m": 2.75}
    if x_m < 50.0:
        return {"support_group": "reactor_torch_structure", "support_radius_m": 2.125}
    return {"support_group": "magnetic_nozzle_support", "support_radius_m": 3.0}


def build_metric_node_array() -> Dict[str, Any]:
    pitch = SHIP_LENGTH_M / AXIAL_RINGS
    rings: List[Dict[str, Any]] = []
    nodes: List[Dict[str, Any]] = []

    for ring_index in range(AXIAL_RINGS):
        x_m = (ring_index + 0.5) * pitch
        support = _support_profile(x_m)
        ring = {
            "ring_index": ring_index,
            "x_m": x_m,
            "support_group": support["support_group"],
            "support_radius_m": support["support_radius_m"],
            "nodes": [],
        }

        for azimuth_index in range(NODES_PER_RING):
            azimuth_deg = azimuth_index * (360.0 / NODES_PER_RING)
            a = math.radians(azimuth_deg)
            radius = float(support["support_radius_m"])
            node_id = f"MN-R{ring_index:02d}-A{azimuth_index:02d}"
            node = {
                "id": node_id,
                "ring_index": ring_index,
                "azimuth_index": azimuth_index,
                "azimuth_deg": azimuth_deg,
                "support_group": support["support_group"],
                "position_m": {
                    "x": x_m,
                    "y": radius * math.cos(a),
                    "z": radius * math.sin(a),
                },
                "placement_status": "DESIGN_BASELINE",
                "role": "METRIC_DISTRIBUTED_BOUNDARY_NODE",
            }
            ring["nodes"].append(node_id)
            nodes.append(node)
        rings.append(ring)

    if len(nodes) != NODE_COUNT:
        raise AssertionError(f"Expected {NODE_COUNT} metric nodes, built {len(nodes)}")

    return {
        "schema": "LOOM.Wayfarer.MetricNodeArray",
        "schema_version": "0.1",
        "node_count": NODE_COUNT,
        "layout": {
            "axial_rings": AXIAL_RINGS,
            "nodes_per_ring": NODES_PER_RING,
            "axial_pitch_m": pitch,
            "azimuth_pitch_deg": 360.0 / NODES_PER_RING,
            "ring_centering_rule": "CELL_CENTERED_ACROSS_57M_REFERENCE_LENGTH",
            "azimuth_rule": "UNIFORM_22_5_DEGREE_SECTORS_WITH_CARDINAL_AND_DIAGONAL_COVERAGE",
        },
        "scope": {
            "metric_design_baseline": True,
            "loom_design_certified": False,
            "future_shared_hardware_compatibility_preserved": True,
            "rcs_geometry_defined_by_this_array": False,
            "torch_geometry_defined_by_this_array": False,
        },
        "provenance": {
            "node_count_status": "CANON",
            "node_count_source": "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
            "placement_status": "DESIGN_BASELINE",
            "placement_basis": "DETERMINISTIC_WAYFARER_GEOMETRY_AND_CURRENT_AXIAL_STRUCTURAL_ENVELOPES",
            "geometry_source": "src/wayfarer_geometry.py",
            "design_note": (
                "13 x 16 is an engineering baseline chosen to realize the governing 208-node count "
                "with regular axial and circumferential coverage; it is not recovered canon."
            ),
        },
        "rings": rings,
        "nodes": nodes,
        "authority": {
            "certifies_metric_node_placement_baseline": True,
            "certifies_metric_domain_boundary": False,
            "certifies_domain_membership": False,
            "certifies_loom_formation": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "SOLVE_METRIC_FIELD_BOUNDARY_FROM_COMMITTED_CONFIGURATION_AND_METRIC_NODE_ARRAY",
    }


def main() -> int:
    result = build_metric_node_array()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("METRIC_NODE_COUNT=208")
    print("METRIC_NODE_PLACEMENT_STATUS=DESIGN_BASELINE")
    print("METRIC_DOMAIN_BOUNDARY_CERTIFIED=NO")
    print("LOOM_DESIGN_CERTIFIED=NO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
