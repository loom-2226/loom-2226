import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "src" / "loom_canon_entity_reference.py"
spec = importlib.util.spec_from_file_location("loom_canon_entity_reference", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def projection():
    return {
        "entity": {"entity_id": "CER", "name": "Ceres"},
        "places": [
            {"entity_id": "CER-P05", "name": "Ceres Metric & Loom Anchorage"},
            {"entity_id": "CER-P03", "name": "Ceres Belt Exchange"},
        ],
    }


def test_resolves_entity_id_exactly():
    assert mod.resolve_projected_entity_id(projection(), "CER-P05") == "CER-P05"


def test_resolves_exact_projected_name():
    assert mod.resolve_projected_entity_id(projection(), "Ceres Metric & Loom Anchorage") == "CER-P05"


def test_resolution_normalizes_case_and_whitespace_only():
    assert mod.resolve_projected_entity_id(projection(), "  ceres   metric & loom anchorage ") == "CER-P05"


def test_unknown_reference_fails_closed():
    try:
        mod.resolve_projected_entity_id(projection(), "Some Plausible Port")
    except KeyError as exc:
        assert "Unknown projected entity reference" in str(exc)
    else:
        raise AssertionError("unknown reference did not fail closed")


def test_ambiguous_name_fails_closed():
    p = projection()
    p["places"].append({"entity_id": "CER-P99", "name": "Ceres Belt Exchange"})
    try:
        mod.resolve_projected_entity_id(p, "Ceres Belt Exchange")
    except ValueError as exc:
        assert "Ambiguous projected entity reference" in str(exc)
    else:
        raise AssertionError("ambiguous reference did not fail closed")
