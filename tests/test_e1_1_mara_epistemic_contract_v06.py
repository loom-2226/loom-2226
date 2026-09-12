from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
HARNESS = HERE / "engineering" / "experience_one" / "spikes" / "e1_1_mara_grounded_synthesis_v06.py"


def _load():
    spec = importlib.util.spec_from_file_location("mara_v06", HARNESS)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = _load()


def _packet():
    return {
        "place": {
            "entity_id": "CER-P05",
            "role": "STRATEGIC_PORT",
            "traffic_class": "RESTRICTED",
        },
        "facts": {
            "administrative": {"value": "Belt Standards Directorate"},
            "civil": {"value": "Ceres Commonwealth"},
            "security": {"value": "Belt Security & Rescue Directorate"},
            "primary_commercial": {"value": "Axiom Precision & Metrology"},
            "security_posture": {"value": 0.875},
            "commercial_openness": {"value": 0.2},
        },
    }


def _case(case_id: str):
    return next(c for c in m.CASES if c["id"] == case_id)


def test_who_runs_accepts_supported():
    answer = {
        "answer": "Differentiated authorities are identified.",
        "assessment": "SUPPORTED",
        "evidence_paths": ["facts.administrative.value"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("who_runs_it"), _packet(), answer)
    assert ok, reasons


def test_who_runs_accepts_mixed():
    answer = {
        "answer": "Authorities are identified but no single operator is established.",
        "assessment": "MIXED",
        "evidence_paths": ["facts.security.value"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("who_runs_it"), _packet(), answer)
    assert ok, reasons


def test_contradictory_claim_accepts_contradicted():
    answer = {
        "answer": "The claim conflicts with the packet.",
        "assessment": "CONTRADICTED",
        "evidence_paths": ["place.traffic_class", "facts.security_posture.value"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("contradictory_user_claim"), _packet(), answer)
    assert ok, reasons


def test_contradictory_claim_accepts_mixed():
    answer = {
        "answer": "Open/lightly policed is contradicted; tourist status is unestablished.",
        "assessment": "MIXED",
        "evidence_paths": ["facts.commercial_openness.value"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("contradictory_user_claim"), _packet(), answer)
    assert ok, reasons


def test_sabotage_does_not_accept_mixed():
    answer = {
        "answer": "No sabotage evidence.",
        "assessment": "MIXED",
        "evidence_paths": [],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("unsupported_sabotage_cause"), _packet(), answer)
    assert not ok
    assert "assessment_outside_acceptable_set" in reasons


def test_why_restricted_remains_strictly_mixed():
    answer = {
        "answer": "Restrictive characteristics are supported; comparison is not established.",
        "assessment": "SUPPORTED",
        "evidence_paths": ["place.traffic_class"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("why_restricted"), _packet(), answer)
    assert not ok
    assert "assessment_outside_acceptable_set" in reasons


def test_nonexistent_evidence_path_still_fails():
    answer = {
        "answer": "Grounded answer.",
        "assessment": "SUPPORTED",
        "evidence_paths": ["facts.imaginary.value"],
        "target_entity_id": "CER-P05",
    }
    ok, reasons = m.validate_answer(_case("who_runs_it"), _packet(), answer)
    assert not ok
    assert "evidence_path_not_in_packet" in reasons
