import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_mara_grounded_synthesis.py"
spec = importlib.util.spec_from_file_location("e1_1_mara_grounded_synthesis", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def packet():
    return {
        "schema": "LOOM_CANON_CONTEXT_QUERY_V1",
        "request": {"intent": "PLACE_DETAIL", "target_entity_id": "CER-P05"},
        "facts": {
            "security_posture": {"value": 0.875, "epistemic_status": "SUPPORTED"},
            "commercial_openness": {"value": 0.20, "epistemic_status": "SUPPORTED"},
            "outsider_attitude": {"value": 0.32, "epistemic_status": "SUPPORTED"},
            "governance_style": {"value": "CIVIC_ASSERTIVE", "epistemic_status": "SUPPORTED"},
        },
    }


def case(case_id, expected_status="SUPPORTED", required=None):
    return {
        "id": case_id,
        "expected_status": expected_status,
        "expected_target": "CER-P05",
        "required_any_fact_keys": set(required or []),
    }


def test_supported_grounded_answer_passes():
    ok, reasons = mod.validate_answer(
        case("why_restricted", required={"security_posture", "commercial_openness"}),
        packet(),
        {
            "answer": "It is restricted and security-heavy, with low commercial openness.",
            "epistemic_status": "SUPPORTED",
            "used_fact_keys": ["security_posture", "commercial_openness"],
            "target_entity_id": "CER-P05",
        },
    )
    assert ok, reasons


def test_used_fact_key_must_exist_in_packet():
    ok, reasons = mod.validate_answer(
        case("why_restricted", required={"security_posture"}),
        packet(),
        {
            "answer": "Grounded.",
            "epistemic_status": "SUPPORTED",
            "used_fact_keys": ["security_posture", "secret_history"],
            "target_entity_id": "CER-P05",
        },
    )
    assert not ok
    assert "used_fact_key_not_in_packet" in reasons


def test_unsupported_cause_requires_not_available_language():
    ok, reasons = mod.validate_answer(
        case("unsupported_sabotage_cause", expected_status="NOT_AVAILABLE"),
        packet(),
        {
            "answer": "The sabotage cause is NOT AVAILABLE from current authoritative context.",
            "epistemic_status": "NOT_AVAILABLE",
            "used_fact_keys": [],
            "target_entity_id": "CER-P05",
        },
    )
    assert ok, reasons


def test_unsupported_sabotage_assertion_fails():
    ok, reasons = mod.validate_answer(
        case("unsupported_sabotage_cause", expected_status="NOT_AVAILABLE"),
        packet(),
        {
            "answer": "It was locked down because of sabotage last week.",
            "epistemic_status": "NOT_AVAILABLE",
            "used_fact_keys": [],
            "target_entity_id": "CER-P05",
        },
    )
    assert not ok
    assert "unsupported_sabotage_asserted" in reasons


def test_contradictory_user_claim_cannot_be_repeated_as_fact():
    ok, reasons = mod.validate_answer(
        case("contradictory_user_claim", required={"security_posture"}),
        packet(),
        {
            "answer": "It is an open, lightly policed tourist port.",
            "epistemic_status": "SUPPORTED",
            "used_fact_keys": ["security_posture"],
            "target_entity_id": "CER-P05",
        },
    )
    assert not ok
    assert "user_contradiction_repeated_as_fact" in reasons
