"""Solar evidence -> bounded Mission/Knowledge opportunity bridge V0.3.

Consumes qualified NAV readiness plus the qualified M4-B candidate evidence layer.
It generates *questions and candidate mission opportunities*, never destinations,
resource inventories, economic resources, projects, facilities, or commitments.
"""
from __future__ import annotations
import csv, json
from pathlib import Path
from typing import Any, Mapping

VERSION="0.3.0"
SUPPORTED={"SUPPORTED_PRESENT_UNQUANTIFIED","SUPPORTED_QUANTIFIED","SUPPORTED_INFERRED_OR_MODELLED"}
DIRECT={"SUPPORTED_PRESENT_UNQUANTIFIED","SUPPORTED_QUANTIFIED"}
FAMILIES=("VOLATILES","METALS","SILICATES_ROCK","CARBONACEOUS_ORGANICS")

def _mission_class(body_class:str, nav1:bool)->tuple[str,str]:
    # Surface prospecting needs a later surface-operations gate. V0.3 deliberately
    # stops at remote/rendezvous reconnaissance for the general Solar bridge.
    if body_class in {"ASTEROID","NEAR_EARTH_ASTEROID","COMET","TRANS_NEPTUNIAN_OBJECT","INTERSTELLAR_OBJECT"}:
        return ("ROBOTIC_RESOURCE_RECONNAISSANCE","RENDEZVOUS_OR_FLYBY_RECON")
    return ("ROBOTIC_RESOURCE_RECONNAISSANCE","ORBITAL_OR_FLYBY_RECON")

def build_solar_mission_opportunity_catalog(nav_path:Path, coverage_path:Path,
                                            transport_assessments:Mapping[tuple[str,str],Any]|None=None)->dict:
    nav=json.loads(nav_path.read_text())
    bodies={x["body_id"]:x for x in nav["bodies"]}
    with coverage_path.open(newline="") as f: rows=list(csv.DictReader(f))
    lanes=[]; questions=[]; missions=[]
    for row in sorted(rows,key=lambda x:(x["body_id"],x["resource_family"])):
        bid=row["body_id"]; fam=row["resource_family"]; b=bodies.get(bid)
        if b is None: continue
        # Earth evidence remains part of the qualified evidence matrix, but Earth is
        # not an extraterrestrial Solar reconnaissance destination. Earth has its
        # own CIVPROP baseline/resource machinery and must not generate missions here.
        if bid == "EARTH":
            continue
        disp=row["coverage_disposition"]; nav1=b["nav1"]=="SUPPORTED"
        transport=(transport_assessments or {}).get((bid,fam))
        transport_status=getattr(transport,"status",None) if transport is not None else "NOT_EVALUATED"
        # Unknown-after-search is itself a legitimate unresolved knowledge state.
        if disp=="UNKNOWN_AFTER_SEARCH":
            knowledge_state="UNRESOLVED_AFTER_SEARCH"
        elif disp in DIRECT:
            knowledge_state="EVIDENCE_PRESENT_SCOPE_LIMITED"
        elif disp=="SUPPORTED_INFERRED_OR_MODELLED":
            knowledge_state="INFERRED_OR_MODELLED_SCOPE_LIMITED"
        else:
            knowledge_state="UNRESOLVED"
        qid=f"{bid}_{fam}_CHARACTERIZATION"
        questions.append({
          "question_id":qid,"body_id":bid,"resource_family":fam,
          "question_kind":"RESOURCE_CHARACTERIZATION","knowledge_state":knowledge_state,
          "coverage_disposition":disp,"evidence_records":[x for x in row["evidence_records"].split(";") if x],
          "prior_probability":None,"prior_status":"NOT_AUTHORIZED_FOR_GENERIC_SOLAR_V03",
          "provenance_refs":["M4B_COVERAGE_MATRIX","SOLAR_MISSION_OPPORTUNITY_BRIDGE_V0_3"]})
        reason=[]
        if not nav1: reason.append("NAV1_UNSUPPORTED_AT_ASSESSMENT_EPOCH")
        if transport_status not in ("NOT_EVALUATED","SCREENABLE_GEOMETRY_AND_ACTOR_ACCESS"):
            reason.append("TRANSPORT_NOT_SCREENABLE_FOR_ACTOR")
        mission_status="CANDIDATE_KNOWLEDGE_OPPORTUNITY" if not reason else "BLOCKED_OR_UNKNOWN"
        mclass,service=_mission_class(b["body_class"],nav1)
        missions.append({
          "opportunity_id":f"SOLAR_RECON::{bid}::{fam}","action_kind":"MISSION",
          "mission_class":mclass,"service_class":service,"target_question_id":qid,
          "destination_body_id":bid,"resource_family":fam,"nav1_status":b["nav1"],
          "transport_status":transport_status,"status":mission_status,
          "limiting_constraints":reason,
          "economic_claim_status":"NONE",
          "resource_inventory_status":"UNKNOWN_UNLESS_SEPARATELY_QUANTIFIED_AND_SCOPED",
          "facility_materialization":"FORBIDDEN",
          "provenance_refs":["NAV_READINESS_V1","M4B_QUALIFIED_CANDIDATE_EVIDENCE","SOLAR_MISSION_OPPORTUNITY_BRIDGE_V0_3"]})
        lanes.append((bid,fam,disp,mission_status))
    return {
      "format":"CIVPROP_SOLAR_MISSION_OPPORTUNITY_CATALOG_V0_3","version":VERSION,
      "status":"NON_CANON_MACHINERY_TEST_INPUT",
      "semantics":{
       "mission_not_project_not_facility":True,
       "unknown_after_search_not_zero":True,
       "resource_presence_not_abundance":True,
       "resource_presence_not_economic_resource":True,
       "inferred_or_modelled_not_measured":True,
       "timeline_not_actor_access":True,
       "nav_failure_not_nonexistence":True,
       "generic_prior_probabilities_authorized":False,
       "surface_prospecting_generalization_authorized":False},
      "questions":questions,"mission_opportunities":missions,
      "counts":{"questions":len(questions),"mission_opportunities":len(missions),
                "candidate":sum(x[3]=="CANDIDATE_KNOWLEDGE_OPPORTUNITY" for x in lanes),
                "blocked_or_unknown":sum(x[3]!="CANDIDATE_KNOWLEDGE_OPPORTUNITY" for x in lanes)}
    }
