from src.wayfarer_dispatch_doctrine import DispatchPolicy
from src.wayfarer_q6_suite import score_suite, score_suite_with_policy


def _r(name, departure, used):
    return {
        "route_id": name,
        "mass": {
            "departure_remass_t": departure,
            "planned_remass_used_t": used,
            "planned_arrival_remass_t": departure - used,
        },
        "speeds": {"terminal_delta_v_km_s": 30.0, "exhaust_velocity_km_s": 2000.0},
        "torch": {"burn_s": 1000.0},
    }


def test_suite_selects_lowest_dispatch_case_that_meets_floor():
    results = [_r("A", 250.0, 30.0), _r("B", 250.0, 60.0)]
    out = score_suite(results, candidate_dispatch_t=(100.0, 150.0, 200.0, 250.0), protected_floor_t=50.0)
    assert out["minimum_candidate_dispatch_t"] == 150.0
    assert out["candidates"]["100.0"]["all_pass"] is False
    assert out["candidates"]["150.0"]["all_pass"] is True


def test_suite_reports_worst_case_route():
    results = [_r("A", 250.0, 20.0), _r("B", 250.0, 70.0)]
    out = score_suite(results, candidate_dispatch_t=(150.0, 200.0), protected_floor_t=50.0)
    assert out["worst_case_route_id"] == "B"
    assert out["max_route_remass_used_t"] == 70.0


def test_policy_scoring_enforces_minimum_dispatch_and_reserve():
    policy = DispatchPolicy(150.0, 100.0, 50.0)
    results = [_r("A", 250.0, 30.0), _r("B", 250.0, 60.0)]
    out = score_suite_with_policy(results, policy, candidate_dispatch_t=(90.0, 100.0, 150.0, 200.0))
    assert out["candidates"]["90.0"]["all_pass"] is False
    assert out["candidates"]["100.0"]["all_pass"] is False
    assert out["candidates"]["150.0"]["all_pass"] is True
    assert out["minimum_candidate_dispatch_t"] == 150.0


def test_policy_scoring_can_apply_one_tank_isolation():
    policy = DispatchPolicy(150.0, 100.0, 50.0)
    results = [_r("A", 250.0, 60.0)]
    nominal = score_suite_with_policy(results, policy, candidate_dispatch_t=(150.0,))
    degraded = score_suite_with_policy(results, policy, candidate_dispatch_t=(150.0,), tank_isolated=True)
    assert nominal["candidates"]["150.0"]["all_pass"] is True
    assert degraded["candidates"]["150.0"]["all_pass"] is True
    assert degraded["candidates"]["150.0"]["minimum_reserve_margin_t"] < nominal["candidates"]["150.0"]["minimum_reserve_margin_t"]
