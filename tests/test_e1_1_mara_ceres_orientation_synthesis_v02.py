import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "engineering" / "experience_one" / "spikes" / "e1_1_mara_ceres_orientation_synthesis_v02.py"
spec = importlib.util.spec_from_file_location("e1_1_mara_ceres_orientation_synthesis_v02", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def _evidence():
    return {
        "orient": {"facts": {"identity": {"value": {"summary": "Belt logistics hub"}}}},
        "interesting": {
            "items": [
                {"name": "Ceres Metric & Loom Anchorage"},
                {"name": "Ceres Belt Exchange"},
                {"name": "Ceres Shipyard Arc"},
            ]
        },
    }


def test_path_exists_accepts_json_style_list_index():
    evidence = _evidence()
    assert mod.path_exists(evidence, "interesting.items[0]") is True
    assert mod.path_exists(evidence, "interesting.items[1].name") is True


def test_path_exists_preserves_dotted_numeric_index_compatibility():
    evidence = _evidence()
    assert mod.path_exists(evidence, "interesting.items.0.name") is True


def test_path_exists_rejects_out_of_range_and_negative_indices():
    evidence = _evidence()
    assert mod.path_exists(evidence, "interesting.items[99]") is False
    assert mod.path_exists(evidence, "interesting.items[-1]") is False


def test_path_exists_rejects_malformed_brackets():
    evidence = _evidence()
    assert mod.path_exists(evidence, "interesting.items[]") is False
    assert mod.path_exists(evidence, "interesting.items[abc]") is False
    assert mod.path_exists(evidence, "interesting.items[0") is False


def test_validator_accepts_exact_empirical_v01_grounding_shape():
    evidence = _evidence()
    answer = {
        "answer": "Ceres is a Belt logistics hub; notice its major ports.",
        "assessment": "SUPPORTED",
        "evidence_paths": [
            "orient.facts.identity.value",
            "interesting.items[0]",
            "interesting.items[1]",
            "interesting.items[2]",
        ],
    }
    passed, reasons = mod.validate_answer(evidence, answer)
    assert passed is True
    assert reasons == []


def test_validator_still_rejects_nonexistent_indexed_evidence():
    evidence = _evidence()
    answer = {
        "answer": "Invented.",
        "assessment": "SUPPORTED",
        "evidence_paths": [
            "orient.facts.identity.value",
            "interesting.items[99]",
        ],
    }
    passed, reasons = mod.validate_answer(evidence, answer)
    assert passed is False
    assert "evidence_path_not_in_packet" in reasons
