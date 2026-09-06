"""HTTP bridge for GIS flight planning and Phase-6 campaign execution."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse, parse_qs, urlencode
import json, threading, traceback, uuid
from loom.runtime import resolve_runtime_roots
from loom.runtime_diagnostics import collect_runtime_manifest
from loom.runtime_trace import RuntimeTrace
from .flight_planning import GISFlightPlanningError

def _json_bytes(value): return (json.dumps(value,separators=(",",":"),default=str)+"\n").encode("utf-8")
def planning_client_js(): return Path(__file__).with_name("flight_planning.js").read_text(encoding="utf-8")+"\n"+Path(__file__).with_name("flight_planning_selection.js").read_text(encoding="utf-8")
def _canonical_navigation_endpoint(registry_owner,candidates):
    registry=getattr(registry_owner,"CIVSTATE_TOKEN_ENTITY",None)
    if not isinstance(registry,Mapping) or not registry: raise GISFlightPlanningError("Navigator endpoint registry is unavailable")
    token_lookup={}; entity_lookup={}
    for raw_token,raw_entity in registry.items():
        token=str(raw_token or "").strip().upper(); entity_id=str(raw_entity or "").strip().upper()
        if not token: continue
        token_lookup[token]=token
        if entity_id: entity_lookup[entity_id]=token
    for candidate in candidates:
        raw=str(candidate or "").strip()
        if not raw: continue
        key=raw.upper().replace(" ","_")
        if key in token_lookup:return token_lookup[key],raw
        if key in entity_lookup:return entity_lookup[key],raw
    return None,None

def install_flight_planning(gis_module,session):
    handler=gis_module.SolarHandler; handler.flight_planning_session=session; handler.flight_planning_base_overlay_json=bytes(getattr(handler,"navigation_overlay_json",b"{}")); handler.flight_planning_job_lock=threading.Lock(); handler.flight_planning_job={"status":"IDLE","job_id":None,"state":None,"error":None,"trace_id":None}
    runtime_root=Path(getattr(session.context,"runtime_root",None) or Path.cwd()); roots=resolve_runtime_roots(app_root=runtime_root); handler.runtime_trace=RuntimeTrace(roots.campaign_root/"logs"/"loom-trace.jsonl"); handler.active_trace_id=None
    run_stamp=datetime.now().astimezone().strftime("%Y%m%d_%H%M%S"); handler.flight_planning_log_path=runtime_root/f"LOOM_PHASE6_HTTP_{run_stamp}.log"
    try:(runtime_root/"LOOM_PHASE6_LATEST.txt").write_text(f"HTTP_LOG={handler.flight_planning_log_path.name}\nTRACE_LOG={handler.runtime_trace.path}\n",encoding="utf-8")
    except Exception:pass
    old_get=handler.do_GET; old_post=getattr(handler,"do_POST",None)
    def _log(event,**fields):
        row={"utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"event":event,**fields}
        try:
            handler.flight_planning_log_path.parent.mkdir(parents=True,exist_ok=True)
            with handler.flight_planning_log_path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,separators=(",",":"),default=str)+"\n")
        except Exception:pass
    def _trace(event_type,trace_id=None,**fields):
        tid=trace_id or handler.active_trace_id or handler.runtime_trace.new_trace_id("flight"); handler.active_trace_id=tid; handler.runtime_trace.emit(event_type,trace_id=tid,subsystem="gis.flight_planning",**fields); return tid
    _log("flight_planning_installed",log_path=str(handler.flight_planning_log_path),runtime_root=str(runtime_root)); _trace("runtime.installed",runtime_root=str(runtime_root),trace_path=str(handler.runtime_trace.path))
    def _send_json(self,value,status=200):return self._send(status,"application/json; charset=utf-8",_json_bytes(value))
    def _send_state(self,state,status=200):return _send_json(self,state.to_dict(),status=status)
    def _redirect(self,location,status=303):
        body=("redirecting to "+location+"\n").encode(); self.send_response(status); self.send_header("Location",location); self.send_header("Content-Type","text/plain; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(body)
    def _job_snapshot():
        with handler.flight_planning_job_lock:return dict(handler.flight_planning_job)
    def _set_job(**updates):
        with handler.flight_planning_job_lock:handler.flight_planning_job.update(updates); return dict(handler.flight_planning_job)
    def _resolve_destination(entity,trace_id=None):
        if not isinstance(entity,dict):raise GISFlightPlanningError("entity descriptor is required")
        display_name=str(entity.get("display_name") or entity.get("name") or entity.get("entity_id") or "SELECTION").strip(); raw_candidates=[entity.get("navigation_token"),entity.get("route_token"),entity.get("navigator_token"),entity.get("canonical_token"),entity.get("body_token"),entity.get("name"),entity.get("display_name"),entity.get("parent_entity_id") if str(entity.get("entity_class") or "").upper()=="INFRASTRUCTURE" else None,entity.get("entity_id")]; candidates=[]; seen=set()
        for value in raw_candidates:
            text=str(value or "").strip()
            if not text:continue
            for variant in [text,text.upper().replace(" ","_")]:
                if variant and variant not in seen:seen.add(variant); candidates.append(variant)
        token,resolved_from=_canonical_navigation_endpoint(handler.flight_planning_session.service.core,candidates)
        if token is None:_trace("destination.unavailable",trace_id,entity_id=entity.get("entity_id"),display_name=display_name); return {"selectable":False,"route_token":None,"display_name":display_name,"entity_id":entity.get("entity_id"),"reason":"not a Navigator route endpoint","authority":"NAVIGATOR_CIVSTATE_TOKEN_ENTITY"}
        result={"selectable":token!=handler.flight_planning_session.origin,"route_token":token,"display_name":display_name,"entity_id":entity.get("entity_id"),"authority":"NAVIGATOR_CIVSTATE_TOKEN_ENTITY"}
        if result["selectable"]:result["resolved_from"]=resolved_from
        else:result["reason"]="already at this location"
        _trace("destination.resolved",trace_id,entity_id=result.get("entity_id"),route_token=token,selectable=result["selectable"]); return result
    def _run_discovery_job(job_id,destination,priority,trace_id):
        _log("discover_job_start",job_id=job_id,destination=destination,priority=priority,trace_id=trace_id); _trace("discover.started",trace_id,job_id=job_id,destination=destination,priority=priority); session.bind_trace(handler.runtime_trace,trace_id)
        try:
            state=session.discover(destination,priority); _set_job(status="COMPLETE",job_id=job_id,state=state.to_dict(),error=None,trace_id=trace_id); _trace("discover.completed",trace_id,job_id=job_id,destination=destination,candidate_count=len(state.candidates)); _log("discover_job_complete",job_id=job_id,candidates=len(state.candidates),trace_id=trace_id)
        except BaseException as exc:
            detail=str(getattr(exc,"code",None)) if isinstance(exc,SystemExit) else str(exc); message=f"Navigator acquisition exited: {detail}" if isinstance(exc,SystemExit) else f"{type(exc).__name__}: {exc}"; _trace("discover.failed",trace_id,job_id=job_id,destination=destination,error=message); _log("discover_job_error",job_id=job_id,error=message,trace_id=trace_id,traceback=traceback.format_exc()); _set_job(status="ERROR",job_id=job_id,state=None,error=message,trace_id=trace_id)
    def _start_discovery(destination,priority):
        current=_job_snapshot()
        if current.get("status")=="RUNNING":return current,409
        job_id="fp-"+uuid.uuid4().hex[:12]; trace_id=handler.runtime_trace.new_trace_id("flight"); handler.active_trace_id=trace_id; session.bind_trace(handler.runtime_trace,trace_id); _set_job(status="RUNNING",job_id=job_id,state=None,error=None,trace_id=trace_id); _trace("discover.accepted",trace_id,job_id=job_id,destination=destination,priority=priority); _log("discover_accepted",job_id=job_id,destination=destination,priority=priority,trace_id=trace_id); threading.Thread(target=_run_discovery_job,args=(job_id,destination,priority,trace_id),name=f"loom-flight-plan-{job_id}",daemon=True).start(); return _job_snapshot(),202
    def do_GET(self):
        parsed=urlparse(self.path); path=parsed.path
        # Diagnostics is deliberately handled before ordinary HTTP logging/tracing.
        # Reading diagnostics must not create or append any runtime artifact.
        if path=="/diagnostics":
            client=str(self.client_address[0] if self.client_address else "")
            if client not in ("127.0.0.1","::1","localhost"):return _send_json(self,{"error":"diagnostics is localhost-only"},403)
            manifest=collect_runtime_manifest(roots=roots); manifest["live_process"]={"flight_planning":session.state().to_dict(),"job":_job_snapshot(),"http_log":str(handler.flight_planning_log_path),"trace_log":str(handler.runtime_trace.path),"active_trace_id":handler.active_trace_id}; return _send_json(self,manifest)
        _log("http_get",path=path,query=parsed.query)
        if path=="/flight-planning.json":return _send_state(self,session.state())
        if path=="/flight-planning/status.json":return _send_json(self,_job_snapshot())
        if path=="/flight-planning/health.json":return _send_json(self,{"ok":True,"planning":session.state().to_dict(),"job":_job_snapshot(),"log_path":str(handler.flight_planning_log_path),"trace_id":handler.active_trace_id})
        if path in ("/flight-planning/discover.json","/flight-planning/discover-start"):
            q=parse_qs(parsed.query); destination=(q.get("destination") or [""])[0]; priority=(q.get("priority") or ["BALANCED"])[0]
            if not destination:return _redirect(self,"/?fp_error=destination_required") if path.endswith("discover-start") else _send_json(self,{"error":"destination is required"},400)
            state,status=_start_discovery(destination,priority)
            if path=="/flight-planning/discover-start":return _redirect(self,"/?"+urlencode({"fp_job":str(state.get("job_id") or ""),"fp_destination":destination}) if status==202 else "/?"+urlencode({"fp_job":str(state.get("job_id") or ""),"fp_busy":"1"}))
            return _send_json(self,state,status)
        return old_get(self)
    def do_POST(self):
        path=urlparse(self.path).path
        if not path.startswith("/flight-planning/"):
            if callable(old_post):return old_post(self)
            return self._send(404,"text/plain; charset=utf-8",b"not found")
        trace_id=str(self.headers.get("X-LOOM-Trace-ID") or handler.active_trace_id or handler.runtime_trace.new_trace_id("flight")); handler.active_trace_id=trace_id; session.bind_trace(handler.runtime_trace,trace_id); _trace("http.request",trace_id,method="POST",path=path)
        try:
            n=int(self.headers.get("Content-Length") or 0); raw=self.rfile.read(n) if n>0 else b"{}"; body=json.loads(raw.decode() or "{}")
            if not isinstance(body,dict):raise GISFlightPlanningError("request body must be a JSON object")
            if path=="/flight-planning/resolve":return _send_json(self,_resolve_destination(body.get("entity"),trace_id))
            if path=="/flight-planning/discover":state=session.discover(body.get("destination"),body.get("priority") or "BALANCED")
            elif path=="/flight-planning/preview":state=session.preview(body.get("route_id")); handler.navigation_overlay_json=_json_bytes(state.preview_overlay) if state.preview_overlay is not None else handler.navigation_overlay_json
            elif path=="/flight-planning/commit":state=session.commit(body.get("route_id")); handler.navigation_overlay_json=_json_bytes(state.preview_overlay) if state.preview_overlay is not None else handler.navigation_overlay_json
            elif path=="/flight-planning/execute":state=session.execute(); hist=((state.last_execution or {}).get("historical_overlay") if state.last_execution else None); handler.navigation_overlay_json=_json_bytes(hist) if hist else handler.flight_planning_base_overlay_json
            elif path=="/flight-planning/cancel":state=session.cancel(); handler.navigation_overlay_json=handler.flight_planning_base_overlay_json
            else:return _send_json(self,{"error":"unknown flight-planning endpoint"},404)
            action=path.rsplit("/",1)[-1]; state_dict=state.to_dict(); _trace(f"planning.{action}.completed",trace_id,route_id=body.get("route_id"),destination=body.get("destination"),state=state_dict); _log("planning_action_complete",path=path,trace_id=trace_id,state=state_dict); return _send_state(self,state)
        except (GISFlightPlanningError,ValueError,KeyError,RuntimeError) as exc:
            _trace("planning.failed",trace_id,path=path,error=f"{type(exc).__name__}: {exc}"); _log("planning_action_error",path=path,trace_id=trace_id,error=f"{type(exc).__name__}: {exc}",traceback=traceback.format_exc()); return _send_json(self,{"error":f"{type(exc).__name__}: {exc}"},400)
    handler.do_GET=do_GET; handler.do_POST=do_POST
    marker="/* LOOM_PHASE5_FLIGHT_PLANNING */\n/* LOOM_PHASE6_CAMPAIGN_EXECUTION */"
    if "LOOM_PHASE5_FLIGHT_PLANNING" not in gis_module.CLIENT_JS:gis_module.CLIENT_JS+="\n"+marker+"\n"+planning_client_js()+"\n"
