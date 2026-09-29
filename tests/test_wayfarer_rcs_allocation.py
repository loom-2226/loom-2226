from wayfarer_rcs_allocation import build_rcs_allocation_screen


def test_nominal_q4_hud_envelope_is_allocatable_with_actuator_caps():
    result = build_rcs_allocation_screen()
    nominal = result["screens"]["NOMINAL"]
    assert nominal["disposition"] == "PASS_BOUNDED_ALLOCATION_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION"
    assert nominal["all_cases_pass"] is True
    assert nominal["max_mount_utilization_fraction"] <= 1.0 + 1e-9


def test_each_one_cluster_out_case_allocates_existing_degraded_hud_envelope():
    result = build_rcs_allocation_screen()
    degraded = result["screens"]["ONE_CLUSTER_OUT"]
    assert set(degraded) == {"A", "B", "C", "D"}
    for cluster_id, screen in degraded.items():
        assert screen["failed_cluster"] == cluster_id
        assert screen["all_cases_pass"] is True
        assert screen["max_mount_utilization_fraction"] <= 1.0 + 1e-9
        assert screen["disposition"] == "PASS_BOUNDED_ALLOCATION_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION"


def test_screen_covers_both_signs_of_all_six_wrench_axes():
    result = build_rcs_allocation_screen()
    case_names = set(result["screens"]["NOMINAL"]["cases"])
    expected = {
        "FX_PLUS", "FX_MINUS", "FY_PLUS", "FY_MINUS", "FZ_PLUS", "FZ_MINUS",
        "TX_PLUS", "TX_MINUS", "TY_PLUS", "TY_MINUS", "TZ_PLUS", "TZ_MINUS",
    }
    assert case_names == expected


def test_allocation_screen_uses_existing_q4_hud_nominal_and_degraded_bounds():
    result = build_rcs_allocation_screen()
    req = result["requirements"]
    assert req["NOMINAL"]["translation_N"] == 100000.0
    assert req["NOMINAL"]["pitch_yaw_torque_Nm"] == 1000000.0
    assert req["NOMINAL"]["roll_torque_Nm"] == 200000.0
    assert req["ONE_CLUSTER_OUT"]["translation_N"] == 75000.0
    assert req["ONE_CLUSTER_OUT"]["pitch_yaw_torque_Nm"] == 750000.0
    assert req["ONE_CLUSTER_OUT"]["roll_torque_Nm"] == 100000.0


def test_physical_resultants_are_reported_without_exceeding_mount_cap():
    result = build_rcs_allocation_screen()
    cases = list(result["screens"]["NOMINAL"]["cases"].values())
    cases += [
        case
        for screen in result["screens"]["ONE_CLUSTER_OUT"].values()
        for case in screen["cases"].values()
    ]
    for case in cases:
        assert case["total_resultant_mount_thrust_N"] > 0.0
        assert case["max_physical_mount_utilization_fraction"] <= 1.0 + 1e-9
        for command in case["physical_mount_commands"].values():
            assert command["commanded_thrust_N"] <= 25000.0 + 1e-8
            assert command["mount_utilization_fraction"] <= 1.0 + 1e-9


def test_screen_does_not_claim_final_nozzle_or_closed_loop_qualification():
    result = build_rcs_allocation_screen()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["allocation_model"] == "SAMPLED_VECTORING_WITH_PER_MOUNT_THRUST_CAP_AND_PHYSICAL_RESULTANT_REPORTING"
    assert result["exact_nozzle_hardware_status"] == "OPEN_Q4"
    assert result["closed_loop_control_status"] == "OPEN_Q4"
    assert result["plume_interference_status"] == "OPEN_Q4"
    assert result["power_thermal_qualification"] == "OPEN_Q5"
