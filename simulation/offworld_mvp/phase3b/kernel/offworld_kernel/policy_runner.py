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
from .exploration_protocol import build_exploration_decision, required_unknown_exploration_inputs
from .publication_protocol import build_publication_decision
from .sponsor_protocol import build_sponsor_project_decision, required_unknown_sponsor_inputs
from .mvp_state import (
    FinancingDecisionOutcome, FinancingReasonCode, FinancingRequest,
    ExplorationDecisionOutcome, ExplorationReasonCode, ExplorationRequest,
    PublicationDecisionOutcome, PublicationReasonCode, PublicationRequest,
    SponsorProjectDecisionOutcome, SponsorProjectReasonCode, SponsorProjectDecisionRequest,
)
from .policy import DecisionSnapshot
from .policies.manifest import FinancierPolicyManifest, policy_source_bytes
from .policies.public_explorer_v1 import (
    POLICY_CONTRACT as PUBLIC_EXPLORER_CONTRACT,
    POLICY_ID as PUBLIC_EXPLORER_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_EXPLORER_SEMANTIC_VERSION,
)
from .policies.public_publisher_v1 import (
    POLICY_CONTRACT as PUBLIC_PUBLISHER_CONTRACT,
    POLICY_ID as PUBLIC_PUBLISHER_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_PUBLISHER_SEMANTIC_VERSION,
)
from .policies.sponsor_operator_v1 import (
    POLICY_CONTRACT as SPONSOR_OPERATOR_CONTRACT,
    POLICY_ID as SPONSOR_OPERATOR_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_OPERATOR_SEMANTIC_VERSION,
)

FORBIDDEN_IMPORT_ROOTS={
    'os','sys','time','datetime','random','secrets','socket','subprocess','pathlib',
    'urllib','requests','http','ftplib','shutil','tempfile','importlib','ctypes','multiprocessing',
}
FORBIDDEN_CALLS={
    'open','exec','eval','compile','input','breakpoint','__import__','globals','locals','vars',
    'getattr','setattr','delattr','hasattr',
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
    for top in tree.body:
        if isinstance(top,ast.Expr) and isinstance(top.value,ast.Constant) and isinstance(top.value.value,str):
            continue
        if not isinstance(top,(ast.Import,ast.ImportFrom,ast.Assign,ast.AnnAssign,ast.FunctionDef)):
            raise ValueError(f'forbidden top-level policy statement: {type(top).__name__}')
        if isinstance(top,(ast.Assign,ast.AnnAssign)):
            value=top.value
            if isinstance(value,ast.Call):
                raise ValueError('forbidden top-level policy call')
    for node in ast.walk(tree):
        if isinstance(node,ast.Name) and node.id.startswith('__'):
            raise ValueError(f'forbidden policy dunder name: {node.id}')
        if isinstance(node,ast.Attribute) and node.attr.startswith('__'):
            raise ValueError(f'forbidden policy dunder attribute: {node.attr}')
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


def exploration_request_to_wire(q:ExplorationRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,'resource_id':q.resource_id,
        'channel':q.channel,'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }

def publication_request_to_wire(q:PublicationRequest):
    return {
        'id':q.id,'year':q.year,'observation_id':q.observation_id,
        'audience':q.audience,'request_version':q.request_version,
    }

def sponsor_request_to_wire(q:SponsorProjectDecisionRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,'resource_id':q.resource_id,
        'observation_id':q.observation_id,
        'required_fact_keys':list(q.required_fact_keys),
        'required_belief_keys':list(q.required_belief_keys),
        'required_prior_keys':list(q.required_prior_keys),
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }

def sponsor_operator_source_bytes()->bytes:
    return (Path(__file__).resolve().parent/'policies'/'sponsor_operator_v1.py').read_bytes()

def sponsor_operator_contract_hash()->str:
    raw=json.dumps(SPONSOR_OPERATOR_CONTRACT,sort_keys=True,separators=(',',':')).encode()
    return sha256(raw).hexdigest()

def sponsor_operator_policy_version(source:bytes|None=None)->str:
    source=source if source is not None else sponsor_operator_source_bytes()
    h=sha256()
    h.update(source)
    h.update(sponsor_operator_contract_hash().encode())
    return f'{SPONSOR_OPERATOR_POLICY_ID}:{SPONSOR_OPERATOR_SEMANTIC_VERSION}:{h.hexdigest()}'

def public_publisher_source_bytes()->bytes:
    return (Path(__file__).resolve().parent/'policies'/'public_publisher_v1.py').read_bytes()

def public_publisher_contract_hash()->str:
    raw=json.dumps(PUBLIC_PUBLISHER_CONTRACT,sort_keys=True,separators=(',',':')).encode()
    return sha256(raw).hexdigest()

def public_publisher_policy_version(source:bytes|None=None)->str:
    source=source if source is not None else public_publisher_source_bytes()
    h=sha256()
    h.update(source)
    h.update(public_publisher_contract_hash().encode())
    return f'{PUBLIC_PUBLISHER_POLICY_ID}:{PUBLIC_PUBLISHER_SEMANTIC_VERSION}:{h.hexdigest()}'

def public_explorer_source_bytes()->bytes:
    return (Path(__file__).resolve().parent/'policies'/'public_explorer_v1.py').read_bytes()

def public_explorer_contract_hash()->str:
    raw=json.dumps(PUBLIC_EXPLORER_CONTRACT,sort_keys=True,separators=(',',':')).encode()
    return sha256(raw).hexdigest()

def public_explorer_policy_version(source:bytes|None=None)->str:
    source=source if source is not None else public_explorer_source_bytes()
    h=sha256()
    h.update(source)
    h.update(public_explorer_contract_hash().encode())
    return f'{PUBLIC_EXPLORER_POLICY_ID}:{PUBLIC_EXPLORER_SEMANTIC_VERSION}:{h.hexdigest()}'

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
        'policy_id':manifest.policy_id,
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

def run_public_explorer_policy(snapshot:DecisionSnapshot,request:ExplorationRequest,
                               decision_key:str)->PolicyExecutionResult:
    request.validate_protocol()
    source=public_explorer_source_bytes()
    assert_policy_source_safe(source)
    version=public_explorer_policy_version(source)
    contract_hash=public_explorer_contract_hash()

    unknowns=required_unknown_exploration_inputs(request,snapshot)
    decision_id='XDEC-'+sha256(
        ('|'.join((request.id,snapshot.fingerprint(),version,str(decision_key)))).encode()
    ).hexdigest()[:20]

    if unknowns:
        decision=build_exploration_decision(
            decision_id,request,snapshot.agent_id,
            ExplorationDecisionOutcome.BLOCKED_UNKNOWN,
            ExplorationReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted exploration inputs are unknown',
            snapshot,version)
        return PolicyExecutionResult(
            decision,version,'CONTRACT_SHA256:'+contract_hash,
            sha256(('BLOCKED|'+'|'.join(unknowns)).encode()).hexdigest(),
            tuple((f'unknown:{i}',k) for i,k in enumerate(unknowns)),
            'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    payload={
        'mode':'EVALUATE',
        'policy_id':PUBLIC_EXPLORER_POLICY_ID,
        'snapshot':snapshot_to_wire(snapshot),
        'request':exploration_request_to_wire(request),
        'manifest':PUBLIC_EXPLORER_CONTRACT,
        'decision_key':str(decision_key),
    }
    out,worker_fp=_run_worker(payload)
    try:
        outcome=ExplorationDecisionOutcome(out['outcome'])
        reason_code=ExplorationReasonCode(out['reason_code'])
        authorized_cost=out.get('authorized_cost','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('public explorer worker returned invalid decision payload') from e

    decision=build_exploration_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,authorized_cost=authorized_cost)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_public_publisher_policy(snapshot:DecisionSnapshot,request:PublicationRequest,
                                decision_key:str)->PolicyExecutionResult:
    request.validate_protocol()
    source=public_publisher_source_bytes()
    assert_policy_source_safe(source)
    version=public_publisher_policy_version(source)
    contract_hash=public_publisher_contract_hash()
    decision_id='PDEC-'+sha256(
        ('|'.join((request.id,snapshot.fingerprint(),version,str(decision_key)))).encode()
    ).hexdigest()[:20]

    payload={
        'mode':'EVALUATE',
        'policy_id':PUBLIC_PUBLISHER_POLICY_ID,
        'snapshot':snapshot_to_wire(snapshot),
        'request':publication_request_to_wire(request),
        'manifest':PUBLIC_PUBLISHER_CONTRACT,
        'decision_key':str(decision_key),
    }
    out,worker_fp=_run_worker(payload)
    try:
        outcome=PublicationDecisionOutcome(out['outcome'])
        reason_code=PublicationReasonCode(out['reason_code'])
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('public publisher worker returned invalid decision payload') from e

    decision=build_publication_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,snapshot,version)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_operator_policy(snapshot:DecisionSnapshot,
                                request:SponsorProjectDecisionRequest,
                                decision_key:str)->PolicyExecutionResult:
    request.validate_protocol()
    source=sponsor_operator_source_bytes()
    assert_policy_source_safe(source)
    version=sponsor_operator_policy_version(source)
    contract_hash=sponsor_operator_contract_hash()

    unknowns=required_unknown_sponsor_inputs(request,snapshot)
    decision_id='SDEC-'+sha256(
        ('|'.join((request.id,snapshot.fingerprint(),version,str(decision_key)))).encode()
    ).hexdigest()[:20]

    if unknowns:
        decision=build_sponsor_project_decision(
            decision_id,request,snapshot.agent_id,
            SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN,
            SponsorProjectReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted sponsor inputs are unknown',
            snapshot,version)
        return PolicyExecutionResult(
            decision,version,'CONTRACT_SHA256:'+contract_hash,
            sha256(('BLOCKED|'+'|'.join(unknowns)).encode()).hexdigest(),
            tuple((f'unknown:{i}',k) for i,k in enumerate(unknowns)),
            'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

    payload={
        'mode':'EVALUATE',
        'policy_id':SPONSOR_OPERATOR_POLICY_ID,
        'snapshot':snapshot_to_wire(snapshot),
        'request':sponsor_request_to_wire(request),
        'manifest':SPONSOR_OPERATOR_CONTRACT,
        'decision_key':str(decision_key),
    }
    out,worker_fp=_run_worker(payload)
    try:
        outcome=SponsorProjectDecisionOutcome(out['outcome'])
        reason_code=SponsorProjectReasonCode(out['reason_code'])
        requested_financing=out.get('requested_financing','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor operator worker returned invalid decision payload') from e

    decision=build_sponsor_project_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,requested_financing=requested_financing)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)

