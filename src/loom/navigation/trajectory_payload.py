"""Structural discovery of Navigator's authoritative Sequence-B payload.

The frozen Navigator remains authoritative. This module performs no trajectory
math and no interpolation. It only locates a packed flight-solutions payload by
validating the payload's own declared codec/header, then promotes that exact
binary object into the canonical adapter location used by LOOM_ROUTE_LAYER_V1.

This deliberately avoids coupling live GIS planning to one legacy dictionary
key or container shape.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import FlightPlan
from .flight_payload import FlightPayloadDecodeError, decode_flight_solutions


_MAX_DEPTH = 8


def _bytes_candidate(value: Any) -> bytes | None:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, memoryview):
        return value.tobytes()
    return None


def find_sequence_b_payload(value: Any, *, _depth: int = 0, _seen: set[int] | None = None) -> bytes | None:
    """Return the first structurally valid packed Sequence-B payload, if any.

    A candidate is accepted only when Navigator's payload decoder validates the
    embedded payload version and binary codec. Arbitrary bytes are never treated
    as trajectory truth.
    """
    if _depth > _MAX_DEPTH:
        return None
    if _seen is None:
        _seen = set()

    raw = _bytes_candidate(value)
    if raw is not None:
        try:
            decode_flight_solutions(raw)
            return raw
        except FlightPayloadDecodeError:
            return None

    oid = id(value)
    if oid in _seen:
        return None
    _seen.add(oid)

    if isinstance(value, Mapping):
        # Prefer semantically likely fields, but correctness comes from the
        # payload header validation rather than the key name.
        preferred = (
            "flightSolutionsPayload",
            "flight_solutions_payload",
            "flight_solutions",
            "trajectory_payload",
            "payloads",
        )
        for key in preferred:
            if key in value:
                found = find_sequence_b_payload(value[key], _depth=_depth + 1, _seen=_seen)
                if found is not None:
                    return found
        for key, child in value.items():
            if key in preferred:
                continue
            found = find_sequence_b_payload(child, _depth=_depth + 1, _seen=_seen)
            if found is not None:
                return found
        return None

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray, memoryview)):
        for child in value:
            found = find_sequence_b_payload(child, _depth=_depth + 1, _seen=_seen)
            if found is not None:
                return found
    return None


def promote_sequence_b_payload(plan: FlightPlan) -> FlightPlan:
    """Return an equivalent FlightPlan with the authoritative payload normalized.

    If no valid Sequence-B binary payload exists, the original plan is returned
    unchanged. No values are synthesized.
    """
    packed = dict(plan.payload)
    payloads = packed.get("payloads")
    if isinstance(payloads, Mapping):
        existing = _bytes_candidate(payloads.get("flightSolutionsPayload"))
        if existing is not None:
            try:
                decode_flight_solutions(existing)
                return plan
            except FlightPayloadDecodeError:
                pass

    found = find_sequence_b_payload(packed)
    if found is None:
        return plan

    normalized_payloads = dict(payloads) if isinstance(payloads, Mapping) else {}
    normalized_payloads["flightSolutionsPayload"] = found
    packed["payloads"] = normalized_payloads
    return FlightPlan(
        flight_id=plan.flight_id,
        candidate=plan.candidate,
        segments=plan.segments,
        arrival_state=plan.arrival_state,
        payload=packed,
    )
