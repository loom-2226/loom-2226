from __future__ import annotations

"""Loopback-only Experience One HUD server. Navigator alone executes/mutates."""
import argparse, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
SCRIPT_PATH=Path(__file__).resolve(); REPO_ROOT=SCRIPT_PATH.parents[2]
if str(REPO_ROOT) not in sys.path: sys.path.insert(0,str(REPO_ROOT))
from engineering.experience_one.e1_flight_interaction_contract import FlightIntent
from engineering.experience_one.e1_hud_interaction import MaraIntentSession
from engineering.experience_one.e1_hud_presenter import build_hud_payload, render_hud_html
from engineering.experience_one.e1_mara_intent_adapter import OpenAIMaraIntentAdapter
from engineering.experience_one.e1_navigator_review_service import NavigatorReviewService
from engineering.experience_one.e1_navigator_finalization_service import NavigatorFinalizationService
from engineering.experience_one.e1_navigator_execution_service import NavigatorExecutionService
DEFAULT_ROOT=Path("/storage/emulated/0/Download/LOOM_TEST"); DEFAULT_AUDIT=Path("/storage/emulated/0/Download/LOOM_OPENAI_DEV_AUDIT.jsonl")
STATE_FILE="LOOM_STATE_V1.json"; MAX_REQUEST_BYTES=8192

def _read_campaign_state(root):
    p=root/STATE_FILE
    if not p.exists(): raise FileNotFoundError(f"authoritative campaign state not found: {p}")
    v=json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(v,dict): raise ValueError("campaign state must be a JSON object")
    return v

def load_live_hud_payload(root,*,intent=None,review_bundle=None,finalization=None,authorization=None):
    review=None if review_bundle is None else review_bundle.get("review"); details=None if review_bundle is None else review_bundle.get("candidate_display")
    return build_hud_payload(_read_campaign_state(root),intent=intent,review=review,candidate_details=details,finalization=finalization,authorization=authorization)

def build_mara_intent_session(*,api_key,audit_path=DEFAULT_AUDIT,model="gpt-5.6-luna"):
    return MaraIntentSession(OpenAIMaraIntentAdapter(api_key=api_key,audit_path=audit_path,model=model).interpret)

def _execution_ui(html:str, authorization, execution)->str:
    if not isinstance(authorization,dict): return html
    if isinstance(execution,dict):
        block=("<section class='panel execution'><div class='eyebrow'>Navigator execution</div><div class='guard'>EXECUTED · CAMPAIGN STATE MUTATED BY NAVIGATOR</div>"
               f"<div class='value compact'>ARRIVED {execution.get('location_token','—')}</div><div class='small'>State {execution.get('state_id','—')} · Flight {execution.get('flight_id','—')}</div></section>")
    else:
        block=("<section class='panel execution-request'><div class='eyebrow'>Governed execution</div><div class='small'>Navigator will re-run, revalidate current state, reviewed candidates, selected plan and final-plan SHA before any mutation.</div>"
               "<button id='execute-flight' type='button'>EXECUTE AUTHORIZED FLIGHT</button><div class='small status' id='execute-status'></div></section>"
               "<script>const eb=document.getElementById('execute-flight');if(eb)eb.addEventListener('click',async()=>{eb.disabled=true;document.getElementById('execute-status').textContent='Navigator is revalidating and executing…';const r=await fetch('/execute.json',{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});const d=await r.json();if(!r.ok){document.getElementById('execute-status').textContent=d.message||'execution failed';eb.disabled=false;return}location.reload()});</script>")
    return html.replace("<footer>",block+"<footer>",1)

def make_handler(root,intent_session=None,navigator_service=None,finalization_service=None,execution_service=None):
    class Handler(BaseHTTPRequestHandler):
        server_version="LOOM-E1-HUD/0.5"
        def _send(self,status,ctype,body):
            self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(body))); self.send_header("Cache-Control","no-store"); self.send_header("X-LOOM-Authority","PRESENTATION_REQUESTS_NAVIGATOR_EXECUTION_ONLY"); self.end_headers(); self.wfile.write(body)
        def _json(self,status,payload): self._send(status,"application/json; charset=utf-8",json.dumps(payload,indent=2,sort_keys=True).encode())
        def _read(self):
            raw=self.headers.get("Content-Length")
            if raw is None: raise ValueError("Content-Length is required")
            n=int(raw)
            if n<0 or n>MAX_REQUEST_BYTES: raise ValueError("request size is invalid")
            v=json.loads(self.rfile.read(n).decode() or "{}")
            if not isinstance(v,dict): raise ValueError("request must be a JSON object")
            return v
        def do_GET(self):
            try:
                route=urlparse(self.path).path; s=intent_session
                intent=None if s is None else s.current(); review=None if s is None else s.current_review(); final=None if s is None else s.current_finalization(); auth=None if s is None else s.current_authorization(); execution=None if s is None else s.current_execution()
                payload=load_live_hud_payload(root,intent=intent,review_bundle=review,finalization=final,authorization=auth)
                if route in ("/","/index.html"):
                    html=_execution_ui(render_hud_html(payload),auth,execution); self._send(200,"text/html; charset=utf-8",html.encode()); return
                if route=="/state.json": self._json(200,{**payload,"navigator_execution":execution}); return
                self._send(404,"text/plain; charset=utf-8",b"not found\n")
            except Exception as exc: self._json(500,{"status":"ERROR","type":type(exc).__name__,"message":str(exc),"execution_authority":"ZERO"})
        def do_POST(self):
            route=urlparse(self.path).path
            try:
                s=intent_session
                if route=="/intent.json":
                    if s is None: raise RuntimeError("OPENAI_API_KEY is not available to this HUD process")
                    q=self._read(); extras=sorted(set(q)-{"text"})
                    if extras: raise ValueError(f"unsupported intent request fields: {extras}")
                    self._json(200,{"status":"TYPED_INTENT_READY","intent":s.capture(str(q.get('text') or '')),"campaign_mutation":"NONE"}); return
                if route=="/navigator-review.json":
                    if s is None or navigator_service is None: raise RuntimeError("Navigator review unavailable")
                    if self._read(): raise ValueError("Navigator review accepts no browser planning fields")
                    current=s.current()
                    if current is None: raise ValueError("typed Mara intent is required before Navigator review")
                    b=navigator_service.generate(root,FlightIntent.from_mapping(current)); self._json(200,{"status":"NAVIGATOR_REVIEW_READY","review":s.store_review(b),"campaign_mutation":"NONE"}); return
                if route=="/navigator-finalize.json":
                    if s is None or finalization_service is None: raise RuntimeError("Navigator finalization unavailable")
                    q=self._read()
                    if sorted(q)!=["plan_number"]: raise ValueError("finalization requires only plan_number")
                    current=s.current(); review=s.current_review()
                    if current is None or review is None: raise ValueError("typed intent and Navigator review are required")
                    b=finalization_service.finalize(root,FlightIntent.from_mapping(current),review,int(q["plan_number"])); self._json(200,{"status":"NAVIGATOR_FINAL_PLAN_READY","finalization":s.store_finalization(b),"campaign_mutation":"NONE","execution_authority":"ZERO"}); return
                if route=="/authorize.json":
                    if s is None: raise RuntimeError("interaction session unavailable")
                    q=self._read()
                    if sorted(q)!=["authorized"] or q.get("authorized") is not True: raise ValueError("explicit authorized=true is required")
                    self._json(200,{"status":"FLIGHT_AUTHORIZATION_RECORDED","authorization":s.authorize("HUMAN_PIXEL"),"campaign_mutation":"NONE","execution_status":"NOT_REQUESTED"}); return
                if route=="/execute.json":
                    if s is None or execution_service is None: raise RuntimeError("Navigator execution unavailable")
                    if self._read(): raise ValueError("execution accepts no browser planning/state fields")
                    if s.current_execution() is not None: raise ValueError("authorized flight has already been executed in this session")
                    current=s.current(); review=s.current_review(); final=s.current_finalization(); auth=s.current_authorization()
                    if None in (current,review,final,auth): raise ValueError("typed intent, review, finalization and explicit authorization are required")
                    result=execution_service.execute(root,FlightIntent.from_mapping(current),review,final,auth); s.store_execution(result)
                    self._json(200,{"status":"NAVIGATOR_EXECUTION_COMPLETE","execution":result}); return
                self._json(405,{"status":"METHOD_NOT_ALLOWED","execution_authority":"ZERO"})
            except Exception as exc: self._json(400,{"status":"REQUEST_REJECTED","type":type(exc).__name__,"message":str(exc),"execution_authority":"ZERO"})
        def log_message(self,fmt,*args): print("E1 HUD",self.address_string(),fmt%args)
    return Handler

def main():
    p=argparse.ArgumentParser(); p.add_argument("--root",type=Path,default=DEFAULT_ROOT); p.add_argument("--bind",default="127.0.0.1"); p.add_argument("--port",type=int,default=8877); p.add_argument("--audit-path",type=Path,default=DEFAULT_AUDIT); p.add_argument("--model",default="gpt-5.6-luna"); a=p.parse_args()
    if a.bind not in {"127.0.0.1","localhost"}: raise RuntimeError("E1 HUD qualification server is loopback-only")
    campaign=load_live_hud_payload(a.root)["campaign"]; key=os.environ.get("OPENAI_API_KEY","").strip(); session=build_mara_intent_session(api_key=key,audit_path=a.audit_path,model=a.model) if key else None
    print("LOOM E1 HUD             GOVERNED EXECUTION v0.5"); print("CAMPAIGN STATE          ",campaign["state_id"]); print("LOCATION                ",campaign["location_token"]); print("EPOCH                   ",campaign["epoch_utc"]); print("BROWSER AUTHORITY       PRESENTATION + TYPED REQUESTS ONLY"); print("MARA INTENT             ","AUDITED / ENABLED" if session else "DISABLED / OPENAI_API_KEY NOT SET"); print("NAVIGATOR               REVIEW + FINALIZE + REVALIDATE + EXECUTE"); print("CAMPAIGN MUTATION       NAVIGATOR ONLY AFTER EXPLICIT AUTHORIZATION"); print("CALC/STATE/EXEC AUTH    ZERO / ZERO / ZERO (BROWSER + MARA)"); print(f"URL                     http://127.0.0.1:{a.port}/")
    server=ThreadingHTTPServer(("127.0.0.1",a.port),make_handler(a.root,session,NavigatorReviewService(),NavigatorFinalizationService(),NavigatorExecutionService()))
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0
if __name__=="__main__": raise SystemExit(main())
