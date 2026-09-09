from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Tuple

from physical_design_core import (
    BoxGeometry,
    CandidateDesign,
    CylinderXGeometry,
    EvaluationResult,
    HardConstraintResult,
    KeepOutCircleYZ,
    ObjectiveTerm,
    PhysicalComponentInstance,
    PhysicalComponentType,
    PhysicalDesignError,
    PointMassContribution,
    Transform,
    component_collisions,
    evaluate_mass_inertia,
)

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "WAYFARER_S0_AUTHORITY_MANIFEST_v0.1.json"
TEST_DEFINITION_PATH = HERE / "WAYFARER_S1_TEST_DEFINITION_v0.1.md"

S1_AUTHORITY_LABEL = "QUALIFICATION_CANDIDATE_NON_CANON_NON_PRODUCTION"
REFERENCE_WET_MASS_KG = 1_158_500.0
REFERENCE_REMASS_KG = 250_000.0
REFERENCE_PROTECTED_WATER_KG = 50_000.0
REFERENCE_WORKING_FLUID_WATER_KG = 300_000.0

RELATIONAL_REGION_X_M = (18.0, 34.0)
RELATIONAL_BODY = CylinderXGeometry(length_m=16.0, diameter_m=1.4)
RELATIONAL_MASS_KG = 88_000.0

LAUNCH_BAY_X_M = (16.0, 28.0)
LAUNCH_BODY = BoxGeometry(x_m=10.5, y_m=3.9, z_m=3.1)
LAUNCH_MASS_KG = 33_000.0
LAUNCH_FIXED_YZ_M = (0.0, 5.2)

TANK_STATION_X_M = (18.0, 32.0)
TANK_COUNT = 4
TANK_MASS_KG = 62_500.0
TANK_CENTER_RADIUS_M = 2.7
TANK_CROSS_SECTION_RADIUS_M = 1.5
TANK_PHASE_RAD = math.pi / 4.0

# Fixed or abstract contributions remain point-mass centroids in S1 Mode A.
# They contribute exact mass/CoM and parallel-axis terms, but no invented
# centroidal inertia.
_FIXED_POINT_MASSES = (
    ("structure", 150_000.0, (28.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("armor_fixed_shield", 105_000.0, (9.5, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("habitation_life_support", 45_000.0, (8.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("thermal_radiators", 90_000.0, (35.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("propulsion", 160_000.0, (46.5, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("electrical", 55_000.0, (31.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("avionics_sensors_comms", 20_000.0, (12.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("rcs_docking_service", 25_000.0, (28.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("mission_courier_systems", 20_000.0, (17.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("engineering_reserve", 67_500.0, (28.0, 0.0, 0.0), "DESIGN_BASELINE", "geometry/wayfarer_geometry_seed.sql"),
    ("protected_water", 50_000.0, (12.5, 0.0, 0.0), "DESIGN_BASELINE", "qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_SEED_v0.1.sql"),
)


class WayfarerS1Error(PhysicalDesignError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_hashes() -> Dict[str, str]:
    return {
        "s0_manifest_sha256": _sha256(MANIFEST_PATH),
        "s1_test_definition_sha256": _sha256(TEST_DEFINITION_PATH),
    }


def component_types() -> Tuple[PhysicalComponentType, ...]:
    return (
        PhysicalComponentType(
            type_id="relational_plant_equivalent",
            mass_kg=RELATIONAL_MASS_KG,
            admitted_geometry=RELATIONAL_BODY,
            authority_status="QUALIFICATION_ONLY",
            provenance="qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
        ),
        PhysicalComponentType(
            type_id="planetary_launch_working_envelope",
            mass_kg=LAUNCH_MASS_KG,
            admitted_geometry=LAUNCH_BODY,
            authority_status="DESIGN_BASELINE",
            provenance="qualification/phase3/LOOM_2226_SHIPCLASSES_WAYFARER_GEOMETRY_COUPLING_v0.1.sql",
        ),
    )


def fixed_point_masses() -> Tuple[PointMassContribution, ...]:
    return tuple(
        PointMassContribution(source_id, mass, centroid, status, provenance)
        for source_id, mass, centroid, status, provenance in _FIXED_POINT_MASSES
    )


def tank_point_masses(common_x_m: float, *, tank_mass_kg: float = TANK_MASS_KG) -> Tuple[PointMassContribution, ...]:
    rows = []
    for i in range(TANK_COUNT):
        angle = TANK_PHASE_RAD + i * (2.0 * math.pi / TANK_COUNT)
        y = TANK_CENTER_RADIUS_M * math.cos(angle)
        z = TANK_CENTER_RADIUS_M * math.sin(angle)
        rows.append(
            PointMassContribution(
                source_id=f"normal_remass_tank_{i + 1}",
                mass_kg=float(tank_mass_kg),
                centroid_m=(float(common_x_m), y, z),
                authority_status="DESIGN_BASELINE",
                provenance="qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            )
        )
    return tuple(rows)


def tank_cross_section_keepouts() -> Tuple[KeepOutCircleYZ, ...]:
    rows = []
    for i in range(TANK_COUNT):
        angle = TANK_PHASE_RAD + i * (2.0 * math.pi / TANK_COUNT)
        rows.append(
            KeepOutCircleYZ(
                keep_out_id=f"tank_cross_section_{i + 1}",
                center_yz_m=(
                    TANK_CENTER_RADIUS_M * math.cos(angle),
                    TANK_CENTER_RADIUS_M * math.sin(angle),
                ),
                radius_m=TANK_CROSS_SECTION_RADIUS_M,
                authority_status="DESIGN_BASELINE_PARTIAL_GEOMETRY",
                provenance="qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
                note="Cross-section only. Tank axial length is not promoted to S1 collision authority.",
            )
        )
    return tuple(rows)


def build_candidate(
    *,
    candidate_id: str,
    seed: int,
    relational_x_m: float,
    launch_x_m: float,
    tank_x_m: float,
    solver_version: str,
    launch_yz_m: Tuple[float, float] = LAUNCH_FIXED_YZ_M,
    tank_mass_kg: float = TANK_MASS_KG,
    open_geometry_used: Tuple[str, ...] = (),
) -> CandidateDesign:
    point_masses = fixed_point_masses() + tank_point_masses(tank_x_m, tank_mass_kg=tank_mass_kg)
    return CandidateDesign(
        candidate_id=candidate_id,
        seed=int(seed),
        component_types=component_types(),
        component_instances=(
            PhysicalComponentInstance(
                "relational_plant",
                "relational_plant_equivalent",
                Transform((float(relational_x_m), 0.0, 0.0)),
            ),
            PhysicalComponentInstance(
                "planetary_launch",
                "planetary_launch_working_envelope",
                Transform((float(launch_x_m), float(launch_yz_m[0]), float(launch_yz_m[1]))),
            ),
        ),
        point_masses=point_masses,
        keep_outs=tank_cross_section_keepouts(),
        active_states={"launch_state": "DOCKED"},
        store_decomposition_kg={
            "normal_remass": TANK_COUNT * float(tank_mass_kg),
            "protected_water": REFERENCE_PROTECTED_WATER_KG,
        },
        provenance_map={
            "authority_manifest": "qualification/synthesis/WAYFARER_S0_AUTHORITY_MANIFEST_v0.1.json",
            "test_definition": "qualification/synthesis/WAYFARER_S1_TEST_DEFINITION_v0.1.md",
            "tank_axial_geometry": "OPEN_NOT_USED",
            "radiator_panel_geometry": "OPEN_NOT_USED",
            "docking_geometry": "OPEN_NOT_USED",
        },
        solver_version=solver_version,
        input_hashes=input_hashes(),
        open_geometry_used=tuple(open_geometry_used),
    )


def _instance(candidate: CandidateDesign, instance_id: str) -> PhysicalComponentInstance:
    for row in candidate.component_instances:
        if row.instance_id == instance_id:
            return row
    raise WayfarerS1Error(f"Missing required component instance {instance_id}")


def _constraint(constraint_id: str, passed: bool, detail: str) -> HardConstraintResult:
    return HardConstraintResult(constraint_id=constraint_id, passed=bool(passed), detail=detail)


def validate_candidate(candidate: CandidateDesign) -> Tuple[HardConstraintResult, ...]:
    results = []
    try:
        mass, _, _, _, _, _ = evaluate_mass_inertia(candidate)
        physical_inputs_valid = True
        physical_detail = "finite positive masses/geometry"
    except PhysicalDesignError as exc:
        mass = float("nan")
        physical_inputs_valid = False
        physical_detail = str(exc)
    results.append(_constraint("PHYSICAL_INPUTS_FINITE_POSITIVE", physical_inputs_valid, physical_detail))

    results.append(
        _constraint(
            "TOTAL_WET_MASS_EXACT",
            physical_inputs_valid and abs(mass - REFERENCE_WET_MASS_KG) <= 1e-6,
            f"resolved={mass!r} expected={REFERENCE_WET_MASS_KG}",
        )
    )

    remass = float(candidate.store_decomposition_kg.get("normal_remass", float("nan")))
    protected = float(candidate.store_decomposition_kg.get("protected_water", float("nan")))
    results.append(
        _constraint("NORMAL_REMASS_EXACT", math.isfinite(remass) and abs(remass - REFERENCE_REMASS_KG) <= 1e-6, f"resolved={remass!r}")
    )
    total_store = remass + protected
    results.append(
        _constraint(
            "WORKING_FLUID_WATER_EXACT",
            math.isfinite(total_store) and abs(total_store - REFERENCE_WORKING_FLUID_WATER_KG) <= 1e-6,
            f"resolved={total_store!r}",
        )
    )

    try:
        relational = _instance(candidate, "relational_plant")
        rx = relational.transform.translation_m[0]
        rel_x0 = rx - RELATIONAL_BODY.length_m / 2.0
        rel_x1 = rx + RELATIONAL_BODY.length_m / 2.0
        relational_ok = rel_x0 >= RELATIONAL_REGION_X_M[0] - 1e-12 and rel_x1 <= RELATIONAL_REGION_X_M[1] + 1e-12
        results.append(_constraint("RELATIONAL_ENVELOPE_IN_REGION", relational_ok, f"envelope=[{rel_x0},{rel_x1}]"))
    except WayfarerS1Error as exc:
        results.append(_constraint("RELATIONAL_ENVELOPE_IN_REGION", False, str(exc)))

    try:
        launch = _instance(candidate, "planetary_launch")
        lx, ly, lz = launch.transform.translation_m
        lx0 = lx - LAUNCH_BODY.x_m / 2.0
        lx1 = lx + LAUNCH_BODY.x_m / 2.0
        launch_in_bay = lx0 >= LAUNCH_BAY_X_M[0] - 1e-12 and lx1 <= LAUNCH_BAY_X_M[1] + 1e-12
        results.append(_constraint("LAUNCH_WITHIN_BAY", launch_in_bay, f"envelope_x=[{lx0},{lx1}]"))
        launch_side_ok = abs(ly - LAUNCH_FIXED_YZ_M[0]) <= 1e-12 and (lz - LAUNCH_BODY.z_m / 2.0) > 0.0
        results.append(_constraint("LAUNCH_PLUS_Z_EXTRACTION_SIDE", launch_side_ok, f"center_yz=[{ly},{lz}]"))
    except WayfarerS1Error as exc:
        results.append(_constraint("LAUNCH_WITHIN_BAY", False, str(exc)))
        results.append(_constraint("LAUNCH_PLUS_Z_EXTRACTION_SIDE", False, str(exc)))

    tanks = sorted((p for p in candidate.point_masses if p.source_id.startswith("normal_remass_tank_")), key=lambda p: p.source_id)
    tank_ok = len(tanks) == TANK_COUNT
    tank_detail = f"count={len(tanks)}"
    if tank_ok:
        xs = [float(p.centroid_m[0]) for p in tanks]
        masses = [float(p.mass_kg) for p in tanks]
        common_x = sum(xs) / len(xs)
        transverse_y = sum(m * float(p.centroid_m[1]) for p, m in zip(tanks, masses))
        transverse_z = sum(m * float(p.centroid_m[2]) for p, m in zip(tanks, masses))
        expected = tank_point_masses(common_x, tank_mass_kg=TANK_MASS_KG)
        topology_ok = all(
            abs(float(p.centroid_m[1]) - float(e.centroid_m[1])) <= 1e-9
            and abs(float(p.centroid_m[2]) - float(e.centroid_m[2])) <= 1e-9
            for p, e in zip(tanks, expected)
        )
        tank_ok = (
            max(xs) - min(xs) <= 1e-12
            and TANK_STATION_X_M[0] - 1e-12 <= common_x <= TANK_STATION_X_M[1] + 1e-12
            and all(abs(m - TANK_MASS_KG) <= 1e-6 for m in masses)
            and abs(transverse_y) <= 1e-6
            and abs(transverse_z) <= 1e-6
            and topology_ok
        )
        tank_detail = f"x={common_x}, masses={masses}, transverse_moments=({transverse_y},{transverse_z})"
    results.append(_constraint("TANK_QUADRATURE_MASS_STATION", tank_ok, tank_detail))

    collisions = component_collisions(candidate) if physical_inputs_valid else ()
    results.append(_constraint("ADMITTED_BODY_COLLISION_FREE", not collisions, f"collisions={collisions}"))

    results.append(
        _constraint(
            "OPEN_GEOMETRY_NOT_USED",
            len(candidate.open_geometry_used) == 0,
            f"open_geometry_used={candidate.open_geometry_used}",
        )
    )
    return tuple(results)


def _distance_to_band(value: float, low: float, high: float) -> float:
    if value < low:
        return low - value
    if value > high:
        return value - high
    return 0.0


def objective_vector(candidate: CandidateDesign, mass_kg: float, com: Tuple[float, float, float]) -> Tuple[ObjectiveTerm, ...]:
    relational = _instance(candidate, "relational_plant")
    launch = _instance(candidate, "planetary_launch")
    tanks = [p for p in candidate.point_masses if p.source_id.startswith("normal_remass_tank_")]
    tank_x = sum(float(p.centroid_m[0]) for p in tanks) / len(tanks)

    transverse = math.hypot(float(com[1]), float(com[2]))
    longitudinal = _distance_to_band(float(com[0]), 26.5, 27.0)
    rotational_surrogate = sum(
        p.mass_kg * ((p.centroid_m[1] - com[1]) ** 2 + (p.centroid_m[2] - com[2]) ** 2)
        for p in tanks
    ) + LAUNCH_MASS_KG * (
        (launch.transform.translation_m[1] - com[1]) ** 2 + (launch.transform.translation_m[2] - com[2]) ** 2
    )
    remass_feed = abs(43.0 - tank_x)
    major_power = abs(31.0 - relational.transform.translation_m[0])
    collision_penalty = float(len(component_collisions(candidate)))
    launch_extraction = abs(22.0 - launch.transform.translation_m[0])

    return (
        ObjectiveTerm("J1_TRANSVERSE_COM_OFFSET", transverse, "m", "absolute transverse CoM offset"),
        ObjectiveTerm("J2_LONGITUDINAL_COM_BAND_DEVIATION", longitudinal, "m", "distance outside qualification target band x=26.5..27.0 m"),
        ObjectiveTerm("J3_ROTATIONAL_CONTROL_BURDEN_SURROGATE", rotational_surrogate, "kg*m^2", "transverse second-moment surrogate for moved launch/remass masses"),
        ObjectiveTerm("J4_REMASS_FEED_DISTANCE_SURROGATE", remass_feed, "m", "tank common station distance to x=43 m propulsion-region boundary"),
        ObjectiveTerm("J5_MAJOR_POWER_PATH_SURROGATE", major_power, "m", "relational station distance to x=31 m electrical reference centroid"),
        ObjectiveTerm("J6_PACKAGING_COLLISION_PENALTY", collision_penalty, "count", "number of collisions between admitted full physical bodies"),
        ObjectiveTerm("J7_LAUNCH_EXTRACTION_PENALTY", launch_extraction, "m", "distance from qualification-only bay-center station x=22 m"),
    )


def evaluate_candidate(candidate: CandidateDesign, *, requested_flight_authority: bool = False) -> EvaluationResult:
    constraints = validate_candidate(candidate)
    failed = [c for c in constraints if not c.passed]
    if failed:
        detail = "; ".join(f"{c.constraint_id}: {c.detail}" for c in failed)
        raise WayfarerS1Error(f"Candidate rejected by hard constraints: {detail}")

    mass, com, pa, centroidal, aggregate, unresolved = evaluate_mass_inertia(candidate)
    if requested_flight_authority:
        raise WayfarerS1Error("S1 Mode A cannot claim flight dynamics authority")
    return EvaluationResult(
        candidate_id=candidate.candidate_id,
        mass_kg=mass,
        center_of_mass_m=com,
        parallel_axis_tensor_kg_m2=pa,
        admitted_centroidal_tensor_kg_m2=centroidal,
        candidate_aggregate_tensor_kg_m2=aggregate,
        unresolved_inertia_mass_fraction=unresolved,
        hard_constraints=constraints,
        objective_vector=objective_vector(candidate, mass, com),
        flight_dynamics_authority=False,
        authority_label=S1_AUTHORITY_LABEL,
    )
