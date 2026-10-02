"""Validated PostgreSQL Timeline -> causal-conductor input V0.3.

Dates create consideration/history-anchor events only.  They never grant actor
capability, installed capacity, access/adoption, service feasibility, migration,
or colonization.  NON-CANON runtime integration / V0.3 UNPROMOTED.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
from typing import Mapping, Sequence

from engineering.civprop.compile_inputs_v1 import TIMELINE_SNAPSHOT_ID

REQUIRED_RULES = {
    "DATE_DOES_NOT_UNLOCK",
    "FOUR_TECH_STATES",
    "SITE_SPECIFIC",
    "UNKNOWN_NOT_ZERO",
    "CANON_COMPARATOR_NOT_DESTINATION",
}


@dataclass(frozen=True)
class TimelineCausalInputV03:
    snapshot_id: str
    snapshot_state: str
    interpretation_rules: tuple[Mapping[str, object], ...]
    milestones: tuple[Mapping[str, object], ...]


def _psql(database: str, query: str):
    p = subprocess.run(
        ["psql", "-X", "-d", database, "-At", "-c",
         "SELECT COALESCE(json_agg(t),'[]'::json)::text FROM (" + query + ") t"],
        check=True, capture_output=True, text=True,
    )
    return json.loads(p.stdout.strip() or "[]")


def load_timeline_causal_input(*, database: str = "loom_dev") -> TimelineCausalInputV03:
    snap = _psql(database,
        "SELECT snapshot_id,state FROM loom_control.snapshot "
        f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}'")
    if len(snap) != 1 or snap[0]["state"] != "VALIDATED":
        raise RuntimeError("TIMELINE_SNAPSHOT_NOT_UNIQUELY_VALIDATED")
    rules = _psql(database,
        "SELECT rule_key,rule_text_md FROM loom_timeline.interpretation_rule "
        f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}' ORDER BY rule_key")
    if {x["rule_key"] for x in rules} != REQUIRED_RULES:
        raise RuntimeError("TIMELINE_INTERPRETATION_RULE_SET_MISMATCH")
    milestones = _psql(database,
        "SELECT milestone_id,family,timeline_kind,authority_class,epistemic_status,"
        "reference_period,start_year,end_year,temporal_precision,capability_change_md,"
        "threshold_gate_md,basis_uncertainty_md,source_section,sort_order,notes_md "
        "FROM loom_timeline.milestone "
        f"WHERE snapshot_id='{TIMELINE_SNAPSHOT_ID}' ORDER BY sort_order,milestone_id")
    if not milestones:
        raise RuntimeError("TIMELINE_MILESTONES_MISSING")
    return TimelineCausalInputV03(
        TIMELINE_SNAPSHOT_ID, snap[0]["state"], tuple(rules), tuple(milestones)
    )


def timeline_seed_events(authority: TimelineCausalInputV03, *,
                         start_year: int, end_year: int) -> tuple[dict, ...]:
    events = []
    for m in authority.milestones:
        year = m.get("start_year")
        if year is None or not (start_year <= int(year) <= end_year):
            continue
        events.append({
            "year": int(year),
            "phase": 5,
            "event_type": "TIMELINE_MILESTONE_REACHED",
            "lane_id": "TIMELINE",
            "provenance_refs": (
                authority.snapshot_id,
                f"loom_timeline.milestone:{m['milestone_id']}",
            ),
            "payload": {
                "milestone_id": m["milestone_id"],
                "family": m["family"],
                "timeline_kind": m["timeline_kind"],
                "authority_class": m["authority_class"],
                "epistemic_status": m["epistemic_status"],
                "temporal_precision": m["temporal_precision"],
                "end_year": m.get("end_year"),
                "capability_change_md": m.get("capability_change_md"),
                "threshold_gate_md": m.get("threshold_gate_md"),
                "frontier_semantics": "CONSIDERATION_OR_HISTORY_ANCHOR_NOT_AUTOMATIC_CAPABILITY",
                "actor_capability_effect": "NONE_WITHOUT_SEPARATE_ACTOR_STATE_EVENT",
                "installed_capacity_effect": "NONE_WITHOUT_SEPARATE_COMMISSIONED_ASSET",
                "actor_access_effect": "NONE_WITHOUT_SEPARATE_ACCESS_ADOPTION_STATE",
                "physical_service_effect": "NONE_WITHOUT_SEPARATE_ENGINEERING_QUALIFICATION",
            },
        })
    return tuple(events)


def timeline_lane(year: int, state: Mapping[str, object], payload: Mapping[str, object]):
    reached = list(state.get("timeline_milestones_reached", ()))
    reached.append({
        "year": year,
        "milestone_id": payload["milestone_id"],
        "authority_class": payload["authority_class"],
        "epistemic_status": payload["epistemic_status"],
        "status": "ANCHOR_REACHED_NO_AUTOMATIC_UNLOCK",
    })
    # Deliberately no actor/capability/capacity/service mutation and no child event.
    return {"timeline_milestones_reached": reached}, ()
