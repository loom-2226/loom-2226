#!/usr/bin/env python3
"""Deterministic entity-reference resolution for compact Canon Context tools.

This adapter converts a caller-supplied reference into an entity_id using only
entities already present in the supplied read-only projection. It never creates
or infers entities. Resolution is exact after conservative normalization and
fails closed on unknown or ambiguous references.
"""
from __future__ import annotations

from typing import Any


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def resolve_projected_entity_id(projection: dict[str, Any], reference: str | None) -> str | None:
    if reference is None:
        return None
    token = _norm(reference)
    if not token:
        return None

    candidates: list[dict[str, Any]] = []
    entity = projection.get("entity")
    if isinstance(entity, dict):
        candidates.append(entity)
    for place in projection.get("places") or []:
        if isinstance(place, dict):
            candidates.append(place)

    matches: list[str] = []
    for item in candidates:
        entity_id = str(item.get("entity_id") or "").strip()
        if not entity_id:
            continue
        names = {_norm(entity_id), _norm(item.get("name"))}
        names.discard("")
        if token in names:
            matches.append(entity_id)

    unique = sorted(set(matches))
    if not unique:
        raise KeyError(f"Unknown projected entity reference: {reference}")
    if len(unique) != 1:
        raise ValueError(f"Ambiguous projected entity reference {reference!r}: {unique}")
    return unique[0]
