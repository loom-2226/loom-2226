import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_mara_grounded_synthesis_v05.py"
spec = importlib.util.spec_from_file_location("e1_1_mara_grounded_synthesis_v05", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def packet():
    return {
        "place": {"entity_id": "CER-P05", "role": "STRATEGIC_PORT", "traffic_class": "RESTRICTED"},
        "facts": {
            "administrative": {"value": "Belt Standards Directorate"},
            "civil": {"value": "Ceres Commonwealth"},
            "security": {"value": "Belt Security & Rescue Directorate"},
            "primary_commercial": {"value": "Axiom Precision & Metrology"},
            "security_posture": {"value": 0.875},
            "commercial_openness": {"value": 0.20},
        },
    }


def case(case_id, assessment, required=None):
    return {
        "id": case_id,
        "expected_assessment": assessment,
        "expected_target": "CER-P05",
        "required_any_paths": set(required or []),
    }


def answer(assessment, paths):
    return {
        "answer": "bounded synthesis",
        "assessment": assessment,
        "evidence_paths": paths,
        "target_entity_id": "CER-P05",
    }


def test_descendant_value_path_satisfies_required_field():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "MIXED", {"facts.administrative"}),
        packet(),
        answer("MIXED", ["facts.administrative.value"]),
    )
    assert ok, reasons


def test_invalid_evidence_path_still_fails_closed():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "MIXED", {"facts.administrative"}),
        packet(),
        answer("MIXED", ["facts.secret_operator.value"]),
    )
    assert not ok
    assert "evidence_path_not_in_packet" in reasons


def test_not_established_is_not_rejected_for_negated_sabotage_phrase():
    a = answer("NOT_ESTABLISHED", ["place.traffic_class"])
    a["answer"] = "The evidence does not establish that sabotage caused it."
    ok, reasons = mod.validate_answer(case("unsupported_sabotage_cause", "NOT_ESTABLISHED"), packet(), a)
    assert ok, reasons


def test_contradicted_answer_may_quote_rejected_user_phrase():
    a = answer("CONTRADICTED", ["place.traffic_class", "facts.security_posture"])
    a["answer"] = "It is restricted, not an open, lightly policed tourist port."
    ok, reasons = mod.validate_answer(
        case("contradictory_user_claim", "CONTRADICTED", {"place.traffic_class"}),
        packet(),
        a,
    )
    assert ok, reasons


def test_who_runs_it_mixed_requires_real_authority_grounding():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "MIXED", {"facts.civil", "facts.administrative", "facts.security", "facts.primary_commercial"}),
        packet(),
        answer("MIXED", ["facts.civil.value", "facts.security.value"]),
    )
    assert ok, reasons


def test_assessment_mismatch_still_fails():
    ok, reasons = mod.validate_answer(
        case("who_runs_it", "MIXED", {"facts.civil"}),
        packet(),
        answer("SUPPORTED", ["facts.civil.value"]),
    )
    assert not ok
    assert "assessment_mismatch" in reasons
