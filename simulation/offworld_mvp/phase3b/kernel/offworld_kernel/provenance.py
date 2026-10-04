from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json, os, re, subprocess
from pathlib import Path
from typing import Tuple
from .kernel import InvariantError

_HEX40=re.compile(r'^[0-9a-f]{40}$')
_HEX64=re.compile(r'^[0-9a-f]{64}$')

def source_tree_hash(package_dir:Path|None=None)->str:
    root=Path(package_dir) if package_dir else Path(__file__).resolve().parent
    h=sha256()
    for p in sorted(x for x in root.rglob('*.py') if '__pycache__' not in x.parts):
        rel=p.relative_to(root).as_posix().encode()
        data=p.read_bytes()
        h.update(len(rel).to_bytes(4,'big')); h.update(rel)
        h.update(len(data).to_bytes(8,'big')); h.update(data)
    return h.hexdigest()

def _git_commit()->str:
    env=os.environ.get('LOOM_GIT_COMMIT','').strip().lower()
    if env:
        if not _HEX40.match(env): raise InvariantError('LOOM_GIT_COMMIT must be exact 40-hex commit')
        return env
    try:
        out=subprocess.check_output(['git','rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip().lower()
    except Exception as e:
        raise InvariantError('exact Git commit unavailable; set LOOM_GIT_COMMIT for exported/archive runs') from e
    if not _HEX40.match(out): raise InvariantError('git rev-parse did not return exact commit')
    return out

def git_object_source_tree_hash(commit:str,package_dir:Path|None=None)->str:
    root=Path(package_dir) if package_dir else Path(__file__).resolve().parent
    try:
        repo=Path(subprocess.check_output(
            ['git','rev-parse','--show-toplevel'],stderr=subprocess.DEVNULL,text=True,cwd=root).strip()).resolve()
    except Exception as e:
        raise InvariantError('Git checkout unavailable for commit/code verification') from e
    try:
        rel_root=root.resolve().relative_to(repo).as_posix()
    except Exception as e:
        raise InvariantError('executable package is outside Git checkout') from e
    names=subprocess.check_output(
        ['git','ls-tree','-r','--name-only',commit,'--',rel_root],
        stderr=subprocess.DEVNULL,text=True,cwd=repo).splitlines()
    names=sorted(n for n in names if n.endswith('.py') and '/__pycache__/' not in n)
    if not names: raise InvariantError('no Python sources found in Git object for commit/code verification')
    h=sha256()
    for name in names:
        rel=Path(name).relative_to(rel_root).as_posix().encode()
        data=subprocess.check_output(['git','show',f'{commit}:{name}'],stderr=subprocess.DEVNULL,cwd=repo)
        h.update(len(rel).to_bytes(4,'big')); h.update(rel)
        h.update(len(data).to_bytes(8,'big')); h.update(data)
    return h.hexdigest()

def verify_commit_code_linkage(commit:str,current_hash:str)->str:
    try:
        object_hash=git_object_source_tree_hash(commit)
    except InvariantError:
        expected=os.environ.get('LOOM_EXPECTED_CODE_TREE_SHA256','').strip().lower()
        if not expected:
            raise InvariantError(
                'cannot verify asserted Git commit against executable code tree; '
                'run from a Git checkout or provide LOOM_EXPECTED_CODE_TREE_SHA256 from a release attestation')
        if not _HEX64.match(expected):
            raise InvariantError('LOOM_EXPECTED_CODE_TREE_SHA256 must be exact SHA-256')
        if expected!=current_hash:
            raise InvariantError('exported executable code hash does not match release attestation')
        return 'EXPORTED_CODE_HASH_ATTESTED'
    if object_hash!=current_hash:
        raise InvariantError('asserted Git commit does not match executable offworld_kernel source tree')
    return 'GIT_OBJECT_VERIFIED'

def parameter_manifest_id(parameters)->str:
    raw=json.dumps(tuple(parameters),sort_keys=True,separators=(',',':')).encode()
    return 'PARAMS_SHA256:'+sha256(raw).hexdigest()

@dataclass(frozen=True,slots=True)
class ReplayProvenance:
    repository:str
    git_commit:str
    code_tree_sha256:str
    input_snapshot_ids:Tuple[str,...]
    parameter_manifest_ids:Tuple[str,...]
    table_manifest_ids:Tuple[str,...]
    commit_code_linkage:str
    provenance_source:str='CURRENT_CHECKOUT_OR_EXPORTED_COMMIT'

    def validate(self):
        if not self.repository: raise InvariantError('replay repository identity missing')
        if not _HEX40.match(self.git_commit): raise InvariantError('replay Git commit must be exact 40-hex SHA')
        if not _HEX64.match(self.code_tree_sha256): raise InvariantError('replay code hash must be SHA-256')
        if not self.input_snapshot_ids or any(not x for x in self.input_snapshot_ids):
            raise InvariantError('replay input snapshot identity missing')
        if not self.parameter_manifest_ids or any(not x for x in self.parameter_manifest_ids):
            raise InvariantError('replay parameter manifest identity missing')
        if not self.table_manifest_ids or any(not x for x in self.table_manifest_ids):
            raise InvariantError('replay table manifest identity missing')
        if self.commit_code_linkage not in {'GIT_OBJECT_VERIFIED','EXPORTED_CODE_HASH_ATTESTED'}:
            raise InvariantError('replay commit/code linkage not verified')
        return self

    @classmethod
    def from_kernel(cls,kernel,table_manifest_ids=('NO_EXTERNAL_TABLES',)):
        rid=kernel.run_identity
        commit=_git_commit()
        code_hash=source_tree_hash()
        linkage=verify_commit_code_linkage(commit,code_hash)
        return cls(
            os.environ.get('LOOM_REPOSITORY','loom-2226/loom-2226'),
            commit,
            code_hash,
            (rid.input_snapshot_id,),
            (parameter_manifest_id(rid.parameters),),
            tuple(table_manifest_ids),
            linkage,
        ).validate()

    def fingerprint(self):
        payload={
          'repository':self.repository,'git_commit':self.git_commit,'code_tree_sha256':self.code_tree_sha256,
          'input_snapshot_ids':self.input_snapshot_ids,'parameter_manifest_ids':self.parameter_manifest_ids,
          'table_manifest_ids':self.table_manifest_ids,'commit_code_linkage':self.commit_code_linkage,
          'provenance_source':self.provenance_source}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
