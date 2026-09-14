#!/usr/bin/env python3
from __future__ import annotations

"""Qualify Neptune local monopole curvature/tidal shear at the earned E1 collapse seam.

This is a bounded local-geometry reference calculation. It does not define a
Geometric Admissibility threshold, exclusion radius, score, or runtime policy.
The current collapse seam remains an earned operational handoff rather than a
fundamental physical boundary.
"""

import json
import math
from typing import Any

C_KM_S = 299_792.458

# Earned E1 endpoint inherited from the already-qualified NAV-V1-A / forced-radius
# lineage. This module does not re-solve Navigator or alter the endpoint.
EARNED_COLLAPSE_RADIUS_KM = 26_085.768742
EARNED_COLLAPSE_EPOCH_UTC = "2226-08-22T09:07:59.475571Z"
EARNED_ARRIVAL_EPOCH_UTC = "2226-08-22T09:45:17.864616Z"

# Versioned Neptune inputs already qualified from data/LOOM_2226.sqlite3 by
# e1_geometric_admissibility_inventory.py.
NEPTUNE_GM_KM3_S2 = 6_836_529.0
NEPTUNE_MEAN_RADIUS_KM = 24_622.0


def local_monopole_geometry(*, gm_km3_s2: float, radius_km: float) -> dict[str, Any]:
    """Return spherical-monopole reference geometry at a body-centered radius.

    The tidal eigenvalues are the Newtonian/weak-field electric-curvature
    eigenvalues for a spherical monopole: (+2,-1,-1) GM/r^3. The Schwarzschild
    Kretschmann scalar is reported only as the corresponding monopole curvature
    invariant reference. Neither is a complete Neptune endpoint spacetime model.
    """
    gm = float(gm_km3_s2)
    radius = float(radius_km)
    if not math.isfinite(gm) or gm <= 0.0:
        raise ValueError("gm_km3_s2 must be finite and positive")
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius_km must be finite and positive")

    lam = gm / radius**3
    radial = 2.0 * lam
    transverse = -lam
    tidal_norm = math.sqrt(radial**2 + 2.0 * transverse**2)
    kretschmann = 48.0 * gm**2 / (C_KM_S**4 * radius**6)

    return {
        "gravity_acceleration_km_s2": gm / radius**2,
        "tidal_eigenvalues_s2_inv": {
            "radial": radial,
            "transverse_1": transverse,
            "transverse_2": transverse,
        },
        "tidal_frobenius_norm_s2_inv": tidal_norm,
        "schwarzschild_kretschmann_km4_inv": kretschmann,
        "schwarzschild_sqrt_kretschmann_km2_inv": math.sqrt(kretschmann),
        "reference_model": "SPHERICAL_MONOPOLE_WEAK_FIELD_PLUS_SCHWARZSCHILD_INVARIANT_REFERENCE",
    }


def qualify_earned_neptune_endpoint() -> dict[str, Any]:
    geometry = local_monopole_geometry(
        gm_km3_s2=NEPTUNE_GM_KM3_S2,
        radius_km=EARNED_COLLAPSE_RADIUS_KM,
    )
    altitude = EARNED_COLLAPSE_RADIUS_KM - NEPTUNE_MEAN_RADIUS_KM

    return {
        "schema": "LOOM_E1_LOCAL_CURVATURE_TIDAL_SHEAR_V1",
        "status": "PASS",
        "endpoint": {
            "body": "NEPTUNE",
            "collapse_radius_km": EARNED_COLLAPSE_RADIUS_KM,
            "collapse_epoch_utc": EARNED_COLLAPSE_EPOCH_UTC,
            "arrival_epoch_utc": EARNED_ARRIVAL_EPOCH_UTC,
            "altitude_above_mean_radius_km": altitude,
            "endpoint_status": "EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY",
        },
        "inputs": {
            "gm_km3_s2": NEPTUNE_GM_KM3_S2,
            "mean_radius_km": NEPTUNE_MEAN_RADIUS_KM,
            "gm_provenance": "data/LOOM_2226.sqlite3 via e1_geometric_admissibility_inventory.py",
            "mean_radius_provenance": "data/LOOM_2226.sqlite3 via e1_geometric_admissibility_inventory.py",
            "endpoint_provenance": "NAV-V1-A earned E1 arrival plus e1_forced_collapse_radius_experiment lineage",
        },
        "local_geometry_reference": geometry,
        "qualified_claims": [
            "neptune_spherical_monopole_gravity_at_earned_endpoint",
            "neptune_spherical_monopole_tidal_eigenvalues_at_earned_endpoint",
            "neptune_spherical_monopole_tidal_norm_at_earned_endpoint",
            "schwarzschild_monopole_kretschmann_reference_at_earned_endpoint",
        ],
        "unresolved_corrections": [
            "neptune_rotation_and_frame_dragging",
            "neptune_oblateness_and_higher_multipoles",
            "local_stress_energy_matter_density",
            "physical_uncertainty_at_2226_endpoint",
            "loom_coherence",
            "lattice_coherence",
            "domain_size_binding_to_admissibility",
        ],
        "admissibility_threshold_defined": False,
        "runtime_policy_mutation": "ZERO",
        "campaign_state_mutation": "ZERO",
        "llm_calculation_authority": "ZERO",
        "authority_note": "REFERENCE_GEOMETRY_ONLY_NO_SCORE_NO_THRESHOLD_NO_EXCLUSION_RADIUS_NO_HILL_OR_SOI_POLICY",
        "interpretation": "LOCAL_GEOMETRY_REFERENCE_QUALIFIED_ADMISSIBILITY_DECISION_NOT_YET_EARNED",
        "next_action": "PROPAGATE_PHYSICAL_UNCERTAINTY_AND_TEST_WHETHER_ROTATION_OR_MULTIPOLE_CORRECTIONS_ARE_MATERIAL_BEFORE_COMPOUND_ADMISSIBILITY",
    }


def main() -> int:
    print(json.dumps(qualify_earned_neptune_endpoint(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
