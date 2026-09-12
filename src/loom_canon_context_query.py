#!/usr/bin/env python3
"""LOOM 2226 deterministic compact Canon Context Query v0.1.

E1.1 additive/read-only projection layer. This module does not read SQLite and
has no world/campaign authority. It consumes LOOM_CANON_CONTEXT_PROJECTION_V1
and deterministically selects a small evidence-bearing answer packet suitable
for a UI or read-only Mara tool.

It deliberately does *not* parse natural language. Natural-language intent may
later map to one of these typed requests, but the model never decides facts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "LOOM_CANON_CONTEXT_PROJECTION_V1"
OUTPUT_SCHEMA = "LOOM_CANON_CONTEXT_QUERY_V1"
SUPPORTED_INTENTS = {
    "ORIENT",
    "INTERESTING",
    "WHO_RUNS",
    "PLACE_DETAIL",
}

_TRAFFIC_RANK = {
    "RESTRICTED": 5,
    "EXTREME": 4,
    "VERY HIGH": 3,
    "HIGH": 2,
    "MEDIUM": 1,
    "LOW": 0,
}


def _require_projection(projection: dict[str, Any]) -> None:
    if projection.get("schema") != INPUT_SCHEMA:
        raise ValueError(f"Expected {INPUT_SCHEMA}; got {projection.get('schema')!r}")
    policy = projection.get("authority_policy") or {}
    if policy.get("read_only") is not True:
        raise ValueError("Projection must declare read_only=true")
    if policy.get("model_access_to_sqlite") is not False:
        raise ValueError("Projection must declare model_access_to_sqlite=false")


def _place_by_id(projection: dict[str, Any], entity_id: str) -> dict[str, Any]:
    for place in projection.get("places") or []:
        if str(place.get("entity_id", "")).upper() == entity_id.upper():
            return place
    raise KeyError(f"Unknown projected place: {entity_id}")


def _fact(value: Any, source: Any, *, status: str = "SUPPORTED") -> dict[str, Any]:
    return {
        "value": value,
        "epistemic_status": status,
        "provenance": source,
    }


def _base(projection: dict[str, Any], intent: str, target_entity_id: str | None) -> dict[str, Any]:
    entity = projection.get("entity") or {}
    return {
        "schema": OUTPUT_SCHEMA,
        "request": {
            "intent": intent,
            "target_entity_id": target_entity_id,
        },
        "context_entity": {
            "entity_id": entity.get("entity_id"),
            "name": entity.get("name"),
        },
        "authority_policy": {
            "read_only": True,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_sqlite_access": False,
            "selection_authority": "PRESENTATION_DERIVED_NON_AUTHORITY",
        },
    }


def _orient(projection: dict[str, Any]) -> dict[str, Any]:
    entity = projection.get("entity") or {}
    morphology = projection.get("regional_morphology") or {}
    mobility = projection.get("mobility") or {}
    prov = projection.get("provenance") or {}
    return {
        "answer_kind": "ORIENTATION",
        "facts": {
            "identity": _fact(
                {
                    "entity_id": entity.get("entity_id"),
                    "name": entity.get("name"),
                    "summary": entity.get("summary"),
                    "canon_status": entity.get("canon_status"),
                },
                prov.get("entity"),
            ),
            "political_context": _fact(
                morphology.get("political_morphology"),
                prov.get("regional_morphology"),
                status="SUPPORTED" if morphology else "NOT_AVAILABLE",
            ),
            "transport_role": _fact(
                mobility.get("transport_role"),
                prov.get("mobility"),
                status="SUPPORTED" if mobility else "NOT_AVAILABLE",
            ),
        },
    }


def _interesting(projection: dict[str, Any], max_items: int) -> dict[str, Any]:
    def rank(place: dict[str, Any]) -> tuple[float, float, str]:
        runtime = place.get("runtime_context") or {}
        traffic = _TRAFFIC_RANK.get(str(place.get("traffic_class", "")).upper(), -1)
        strategic = runtime.get("strategic_importance")
        strategic_num = float(strategic) if isinstance(strategic, (int, float)) else -1.0
        return (-float(traffic), -strategic_num, str(place.get("entity_id", "")))

    places = sorted(projection.get("places") or [], key=rank)[:max_items]
    items = []
    for place in places:
        runtime = place.get("runtime_context") or {}
        items.append(
            {
                "entity_id": place.get("entity_id"),
                "name": place.get("name"),
                "role": place.get("role"),
                "traffic_class": place.get("traffic_class"),
                "strategic_importance": runtime.get("strategic_importance"),
                "governance_style": runtime.get("governance_style"),
                "commercial_openness": runtime.get("commercial_openness"),
                "why_selected": {
                    "method": "traffic_class_then_strategic_importance",
                    "authority": "PRESENTATION_DERIVED_NON_AUTHORITY",
                },
                "provenance": place.get("provenance"),
                "epistemic_status": "SUPPORTED",
            }
        )
    return {"answer_kind": "INTERESTING_PLACES", "items": items}


def _who_runs(projection: dict[str, Any], target_entity_id: str | None) -> dict[str, Any]:
    prov = projection.get("provenance") or {}
    if target_entity_id:
        place = _place_by_id(projection, target_entity_id)
        return {
            "answer_kind": "PLACE_AUTHORITY",
            "place": {"entity_id": place.get("entity_id"), "name": place.get("name")},
            "facts": {
                "civil": _fact(place.get("authorities", {}).get("civil"), place.get("provenance")),
                "administrative": _fact(place.get("authorities", {}).get("administrative"), place.get("provenance")),
                "security": _fact(place.get("authorities", {}).get("security"), place.get("provenance")),
                "primary_commercial": _fact(place.get("commercial", {}).get("primary"), place.get("provenance")),
            },
        }

    morphology = projection.get("regional_morphology") or {}
    return {
        "answer_kind": "REGIONAL_AUTHORITY",
        "facts": {
            "civil": _fact(morphology.get("civil_authorities"), prov.get("regional_morphology")),
            "administrative": _fact(morphology.get("administrative_authorities"), prov.get("regional_morphology")),
            "security": _fact(morphology.get("security_authorities"), prov.get("regional_morphology")),
            "network_form": _fact(morphology.get("network_form"), prov.get("regional_morphology")),
        },
    }


def _place_detail(projection: dict[str, Any], target_entity_id: str | None) -> dict[str, Any]:
    if not target_entity_id:
        raise ValueError("PLACE_DETAIL requires target_entity_id")
    place = _place_by_id(projection, target_entity_id)
    runtime = place.get("runtime_context") or {}
    return {
        "answer_kind": "PLACE_DETAIL",
        "place": {
            "entity_id": place.get("entity_id"),
            "name": place.get("name"),
            "role": place.get("role"),
            "traffic_class": place.get("traffic_class"),
        },
        "facts": {
            "governance_style": _fact(runtime.get("governance_style"), place.get("provenance")),
            "security_posture": _fact(runtime.get("security_posture"), place.get("provenance")),
            "commercial_openness": _fact(runtime.get("commercial_openness"), place.get("provenance")),
            "outsider_attitude": _fact(runtime.get("outsider_attitude"), place.get("provenance")),
            "scarcity_pressure": _fact(runtime.get("scarcity_pressure"), place.get("provenance")),
            "strategic_importance": _fact(runtime.get("strategic_importance"), place.get("provenance")),
            "authorities": _fact(place.get("authorities"), place.get("provenance")),
            "commercial": _fact(place.get("commercial"), place.get("provenance")),
        },
    }


def query_projection(
    projection: dict[str, Any],
    intent: str,
    *,
    target_entity_id: str | None = None,
    max_items: int = 3,
) -> dict[str, Any]:
    _require_projection(projection)
    token = intent.strip().upper()
    if token not in SUPPORTED_INTENTS:
        raise ValueError(f"Unsupported intent {intent!r}; expected one of {sorted(SUPPORTED_INTENTS)}")
    if max_items < 1 or max_items > 5:
        raise ValueError("max_items must be between 1 and 5")

    out = _base(projection, token, target_entity_id)
    if token == "ORIENT":
        body = _orient(projection)
    elif token == "INTERESTING":
        body = _interesting(projection, max_items)
    elif token == "WHO_RUNS":
        body = _who_runs(projection, target_entity_id)
    else:
        body = _place_detail(projection, target_entity_id)
    out.update(body)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--projection", required=True)
    p.add_argument("--intent", required=True, choices=sorted(SUPPORTED_INTENTS))
    p.add_argument("--target")
    p.add_argument("--max-items", type=int, default=3)
    p.add_argument("--out")
    args = p.parse_args()

    projection = json.loads(Path(args.projection).expanduser().read_text(encoding="utf-8"))
    result = query_projection(
        projection,
        args.intent,
        target_entity_id=args.target,
        max_items=args.max_items,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).expanduser().write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
