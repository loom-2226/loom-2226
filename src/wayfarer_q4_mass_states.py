from __future__ import annotations

import math

from src.wayfarer_mass_properties import center_of_mass, point_mass_inertia_tensor


# Current engineering mass ledger centroids. Composite subsystem intrinsic tensors
# are not yet admitted; this module improves Q4 specifically by restoring the
# known radial distribution of the four normal-remass tanks and launch offset.
_DRY_LEDGER = (
    ("structure", 150.0, 28.0, 0.0, 0.0),
    ("armor_fixed_shield", 105.0, 9.5, 0.0, 0.0),
    ("habitation_life_support", 45.0, 8.0, 0.0, 0.0),
    ("relational_plant", 88.0, 26.0, 0.0, 0.0),
    ("thermal_radiators", 90.0, 35.0, 0.0, 0.0),
    ("propulsion", 160.0, 46.5, 0.0, 0.0),
    ("electrical", 55.0, 31.0, 0.0, 0.0),
    ("avionics_sensors_comms", 20.0, 12.0, 0.0, 0.0),
    ("rcs_docking_service", 25.0, 28.0, 0.0, 0.0),
    ("mission_courier_systems", 20.0, 17.0, 0.0, 0.0),
    ("engineering_reserve", 67.5, 28.0, 0.0, 0.0),
)

LAUNCH = ("planetary_launch", 33.0, 21.8, 0.0, 5.2)
TANK_X_M = 25.0
TANK_CENTER_RADIUS_M = 2.7
PROTECTED_WATER_X_M = 12.5


def _element(name: str, mass_t: float, x_m: float, y_m: float, z_m: float, kind: str) -> dict:
    return {
        "name": name,
        "mass_t": float(mass_t),
        "x_m": float(x_m),
        "y_m": float(y_m),
        "z_m": float(z_m),
        "kind": kind,
    }


def build_q4_mass_state(*, normal_remass_t: float, protected_water_t: float = 50.0, launch_docked: bool = True) -> dict:
    """Build Q4 centroid mass state with known tank radial geometry restored.

    Normal remass is depleted symmetrically across all four tanks. The resulting
    tensor is still not the final rigid-body tensor because composite subsystem
    intrinsic shape inertias remain open.
    """
    if normal_remass_t < 0 or normal_remass_t > 250.0:
        raise ValueError("normal_remass_t must be in 0..250")
    if protected_water_t < 0 or protected_water_t > 50.0:
        raise ValueError("protected_water_t must be in 0..50")

    elements = [_element(n, m, x, y, z, "DRY_LEDGER_CENTROID") for n, m, x, y, z in _DRY_LEDGER]
    if launch_docked:
        elements.append(_element(*LAUNCH, kind="PLANETARY_LAUNCH"))

    per_tank = normal_remass_t / 4.0
    for idx, angle_deg in enumerate((45.0, 135.0, 225.0, 315.0), 1):
        angle = math.radians(angle_deg)
        elements.append(_element(
            f"normal_remass_tank_{idx}", per_tank, TANK_X_M,
            TANK_CENTER_RADIUS_M * math.cos(angle),
            TANK_CENTER_RADIUS_M * math.sin(angle),
            "NORMAL_REMASS_TANK_FLUID",
        ))

    elements.append(_element(
        "protected_water", protected_water_t, PROTECTED_WATER_X_M, 0.0, 0.0,
        "PROTECTED_WATER_CENTROID",
    ))

    com = center_of_mass(elements)
    inertia = point_mass_inertia_tensor(elements)
    tensor = inertia["tensor_kg_m2"]
    return {
        "contract": "WAYFARER_Q4_MASS_STATE_V0.3",
        "normal_remass_t": float(normal_remass_t),
        "protected_water_t": float(protected_water_t),
        "launch_state": "DOCKED" if launch_docked else "ABSENT",
        "mass_t": com["mass_kg"] / 1000.0,
        "center_of_mass_m": list(com["com_m"]),
        "centroid_inertia_tensor_kg_m2": [list(row) for row in tensor],
        "centroid_inertia_diag_kg_m2": [tensor[0][0], tensor[1][1], tensor[2][2]],
        "depletion_doctrine": "BALANCED_FOUR_TANK_DRAW",
        "model_quality": "CENTROID_PLUS_KNOWN_RADIAL_FLUID_DISTRIBUTION",
        "final_intrinsic_tensor_available": False,
        "elements": elements,
        "open_inertia_terms": [
            "composite_structure_intrinsic_tensor",
            "armor_habitat_intrinsic_tensor",
            "relational_plant_intrinsic_tensor",
            "radiator_state_dependent_intrinsic_tensor",
            "propulsion_intrinsic_tensor",
            "launch_intrinsic_tensor",
            "protected_water_internal_distribution",
        ],
    }
