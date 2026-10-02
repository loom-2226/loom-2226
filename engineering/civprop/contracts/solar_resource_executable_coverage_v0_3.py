"""Audit Solar resource evidence against executable CIVPROP knowledge machinery."""
from __future__ import annotations
import csv, json
from collections import defaultdict
from pathlib import Path

SUPPORTED={"SUPPORTED_PRESENT_UNQUANTIFIED","SUPPORTED_QUANTIFIED","SUPPORTED_INFERRED_OR_MODELLED"}

def audit(coverage_path:Path, mission_path:Path)->dict:
    with coverage_path.open(newline="") as f: rows=list(csv.DictReader(f))
    mission=json.loads(mission_path.read_text())
    executable={(q["location_id"],q["subject_id"]):q for q in mission["questions"]}
    by=defaultdict(list)
    for r in rows: by[r["body_id"]].append(r)
    bodies=[]
    for bid, rs in sorted(by.items()):
        supported=[r for r in rs if r["coverage_disposition"] in SUPPORTED]
        bodies.append({
            "body_id":bid,"canonical_name":rs[0]["canonical_name"],
            "supported_resource_families":len(supported),
            "unknown_after_search":sum(r["coverage_disposition"]=="UNKNOWN_AFTER_SEARCH" for r in rs),
            "evidence_records":sum(bool(r["evidence_records"]) for r in rs),
        })
    moon=next(x for x in bodies if x["body_id"]=="MOON")
    return {
      "format":"CIVPROP_SOLAR_RESOURCE_EXECUTABLE_COVERAGE_AUDIT_V0_3",
      "classification":"NON_CANON_DIAGNOSTIC",
      "resource_lanes":len(rows),
      "supported_lanes":sum(x["supported_resource_families"] for x in bodies),
      "unknown_after_search_lanes":sum(x["unknown_after_search"] for x in bodies),
      "mission_knowledge_questions":len(mission["questions"]),
      "mission_destinations":sorted({m["destination_location_id"] for m in mission["missions"]}),
      "moon":moon,
      "bodies_with_at_least_moon_evidence_coverage":[x for x in bodies if x["supported_resource_families"]>=moon["supported_resource_families"]],
      "diagnosis":"RESOURCE_EVIDENCE_EXISTS_BEYOND_MOON_BUT_GENERIC_SOLAR_EVIDENCE_IS_NOT_EXECUTABLE_MISSION_KNOWLEDGE_V1",
      "firewalls":["UNKNOWN_AFTER_SEARCH_NOT_ZERO","EVIDENCE_PRESENCE_NOT_ABUNDANCE","EVIDENCE_NOT_ECONOMIC_VALUE","NO_GENERIC_PRIOR_INFERENCE"],
    }
