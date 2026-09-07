"""Stage F-PA-5 read-only Navigator / trajectory telemetry authority audit.

This module records the exact telemetry surface currently promoted from the
Navigator Sequence-B route payload and classifies what it can and cannot support
for simulator telemetry. It performs no navigation math, persistence, physics
promotion, or campaign mutation.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

NAVIGATOR_TRAJECTORY_AUDIT_CONTRACT = "LOOM_F_PA_NAVIGATOR_TRAJECTORY_AUDIT_V1"

SEQUENCE_B_SAMPLE_FIELDS: tuple[str, ...] = (
    "sample_index",
    "flight_t_s",
    "epoch_utc",
    "phase_code",
    "phase_progress",
    "eta_s",
    "position_semantics_code",
    "relational_progress",
    "ordinary_state_kind_code",
    "ordinary_pos_x_km",
    "ordinary_pos_y_km",
    "ordinary_pos_z_km",
    "ordinary_vel_x_km_s",
    "ordinary_vel_y_km_s",
    "ordinary_vel_z_km_s",
    "ordinary_speed_km_s",
    "ordinary_accel_g",
    "target_range_km",
    "target_delta_v_km_s",
    "metric_state_code",
    "metric_beta_current",
    "torch_state_code",
    "wet_mass_t",
    "remass_remaining_t",
    "thermal_state_code",
)

# Classification is deliberately conservative. Presence in a payload is not
# equivalent to navigation grade or to a complete simulator state variable.
FIELD_CLASSIFICATION: dict[str, tuple[str, str]] = {
    "sample_index": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "Sequence-B sample ordering"),
    "flight_t_s": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "trajectory-relative time"),
    "epoch_utc": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "absolute sample epoch"),
    "phase_code": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "trajectory phase identity"),
    "phase_progress": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "phase progress scalar"),
    "eta_s": ("AUTHORITATIVE_NAVIGATOR_SAMPLE_METADATA", "remaining-time scalar"),
    "position_semantics_code": ("AUTHORITATIVE_NAVIGATOR_SEMANTICS", "ordinary vs relational position semantics"),
    "relational_progress": ("AUTHORITATIVE_NAVIGATOR_SEMANTICS", "metric/relational progress; not ordinary occupancy"),
    "ordinary_state_kind_code": ("AUTHORITATIVE_NAVIGATOR_SEMANTICS", "ordinary state availability/type"),
    "ordinary_pos_x_km": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary J2000-ecliptic position component"),
    "ordinary_pos_y_km": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary J2000-ecliptic position component"),
    "ordinary_pos_z_km": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary J2000-ecliptic position component"),
    "ordinary_vel_x_km_s": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary velocity component"),
    "ordinary_vel_y_km_s": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary velocity component"),
    "ordinary_vel_z_km_s": ("AUTHORITATIVE_NAVIGATOR_ORDINARY_STATE", "ordinary velocity component"),
    "ordinary_speed_km_s": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "ordinary speed magnitude"),
    "ordinary_accel_g": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "acceleration magnitude only; no vector"),
    "target_range_km": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "target range magnitude only"),
    "target_delta_v_km_s": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "target delta-v magnitude only"),
    "metric_state_code": ("AUTHORITATIVE_NAVIGATOR_PROPULSION_STATE", "metric state code"),
    "metric_beta_current": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "current metric beta scalar"),
    "torch_state_code": ("AUTHORITATIVE_NAVIGATOR_PROPULSION_STATE", "torch state code"),
    "wet_mass_t": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "wet mass sample"),
    "remass_remaining_t": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_SCALAR", "remaining reaction mass sample"),
    "thermal_state_code": ("AUTHORITATIVE_NAVIGATOR_ENGINEERING_STATE_CODE", "qualitative thermal state code"),
}

SIMULATOR_NEED_MATRIX: tuple[dict[str, Any], ...] = (
    {"need": "trajectory_epoch_phase", "status": "PRESENT", "evidence": ("epoch_utc", "flight_t_s", "phase_code", "phase_progress", "eta_s")},
    {"need": "ordinary_position_3d", "status": "PRESENT_WHERE_SEQUENCE_B_DECLARES_ORDINARY_OCCUPANCY", "evidence": ("ordinary_pos_x_km", "ordinary_pos_y_km", "ordinary_pos_z_km")},
    {"need": "ordinary_velocity_3d", "status": "PRESENT_WHERE_SEQUENCE_B_DECLARES_ORDINARY_OCCUPANCY", "evidence": ("ordinary_vel_x_km_s", "ordinary_vel_y_km_s", "ordinary_vel_z_km_s")},
    {"need": "metric_relational_state", "status": "PRESENT_NO_ORDINARY_OCCUPANCY", "evidence": ("position_semantics_code", "relational_progress", "metric_state_code", "metric_beta_current")},
    {"need": "acceleration_vector", "status": "MISSING", "evidence": ("ordinary_accel_g",), "note": "scalar magnitude cannot determine inertial or body-frame acceleration vector"},
    {"need": "attitude_orientation", "status": "MISSING", "evidence": ()},
    {"need": "angular_rate", "status": "MISSING", "evidence": ()},
    {"need": "thrust_vector_and_command", "status": "MISSING", "evidence": ("torch_state_code",), "note": "state code is not a thrust vector or actuator command"},
    {"need": "mass_and_remass", "status": "PARTIAL", "evidence": ("wet_mass_t", "remass_remaining_t"), "note": "sample mass exists; component mass properties and flow rate are absent"},
    {"need": "remass_flow_rate", "status": "MISSING", "evidence": ()},
    {"need": "thermal_quantitative_state", "status": "MISSING", "evidence": ("thermal_state_code",), "note": "qualitative code only"},
    {"need": "power_state", "status": "MISSING", "evidence": ()},
    {"need": "target_relative_vector_state", "status": "PARTIAL", "evidence": ("target_range_km", "target_delta_v_km_s"), "note": "magnitudes only; no relative position/velocity vector"},
    {"need": "navigation_uncertainty_covariance", "status": "MISSING", "evidence": ()},
    {"need": "sensor_measurements", "status": "MISSING", "evidence": ()},
    {"need": "estimated_navigation_state", "status": "MISSING", "evidence": ()},
    {"need": "guidance_command_state", "status": "MISSING", "evidence": ()},
    {"need": "control_actuator_state", "status": "MISSING", "evidence": ()},
    {"need": "docking_proximity_state", "status": "MISSING", "evidence": ()},
    {"need": "traffic_clearance_state", "status": "MISSING", "evidence": ()},
)


def navigator_trajectory_authority_audit() -> dict[str, Any]:
    counts = Counter(v[0] for v in FIELD_CLASSIFICATION.values())
    need_counts = Counter(str(row["status"]) for row in SIMULATOR_NEED_MATRIX)
    return {
        "contract": NAVIGATOR_TRAJECTORY_AUDIT_CONTRACT,
        "coordinate_frame_promoted_by_route_adapter": "J2000_ECLIPTIC",
        "sequence_b_sample_field_count": len(SEQUENCE_B_SAMPLE_FIELDS),
        "sequence_b_sample_fields": SEQUENCE_B_SAMPLE_FIELDS,
        "field_classification": {
            field: {"classification": classification, "meaning": meaning}
            for field, (classification, meaning) in FIELD_CLASSIFICATION.items()
        },
        "field_classification_counts": dict(sorted(counts.items())),
        "simulator_need_matrix": SIMULATOR_NEED_MATRIX,
        "simulator_need_status_counts": dict(sorted(need_counts.items())),
        "authority_boundaries": {
            "ordinary_state_promotion": "ONLY_COMPLETE_XYZ_PLUS_VXYZ_SEQUENCE_B_SAMPLES",
            "metric_ordinary_occupancy": "PROHIBITED_NO_INVENTED_XYZ",
            "time_interpolation": "LINEAR_PRESENTATION_RUNTIME_ONLY_NON_NAVIGATION_GRADE",
            "extrapolation": "PROHIBITED",
            "visual_sampling": "VISUALIZATION_ONLY",
            "campaign_mutation": "NONE",
        },
    }
