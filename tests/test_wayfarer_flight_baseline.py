import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "engineering" / "current" / "wayfarer_flight_system_baseline_v0.1.json"


def _load():
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_mass_identity_closes():
    d = _load()
    m = d["mass_states"]
    assert abs((m["dry_mass_t"] + m["working_fluid_water_inventory_t"]) - m["reference_wet_mass_t"]) < 1e-9
    assert abs((m["reference_wet_mass_t"] - m["normal_remass_allowance_t"]) - m["post_normal_remass_reference_mass_t"]) < 1e-9
    assert abs((m["normal_remass_allowance_t"] + m["protected_water_reserve_t"]) - m["working_fluid_water_inventory_t"]) < 1e-9


def test_torch_remains_ordinary_momentum_exchange():
    d = _load()
    assert d["mobility_regimes"]["torch"]["physics_class"] == "ordinary_momentum_exchange"


def test_water_is_not_silently_frozen_as_only_remass():
    d = _load()
    ident = d["mobility_regimes"]["torch"]["feedstock_identity"]
    assert ident["status"] == "OPEN_FOR_QUALIFICATION"
    assert ident["water_only_requirement"] is False
    assert len(d["torch_feedstock_qualification"]["candidate_species"]) >= 2


def test_endurance_slot_preserves_e0_e1_e2_optionality():
    d = _load()
    e = d["mobility_regimes"]["endurance"]
    assert e["implementation_class"] == "E0_NONE"
    assert e["allowed_qualification_classes"] == ["E0_NONE", "E1_LOW_REMASS", "E2_MOMENTUM_COUPLED"]
    assert e["canon_effect"] == "none"


def test_metric_cannot_reset_ordinary_velocity_for_free():
    d = _load()
    metric = d["mobility_regimes"]["metric"]
    assert metric["ordinary_velocity_reset_allowed"] is False
    assert "free_momentum_cycle" in d["hard_kills"]
    assert "metric_silently_erases_ordinary_state_mismatch" in d["hard_kills"]


def test_feedstock_rating_vocabulary_is_closed():
    d = _load()
    assert d["torch_feedstock_qualification"]["rating_enum"] == [
        "CERTIFIED", "DERATED", "CONTINGENCY", "PROHIBITED"
    ]


def test_existing_torch_velocity_card_is_captured():
    d = _load()
    cards = {x["mode"]: x["exhaust_velocity_km_s"] for x in d["mobility_regimes"]["torch"]["mode_cards"]}
    assert cards == {
        "ECON": 3000.0,
        "CRUISE": 2000.0,
        "EXPEDITE": 1000.0,
        "FAST": 700.0,
        "HARD": 450.0,
        "LIMIT": 300.0,
    }
