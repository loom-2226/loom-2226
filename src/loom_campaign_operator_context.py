#!/usr/bin/env python3
from __future__ import annotations

"""Read-only operator context projection over Navigator-owned campaign state.

Runtime change class
--------------------
Additive read-only projection / bounded adapter for Experience One E1.1.

Compatibility
-------------
No Navigator mutation semantics, state schema, browser behavior, launchers, or
Pixel/Windows paths are changed. Navigator remains the sole campaign-state authority.
This module consumes an already-loaded LOOM_STATE_V1 object and emits a compact,
reconstructible read-only context packet for questions such as "Where am I?".

Authority
---------
- Navigator campaign state owns ship/location/epoch truth.
- This adapter owns no state and performs no campaign mutation.
- LLM calculation/state/canon authority remains ZERO.
- Canon/world context is intentionally not merged here.
"""

from copy import deepcopy
from typing import Any, Mapping

STATE_SCHEMA = "LOOM_STATE_V1"
OUTPUT_SCHEMA = "LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1"


class CampaignOperatorContextError(ValueError):
    """Raised when required Navigator campaign-state evidence is unavailable."""


def _required_text(state: Mapping[str, Any], key: str) -> str:
    value = state.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CampaignOperatorContextError(f"missing required campaign field: {key}")
    return value


def _required_mapping(state: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = state.get(key)
    if not isinstance(value, Mapping):
        raise CampaignOperatorContextError(f"missing required campaign object: {key}")
    return value


def project_campaign_operator_context(state: Mapping[str, Any]) -> dict[str, Any]:
    """Project a compact read-only operator context from Navigator campaign state.

    The function deliberately treats ``location_token`` as current location authority.
    It does not infer current location from ``last_flight.route`` or surrounding canon.
    """
    if not isinstance(state, Mapping):
        raise CampaignOperatorContextError("campaign state must be a mapping")
    if state.get("schema") != STATE_SCHEMA:
        raise CampaignOperatorContextError("campaign state schema mismatch")

    location_token = _required_text(state, "location_token")
    epoch_utc = _required_text(state, "epoch_utc")
    state_id = _required_text(state, "state_id")
    embedded_state_sha256 = _required_text(state, "state_sha256")

    kinematic = _required_mapping(state, "kinematic_boundary")
    kinematic_status = kinematic.get("status")
    if not isinstance(kinematic_status, str) or not kinematic_status.strip():
        raise CampaignOperatorContextError("missing required campaign field: kinematic_boundary.status")
    kinematic_source = kinematic.get("source")
    if kinematic_source is not None and not isinstance(kinematic_source, str):
        raise CampaignOperatorContextError("invalid campaign field: kinematic_boundary.source")

    identity = _required_mapping(state, "ship_identity")
    ship_name = identity.get("ship_name")
    ship_instance_id = identity.get("ship_instance_id")
    ship_class = identity.get("ship_class")
    ship_template = identity.get("ship_template")
    for key, value in (
        ("ship_identity.ship_name", ship_name),
        ("ship_identity.ship_instance_id", ship_instance_id),
        ("ship_identity.ship_class", ship_class),
        ("ship_identity.ship_template", ship_template),
    ):
        if not isinstance(value, str) or not value.strip():
            raise CampaignOperatorContextError(f"missing required campaign field: {key}")

    # Copy only the compact facts required by the operator-context contract.
    return {
        "schema": OUTPUT_SCHEMA,
        "operator_context": {
            "ship": {
                "ship_name": ship_name,
                "ship_instance_id": ship_instance_id,
                "ship_class": ship_class,
                "ship_template": ship_template,
            },
            "current_location": {
                "location_token": location_token,
                "epoch_utc": epoch_utc,
                "kinematic_status": kinematic_status,
                "kinematic_source": kinematic_source,
            },
            "campaign_state": {
                "state_id": state_id,
                "state_sha256": embedded_state_sha256,
                "revision": deepcopy(state.get("revision")),
                "status": deepcopy(state.get("status")),
            },
        },
        "provenance": {
            "ship": "NAVIGATOR_CAMPAIGN_STATE:$.ship_identity",
            "current_location.location_token": "NAVIGATOR_CAMPAIGN_STATE:$.location_token",
            "current_location.epoch_utc": "NAVIGATOR_CAMPAIGN_STATE:$.epoch_utc",
            "current_location.kinematic_status": "NAVIGATOR_CAMPAIGN_STATE:$.kinematic_boundary.status",
            "current_location.kinematic_source": "NAVIGATOR_CAMPAIGN_STATE:$.kinematic_boundary.source",
            "campaign_state": "NAVIGATOR_CAMPAIGN_STATE:$",
        },
        "authority_policy": {
            "source_authority": "NAVIGATOR_CAMPAIGN_STATE",
            "projection_authority": "READ_ONLY_NON_STATE",
            "location_authority": "NAVIGATOR_LOCATION_TOKEN",
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "model_sqlite_access": False,
            "campaign_mutation": False,
            "canon_mutation": False,
            "world_context_merged": False,
        },
    }
