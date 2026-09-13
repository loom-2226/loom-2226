import json
from pathlib import Path


MATRIX = Path("engineering/current/wayfarer_torch_feedstock_screening_v0.2.json")


def load_matrix():
    return json.loads(MATRIX.read_text(encoding="utf-8"))


def test_feedstock_screening_preserves_optionality():
    doc = load_matrix()
    species = {row["species"] for row in doc["feeds"]}
    assert {"H2O", "NH3", "Ar", "N2", "CO2", "H2", "O2", "CH4", "CO"} <= species
    assert len(doc["provisional_doctrine"]["alternates"]) >= 2


def test_water_is_primary_candidate_not_unique_engine_requirement():
    doc = load_matrix()
    assert doc["provisional_doctrine"]["primary"] == "H2O"
    water = next(row for row in doc["feeds"] if row["species"] == "H2O")
    assert water["screening"] == "ADVANCE_PRIMARY"
    assert "species-independent" in doc["design_rule"]


def test_no_false_final_certification_in_screening_matrix():
    doc = load_matrix()
    forbidden = {"CERTIFIED", "DERATED", "PROHIBITED"}
    values = {rating for row in doc["feeds"] for rating in row["mode_screen"].values()}
    assert not (values & forbidden)
    assert "final CERTIFIED/DERATED/CONTINGENCY/PROHIBITED" in doc["authority_boundary"]


def test_co_is_deferred_not_silently_dropped():
    doc = load_matrix()
    co = next(row for row in doc["feeds"] if row["species"] == "CO")
    assert co["screening"] == "DEFER"
    assert all(v == "DEFER" for v in co["mode_screen"].values())
