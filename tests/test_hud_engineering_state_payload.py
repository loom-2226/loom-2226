from loom.hud.engineering_state_payload import (
    attach_typed_engineering_payload,
    build_wayfarer_engineering_payload,
)


def test_typed_engineering_payload_preserves_datum_metadata_and_firewalls():
    payload = build_wayfarer_engineering_payload(epoch="QUALIFICATION_STATIC")

    assert payload["contract"] == "LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1"
    assert payload["source_commit"] == "835cccfb4a37a2a683c6196cbb7382b826271d67"

    wet = payload["mass"]["reference_wet_mass"]
    assert wet["value"] == 1158.5
    assert wet["unit"] == "t"
    assert wet["authority"] == "QUALIFICATION_ONLY"
    assert wet["availability"] == "AVAILABLE"
    assert wet["quality"] == "ENGINEERING_BASELINE_NON_CANON"

    assert payload["dispatch"]["routine_optimizer_may_consume_protected_water"]["value"] is False
    assert payload["firewalls"]["torch_jet_power_is_electrical_bus_power"]["value"] is False
    assert payload["firewalls"]["metric_velocity_reset_allowed"]["value"] is False


def test_open_candidate_and_attitude_energy_states_remain_visible():
    payload = build_wayfarer_engineering_payload(epoch="QUALIFICATION_STATIC")

    assert payload["power_thermal"]["status"]["value"] == "OPEN_BOUNDED"
    assert payload["dispatch"]["status"]["value"] == "CANDIDATE_NON_CANON"
    assert payload["feedstock"]["primary"]["value"] == "H2O"
    assert payload["feedstock"]["primary"]["quality"] == "PRIMARY_CANDIDATE_NOT_CERTIFIED"
    assert payload["feedstock"]["certified_species"]["value"] == []
    assert payload["feedstock"]["certified_species"]["quality"] == "CERTIFIED_NONE"

    energy = payload["attitude"]["energy_screen"]
    assert energy["status"]["value"] == "OPEN_BOUNDED"
    assert energy["gross_conversion_heat_within_50GJ_buffer"]["value"] is True
    assert energy["per_maneuver_detail_available"]["value"] is True
    assert len(energy["maneuvers"]) == 12
    assert energy["max_checked_jet_energy"]["value"] == 113.991693
    assert energy["max_gross_conversion_waste_heat_energy"]["value"] == 12.665744
    assert energy["max_equivalent_expelled_mass"]["value"] == 227.983387

    pitch = energy["maneuvers"]["ONE_CLUSTER_OUT:PITCH_180"]
    assert pitch["powered_rcs_time"]["value"] == 57.483333
    assert pitch["settle_margin_time"]["value"] == 11.496667
    assert pitch["worst_failed_cluster"]["value"] == "B"
    alt = pitch["candidates"]["alternate_50kms"]
    assert alt["jet_energy"]["value"] == 113.991693
    assert alt["waste_heat_energy"]["value"] == 12.665744
    assert alt["heat_fraction_of_50GJ_buffer"]["value"] == 0.253314874
    assert alt["radiator_transient_credit_applied"]["value"] is False

    assert energy["combined_maneuver_energy_available"]["value"] is False
    assert energy["combined_maneuver_energy_available"]["quality"] == "TIMING_OPEN_Q4_Q5"
    assert energy["translation_maneuver_energy_available"]["value"] is False
    assert energy["translation_maneuver_energy_available"]["quality"] == "TIMING_OPEN_Q4_Q5"


def test_realtime_attachment_replaces_raw_engineering_with_typed_payload():
    snapshot = {
        "sim_epoch_utc": "2026-09-11T00:00:00Z",
        "engineering": {"raw": "must-not-leak-to-presentation"},
        "wayfarer": {"remass_t": 250.0},
    }
    result = attach_typed_engineering_payload(snapshot)

    assert result["engineering"]["contract"] == "LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1"
    assert "raw" not in result["engineering"]
    assert result["engineering"]["epoch"] == "2026-09-11T00:00:00Z"
    assert result["wayfarer"]["remass_t"] == 250.0
