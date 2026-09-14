#!/usr/bin/env python3
from __future__ import annotations

"""Expose the governing Wayfarer schematic identity needed by E1 configuration binding.

This artifact identifies the already-governing reference schematic. It does not
freeze open detailed geometry, exact relational-node placement, domain geometry,
or a runtime attachment/membership state.
"""

import json
from typing import Any

SCHEMA = "LOOM_E1_HULL_LATTICE_CONFIGURATION_EVIDENCE_V1"
CONFIGURATION_ID = "WAYFARER_REFERENCE_SCHEMATIC_V2_4A"


def build_current_e1_hull_lattice_configuration() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "configuration_id": CONFIGURATION_ID,
        "configuration_identity_present": True,
        "governing_authority": [
            "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
            "canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md",
        ],
        "primary_structural_grammar": {
            "axial_longerons": 4,
            "working_fluid_remass_tanks": 4,
            "working_fluid_remass_tank_arrangement": "QUADRATURE",
            "radiator_assemblies": 4,
            "radiator_arrangement": "QUADRATURE",
            "primary_axial_torch_nozzle_systems": 1,
        },
        "relational_node_topology": {
            "architecture": "UNIFIED_RELATIONAL_PROPULSION_PLANT",
            "distributed_boundary_metric_nodes": 208,
            "exact_node_placement": "OPEN",
        },
        "integrated_launch_bay": {
            "packaging": "SEMI_RECESSED_UNPRESSURIZED_INTEGRATED_PRIMARY_STRUCTURE",
            "crew_transfer": "PRESSURE_TIGHT_INTERFACE",
            "departure": "LATERAL",
            "attachment_state_required_in_dependent_solutions": True,
        },
        "open_detail": [
            "exact_hull_outer_contour",
            "exact_armor_panel_pattern",
            "detailed_relational_subassemblies",
            "tile_arrangement",
            "exact_node_placement",
            "service_routing",
        ],
        "policy": {
            "exact_hull_contour_required_for_configuration_identity": False,
            "node_count_substitutes_for_exact_node_placement": False,
            "open_detail_promoted_to_canon": False,
            "hull_dimensions_substitute_for_translation_domain_geometry": False,
        },
        "authority": {
            "certifies_configuration_identity": True,
            "certifies_domain_geometry": False,
            "certifies_domain_membership_or_attachment": False,
            "certifies_domain_size": False,
            "certifies_lattice_coherence": False,
            "certifies_overall_ga": False,
            "campaign_state_mutation": "ZERO",
            "runtime_policy_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }


def main() -> int:
    print(json.dumps(build_current_e1_hull_lattice_configuration(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
