#!/usr/bin/env python3
"""LOOM 2226 updater/bootstrap v0.7-convergence.

Installs application/code and canonical reference data into explicit roots.
Mutable campaign state is outside updater authority and is never an installation
target. This convergence version preserves the physically audited Pixel layout:
APP=/Download/LOOM_TEST and DATA=/Documents/LOOM/data until migration activation.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import argparse,hashlib,json,os,shutil,sys,tempfile
from urllib.request import Request,urlopen
OWNER="loom-2226"; REPO="loom-2226"; DEFAULT_REF="main"
CONTENTS_API=f"https://api.github.com/repos/{OWNER}/{REPO}/contents"; RELEASE_ASSET_API=f"https://api.github.com/repos/{OWNER}/{REPO}/releases/assets"
ANDROID_APP_ROOT=Path("/storage/emulated/0/Download/LOOM_TEST"); ANDROID_DATA_ROOT=Path("/storage/emulated/0/Documents/LOOM/data")
WINDOWS_APP_ROOT=Path.home()/"Documents"/"LOOM"; MANIFEST_PATH="manifests/release_manifest.json"; INSTALL_STATE=".loom_install_state.json"; DOWNLOAD_CHUNK_BYTES=1024*1024; PROGRESS_THRESHOLD_BYTES=8*1024*1024
@dataclass(frozen=True)
class InstallRoots: app_root:Path; data_root:Path
@dataclass(frozen=True)
class ArtifactResult: path:str; target:str|None; state:str; expected_sha256:str|None; actual_sha256:str|None
def sha256_bytes(data):return hashlib.sha256(data).hexdigest()
def git_blob_sha1_bytes(data):return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()
def sha256_file(path):
 h=hashlib.sha256()
 with path.open("rb") as fh:
  for chunk in iter(lambda:fh.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def git_blob_sha1_file(path):
 data=path.read_bytes(); return git_blob_sha1_bytes(data)
def expected_digest(a):
 if a.get("sha256"):return "sha256",a["sha256"]
 if a.get("git_blob_sha1"):return "git_blob_sha1",a["git_blob_sha1"]
 return None,None
def actual_digest_bytes(data,kind):return sha256_bytes(data) if kind=="sha256" else git_blob_sha1_bytes(data)
def actual_digest_file(path,kind):return sha256_file(path) if kind=="sha256" else git_blob_sha1_file(path)
def _is_android(env):return bool(env.get("ANDROID_ROOT") or env.get("TERMUX_VERSION")) or Path("/storage/emulated/0").exists()
def platform_roots(app_explicit=None,data_explicit=None,environ=None):
 env=os.environ if environ is None else environ; legacy=str(env.get("LOOM_HOME","")).strip(); app_value=app_explicit or str(env.get("LOOM_APP_ROOT","")).strip() or legacy; android=_is_android(env); app=Path(app_value).expanduser() if app_value else (ANDROID_APP_ROOT if android else WINDOWS_APP_ROOT); data_value=data_explicit or str(env.get("LOOM_DATA_ROOT","")).strip(); data=Path(data_value).expanduser() if data_value else (ANDROID_DATA_ROOT if android else app/"data"); return InstallRoots(app.resolve(),data.resolve())
def platform_root(explicit=None):return platform_roots(app_explicit=explicit).app_root
def token():
 value=os.environ.get("LOOM_GITHUB_TOKEN","").strip()
 if value:return value
 p=Path.home()/".loom_github_token"
 if p.exists() and (value:=p.read_text(encoding="utf-8").strip()):return value
 raise RuntimeError("GitHub token not configured. Set LOOM_GITHUB_TOKEN or create ~/.loom_github_token")
def _format_bytes(n):
 value=float(n)
 for unit in ("B","KiB","MiB","GiB"):
  if value<1024 or unit=="GiB":return f"{value:.0f} {unit}" if unit=="B" else f"{value:.1f} {unit}"
  value/=1024
def _progress_line(label,downloaded,total):
 if total and total>0:return f"DOWNLOADING      {label}  {min(100.0,downloaded*100.0/total):5.1f}%  {_format_bytes(downloaded)} / {_format_bytes(total)}"
 return f"DOWNLOADING      {label}  {_format_bytes(downloaded)}"
def github_bytes(url,accept,*,label=None,expected_size=None):
 req=Request(url,headers={"Authorization":f"Bearer {token()}","Accept":accept,"X-GitHub-Api-Version":"2022-11-28","User-Agent":"LOOM-2226-Updater/0.7-convergence"})
 with urlopen(req,timeout=900) as response:
  total=expected_size
  if total is None and response.headers.get("Content-Length"):
   try:total=int(response.headers["Content-Length"])
   except ValueError:total=None
  show=bool(label) and (total is None or total>=PROGRESS_THRESHOLD_BYTES); payload=bytearray(); last=-1
  while True:
   chunk=response.read(DOWNLOAD_CHUNK_BYTES)
   if not chunk:break
   payload.extend(chunk)
   if show:
    downloaded=len(payload); bucket=int(downloaded*20/total) if total else downloaded//(8*1024*1024)
    if bucket!=last:print("\r"+_progress_line(label or "payload",downloaded,total),end="",flush=True); last=bucket
  if show:print("\r"+_progress_line(label or "payload",len(payload),total),flush=True)
  return bytes(payload)
def github_contents_bytes(path,ref):return github_bytes(f"{CONTENTS_API}/{path}?ref={ref}","application/vnd.github.raw+json")
def github_artifact_bytes(a,ref):
 source=a.get("source","repository"); label=a["path"]; size=a.get("size_bytes")
 if source=="repository":return github_bytes(f"{CONTENTS_API}/{a['path']}?ref={ref}","application/vnd.github.raw+json",label=label,expected_size=size)
 if source=="release_asset":
  aid=a.get("asset_id")
  if not isinstance(aid,int):raise RuntimeError(f"Release asset missing numeric asset_id: {a['path']}")
  return github_bytes(f"{RELEASE_ASSET_API}/{aid}","application/octet-stream",label=label,expected_size=size)
 raise RuntimeError(f"Unknown artifact source {source!r}: {a['path']}")
def _coerce_roots(roots):
 if isinstance(roots,InstallRoots):return roots
 p=Path(roots).expanduser().resolve(); return InstallRoots(p,p/"data")
def target_for(roots,a):
 roots=_coerce_roots(roots); src=Path(a["path"]); group=a["install_group"]
 if group=="code":
  if not src.parts or src.parts[0]!="src" or ".." in src.parts:raise ValueError(f"Unsafe code artifact path: {a['path']}")
  return roots.app_root/src
 if group in {"canonical_data","media"}:
  if src.name!=str(src).split("/")[-1]:raise ValueError(f"Unsafe data artifact path: {a['path']}")
  return roots.data_root/src.name
 raise ValueError(f"Unknown install_group: {group}")
def atomic_write(target,data,backup_root=None,relative_backup=None):
 target.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as tf:tmp=Path(tf.name); tf.write(data); tf.flush(); os.fsync(tf.fileno())
 try:
  if target.exists() and backup_root is not None:
   backup=backup_root/(relative_backup or Path(target.name)); backup.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(target,backup)
  os.replace(tmp,target)
 finally:
  if tmp.exists():tmp.unlink(missing_ok=True)
def validate_manifest(manifest):
 artifacts=manifest.get("artifacts")
 if not isinstance(artifacts,list):raise RuntimeError("Release manifest is missing artifacts list")
 for a in artifacts:
  for key in ("path","install_group","required"):
   if key not in a:raise RuntimeError(f"Artifact missing {key}: {a}")
  if a["install_group"] not in {"code","canonical_data","media"}:raise RuntimeError(f"Unknown install_group: {a['install_group']}")
  source=a.get("source","repository")
  if source not in {"repository","release_asset"}:raise RuntimeError(f"Unknown artifact source {source!r}")
  if source=="release_asset" and not isinstance(a.get("asset_id"),int):raise RuntimeError(f"Release asset missing numeric asset_id: {a['path']}")
  if a.get("sha256") and a.get("git_blob_sha1"):raise RuntimeError(f"Artifact has multiple digests: {a['path']}")
  size=a.get("size_bytes")
  if size is not None and (not isinstance(size,int) or size<0):raise RuntimeError(f"Invalid size_bytes for {a['path']}")
def load_manifest(ref):
 manifest=json.loads(github_contents_bytes(MANIFEST_PATH,ref).decode("utf-8")); validate_manifest(manifest); source=manifest.get("source_ref")
 if source and source!=ref:raise RuntimeError(f"Manifest source_ref={source!r} does not match requested ref={ref!r}")
 return manifest
def validate_local(roots,manifest):
 roots=_coerce_roots(roots); out=[]
 for a in manifest["artifacts"]:
  kind,expected=expected_digest(a); target=target_for(roots,a)
  if not expected:out.append(ArtifactResult(a["path"],str(target),"PENDING_REQUIRED" if a.get("required") else "PENDING_OPTIONAL",None,None)); continue
  if not target.exists():out.append(ArtifactResult(a["path"],str(target),"MISSING",expected,None)); continue
  actual=actual_digest_file(target,kind); size=a.get("size_bytes"); out.append(ArtifactResult(a["path"],str(target),"OK" if actual==expected and (size is None or target.stat().st_size==size) else "MISMATCH",expected,actual))
 return out
def install_release(roots,manifest,ref,artifact_fetcher=github_artifact_bytes,dry_run=False):
 roots=_coerce_roots(roots); release=manifest["release_id"]; backup_root=roots.app_root/".loom_backups"/release; out=[]
 for a in manifest["artifacts"]:
  kind,expected=expected_digest(a); required=bool(a.get("required")); target=target_for(roots,a); print(f"CHECKING         {a['path']}")
  if not expected:out.append(ArtifactResult(a["path"],str(target),"PENDING_REQUIRED" if required else "PENDING_OPTIONAL",None,None)); continue
  if target.exists() and (a.get("size_bytes") is None or target.stat().st_size==a["size_bytes"]):
   print(f"VERIFYING        {a['path']}")
   if actual_digest_file(target,kind)==expected:out.append(ArtifactResult(a["path"],str(target),"UNCHANGED",expected,expected)); continue
  print(f"FETCHING         {a['path']}"); payload=artifact_fetcher(a,ref); size=a.get("size_bytes")
  if size is not None and len(payload)!=size:raise RuntimeError(f"SIZE MISMATCH for {a['path']}\nexpected={size}\nactual={len(payload)}")
  print(f"VERIFYING        {a['path']}"); actual=actual_digest_bytes(payload,kind)
  if actual!=expected:raise RuntimeError(f"DIGEST MISMATCH for {a['path']}\nexpected={expected}\nactual={actual}")
  if not dry_run:
   rel=Path(a["path"]) if a["install_group"]=="code" else Path("data")/target.name; atomic_write(target,payload,backup_root=backup_root,relative_backup=rel); state="INSTALLED"
  else:state="DRY_RUN_OK"
  out.append(ArtifactResult(a["path"],str(target),state,expected,actual))
 if not dry_run:
  roots.app_root.mkdir(parents=True,exist_ok=True); state={"release_id":release,"release_state":manifest.get("release_state"),"source_ref":ref,"app_root":str(roots.app_root),"data_root":str(roots.data_root),"artifacts":[r.__dict__ for r in out]}; (roots.app_root/INSTALL_STATE).write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
 return out
def print_results(results):
 for r in results:print(f"{r.state:16} {r.path}")
def has_blockers(results):return any(r.state in {"PENDING_REQUIRED","MISSING","MISMATCH"} for r in results)
def parse_args(argv=None):
 p=argparse.ArgumentParser(description="LOOM 2226 GitHub updater and validator"); p.add_argument("command",nargs="?",choices=["update","validate","status"],default="update"); p.add_argument("--ref",default=os.environ.get("LOOM_REF",DEFAULT_REF)); p.add_argument("--root",help="Compatibility alias for --app-root"); p.add_argument("--app-root"); p.add_argument("--data-root"); p.add_argument("--dry-run",action="store_true"); return p.parse_args(argv)
def main(argv=None,manifest_loader=load_manifest,artifact_fetcher=github_artifact_bytes):
 args=parse_args(argv); roots=platform_roots(args.app_root or args.root,args.data_root); manifest=manifest_loader(args.ref); print(f"LOOM APP ROOT: {roots.app_root}"); print(f"LOOM DATA ROOT: {roots.data_root}"); print(f"SOURCE REF: {args.ref}"); print(f"RELEASE: {manifest['release_id']} ({manifest['release_state']})")
 if args.command in {"validate","status"}:results=validate_local(roots,manifest); print_results(results); return 2 if has_blockers(results) else 0
 results=install_release(roots,manifest,args.ref,artifact_fetcher=artifact_fetcher,dry_run=args.dry_run); print_results(results)
 if has_blockers(results):print("\nNOT RELEASE-COMPLETE: one or more required artifacts are pending or invalid."); return 2
 print("\nLOOM UPDATE COMPLETE"); return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except Exception as exc:print(f"UPDATE FAILED: {exc}",file=sys.stderr); raise SystemExit(1)
