from wayfarer_rcs_combined_maneuvers import build_rcs_combined_maneuver_screen


_RESULT = build_rcs_combined_maneuver_screen()


def test_combined_screen_preserves_engineering_authority_boundary():
    result = _RESULT
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["scope"] == "REPRESENTATIVE_COMBINED_WRENCH_FEASIBILITY_ONLY"
    assert result["authority_limits"]["closed_loop_guidance_control"] == "OPEN_Q4"
    assert result["authority_limits"]["power_thermal_duty"] == "OPEN_Q5"


def test_combined_screen_contains_mission_relevant_nominal_cases():
    result = _RESULT
    assert set(result["nominal_cases"]) == {
        "DOCKING_CORRECTION",
        "COLLISION_AVOIDANCE_SIDESTEP_SLEW",
        "TORCH_AXIS_ACQUISITION",
        "PROXIMITY_BRAKE_AND_ALIGN",
    }


def test_combined_screen_exercises_every_single_cluster_failure():
    result = _RESULT
    assert set(result["one_cluster_out_cases"]) == {"A", "B", "C", "D"}
    for cluster_id, cases in result["one_cluster_out_cases"].items():
        assert set(cases) == {
            "ONE_CLUSTER_OUT_APPROACH_CORRECTION",
            "ONE_CLUSTER_OUT_ABORT_SIDESTEP",
        }
        for case in cases.values():
            assert case["failed_cluster"] == cluster_id
            assert case["active_mount_count"] == 12


def test_all_combined_cases_fit_current_bounded_allocator():
    result = _RESULT
    assert result["summary"]["all_nominal_cases_pass"]
    assert result["summary"]["all_one_cluster_out_cases_pass"]
    assert result["summary"]["max_mount_utilization_fraction"] <= 1.0 + 1e-9
    assert (
        result["summary"]["disposition"]
        == "PASS_COMBINED_WRENCH_SCREEN_NOT_FINAL_CONTROL_QUALIFICATION"
    )


def test_cases_are_genuinely_combined_not_pure_axis_repeats():
    result = _RESULT
    for case in result["nominal_cases"].values():
        nonzero = sum(abs(value) > 1e-9 for value in case["requested_wrench"].values())
        assert nonzero >= 4
    for cluster_cases in result["one_cluster_out_cases"].values():
        for case in cluster_cases.values():
            nonzero = sum(abs(value) > 1e-9 for value in case["requested_wrench"].values())
            assert nonzero >= 4
