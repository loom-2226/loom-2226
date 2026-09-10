from __future__ import annotations

from loom.hud.wayfarer_engineering_state import (
    ENGINEERING_SOURCE_BRANCH,
    ENGINEERING_SOURCE_COMMIT,
    load_wayfarer_engineering_state,
)


def test_engineering_handoff_is_pinned_to_pr96_source():
    state = load_wayfarer_engineering_state()
    assert ENGINEERING_SOURCE_BRANCH == "engineering/wayfarer-flight-system-qualification-v1"
    assert ENGINEERING_SOURCE_COMMIT == "e2df887d5e901eed9378c7aeb7d4964040b9a7e6"
    assert state["source"]["commit"] == ENGINEERING_SOURCE_COMMIT
    assert state["authority"]["canon"] is False
    assert state["authority"]["hud_consumer_only"] is True


def test_mass_and_torch_cards_come_from_engineering_baseline_object():
    state = load_wayfarer_engineering_state()
    mass = state["mass"]
    assert mass["reference_wet_mass_t"] == 1158.5
    assert mass["dry_mass_t"] == 858.5
    assert mass["normal_remass_allowance_t"] == 250.0
    assert mass["protected_water_reserve_t"] == 50.0

    cards = state["torch"]["mode_cards"]
    assert cards["ECON"]["acceleration_g"] == 0.3
    assert cards["CRUISE"]["exhaust_velocity_km_s"] == 2000.0
    assert cards["LIMIT"]["acceleration_g"] == 7.5
    assert all(card["status"] == "WORKING_ENGINEERING_CARD" for card in cards.values())
    assert state["torch"]["jet_power_is_electrical_bus_power"] is False


def test_dispatch_reserves_remain_separate_and_candidate():
    state = load_wayfarer_engineering_state()
    dispatch = state["dispatch"]
    assert dispatch["status"] == "CANDIDATE_NON_CANON"
    assert dispatch["normal_dispatch_remass_t"] == 150.0
    assert dispatch["minimum_dispatch_remass_t"] == 100.0
    assert dispatch["protected_optimizer_reserve_t"] == 50.0
    assert dispatch["protected_water_reserve_t"] == 50.0
    assert dispatch["protected_optimizer_reserve_is_protected_water"] is False
    assert dispatch["routine_optimizer_may_consume_protected_water"] is False


def test_thermal_and_feedstock_state_stay_open_not_certified():
    state = load_wayfarer_engineering_state()
    thermal = state["power_thermal"]
    assert thermal["qualification_status"] == "OPEN_BOUNDED"
    assert thermal["radiator"]["physical_geometry_status"] == "OPEN"
    assert thermal["thermal_buffer"]["medium_status"] == "OPEN"
    assert thermal["torch"]["normal_ship_coupled_heat_ceiling_MW"] == 50.0

    feedstock = state["feedstock"]
    assert feedstock["status"] == "ENGINEERING_SCREENING_NON_CANON"
    assert feedstock["primary_candidate"] == "H2O"
    assert feedstock["certified_species"] == []
    assert feedstock["final_mode_ratings_closed"] is False


def test_attitude_source_is_same_pinned_engineering_handoff():
    state = load_wayfarer_engineering_state()
    attitude = state["attitude"]
    assert attitude["status"] == "QUALIFIED_FOR_HUD_FINITE_ATTITUDE_ENVELOPE_NON_CANON"
    assert attitude["instantaneous_attitude_reset_allowed"] is False
    assert attitude["control_cases"]["NOMINAL"]["reference_wet_docked_slew_s"]["pitch_180"] == 59.74
    assert attitude["control_cases"]["ONE_CLUSTER_OUT"]["reference_wet_docked_slew_s"]["roll_180"] == 40.60
