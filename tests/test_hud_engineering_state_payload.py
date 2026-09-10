from loom.hud.engineering_state_payload import (
    attach_typed_engineering_payload,
    build_wayfarer_engineering_payload,
)


def test_typed_engineering_payload_preserves_datum_metadata_and_firewalls():
    payload = build_wayfarer_engineering_payload(epoch="QUALIFICATION_STATIC")

    assert payload["contract"] == "LOOM_HUD_WAYFARER_ENGINEERING_TYPED_PAYLOAD_V1"
    assert payload["source_commit"] == "e2df887d5e901eed9378c7aeb7d4964040b9a7e6"

    wet = payload["mass"]["reference_wet_mass"]
    assert wet["value"] == 1158.5
    assert wet["unit"] == "t"
    assert wet["authority"] == "QUALIFICATION_ONLY"
    assert wet["availability"] == "AVAILABLE"
    assert wet["quality"] == "ENGINEERING_BASELINE_NON_CANON"

    assert payload["dispatch"]["routine_optimizer_may_consume_protected_water"]["value"] is False
    assert payload["firewalls"]["torch_jet_power_is_electrical_bus_power"]["value"] is False
    assert payload["firewalls"]["metric_velocity_reset_allowed"]["value"] is False


def test_open_candidate_and_feedstock_states_remain_visible():
    payload = build_wayfarer_engineering_payload(epoch="QUALIFICATION_STATIC")

    assert payload["power_thermal"]["status"]["value"] == "OPEN_BOUNDED"
    assert payload["dispatch"]["status"]["value"] == "CANDIDATE_NON_CANON"
    assert payload["feedstock"]["primary"]["value"] == "H2O"
    assert payload["feedstock"]["primary"]["quality"] == "PRIMARY_CANDIDATE_NOT_CERTIFIED"
    assert payload["feedstock"]["certified_species"]["value"] == []
    assert payload["feedstock"]["certified_species"]["quality"] == "CERTIFIED_NONE"


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
