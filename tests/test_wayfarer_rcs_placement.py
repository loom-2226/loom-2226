from wayfarer_rcs_placement import build_rcs_mount_candidate


def test_candidate_has_four_bands_and_sixteen_mounts():
    result = build_rcs_mount_candidate()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert len(result["bands"]) == 4
    mounts = [m for band in result["bands"] for m in band["mounts"]]
    assert len(mounts) == 16


def test_interference_bands_rotate_off_cardinal_launch_and_radiator_axes():
    result = build_rcs_mount_candidate()
    by_name = {band["name"]: band for band in result["bands"]}
    assert by_name["FORE_MID"]["azimuth_offset_deg"] == 45.0
    assert by_name["RADIATOR_ROOT"]["azimuth_offset_deg"] == 45.0
    for name in ("FORE_MID", "RADIATOR_ROOT"):
        az = {round(m["azimuth_deg"], 6) for m in by_name[name]["mounts"]}
        assert az == {45.0, 135.0, 225.0, 315.0}


def test_each_band_is_radially_symmetric_about_ship_axis():
    result = build_rcs_mount_candidate()
    for band in result["bands"]:
        ys = [m["position_m"][1] for m in band["mounts"]]
        zs = [m["position_m"][2] for m in band["mounts"]]
        assert abs(sum(ys)) < 1e-9
        assert abs(sum(zs)) < 1e-9


def test_mount_radius_matches_main_body_radius():
    result = build_rcs_mount_candidate()
    for band in result["bands"]:
        for mount in band["mounts"]:
            y, z = mount["position_m"][1:]
            assert abs((y*y + z*z) ** 0.5 - 4.5) < 1e-9


def test_fore_aft_geometry_provides_long_pitch_yaw_lever_arms():
    result = build_rcs_mount_candidate()
    wet_com_x = result["reference_wet_com_m"][0]
    x_positions = [m["position_m"][0] for band in result["bands"] for m in band["mounts"]]
    assert wet_com_x - min(x_positions) > 20.0
    assert max(x_positions) - wet_com_x > 15.0
    assert max(x_positions) - min(x_positions) >= 38.0


def test_nozzle_and_full_controllability_remain_open():
    result = build_rcs_mount_candidate()
    assert result["nozzle_solution_status"] == "OPEN_Q4"
    assert result["one_cluster_out_controllability"] == "OPEN_Q4"
    assert result["plume_clearance_status"] == "GEOMETRIC_SCREEN_ONLY_NOT_QUALIFIED"
