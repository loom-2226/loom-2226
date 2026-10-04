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
        return self

    @classmethod
    def from_kernel(cls,kernel,table_manifest_ids=('NO_EXTERNAL_TABLES',)):
        rid=kernel.run_identity
        return cls(
            os.environ.get('LOOM_REPOSITORY','loom-2226/loom-2226'),
            _git_commit(),
            source_tree_hash(),
            (rid.input_snapshot_id,),
            (parameter_manifest_id(rid.parameters),),
            tuple(table_manifest_ids),
        ).validate()

    def fingerprint(self):
        payload={
          'repository':self.repository,'git_commit':self.git_commit,'code_tree_sha256':self.code_tree_sha256,
          'input_snapshot_ids':self.input_snapshot_ids,'parameter_manifest_ids':self.parameter_manifest_ids,
          'table_manifest_ids':self.table_manifest_ids,'provenance_source':self.provenance_source}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
