#!/usr/bin/env python3
from __future__ import annotations

"""Qualify whether local stress-energy is material to the earned Neptune geometry reference.

This is a bounded standard-GR engineering materiality screen. It preserves the earned
E1 endpoint and the qualified J2-corrected tidal reference. Observational atmosphere,
magnetic-field, and plasma values are used only as present-day scale proxies; they do
not assert a known 2226 Neptune environment and do not introduce LOOM-specific
EM-to-metric coupling.
"""

import json
import math
from typing import Any

EARNED_COLLAPSE_RADIUS_KM = 26_085.768742
MINIMUM_J2_CORRECTED_TIDAL_FROBENIUS_S2_INV = 9.253496458704657e-7
MATERIALITY_RESOLUTION_FRACTION = 0.01

G_M3_KG_S2 = 6.67430e-11
C_M_S = 299_792_458.0
K_B_J_K = 1.380649e-23
H_ATOM_KG = 1.6735575e-27
H2_MOLECULE_KG = 2.0 * H_ATOM_KG
MU0_N_A2 = 4.0 * math.pi * 1e-7
EV_J = 1.602176634e-19

# Present-day observational proxies only.
# Melin et al. 2018 summarize Lyons (1995)/Voyager radio-occultation ionosphere
# modeling: ~1.1 nbar and ~550 K around 1400 km above the 1-bar level.
ATMOSPHERE_PROXY_PRESSURE_PA = 1.1e-4
ATMOSPHERE_PROXY_TEMPERATURE_K = 550.0

# Connerney et al. 1991 Voyager magnetic-field solution reports a 0.14 G R_N^3
# dipole magnitude. This is used only as a planetary-field scale proxy, not as a
# resolved endpoint field magnitude; higher harmonics and endpoint orientation remain unresolved.
MAGNETIC_FIELD_PROXY_GAUSS = 0.14

# Voyager particles/fields summaries report plasma generally ~5e-3 cm^-3 and up to
# ~1 cm^-3 at magnetic-equatorial crossings. We use the larger density plus an
# intentionally conservative 100 keV per-particle energy stress-test scale.
PLASMA_PROXY_NUMBER_DENSITY_CM3 = 1.0
PLASMA_PROXY_PARTICLE_ENERGY_KEV = 100.0


def _ricci_to_tidal_ratio_from_equivalent_mass_density(rho_kg_m3: float) -> float:
    """Compare standard-GR local source curvature scale to the qualified tidal scale.

    Einstein-equation source scale: 8*pi*G*rho/c^2 [1/m^2].
    Tidal geometric scale: lambda/c^2 [1/m^2], where lambda is in s^-2.
    c^2 cancels in the ratio, leaving 8*pi*G*rho/lambda.
    """
    return 8.0 * math.pi * G_M3_KG_S2 * rho_kg_m3 / MINIMUM_J2_CORRECTED_TIDAL_FROBENIUS_S2_INV


def _atmosphere_proxy() -> dict[str, Any]:
    n = ATMOSPHERE_PROXY_PRESSURE_PA / (K_B_J_K * ATMOSPHERE_PROXY_TEMPERATURE_K)
    rho = n * H2_MOLECULE_KG
    ratio = _ricci_to_tidal_ratio_from_equivalent_mass_density(rho)
    return {
        "role": "PRESENT_DAY_SCALE_PROXY_NOT_2226_STATE",
        "pressure_pa": ATMOSPHERE_PROXY_PRESSURE_PA,
        "temperature_k": ATMOSPHERE_PROXY_TEMPERATURE_K,
        "composition_proxy": "H2_ONLY_FOR_CONSERVATIVE_MASS_DENSITY_SCALE",
        "h2_number_density_m3": n,
        "h2_mass_density_kg_m3": rho,
        "ricci_to_tidal_materiality_ratio": ratio,
        "material_at_one_percent_resolution": ratio >= MATERIALITY_RESOLUTION_FRACTION,
        "provenance": "Melin_et_al_2018_summary_of_Lyons_1995_and_Broadfoot_et_al_1989_Voyager_results",
    }


def _magnetic_proxy() -> dict[str, Any]:
    field_t = MAGNETIC_FIELD_PROXY_GAUSS * 1e-4
    energy_density = field_t * field_t / (2.0 * MU0_N_A2)
    equivalent_rho = energy_density / (C_M_S * C_M_S)
    ratio = _ricci_to_tidal_ratio_from_equivalent_mass_density(equivalent_rho)
    return {
        "role": "PRESENT_DAY_PLANETARY_FIELD_SCALE_PROXY_NOT_ENDPOINT_FIELD_BOUND",
        "field_gauss": MAGNETIC_FIELD_PROXY_GAUSS,
        "field_tesla": field_t,
        "magnetic_energy_density_j_m3": energy_density,
        "equivalent_mass_density_kg_m3": equivalent_rho,
        "ricci_to_tidal_materiality_ratio": ratio,
        "material_at_one_percent_resolution": ratio >= MATERIALITY_RESOLUTION_FRACTION,
        "provenance": "Connerney_Acuna_Ness_1991_Voyager_2_Neptune_magnetic_field_model",
    }


def _plasma_proxy() -> dict[str, Any]:
    n_m3 = PLASMA_PROXY_NUMBER_DENSITY_CM3 * 1e6
    particle_energy_j = PLASMA_PROXY_PARTICLE_ENERGY_KEV * 1e3 * EV_J
    energy_density = n_m3 * particle_energy_j
    equivalent_rho = energy_density / (C_M_S * C_M_S)
    ratio = _ricci_to_tidal_ratio_from_equivalent_mass_density(equivalent_rho)
    return {
        "role": "PRESENT_DAY_HIGH_DENSITY_PROXY_WITH_CONSERVATIVE_PARTICLE_ENERGY_STRESS_TEST",
        "number_density_cm3": PLASMA_PROXY_NUMBER_DENSITY_CM3,
        "particle_energy_kev": PLASMA_PROXY_PARTICLE_ENERGY_KEV,
        "energy_density_j_m3": energy_density,
        "equivalent_mass_density_kg_m3": equivalent_rho,
        "ricci_to_tidal_materiality_ratio": ratio,
        "material_at_one_percent_resolution": ratio >= MATERIALITY_RESOLUTION_FRACTION,
        "density_provenance": "Krimigis_et_al_1992_Voyager_2_particles_and_fields_summary",
        "energy_scope": "ENGINEERING_STRESS_TEST_NOT_CLAIMED_CHARACTERISTIC_PLASMA_TEMPERATURE",
    }


def _one_percent_requirements() -> dict[str, Any]:
    rho_required = (
        MATERIALITY_RESOLUTION_FRACTION
        * MINIMUM_J2_CORRECTED_TIDAL_FROBENIUS_S2_INV
        / (8.0 * math.pi * G_M3_KG_S2)
    )
    energy_density_required = rho_required * C_M_S * C_M_S
    h2_pressure = rho_required / H2_MOLECULE_KG * K_B_J_K * ATMOSPHERE_PROXY_TEMPERATURE_K
    magnetic_field = math.sqrt(2.0 * MU0_N_A2 * energy_density_required)
    return {
        "materiality_resolution_fraction": MATERIALITY_RESOLUTION_FRACTION,
        "equivalent_mass_density_kg_m3": rho_required,
        "equivalent_energy_density_j_m3": energy_density_required,
        "h2_pressure_at_550k_pa": h2_pressure,
        "h2_pressure_at_550k_bar": h2_pressure / 1e5,
        "magnetic_field_tesla": magnetic_field,
        "magnetic_field_gauss": magnetic_field * 1e4,
        "interpretation": "SOURCE_STRENGTH_REQUIRED_FOR_STANDARD_GR_LOCAL_RICCI_SCALE_TO_REACH_ONE_PERCENT_OF_QUALIFIED_TIDAL_SCALE",
    }


def qualify_local_stress_energy_materiality() -> dict[str, Any]:
    atmosphere = _atmosphere_proxy()
    magnetic = _magnetic_proxy()
    plasma = _plasma_proxy()
    required = _one_percent_requirements()

    return {
        "schema": "LOOM_E1_NEPTUNE_LOCAL_STRESS_ENERGY_MATERIALITY_V1",
        "status": "PASS",
        "endpoint": {
            "body": "NEPTUNE",
            "collapse_radius_km": EARNED_COLLAPSE_RADIUS_KM,
            "endpoint_moved_or_resolved_again": False,
        },
        "qualified_local_geometry_reference": {
            "minimum_j2_corrected_tidal_frobenius_s2_inv": MINIMUM_J2_CORRECTED_TIDAL_FROBENIUS_S2_INV,
            "reference_origin": "E1_NEPTUNE_J2_CORRECTED_LOCAL_TIDAL_REFERENCE_V1",
            "comparison_role": "CONSERVATIVE_LOW_END_OF_QUALIFIED_TIDAL_NORM_ENVELOPE",
        },
        "materiality_model": {
            "gravity_theory": "STANDARD_GENERAL_RELATIVITY_ONLY",
            "comparison": "LOCAL_RICCI_SOURCE_SCALE_VS_QUALIFIED_NEPTUNE_TIDAL_GEOMETRIC_SCALE",
            "materiality_resolution_fraction": MATERIALITY_RESOLUTION_FRACTION,
            "note": "ORDER_OF_MAGNITUDE_ENGINEERING_SCREEN_NOT_FULL_EINSTEIN_MAXWELL_OR_ATMOSPHERE_SOLUTION",
        },
        "observational_screens": {
            "upper_atmosphere_proxy": atmosphere,
            "magnetic_field_proxy": magnetic,
            "plasma_proxy": plasma,
        },
        "one_percent_materiality_requirements": required,
        "uncertainty": {
            "2226_neptune_atmosphere_treated_as_known": False,
            "2226_neptune_magnetosphere_treated_as_known": False,
            "endpoint_magnetic_field_orientation_treated_as_known": False,
            "endpoint_plasma_state_treated_as_known": False,
            "loom_specific_em_metric_coupling_assumed": False,
            "present_day_proxies_extrapolated_to_2226": False,
        },
        "qualified_claims": [
            "present_day_neptune_upper_atmosphere_scale_is_far_below_one_percent_standard_gr_materiality",
            "present_day_planetary_magnetic_field_scale_is_far_below_one_percent_standard_gr_materiality",
            "conservative_neptune_plasma_energy_density_screen_is_far_below_one_percent_standard_gr_materiality",
            "one_percent_standard_gr_local_source_requirements_are_explicit",
        ],
        "preserved_unresolved": [
            "2226_local_atmospheric_state",
            "2226_local_magnetospheric_state",
            "endpoint_planetographic_latitude_and_orientation",
            "endpoint_magnetic_field_vector",
            "unmeasured_j6_and_higher_zonal_harmonics",
            "full_rotating_neptune_spacetime",
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
        "decision": "LOCAL_STRESS_ENERGY_NOT_MATERIAL_AT_ONE_PERCENT_STANDARD_GR_SCREEN_PRESERVE_2226_ENVIRONMENT_UNCERTAINTY",
        "authority_note": "MATERIALITY_SCREEN_ONLY_NO_RUNTIME_BINDING_NO_EXCLUSION_RADIUS_NO_DRIVE_COUPLING_NO_2226_ENVIRONMENT_CLAIM",
        "qualified_next_step": "ASSESS_COMPOUND_GEOMETRIC_ADMISSIBILITY_MODEL_FORM_WITHOUT_BINDING_RUNTIME_POLICY",
    }


def main() -> int:
    print(json.dumps(qualify_local_stress_energy_materiality(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
