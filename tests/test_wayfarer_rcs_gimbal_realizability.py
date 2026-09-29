from wayfarer_rcs_gimbal_realizability import (
    build_gimbal_realizability_proof,
    collapse_sample_mix_to_single_gimbal,
)
from wayfarer_rcs_control import build_rcs_control_candidate


def test_realizability_proof_preserves_engineering_authority_boundary():
    result = build_gimbal_realizability_proof()
    assert result["status"] == "ENGINEERING_CANDIDATE_NON_CANON"
    assert result["authority"] == "ENGINEERING_STUDY_NON_CANON"
    assert result["authority_limits"]["physical_gimbal_hardware"] == "OPEN_Q4"
    assert result["authority_limits"]["power_thermal_duty"] == "OPEN_Q5"


def test_every_sample_direction_lies_inside_assumed_continuous_gimbal_cone():
    result = build_gimbal_realizability_proof()
    assert result["continuous_gimbal_half_angle_deg"] == 45.0
    assert result["all_sample_directions_inside_continuous_cone"]
    for mount in result["mount_checks"]:
        assert mount["all_samples_inside_cone"]
        for sample in mount["sample_checks"]:
            assert sample["inside_cone"]
            assert sample["unit_norm_error"] < 1e-12


def test_positive_sample_mixtures_collapse_to_one_simultaneous_gimbal_vector():
    result = build_gimbal_realizability_proof()
    assert result["representative_positive_mixtures_collapse_inside_cone_and_cap"]
    assert (
        result["allocation_implication"]
        == "ANY_FEASIBLE_NONNEGATIVE_SAMPLED_MIX_AT_ONE_MOUNT_COLLAPSES_TO_ONE_SIMULTANEOUS_GIMBAL_VECTOR"
    )
    assert (
        result["disposition"]
        == "PASS_SINGLE_GIMBAL_REALIZABILITY_UNDER_CONTINUOUS_45_DEG_ASSUMPTION"
    )


def test_collapsed_resultant_never_exceeds_sample_sum_or_mount_cap():
    control = build_rcs_control_candidate()
    mix = (1_000.0, 6_000.0, 3_000.0, 8_000.0, 7_000.0)
    for mount in control["mounts"]:
        collapsed = collapse_sample_mix_to_single_gimbal(mount, mix)
        assert collapsed["commanded_thrust_N"] <= collapsed["summed_sample_channel_thrust_N"] + 1e-9
        assert collapsed["summed_sample_channel_thrust_N"] == 25_000.0
        assert collapsed["within_mount_thrust_cap"]
        assert collapsed["within_45_deg_cone"]


def test_single_channel_collapse_preserves_that_sample_direction():
    control = build_rcs_control_candidate()
    mount = control["mounts"][0]
    for index, sample in enumerate(mount["sampled_force_directions"]):
        mix = [0.0] * len(mount["sampled_force_directions"])
        mix[index] = 12_345.0
        collapsed = collapse_sample_mix_to_single_gimbal(mount, mix)
        assert abs(collapsed["commanded_thrust_N"] - 12_345.0) < 1e-8
        for actual, expected in zip(collapsed["commanded_force_unit_ship"], sample["force_unit_ship"]):
            assert abs(actual - expected) < 1e-12
