from src.wayfarer_q6_suite import score_suite


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
    # Replay assumes same route burn demand against each candidate dispatch inventory.
    assert out["minimum_candidate_dispatch_t"] == 150.0
    assert out["candidates"]["100.0"]["all_pass"] is False
    assert out["candidates"]["150.0"]["all_pass"] is True


def test_suite_reports_worst_case_route():
    results = [_r("A", 250.0, 20.0), _r("B", 250.0, 70.0)]
    out = score_suite(results, candidate_dispatch_t=(150.0, 200.0), protected_floor_t=50.0)
    assert out["worst_case_route_id"] == "B"
    assert out["max_route_remass_used_t"] == 70.0
