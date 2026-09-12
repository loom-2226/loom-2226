#!/usr/bin/env python3
from __future__ import annotations

"""E1.1 deterministic Ceres legibility discriminator.

This is a diagnostic harness, not production composition architecture. It uses the
existing disposable 2226 Ceres operator fixture, existing Navigator operator-context
projection, existing fail-closed current-place handoff, and existing Canon Context
query layer to ask the two smallest preregistered world-texture questions:

- What is this place?      -> ORIENT
- What is interesting here? -> INTERESTING

No model is called. No source database or campaign state is mutated.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loom_campaign_operator_context import project_campaign_operator_context
from loom_current_place_handoff import resolve_current_place_handoff
from loom_canon_context_query import query_projection

RESULT_SCHEMA = "LOOM_E1_1_CERES_LEGIBILITY_QUERY_RESULT_V1"


def _supported_fact_count(orient: dict[str, Any]) -> int:
    facts = orient.get("facts") or {}
    count = 0
    for fact in facts.values():
        if isinstance(fact, dict) and fact.get("epistemic_status") == "SUPPORTED" and fact.get("value") not in (None, "", [], {}):
            count += 1
    return count


def evaluate_legibility(
    state: dict[str, Any],
    world_db: Path,
    civstate_db: Path,
    *,
    max_items: int = 3,
) -> dict[str, Any]:
    operator = project_campaign_operator_context(state)
    handoff = resolve_current_place_handoff(operator, world_db, civstate_db)
    if handoff.get("status") != "AVAILABLE":
        return {
            "schema": RESULT_SCHEMA,
            "status": "BLOCKED_BY_HANDOFF",
            "handoff_status": handoff.get("status"),
            "handoff_message": handoff.get("human_message"),
            "all_pass": False,
            "authority": {
                "model_called": False,
                "campaign_mutation": False,
                "canon_mutation": False,
            },
        }

    projection = handoff["canon_context"]
    orient = query_projection(projection, "ORIENT")
    interesting = query_projection(projection, "INTERESTING", max_items=max_items)

    # Repeat exactly to demonstrate deterministic query packets from fixed inputs.
    orient_repeat = query_projection(projection, "ORIENT")
    interesting_repeat = query_projection(projection, "INTERESTING", max_items=max_items)

    identity = ((orient.get("facts") or {}).get("identity") or {}).get("value") or {}
    items = interesting.get("items") or []

    checks = {
        "handoff_available": handoff.get("status") == "AVAILABLE",
        "current_location_is_ceres": (handoff.get("current_location") or {}).get("location_token") == "CERES",
        "temporal_scope_is_2226": handoff.get("canon_reference_year") == 2226,
        "orient_context_is_ceres": (orient.get("context_entity") or {}).get("entity_id") == "CER",
        "orient_identity_named": bool(identity.get("name")),
        "orient_summary_present": bool(identity.get("summary")),
        "orient_supported_fact_count_at_least_two": _supported_fact_count(orient) >= 2,
        "interesting_items_present": len(items) >= 1,
        "interesting_items_unique": len({item.get("entity_id") for item in items}) == len(items),
        "interesting_items_grounded": all(
            bool(item.get("entity_id"))
            and bool(item.get("name"))
            and bool(item.get("role"))
            and bool(item.get("traffic_class"))
            and item.get("epistemic_status") == "SUPPORTED"
            and bool((item.get("why_selected") or {}).get("inputs"))
            for item in items
        ),
        "orient_deterministic": orient == orient_repeat,
        "interesting_deterministic": interesting == interesting_repeat,
        "query_model_authority_zero": (orient.get("authority_policy") or {}).get("model_state_authority") == "ZERO"
        and (interesting.get("authority_policy") or {}).get("model_state_authority") == "ZERO",
    }

    return {
        "schema": RESULT_SCHEMA,
        "status": "EVALUATED",
        "questions": {
            "what_is_this_place": orient,
            "what_is_interesting_here": interesting,
        },
        "checks": checks,
        "all_pass": all(checks.values()),
        "authority": {
            "location_authority": (handoff.get("authority_policy") or {}).get("location_authority"),
            "canon_source_authority": (handoff.get("authority_policy") or {}).get("canon_source_authority"),
            "sources_merged": (handoff.get("authority_policy") or {}).get("sources_merged"),
            "model_called": False,
            "model_calculation_authority": "ZERO",
            "model_state_authority": "ZERO",
            "model_canon_authority": "ZERO",
            "campaign_mutation": False,
            "canon_mutation": False,
        },
        "interpretation": (
            "Structural PASS establishes deterministic, grounded query packets only. "
            "Whether the resulting Ceres texture is actually legible/interesting remains an empirical human review question."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--state",
        default=str(ROOT / "engineering" / "experience_one" / "fixtures" / "E1_1_CERES_OPERATOR_STATE_2226.json"),
    )
    p.add_argument("--root", required=True)
    p.add_argument("--out")
    p.add_argument("--max-items", type=int, default=3)
    args = p.parse_args()

    state = json.loads(Path(args.state).expanduser().read_text(encoding="utf-8"))
    runtime_root = Path(args.root).expanduser().resolve()
    result = evaluate_legibility(
        state,
        runtime_root / "data" / "LOOM_2226.sqlite3",
        runtime_root / "data" / "LOOM_2226_CIVSTATE.sqlite3",
        max_items=args.max_items,
    )

    print("schema:", result["schema"])
    print("status:", result["status"])
    if result.get("status") == "EVALUATED":
        orient = result["questions"]["what_is_this_place"]
        interesting = result["questions"]["what_is_interesting_here"]
        identity = orient["facts"]["identity"]["value"]
        print("place:", identity.get("name"))
        print("summary:", identity.get("summary"))
        print("political_context:", orient["facts"]["political_context"]["value"])
        print("transport_role:", orient["facts"]["transport_role"]["value"])
        print("interesting_count:", len(interesting.get("items") or []))
        for idx, item in enumerate(interesting.get("items") or [], 1):
            print(
                f"interesting_{idx}: {item.get('entity_id')} | {item.get('name')} | "
                f"role={item.get('role')} | traffic={item.get('traffic_class')} | "
                f"strategic={item.get('strategic_importance')}"
            )
        for name, passed in result["checks"].items():
            print(f"check {name}: {'PASS' if passed else 'FAIL'}")
    else:
        print("handoff_status:", result.get("handoff_status"))
        print("handoff_message:", result.get("handoff_message"))
    print("all_pass:", result["all_pass"])

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("out:", out)
    return 0 if result["all_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
