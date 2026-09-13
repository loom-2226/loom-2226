from wayfarer_rcs_plume_screen import build_rcs_plume_screen


def test_sampled_exhaust_centerlines_point_outward_and_clear_local_hull():
    result = build_rcs_plume_screen()
    assert result["minimum_local_hull_half_angle_margin_deg"] >= 45.0 - 1e-9
    for mount in result["mounts"]:
        for sample in mount["samples"]:
            assert sample["exhaust_radial_dot"] > 0.0
            assert sample["local_hull_centerline_clear"] is True


def test_known_launch_and_docking_centerline_interference_is_screened():
    result = build_rcs_plume_screen()
    assert result["known_geometry_centerline_screen"]["planetary_launch"]["intersecting_sample_count"] == 0
    assert result["known_geometry_centerline_screen"]["docking_collar"]["intersecting_sample_count"] == 0


def test_open_radiator_geometry_prevents_finite_plume_qualification():
    result = build_rcs_plume_screen()
    assert result["radiator_interference_status"] == "OPEN_PHYSICAL_PANEL_GEOMETRY"
    assert result["finite_plume_cone_qualification"] == "OPEN_Q4_REQUIRES_PLUME_HALF_ANGLE_AND_RADIATOR_GEOMETRY"
    assert result["plume_half_angle_deg"] is None


def test_screen_preserves_noncanon_authority_boundary():
    result = build_rcs_plume_screen()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["qualification"] == "CENTERLINE_AND_LOCAL_HULL_GEOMETRY_SCREEN_ONLY"
    assert result["structural_qualification"] == "OPEN_Q4"
    assert result["power_thermal_qualification"] == "OPEN_Q5"
