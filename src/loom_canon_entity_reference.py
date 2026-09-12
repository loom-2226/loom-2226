#!/usr/bin/env python3
"""Deterministic entity-reference resolution for compact Canon Context tools.

This adapter converts a caller-supplied reference into an entity_id using only
entities already present in the supplied read-only projection. It never creates
or infers entities. Resolution is exact after conservative normalization and
fails closed on unknown or ambiguous references.

A place also receives one deterministic context-qualified alias: if its exact
projected name begins with the current context entity name plus a space, that
prefix may be omitted. Example: within a Ceres projection,
"Ceres Metric & Loom Anchorage" may be referenced exactly as
"Metric & Loom Anchorage". This is not fuzzy matching or suffix guessing; the
alias is mechanically derived from the active projection context.
"""
from __future__ import annotations

from typing import Any


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _aliases(projection: dict[str, Any], item: dict[str, Any]) -> set[str]:
    values = {_norm(item.get("entity_id")), _norm(item.get("name"))}
    context = projection.get("entity")
    context_name = _norm(context.get("name")) if isinstance(context, dict) else ""
    item_name = _norm(item.get("name"))
    prefix = f"{context_name} " if context_name else ""
    if prefix and item_name.startswith(prefix):
        shortened = item_name[len(prefix):].strip()
        if shortened:
            values.add(shortened)
    values.discard("")
    return values


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
        if token in _aliases(projection, item):
            matches.append(entity_id)

    unique = sorted(set(matches))
    if not unique:
        raise KeyError(f"Unknown projected entity reference: {reference}")
    if len(unique) != 1:
        raise ValueError(f"Ambiguous projected entity reference {reference!r}: {unique}")
    return unique[0]
