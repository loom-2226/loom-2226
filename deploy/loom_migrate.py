#!/usr/bin/env python3
"""Non-destructive LOOM runtime filesystem migration.

Audit first, copy second, validate hashes, then write an activation record. Source
material is never deleted by this tool.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, os, shutil, tempfile

CONTRACT="LOOM_RUNTIME_MIGRATION_V1"; ACTIVATION_CONTRACT="LOOM_RUNTIME_ROOTS_ACTIVATION_V1"
CAMPAIGN={"LOOM_STATE_V1.json","LOOM_STATE_V1.bak","LOOM_CAMPAIGN_HISTORY.jsonl.gz","LOOM_CAMPAIGN_DEV.sqlite3"}
APP_DIRS={"src","deploy","manifests","web","docs"}; APP_FILES={".loom_install_state.json","LOOM_Navigator_Visual_Design_B1_LOCKED_Package_v1.0.zip","loom_update.py"}; CACHE_DIRS={"LOOM_Navigator_Cache_v1","ephemeris_cache"}; SKIP_DIRS={"data","inventory",".git"}; AUDIT_FILES={"LOOM_PHONE_RUNTIME_AUDIT.txt","LOOM_Navigator_Browser_Report.json","LOOM_KNOWLEDGE_RELATIONSHIPS_DIFF.txt","LOOM_Android_Phase6_Convergence_Sync.py","LOOM_WORLD_DB_DIVERGENCE_AUDIT.txt","LOOM_WORLD_DB_LOGICAL_DIFF_AUDIT.txt"}
def sha256_file(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
sha256=sha256_file

def classify(rel):
 p=Path(rel); top=p.parts[0] if p.parts else ''; name=p.name; lower_parts={x.lower() for x in p.parts}
 if name.endswith(('.pyc','.pyo')) or '__pycache__' in lower_parts:return 'generated',None
 if name in CAMPAIGN:return 'campaign',str(Path('campaign')/name)
 if name=='LOOM_CAMPAIGN_HISTORY.jsonl.gz.bak':return 'backup',str(Path('backups/campaign')/name)
 if top=='.loom_backups':return 'backup',str(Path('backups/legacy_runtime')/Path(*p.parts[1:]))
 if top=='logs':return 'logs',str(Path('logs')/Path(*p.parts[1:]))
 if name.startswith('LOOM_PHASE6_') and (name.endswith('.log') or name=='LOOM_PHASE6_LATEST.txt'):return 'logs',str(Path('logs')/name)
 if top in CACHE_DIRS:return 'cache',str(Path('cache')/p)
 if name=='LOOM_Navigator_Current.html':return 'generated',str(Path('cache/generated')/name)
 if name in AUDIT_FILES:return 'audit',str(Path('audit/legacy')/name)
 if top in SKIP_DIRS:return 'preserve_existing',None
 if top in APP_DIRS or top in APP_FILES:return 'application',str(Path('runtime')/p)
 if any('sequenceh' in x.lower() for x in p.parts):return 'application',str(Path('runtime')/p)
 return 'unknown',None

def audit(source,target):
 source=Path(source).expanduser().resolve(); target=Path(target).expanduser().resolve(); items=[]
 for path in sorted(x for x in source.rglob('*') if x.is_file()):
  rel=path.relative_to(source); cls,dest=classify(rel); items.append({'source':str(path),'relative':str(rel),'classification':cls,'target':str(target/dest) if dest else None,'size_bytes':path.stat().st_size,'sha256':sha256_file(path)})
 return {'contract':CONTRACT,'source_root':str(source),'target_root':str(target),'unknown_count':sum(i['classification']=='unknown' for i in items),'items':items}
def _migrates(i):return i['classification'] not in {'preserve_existing','generated'}
def _copy_verified(src,dst,expected):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():
  actual=sha256_file(dst)
  if actual!=expected:raise RuntimeError(f'COLLISION MISMATCH: {dst}')
  return 'UNCHANGED'
 with tempfile.NamedTemporaryFile(dir=dst.parent,delete=False) as f:tmp=Path(f.name)
 try:
  shutil.copy2(src,tmp)
  if sha256_file(tmp)!=expected:raise RuntimeError(f'copy verification failed: {src}')
  os.replace(tmp,dst); return 'COPIED'
 finally:tmp.unlink(missing_ok=True)
def validate(plan,exclude_classes=None):
 excluded=set(exclude_classes or ()); failures=[]; checked=0; skipped=0
 for i in plan['items']:
  if not _migrates(i):continue
  if i['classification'] in excluded:
   skipped+=1; continue
  checked+=1; dst=Path(i['target'])
  if not dst.exists():failures.append({'target':str(dst),'error':'missing'});continue
  actual=sha256_file(dst)
  if actual!=i['sha256']:failures.append({'target':str(dst),'error':'hash_mismatch','expected':i['sha256'],'actual':actual})
 return {'contract':CONTRACT,'checked_files':checked,'skipped_files':skipped,'excluded_classes':sorted(excluded),'failures':failures,'valid':not failures}
def stage(plan):
 if plan.get('contract')!=CONTRACT:raise RuntimeError('unsupported migration contract')
 if plan.get('unknown_count'):raise RuntimeError('UNKNOWN FILES BLOCK STAGE')
 results=[]
 for i in plan['items']:
  if not _migrates(i):continue
  results.append({'source':i['source'],'target':i['target'],'state':_copy_verified(Path(i['source']),Path(i['target']),i['sha256'])})
 validation=validate(plan)
 return validation|{'staged_files':len(results),'staged_results':results,'validation':validation}
def activate(plan):
 if plan.get('unknown_count'):raise RuntimeError('cannot activate with unknown files')
 # Application files may differ after qualified deployment. Logs and caches are live,
 # non-authoritative runtime products and may continue changing while the retained
 # legacy runtime remains available during cutover. Campaign, backup, and audit
 # preservation material remains hash-checked.
 validation=validate(plan,exclude_classes={'application','logs','cache'})
 if not validation['valid']:raise RuntimeError('migration is not fully staged and validated')
 target=Path(plan['target_root']); roots={'contract':ACTIVATION_CONTRACT,'app_root':str((target/'runtime').resolve()),'data_root':str((target/'data').resolve()),'campaign_root':str((target/'campaign').resolve()),'source_root_retained':plan['source_root']}
 required=[Path(roots['app_root'])/'src'/name for name in ('loom_gis.py','loom_navigator.py')]
 required += [Path(roots['data_root'])/name for name in ('LOOM_2226.sqlite3','LOOM_2226_CIVSTATE.sqlite3')]
 required += [Path(roots['campaign_root'])/'LOOM_STATE_V1.json',Path(roots['campaign_root'])/'LOOM_CAMPAIGN_HISTORY.jsonl.gz']
 missing=[str(p) for p in required if not p.exists()]
 if missing:raise RuntimeError('cannot activate; authoritative root files missing: '+', '.join(missing))
 audit_dir=target/'audit'; audit_dir.mkdir(parents=True,exist_ok=True); out=audit_dir/'runtime_roots.json'; payload=(json.dumps(roots,indent=2)+'\n').encode(); _copy_atomic(out,payload); return {'contract':CONTRACT,'activation_file':str(out),'roots':roots,'validation':validation,'required_files_verified':[str(p) for p in required]}
def _copy_atomic(target,data):
 target.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:tmp=Path(f.name); f.write(data); f.flush(); os.fsync(f.fileno())
 try:os.replace(tmp,target)
 finally:tmp.unlink(missing_ok=True)
def parse_args(argv=None):
 p=argparse.ArgumentParser();p.add_argument('action',choices=['audit','stage','validate','activate']);p.add_argument('--source',required=True);p.add_argument('--target',required=True);p.add_argument('--json',action='store_true');return p.parse_args(argv)
def main(argv=None):
 a=parse_args(argv);plan=audit(a.source,a.target);result=plan if a.action=='audit' else stage(plan) if a.action=='stage' else validate(plan) if a.action=='validate' else activate(plan);print(json.dumps(result,indent=2) if a.json else result);return 0
if __name__=='__main__':raise SystemExit(main())
