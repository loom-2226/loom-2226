from __future__ import annotations

import math

from loom.hud.wayfarer_attitude_envelope import ENGINEERING_SOURCE_COMMIT, attitude_transition_time_s, angle_between_deg


def test_engineering_source_is_pinned():
    assert ENGINEERING_SOURCE_COMMIT == "e2df887d5e901eed9378c7aeb7d4964040b9a7e6"


def test_opposed_vectors_are_180_deg():
    assert math.isclose(angle_between_deg((1, 0, 0), (-1, 0, 0)), 180.0, abs_tol=1e-9)


def test_nominal_and_degraded_transitions_are_finite():
    nominal = attitude_transition_time_s(90.0, axis="pitch", degraded=False)
    degraded = attitude_transition_time_s(90.0, axis="pitch", degraded=True)
    assert 40.0 <= nominal <= 45.0
    assert degraded > nominal


def test_zero_angle_requires_zero_time():
    assert attitude_transition_time_s(0.0, axis="yaw", degraded=False) == 0.0
