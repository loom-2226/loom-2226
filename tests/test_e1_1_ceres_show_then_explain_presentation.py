import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_ceres_show_then_explain_presentation.py"
spec = importlib.util.spec_from_file_location("e1_1_ceres_show_then_explain_presentation", MODULE_PATH)
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


def test_view_model_exposes_orientation_notice_and_next_questions():
    view = mod.build_view_model(_projection())
    assert view["schema"] == "LOOM_E1_1_CERES_PRESENTATION_VIEW_V1"
    assert view["entity"]["name"] == "Ceres"
    assert view["entity"]["summary"] == "Belt logistics hub"
    assert len(view["notice_cards"]) == 2
    assert view["notice_cards"][0]["entity_id"] == "CER-P05"
    assert "What is this place?" in view["ask_next"]
    assert "What is interesting here?" in view["ask_next"]


def test_view_model_preserves_zero_authority_and_offline_boundary():
    authority = mod.build_view_model(_projection())["authority"]
    assert authority["model_called"] is False
    assert authority["model_calculation_authority"] == "ZERO"
    assert authority["model_state_authority"] == "ZERO"
    assert authority["model_canon_authority"] == "ZERO"
    assert authority["campaign_mutation"] is False
    assert authority["canon_mutation"] is False
    assert authority["network_required"] is False


def test_renderer_is_self_contained_and_contains_no_remote_dependencies():
    rendered = mod.render_html(mod.build_view_model(_projection()))
    lower = rendered.lower()
    assert "<html" in lower
    assert "<script>" in lower
    assert "http://" not in lower
    assert "https://" not in lower
    assert "<link " not in lower
    assert "<script src=" not in lower
    assert "Ceres Metric &amp; Loom Anchorage" in rendered


def test_renderer_escapes_source_text():
    projection = _projection()
    projection["entity"]["summary"] = "<script>alert('no')</script>"
    rendered = mod.render_html(mod.build_view_model(projection))
    assert "<script>alert('no')</script>" not in rendered
    assert "&lt;script&gt;alert" in rendered


def test_fixed_input_renders_deterministically():
    view1 = mod.build_view_model(_projection())
    view2 = mod.build_view_model(_projection())
    assert view1 == view2
    assert mod.render_html(view1) == mod.render_html(view2)


def test_non_ceres_projection_fails_closed():
    projection = _projection()
    projection["entity"]["entity_id"] = "MARS"
    projection["entity"]["name"] = "Mars"
    try:
        mod.build_view_model(projection)
    except ValueError as exc:
        assert "bounded to Ceres/CER" in str(exc)
    else:
        raise AssertionError("expected non-Ceres projection to fail closed")
