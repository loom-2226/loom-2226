from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "engineering" / "current" / "wayfarer_q4_hud_attitude_envelope_v0.4.json"


def _load():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_hud_envelope_is_finite_and_not_canon():
    doc = _load()
    assert doc["status"] == "QUALIFIED_FOR_HUD_FINITE_ATTITUDE_ENVELOPE_NON_CANON"
    assert doc["hud_use_allowed"] is True
    assert doc["canon_promotion_allowed"] is False
    assert doc["instantaneous_attitude_reset_allowed"] is False


def test_hud_envelope_contains_nominal_and_cluster_out_cases():
    doc = _load()
    assert "REFERENCE_WET_DOCKED" in doc["mass_states"]
    assert "REFERENCE_WET_LAUNCH_ABSENT" in doc["mass_states"]
    assert doc["control_cases"]["NOMINAL"]["three_axis_control_retained"] is True
    assert doc["control_cases"]["ONE_CLUSTER_OUT"]["three_axis_control_retained"] is True


def test_closed_loop_and_plume_authority_remain_blocked():
    doc = _load()
    blocked = set(doc["not_qualified_for"])
    assert "closed_loop_guidance_control" in blocked
    assert "final_thruster_plume_clearance" in blocked
    assert "structural_load_limit" in blocked
