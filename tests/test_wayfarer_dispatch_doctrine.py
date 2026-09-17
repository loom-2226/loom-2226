from src.wayfarer_dispatch_doctrine import (
    DispatchPolicy,
    degraded_system_actions,
    dispatch_assessment,
    mode_authorized,
)


def policy():
    return DispatchPolicy(
        normal_dispatch_remass_t=150.0,
        minimum_dispatch_remass_t=100.0,
        protected_optimizer_reserve_t=50.0,
    )


def test_mode_authorization_ladder():
    assert mode_authorized("ECON", "ROUTINE")
    assert mode_authorized("CRUISE", "ROUTINE")
    assert not mode_authorized("EXPEDITE", "ROUTINE")
    assert mode_authorized("EXPEDITE", "TIME_CRITICAL")
    assert not mode_authorized("HARD", "EXCEPTIONAL")
    assert mode_authorized("HARD", "EMERGENCY")
    assert not mode_authorized("LIMIT", "EMERGENCY")
    assert mode_authorized("LIMIT", "CONTINGENCY")


def test_protected_optimizer_reserve_is_enforced():
    out = dispatch_assessment(80.0, 150.0, policy())
    assert out["arrival_remass_t"] == 70.0
    assert out["reserve_margin_t"] == 20.0
    assert out["mission_pass"] is True
    assert out["disposition"] == "PASS"


def test_route_that_consumes_protected_reserve_requires_replan():
    out = dispatch_assessment(120.0, 150.0, policy())
    assert out["arrival_remass_t"] == 30.0
    assert out["mission_pass"] is False
    assert out["disposition"] == "DIVERT_OR_REPLAN"


def test_below_minimum_dispatch_is_blocked_even_if_short_mission():
    out = dispatch_assessment(10.0, 90.0, policy())
    assert out["minimum_dispatch_pass"] is False
    assert out["disposition"] == "NO_DISPATCH"


def test_one_full_tank_isolation_removes_quarter_accessible_remass():
    out = dispatch_assessment(50.0, 150.0, policy(), tank_isolated=True)
    assert out["accessible_remass_t"] == 112.5
    assert out["arrival_remass_t"] == 62.5
    assert out["mission_pass"] is True


def test_alternate_feed_derating_changes_accessible_mass():
    out = dispatch_assessment(
        40.0,
        150.0,
        policy(),
        alternate_feed_only=True,
        alternate_feed_usable_fraction=0.6,
    )
    assert out["accessible_remass_t"] == 90.0
    assert out["arrival_remass_t"] == 50.0
    assert out["mission_pass"] is True


def test_degraded_state_actions_are_explicit():
    actions = degraded_system_actions({
        "metric_unavailable": True,
        "tank_isolated": True,
        "rcs_cluster_lost": True,
    })
    assert "REPLAN_ORDINARY_SPACE" in actions
    assert "RECOMPUTE_ACCESSIBLE_REMASS" in actions
    assert "RECOMPUTE_CONTROL_AUTHORITY" in actions
