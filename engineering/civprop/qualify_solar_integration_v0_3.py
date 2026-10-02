"""Hostile pre-GAP-014 qualification for CIVPROP Solar integration V0.3."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
from engineering.civprop.contracts.solar_object_location_bridge_v0_3 import build_solar_candidate_locations
from engineering.civprop.contracts.timeline_technology_bridge_v0_3 import build_timeline_technology_bridge
from engineering.civprop.contracts.solar_mission_opportunity_bridge_v0_3 import build_solar_mission_opportunity_catalog
from engineering.civprop.contracts.solar_transport_actor_access_v0_3 import PROPULSION_REGIMES

ROOT=Path(__file__).resolve().parents[2]
NAV=ROOT/"reports/solar_civprop/NAV_READINESS_V1.json"
M4B=ROOT/"dev/solar_civprop_m4b/reports/M4B_COVERAGE_MATRIX.csv"
TIMELINE=ROOT/"docs/architecture/LOOM_TECHNOLOGY_TIMELINE_REGISTER_v0.1.md"
GAPS=ROOT/"engineering/civprop/gap_register_v1.json"

def qualify():
 loc=build_solar_candidate_locations(NAV)
 tech=build_timeline_technology_bridge(TIMELINE,"timeline-v0-1-0232bf23494f-20260925")
 mis=build_solar_mission_opportunity_catalog(NAV,M4B)
 gaps=json.loads(GAPS.read_text())
 gs={x["gap_id"]:x.get("current_status",x.get("closure_status",x.get("status"))) for x in gaps["gaps"]}
 checks={
  "SOLAR_LOCATIONS_EXPANDED":len(loc["locations"])==187,
  "M4B_ALL_LANES_DISPOSITIONED":len(mis["questions"])==380,
  "UNKNOWN_NOT_ZERO":sum(x["knowledge_state"]=="UNRESOLVED_AFTER_SEARCH" for x in mis["questions"])==343,
  "MISSION_NOT_FACILITY":all(x["facility_materialization"]=="FORBIDDEN" for x in mis["mission_opportunities"]),
  "RESOURCE_PRESENCE_NOT_ECONOMIC_RESOURCE":all(x["economic_claim_status"]=="NONE" for x in mis["mission_opportunities"]),
  "GENERIC_PRIORS_NOT_INVENTED":all(x["prior_probability"] is None for x in mis["questions"]),
  "NAV_FAILURE_PRESERVES_OBJECT":loc["semantics"]["nav1_failure_preserves_body"],
  "DATE_DOES_NOT_UNLOCK":tech["semantics"]["date_does_not_unlock"],
  "CANON_COMPARATOR_EXCLUDED":tech["semantics"]["canon_comparator_excluded"],
  "ADVANCED_PROPULSION_SOLVER_GATED":all(PROPULSION_REGIMES[x]["performance_model_status"]=="NOT_IMPLEMENTED" for x in ("NUCLEAR_ELECTRIC","FUSION_TORCH","METRIC_VESSEL")),
  "GAP014_STILL_OPEN":gs.get("GAP-014")=="OPEN",
  "GAP015_STILL_OPEN":gs.get("GAP-015")=="OPEN",
  "GAPS001_013_STILL_CLOSED":all(gs.get(f"GAP-{i:03d}")=="CLOSED" for i in range(1,14)),
 }
 hard=all(checks.values())
 blockers=[
  "FULL_SOLAR_TRANSPORT_SURFACE_NOT_PRECOMPUTED_OR_BOUND_TO_HYBRID",
  "GENERAL_SOLAR_MISSION_ARCHETYPES_NOT_YET_COMPILED_INTO_MISSION_KNOWLEDGE_V1",
  "GENERIC_SOLAR_OBSERVATION_MODELS_AND_PRIORS_NOT_AUTHORIZED",
  "ADVANCED_PROPULSION_PERFORMANCE_SOLVERS_NOT_IMPLEMENTED",
 ]
 return {
  "format":"CIVPROP_SOLAR_INTEGRATION_V0_3_HOSTILE_QUALIFICATION",
  "classification":"NON_CANON_PRE_GAP14_ENGINEERING_QUALIFICATION",
  "verdict":"PASS_WITH_BLOCKERS" if hard else "FAIL",
  "checks":checks,
  "counts":{
   "candidate_locations":len(loc["locations"]),
   "knowledge_questions":len(mis["questions"]),
   "candidate_mission_opportunities":mis["counts"]["candidate"],
   "blocked_or_unknown_mission_opportunities":mis["counts"]["blocked_or_unknown"],
   "unknown_after_search_questions":sum(x["knowledge_state"]=="UNRESOLVED_AFTER_SEARCH" for x in mis["questions"]),
   "technology_frontier_anchors":len(tech["technology_frontier"])},
  "blockers_before_full_solar_reference_run":blockers,
  "ready_now":{
   "solar_candidate_universe":True,
   "geometry_transport_kernel":True,
   "actor_transport_screening_boundary":True,
   "resource_evidence_to_question_bridge":True,
   "full_hybrid_solar_run":False},
  "next_action":"BUILD_BOUND_TRANSPORT_CACHE_AND_COMPILE_GATED_SOLAR_MISSIONS_INTO_TEMPORARY_V0_3_BUNDLE_THEN_RUN_HOSTILE_SEED42",
 }
if __name__=="__main__":
 print(json.dumps(qualify(),indent=2,sort_keys=True))
