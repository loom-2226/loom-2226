"""Read-only row-level Stage F-PA audit of infrastructure spatial authority.

This module reports what the exact governed WORLD SQLite contains. It does not
invent coordinates, re-grade rows, or convert presentation geometry into
navigation authority.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import sqlite3

MATRIX_CONTRACT = "LOOM_F_PA_INFRASTRUCTURE_AUTHORITY_MATRIX_V1"


def _connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise FileNotFoundError(path)
    conn = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _truth(value: Any) -> bool | None:
    if value is None:
        return None
    return bool(int(value))


def _complete(values: list[Any]) -> bool:
    return all(value is not None for value in values)


def infrastructure_authority_matrix(world_path: Path | str) -> dict[str, Any]:
    world = Path(world_path).expanduser().resolve()
    with _connect(world) as conn:
        rows = conn.execute(
            """
            SELECT
                n.node_id,n.node_name,n.system,n.parent_body,n.facility_type,
                n.traffic,n.source AS node_source,n.entity_id,n.parent_entity_id,
                l.model_id AS location_model_id,l.parent_entity_id AS location_parent_entity_id,
                l.center_entity_id,l.frame_family,l.geometry_kind,l.precision_class,
                l.position_authority,l.navigation_grade AS location_navigation_grade,
                l.parameter_json AS location_parameter_json,l.assumption_json AS location_assumption_json,
                l.valid_from AS location_valid_from,l.valid_until AS location_valid_until,
                o.orbit_family,o.parent_entity_id AS orbit_parent_entity_id,o.secondary_entity_id,
                o.reference_frame AS orbit_reference_frame,o.reference_plane,o.epoch_utc AS orbit_epoch_utc,
                o.semi_major_axis_km,o.eccentricity,o.inclination_deg,o.raan_deg,
                o.arg_periapsis_deg,o.mean_anomaly_deg,o.period_s,
                o.amplitude_x_km,o.amplitude_y_km,o.amplitude_z_km,
                o.navigation_grade AS orbit_navigation_grade,o.epistemic_status AS orbit_epistemic_status,
                o.source_id AS orbit_source_id,o.derivation_model_id,o.notes AS orbit_notes,
                s.epoch_utc AS state_epoch_utc,s.center_entity_id AS state_center_entity_id,
                s.reference_frame AS state_reference_frame,s.units AS state_units,
                s.x_km,s.y_km,s.z_km,s.vx_km_s,s.vy_km_s,s.vz_km_s,
                s.state_source,s.model_id AS state_model_id,
                s.navigation_grade AS state_navigation_grade,s.validity_status,
                h.traffic_class_torch,h.traffic_class_metric,h.loom_access_class,
                h.shipyard_class,h.heavy_repair,h.metric_overhaul,h.local_feeder_class,
                h.traffic_control_authority_id,h.roadstead_id,h.roadstead_status,
                h.physical_cert_model_id,h.model_status AS hub_model_status,h.provenance AS hub_provenance
            FROM infrastructure_nodes n
            LEFT JOIN entity_location_models l ON l.entity_id=n.entity_id
            LEFT JOIN orbit_geometry_models o ON o.entity_id=n.entity_id
            LEFT JOIN spatial_states s ON s.entity_id=n.entity_id
            LEFT JOIN transport_hubs h ON h.entity_id=n.entity_id
            ORDER BY n.node_id
            """
        ).fetchall()

    matrix: list[dict[str, Any]] = []
    for raw in rows:
        r = dict(raw)
        state_complete = _complete([r.get("x_km"),r.get("y_km"),r.get("z_km"),r.get("vx_km_s"),r.get("vy_km_s"),r.get("vz_km_s")])
        kepler_complete = _complete([
            r.get("semi_major_axis_km"),r.get("eccentricity"),r.get("inclination_deg"),
            r.get("raan_deg"),r.get("arg_periapsis_deg"),r.get("mean_anomaly_deg"),
            r.get("orbit_epoch_utc"),r.get("orbit_reference_frame"),
        ])
        amplitude_present = any(r.get(k) is not None for k in ("amplitude_x_km","amplitude_y_km","amplitude_z_km"))
        state_nav = _truth(r.get("state_navigation_grade"))
        location_nav = _truth(r.get("location_navigation_grade"))
        orbit_nav = _truth(r.get("orbit_navigation_grade"))

        if state_complete and state_nav is True:
            state_authority = "AUTHORITATIVE_NAVIGATION_GRADE"
            spatial_derivability = "DETERMINATE_FROM_EXISTING_AUTHORITY"
        elif state_complete:
            state_authority = "AUTHORITATIVE_NON_NAVIGATION_GRADE"
            spatial_derivability = "CONSTRAINED_DESIGN_REQUIRED"
        else:
            state_authority = "MISSING"
            spatial_derivability = "UNDERDETERMINED"

        matrix.append({
            **r,
            "state_6d_complete": state_complete,
            "keplerian_orbit_definition_complete": kepler_complete,
            "amplitude_orbit_parameters_present": amplitude_present,
            "location_navigation_grade_bool": location_nav,
            "orbit_navigation_grade_bool": orbit_nav,
            "state_navigation_grade_bool": state_nav,
            "structured_state_authority": state_authority,
            "spatial_derivability_initial": spatial_derivability,
            "surface_coordinates_structured": False,
            "docking_transition_geometry_structured": False,
        })

    def counts(field: str) -> dict[str, int]:
        c = Counter("<NULL>" if row.get(field) is None else str(row.get(field)) for row in matrix)
        return dict(sorted(c.items()))

    summary = {
        "row_count": len(matrix),
        "facility_type": counts("facility_type"),
        "geometry_kind": counts("geometry_kind"),
        "frame_family": counts("frame_family"),
        "position_authority": counts("position_authority"),
        "precision_class": counts("precision_class"),
        "orbit_family": counts("orbit_family"),
        "orbit_epistemic_status": counts("orbit_epistemic_status"),
        "state_validity_status": counts("validity_status"),
        "state_authority": counts("structured_state_authority"),
        "spatial_derivability_initial": counts("spatial_derivability_initial"),
        "state_6d_complete": counts("state_6d_complete"),
        "keplerian_orbit_definition_complete": counts("keplerian_orbit_definition_complete"),
        "location_navigation_grade": counts("location_navigation_grade_bool"),
        "orbit_navigation_grade": counts("orbit_navigation_grade_bool"),
        "state_navigation_grade": counts("state_navigation_grade_bool"),
        "traffic_hub_rows": sum(row.get("traffic_class_torch") is not None for row in matrix),
    }
    return {"contract": MATRIX_CONTRACT, "database": str(world), "summary": summary, "rows": matrix}
