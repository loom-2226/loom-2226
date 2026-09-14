from __future__ import annotations

"""Configuration-aware Wayfarer mass and inertia engineering model.

This module promotes no canon and claims no FEA-grade internal mass distribution.
It turns the existing governed mass ledger plus explicit equivalent-shape assumptions
into a deterministic full rigid-body tensor suitable for RCS requalification.
Every shape assumption is exposed in the returned evidence.
"""

import math
from typing import Any

SCHEMA = "LOOM.Wayfarer.MassInertiaState"
SCHEMA_VERSION = "0.1"

# Existing engineering mass ledger lineage recovered from the Q4/HUD/Shipyard work.
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

_LAUNCH = ("planetary_launch", 33.0, 21.8, 0.0, 5.2)
_TANK_X_M = 25.0
_TANK_CENTER_RADIUS_M = 2.7
_PROTECTED_WATER_X_M = 12.5

# Equivalent shapes are engineering surrogates, not literal structural meshes.
# tuple forms:
#   ("CYLINDER_X", length_m, radius_m)
#   ("BOX", x_m, y_m, z_m)
_SHAPES = {
    "structure": ("CYLINDER_X", 57.0, 4.5),
    "armor_fixed_shield": ("CYLINDER_X", 19.0, 4.3),
    "habitation_life_support": ("CYLINDER_X", 14.0, 4.3),
    "relational_plant": ("CYLINDER_X", 16.0, 2.25),
    "thermal_radiators": ("CYLINDER_X", 5.0, 4.5),
    "propulsion": ("CYLINDER_X", 14.0, 3.0),
    "electrical": ("CYLINDER_X", 8.0, 2.5),
    "avionics_sensors_comms": ("CYLINDER_X", 6.0, 3.5),
    "rcs_docking_service": ("CYLINDER_X", 20.0, 4.5),
    "mission_courier_systems": ("CYLINDER_X", 8.0, 3.5),
    "engineering_reserve": ("CYLINDER_X", 20.0, 4.0),
    "planetary_launch": ("BOX", 10.5, 3.9, 3.1),
    "protected_water": ("CYLINDER_X", 5.0, 2.0),
}

_TANK_SHAPE = ("CYLINDER_X", 14.0, 1.5)


def _element(name: str, mass_t: float, x_m: float, y_m: float, z_m: float, source: str) -> dict[str, Any]:
    return {
        "name": name,
        "mass_t": float(mass_t),
        "position_m": [float(x_m), float(y_m), float(z_m)],
        "source": source,
    }


def _build_elements(normal_remass_t: float, protected_water_t: float, launch_docked: bool) -> list[dict[str, Any]]:
    if not 0.0 <= normal_remass_t <= 250.0:
        raise ValueError("normal_remass_t must be in 0..250")
    if not 0.0 <= protected_water_t <= 50.0:
        raise ValueError("protected_water_t must be in 0..50")

    elements = [
        _element(name, mass_t, x, y, z, "RECOVERED_ENGINEERING_MASS_LEDGER")
        for name, mass_t, x, y, z in _DRY_LEDGER
    ]
    if launch_docked:
        elements.append(_element(*_LAUNCH, source="WAYFARER_LAUNCH_DOCKED_CONFIGURATION"))

    per_tank_t = normal_remass_t / 4.0
    for idx, angle_deg in enumerate((45.0, 135.0, 225.0, 315.0), 1):
        angle = math.radians(angle_deg)
        elements.append(
            _element(
                f"normal_remass_tank_{idx}",
                per_tank_t,
                _TANK_X_M,
                _TANK_CENTER_RADIUS_M * math.cos(angle),
                _TANK_CENTER_RADIUS_M * math.sin(angle),
                "BALANCED_FOUR_TANK_REMASS_STATE",
            )
        )

    elements.append(
        _element(
            "protected_water",
            protected_water_t,
            _PROTECTED_WATER_X_M,
            0.0,
            0.0,
            "PROTECTED_WATER_STORE_STATE",
        )
    )
    return elements


def _center_of_mass(elements: list[dict[str, Any]]) -> tuple[float, list[float]]:
    total_kg = sum(e["mass_t"] * 1000.0 for e in elements)
    if total_kg <= 0.0:
        raise ValueError("total mass must be positive")
    com = [
        sum(e["mass_t"] * 1000.0 * e["position_m"][axis] for e in elements) / total_kg
        for axis in range(3)
    ]
    return total_kg, com


def _intrinsic_diag(name: str, mass_kg: float) -> tuple[float, float, float]:
    shape = _TANK_SHAPE if name.startswith("normal_remass_tank_") else _SHAPES.get(name)
    if shape is None:
        raise ValueError(f"no equivalent-shape assumption for {name}")
    if shape[0] == "CYLINDER_X":
        _, length_m, radius_m = shape
        ixx = 0.5 * mass_kg * radius_m**2
        transverse = mass_kg * (3.0 * radius_m**2 + length_m**2) / 12.0
        return ixx, transverse, transverse
    if shape[0] == "BOX":
        _, lx, ly, lz = shape
        return (
            mass_kg * (ly**2 + lz**2) / 12.0,
            mass_kg * (lx**2 + lz**2) / 12.0,
            mass_kg * (lx**2 + ly**2) / 12.0,
        )
    raise ValueError(f"unsupported equivalent shape {shape[0]}")


def _tensor(elements: list[dict[str, Any]], com: list[float], include_intrinsic: bool) -> list[list[float]]:
    ixx = iyy = izz = ixy = ixz = iyz = 0.0
    cx, cy, cz = com
    for e in elements:
        m = e["mass_t"] * 1000.0
        x, y, z = e["position_m"]
        dx, dy, dz = x - cx, y - cy, z - cz
        if include_intrinsic:
            qxx, qyy, qzz = _intrinsic_diag(e["name"], m)
        else:
            qxx = qyy = qzz = 0.0
        ixx += qxx + m * (dy * dy + dz * dz)
        iyy += qyy + m * (dx * dx + dz * dz)
        izz += qzz + m * (dx * dx + dy * dy)
        ixy -= m * dx * dy
        ixz -= m * dx * dz
        iyz -= m * dy * dz
    return [[ixx, ixy, ixz], [ixy, iyy, iyz], [ixz, iyz, izz]]


def _det3(m: list[list[float]]) -> float:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def _tensor_checks(tensor: list[list[float]]) -> dict[str, Any]:
    symmetric = all(
        math.isclose(tensor[i][j], tensor[j][i], rel_tol=0.0, abs_tol=1e-6)
        for i in range(3)
        for j in range(3)
    )
    minor1 = tensor[0][0]
    minor2 = tensor[0][0] * tensor[1][1] - tensor[0][1] * tensor[1][0]
    minor3 = _det3(tensor)
    return {
        "symmetric": symmetric,
        "leading_principal_minors": [minor1, minor2, minor3],
        "positive_definite_sylvester": symmetric and minor1 > 0.0 and minor2 > 0.0 and minor3 > 0.0,
    }


def _shape_assumptions(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for e in elements:
        shape = _TANK_SHAPE if e["name"].startswith("normal_remass_tank_") else _SHAPES[e["name"]]
        result.append(
            {
                "component": e["name"],
                "equivalent_shape": list(shape),
                "status": "ENGINEERING_EQUIVALENT_SHAPE_ASSUMPTION",
                "literal_geometry_claim": False,
            }
        )
    return result


def build_mass_inertia_state(
    *,
    normal_remass_t: float,
    protected_water_t: float = 50.0,
    launch_docked: bool = True,
) -> dict[str, Any]:
    elements = _build_elements(normal_remass_t, protected_water_t, launch_docked)
    total_kg, com = _center_of_mass(elements)
    full_tensor = _tensor(elements, com, include_intrinsic=True)
    centroid_only = _tensor(elements, com, include_intrinsic=False)
    checks = _tensor_checks(full_tensor)
    if not checks["positive_definite_sylvester"]:
        raise RuntimeError("computed Wayfarer inertia tensor is not positive definite")

    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "mass_t": total_kg / 1000.0,
        "center_of_mass_m": com,
        "inertia_tensor_kg_m2": full_tensor,
        "inertia_diag_kg_m2": [full_tensor[0][0], full_tensor[1][1], full_tensor[2][2]],
        "intrinsic_component_inertia_included": True,
        "normal_remass_t": float(normal_remass_t),
        "protected_water_t": float(protected_water_t),
        "launch_state": "DOCKED" if launch_docked else "ABSENT",
        "depletion_doctrine": "BALANCED_FOUR_TANK_DRAW",
        "elements": elements,
        "equivalent_shape_assumptions": _shape_assumptions(elements),
        "centroid_only_comparator": {
            "inertia_tensor_kg_m2": centroid_only,
            "semantics": "PARALLEL_AXIS_CENTROID_ONLY_DIAGNOSTIC_NOT_FLIGHT_AUTHORITY",
        },
        "model_delta_from_centroid_only": {
            "roll_Ixx_added_kg_m2": full_tensor[0][0] - centroid_only[0][0],
            "pitch_Iyy_added_kg_m2": full_tensor[1][1] - centroid_only[1][1],
            "yaw_Izz_added_kg_m2": full_tensor[2][2] - centroid_only[2][2],
            "semantics": "INTRINSIC_EQUIVALENT_SHAPE_CONTRIBUTION_NOT_UNCERTAINTY_BOUND",
        },
        "tensor_checks": checks,
        "source_lineage": [
            "canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md",
            "canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md",
            "PR_96_Q4_MASS_PROPERTIES_AND_RIGID_BODY_ENGINEERING",
            "COMPUTATIONAL_SHIPYARD_PHASE5B_INERTIA_AUTHORITY_FINDING",
            "PR_184_E1_RCS_RECOVERY_AND_FLIGHT_PHYSICS_OBJECTIVE",
        ],
        "open_physics": [
            "radiator_deployed_mass_distribution",
            "fluid_slosh_and_free_surface_dynamics",
            "flexible_body_modes",
            "structural_fea_mass_distribution",
            "moving_internal_masses_beyond_declared_stores",
        ],
        "authority": {
            "status": "ENGINEERING_MODEL_FOR_RCS_REQUALIFICATION",
            "configuration_aware_mass_authority": True,
            "configuration_aware_com_authority": True,
            "full_rigid_body_tensor_model_present": True,
            "structural_fea_authority": False,
            "fluid_slosh_authority": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
        "qualified_next_step": "REQUALIFY_RCS_WRENCH_AND_FINITE_ATTITUDE_AUTHORITY_AGAINST_THIS_CONFIGURATION_AWARE_TENSOR",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(build_mass_inertia_state(normal_remass_t=250.0, protected_water_t=50.0, launch_docked=True), indent=2, sort_keys=True))
