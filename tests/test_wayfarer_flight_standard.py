import json
from pathlib import Path

from src.wayfarer_flight_standard import promotable, validate_flight_standard


DRAFT = Path("engineering/current/WAYFARER_FLIGHT_SYSTEM_STANDARD_DRAFT_v0.1.json")


def test_draft_standard_validates_structurally_but_is_not_promotable():
    payload = json.loads(DRAFT.read_text(encoding="utf-8"))
    result = validate_flight_standard(payload)
    assert result["pass"] is True
    assert promotable(payload) is False


def test_free_ordinary_velocity_reset_is_rejected():
    payload = json.loads(DRAFT.read_text(encoding="utf-8"))
    payload["metric_interface"]["ordinary_velocity_reset_allowed"] = True
    result = validate_flight_standard(payload)
    assert result["pass"] is False
    assert any("ordinary-velocity reset" in err for err in result["errors"])


def test_reaction_mass_firewall_is_rejected_if_removed():
    payload = json.loads(DRAFT.read_text(encoding="utf-8"))
    payload["torch"]["momentum_exchange"] = "REACTIONLESS"
    result = validate_flight_standard(payload)
    assert result["pass"] is False


def test_overall_qualified_requires_all_gates_qualified():
    payload = json.loads(DRAFT.read_text(encoding="utf-8"))
    payload["qualification_status"]["overall"] = "QUALIFIED"
    result = validate_flight_standard(payload)
    assert result["pass"] is False
    assert promotable(payload) is False
