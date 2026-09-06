#!/usr/bin/env python3
import argparse, hashlib, json, os, platform, sqlite3
from datetime import datetime, timezone
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()

def dbinfo(p):
 out={"path":str(p),"tables":[]}
 try:
  c=sqlite3.connect(f"file:{p.as_posix()}?mode=ro",uri=True)
  for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
   q='SELECT COUNT(*) FROM "'+t.replace(chr(34),chr(34)*2)+'"'
   n=c.execute(q).fetchone()[0]
   cols=[{"name":r[1],"type":r[2],"pk":bool(r[5])} for r in c.execute('PRAGMA table_info("'+t.replace(chr(34),chr(34)*2)+'")')]
   out["tables"].append({"name":t,"rows":n,"columns":cols})
  c.close()
 except Exception as e: out["error"]=repr(e)
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--root"); ap.add_argument("--source-root"); ap.add_argument("--hash-all",action="store_true"); a=ap.parse_args()
 root=Path(a.root or Path(__file__).resolve().parent.parent).resolve(); out=root/"inventory"; out.mkdir(exist_ok=True)
 skip={".git",".loom_backups","__pycache__","ephemeris_cache","inventory"}; files=[]; dbs=[]
 for base,dirs,names in os.walk(root):
  dirs[:]=sorted(d for d in dirs if d not in skip)
  for n in sorted(names):
   p=Path(base)/n
   try:
    r=p.relative_to(root).as_posix(); s=p.stat(); x={"path":r,"bytes":s.st_size,"mtime_utc":datetime.fromtimestamp(s.st_mtime,timezone.utc).isoformat()}
    if a.hash_all or r.startswith(("src/","data/","deploy/","manifests/")): x["sha256"]=sha(p)
    files.append(x)
    if p.suffix.lower() in {".sqlite",".sqlite3",".db"}: dbs.append(dbinfo(p))
   except Exception as e: files.append({"path":str(p),"error":repr(e)})
 state=None
 for p in (root/"manifests"/"release_manifest.json",root/".loom_install_state.json"):
  if p.exists():
   try: state={"path":str(p),"content":json.loads(p.read_text())}
   except Exception as e: state={"path":str(p),"error":repr(e)}
   break
 inv={"format":"LOOM_RUNTIME_INVENTORY_V1","generated_utc":datetime.now(timezone.utc).isoformat(),"runtime_root":str(root),"source_root":a.source_root,"host":{"platform":platform.platform()},"release_or_install_state":state,"files":files,"sqlite_databases":dbs,"excluded_dirs":sorted(skip)}
 stamp=datetime.now().strftime("%Y%m%d_%H%M%S"); jp=out/f"LOOM_RUNTIME_INVENTORY_{stamp}.json"; mp=out/f"LOOM_RUNTIME_INVENTORY_{stamp}.md"
 jp.write_text(json.dumps(inv,indent=2)+"\n")
 lines=["# LOOM Runtime Inventory","",f"Generated: `{inv['generated_utc']}`",f"Runtime: `{root}`",f"Files: **{len(files)}**","","## Databases",""]
 for d in dbs:
  lines += [f"### `{d['path']}`",f"Tables: **{len(d.get('tables',[]))}**","","| Table | Rows |","|---|---:|"]+[f"| `{t['name']}` | {t['rows']} |" for t in d.get('tables',[])]+[""]
 lines += ["## Files","","| Path | Bytes | SHA-256 |","|---|---:|---|"]+[f"| `{x.get('path','')}` | {x.get('bytes','')} | `{x.get('sha256','')}` |" for x in files]
 mp.write_text("\n".join(lines)+"\n")
 print("LOOM RUNTIME INVENTORY v1.0"); print("ROOT",root); print("FILES",len(files)); print("DATABASES",len(dbs)); print("JSON",jp); print("MARKDOWN",mp)
if __name__=="__main__": main()
