import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_mara_grounded_synthesis_v04.py"
spec = importlib.util.spec_from_file_location("e1_1_mara_grounded_synthesis_v04", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def packet():
    return {
        "request": {"intent": "PLACE_DETAIL", "target_entity_id": "CER-P05"},
        "place": {
            "entity_id": "CER-P05",
            "name": "Ceres Metric & Loom Anchorage",
            "role": "STRATEGIC_PORT",
            "traffic_class": "RESTRICTED",
        },
        "facts": {
            "security_posture": {"value": 0.875, "epistemic_status": "SUPPORTED"},
            "commercial_openness": {"value": 0.20, "epistemic_status": "SUPPORTED"},
            "outsider_attitude": {"value": 0.32, "epistemic_status": "SUPPORTED"},
            "administrative": {"value": "Belt Standards Directorate", "epistemic_status": "SUPPORTED"},
        },
    }


def case(case_id, assessment, required=None):
    return {
        "id": case_id,
        "expected_assessment": assessment,
        "expected_target": "CER-P05",
        "required_any_paths": set(required or []),
    }


def test_packet_path_accepts_place_and_fact_paths():
    p = packet()
    assert mod.packet_path_exists(p, "place.traffic_class")
    assert mod.packet_path_exists(p, "facts.security_posture")
    assert not mod.packet_path_exists(p, "facts.missing")
    assert not mod.packet_path_exists(p, "traffic_class")


def test_mixed_answer_can_cite_place_and_facts():
    ok, reasons = mod.validate_answer(
        case("why_restricted", "MIXED", {"place.traffic_class", "facts.security_posture"}),
        packet(),
        {
            "answer": "It is restricted and security-heavy, but a direct comparison with the rest of Ceres is not established by this packet.",
            "assessment": "MIXED",
            "evidence_paths": ["place.traffic_class", "facts.security_posture"],
            "target_entity_id": "CER-P05",
        },
    )
    assert ok, reasons


def test_not_established_sabotage_passes_without_fabricated_evidence():
    ok, reasons = mod.validate_answer(
        case("unsupported_sabotage_cause", "NOT_ESTABLISHED"),
        packet(),
        {
            "answer": "Current authoritative context does not establish sabotage as the cause.",
            "assessment": "NOT_ESTABLISHED",
            "evidence_paths": [],
            "target_entity_id": "CER-P05",
        },
    )
    assert ok, reasons


def test_contradicted_claim_requires_grounding():
    ok, reasons = mod.validate_answer(
        case("contradictory_user_claim", "CONTRADICTED", {"place.traffic_class", "facts.security_posture"}),
        packet(),
        {
            "answer": "That description is contradicted by the restricted traffic class and high security posture.",
            "assessment": "CONTRADICTED",
            "evidence_paths": ["place.traffic_class", "facts.security_posture"],
            "target_entity_id": "CER-P05",
        },
    )
    assert ok, reasons


def test_nonexistent_evidence_path_fails():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "SUPPORTED"),
        packet(),
        {
            "answer": "Grounded answer.",
            "assessment": "SUPPORTED",
            "evidence_paths": ["facts.secret_history"],
            "target_entity_id": "CER-P05",
        },
    )
    assert not ok
    assert "evidence_path_not_in_packet" in reasons


def test_invalid_assessment_fails():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "SUPPORTED"),
        packet(),
        {
            "answer": "Grounded answer.",
            "assessment": "MAYBE",
            "evidence_paths": ["facts.administrative"],
            "target_entity_id": "CER-P05",
        },
    )
    assert not ok
    assert "assessment_invalid" in reasons
    assert "assessment_mismatch" in reasons
