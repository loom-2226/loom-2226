#!/usr/bin/env python3
from __future__ import annotations

"""Bounded Neptune rotation/multipole materiality screen at the earned E1 endpoint.

This module asks only whether measured/non-spherical corrections are large enough
that the already-qualified spherical-monopole local-geometry reference should be
refined before compound Geometric Admissibility work proceeds.

It does not define an admissibility threshold, exclusion radius, drive coupling,
runtime policy, or campaign-state mutation.
"""

import json
import math
from typing import Any

C_KM_S = 299_792.458
EARNED_COLLAPSE_RADIUS_KM = 26_085.768742

# Declared engineering resolution for deciding whether another local-geometry
# term is worth carrying at this stage. This is NOT a Geometric Admissibility
# threshold and has no runtime or physical-boundary authority.
LOCAL_GEOMETRY_MATERIALITY_FRACTION = 0.01

# Neptune gravity-field values used by Brozovic et al. (2020) / Yuan et al.
# (2021), with the Jacobson gravity-field reference radius. These are external
# physical source inputs for this bounded engineering experiment; they do not
# replace the versioned LOOM mean radius used for altitude reporting.
NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM = 25_225.0
NEPTUNE_J2 = 3_409.138069414930e-6
NEPTUNE_J2_SIGMA = 2.9e-6
NEPTUNE_J4 = -33.39891759006578e-6
NEPTUNE_J4_SIGMA = 2.9e-6

# Specific angular momentum estimate reported by Yuan et al. (2021), based on
# an interior-rotation period and moment-of-inertia factor, with quoted
# uncertainty dominated by the inertia factor. It is used only for an
# order-of-magnitude frame-dragging materiality screen.
NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_KM2_S = 15_903.13513325206
NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_SIGMA_KM2_S = 637.0

# Conservative multiplier used to turn a/r into a deliberately loose curvature
# relevance screen. The exact rotating-planet spacetime is not claimed here.
FRAME_DRAGGING_CONSERVATIVE_FACTOR = 10.0


def _legendre_terms(order: int, cos_theta: float) -> tuple[float, float, float, float]:
    """Return P_n, dP/dtheta, d2P/dtheta2, cot(theta)dP/dtheta for n=2 or 4."""
    c = float(cos_theta)
    s2 = max(0.0, 1.0 - c * c)
    s = math.sqrt(s2)

    if order == 2:
        p = 0.5 * (3.0 * c * c - 1.0)
        dp_dc = 3.0 * c
        d2p_dc2 = 3.0
    elif order == 4:
        p = (35.0 * c**4 - 30.0 * c * c + 3.0) / 8.0
        dp_dc = (140.0 * c**3 - 60.0 * c) / 8.0
        d2p_dc2 = (420.0 * c * c - 60.0) / 8.0
    else:
        raise ValueError("only J2 and J4 are supported by this measured-harmonic screen")

    dp_dtheta = -s * dp_dc
    d2p_dtheta2 = -c * dp_dc + s2 * d2p_dc2
    cot_theta_dp_dtheta = -c * dp_dc
    return p, dp_dtheta, d2p_dtheta2, cot_theta_dp_dtheta


def _zonal_tidal_components(
    *,
    order: int,
    coefficient: float,
    radius_km: float,
    reference_radius_km: float,
    colatitude_rad: float,
) -> tuple[float, float, float, float]:
    """Return dimensionless zonal Hessian components relative to GM/r^3.

    Components are (rr, rtheta, thetatheta, phiphi) in the local orthonormal
    spherical basis. The common GM/r^3 factor is divided out, so the result is
    suitable for a source-independent fractional materiality comparison.
    """
    radius = float(radius_km)
    reference_radius = float(reference_radius_km)
    if not math.isfinite(radius) or radius <= 0.0:
        raise ValueError("radius_km must be finite and positive")
    if not math.isfinite(reference_radius) or reference_radius <= 0.0:
        raise ValueError("reference_radius_km must be finite and positive")
    if order not in (2, 4):
        raise ValueError("only J2 and J4 are supported")

    c = math.cos(float(colatitude_rad))
    p, dp, d2p, cotdp = _legendre_terms(order, c)
    scale = float(coefficient) * (reference_radius / radius) ** order

    rr = -(order + 1.0) * (order + 2.0) * scale * p
    rtheta = (order + 2.0) * scale * dp
    thetatheta = scale * ((order + 1.0) * p - d2p)
    phiphi = scale * ((order + 1.0) * p - cotdp)
    return rr, rtheta, thetatheta, phiphi


def _fractional_frobenius(components: tuple[float, float, float, float]) -> float:
    rr, rtheta, thetatheta, phiphi = components
    correction_norm = math.sqrt(rr * rr + 2.0 * rtheta * rtheta + thetatheta * thetatheta + phiphi * phiphi)
    monopole_norm = math.sqrt(6.0)  # (+2,-1,-1) after dividing by GM/r^3
    return correction_norm / monopole_norm


def _sweep_single_harmonic(*, order: int, coefficient: float, samples: int = 721) -> dict[str, Any]:
    if samples < 181:
        raise ValueError("samples must cover the orientation envelope with at least 181 points")

    fractions: list[float] = []
    colatitudes: list[float] = []
    for index in range(samples):
        colatitude_deg = 180.0 * index / (samples - 1)
        components = _zonal_tidal_components(
            order=order,
            coefficient=coefficient,
            radius_km=EARNED_COLLAPSE_RADIUS_KM,
            reference_radius_km=NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM,
            colatitude_rad=math.radians(colatitude_deg),
        )
        fractions.append(_fractional_frobenius(components))
        colatitudes.append(colatitude_deg)

    max_index = max(range(samples), key=fractions.__getitem__)
    min_index = min(range(samples), key=fractions.__getitem__)
    maximum = fractions[max_index]
    minimum = fractions[min_index]
    return {
        "order": order,
        "max_tidal_tensor_fraction": maximum,
        "max_at_colatitude_deg": colatitudes[max_index],
        "min_tidal_tensor_fraction": minimum,
        "min_at_colatitude_deg": colatitudes[min_index],
        "material_at_declared_resolution": maximum >= LOCAL_GEOMETRY_MATERIALITY_FRACTION,
    }


def measured_zonal_materiality_sweep(*, j2: float = NEPTUNE_J2, j4: float = NEPTUNE_J4) -> dict[str, Any]:
    """Sweep all colatitudes because endpoint latitude has not been qualified."""
    samples = 721
    return {
        "orientation_policy": "FULL_COLATITUDE_SWEEP_NO_ENDPOINT_LATITUDE_ASSUMED",
        "colatitude_min_deg": 0.0,
        "colatitude_max_deg": 180.0,
        "samples": samples,
        "gravity_reference_radius_km": NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM,
        "j2_only": _sweep_single_harmonic(order=2, coefficient=j2, samples=samples),
        "j4_only": _sweep_single_harmonic(order=4, coefficient=j4, samples=samples),
    }


def rotation_materiality_screen(
    *,
    specific_angular_momentum_km2_s: float = NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_KM2_S,
) -> dict[str, Any]:
    """Return a conservative dimensionless spin-curvature relevance screen.

    a/r = (J/Mc)/r is the natural dimensionless spin-length ratio. Multiplying
    it by ten deliberately over-screens order-unity angular factors. This is not
    a Kerr fit, a full Lense-Thirring solution, or a rotating-Neptune metric.
    """
    specific_h = float(specific_angular_momentum_km2_s)
    if not math.isfinite(specific_h) or specific_h <= 0.0:
        raise ValueError("specific angular momentum must be finite and positive")

    spin_length_km = specific_h / C_KM_S
    spin_length_ratio = spin_length_km / EARNED_COLLAPSE_RADIUS_KM
    conservative_fraction = FRAME_DRAGGING_CONSERVATIVE_FACTOR * spin_length_ratio
    return {
        "specific_angular_momentum_km2_s": specific_h,
        "spin_length_km": spin_length_km,
        "specific_angular_momentum_spin_length_ratio": spin_length_ratio,
        "conservative_factor": FRAME_DRAGGING_CONSERVATIVE_FACTOR,
        "conservative_frame_dragging_curvature_scale_fraction": conservative_fraction,
        "material_at_declared_resolution": conservative_fraction >= LOCAL_GEOMETRY_MATERIALITY_FRACTION,
        "authority": "MATERIALITY_SCREEN_NOT_FULL_ROTATING_SPACETIME_SOLUTION",
    }


def _classification_stable(*, nominal: float, sigma: float, order: int, expected_material: bool) -> bool:
    classifications = []
    for value in (nominal - sigma, nominal + sigma):
        result = _sweep_single_harmonic(order=order, coefficient=value)
        classifications.append(bool(result["material_at_declared_resolution"]))
    return all(item is expected_material for item in classifications)


def qualify_neptune_rotation_multipole_materiality() -> dict[str, Any]:
    zonals = measured_zonal_materiality_sweep()
    rotation = rotation_materiality_screen()

    rotation_low = rotation_materiality_screen(
        specific_angular_momentum_km2_s=(
            NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_KM2_S - NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_SIGMA_KM2_S
        )
    )
    rotation_high = rotation_materiality_screen(
        specific_angular_momentum_km2_s=(
            NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_KM2_S + NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_SIGMA_KM2_S
        )
    )

    uncertainty = {
        "j2_sigma": NEPTUNE_J2_SIGMA,
        "j4_sigma": NEPTUNE_J4_SIGMA,
        "specific_angular_momentum_sigma_km2_s": NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_SIGMA_KM2_S,
        "j2_materiality_classification_stable_at_1sigma": _classification_stable(
            nominal=NEPTUNE_J2, sigma=NEPTUNE_J2_SIGMA, order=2, expected_material=True
        ),
        "j4_materiality_classification_stable_at_1sigma": _classification_stable(
            nominal=NEPTUNE_J4, sigma=NEPTUNE_J4_SIGMA, order=4, expected_material=False
        ),
        "rotation_materiality_classification_stable_at_1sigma": (
            not rotation_low["material_at_declared_resolution"]
            and not rotation_high["material_at_declared_resolution"]
        ),
        "unmeasured_higher_zonals_treated_as_zero": False,
        "uncertainty_scope": "PUBLISHED_SOURCE_PARAMETER_1SIGMA_ONLY_NOT_2226_MODEL_EVOLUTION",
    }

    return {
        "schema": "LOOM_E1_NEPTUNE_ROTATION_MULTIPOLE_MATERIALITY_V1",
        "status": "PASS",
        "endpoint": {
            "body": "NEPTUNE",
            "collapse_radius_km": EARNED_COLLAPSE_RADIUS_KM,
            "endpoint_status": "EARNED_OPERATIONAL_HANDOFF_NOT_FUNDAMENTAL_BOUNDARY",
        },
        "materiality_resolution": {
            "fraction": LOCAL_GEOMETRY_MATERIALITY_FRACTION,
            "purpose": "ENGINEERING_LOCAL_GEOMETRY_MODEL_RESOLUTION_ONLY",
            "not_an_admissibility_threshold": True,
        },
        "source_inputs": {
            "gravity_reference_radius_km": NEPTUNE_GRAVITY_REFERENCE_RADIUS_KM,
            "j2": NEPTUNE_J2,
            "j2_sigma": NEPTUNE_J2_SIGMA,
            "j4": NEPTUNE_J4,
            "j4_sigma": NEPTUNE_J4_SIGMA,
            "specific_angular_momentum_km2_s": NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_KM2_S,
            "specific_angular_momentum_sigma_km2_s": NEPTUNE_SPECIFIC_ANGULAR_MOMENTUM_SIGMA_KM2_S,
            "gravity_provenance": "Brozovic_et_al_2020_values_as_tabulated_by_Yuan_et_al_2021_AA_654_A66",
            "spin_provenance": "Yuan_et_al_2021_AA_654_A66_specific_angular_momentum_estimate",
        },
        "measured_zonal_sweep": zonals,
        "rotation_screen": rotation,
        "source_uncertainty_screen": uncertainty,
        "decision": "J2_MATERIAL_INCLUDE_BOUNDED_CORRECTION_FRAME_DRAGGING_AND_J4_NOT_MATERIAL_AT_THIS_STAGE",
        "qualified_next_step": "QUALIFY_J2_CORRECTED_LOCAL_TIDAL_REFERENCE_WITHOUT_MOVING_EARNED_ENDPOINT",
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
        "authority_note": "MATERIALITY_ONLY_NO_SCORE_NO_EXCLUSION_RADIUS_NO_HILL_OR_SOI_POLICY_NO_DRIVE_COUPLING",
    }


def main() -> int:
    print(json.dumps(qualify_neptune_rotation_multipole_materiality(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
