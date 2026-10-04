from __future__ import annotations
import ast
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Tuple

from .financing_protocol import build_financing_decision, required_unknown_inputs
from .mvp_state import FinancingDecisionOutcome, FinancingReasonCode, FinancingRequest
from .policy import DecisionSnapshot
from .policies.manifest import FinancierPolicyManifest, policy_source_bytes

FORBIDDEN_IMPORT_ROOTS={
    'os','sys','time','datetime','random','secrets','socket','subprocess','pathlib',
    'urllib','requests','http','ftplib','shutil','tempfile','importlib','ctypes','multiprocessing',
}
FORBIDDEN_CALLS={
    'open','exec','eval','compile','input','breakpoint','__import__','globals','locals','vars',
}
ALLOWED_IMPORT_ROOTS={'decimal'}

@dataclass(frozen=True,slots=True)
class PolicyExecutionResult:
    decision: object
    policy_version: str
    parameter_manifest_hash: str
    worker_fingerprint: str
    metrics: Tuple[Tuple[str,str],...]
    sandbox_mode: str='ISOLATED_SUBPROCESS_SERIALIZED_INPUTS'

def assert_policy_source_safe(source:bytes):
    tree=ast.parse(source.decode())
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[]
            if isinstance(node,ast.Import):
                names=[a.name.split('.')[0] for a in node.names]
            elif node.module:
                names=[node.module.split('.')[0]]
            for root in names:
                if root in FORBIDDEN_IMPORT_ROOTS or root not in ALLOWED_IMPORT_ROOTS:
                    raise ValueError(f'forbidden policy import: {root}')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_CALLS:
            raise ValueError(f'forbidden policy call: {node.func.id}')
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name):
            if node.value.id in FORBIDDEN_IMPORT_ROOTS:
                raise ValueError(f'forbidden policy module access: {node.value.id}')
    return True

def _fact_wire(f):
    return {'key':f.key,'state':f.state.value,'value':f.value,'source_ref':f.source_ref}

def snapshot_to_wire(s:DecisionSnapshot):
    return {
        'agent_id':s.agent_id,
        'agent_kind':s.agent_kind,
        'node_id':s.node_id,
        'period_key':s.period_key,
        'effective_time':s.effective_time,
        'account_balance':str(s.account_balance),
        'capabilities':list(s.capabilities),
        'objectives':list(s.objectives),
        'information_refs':list(s.information_refs),
        'beliefs':[[k,str(v)] for k,v in s.beliefs],
        'priors':[[k,str(v)] for k,v in s.priors],
        'asset_refs':list(s.asset_refs),
        'resource_holdings':[[k,str(v)] for k,v in s.resource_holdings],
        'claim_holdings':[[k,str(v)] for k,v in s.claim_holdings],
        'admitted_facts':[_fact_wire(f) for f in s.admitted_facts],
    }

def request_to_wire(q:FinancingRequest):
    return {
        'id':q.id,'year':q.year,'sponsor_id':q.sponsor_id,'project_id':q.project_id,
        'amount':str(q.amount),'stage':q.stage,
        'disclosed_observation_ids':list(q.disclosed_observation_ids),
        'required_underwriting_keys':list(q.required_underwriting_keys),
        'required_belief_keys':list(q.required_belief_keys),
        'required_prior_keys':list(q.required_prior_keys),
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }

def _worker_path():
    return Path(__file__).resolve().parent/'policies'/'worker.py'

def _run_worker(payload,timeout_seconds=3):
    raw=json.dumps(payload,sort_keys=True,separators=(',',':'))
    cp=subprocess.run(
        [sys.executable,'-I','-S',str(_worker_path())],
        input=raw,text=True,capture_output=True,timeout=timeout_seconds,
        env={'PYTHONHASHSEED':'0'},cwd='/',
    )
    if cp.returncode!=0:
        raise RuntimeError(f'policy worker failed: {cp.stderr.strip()}')
    try:
        result=json.loads(cp.stdout)
    except Exception as e:
        raise RuntimeError('policy worker returned invalid JSON') from e
    fp=sha256(cp.stdout.encode()).hexdigest()
    return result,fp

def run_hostile_access_probe(snapshot:DecisionSnapshot):
    payload={'mode':'HOSTILE_ACCESS_PROBE','snapshot':snapshot_to_wire(snapshot)}
    result,fp=_run_worker(payload)
    return result,fp

def run_financier_policy(snapshot:DecisionSnapshot,request:FinancingRequest,
                         manifest:FinancierPolicyManifest,decision_key:str,
                         allow_test_fixture:bool=False)->PolicyExecutionResult:
    request.validate_protocol()
    manifest.validate(require_authorized=not allow_test_fixture)
    source=policy_source_bytes()
    assert_policy_source_safe(source)
    version=manifest.policy_version_hash(source)
    manifest_hash=manifest.parameter_manifest_hash()

    unknowns=required_unknown_inputs(request,snapshot)
    decision_id='DEC-'+sha256(
        ('|'.join((request.id,snapshot.fingerprint(),version,str(decision_key)))).encode()
    ).hexdigest()[:20]
    if unknowns:
        decision=build_financing_decision(
            decision_id,request,snapshot.agent_id,
            FinancingDecisionOutcome.BLOCKED_UNKNOWN,
            FinancingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted decision inputs are unknown',
            snapshot,version)
        return PolicyExecutionResult(
            decision,version,manifest_hash,
            sha256(('BLOCKED|'+'|'.join(unknowns)).encode()).hexdigest(),
            tuple((f'unknown:{i}',k) for i,k in enumerate(unknowns)),
            'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    payload={
        'mode':'EVALUATE',
        'snapshot':snapshot_to_wire(snapshot),
        'request':request_to_wire(request),
        'manifest':manifest.wire_dict(),
        'decision_key':str(decision_key),
    }
    out,worker_fp=_run_worker(payload)
    try:
        outcome=FinancingDecisionOutcome(out['outcome'])
        reason_code=FinancingReasonCode(out['reason_code'])
        amount=out.get('amount','0')
        instrument=out.get('instrument','')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('policy worker returned invalid decision payload') from e

    decision=build_financing_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,amount=amount,instrument=instrument)
    return PolicyExecutionResult(decision,version,manifest_hash,worker_fp,metrics)
