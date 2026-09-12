#!/usr/bin/env python3
from __future__ import annotations

"""Fail-closed E1.1 handoff from Navigator location to Canon Context.

Runtime change class
--------------------
Additive read-only bounded adapter. This is NOT a generalized Experience Context
merger. It keeps Navigator campaign state and Canon Context as separately labelled
sources and refuses unsupported entities or temporal mismatches.

Compatibility / dependencies
----------------------------
- consumes LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1;
- calls the existing read-only LOOM_CANON_CONTEXT_PROJECTION_V1 builder;
- changes no Navigator schema, campaign mutation path, browser behavior, launcher,
  release path, WORLD/CIVSTATE data, or Pixel/Windows behavior;
- model calculation/state/canon authority remains ZERO.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from loom_canon_context_projection import build_projection

OPERATOR_SCHEMA = "LOOM_CAMPAIGN_OPERATOR_CONTEXT_V1"
CANON_SCHEMA = "LOOM_CANON_CONTEXT_PROJECTION_V1"
OUTPUT_SCHEMA = "LOOM_CURRENT_PLACE_HANDOFF_V1"


class CurrentPlaceHandoffError(ValueError):
    """Raised when the handoff input violates its typed authority contract."""


def _campaign_year(epoch_utc: str) -> int:
    if not isinstance(epoch_utc, str) or not epoch_utc.strip():
        raise CurrentPlaceHandoffError("missing operator epoch")
    text = epoch_utc.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).year
    except ValueError as exc:
        raise CurrentPlaceHandoffError("invalid operator epoch") from exc


def _collect_reference_years(value: Any, years: set[int]) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key == "year" and isinstance(child, int) and not isinstance(child, bool):
                years.add(child)
            else:
                _collect_reference_years(child, years)
    elif isinstance(value, list):
        for child in value:
            _collect_reference_years(child, years)


def _canon_reference_year(projection: Mapping[str, Any]) -> int | None:
    years: set[int] = set()
    _collect_reference_years(projection, years)
    if not years:
        return None
    if len(years) != 1:
        raise CurrentPlaceHandoffError(
            "canon projection contains multiple reference years; temporal scope is ambiguous"
        )
    return next(iter(years))


def _operator_location(operator_context: Mapping[str, Any]) -> tuple[str, str, int]:
    if operator_context.get("schema") != OPERATOR_SCHEMA:
        raise CurrentPlaceHandoffError("operator context schema mismatch")
    policy = operator_context.get("authority_policy")
    if not isinstance(policy, Mapping):
        raise CurrentPlaceHandoffError("operator authority policy missing")
    if policy.get("location_authority") != "NAVIGATOR_LOCATION_TOKEN":
        raise CurrentPlaceHandoffError("Navigator location authority not preserved")
    if policy.get("model_state_authority") != "ZERO":
        raise CurrentPlaceHandoffError("model state authority must remain ZERO")
    if policy.get("world_context_merged") is not False:
        raise CurrentPlaceHandoffError("operator context must not pre-merge world context")

    root = operator_context.get("operator_context")
    if not isinstance(root, Mapping):
        raise CurrentPlaceHandoffError("operator context payload missing")
    current = root.get("current_location")
    if not isinstance(current, Mapping):
        raise CurrentPlaceHandoffError("current location payload missing")
    token = current.get("location_token")
    epoch = current.get("epoch_utc")
    if not isinstance(token, str) or not token.strip():
        raise CurrentPlaceHandoffError("current location token missing")
    if not isinstance(epoch, str) or not epoch.strip():
        raise CurrentPlaceHandoffError("current location epoch missing")
    return token.strip().upper(), epoch.strip(), _campaign_year(epoch)


def resolve_current_place_handoff(
    operator_context: Mapping[str, Any],
    world_db: Path,
    civstate_db: Path,
) -> dict[str, Any]:
    """Resolve current-place Canon Context without merging source authorities.

    Statuses are deliberately human-boundary safe:
    - UNSUPPORTED_ENTITY: current Navigator location has no supported projection;
    - TEMPORAL_SCOPE_UNKNOWN: projection lacks a single evidenced reference year;
    - TEMPORAL_MISMATCH: campaign year differs from canon projection year;
    - AVAILABLE: supported entity and compatible temporal scope.

    On every non-AVAILABLE status, ``canon_context`` is None so callers cannot
    narrate over rejected facts by accident.
    """
    token, epoch, campaign_year = _operator_location(operator_context)

    common = {
        "schema": OUTPUT_SCHEMA,
        "current_location": {
            "location_token": token,
            "epoch_utc": epoch,
            "campaign_year": campaign_year,
            "source": "NAVIGATOR_CAMPAIGN_STATE",
        },
        "authority_policy": {
            "location_authority": "NAVIGATOR_LOCATION_TOKEN",
            "canon_source_authority": "CANON_CONTEXT_PROJECTION",
            "sources_merged": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "campaign_mutation": False,
            "canon_mutation": False,
        },
    }

    try:
        projection = build_projection(world_db, civstate_db, token)
    except ValueError:
        return {
            **common,
            "status": "UNSUPPORTED_ENTITY",
            "canon_reference_year": None,
            "canon_context": None,
            "human_message": f"Canon context is unavailable for the current location {token}.",
        }

    if projection.get("schema") != CANON_SCHEMA:
        raise CurrentPlaceHandoffError("canon projection schema mismatch")

    canon_year = _canon_reference_year(projection)
    if canon_year is None:
        return {
            **common,
            "status": "TEMPORAL_SCOPE_UNKNOWN",
            "canon_reference_year": None,
            "canon_context": None,
            "human_message": "Canon context is unavailable because its temporal scope is not established.",
        }

    if campaign_year != canon_year:
        return {
            **common,
            "status": "TEMPORAL_MISMATCH",
            "canon_reference_year": canon_year,
            "canon_context": None,
            "human_message": (
                f"Canon context is unavailable because the campaign year {campaign_year} "
                f"does not match the canon reference year {canon_year}."
            ),
        }

    return {
        **common,
        "status": "AVAILABLE",
        "canon_reference_year": canon_year,
        "canon_context": projection,
        "human_message": f"Canon context is available for the current location {token}.",
    }
