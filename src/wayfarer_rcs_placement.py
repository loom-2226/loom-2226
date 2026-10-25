from __future__ import annotations

"""Deterministic Q4 RCS mount-placement candidate for Wayfarer.

This module places candidate *mount hardpoints*, not qualified nozzles. It uses
current Wayfarer geometry/Q4 engineering anchors and preserves OPEN status for
nozzle directions, plume qualification, working fluid, and one-cluster-out
controllability.

Coordinate convention follows the Wayfarer geometry compiler:
- +X runs bow -> aft
- Y/Z are transverse
- +Z is launch-bay side
- -Z is docking side
"""

import math
from typing import Any

STATUS = "ENGINEERING_CANDIDATE_NON_CANON"
SHIP_RADIUS_M = 4.5
REFERENCE_WET_COM_M = (26.6767, 0.0, 0.1481)

# Q4 v0.1/v0.2 candidate station bands. Centers are used only as geometric
# hardpoint candidates; exact structure/nozzle locations remain unqualified.
_BANDS = (
    ("FORE", 5.0, 8.0, 0.0, "forward hull; no declared cardinal interference"),
    (
        "FORE_MID",
        17.0,
        20.0,
        45.0,
        "+Z launch bay spans x=16..27.5 m; rotate ring off launch/docking cardinals",
    ),
    (
        "RADIATOR_ROOT",
        35.0,
        38.0,
        45.0,
        "radiator roots occupy cardinal azimuths in x=33..38 m; rotate mount ring by 45 deg",
    ),
    ("AFT", 43.0, 46.0, 0.0, "aft reactor/torch machinery exterior candidate band"),
)


def _clean(value: float) -> float:
    return 0.0 if abs(value) < 1e-12 else value


def _mount(*, band_name: str, x_m: float, azimuth_deg: float, index: int) -> dict[str, Any]:
    a = math.radians(azimuth_deg)
    y = _clean(SHIP_RADIUS_M * math.cos(a))
    z = _clean(SHIP_RADIUS_M * math.sin(a))

    # Local basis is geometry only. It does not assert a nozzle set.
    radial = (_clean(0.0), _clean(math.cos(a)), _clean(math.sin(a)))
    tangent = (_clean(0.0), _clean(-math.sin(a)), _clean(math.cos(a)))

    return {
        "id": f"RCS_{band_name}_{index+1}",
        "position_m": [x_m, y, z],
        "azimuth_deg": float(azimuth_deg % 360.0),
        "surface_normal": list(radial),
        "circumferential_tangent": list(tangent),
        "axial_basis": [1.0, 0.0, 0.0],
        "mount_status": STATUS,
        "nozzle_axes": "OPEN_Q4",
        "thruster_unit_max_N_sizing_point": 25000.0,
    }


def build_rcs_mount_candidate() -> dict[str, Any]:
    """Return one geometry-screened 16-hardpoint Q4 candidate.

    The layout intentionally rotates rings that overlap declared launch-bay and
    radiator-root cardinal geometry. This is not plume qualification and does
    not prove six-DOF or one-cluster-out control because exact nozzle axes and
    vectoring remain OPEN in Q4.
    """

    bands: list[dict[str, Any]] = []
    for name, x0, x1, offset, rationale in _BANDS:
        x = (x0 + x1) / 2.0
        azimuths = tuple((offset + step) % 360.0 for step in (0.0, 90.0, 180.0, 270.0))
        mounts = [_mount(band_name=name, x_m=x, azimuth_deg=az, index=i) for i, az in enumerate(azimuths)]
        bands.append(
            {
                "name": name,
                "x_range_m": [x0, x1],
                "x_center_m": x,
                "azimuth_offset_deg": offset,
                "placement_rationale": rationale,
                "mounts": mounts,
            }
        )

    xs = [m["position_m"][0] for band in bands for m in band["mounts"]]
    return {
        "standard_id": "WAYFARER_Q4_RCS_MOUNT_PLACEMENT_V0.1",
        "status": STATUS,
        "authority": "ENGINEERING_STUDY_NON_CANON",
        "coordinate_system": {
            "x": "forward-to-aft; bow datum x=0 m; aftmost permanent structure x=57 m",
            "y": "transverse",
            "z": "transverse; +Z launch-bay side; -Z docking side",
        },
        "reference_wet_com_m": list(REFERENCE_WET_COM_M),
        "ship_radius_m": SHIP_RADIUS_M,
        "candidate_thruster_unit_max_N": 25000.0,
        "bands": bands,
        "geometry_metrics": {
            "foremost_mount_x_m": min(xs),
            "aftmost_mount_x_m": max(xs),
            "fore_aft_station_span_m": max(xs) - min(xs),
            "fore_lever_arm_from_wet_com_m": REFERENCE_WET_COM_M[0] - min(xs),
            "aft_lever_arm_from_wet_com_m": max(xs) - REFERENCE_WET_COM_M[0],
        },
        "nozzle_solution_status": "OPEN_Q4",
        "one_cluster_out_controllability": "OPEN_Q4",
        "working_fluid_status": "OPEN_Q5",
        "minimum_impulse_bit_status": "OPEN_Q4",
        "plume_clearance_status": "GEOMETRIC_SCREEN_ONLY_NOT_QUALIFIED",
        "structural_mount_qualification": "OPEN_Q4",
        "notes": [
            "Mount hardpoints are not nozzle locations or final cluster count authority.",
            "FORE_MID ring is rotated 45 deg to avoid the +Z launch-bay and -Z docking cardinal axes in the current geometry envelope.",
            "RADIATOR_ROOT ring is rotated 45 deg because current radiator roots occupy cardinal azimuths.",
            "Exact force directions, vectoring cones, plume cones, duty cycle, power, thermal closure and one-cluster-out controllability remain OPEN.",
        ],
    }
