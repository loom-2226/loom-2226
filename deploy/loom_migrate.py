#!/usr/bin/env python3
"""LOOM runtime filesystem migration: audit -> stage -> activate.

Never deletes source material. Unknown files and mismatched collisions fail closed.
Activation only writes an atomic root-contract file after staged hashes validate.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import argparse,hashlib,json,os,shutil,tempfile

CONTRACT="LOOM_RUNTIME_MIGRATION_V1"
ROOT_CONTRACT="LOOM_RUNTIME_ROOTS_ACTIVATION_V1"
CAMPAIGN_FILES={"LOOM_STATE_V1.json","LOOM_STATE_V1.bak","LOOM_CAMPAIGN_HISTORY.jsonl.gz","LOOM_CAMPAIGN_DEV.sqlite3"}
APP_DIRS={"src","deploy","manifests","web","docs"}
CACHE_DIRS={"LOOM_Navigator_Cache_v1","ephemeris_cache"}
SKIP_DIRS={"data","inventory",".git"}
APP_FILES={".loom_install_state.json","LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip"}
AUDIT_FILES={"LOOM_PHONE_RUNTIME_AUDIT.txt","LOOM_Navigator_Browser_Report.json","LOOM_KNOWLEDGE_RELATIONSHIPS_DIFF.txt","LOOM_Android_Phase6_Convergence_Sync.py"}
GENERATED_FILES={"LOOM_Navigator_Current.html"}

@dataclass(frozen=True)
class Item:
    source:str; target:str|None; classification:str; size_bytes:int; sha256:str

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def classify(rel:Path)->tuple[str,str|None]:
    top=rel.parts[0]
    name=rel.name
    # Generated Python bytecode is never runtime authority; source remains retained.
    if "__pycache__" in rel.parts or name.endswith((".pyc",".pyo")):
        return "generated",None
    if top in CAMPAIGN_FILES:return "campaign",str(Path("campaign")/rel)
    if top=="LOOM_CAMPAIGN_HISTORY.jsonl.gz.bak":return "backup",str(Path("backups")/"campaign"/top)
    if top==".loom_backups":return "backup",str(Path("backups")/"legacy_runtime"/Path(*rel.parts[1:]))
    if top=="logs":return "logs",str(Path("logs")/Path(*rel.parts[1:]))
    if top.startswith("LOOM_PHASE6_") and (top.endswith(".log") or top=="LOOM_PHASE6_LATEST.txt"):
        return "logs",str(Path("logs")/top)
    if top in CACHE_DIRS:return "cache",str(Path("cache")/rel)
    if top in GENERATED_FILES:return "generated",str(Path("cache")/"generated"/top)
    if top in AUDIT_FILES:return "audit",str(Path("audit")/"legacy"/top)
    if top in SKIP_DIRS:return "preserve_existing",None
    if top in APP_DIRS or top in APP_FILES:return "application",str(Path("runtime")/rel)
    # Phase-6 SequenceH artifacts are application dependencies. Keep source/package,
    # but the bytecode exclusion above still wins.
    if "SequenceH" in top or "SEQUENCEH" in top.upper():return "application",str(Path("runtime")/rel)
    return "unknown",None

def audit(source:Path,target:Path)->dict:
    source=source.resolve(); target=target.resolve(); items=[]
    for p in sorted(source.rglob("*")):
        if not p.is_file():continue
        rel=p.relative_to(source); cls,dest=classify(rel); items.append(Item(str(p),str(target/dest) if dest else None,cls,p.stat().st_size,sha256(p)))
    return {"contract":CONTRACT,"source_root":str(source),"target_root":str(target),"items":[asdict(x) for x in items],"unknown_count":sum(x.classification=="unknown" for x in items)}

def _copy_verified(item:dict):
    src=Path(item["source"]); dst=Path(item["target"]); dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        if not dst.is_file() or sha256(dst)!=item["sha256"]:raise RuntimeError(f"COLLISION MISMATCH: {dst}")
        return
    fd,tmp=tempfile.mkstemp(prefix=dst.name+".",suffix=".stage",dir=str(dst.parent)); os.close(fd); temp=Path(tmp)
    try:
        shutil.copy2(src,temp)
        if sha256(temp)!=item["sha256"]:raise RuntimeError(f"STAGE HASH MISMATCH: {src}")
        temp.replace(dst)
    finally:
        if temp.exists():temp.unlink()

def _migrates(item:dict)->bool:
    return item["classification"] not in {"preserve_existing","generated"}

def stage(plan:dict)->dict:
    if plan.get("contract")!=CONTRACT:raise RuntimeError("unsupported migration contract")
    if plan.get("unknown_count"):raise RuntimeError(f"UNKNOWN FILES BLOCK STAGE: {plan['unknown_count']}")
    copied=0
    for item in plan["items"]:
        if not _migrates(item):continue
        _copy_verified(item); copied+=1
    return validate(plan)|{"staged_files":copied}

def validate(plan:dict)->dict:
    failures=[]; checked=0
    for item in plan["items"]:
        if not _migrates(item):continue
        checked+=1; dst=Path(item["target"])
        if not dst.is_file() or sha256(dst)!=item["sha256"]:failures.append(str(dst))
    return {"contract":CONTRACT,"checked_files":checked,"valid":not failures,"failures":failures}

def activate(plan:dict)->Path:
    result=validate(plan)
    if plan.get("unknown_count") or not result["valid"]:raise RuntimeError("migration is not fully staged and validated")
    target=Path(plan["target_root"]); audit_dir=target/"audit"; audit_dir.mkdir(parents=True,exist_ok=True)
    payload={"contract":ROOT_CONTRACT,"LOOM_APP_ROOT":str((target/"runtime").resolve()),"LOOM_DATA_ROOT":str((target/"data").resolve()),"LOOM_CAMPAIGN_ROOT":str((target/"campaign").resolve()),"source_root_retained":plan["source_root"]}
    dst=audit_dir/"runtime_roots.json"; tmp=dst.with_suffix(".json.tmp"); tmp.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8"); tmp.replace(dst); return dst

def main(argv=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument("action",choices=("audit","stage","validate","activate")); ap.add_argument("--source",required=True); ap.add_argument("--target",required=True); ap.add_argument("--json",action="store_true"); args=ap.parse_args(argv)
    plan=audit(Path(args.source),Path(args.target))
    if args.action=="audit":result=plan
    elif args.action=="stage":result=stage(plan)
    elif args.action=="validate":result=validate(plan)
    else:result={"activated":str(activate(plan))}
    print(json.dumps(result,indent=2,sort_keys=True) if args.json else result); return 0
if __name__=="__main__":raise SystemExit(main())
