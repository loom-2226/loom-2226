from wayfarer_rcs_control import build_rcs_control_candidate


def test_vectoring_candidate_uses_existing_mount_layout_and_stays_noncanon():
    result = build_rcs_control_candidate()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["mount_placement_standard"] == "WAYFARER_Q4_RCS_MOUNT_PLACEMENT_V0.1"
    assert result["vectoring_half_angle_deg"] == 45.0
    assert result["qualification"] == "KINEMATIC_CONTROLLABILITY_SCREEN_ONLY"


def test_each_mount_has_five_sampled_force_directions_and_outward_exhaust_component():
    result = build_rcs_control_candidate()
    mounts = result["mounts"]
    assert len(mounts) == 16
    for mount in mounts:
        assert len(mount["sampled_force_directions"]) == 5
        radial = mount["surface_normal"]
        for sample in mount["sampled_force_directions"]:
            force = sample["force_unit_ship"]
            exhaust = sample["exhaust_unit"]
            # Force remains in the inward hemisphere, so exhaust retains an
            # outward radial component and does not point through the hull.
            assert sum(force[i] * radial[i] for i in range(3)) < -0.70
            assert sum(exhaust[i] * radial[i] for i in range(3)) > 0.70


def test_nominal_candidate_has_full_six_dof_wrench_rank_and_bidirectional_axes():
    result = build_rcs_control_candidate()
    nominal = result["controllability"]["NOMINAL"]
    assert nominal["wrench_rank"] == 6
    assert nominal["full_six_dof_rank"] is True
    assert all(nominal["bidirectional_axes"].values())


def test_every_single_logical_cluster_out_case_retains_six_dof_screen():
    result = build_rcs_control_candidate()
    cases = result["controllability"]["ONE_CLUSTER_OUT"]
    assert set(cases) == {"A", "B", "C", "D"}
    for case in cases.values():
        assert case["surviving_mount_count"] == 12
        assert case["wrench_rank"] == 6
        assert case["full_six_dof_rank"] is True
        assert all(case["bidirectional_axes"].values())
        assert case["disposition"] == "PASS_KINEMATIC_SCREEN_NOT_FORCE_QUALIFICATION"


def test_cluster_topology_is_cross_strapped_across_all_four_axial_bands():
    result = build_rcs_control_candidate()
    clusters = result["logical_clusters"]
    for cluster_id, cluster in clusters.items():
        assert cluster_id in {"A", "B", "C", "D"}
        assert len(cluster["mount_ids"]) == 4
        assert set(cluster["bands"]) == {"FORE", "FORE_MID", "RADIATOR_ROOT", "AFT"}


def test_force_and_power_authority_remain_open_after_kinematic_screen():
    result = build_rcs_control_candidate()
    assert result["plume_clearance_status"] == "LOCAL_OUTWARD_HEMISPHERE_ONLY"
    assert result["structural_qualification"] == "OPEN_Q4"
    assert result["power_thermal_qualification"] == "OPEN_Q5"
    assert result["minimum_impulse_bit_status"] == "OPEN_Q4"
    assert result["one_cluster_out_force_authority"] == "BOUNDED_BY_Q4_HUD_ENVELOPE_NOT_REDERIVED_HERE"
