#!/usr/bin/env python3
"""Create one compact LOOM runtime-debug bundle for physical-host diagnosis.

Runtime inputs are read-only. The only mutation is creation/replacement of the
requested ZIP artifact under the audit tree (or an explicit output path).
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import zipfile

SRC=Path(__file__).resolve().parent
if str(SRC) not in sys.path:sys.path.insert(0,str(SRC))

from loom.runtime import resolve_runtime_roots
from loom.runtime_diagnostics import collect_runtime_manifest,manifest_json,render_runtime_audit

CONTRACT="LOOM_RUNTIME_DEBUG_BUNDLE_V1"
TAIL_BYTES=256*1024


def _read_tail(path:Path,limit:int=TAIL_BYTES)->bytes:
    if not path.is_file():return b""
    size=path.stat().st_size
    with path.open("rb") as fh:
        if size>limit:fh.seek(size-limit)
        return fh.read()


def _latest_http_log(app:Path)->Path|None:
    items=[p for p in app.glob("LOOM_PHASE6_HTTP_*.log") if p.is_file()]
    return max(items,key=lambda p:p.stat().st_mtime) if items else None


def _repo_identity(repo:Path|None)->dict:
    out={"path":str(repo) if repo else None,"exists":bool(repo and repo.is_dir()),"head":None,"status_short":None,"error":None}
    if not repo or not repo.is_dir():return out
    try:
        head=subprocess.run(["git","-C",str(repo),"rev-parse","HEAD"],capture_output=True,text=True,timeout=3,check=False)
        status=subprocess.run(["git","-C",str(repo),"status","--short"],capture_output=True,text=True,timeout=3,check=False)
        if head.returncode==0:out["head"]=head.stdout.strip() or None
        if status.returncode==0:out["status_short"]=status.stdout
        if head.returncode or status.returncode:out["error"]="git command returned non-zero"
    except Exception as exc:out["error"]=f"{type(exc).__name__}: {exc}"
    return out


def build_bundle(*,app_root=None,data_root=None,campaign_root=None,repo_root=None,output=None)->Path:
    roots=resolve_runtime_roots(app_root=app_root,data_root=data_root,campaign_root=campaign_root)
    manifest=collect_runtime_manifest(roots=roots)
    app,data,campaign=roots.app_root,roots.data_root,roots.campaign_root
    topology=app.parent if campaign!=app else app
    audit=topology/"audit"
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=Path(output).expanduser().resolve() if output else audit/f"LOOM_DEBUG_BUNDLE_{stamp}.zip"
    out.parent.mkdir(parents=True,exist_ok=True)
    repo=Path(repo_root).expanduser().resolve() if repo_root else (Path(os.environ["LOOM_REPO_ROOT"]).expanduser().resolve() if os.environ.get("LOOM_REPO_ROOT") else None)
    summary={
        "contract":CONTRACT,
        "created_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "bundle_path":str(out),
        "roots":roots.to_dict(),
        "repo":_repo_identity(repo),
    }
    http=_latest_http_log(app)
    trace=campaign/"logs"/"loom-trace.jsonl"
    activation=topology/"audit"/"runtime_roots.json"
    install=app/".loom_install_state.json"
    state=campaign/"LOOM_STATE_V1.json"
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("summary.json",json.dumps(summary,indent=2,sort_keys=True)+"\n")
        z.writestr("diagnostics.json",manifest_json(manifest))
        z.writestr("runtime_audit.txt",render_runtime_audit(manifest))
        for arc,path in (("install_state.json",install),("activation_roots.json",activation),("campaign_state.json",state)):
            if path.is_file():z.writestr(arc,path.read_bytes())
        if http:z.writestr("logs/latest_http_tail.log",_read_tail(http))
        if trace.is_file():z.writestr("logs/trace_tail.jsonl",_read_tail(trace))
    return out


def main(argv=None)->int:
    ap=argparse.ArgumentParser(description="Create a compact LOOM physical-runtime debug bundle.")
    ap.add_argument("--app-root",type=Path);ap.add_argument("--data-root",type=Path);ap.add_argument("--campaign-root",type=Path)
    ap.add_argument("--repo-root",type=Path,help="optional local Git checkout for HEAD/status evidence")
    ap.add_argument("--output",type=Path)
    a=ap.parse_args(argv)
    out=build_bundle(app_root=a.app_root,data_root=a.data_root,campaign_root=a.campaign_root,repo_root=a.repo_root,output=a.output)
    print(out)
    return 0

if __name__=="__main__":raise SystemExit(main())
