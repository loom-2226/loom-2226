from __future__ import annotations

"""Recover and revalidate the prior Wayfarer RCS hardpoint candidate.

This module preserves the useful geometry from the unmerged Q4/Q5/HUD flight-control
work without promoting its old torque/inertia assumptions to present flight authority.
The recovered hardpoints are checked against the current deterministic Wayfarer
geometry. Final nozzle hardware, finite plume cones, structural loads and closed-loop
GNC remain open.
"""

import math
import sqlite3
from pathlib import Path
from typing import Any

from src.wayfarer_geometry import compile_geometry

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
ROOT = Path(__file__).resolve().parents[1]
SEED_SQL = ROOT / "geometry" / "wayfarer_geometry_seed.sql"
SOURCE_PR = 96
SOURCE_VALIDATION_HEAD = "5aecbd98fd27063c5d5e7b4b352cc19e74f31627"
SOURCE_HUD_BRANCH = "feature/hud-wayfarer-attitude-envelope-v0.1-2026-09-11"
SOURCE_SHIPYARD_LINEAGE = "research/computational-shipyard-m2a-attitude-coupling-v0.1-2026-09-11"
MOUNT_THRUST_CAP_N = 25_000.0

_BANDS = (
    ("FORE", 5.0, 8.0, 0.0, "forward hull"),
    ("FORE_MID", 17.0, 20.0, 45.0, "rotated off launch/docking cardinals"),
    ("RADIATOR_ROOT", 35.0, 38.0, 45.0, "rotated off cardinal radiator roots"),
    ("AFT", 43.0, 46.0, 0.0, "aft propulsion exterior candidate band"),
)


def _compile_geometry() -> dict[str, Any]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SEED_SQL.read_text(encoding="utf-8"))
        return compile_geometry(conn)
    finally:
        conn.close()


def _box_bounds(component: dict[str, Any]) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    cx, cy, cz = (float(v) for v in component["center_m"])
    dims = component["dimensions"]
    kind = component["kind"]
    if kind == "box":
        hx, hy, hz = float(dims["x_m"]) / 2.0, float(dims["y_m"]) / 2.0, float(dims["z_m"]) / 2.0
    elif kind == "collar_z":
        hx = hy = float(dims["diameter_m"]) / 2.0
        hz = float(dims["depth_m"]) / 2.0
    else:
        raise ValueError(f"unsupported clearance component kind: {kind}")
    return ((cx - hx, cx + hx), (cy - hy, cy + hy), (cz - hz, cz + hz))


def _point_in_bounds(point: list[float], bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]]) -> bool:
    return all(bounds[i][0] <= float(point[i]) <= bounds[i][1] for i in range(3))


def _mount(*, band: str, x_m: float, radius_m: float, azimuth_deg: float, index: int) -> dict[str, Any]:
    a = math.radians(azimuth_deg)
    y = radius_m * math.cos(a)
    z = radius_m * math.sin(a)
    return {
        "id": f"RCS_{band}_{index + 1}",
        "band": band,
        "position_m": [x_m, 0.0 if abs(y) < 1e-12 else y, 0.0 if abs(z) < 1e-12 else z],
        "azimuth_deg": float(azimuth_deg % 360.0),
        "candidate_thruster_unit_max_N": MOUNT_THRUST_CAP_N,
        "mount_status": STATUS,
        "nozzle_solution_status": "RECOVERED_Q4_CANDIDATE_NOT_FINAL_HARDWARE",
    }


def build_recovered_rcs_candidate() -> dict[str, Any]:
    geometry = _compile_geometry()
    parameters = geometry["parameters"]
    radius_m = float(parameters["ship.main_body_diameter_m"]["value"]) / 2.0
    components = {component["id"]: component for component in geometry["components"]}

    bands: list[dict[str, Any]] = []
    mounts: list[dict[str, Any]] = []
    for band_name, x0, x1, offset, rationale in _BANDS:
        x_center = (x0 + x1) / 2.0
        azimuths = [float((offset + step) % 360.0) for step in (0.0, 90.0, 180.0, 270.0)]
        band_mounts = [
            _mount(band=band_name, x_m=x_center, radius_m=radius_m, azimuth_deg=az, index=i)
            for i, az in enumerate(azimuths)
        ]
        mounts.extend(band_mounts)
        bands.append(
            {
                "name": band_name,
                "x_range_m": [x0, x1],
                "x_center_m": x_center,
                "azimuths_deg": azimuths,
                "placement_rationale": rationale,
                "mount_ids": [m["id"] for m in band_mounts],
            }
        )

    launch_bounds = _box_bounds(components["launch_bay"])
    docking_bounds = _box_bounds(components["docking_collar"])
    launch_clear = all(not _point_in_bounds(m["position_m"], launch_bounds) for m in mounts)
    docking_clear = all(not _point_in_bounds(m["position_m"], docking_bounds) for m in mounts)

    radiator_band = next(b for b in bands if b["name"] == "RADIATOR_ROOT")
    cardinal = (0.0, 90.0, 180.0, 270.0)
    radiator_sep = all(
        min(abs(((az - c + 180.0) % 360.0) - 180.0) for c in cardinal) >= 45.0 - 1e-9
        for az in radiator_band["azimuths_deg"]
    )

    return {
        "schema": "LOOM.Wayfarer.RecoveredRCSCandidate",
        "schema_version": "0.1",
        "status": STATUS,
        "provenance": {
            "source_pr": SOURCE_PR,
            "source_validation_head": SOURCE_VALIDATION_HEAD,
            "source_hud_branch": SOURCE_HUD_BRANCH,
            "source_shipyard_lineage": SOURCE_SHIPYARD_LINEAGE,
            "source_modules": [
                "src/wayfarer_rcs_placement.py",
                "src/wayfarer_rcs_wrench.py",
                "src/wayfarer_rcs_allocation.py",
                "src/wayfarer_rcs_gimbal_realizability.py",
                "src/wayfarer_rcs_plume_clearance.py",
                "src/wayfarer_q5_rcs_duty.py",
            ],
            "current_geometry_source": "geometry/wayfarer_geometry_seed.sql -> src/wayfarer_geometry.py",
        },
        "mount_count": len(mounts),
        "bands": bands,
        "mounts": mounts,
        "candidate_thruster_unit_max_N": MOUNT_THRUST_CAP_N,
        "current_geometry_screen": {
            "hardpoint_point_clearance_pass": launch_clear and docking_clear and radiator_sep,
            "launch_bay_point_clearance_pass": launch_clear,
            "docking_collar_point_clearance_pass": docking_clear,
            "radiator_root_azimuth_separation_pass": radiator_sep,
            "finite_plume_cone_status": "OPEN_NOT_INVENTED",
            "radiator_deployed_sweep_clearance_status": "OPEN_PENDING_FINAL_RADIATOR_GEOMETRY",
            "hardpoint_extent_beyond_skin_modelled": False,
        },
        "recovered_q4_q5_evidence": {
            "nominal_six_dof_wrench_rank": "RECOVERED_PASS_CANDIDATE",
            "one_logical_cluster_out_rank": "RECOVERED_PASS_CANDIDATE",
            "bounded_allocation_25kN_per_mount": "RECOVERED_PASS_CANDIDATE",
            "single_gimbal_45deg_realizability": "RECOVERED_CONDITIONAL_CANDIDATE",
            "q5_energy_thermal_screen": "RECOVERED_CONDITIONAL_CANDIDATE",
            "role": "PRIOR_ENGINEERING_EVIDENCE_REQUIRES_CURRENT_REQUALIFICATION",
        },
        "dynamics_status": {
            "full_wayfarer_inertia": "WAYFARER_INERTIA_OPEN_NOT_QUALIFIED",
            "old_q4_torque_targets_role": "RECOVERED_SCREENING_TARGETS_NOT_CURRENT_FLIGHT_AUTHORITY",
            "closed_loop_gnc_qualified": False,
            "structural_mount_loads_qualified": False,
            "minimum_impulse_bit_qualified": False,
            "working_fluid_selected": False,
        },
        "disposition": "RECOVERED_RCS_HARDPOINT_CANDIDATE_GEOMETRY_COMPATIBLE_CURRENT_DYNAMICS_REQUALIFICATION_REQUIRED",
        "authority": {
            "geometry_candidate_recovered": True,
            "current_point_clearance_screen": True,
            "flight_dynamics_authority": False,
            "final_rcs_hardware_authority": False,
            "canon_changed": False,
            "campaign_state_mutation": "ZERO",
            "llm_calculation_authority": "ZERO",
        },
    }
