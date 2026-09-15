import json
from pathlib import Path

from wayfarer_q5_attitude_energy import build_q5_attitude_energy_bridge


def test_attitude_energy_bridge_preserves_authority_boundary():
    result = build_q5_attitude_energy_bridge()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["scope"] == "QUALIFIED_Q4_PURE_ATTITUDE_TIMING_TO_Q5_ENERGY_SCREEN"
    assert result["authority_limits"]["combined_maneuver_duration"] == "OPEN_Q4_Q5"
    assert result["authority_limits"]["radiator_transient_response"] == "OPEN_Q5"
    assert result["authority_limits"]["working_fluid"] == "OPEN_Q2_Q4"


def test_reference_wet_docked_contains_nominal_and_degraded_slews():
    result = build_q5_attitude_energy_bridge()
    state = result["mass_states"]["REFERENCE_WET_DOCKED"]
    assert set(state["control_cases"]) == {"NOMINAL", "ONE_CLUSTER_OUT"}
    for control_case in state["control_cases"].values():
        assert set(control_case["slews"]) == {
            "ROLL_90", "ROLL_180", "PITCH_90", "PITCH_180", "YAW_90", "YAW_180"
        }


def test_powered_duration_is_qualified_time_without_20pct_settle_margin():
    result = build_q5_attitude_energy_bridge()
    case = result["mass_states"]["REFERENCE_WET_DOCKED"]["control_cases"]["NOMINAL"]["slews"]["PITCH_90"]
    assert case["qualified_transition_time_s"] > case["powered_bang_bang_time_s"]
    ratio = case["qualified_transition_time_s"] / case["powered_bang_bang_time_s"]
    assert abs(ratio - 1.20) < 1e-9
    assert case["settle_margin_time_s"] > 0.0


def test_energy_and_equivalent_expellant_are_derived_for_candidate_exhaust_velocities():
    result = build_q5_attitude_energy_bridge()
    case = result["mass_states"]["REFERENCE_WET_DOCKED"]["control_cases"]["NOMINAL"]["slews"]["YAW_180"]
    for candidate in ("lead_20kms", "alternate_50kms"):
        screen = case["candidate_propulsion_screens"][candidate]
        assert screen["jet_power_GW"] > 0.0
        assert screen["jet_energy_GJ"] > 0.0
        assert screen["equivalent_expelled_mass_kg"] > 0.0
        assert max(screen["conversion_waste_heat_energy_GJ_by_efficiency"].values()) > 0.0


def test_gross_conversion_heat_stays_within_existing_buffer_screen_for_checked_slews():
    result = build_q5_attitude_energy_bridge()
    assert result["summary"]["all_checked_gross_conversion_heat_within_50GJ_buffer_screen"] is True
    assert result["summary"]["max_gross_conversion_waste_heat_energy_GJ"] < 50.0


def test_machine_readable_attitude_energy_envelope_tracks_bridge():
    root = Path(__file__).resolve().parents[1]
    artifact = json.loads(
        (root / "engineering/current/wayfarer_q5_attitude_energy_envelope_v0.1.json").read_text(encoding="utf-8")
    )
    bridge = build_q5_attitude_energy_bridge()

    assert artifact["schema"] == "LOOM.Wayfarer.Q5AttitudeEnergyEnvelope"
    assert artifact["status"] == bridge["status"]
    assert artifact["unavailable"]["combined_maneuver_energy"] == "TIMING_OPEN_Q4_Q5"
    assert artifact["unavailable"]["translation_maneuver_energy"] == "TIMING_OPEN_Q4_Q5"
    assert len(artifact["maneuvers"]) == 12

    for row in artifact["maneuvers"]:
        source = bridge["mass_states"]["REFERENCE_WET_DOCKED"]["control_cases"][row["control_case"]]["slews"][row["maneuver"]]
        assert abs(row["qualified_transition_time_s"] - source["qualified_transition_time_s"]) < 1e-6
        assert abs(row["powered_rcs_time_s"] - source["powered_bang_bang_time_s"]) < 1e-6
        assert abs(row["settle_margin_time_s"] - source["settle_margin_time_s"]) < 1e-6
        assert abs(row["total_resultant_mount_thrust_kN"] - source["total_resultant_mount_thrust_kN"]) < 1e-6
        assert row["worst_failed_cluster"] == source["worst_screen_failed_cluster"]

        for candidate, compact in row["candidates"].items():
            detailed = source["candidate_propulsion_screens"][candidate]
            assert abs(compact["jet_energy_GJ"] - detailed["jet_energy_GJ"]) < 1e-6
            assert abs(compact["equivalent_expelled_mass_kg"] - detailed["equivalent_expelled_mass_kg"]) < 1e-6
            assert abs(
                compact["worst_conversion_waste_heat_energy_GJ"]
                - max(detailed["conversion_waste_heat_energy_GJ_by_efficiency"].values())
            ) < 1e-6
            assert abs(
                compact["worst_heat_fraction_of_50GJ_buffer"]
                - detailed["gross_worst_conversion_heat_fraction_of_buffer"]["buffer_50GJ"]
            ) < 1e-6
            assert compact["radiator_transient_credit_applied"] is False
