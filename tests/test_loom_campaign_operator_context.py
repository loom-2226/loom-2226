from __future__ import annotations

from copy import deepcopy

from src.loom_campaign_operator_context import (
    CampaignOperatorContextError,
    OUTPUT_SCHEMA,
    project_campaign_operator_context,
)


def _state():
    return {
        "schema": "LOOM_STATE_V1",
        "state_id": "S000008-1f8140b205a7",
        "state_sha256": "1f8140b205a7139be2cbf983a17b4b83c1c35e4b32a18a767c945c49b1843fdc",
        "revision": 8,
        "status": "ACTIVE",
        "epoch_utc": "2027-06-15T08:57:51.391985Z",
        "location_token": "MARS",
        "kinematic_boundary": {
            "status": "BODY_RENDEZVOUS",
            "source": "PYTHON_NAV_V1_A_TERMINAL_BOUNDARY",
        },
        "ship_identity": {
            "ship_name": "wayfarer",
            "ship_instance_id": "SHIP-444BFD9B8294",
            "ship_class": "WAYFARER",
            "ship_template": "WAYFARER_BASELINE",
        },
        "last_flight": {
            "route": "CERES>NEPTUNE",
            "arrival_epoch_utc": "2027-06-15T08:57:51.391985Z",
        },
    }


def test_projects_current_location_from_location_token():
    result = project_campaign_operator_context(_state())
    assert result["schema"] == OUTPUT_SCHEMA
    loc = result["operator_context"]["current_location"]
    assert loc["location_token"] == "MARS"
    assert loc["epoch_utc"] == "2027-06-15T08:57:51.391985Z"
    assert loc["kinematic_status"] == "BODY_RENDEZVOUS"


def test_does_not_infer_current_location_from_last_flight_route():
    state = _state()
    state["last_flight"]["route"] = "CERES>NEPTUNE"
    result = project_campaign_operator_context(state)
    assert result["operator_context"]["current_location"]["location_token"] == "MARS"


def test_preserves_navigator_authority_and_zero_model_authority():
    policy = project_campaign_operator_context(_state())["authority_policy"]
    assert policy["source_authority"] == "NAVIGATOR_CAMPAIGN_STATE"
    assert policy["location_authority"] == "NAVIGATOR_LOCATION_TOKEN"
    assert policy["model_calculation_authority"] == "ZERO"
    assert policy["model_state_authority"] == "ZERO"
    assert policy["model_canon_authority"] == "ZERO"
    assert policy["campaign_mutation"] is False
    assert policy["world_context_merged"] is False


def test_provenance_points_to_exact_campaign_fields():
    provenance = project_campaign_operator_context(_state())["provenance"]
    assert provenance["current_location.location_token"].endswith("$.location_token")
    assert provenance["current_location.epoch_utc"].endswith("$.epoch_utc")
    assert provenance["current_location.kinematic_status"].endswith("$.kinematic_boundary.status")


def test_input_state_is_not_mutated():
    state = _state()
    before = deepcopy(state)
    project_campaign_operator_context(state)
    assert state == before


def test_missing_location_fails_closed():
    state = _state()
    del state["location_token"]
    try:
        project_campaign_operator_context(state)
    except CampaignOperatorContextError as exc:
        assert "location_token" in str(exc)
    else:
        raise AssertionError("missing location_token should fail closed")


def test_missing_kinematic_status_fails_closed():
    state = _state()
    del state["kinematic_boundary"]["status"]
    try:
        project_campaign_operator_context(state)
    except CampaignOperatorContextError as exc:
        assert "kinematic_boundary.status" in str(exc)
    else:
        raise AssertionError("missing kinematic status should fail closed")


def test_schema_mismatch_fails_closed():
    state = _state()
    state["schema"] = "WRONG_SCHEMA"
    try:
        project_campaign_operator_context(state)
    except CampaignOperatorContextError as exc:
        assert "schema mismatch" in str(exc)
    else:
        raise AssertionError("schema mismatch should fail closed")
