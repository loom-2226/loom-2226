#!/usr/bin/env python3
from __future__ import annotations

"""Promote already-earned Wayfarer configuration evidence without inventing hull/lattice identity.

Mass-state values come from the current Wayfarer engineering candidate/project state.
Node topology comes from Canon II v2.5 (pending PR #471 merge). The repository does not yet expose a
governed hull/lattice configuration identity, so that member remains unresolved.
"""

import json
from typing import Any

SCHEMA = "LOOM_E1_WAYFARER_CONFIGURATION_EVIDENCE_V1"


def build_evidence() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "ship": "WAYFARER_BASELINE",
        "mass_state_model": {
            "state": "PRESENT_QUALIFIED_SUPPORT",
            "model_id": "WAYFARER_MASS_STATE_CURRENT_ENGINEERING_V1",
            "dry_mass_t": 858.5,
            "working_fluid_water_t": 295.3904317110822,
            "wet_mass_t": 1153.8904317110823,
            "normal_remass_t": 245.39043171108221,
            "protected_water_reserve_t": 50.0,
            "normal_remass_is_within_working_fluid_inventory": True,
            "source": "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.5.md",
            "supporting_source": "geometry/wayfarer_geometry_seed.sql",
        },
        "node_topology": {
            "state": "PRESENT_QUALIFIED_SUPPORT",
            "topology_id": "UNIFIED_RELATIONAL_PROPULSION_208_NODE_BASELINE",
            "architecture": "UNIFIED_RELATIONAL_PROPULSION_PLANT",
            "distributed_boundary_metric_nodes": 208,
            "source": "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.5.md",
        },
        "hull_lattice_configuration": {
            "state": "UNRESOLVED",
            "configuration_identity_claimed": False,
            "reason": "NO_GOVERNED_WAYFARER_HULL_LATTICE_CONFIGURATION_IDENTITY_EXPOSED",
        },
        "policy": {
            "promote_only_existing_values": True,
            "invent_hull_lattice_identity": False,
            "node_count_substitutes_for_hull_lattice_configuration": False,
            "mass_model_substitutes_for_domain_membership": False,
        },
        "authority": {
            "certifies_configuration_identity_complete": False,
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
    print(json.dumps(build_evidence(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
