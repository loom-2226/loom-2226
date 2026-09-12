import importlib.util
from pathlib import Path

MODULE_PATH=Path(__file__).resolve().parents[1]/"engineering"/"experience_one"/"spikes"/"e1_1_ceres_show_then_explain_presentation_v02.py"
spec=importlib.util.spec_from_file_location("presentation_v02",MODULE_PATH); mod=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(mod)

def _projection():
    return {"schema":"LOOM_CANON_CONTEXT_PROJECTION_V1","entity":{"entity_id":"CER","name":"Ceres","summary":"database prose"},"regional_morphology":{"political_morphology":"Ceres Commonwealth embedded in Belt network compacts"},"mobility":{"transport_role":"bulk materials and Belt exchange"},"places":[{"entity_id":"CER-P05","name":"Ceres Metric & Loom Anchorage","role":"STRATEGIC_PORT","traffic_class":"RESTRICTED","runtime_context":{"strategic_importance":.688,"governance_style":"CIVIC_ASSERTIVE","commercial_openness":.2},"provenance":[{"database":"WORLD","relation":"infrastructure_nodes"},{"database":"CIVSTATE","relation":"civ_runtime_place_context"}]}],"provenance":{"entity":{"database":"WORLD","relation":"atlas_profiles"},"regional_morphology":{"database":"WORLD","relation":"regional_morphology"},"mobility":{"database":"WORLD","relation":"region_mobility"}},"authority_policy":{"read_only":True,"model_access_to_sqlite":False}}

def _synthesis():
    return {"structural_pass":True,"assessment":"SUPPORTED","evidence_paths":["orient.facts.identity.value","interesting.items[0]"],"answer":"Ceres is a Belt logistics and exchange hub. Notice the restricted Metric & Loom Anchorage."}

def test_uses_qualified_synthesis_as_human_facing_explain():
    view=mod.build_view_model(_projection(),_synthesis()); assert view["entity"]["explain"]==_synthesis()["answer"]; assert view["entity"]["explain"]!="database prose"

def test_machine_metrics_are_not_primary_card_copy():
    rendered=mod.render_html(mod.build_view_model(_projection(),_synthesis())); assert "<summary>Details</summary>" in rendered; assert "Strategic <b>0.688</b>" in rendered; assert "Ask Mara about this" in rendered

def test_machine_labels_are_humanized():
    rendered=mod.render_html(mod.build_view_model(_projection(),_synthesis())); assert "Strategic Port · Restricted" in rendered; assert "Civic Assertive" in rendered; assert "STRATEGIC_PORT" not in rendered; assert "CIVIC_ASSERTIVE" not in rendered

def test_top_level_mara_affordance_precedes_cards():
    rendered=mod.render_html(mod.build_view_model(_projection(),_synthesis())); assert rendered.index("Ask Mara what matters here") < rendered.index("What to notice")

def test_authority_boundary_remains_zero_and_offline():
    view=mod.build_view_model(_projection(),_synthesis()); a=view["authority"]; assert a["model_called"] is False; assert a["network_required"] is False; assert a["campaign_mutation"] is False; assert a["canon_mutation"] is False; assert a["model_calculation_authority"]=="ZERO"; assert a["model_state_authority"]=="ZERO"; assert a["model_canon_authority"]=="ZERO"

def test_unqualified_synthesis_fails_closed():
    bad=_synthesis(); bad["structural_pass"]=False
    try: mod.build_view_model(_projection(),bad)
    except ValueError as exc: assert "structural_pass" in str(exc)
    else: raise AssertionError("expected unqualified synthesis to fail closed")

def test_non_ceres_projection_still_fails_closed():
    p=_projection(); p["entity"]["entity_id"]="MARS"
    try: mod.build_view_model(p,_synthesis())
    except ValueError as exc: assert "bounded to Ceres/CER" in str(exc)
    else: raise AssertionError("expected non-Ceres projection to fail closed")

def test_fixed_inputs_render_deterministically():
    v1=mod.build_view_model(_projection(),_synthesis()); v2=mod.build_view_model(_projection(),_synthesis()); assert v1==v2; assert mod.render_html(v1)==mod.render_html(v2)
