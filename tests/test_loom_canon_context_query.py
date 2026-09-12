import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "src" / "loom_canon_context_query.py"
spec = importlib.util.spec_from_file_location("loom_canon_context_query", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def projection():
    return {
        "schema": "LOOM_CANON_CONTEXT_PROJECTION_V1",
        "entity": {
            "entity_id": "CER",
            "name": "Ceres",
            "summary": "Belt hub",
            "canon_status": "DERIVED CANON",
        },
        "regional_morphology": {
            "civil_authorities": "Ceres Commonwealth",
            "administrative_authorities": "Belt Transit Authority",
            "security_authorities": "Belt Security & Rescue Directorate",
            "network_form": "Network institutions do not imply Belt sovereignty.",
            "political_morphology": "Ceres Commonwealth embedded in Belt network compacts",
        },
        "mobility": {"transport_role": "bulk materials and network exchange"},
        "places": [
            {
                "entity_id": "CER-P03",
                "name": "Ceres Belt Exchange",
                "role": "ORBITAL_HABITAT_PORT",
                "traffic_class": "EXTREME",
                "authorities": {
                    "civil": "Ceres Commonwealth",
                    "administrative": "Belt Transit Authority",
                    "security": "Belt Security & Rescue Directorate",
                },
                "commercial": {
                    "primary": "Concord Mutual Infrastructure & Assurance",
                    "secondary": "Ferrum Meridian",
                    "regime": "PLURAL / NO DOMINANT",
                },
                "runtime_context": {
                    "strategic_importance": 0.78,
                    "governance_style": "NETWORK_COMPACT",
                    "commercial_openness": 0.46,
                    "security_posture": 0.67,
                    "outsider_attitude": 0.47,
                    "scarcity_pressure": 0.41,
                },
                "provenance": [{"database": "WORLD", "relation": "infrastructure_nodes"}],
            },
            {
                "entity_id": "CER-P05",
                "name": "Ceres Metric & Loom Anchorage",
                "role": "STRATEGIC_PORT",
                "traffic_class": "RESTRICTED",
                "authorities": {
                    "civil": "Ceres Commonwealth",
                    "administrative": "Belt Standards Directorate",
                    "security": "Belt Security & Rescue Directorate",
                },
                "commercial": {
                    "primary": "Axiom Precision & Metrology",
                    "secondary": "Ferrum Meridian",
                    "regime": "LEADING / CONTESTED",
                },
                "runtime_context": {
                    "strategic_importance": 0.688,
                    "governance_style": "CIVIC_ASSERTIVE",
                    "commercial_openness": 0.20,
                    "security_posture": 0.88,
                    "outsider_attitude": 0.32,
                    "scarcity_pressure": 0.55,
                },
                "provenance": [{"database": "CIVSTATE", "relation": "civ_runtime_place_context"}],
            },
        ],
        "authority_policy": {
            "read_only": True,
            "model_access_to_sqlite": False,
        },
        "provenance": {
            "entity": {"database": "WORLD", "relation": "atlas_profiles"},
            "regional_morphology": {"database": "WORLD", "relation": "regional_morphology"},
            "mobility": {"database": "WORLD", "relation": "region_mobility"},
        },
    }


def test_orient_is_small_and_grounded():
    out = mod.query_projection(projection(), "ORIENT")
    assert out["schema"] == "LOOM_CANON_CONTEXT_QUERY_V1"
    assert out["answer_kind"] == "ORIENTATION"
    assert out["facts"]["identity"]["value"]["name"] == "Ceres"
    assert out["facts"]["identity"]["provenance"]["relation"] == "atlas_profiles"
    assert out["authority_policy"]["model_state_authority"] == "ZERO"


def test_interesting_is_deterministic_and_marks_selection_non_authoritative():
    out = mod.query_projection(projection(), "INTERESTING", max_items=2)
    assert [x["entity_id"] for x in out["items"]] == ["CER-P05", "CER-P03"]
    assert all(x["why_selected"]["authority"] == "PRESENTATION_DERIVED_NON_AUTHORITY" for x in out["items"])


def test_who_runs_place_preserves_authority_separation():
    out = mod.query_projection(projection(), "WHO_RUNS", target_entity_id="CER-P05")
    assert out["facts"]["civil"]["value"] == "Ceres Commonwealth"
    assert out["facts"]["administrative"]["value"] == "Belt Standards Directorate"
    assert out["facts"]["security"]["value"] == "Belt Security & Rescue Directorate"
    assert out["facts"]["primary_commercial"]["value"] == "Axiom Precision & Metrology"


def test_place_detail_surfaces_behavior_without_inventing_prose():
    out = mod.query_projection(projection(), "PLACE_DETAIL", target_entity_id="CER-P05")
    assert out["facts"]["governance_style"]["value"] == "CIVIC_ASSERTIVE"
    assert out["facts"]["commercial_openness"]["value"] == 0.20
    assert out["facts"]["security_posture"]["value"] == 0.88
    assert out["facts"]["outsider_attitude"]["value"] == 0.32


def test_unknown_place_fails_closed():
    try:
        mod.query_projection(projection(), "PLACE_DETAIL", target_entity_id="CER-P99")
    except KeyError as exc:
        assert "Unknown projected place" in str(exc)
    else:
        raise AssertionError("unknown place did not fail closed")


def test_bad_authority_contract_fails_closed():
    p = projection()
    p["authority_policy"]["model_access_to_sqlite"] = True
    try:
        mod.query_projection(p, "ORIENT")
    except ValueError as exc:
        assert "model_access_to_sqlite=false" in str(exc)
    else:
        raise AssertionError("bad authority contract did not fail closed")
