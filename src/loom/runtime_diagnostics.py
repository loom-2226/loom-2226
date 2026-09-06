"""Read-only runtime diagnostics for LOOM.

The collector reports what exists and what the runtime resolved. It does not create,
move, delete, repair, or otherwise mutate runtime data.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,platform,sqlite3,subprocess,sys
from loom.runtime import resolve_runtime_roots
CONTRACT="LOOM_RUNTIME_DIAGNOSTICS_V1"
def _sha256(path):
    if not path.is_file():return None
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def _file_identity(path):
    exists=path.exists(); return {"path":str(path),"exists":exists,"is_file":path.is_file(),"size_bytes":path.stat().st_size if path.is_file() else None,"sha256":_sha256(path)}
def _git_head(app_root):
    try:proc=subprocess.run(["git","-C",str(app_root),"rev-parse","HEAD"],capture_output=True,text=True,timeout=2,check=False)
    except (OSError,subprocess.SubprocessError):return None
    value=proc.stdout.strip(); return value if proc.returncode==0 and value else None
def _install_identity(app_root):
    path=app_root/".loom_install_state.json"; item=_file_identity(path); item.update(release_id=None,release_state=None,source_ref=None,recorded_app_root=None,recorded_data_root=None,error=None)
    if not path.is_file():return item
    try:
        raw=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw,dict):raise ValueError("install state is not a JSON object")
        item.update(release_id=raw.get("release_id"),release_state=raw.get("release_state"),source_ref=raw.get("source_ref"),recorded_app_root=raw.get("app_root"),recorded_data_root=raw.get("data_root"))
    except (OSError,UnicodeError,json.JSONDecodeError,ValueError) as exc:item["error"]=f"{type(exc).__name__}: {exc}"
    return item
def _campaign_state_identity(path):
    item=_file_identity(path); item.update(revision=None,state_id=None,error=None)
    if not path.is_file():return item
    try:
        raw=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw,dict):raise ValueError("campaign state is not a JSON object")
        item["revision"]=raw.get("revision"); item["state_id"]=raw.get("state_id") or raw.get("id")
    except (OSError,UnicodeError,json.JSONDecodeError,ValueError) as exc:item["error"]=f"{type(exc).__name__}: {exc}"
    return item
def _shadow_sql_identity(path):
    item=_file_identity(path); item.update(contract=None,flight_commit_count=None,min_revision=None,max_revision=None,integrity_check=None,error=None)
    if not path.is_file():return item
    try:
        uri=path.resolve().as_uri()+"?mode=ro"
        with sqlite3.connect(uri,uri=True) as conn:
            meta=conn.execute("SELECT value FROM campaign_shadow_meta WHERE key='contract'").fetchone(); counts=conn.execute("SELECT COUNT(*),MIN(revision_after),MAX(revision_after) FROM campaign_flight_commits").fetchone(); integrity=conn.execute("PRAGMA integrity_check").fetchone()
        item.update(contract=meta[0] if meta else None,flight_commit_count=int(counts[0]),min_revision=counts[1],max_revision=counts[2],integrity_check=integrity[0] if integrity else None)
    except (sqlite3.Error,OSError,ValueError) as exc:item["error"]=f"{type(exc).__name__}: {exc}"
    return item
def collect_runtime_manifest(*,roots=None):
    roots=roots or resolve_runtime_roots(); app,data,campaign=roots.app_root,roots.data_root,roots.campaign_root; db_names=("LOOM_2226.sqlite3","LOOM_2226_media.sqlite3","LOOM_2226_CIVSTATE.sqlite3"); databases=[]; seen=set()
    for root_name,root in (("data_root",data),("app_data",app/"data")):
        for name in db_names:
            path=root/name
            if str(path) in seen:continue
            seen.add(str(path)); item=_file_identity(path); item.update(root=root_name,name=name); databases.append(item)
    campaign_state=_campaign_state_identity(campaign/"LOOM_STATE_V1.json")
    if not campaign_state["exists"] and campaign!=app:campaign_state=_campaign_state_identity(app/"LOOM_STATE_V1.json"); campaign_state["compatibility_fallback"]=True
    history_path=campaign/"LOOM_CAMPAIGN_HISTORY.jsonl.gz"; campaign_history=_file_identity(history_path)
    if not campaign_history["exists"] and campaign!=app:campaign_history=_file_identity(app/"LOOM_CAMPAIGN_HISTORY.jsonl.gz"); campaign_history["compatibility_fallback"]=True
    trace_path=campaign/"logs"/"loom-trace.jsonl"; shadow_path=campaign/"LOOM_CAMPAIGN_DEV.sqlite3"; cache_path=app/"LOOM_Navigator_Cache_v1"
    return {"contract":CONTRACT,"runtime":{"platform":platform.platform(),"python":sys.version.split()[0],"executable":sys.executable,"cwd":str(Path.cwd().resolve())},"deployment":{"install_state":_install_identity(app),"app_git_head":_git_head(app)},"roots":roots.to_dict(),"environment":{key:os.environ.get(key) for key in ("LOOM_APP_ROOT","LOOM_DATA_ROOT","LOOM_CAMPAIGN_ROOT","LOOM_HOME")},"source":{"loom_gis":_file_identity(app/"src"/"loom_gis.py"),"runtime":_file_identity(app/"src"/"loom"/"runtime.py")},"databases":databases,"campaign":{"state":campaign_state,"history":campaign_history,"navigator_cache":{"path":str(cache_path),"exists":cache_path.exists(),"root":"app_root"},"shadow_sql":_shadow_sql_identity(shadow_path)},"observability":{"trace":_file_identity(trace_path)}}
def render_runtime_audit(manifest):
    roots,runtime=manifest["roots"],manifest["runtime"]; deployment=manifest.get("deployment",{}); install=deployment.get("install_state",{}); lines=["LOOM RUNTIME AUDIT","==================",f"Contract      {manifest['contract']}",f"Platform      {runtime['platform']}",f"Python        {runtime['python']}",f"App Git head  {deployment.get('app_git_head') or 'unavailable'}",f"Release       {install.get('release_id') or 'unavailable'}",f"APP ROOT      {roots['app_root']} [{roots['app_source']}]",f"DATA ROOT     {roots['data_root']} [{roots['data_source']}]",f"CAMPAIGN ROOT {roots['campaign_root']} [{roots['campaign_source']}]","","DATABASES"]
    for db in manifest["databases"]:
        status="PRESENT" if db["exists"] else "missing"; digest=db["sha256"][:12] if db["sha256"] else "-"; lines.append(f"{status:7} {db['root']:9} {db['name']} sha256={digest} path={db['path']}")
    state=manifest["campaign"]["state"]; history=manifest["campaign"]["history"]; shadow=manifest["campaign"]["shadow_sql"]; trace=manifest["observability"]["trace"]
    shadow_detail=f"rows={shadow['flight_commit_count']} revisions={shadow['min_revision']}..{shadow['max_revision']} integrity={shadow['integrity_check']}" if shadow["exists"] and not shadow["error"] else (shadow["error"] or "-")
    lines.extend(["",f"CAMPAIGN STATE {'PRESENT' if state['exists'] else 'missing'} {state['path']} revision={state.get('revision')}",f"CAMPAIGN HIST  {'PRESENT' if history['exists'] else 'missing'} {history['path']}",f"SHADOW SQL     {'PRESENT' if shadow['exists'] else 'missing'} {shadow['path']} {shadow_detail}",f"TRACE          {'PRESENT' if trace['exists'] else 'missing'} {trace['path']}"]); return "\n".join(lines)+"\n"
def manifest_json(manifest):return json.dumps(manifest,indent=2,sort_keys=True)+"\n"
