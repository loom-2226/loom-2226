from src.wayfarer_q6_navigator_adapter import score_navigator_result


def _fixture(remass_used=15.6, departure_remass=250.0, arrival_remass=234.4, dv=29.1, ve=2000.0):
    return {
        "mass": {
            "departure_remass_t": departure_remass,
            "planned_remass_used_t": remass_used,
            "planned_arrival_remass_t": arrival_remass,
        },
        "speeds": {
            "terminal_delta_v_km_s": dv,
            "exhaust_velocity_km_s": ve,
        },
        "torch": {"burn_s": 1200.0},
    }


def test_scores_reserve_and_fraction():
    out = score_navigator_result(_fixture(), protected_dispatch_floor_t=100.0)
    assert out["remass_used_t"] == 15.6
    assert out["arrival_remass_t"] == 234.4
    assert out["reserve_margin_t"] == 134.4
    assert out["dispatch_floor_pass"] is True
    assert round(out["fraction_of_departure_remass_used"], 4) == 0.0624


def test_fails_floor_when_arrival_below_floor():
    out = score_navigator_result(_fixture(remass_used=170.0, arrival_remass=80.0), protected_dispatch_floor_t=100.0)
    assert out["dispatch_floor_pass"] is False
    assert out["reserve_margin_t"] == -20.0


def test_requires_navigator_mass_contract():
    try:
        score_navigator_result({"mass": {}}, protected_dispatch_floor_t=100.0)
    except KeyError as exc:
        assert "departure_remass_t" in str(exc)
    else:
        raise AssertionError("missing Navigator mass fields must fail")
