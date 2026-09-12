import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_mara_ceres_orientation_synthesis_v01.py"
spec = importlib.util.spec_from_file_location("e1_1_mara_ceres_orientation_synthesis_v01", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _projection():
    return {
        "schema": "LOOM_CANON_CONTEXT_PROJECTION_V1",
        "entity": {"entity_id": "CER", "name": "Ceres", "summary": "Belt logistics hub", "canon_status": "DERIVED CANON"},
        "regional_morphology": {"political_morphology": "Ceres Commonwealth embedded in Belt network compacts"},
        "mobility": {"transport_role": "bulk materials and Belt exchange"},
        "places": [
            {
                "entity_id": "CER-P05",
                "name": "Ceres Metric & Loom Anchorage",
                "role": "STRATEGIC_PORT",
                "traffic_class": "RESTRICTED",
                "runtime_context": {"strategic_importance": 0.688, "governance_style": "CIVIC_ASSERTIVE", "commercial_openness": 0.2},
                "provenance": [
                    {"database": "WORLD", "relation": "infrastructure_nodes"},
                    {"database": "CIVSTATE", "relation": "civ_runtime_place_context"},
                ],
            },
            {
                "entity_id": "CER-P03",
                "name": "Ceres Belt Exchange",
                "role": "ORBITAL_HABITAT_PORT",
                "traffic_class": "EXTREME",
                "runtime_context": {"strategic_importance": 0.78, "governance_style": "NETWORK_COMPACT", "commercial_openness": 0.46},
                "provenance": [
                    {"database": "WORLD", "relation": "infrastructure_nodes"},
                    {"database": "CIVSTATE", "relation": "civ_runtime_place_context"},
                ],
            },
        ],
        "provenance": {
            "entity": {"database": "WORLD", "relation": "atlas_profiles"},
            "regional_morphology": {"database": "WORLD", "relation": "regional_morphology"},
            "mobility": {"database": "WORLD", "relation": "region_mobility"},
        },
        "authority_policy": {"read_only": True, "model_access_to_sqlite": False},
    }


def test_build_evidence_uses_only_deterministic_query_packets():
    evidence = mod.build_evidence(_projection())
    assert evidence["schema"] == "LOOM_E1_1_MARA_CERES_SYNTHESIS_EVIDENCE_V1"
    assert evidence["orient"]["answer_kind"] == "ORIENTATION"
    assert evidence["interesting"]["answer_kind"] == "INTERESTING_PLACES"
    assert evidence["authority_policy"]["fact_selection"] == "DETERMINISTIC_PRECOMPUTED"
    assert evidence["authority_policy"]["place_ranking"] == "DETERMINISTIC_PRECOMPUTED"


def test_model_authority_is_zero():
    policy = mod.build_evidence(_projection())["authority_policy"]
    assert policy["model_calculation_authority"] == "ZERO"
    assert policy["model_state_authority"] == "ZERO"
    assert policy["model_canon_authority"] == "ZERO"
    assert policy["model_sqlite_access"] is False


def test_validator_requires_orientation_and_interest_grounding():
    evidence = mod.build_evidence(_projection())
    answer = {
        "answer": "Ceres is a Belt logistics hub; notice the restricted Metric & Loom Anchorage.",
        "assessment": "SUPPORTED",
        "evidence_paths": [
            "orient.facts.identity.value.summary",
            "interesting.items.0.name",
        ],
    }
    passed, reasons = mod.validate_answer(evidence, answer)
    assert passed is True
    assert reasons == []


def test_validator_rejects_invented_evidence_path():
    evidence = mod.build_evidence(_projection())
    answer = {
        "answer": "Something invented.",
        "assessment": "SUPPORTED",
        "evidence_paths": ["orient.facts.identity.value.summary", "interesting.items.99.name"],
    }
    passed, reasons = mod.validate_answer(evidence, answer)
    assert passed is False
    assert "evidence_path_not_in_packet" in reasons


def test_validator_rejects_missing_interest_grounding():
    evidence = mod.build_evidence(_projection())
    answer = {
        "answer": "Ceres is a Belt logistics hub.",
        "assessment": "SUPPORTED",
        "evidence_paths": ["orient.facts.identity.value.summary"],
    }
    passed, reasons = mod.validate_answer(evidence, answer)
    assert passed is False
    assert "interesting_grounding_missing" in reasons
