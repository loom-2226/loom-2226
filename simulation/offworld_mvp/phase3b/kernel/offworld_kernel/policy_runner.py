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
from .operating_protocol import build_operating_cycle_decision, required_unknown_operating_inputs
from .market_protocol import build_sale_decision, required_unknown_sale_inputs
from .distribution_protocol import build_surplus_distribution_decision, required_unknown_surplus_inputs
from .settlement_protocol import build_settlement_support_decision, required_unknown_settlement_inputs
from .transport_protocol import build_transport_settlement_decision, required_unknown_transport_settlement_inputs
from .enterprise import (
    EnterpriseReviewDecisionOutcome, EnterpriseReviewReasonCode, EnterpriseReviewRequest,
    build_enterprise_review_decision, required_unknown_enterprise_review_inputs,
)
from .project_activity import (
    SponsorPortfolioDecisionOutcome, SponsorPortfolioReasonCode,
    SponsorPortfolioDecisionRequest, build_sponsor_portfolio_decision,
    required_unknown_portfolio_inputs,
)
from .project_study import (
    ProjectStudyReviewOutcome, ProjectStudyReviewReasonCode,
    ProjectStudyReviewRequest, build_project_study_review_decision,
    required_unknown_study_review_inputs,
)
from .prospecting import (
    SponsorProspectingOutcome, SponsorProspectingReasonCode,
    SponsorProspectingRequest, build_prospecting_decision,
    required_unknown_prospecting_inputs,
    SponsorOpportunityOutcome, SponsorOpportunityReasonCode,
    SponsorOpportunityRequest, build_sponsor_opportunity_decision,
    required_unknown_sponsor_opportunity_inputs,
)
from .mvp_state import (
    FinancingDecisionOutcome, FinancingReasonCode, FinancingRequest,
    ExplorationDecisionOutcome, ExplorationReasonCode, ExplorationRequest,
    PublicationDecisionOutcome, PublicationReasonCode, PublicationRequest,
    SponsorProjectDecisionOutcome, SponsorProjectReasonCode, SponsorProjectDecisionRequest,
    OperatingCycleDecisionOutcome, OperatingCycleReasonCode, OperatingCycleRequest,
    SaleDecisionOutcome, SaleReasonCode, SaleDecisionRequest,
    SurplusDistributionDecisionOutcome, SurplusDistributionReasonCode, SurplusDistributionRequest,
    SettlementSupportDecisionOutcome, SettlementSupportReasonCode, SettlementSupportRequest,
)
from .transport import (
    TransportSettlementDecisionOutcome, TransportSettlementReasonCode, TransportSettlementRequest,
)
from .policy import DecisionSnapshot
from .policies.manifest import FinancierPolicyManifest, policy_source_bytes
from .policies.public_explorer_v1 import (
    POLICY_CONTRACT as PUBLIC_EXPLORER_CONTRACT,
    POLICY_ID as PUBLIC_EXPLORER_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_EXPLORER_SEMANTIC_VERSION,
)
from .policies.public_surface_prospector_v1 import (
    POLICY_CONTRACT as PUBLIC_SURFACE_PROSPECTOR_CONTRACT,
    POLICY_ID as PUBLIC_SURFACE_PROSPECTOR_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_SURFACE_PROSPECTOR_SEMANTIC_VERSION,
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
from .policies.sponsor_operating_v1 import (
    POLICY_CONTRACT as SPONSOR_OPERATING_CONTRACT,
    POLICY_ID as SPONSOR_OPERATING_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_OPERATING_SEMANTIC_VERSION,
)
from .policies.sponsor_enterprise_review_v1 import (
    POLICY_CONTRACT as SPONSOR_ENTERPRISE_REVIEW_CONTRACT,
    POLICY_ID as SPONSOR_ENTERPRISE_REVIEW_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_ENTERPRISE_REVIEW_SEMANTIC_VERSION,
)
from .policies.sponsor_sale_v1 import (
    POLICY_CONTRACT as SPONSOR_SALE_CONTRACT,
    POLICY_ID as SPONSOR_SALE_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_SALE_SEMANTIC_VERSION,
)
from .policies.sponsor_surplus_v1 import (
    POLICY_CONTRACT as SPONSOR_SURPLUS_CONTRACT,
    POLICY_ID as SPONSOR_SURPLUS_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_SURPLUS_SEMANTIC_VERSION,
)
from .policies.public_settlement_v1 import (
    POLICY_CONTRACT as PUBLIC_SETTLEMENT_CONTRACT,
    POLICY_ID as PUBLIC_SETTLEMENT_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_SETTLEMENT_SEMANTIC_VERSION,
)
from .policies.public_settlement_transport_v1 import (
    POLICY_CONTRACT as PUBLIC_SETTLEMENT_TRANSPORT_CONTRACT,
    POLICY_ID as PUBLIC_SETTLEMENT_TRANSPORT_POLICY_ID,
    SEMANTIC_VERSION as PUBLIC_SETTLEMENT_TRANSPORT_SEMANTIC_VERSION,
)
from .policies.sponsor_portfolio_v1 import (
    POLICY_CONTRACT as SPONSOR_PORTFOLIO_CONTRACT,
    POLICY_ID as SPONSOR_PORTFOLIO_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_PORTFOLIO_SEMANTIC_VERSION,
)
from .policies.sponsor_study_review_v1 import (
    POLICY_CONTRACT as SPONSOR_STUDY_REVIEW_CONTRACT,
    POLICY_ID as SPONSOR_STUDY_REVIEW_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_STUDY_REVIEW_SEMANTIC_VERSION,
)
from .policies.sponsor_prospecting_v1 import (
    POLICY_CONTRACT as SPONSOR_PROSPECTING_CONTRACT,
    POLICY_ID as SPONSOR_PROSPECTING_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_PROSPECTING_SEMANTIC_VERSION,
)
from .policies.sponsor_opportunity_v1 import (
    POLICY_CONTRACT as SPONSOR_OPPORTUNITY_CONTRACT,
    POLICY_ID as SPONSOR_OPPORTUNITY_POLICY_ID,
    SEMANTIC_VERSION as SPONSOR_OPPORTUNITY_SEMANTIC_VERSION,
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
    value={
        'id':q.id,'year':q.year,'project_id':q.project_id,'resource_id':q.resource_id,
        'channel':q.channel,'required_fact_keys':list(q.required_fact_keys),
        'prerequisite_observation_id':q.prerequisite_observation_id,
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }
    if q.request_version=='EXPLORATION_REQUEST_BODY_V1':
        value.update(body_id=q.body_id,question_ref=q.question_ref)
    return value

def publication_request_to_wire(q:PublicationRequest):
    return {
        'id':q.id,'year':q.year,'observation_id':q.observation_id,
        'audience':q.audience,'request_version':q.request_version,
    }

def sponsor_prospecting_request_to_wire(q:SponsorProspectingRequest):
    return {
        'id':q.id,'year':q.year,'actor_id':q.actor_id,
        'opportunity_id':q.opportunity_id,'project_id':q.project_id,
        'body_key':q.body_key,'region_key':q.region_key,'location_id':str(q.location_id),
        'observation_ids':list(q.observation_ids),'belief_keys':list(q.belief_keys),
        'amount':str(q.amount),
        'prospective_information_value':str(q.prospective_information_value),
        'required_fact_keys':list(q.required_fact_keys),
        'request_version':q.request_version,
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

def project_study_review_request_to_wire(q:ProjectStudyReviewRequest):
    return {
        'id':q.id,'project_id':q.project_id,'activity_id':q.activity_id,
        'result_ref':q.result_ref,'required_fact_keys':list(q.required_fact_keys),
        'request_version':q.request_version,
    }

def sponsor_portfolio_request_to_wire(q:SponsorPortfolioDecisionRequest):
    return {
        'id':q.id,'effective_time':str(q.effective_time),
        'candidate_activity_ids':list(q.candidate_activity_ids),
        'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }

def sponsor_opportunity_request_to_wire(q:SponsorOpportunityRequest):
    return {
        'id':q.id,'year':q.year,'actor_id':q.actor_id,
        'existing_project_id':q.existing_project_id,
        'candidates':[{
            'opportunity_id':c.opportunity_id,'body_key':c.body_key,
            'observation_ids':list(c.observation_ids),'belief_keys':list(c.belief_keys),
            'required_capital':str(c.required_capital),
            'commercial_opportunity':str(c.commercial_opportunity),
            'tie_break_key':c.tie_break_key,
        } for c in q.candidates],
        'required_fact_keys':list(q.required_fact_keys),
        'request_version':q.request_version,
    }

def _policy_source_bytes(filename:str)->bytes:
    return (Path(__file__).resolve().parent/'policies'/filename).read_bytes()

def _contract_hash(contract)->str:
    raw=json.dumps(contract,sort_keys=True,separators=(',',':')).encode()
    return sha256(raw).hexdigest()

def _policy_version(policy_id:str,semantic_version:str,contract,filename:str,source:bytes|None=None)->str:
    source=source if source is not None else _policy_source_bytes(filename)
    h=sha256()
    h.update(source)
    h.update(_contract_hash(contract).encode())
    return f'{policy_id}:{semantic_version}:{h.hexdigest()}'

def sponsor_study_review_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_study_review_v1.py')

def sponsor_study_review_contract_hash()->str:
    return _contract_hash(SPONSOR_STUDY_REVIEW_CONTRACT)

def sponsor_study_review_policy_version(source:bytes|None=None)->str:
    return _policy_version(
        SPONSOR_STUDY_REVIEW_POLICY_ID,SPONSOR_STUDY_REVIEW_SEMANTIC_VERSION,
        SPONSOR_STUDY_REVIEW_CONTRACT,'sponsor_study_review_v1.py',source)

def sponsor_portfolio_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_portfolio_v1.py')

def sponsor_portfolio_contract_hash()->str:
    return _contract_hash(SPONSOR_PORTFOLIO_CONTRACT)

def sponsor_portfolio_policy_version(source:bytes|None=None)->str:
    return _policy_version(
        SPONSOR_PORTFOLIO_POLICY_ID,SPONSOR_PORTFOLIO_SEMANTIC_VERSION,
        SPONSOR_PORTFOLIO_CONTRACT,'sponsor_portfolio_v1.py',source)

def sponsor_opportunity_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_opportunity_v1.py')

def sponsor_opportunity_contract_hash()->str:
    return _contract_hash(SPONSOR_OPPORTUNITY_CONTRACT)

def sponsor_opportunity_policy_version(source:bytes|None=None)->str:
    return _policy_version(
        SPONSOR_OPPORTUNITY_POLICY_ID,SPONSOR_OPPORTUNITY_SEMANTIC_VERSION,
        SPONSOR_OPPORTUNITY_CONTRACT,'sponsor_opportunity_v1.py',source)

def sponsor_operator_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_operator_v1.py')

def sponsor_operator_contract_hash()->str:
    return _contract_hash(SPONSOR_OPERATOR_CONTRACT)

def sponsor_operator_policy_version(source:bytes|None=None)->str:
    return _policy_version(SPONSOR_OPERATOR_POLICY_ID,SPONSOR_OPERATOR_SEMANTIC_VERSION,SPONSOR_OPERATOR_CONTRACT,'sponsor_operator_v1.py',source)

def public_surface_prospector_source_bytes()->bytes:
    return _policy_source_bytes('public_surface_prospector_v1.py')

def public_surface_prospector_contract_hash()->str:
    return _contract_hash(PUBLIC_SURFACE_PROSPECTOR_CONTRACT)

def public_surface_prospector_policy_version(source:bytes|None=None)->str:
    return _policy_version(PUBLIC_SURFACE_PROSPECTOR_POLICY_ID,PUBLIC_SURFACE_PROSPECTOR_SEMANTIC_VERSION,PUBLIC_SURFACE_PROSPECTOR_CONTRACT,'public_surface_prospector_v1.py',source)

def operating_request_to_wire(q:OperatingCycleRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,'resource_id':q.resource_id,
        'asset_id':q.asset_id,'observation_id':q.observation_id,
        'required_fact_keys':list(q.required_fact_keys),
        'required_belief_keys':list(q.required_belief_keys),
        'required_prior_keys':list(q.required_prior_keys),
        'currency_unit':q.currency_unit,'quantity_unit':q.quantity_unit,
        'request_version':q.request_version,
    }

def sponsor_operating_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_operating_v1.py')

def sponsor_operating_contract_hash()->str:
    return _contract_hash(SPONSOR_OPERATING_CONTRACT)

def sponsor_operating_policy_version(source:bytes|None=None)->str:
    return _policy_version(SPONSOR_OPERATING_POLICY_ID,SPONSOR_OPERATING_SEMANTIC_VERSION,SPONSOR_OPERATING_CONTRACT,'sponsor_operating_v1.py',source)

def enterprise_review_request_to_wire(q:EnterpriseReviewRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,
        'extraction_event_id':q.extraction_event_id,
        'required_fact_keys':list(q.required_fact_keys),
        'quantity_unit':q.quantity_unit,'request_version':q.request_version,
    }

def sponsor_enterprise_review_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_enterprise_review_v1.py')

def sponsor_enterprise_review_contract_hash()->str:
    return _contract_hash(SPONSOR_ENTERPRISE_REVIEW_CONTRACT)

def sponsor_enterprise_review_policy_version(source:bytes|None=None)->str:
    return _policy_version(
        SPONSOR_ENTERPRISE_REVIEW_POLICY_ID,SPONSOR_ENTERPRISE_REVIEW_SEMANTIC_VERSION,
        SPONSOR_ENTERPRISE_REVIEW_CONTRACT,'sponsor_enterprise_review_v1.py',source)

def sale_request_to_wire(q:SaleDecisionRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,'resource_id':q.resource_id,
        'market_state_id':q.market_state_id,'observation_id':q.observation_id,
        'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'quantity_unit':q.quantity_unit,
        'request_version':q.request_version,
    }

def sponsor_sale_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_sale_v1.py')

def sponsor_sale_contract_hash()->str:
    return _contract_hash(SPONSOR_SALE_CONTRACT)

def sponsor_sale_policy_version(source:bytes|None=None)->str:
    return _policy_version(SPONSOR_SALE_POLICY_ID,SPONSOR_SALE_SEMANTIC_VERSION,SPONSOR_SALE_CONTRACT,'sponsor_sale_v1.py',source)

def surplus_request_to_wire(q:SurplusDistributionRequest):
    return {
        'id':q.id,'year':q.year,'project_id':q.project_id,
        'financing_return_claim_id':q.financing_return_claim_id,
        'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'request_version':q.request_version,
    }

def sponsor_surplus_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_surplus_v1.py')

def sponsor_surplus_contract_hash()->str:
    return _contract_hash(SPONSOR_SURPLUS_CONTRACT)

def sponsor_surplus_policy_version(source:bytes|None=None)->str:
    return _policy_version(SPONSOR_SURPLUS_POLICY_ID,SPONSOR_SURPLUS_SEMANTIC_VERSION,SPONSOR_SURPLUS_CONTRACT,'sponsor_surplus_v1.py',source)

def settlement_request_to_wire(q:SettlementSupportRequest):
    return {
        'id':q.id,'year':q.year,'node_id':q.node_id,
        'support_account_id':q.support_account_id,
        'requested_residents':q.requested_residents,
        'support_cost':str(q.support_cost),
        'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'population_unit':q.population_unit,
        'request_version':q.request_version,
    }

def public_settlement_source_bytes()->bytes:
    return _policy_source_bytes('public_settlement_v1.py')

def public_settlement_contract_hash()->str:
    return _contract_hash(PUBLIC_SETTLEMENT_CONTRACT)

def public_settlement_policy_version(source:bytes|None=None)->str:
    return _policy_version(PUBLIC_SETTLEMENT_POLICY_ID,PUBLIC_SETTLEMENT_SEMANTIC_VERSION,PUBLIC_SETTLEMENT_CONTRACT,'public_settlement_v1.py',source)

def transport_settlement_request_to_wire(q:TransportSettlementRequest):
    return {
        'id':q.id,'departure_time':str(q.departure_time),
        'origin_node_id':q.origin_node_id,'destination_node_id':q.destination_node_id,
        'support_account_id':q.support_account_id,
        'transport_account_id':q.transport_account_id,
        'requested_residents':q.requested_residents,
        'support_cost':str(q.support_cost),
        'transport_relationship_id':q.transport_relationship_id,
        'technology_state_id':q.technology_state_id,
        'required_fact_keys':list(q.required_fact_keys),
        'currency_unit':q.currency_unit,'population_unit':q.population_unit,
        'time_unit':q.time_unit,'request_version':q.request_version,
    }

def public_settlement_transport_source_bytes()->bytes:
    return _policy_source_bytes('public_settlement_transport_v1.py')

def public_settlement_transport_contract_hash()->str:
    return _contract_hash(PUBLIC_SETTLEMENT_TRANSPORT_CONTRACT)

def public_settlement_transport_policy_version(source:bytes|None=None)->str:
    return _policy_version(PUBLIC_SETTLEMENT_TRANSPORT_POLICY_ID,PUBLIC_SETTLEMENT_TRANSPORT_SEMANTIC_VERSION,PUBLIC_SETTLEMENT_TRANSPORT_CONTRACT,'public_settlement_transport_v1.py',source)

def public_publisher_source_bytes()->bytes:
    return _policy_source_bytes('public_publisher_v1.py')

def public_publisher_contract_hash()->str:
    return _contract_hash(PUBLIC_PUBLISHER_CONTRACT)

def public_publisher_policy_version(source:bytes|None=None)->str:
    return _policy_version(PUBLIC_PUBLISHER_POLICY_ID,PUBLIC_PUBLISHER_SEMANTIC_VERSION,PUBLIC_PUBLISHER_CONTRACT,'public_publisher_v1.py',source)

def public_explorer_source_bytes()->bytes:
    return _policy_source_bytes('public_explorer_v1.py')

def public_explorer_contract_hash()->str:
    return _contract_hash(PUBLIC_EXPLORER_CONTRACT)

def public_explorer_policy_version(source:bytes|None=None)->str:
    return _policy_version(PUBLIC_EXPLORER_POLICY_ID,PUBLIC_EXPLORER_SEMANTIC_VERSION,PUBLIC_EXPLORER_CONTRACT,'public_explorer_v1.py',source)

def sponsor_prospecting_source_bytes()->bytes:
    return _policy_source_bytes('sponsor_prospecting_v1.py')

def sponsor_prospecting_contract_hash()->str:
    return _contract_hash(SPONSOR_PROSPECTING_CONTRACT)

def sponsor_prospecting_policy_version(source:bytes|None=None)->str:
    return _policy_version(
        SPONSOR_PROSPECTING_POLICY_ID,SPONSOR_PROSPECTING_SEMANTIC_VERSION,
        SPONSOR_PROSPECTING_CONTRACT,'sponsor_prospecting_v1.py',source)

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


def _policy_identity_context(request,source_fn,version_fn,contract_hash_fn):
    request.validate_protocol()
    source=source_fn()
    assert_policy_source_safe(source)
    return version_fn(source),contract_hash_fn()

def _decision_id(prefix,request,snapshot,version,decision_key):
    material='|'.join((request.id,snapshot.fingerprint(),version,str(decision_key)))
    return prefix+sha256(material.encode()).hexdigest()[:20]

def _run_contract_worker(policy_id,snapshot,request_wire,contract,decision_key):
    return _run_worker({
        'mode':'EVALUATE','policy_id':policy_id,'snapshot':snapshot_to_wire(snapshot),
        'request':request_wire,'manifest':contract,'decision_key':str(decision_key),
    })

def _blocked_contract_result(decision,version,contract_hash,unknowns):
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,
        sha256(('BLOCKED|'+'|'.join(unknowns)).encode()).hexdigest(),
        tuple((f'unknown:{i}',k) for i,k in enumerate(unknowns)),
        'PROTOCOL_UNKNOWN_GATE_NO_WORKER')

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
    version,contract_hash=_policy_identity_context(
        request,public_explorer_source_bytes,public_explorer_policy_version,public_explorer_contract_hash)

    unknowns=required_unknown_exploration_inputs(request,snapshot)
    decision_id=_decision_id('XDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_exploration_decision(
            decision_id,request,snapshot.agent_id,
            ExplorationDecisionOutcome.BLOCKED_UNKNOWN,
            ExplorationReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted exploration inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        PUBLIC_EXPLORER_POLICY_ID,snapshot,exploration_request_to_wire(request),PUBLIC_EXPLORER_CONTRACT,decision_key)
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


def run_public_surface_prospector_policy(snapshot:DecisionSnapshot,request:ExplorationRequest,
                                         decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,public_surface_prospector_source_bytes,public_surface_prospector_policy_version,public_surface_prospector_contract_hash)

    unknowns=required_unknown_exploration_inputs(request,snapshot)
    decision_id=_decision_id('XDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_exploration_decision(
            decision_id,request,snapshot.agent_id,
            ExplorationDecisionOutcome.BLOCKED_UNKNOWN,
            ExplorationReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted surface-prospecting inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        PUBLIC_SURFACE_PROSPECTOR_POLICY_ID,snapshot,exploration_request_to_wire(request),PUBLIC_SURFACE_PROSPECTOR_CONTRACT,decision_key)
    try:
        outcome=ExplorationDecisionOutcome(out['outcome'])
        reason_code=ExplorationReasonCode(out['reason_code'])
        authorized_cost=out.get('authorized_cost','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('public surface prospector worker returned invalid decision payload') from e

    decision=build_exploration_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,authorized_cost=authorized_cost)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_public_publisher_policy(snapshot:DecisionSnapshot,request:PublicationRequest,
                                decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,public_publisher_source_bytes,public_publisher_policy_version,public_publisher_contract_hash)
    decision_id=_decision_id('PDEC-',request,snapshot,version,decision_key)

    out,worker_fp=_run_contract_worker(
        PUBLIC_PUBLISHER_POLICY_ID,snapshot,publication_request_to_wire(request),PUBLIC_PUBLISHER_CONTRACT,decision_key)
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


def run_sponsor_prospecting_policy(snapshot:DecisionSnapshot,
                                   request:SponsorProspectingRequest,
                                   decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_prospecting_source_bytes,sponsor_prospecting_policy_version,
        sponsor_prospecting_contract_hash)
    unknowns=required_unknown_prospecting_inputs(request,snapshot)
    decision_id=_decision_id('PRDEC-',request,snapshot,version,decision_key)
    if unknowns:
        decision=build_prospecting_decision(
            decision_id,request,snapshot,SponsorProspectingOutcome.BLOCKED_UNKNOWN,
            SponsorProspectingReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required prospecting inputs are unknown',version,unknowns)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)
    out,worker_fp=_run_contract_worker(
        SPONSOR_PROSPECTING_POLICY_ID,snapshot,
        sponsor_prospecting_request_to_wire(request),SPONSOR_PROSPECTING_CONTRACT,
        decision_key)
    try:
        outcome=SponsorProspectingOutcome(out['outcome'])
        reason_code=SponsorProspectingReasonCode(out['reason_code'])
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as exc:
        raise RuntimeError('sponsor prospecting worker returned invalid decision payload') from exc
    decision=build_prospecting_decision(
        decision_id,request,snapshot,outcome,reason_code,reason,version)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_opportunity_policy(snapshot:DecisionSnapshot,
                                   request:SponsorOpportunityRequest,
                                   decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_opportunity_source_bytes,sponsor_opportunity_policy_version,
        sponsor_opportunity_contract_hash)
    unknowns=required_unknown_sponsor_opportunity_inputs(request,snapshot)
    decision_id=_decision_id('SODEC-',request,snapshot,version,decision_key)
    if unknowns:
        decision=build_sponsor_opportunity_decision(
            decision_id,request,snapshot,SponsorOpportunityOutcome.BLOCKED_UNKNOWN,
            SponsorOpportunityReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required annual sponsor inputs are unknown',version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)
    out,worker_fp=_run_contract_worker(
        SPONSOR_OPPORTUNITY_POLICY_ID,snapshot,
        sponsor_opportunity_request_to_wire(request),SPONSOR_OPPORTUNITY_CONTRACT,
        decision_key)
    try:
        outcome=SponsorOpportunityOutcome(out['outcome'])
        reason_code=SponsorOpportunityReasonCode(out['reason_code'])
        reason=out['reason']
        selected_opportunity_id=out.get('selected_opportunity_id','')
        selected_body_key=out.get('selected_body_key','')
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as exc:
        raise RuntimeError('sponsor opportunity worker returned invalid decision payload') from exc
    decision=build_sponsor_opportunity_decision(
        decision_id,request,snapshot,outcome,reason_code,reason,version,
        selected_opportunity_id,selected_body_key)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_study_review_policy(snapshot:DecisionSnapshot,
                                    request:ProjectStudyReviewRequest,
                                    decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_study_review_source_bytes,sponsor_study_review_policy_version,
        sponsor_study_review_contract_hash)

    unknowns=required_unknown_study_review_inputs(request,snapshot)
    decision_id=_decision_id('STDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_project_study_review_decision(
            decision_id,request,snapshot.agent_id,
            ProjectStudyReviewOutcome.BLOCKED_UNKNOWN,
            ProjectStudyReviewReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted study-review inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_STUDY_REVIEW_POLICY_ID,snapshot,
        project_study_review_request_to_wire(request),
        SPONSOR_STUDY_REVIEW_CONTRACT,decision_key)
    try:
        outcome=ProjectStudyReviewOutcome(out['outcome'])
        reason_code=ProjectStudyReviewReasonCode(out['reason_code'])
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor study review worker returned invalid decision payload') from e

    decision=build_project_study_review_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_portfolio_policy(snapshot:DecisionSnapshot,
                                 request:SponsorPortfolioDecisionRequest,
                                 decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_portfolio_source_bytes,sponsor_portfolio_policy_version,
        sponsor_portfolio_contract_hash)

    unknowns=required_unknown_portfolio_inputs(request,snapshot)
    decision_id=_decision_id('PFDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_sponsor_portfolio_decision(
            decision_id,request,snapshot.agent_id,
            SponsorPortfolioDecisionOutcome.BLOCKED_UNKNOWN,
            SponsorPortfolioReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted portfolio inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_PORTFOLIO_POLICY_ID,snapshot,
        sponsor_portfolio_request_to_wire(request),
        SPONSOR_PORTFOLIO_CONTRACT,decision_key)
    try:
        outcome=SponsorPortfolioDecisionOutcome(out['outcome'])
        reason_code=SponsorPortfolioReasonCode(out['reason_code'])
        selected_activity_id=out.get('selected_activity_id','')
        reserved_capital=out.get('reserved_capital','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor portfolio worker returned invalid decision payload') from e

    decision=build_sponsor_portfolio_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,selected_activity_id=selected_activity_id,
        reserved_capital=reserved_capital)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_operator_policy(snapshot:DecisionSnapshot,
                                request:SponsorProjectDecisionRequest,
                                decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_operator_source_bytes,sponsor_operator_policy_version,sponsor_operator_contract_hash)

    unknowns=required_unknown_sponsor_inputs(request,snapshot)
    decision_id=_decision_id('SDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_sponsor_project_decision(
            decision_id,request,snapshot.agent_id,
            SponsorProjectDecisionOutcome.BLOCKED_UNKNOWN,
            SponsorProjectReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted sponsor inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_OPERATOR_POLICY_ID,snapshot,sponsor_request_to_wire(request),SPONSOR_OPERATOR_CONTRACT,decision_key)
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


def run_sponsor_operating_policy(snapshot:DecisionSnapshot,
                                 request:OperatingCycleRequest,
                                 decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_operating_source_bytes,sponsor_operating_policy_version,sponsor_operating_contract_hash)

    unknowns=required_unknown_operating_inputs(request,snapshot)
    decision_id=_decision_id('ODEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_operating_cycle_decision(
            decision_id,request,snapshot.agent_id,
            OperatingCycleDecisionOutcome.BLOCKED_UNKNOWN,
            OperatingCycleReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted operating inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_OPERATING_POLICY_ID,snapshot,operating_request_to_wire(request),SPONSOR_OPERATING_CONTRACT,decision_key)
    try:
        outcome=OperatingCycleDecisionOutcome(out['outcome'])
        reason_code=OperatingCycleReasonCode(out['reason_code'])
        requested_financing=out.get('requested_financing','0')
        planned_quantity=out.get('planned_quantity','0')
        authorized_opex=out.get('authorized_opex','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor operating worker returned invalid decision payload') from e

    decision=build_operating_cycle_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,requested_financing=requested_financing,
        planned_quantity=planned_quantity,authorized_opex=authorized_opex)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_enterprise_review_policy(snapshot:DecisionSnapshot,
                                         request:EnterpriseReviewRequest,
                                         decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_enterprise_review_source_bytes,
        sponsor_enterprise_review_policy_version,sponsor_enterprise_review_contract_hash)
    unknowns=required_unknown_enterprise_review_inputs(request,snapshot)
    decision_id=_decision_id('ERDEC-',request,snapshot,version,decision_key)
    if unknowns:
        decision=build_enterprise_review_decision(
            decision_id,request,snapshot.agent_id,
            EnterpriseReviewDecisionOutcome.BLOCKED_UNKNOWN,
            EnterpriseReviewReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted enterprise-review inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)
    out,worker_fp=_run_contract_worker(
        SPONSOR_ENTERPRISE_REVIEW_POLICY_ID,snapshot,enterprise_review_request_to_wire(request),
        SPONSOR_ENTERPRISE_REVIEW_CONTRACT,decision_key)
    try:
        outcome=EnterpriseReviewDecisionOutcome(out['outcome'])
        reason_code=EnterpriseReviewReasonCode(out['reason_code'])
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor enterprise-review worker returned invalid decision payload') from e
    decision=build_enterprise_review_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,snapshot,version)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_sale_policy(snapshot:DecisionSnapshot,
                            request:SaleDecisionRequest,
                            decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_sale_source_bytes,sponsor_sale_policy_version,sponsor_sale_contract_hash)

    unknowns=required_unknown_sale_inputs(request,snapshot)
    decision_id=_decision_id('SDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_sale_decision(
            decision_id,request,snapshot.agent_id,
            SaleDecisionOutcome.BLOCKED_UNKNOWN,
            SaleReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted sale inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_SALE_POLICY_ID,snapshot,sale_request_to_wire(request),SPONSOR_SALE_CONTRACT,decision_key)
    try:
        outcome=SaleDecisionOutcome(out['outcome'])
        reason_code=SaleReasonCode(out['reason_code'])
        offered_quantity=out.get('offered_quantity','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor sale worker returned invalid decision payload') from e

    decision=build_sale_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,offered_quantity=offered_quantity)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_sponsor_surplus_policy(snapshot:DecisionSnapshot,
                               request:SurplusDistributionRequest,
                               decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,sponsor_surplus_source_bytes,sponsor_surplus_policy_version,sponsor_surplus_contract_hash)

    unknowns=required_unknown_surplus_inputs(request,snapshot)
    decision_id=_decision_id('DDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_surplus_distribution_decision(
            decision_id,request,snapshot.agent_id,
            SurplusDistributionDecisionOutcome.BLOCKED_UNKNOWN,
            SurplusDistributionReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted surplus-allocation inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        SPONSOR_SURPLUS_POLICY_ID,snapshot,surplus_request_to_wire(request),SPONSOR_SURPLUS_CONTRACT,decision_key)
    try:
        outcome=SurplusDistributionDecisionOutcome(out['outcome'])
        reason_code=SurplusDistributionReasonCode(out['reason_code'])
        reserve=out.get('reserve','0')
        financier_return=out.get('financier_return','0')
        local_reinvestment=out.get('local_reinvestment','0')
        owner_distribution=out.get('owner_distribution','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('sponsor surplus worker returned invalid decision payload') from e

    decision=build_surplus_distribution_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,reserve=reserve,financier_return=financier_return,
        local_reinvestment=local_reinvestment,owner_distribution=owner_distribution)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)


def run_public_settlement_policy(snapshot:DecisionSnapshot,
                                 request:SettlementSupportRequest,
                                 decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,public_settlement_source_bytes,public_settlement_policy_version,public_settlement_contract_hash)

    unknowns=required_unknown_settlement_inputs(request,snapshot)
    decision_id=_decision_id('SETDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_settlement_support_decision(
            decision_id,request,snapshot.agent_id,
            SettlementSupportDecisionOutcome.BLOCKED_UNKNOWN,
            SettlementSupportReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted settlement-support inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        PUBLIC_SETTLEMENT_POLICY_ID,snapshot,settlement_request_to_wire(request),PUBLIC_SETTLEMENT_CONTRACT,decision_key)
    try:
        outcome=SettlementSupportDecisionOutcome(out['outcome'])
        reason_code=SettlementSupportReasonCode(out['reason_code'])
        residents=int(out.get('authorized_residents',0))
        support=out.get('support_amount','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('public settlement worker returned invalid decision payload') from e

    decision=build_settlement_support_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,authorized_residents=residents,support_amount=support)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)



def run_public_settlement_transport_policy(snapshot:DecisionSnapshot,
                                           request:TransportSettlementRequest,
                                           decision_key:str)->PolicyExecutionResult:
    version,contract_hash=_policy_identity_context(
        request,public_settlement_transport_source_bytes,public_settlement_transport_policy_version,public_settlement_transport_contract_hash)

    unknowns=required_unknown_transport_settlement_inputs(request,snapshot)
    decision_id=_decision_id('TRSETDEC-',request,snapshot,version,decision_key)

    if unknowns:
        decision=build_transport_settlement_decision(
            decision_id,request,snapshot.agent_id,
            TransportSettlementDecisionOutcome.BLOCKED_UNKNOWN,
            TransportSettlementReasonCode.BLOCKED_REQUIRED_INPUT_UNKNOWN,
            'one or more required admitted transport-settlement inputs are unknown',
            snapshot,version)
        return _blocked_contract_result(decision,version,contract_hash,unknowns)

    out,worker_fp=_run_contract_worker(
        PUBLIC_SETTLEMENT_TRANSPORT_POLICY_ID,snapshot,transport_settlement_request_to_wire(request),PUBLIC_SETTLEMENT_TRANSPORT_CONTRACT,decision_key)
    try:
        outcome=TransportSettlementDecisionOutcome(out['outcome'])
        reason_code=TransportSettlementReasonCode(out['reason_code'])
        residents=int(out.get('authorized_residents',0))
        support=out.get('support_amount','0')
        transport=out.get('transport_amount','0')
        relationship_id=out.get('relationship_id','')
        technology_state_id=out.get('technology_state_id','')
        departure_time=out.get('departure_time','0')
        arrival_time=out.get('arrival_time','0')
        reason=out['reason']
        metrics=tuple(sorted((str(k),str(v)) for k,v in out.get('metrics',{}).items()))
    except Exception as e:
        raise RuntimeError('public transport-settlement worker returned invalid decision payload') from e

    decision=build_transport_settlement_decision(
        decision_id,request,snapshot.agent_id,outcome,reason_code,reason,
        snapshot,version,authorized_residents=residents,
        support_amount=support,transport_amount=transport,
        relationship_id=relationship_id,technology_state_id=technology_state_id,
        departure_time=departure_time,arrival_time=arrival_time)
    return PolicyExecutionResult(
        decision,version,'CONTRACT_SHA256:'+contract_hash,worker_fp,metrics)
