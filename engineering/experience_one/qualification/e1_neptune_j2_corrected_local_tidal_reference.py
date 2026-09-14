#!/usr/bin/env python3
from __future__ import annotations

"""Qualify a bounded J2-corrected Neptune local tidal reference at the earned E1 endpoint.

This module preserves the already-earned collapse radius and propagates the measured
Neptune J2 term across the full unresolved endpoint-orientation envelope. It does not
define a Geometric Admissibility threshold, exclusion radius, drive-coupling rule,
runtime policy, or campaign-state mutation.
"""

import json
import math
from typing import Any

EARNED_COLLAPSE_RADIUS_KM = 26_085.768742
EARNED_COLLAPSE_EPOCH_UTC = "2226-08-22T09:07:59.475571Z"
EARNED_ARRIVAL_EPOCH_UTC = "2226-08-22T09:45:17.864616Z"
NEPTUNE_GM_KM3_S2 = 6_836_529.0
NEPTUNE_MEAN_RADIUS_KM = 24_622.0
NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM = 25_225.0
NEPTUNE_J2 = 3_409.138069414930e-6
NEPTUNE_J2_SIGMA = 2.9e-6
ORIENTATION_SAMPLES = 721


def _j2_dimensionless_components(*, colatitude_rad: float, j2: float) -> tuple[float, float, float, float]:
    """Return J2 Hessian components divided by GM/r^3.

    Output is (rr, rtheta, thetatheta, phiphi) in the local orthonormal spherical
    basis for the standard axisymmetric zonal-harmonic potential convention used
    by the preceding materiality qualification.
    """
    theta = float(colatitude_rad)
    coefficient = float(j2)
    if not math.isfinite(theta):
        raise ValueError("colatitude_rad must be finite")
    if not math.isfinite(coefficient):
        raise ValueError("j2 must be finite")

    c = math.cos(theta)
    s = math.sin(theta)
    p2 = 0.5 * (3.0 * c * c - 1.0)
    dp_dtheta = -3.0 * s * c
    d2p_dtheta2 = -3.0 * (c * c - s * s)
    cot_dp = -3.0 * c * c
    scale = coefficient * (NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM / EARNED_COLLAPSE_RADIUS_KM) ** 2

    rr = -12.0 * scale * p2
    rtheta = 4.0 * scale * dp_dtheta
    thetatheta = scale * (3.0 * p2 - d2p_dtheta2)
    phiphi = scale * (3.0 * p2 - cot_dp)
    return rr, rtheta, thetatheta, phiphi


def _principal_values(*, rr: float, rtheta: float, thetatheta: float, phiphi: float) -> tuple[float, float, float]:
    """Return sorted eigenvalues for the axisymmetric local tidal tensor."""
    mean = 0.5 * (rr + thetatheta)
    spread = math.sqrt((0.5 * (rr - thetatheta)) ** 2 + rtheta * rtheta)
    values = [mean - spread, mean + spread, phiphi]
    values.sort()
    return values[0], values[1], values[2]


def _orientation_sweep(*, j2: float) -> dict[str, Any]:
    if ORIENTATION_SAMPLES < 181:
        raise ValueError("orientation sweep must contain at least 181 samples")

    lam = NEPTUNE_GM_KM3_S2 / EARNED_COLLAPSE_RADIUS_KM**3
    monopole_norm = math.sqrt(6.0) * lam

    norms: list[float] = []
    fractional_norm_changes: list[float] = []
    eig0: list[float] = []
    eig1: list[float] = []
    eig2: list[float] = []
    traces: list[float] = []
    colatitudes: list[float] = []

    for index in range(ORIENTATION_SAMPLES):
        colatitude_deg = 180.0 * index / (ORIENTATION_SAMPLES - 1)
        colatitudes.append(colatitude_deg)
        j_rr, j_rt, j_tt, j_pp = _j2_dimensionless_components(
            colatitude_rad=math.radians(colatitude_deg),
            j2=j2,
        )

        rr = (2.0 + j_rr) * lam
        rtheta = j_rt * lam
        thetatheta = (-1.0 + j_tt) * lam
        phiphi = (-1.0 + j_pp) * lam

        norm = math.sqrt(rr * rr + 2.0 * rtheta * rtheta + thetatheta * thetatheta + phiphi * phiphi)
        principal = _principal_values(rr=rr, rtheta=rtheta, thetatheta=thetatheta, phiphi=phiphi)

        norms.append(norm)
        fractional_norm_changes.append(norm / monopole_norm - 1.0)
        eig0.append(principal[0])
        eig1.append(principal[1])
        eig2.append(principal[2])
        traces.append(rr + thetatheta + phiphi)

    min_norm_index = min(range(ORIENTATION_SAMPLES), key=norms.__getitem__)
    max_norm_index = max(range(ORIENTATION_SAMPLES), key=norms.__getitem__)

    return {
        "orientation_policy": "FULL_COLATITUDE_SWEEP_NO_ENDPOINT_LATITUDE_ASSUMED",
        "samples": ORIENTATION_SAMPLES,
        "colatitude_min_deg": 0.0,
        "colatitude_max_deg": 180.0,
        "tidal_frobenius_norm_s2_inv": {
            "min": norms[min_norm_index],
            "min_at_colatitude_deg": colatitudes[min_norm_index],
            "max": norms[max_norm_index],
            "max_at_colatitude_deg": colatitudes[max_norm_index],
        },
        "fractional_change_from_monopole_norm": {
            "min": min(fractional_norm_changes),
            "max": max(fractional_norm_changes),
        },
        "principal_tidal_eigenvalues_s2_inv": {
            "most_negative": {"min": min(eig0), "max": max(eig0)},
            "middle": {"min": min(eig1), "max": max(eig1)},
            "most_positive": {"min": min(eig2), "max": max(eig2)},
        },
        "max_abs_trace_s2_inv": max(abs(value) for value in traces),
    }


def qualify_j2_corrected_local_tidal_reference() -> dict[str, Any]:
    nominal = _orientation_sweep(j2=NEPTUNE_J2)
    lower = _orientation_sweep(j2=NEPTUNE_J2 - NEPTUNE_J2_SIGMA)
    upper = _orientation_sweep(j2=NEPTUNE_J2 + NEPTUNE_J2_SIGMA)
    altitude = EARNED_COLLAPSE_RADIUS_KM - NEPTUNE_MEAN_RADIUS_KM
    monopole_norm = math.sqrt(6.0) * NEPTUNE_GM_KM3_S2 / EARNED_COLLAPSE_RADIUS_KM**3

    uncertainty_norm_mins = [
        lower["tidal_frobenius_norm_s2_inv"]["min"],
        nominal["tidal_frobenius_norm_s2_inv"]["min"],
        upper["tidal_frobenius_norm_s2_inv"]["min"],
    ]
    uncertainty_norm_maxs = [
        lower["tidal_frobenius_norm_s2_inv"]["max"],
        nominal["tidal_frobenius_norm_s2_inv"]["max"],
        upper["tidal_frobenius_norm_s2_inv"]["max"],
    ]

    return {
        "schema": "LOOM_E1_NEPTUNE_J2_CORRECTED_LOCAL_TIDAL_REFERENCE_V1",
        "status": "PASS",
        "endpoint": {
            "body": "NEPTUNE",
            "collapse_radius_km": EARNED_COLLAPSE_RADIUS_KM,
            "collapse_epoch_utc": EARNED_COLLAPSE_EPOCH_UTC,
            "arrival_epoch_utc": EARNED_ARRIVAL_EPOCH_UTC,
            "altitude_above_mean_radius_km": altitude,
            "endpoint_status": "EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY",
            "endpoint_moved_or_resolved_again": False,
        },
        "inputs": {
            "gm_km3_s2": NEPTUNE_GM_KM3_S2,
            "mean_radius_km": NEPTUNE_MEAN_RADIUS_KM,
            "gravity_reference_radius_km": NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM,
            "j2": NEPTUNE_J2,
            "j2_sigma": NEPTUNE_J2_SIGMA,
            "gravity_provenance": "Brozovic_et_al_2020_values_as_tabulated_by_Yuan_et_al_2021_AA_654_A66",
            "gm_provenance": "data/LOOM_2226.sqlite3 via e1_geometric_admissibility_inventory.py",
        },
        "monopole_reference": {
            "tidal_frobenius_norm_s2_inv": monopole_norm,
            "reference_model": "SPHERICAL_MONOPOLE_WEAK_FIELD",
        },
        "j2_corrected_tidal_reference": {
            "reference_model": "AXISYMMETRIC_MONOPOLE_PLUS_MEASURED_J2_WEAK_FIELD_TIDAL_ENVELOPE",
            "single_endpoint_orientation_claimed": False,
            "max_abs_trace_s2_inv": nominal["max_abs_trace_s2_inv"],
            "orientation_envelope": nominal,
        },
        "source_uncertainty_envelope": {
            "scope": "PUBLISHED_J2_1SIGMA_ONLY_NOT_2226_MODEL_EVOLUTION",
            "orientation_policy": "FULL_COLATITUDE_SWEEP_FOR_EACH_J2_BOUND",
            "j2_lower_1sigma": NEPTUNE_J2 - NEPTUNE_J2_SIGMA,
            "j2_upper_1sigma": NEPTUNE_J2 + NEPTUNE_J2_SIGMA,
            "tidal_frobenius_norm_s2_inv": {
                "global_min_across_j2_1sigma_and_orientation": min(uncertainty_norm_mins),
                "global_max_across_j2_1sigma_and_orientation": max(uncertainty_norm_maxs),
            },
            "2226_gravity_field_evolution_treated_as_zero": False,
        },
        "qualified_claims": [
            "neptune_j2_corrected_local_tidal_orientation_envelope_at_earned_endpoint",
            "published_j2_1sigma_propagated_through_orientation_envelope",
            "j2_corrected_tidal_tensor_remains_trace_free_to_numerical_precision",
        ],
        "preserved_unresolved": [
            "unmeasured_j6_and_higher_zonal_harmonics",
            "endpoint_planetographic_latitude_and_orientation",
            "2226_neptune_gravity_field_evolution",
            "full_rotating_neptune_spacetime",
            "local_stress_energy_matter_density",
            "em_to_metric_coupling",
            "causal_structure_from_eventual_qualified_spacetime",
            "domain_size_binding_to_admissibility",
            "loom_coherence",
            "lattice_coherence",
        ],
        "admissibility_threshold_defined": False,
        "runtime_policy_mutation": "ZERO",
        "campaign_state_mutation": "ZERO",
        "llm_calculation_authority": "ZERO",
        "authority_note": "J2_CORRECTED_REFERENCE_ENVELOPE_ONLY_NO_SCORE_NO_THRESHOLD_NO_EXCLUSION_RADIUS_NO_HILL_OR_SOI_POLICY_NO_DRIVE_COUPLING",
        "interpretation": "J2_CORRECTED_LOCAL_TIDAL_REFERENCE_QUALIFIED_ORIENTATION_REMAINS_UNRESOLVED",
        "qualified_next_step": "ASSESS_LOCAL_STRESS_ENERGY_MATTER_DENSITY_RELEVANCE_BEFORE_COMPOUND_GEOMETRIC_ADMISSIBILITY",
    }


def main() -> int:
    print(json.dumps(qualify_j2_corrected_local_tidal_reference(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
