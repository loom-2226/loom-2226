"""GIS flight planning and Phase-6 campaign execution orchestration.

GIS owns interaction and comparison. Navigator remains sole authority for route
planning and flight calculations. Campaign services remain sole persistence
authority. A planning COMMIT locks a choice; EXECUTE performs the separate,
explicit campaign transition.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping
import copy, hashlib, json
from loom.navigation import NavigationContext, NavigationRequest, RouteCandidate
from loom.navigation.trajectory_payload import find_sequence_b_payload, promote_sequence_b_payload, sequence_b_payload_probe
from loom.navigation.live_gravity_compare import compare_live_route_trajectory
from loom.navigation.live_gravity_guidance_compare import compare_live_route_guidance
from loom.navigation.engineering_feasibility_shadow import evaluate_engineering_feasibility_shadow
from loom.campaign.shadow_ledger import CampaignShadowLedger
from loom.runtime import resolve_runtime_roots
from .navigation_overlay import build_navigation_overlay
GIS_FLIGHT_PLANNING_VERSION="LOOM_GIS_FLIGHT_PLANNING_V1"
class GISFlightPlanningError(RuntimeError):pass
def _stable_json(value):return json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()
def _first(payload,*keys):
    for key in keys:
        if key in payload and payload[key] is not None:return payload[key]
def _minutes(source):
    direct=_first(source,"total_minutes","duration_minutes","elapsed_minutes","flight_minutes")
    if direct is not None:return direct
    seconds=_first(source,"total_s","duration_s","elapsed_s","flight_s")
    if seconds is None:return None
    try:return float(seconds)/60.0
    except (TypeError,ValueError):return None
def _candidate_summary(candidate):
    p=dict(candidate.payload); leg=p.get("leg") if isinstance(p.get("leg"),Mapping) else {}; source=dict(p)
    for k,v in dict(leg).items():source.setdefault(k,v)
    return {"route_id":candidate.route_id,"origin":candidate.origin,"destination":candidate.destination,"departure_epoch":candidate.departure_epoch,"arrival_epoch":candidate.arrival_epoch,"strategy":candidate.strategy,"duration_minutes":_minutes(source),"remass_t":_first(source,"stage_remass_t","remass_t","remass_used_t","total_remass_t"),"holonomy":_first(source,"holonomy","H","holonomy_cost"),"confidence":_first(source,"confidence","C_M","mission_confidence"),"metric_mode":_first(source,"metric","metric_mode"),"torch_mode":_first(source,"torch","torch_mode"),"thermal_posture":_first(source,"thermal","thermal_posture"),"arrival_remass_t":_first(source,"arrival_remass_t","final_remass_t"),"selectable":bool(source.get("selectable",True))}
@dataclass(frozen=True)
class GISPlanningCandidateV1:
    route_id:str; summary:Mapping[str,Any]; source_payload:Mapping[str,Any]=field(default_factory=dict)
    def to_dict(self):return asdict(self)
@dataclass(frozen=True)
class GISPlanningStateV1:
    session_id:str; origin:str; destination:str|None; priority:str; candidates:tuple[GISPlanningCandidateV1,...]=(); preview_route_id:str|None=None; committed_route_id:str|None=None; preview_overlay:Mapping[str,Any]|None=None; gravity_shadow_report:Mapping[str,Any]|None=None; gravity_guidance_shadow_report:Mapping[str,Any]|None=None; gravity_engineering_feasibility_report:Mapping[str,Any]|None=None; campaign_state_sha256:str|None=None; execution_available:bool=False; last_execution:Mapping[str,Any]|None=None; contract:str=GIS_FLIGHT_PLANNING_VERSION
    def to_dict(self):return asdict(self)
class GISFlightPlanningSession:
    def __init__(self,navigation_service,context,*,offline=False,campaign_execution_service=None):self.service=navigation_service; self.campaign_execution_service=campaign_execution_service; self.offline=bool(offline); self.last_execution=None; self.trace=None; self.trace_id=None; self._bind_context(context)
    def bind_trace(self,trace,trace_id):self.trace=trace; self.trace_id=trace_id
    def _emit(self,event_type,**fields):
        if self.trace is not None and self.trace_id:self.trace.emit(event_type,trace_id=self.trace_id,subsystem="gis.flight_planning.session",session_id=self.session_id,**fields)
    def _bind_context(self,context):
        self.context=context; self._campaign_before=copy.deepcopy(dict(context.campaign_state)); origin=str(self._campaign_before.get("location_token") or "").strip()
        if not origin:raise GISFlightPlanningError("campaign state has no location_token")
        self.origin=origin; self.destination=None; self.priority="BALANCED"; self._request=None; self._candidates={}; self._plans={}; self.preview_route_id=None; self.committed_route_id=None; self.preview_overlay=None; self.gravity_shadow_report=None; self.gravity_guidance_shadow_report=None; self.gravity_engineering_feasibility_report=None; seed={"state":self._campaign_before.get("state_id"),"revision":self._campaign_before.get("revision"),"origin":origin}; self.session_id="plan-"+hashlib.sha256(_stable_json(seed)).hexdigest()[:16]; self.campaign_state_sha256=hashlib.sha256(_stable_json(self._campaign_before)).hexdigest()
    def _assert_read_only(self):
        if dict(self.context.campaign_state)!=self._campaign_before:raise GISFlightPlanningError("planning mutated canonical campaign state")
    def state(self):return GISPlanningStateV1(session_id=self.session_id,origin=self.origin,destination=self.destination,priority=self.priority,candidates=tuple(GISPlanningCandidateV1(c.route_id,_candidate_summary(c),dict(c.payload)) for c in self._candidates.values()),preview_route_id=self.preview_route_id,committed_route_id=self.committed_route_id,preview_overlay=self.preview_overlay,gravity_shadow_report=self.gravity_shadow_report,gravity_guidance_shadow_report=self.gravity_guidance_shadow_report,gravity_engineering_feasibility_report=self.gravity_engineering_feasibility_report,campaign_state_sha256=self.campaign_state_sha256,execution_available=self.campaign_execution_service is not None,last_execution=self.last_execution)
    def discover(self,destination,priority="BALANCED"):
        destination=str(destination or "").strip()
        if not destination:raise GISFlightPlanningError("destination is required")
        if destination==self.origin:raise GISFlightPlanningError("destination must differ from origin")
        self.destination=destination; self.priority=str(priority or "BALANCED").upper(); self._request=NavigationRequest(origin=self.origin,destination=destination,priority=self.priority); self.context=self.service.prepare_context(self._request,self.context,offline=self.offline,refresh=False); rows=self.service.discover_routes(self._request,self.context); self._candidates={c.route_id:c for c in rows}; self._plans.clear(); self.preview_route_id=None; self.committed_route_id=None; self.preview_overlay=None; self.gravity_shadow_report=None; self.gravity_guidance_shadow_report=None; self.gravity_engineering_feasibility_report=None; self.last_execution=None; self._assert_read_only(); return self.state()
    def preview(self,route_id):
        if self._request is None:raise GISFlightPlanningError("discover routes before preview")
        candidate=self._candidates.get(str(route_id))
        if candidate is None:raise GISFlightPlanningError(f"unknown route_id: {route_id}")
        if not _candidate_summary(candidate)["selectable"]:raise GISFlightPlanningError(f"route is not selectable: {route_id}")
        plan=self._plans.get(candidate.route_id)
        if plan is None:
            plan=self.service.compile_flight(self._request,candidate,self.context); plan=promote_sequence_b_payload(plan)
            if find_sequence_b_payload(plan.payload) is None:
                print("NAV TRAJECTORY  Sequence-B payload absent after live determinism gate")
                for row in sequence_b_payload_probe(plan.payload):print("NAV PAYLOAD     ",row)
            else:print("NAV TRAJECTORY  Sequence-B payload available")
            self._plans[candidate.route_id]=plan
        layer=self.service.get_route_layer(plan,self.context); self.preview_route_id=candidate.route_id; self.preview_overlay=build_navigation_overlay(layer).to_dict(); self.gravity_shadow_report=None; self.gravity_guidance_shadow_report=None; self.gravity_engineering_feasibility_report=None
        active=(self.preview_overlay or {}).get("active_route") or {}; trajectory=active.get("trajectory") if isinstance(active,Mapping) else None
        if isinstance(trajectory,Mapping):
            roots=resolve_runtime_roots(app_root=getattr(self.context,"runtime_root",None)); db_path=roots.data_root/"LOOM_2226.sqlite3"
            try:
                self.gravity_shadow_report=compare_live_route_trajectory(trajectory,db_path)
                self._emit("navigator.gravity_shadow.completed",route_id=candidate.route_id,terminal_position_error_km=((self.gravity_shadow_report.get("report") or {}).get("terminal_position_error_km")),terminal_velocity_error_km_s=((self.gravity_shadow_report.get("report") or {}).get("terminal_velocity_error_km_s")))
            except Exception as exc:
                self.gravity_shadow_report={"contract":"LOOM_NAV_PHYSICS_V2_LIVE_GRAVITY_COMPARE_V1","authority":"DIAGNOSTIC_SHADOW_ONLY_NOT_ROUTE_AUTHORITY","status":"ERROR","error":f"{type(exc).__name__}: {exc}"}; self._emit("navigator.gravity_shadow.failed",route_id=candidate.route_id,error=self.gravity_shadow_report["error"])
            try:
                self.gravity_guidance_shadow_report=compare_live_route_guidance(trajectory,db_path)
                self._emit("navigator.gravity_guidance_shadow.completed",route_id=candidate.route_id,terminal_position_error_km=((self.gravity_guidance_shadow_report.get("report") or {}).get("terminal_position_error_km")),terminal_velocity_error_km_s=((self.gravity_guidance_shadow_report.get("report") or {}).get("terminal_velocity_error_km_s")),guidance_correction_delta_v_km_s=((self.gravity_guidance_shadow_report.get("report") or {}).get("guidance_correction_delta_v_km_s")))
            except Exception as exc:
                self.gravity_guidance_shadow_report={"contract":"LOOM_NAV_PHYSICS_V2_D2H_LIVE_GRAVITY_GUIDANCE_COMPARE_V1","authority":"DIAGNOSTIC_GUIDANCE_SHADOW_ONLY_NOT_ROUTE_AUTHORITY","status":"ERROR","error":f"{type(exc).__name__}: {exc}"}; self._emit("navigator.gravity_guidance_shadow.failed",route_id=candidate.route_id,error=self.gravity_guidance_shadow_report["error"])
            if isinstance(self.gravity_guidance_shadow_report,Mapping) and isinstance(self.gravity_guidance_shadow_report.get("report"),Mapping):
                try:
                    self.gravity_engineering_feasibility_report=evaluate_engineering_feasibility_shadow(trajectory,dict(candidate.payload),self.gravity_guidance_shadow_report)
                    self._emit("navigator.gravity_engineering_shadow.completed",route_id=candidate.route_id,status=self.gravity_engineering_feasibility_report.get("status"),minimum_thrust_margin_km_s2=self.gravity_engineering_feasibility_report.get("minimum_sampled_thrust_accel_margin_km_s2"),estimated_remass_delta_t=self.gravity_engineering_feasibility_report.get("estimated_remass_delta_t_over_qualified_interval"))
                except Exception as exc:
                    self.gravity_engineering_feasibility_report={"contract":"LOOM_NAV_PHYSICS_V2_D2I_ENGINEERING_FEASIBILITY_SHADOW_V1","authority":"DIAGNOSTIC_ENGINEERING_SHADOW_ONLY_NOT_ROUTE_AUTHORITY","status":"ERROR","error":f"{type(exc).__name__}: {exc}"}; self._emit("navigator.gravity_engineering_shadow.failed",route_id=candidate.route_id,error=self.gravity_engineering_feasibility_report["error"])
        self._assert_read_only(); return self.state()
    def commit(self,route_id=None):
        selected=str(route_id or self.preview_route_id or "")
        if not selected or selected not in self._candidates:raise GISFlightPlanningError("preview/select a valid route before commit")
        if self.preview_route_id!=selected:self.preview(selected)
        self.committed_route_id=selected; self._assert_read_only(); return self.state()
    def execute(self):
        if self.campaign_execution_service is None:raise GISFlightPlanningError("campaign execution is unavailable in this runtime")
        plan=self.committed_plan()
        if plan is None or self.committed_route_id is None:raise GISFlightPlanningError("commit a route before execute")
        self._emit("navigator.execute.started",flight_id=plan.flight_id,route_id=self.committed_route_id,origin=self.origin,destination=self.destination,campaign_revision=self._campaign_before.get("revision"),campaign_state_sha256=self.campaign_state_sha256)
        execution=self.service.execute_flight(plan,self.context); self._emit("navigator.arrival.computed",flight_id=plan.flight_id,status=execution.status,state_after_id=dict(execution.final_state).get("state_id"),revision_after=dict(execution.final_state).get("revision"),arrival_epoch_utc=dict(execution.final_state).get("epoch_utc")); layer=self.service.get_route_layer(plan,self.context); self._emit("campaign.commit.started",flight_id=plan.flight_id,state_before_id=self._campaign_before.get("state_id"),revision_before=self._campaign_before.get("revision")); committed=self.campaign_execution_service.commit_flight(plan,execution,self.context); self._emit("campaign.commit.completed",flight_id=plan.flight_id,state_before_id=committed.state_before_id,state_after_id=committed.state_after_id,revision_before=committed.revision_before,revision_after=committed.revision_after,history_record_number=committed.history_record_number,history_record_sha256=committed.history_record_sha256,state_path=committed.state_path,history_path=committed.history_path)
        try:
            roots=resolve_runtime_roots(); shadow=CampaignShadowLedger(roots.campaign_root); shadow.mirror_commit(committed); reconciliation=shadow.reconcile_commit(committed); self._emit("campaign.shadow_sql.mirrored",flight_id=plan.flight_id,db_path=str(shadow.path),reconciliation=reconciliation)
        except Exception as exc:
            reconciliation={"status":"ERROR","match":False,"error":f"{type(exc).__name__}: {exc}"}; self._emit("campaign.shadow_sql.failed",flight_id=plan.flight_id,error=reconciliation["error"])
        history_overlay=build_navigation_overlay(historical_routes=(layer,),current_vehicle_state=committed.final_state).to_dict(); summary=committed.to_dict(); summary["navigation_status"]=execution.status; summary["historical_overlay"]=history_overlay; summary["shadow_sql"]=reconciliation; new_context=NavigationContext(campaign_state=copy.deepcopy(dict(committed.final_state)),acquisition=None,cache_dir=self.context.cache_dir,b1_package=self.context.b1_package,runtime_root=self.context.runtime_root,payload=self.context.payload); self._bind_context(new_context); self.last_execution=summary; self._emit("campaign.rebound",flight_id=plan.flight_id,state_after_id=committed.state_after_id,revision_after=committed.revision_after,location_token=committed.destination); return self.state()
    def cancel(self):self.destination=None; self.priority="BALANCED"; self._request=None; self._candidates.clear(); self._plans.clear(); self.preview_route_id=None; self.committed_route_id=None; self.preview_overlay=None; self.gravity_shadow_report=None; self.gravity_guidance_shadow_report=None; self.gravity_engineering_feasibility_report=None; self._assert_read_only(); return self.state()
    def committed_plan(self):return self._plans.get(self.committed_route_id) if self.committed_route_id else None
