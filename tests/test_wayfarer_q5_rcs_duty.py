from wayfarer_q5_rcs_duty import build_q5_rcs_duty_envelope


def test_q5_rcs_duty_preserves_authority_boundaries():
    result = build_q5_rcs_duty_envelope()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["q5_qualification_status"] == "OPEN_BOUNDED"
    assert result["authority_limits"]["maneuver_duration"] == "OPEN_Q4_Q5"
    assert result["authority_limits"]["electrical_bus_source"] == "NOT_ASSUMED"
    assert result["authority_limits"]["physical_radiator_geometry"] == "OPEN"


def test_q5_rcs_duty_uses_actual_resultant_mount_thrust():
    result = build_q5_rcs_duty_envelope()
    cases = list(result["nominal_cases"].values())
    cases += [case for group in result["one_cluster_out_cases"].values() for case in group.values()]
    for case in cases:
        assert case["total_resultant_mount_thrust_kN"] > 0.0
        assert 0.0 <= case["max_physical_mount_utilization_fraction"] <= 1.0 + 1e-9
        assert case["firing_mount_count_gt_1N"] <= case["active_mount_count"]
        assert case["duration_s"] is None
        assert case["energy_draw_GJ"] is None
        assert case["thermal_buffer_draw_GJ"] is None


def test_candidate_exhaust_velocity_power_scaling_is_consistent():
    result = build_q5_rcs_duty_envelope()
    assert result["candidate_exhaust_velocity_km_s"] == {"lead": 20.0, "alternate": 50.0}
    for case in result["nominal_cases"].values():
        ratio = case["alternate_50kms_jet_power_GW"] / case["lead_20kms_jet_power_GW"]
        assert abs(ratio - 2.5) < 1e-12


def test_conversion_waste_heat_decreases_with_efficiency():
    result = build_q5_rcs_duty_envelope()
    for case in result["nominal_cases"].values():
        lead = case["lead_conversion_waste_heat_MW_by_efficiency"]
        alt = case["alternate_conversion_waste_heat_MW_by_efficiency"]
        assert lead["eta_0.95"] < lead["eta_0.90"]
        assert alt["eta_0.95"] < alt["eta_0.90"]


def test_summary_bounds_all_cases():
    result = build_q5_rcs_duty_envelope()
    all_cases = list(result["nominal_cases"].values())
    all_cases += [case for group in result["one_cluster_out_cases"].values() for case in group.values()]
    assert result["summary"]["max_total_resultant_mount_thrust_kN"] == max(
        case["total_resultant_mount_thrust_kN"] for case in all_cases
    )
    assert result["summary"]["max_lead_20kms_jet_power_GW"] == max(
        case["lead_20kms_jet_power_GW"] for case in all_cases
    )
