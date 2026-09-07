"""Stage F-PA-4 read-only audit of campaign mutable-state coverage.

The audit classifies fields present in a canonical campaign state mapping against
simulator true-state requirements. It never mutates campaign authority and does
not infer missing physics from location tokens or historical flight data.
"""
from __future__ import annotations

from typing import Any, Mapping

CAMPAIGN_TRUE_STATE_AUDIT_CONTRACT = "LOOM_F_PA_CAMPAIGN_TRUE_STATE_AUDIT_V1"


def _path(state: Mapping[str, Any], dotted: str) -> tuple[bool, Any]:
    cur: Any = state
    for part in dotted.split("."):
        if not isinstance(cur, Mapping) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def _present(state: Mapping[str, Any], dotted: str) -> dict[str, Any]:
    ok, value = _path(state, dotted)
    return {"path": dotted, "present": ok, "value_status": "NON_NULL" if ok and value is not None else ("NULL" if ok else "MISSING")}


def campaign_true_state_matrix(state: Mapping[str, Any]) -> dict[str, Any]:
    """Return an explicit persisted-vs-missing simulator state matrix."""
    present_paths = [
        "state_id", "state_sha256", "revision", "epoch_utc", "location_token", "status",
        "campaign.campaign_id", "ship_identity.ship_instance_id",
        "ship.fixed_nonremass_mass_t", "ship.variable_cargo_t", "ship.remass_capacity_t",
        "ship.remass_t", "ship.wet_mass_t", "ship.fusion_fuel.status",
        "ship.fusion_fuel.quantity_t", "ship.thermal.status", "ship.thermal.last_declared_action",
        "ship.configuration_sha256", "ship.condition.status", "ship.condition.ship_destroyed",
        "kinematic_boundary.status", "kinematic_boundary.source", "kinematic_boundary.state_source_units",
        "last_flight", "last_reconciliation", "authority.python",
    ]
    persisted = [_present(state, p) for p in present_paths]

    requirements = [
        ("campaign_clock", ["revision", "epoch_utc"], "PERSISTED"),
        ("semantic_location", ["location_token", "status", "kinematic_boundary.status"], "PERSISTED_SEMANTIC_BOUNDARY"),
        ("mass_remass_cargo", ["ship.fixed_nonremass_mass_t", "ship.variable_cargo_t", "ship.remass_capacity_t", "ship.remass_t", "ship.wet_mass_t"], "PERSISTED"),
        ("fusion_fuel_quantity", ["ship.fusion_fuel.quantity_t"], "OPEN_MODEL_NULL"),
        ("thermal_quantitative_state", ["ship.thermal.temperature_k", "ship.thermal.energy_j", "ship.thermal.heat_load_w"], "MISSING"),
        ("true_position_velocity", ["vehicle_state.position", "vehicle_state.velocity", "vehicle_state.reference_frame"], "MISSING"),
        ("attitude_angular_rate", ["vehicle_state.orientation", "vehicle_state.angular_rate"], "MISSING"),
        ("mass_properties", ["vehicle_state.center_of_mass", "vehicle_state.inertia_tensor"], "MISSING"),
        ("propulsion_actuator_state", ["propulsion.thrust", "propulsion.thrust_vector", "propulsion.rcs", "propulsion.actuator_state"], "MISSING"),
        ("power_state", ["power.generation_w", "power.load_w", "power.storage_j"], "MISSING"),
        ("metric_state", ["metric.state", "metric.mode", "metric.holonomy"], "MISSING"),
        ("active_trajectory", ["active_trajectory.trajectory_id", "active_trajectory.solution_id"], "MISSING"),
        ("guidance_control", ["guidance.mode", "guidance.target", "control.mode", "control.command"], "MISSING"),
        ("docking_landing_local_flight", ["proximity.mode", "docking.state", "landing.state", "local_flight.state"], "MISSING"),
        ("estimated_navigation", ["navigation_estimate.state", "navigation_estimate.covariance", "navigation_estimate.epoch_utc"], "MISSING"),
        ("sensor_measurements", ["sensors.measurements"], "MISSING"),
        ("traffic_clearance", ["traffic.clearance_id", "traffic.clearance_state"], "MISSING"),
        ("fault_state", ["faults.active"], "MISSING"),
    ]

    matrix: list[dict[str, Any]] = []
    for requirement, paths, expected in requirements:
        observations = [_present(state, p) for p in paths]
        all_present = all(x["present"] for x in observations)
        any_present = any(x["present"] for x in observations)
        if all_present:
            observed = "PRESENT"
        elif any_present:
            observed = "PARTIAL"
        else:
            observed = "ABSENT"
        matrix.append({
            "requirement": requirement,
            "expected_classification": expected,
            "observed": observed,
            "paths": observations,
        })

    return {
        "contract": CAMPAIGN_TRUE_STATE_AUDIT_CONTRACT,
        "state_schema": state.get("schema"),
        "state_id": state.get("state_id"),
        "revision": state.get("revision"),
        "persisted_field_probe": persisted,
        "simulator_state_matrix": matrix,
        "no_inference_rule": "Missing physical state is not inferred from location_token, kinematic_boundary, last_flight, or history.",
    }
