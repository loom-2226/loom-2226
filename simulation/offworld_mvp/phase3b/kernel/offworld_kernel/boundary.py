"""Build 6D checked projections/admission over the existing kernel.

Four immutable contracts, fixed resolvers and one narrow Earth source reader.
No parallel world state, authority service, ontology, or financial ledger.
"""
from __future__ import annotations
from dataclasses import dataclass, fields, replace
from decimal import Decimal as D
from hashlib import sha256
import json
from pathlib import Path
import re
from .kernel import InvariantError
from .policy import FactState, SnapshotFact
from .causal_trace import canonical, content_hash

CONTRACT='BUILD6D_CORE_FRD_CLOSURE_V1'
AUTHORIZATION='BUILD6D_IMPLEMENTATION_AUTHORIZATION_001_CORE_FRD_CLOSURE'
CONTEXTS=('REAL','SCENARIO','REALIZED')
PERSPECTIVES=('GOVERNANCE','WORLD_SIM','AGENT')
ADMISSION_STATES=('ADMITTED','CANDIDATE','HOLD','REJECTED','QUARANTINED')
RESOURCE_CONCEPTS=('R_IN_SITU','R_ACCESSIBLE','R_RECOVERABLE','R_RESERVE')


def _immutable(x):
    if isinstance(x,(str,int,bool,D,FactState)) or x is None:return
    if isinstance(x,tuple):
        for v in x:_immutable(v)
        return
    if isinstance(x,(ContextValue,ConsumptionRequest,AdmissionReceipt)):
        for f in fields(x):_immutable(getattr(x,f.name))
        return
    raise InvariantError('boundary contract contains mutable/unsupported data')


def _time(x):
    try:v=D(x)
    except Exception as e:raise InvariantError('BLOCKED_DECLARATION: invalid time') from e
    if not v.is_finite() or v<0:raise InvariantError('BLOCKED_DECLARATION: invalid time')
    return v


@dataclass(frozen=True, slots=True)
class ConsumptionRequest:
    request_id: str
    consumer_id: str
    use: str
    subject_id: str
    concept: str
    scope: str
    time_basis: str
    effective_time: str
    knowledge_cutoff: str
    world_context: str
    context_id: str
    perspective: str
    perspective_actor_id: str
    assertion_set: str
    required_unit: str
    required_role: str

    def __post_init__(self):
        for f in fields(self):
            if f.name not in ('context_id','perspective_actor_id') and not getattr(self,f.name):
                raise InvariantError(f'BLOCKED_DECLARATION: {f.name}')
        if self.world_context not in CONTEXTS or self.perspective not in PERSPECTIVES:
            raise InvariantError('BLOCKED_CONTEXT: unknown context/perspective')
        if bool(self.context_id)!=(self.world_context!='REAL'):
            raise InvariantError('BLOCKED_CONTEXT: context identity required only outside REAL')
        if self.perspective=='AGENT' and self.perspective_actor_id!=self.consumer_id:
            raise InvariantError('BLOCKED_PERSPECTIVE: consumer/Agent mismatch')
        if self.assertion_set not in ('ADMITTED','ALL_RECORDED') or self.time_basis not in ('SIM_TIME','CALENDAR_YEAR'):
            raise InvariantError('BLOCKED_DECLARATION: assertion set/time basis')
        if _time(self.knowledge_cutoff)>_time(self.effective_time):
            raise InvariantError('BLOCKED_TIME: knowledge cutoff after use')


@dataclass(frozen=True, slots=True)
class ContextValue:
    assertion_id: str
    subject_id: str
    concept: str
    scope: str
    world_context: str
    context_id: str
    perspective: str
    perspective_actor_id: str
    value_state: FactState
    value: str|None
    unit: str
    reason_code: str
    proposition_kind: str
    proposition_role: str
    epistemic_mode: str
    admission_state: str
    uncertainty_state: str
    uncertainty_ref: str
    valid_from: str
    valid_to: str
    time_basis: str
    available_from: str
    source_refs: tuple[str,...]
    source_hashes: tuple[str,...]
    warrant_refs: tuple[str,...]
    support_conflict_refs: tuple[str,...]
    dependency_refs: tuple[str,...]
    transformation_ref: str
    transformation_version: str
    authorization_ref: str
    reference_role: str
    exception_flags: tuple[tuple[str,str],...]
    record_version: str
    source_time: str

    def __post_init__(self):
        _immutable(tuple(getattr(self,f.name) for f in fields(self)))
        if self.value_state not in tuple(FactState) or (self.value_state==FactState.KNOWN)!=(self.value is not None):
            raise InvariantError('UNKNOWN/BLOCKED cannot carry a numerical/default payload')
        if self.world_context not in CONTEXTS or self.perspective not in PERSPECTIVES or self.admission_state not in ADMISSION_STATES:
            raise InvariantError('invalid source context/standing')
        if bool(self.context_id)!=(self.world_context!='REAL'):
            raise InvariantError('invalid source context identity')
        if not all((self.assertion_id,self.subject_id,self.concept,self.scope,self.unit,self.proposition_kind,self.proposition_role,self.epistemic_mode,self.uncertainty_state,self.authorization_ref,self.record_version)):
            raise InvariantError('source provenance incomplete')
        if len(self.source_refs)!=len(self.source_hashes) or not self.source_refs:
            raise InvariantError('source/hash binding incomplete')
        if _time(self.valid_from)>_time(self.valid_to):
            raise InvariantError('invalid source validity')
        _time(self.available_from);_time(self.source_time)

    def fingerprint(self):return content_hash(self)


@dataclass(frozen=True, slots=True)
class AdmissionReceipt:
    receipt_id: str
    consumption_request: ConsumptionRequest
    source_assertion_refs: tuple[tuple[str,str],...]
    transformation_refs: tuple[tuple[str,str],...]
    decision_snapshot_ref: str
    resolved_value_hash: str
    state: FactState
    reason_code: str
    dependency_receipt_refs: tuple[str,...]
    consumer_contract_ref: str
    consumer_contract_version: str
    receipt_version: str

    def digest(self):
        return content_hash(tuple((f.name,getattr(self,f.name)) for f in fields(self) if f.name!='receipt_id'))

    def __post_init__(self):
        _immutable(tuple(getattr(self,f.name) for f in fields(self)))
        if self.receipt_id and self.receipt_id!='receipt:'+self.digest():
            raise InvariantError('BLOCKED_LINEAGE: forged receipt')


@dataclass(frozen=True, slots=True)
class BoundaryManifest:
    contract_version: str
    input_snapshot_id: str
    scenario_id: str
    scenario_version: str
    run_id: str
    scenario_definition_refs: tuple[tuple[str,str],...]
    real_source_refs: tuple[tuple[str,str],...]
    opening_state_hash: str
    parameter_manifest_refs: tuple[tuple[str,str],...]
    allowed_use_contracts: tuple[tuple[str,...],...]
    source_resolver_bindings: tuple[tuple[str,str,str],...]
    comparison_spec_ref: tuple[str,str]
    earth_slice_ref: tuple[str,str]
    qualification_protocol_ref: tuple[str,str]
    clock_mapping_ref: str
    schema_version: str
    authorization_ref: str
    assertions: tuple[ContextValue,...]
    parameters: tuple[tuple[str,str],...]
    comparison_parameters: tuple[tuple[str,str],...]
    allowed_transitions: tuple[tuple[str,tuple[str,...]],...]
    opening_bindings: tuple[tuple[str,str],...]
    harness_refs: tuple[tuple[str,str],...]

    def __post_init__(self):
        for f in fields(self):_immutable(getattr(self,f.name))
        if self.contract_version!=CONTRACT or self.authorization_ref!=AUTHORIZATION:
            raise InvariantError('BLOCKED_AUTHORIZATION: strict contract/authorization missing')
        if self.clock_mapping_ref!='SIM_YEAR_PLUS_2025_V1':
            raise InvariantError('BLOCKED_TIME: unregistered clock mapping')
        if not all((self.input_snapshot_id,self.scenario_id,self.scenario_version,self.run_id,self.opening_state_hash,self.schema_version)):
            raise InvariantError('boundary identity missing')
        for values in (self.parameters,self.comparison_parameters,self.allowed_transitions,self.harness_refs):
            if len({r[0] for r in values})!=len(values):raise InvariantError('duplicate boundary binding')
        if len({a.assertion_id for a in self.assertions})!=len(self.assertions):raise InvariantError('duplicate assertion identity')
        if any(len(c)!=8 for c in self.allowed_use_contracts):raise InvariantError('invalid use-contract shape')
        required=('world_seed','policy_seed','comparison_group','key_schema','algorithm','decimal_precision','decimal_rounding')
        if not all(k in dict(self.comparison_parameters) for k in required):raise InvariantError('BLOCKED_PARAMETER: comparison metadata missing')
        if dict(self.comparison_parameters)['world_seed']==dict(self.comparison_parameters)['policy_seed']:
            raise InvariantError('WORLD/POLICY seeds must be independently declared')
        for ref in (*self.scenario_definition_refs,*self.real_source_refs,*self.parameter_manifest_refs,self.comparison_spec_ref,self.earth_slice_ref,self.qualification_protocol_ref,*self.harness_refs):
            if len(ref)!=2 or not ref[0] or not re.fullmatch('[0-9a-f]{64}',ref[1]):raise InvariantError('invalid immutable input identity')

    def parameter(self,key):
        params=dict(self.parameters)
        if key not in params:raise InvariantError(f'BLOCKED_PARAMETER: {key}')
        return params[key]

    def fingerprint(self):return content_hash(self)


def _value(kernel, req, value, *, kind, mode, source, role=None, state=FactState.KNOWN, reason='ADMITTED', dependencies=(), available='0', source_time=None):
    """Only fixed live resolvers use this; authored/REAL sources retain full metadata."""
    return ContextValue('live:'+content_hash((source,value,req.consumer_id)),req.subject_id,req.concept,req.scope,
        req.world_context,req.context_id,req.perspective,req.perspective_actor_id,state,value,req.required_unit,reason,
        kind,role or req.required_role,mode,'ADMITTED','UNCHARACTERIZED','NOT_SUPPLIED','0','20','SIM_TIME',available,
        (source,),(content_hash((source,value)),),('EXISTING_TYPED_RECORD',),(),dependencies,'','',kernel.boundary_manifest.authorization_ref,
        'NOT_EARTH_REFERENCE',(('uncertainty','NOT_SUPPLIED'),),'CONTEXT_VALUE_V1',source_time or available)


def _outcome(kernel,req,state,reason,parents=()):
    return _value(kernel,req,None,kind='USE_EVALUATION',mode='USE_EVALUATION',source='use:'+req.request_id,state=state,reason=reason,dependencies=tuple(a.assertion_id for a in parents))


def _validate_request(kernel,req):
    m=kernel.boundary_manifest
    if m is None:raise InvariantError('BLOCKED_CONTRACT: strict manifest absent')
    if req.world_context=='SCENARIO' and req.context_id!=m.scenario_id:raise InvariantError('BLOCKED_CONTEXT: wrong scenario')
    if req.world_context=='REALIZED' and req.context_id!=m.run_id:raise InvariantError('BLOCKED_CONTEXT: wrong run')
    contract=(req.consumer_id,req.use,req.concept,req.scope,req.world_context,req.perspective,req.required_unit,req.required_role)
    if contract not in m.allowed_use_contracts:raise InvariantError('BLOCKED_SCOPE: undeclared natural use contract')
    if req.perspective=='AGENT':
        if req.consumer_id not in kernel.agents:raise InvariantError('BLOCKED_PERSPECTIVE: Agent missing')
    elif req.consumer_id not in kernel.systems and req.consumer_id!='GENESIS':
        raise InvariantError('BLOCKED_PERSPECTIVE: governed SYSTEM missing')
    if req.perspective=='AGENT' and req.concept in RESOURCE_CONCEPTS:
        raise InvariantError('BLOCKED_PERSPECTIVE: physical truth is not Agent evidence')


def _check_source(req,a):
    if (a.subject_id,a.concept,a.scope,a.world_context,a.context_id)!=(req.subject_id,req.concept,req.scope,req.world_context,req.context_id):
        return 'BLOCKED_SCOPE'
    if a.unit!=req.required_unit or a.proposition_role!=req.required_role:return 'BLOCKED_UNIT_ROLE'
    if a.time_basis!=req.time_basis:return 'BLOCKED_TIME_BASIS'
    if not _time(a.valid_from)<=_time(req.effective_time)<=_time(a.valid_to) or _time(a.available_from)>_time(req.knowledge_cutoff):return 'BLOCKED_TIME'
    if a.admission_state!='ADMITTED':return 'BLOCKED_ADMISSION:'+a.admission_state
    if req.perspective=='AGENT' and (a.perspective!='AGENT' or a.perspective_actor_id!=req.consumer_id):return 'BLOCKED_POSSESSION'
    return ''


def query_context(kernel,request):
    _validate_request(kernel,request);m=kernel.boundary_manifest
    recorded=tuple(a for a in m.assertions if a.subject_id==request.subject_id and a.concept==request.concept and a.world_context==request.world_context and a.context_id==request.context_id)
    if recorded:
        if any(a.scope!=request.scope for a in recorded):return _outcome(kernel,request,FactState.BLOCKED,'BLOCKED_SCOPE',recorded)
        relevant=tuple(a for a in recorded if request.perspective!='AGENT' or a.perspective_actor_id==request.consumer_id)
        if not relevant:return _outcome(kernel,request,FactState.BLOCKED,'BLOCKED_POSSESSION',recorded)
        if len({a.value for a in relevant if a.value_state==FactState.KNOWN})>1 or any(a.support_conflict_refs for a in relevant):
            return _outcome(kernel,request,FactState.BLOCKED,'CONFLICT_REVIEW_REQUIRED',relevant)
        reasons=tuple(_check_source(request,a) for a in relevant)
        admitted=tuple(a for a,r in zip(relevant,reasons) if not r)
        if not admitted:return _outcome(kernel,request,FactState.BLOCKED,next((r for r in reasons if r),'BLOCKED_ADMISSION'),relevant)
        return admitted[0]
    if request.world_context=='REAL':
        return _outcome(kernel,request,FactState.UNKNOWN,'NO_APPLICABLE_ASSERTION')
    if request.world_context=='SCENARIO':
        return _outcome(kernel,request,FactState.UNKNOWN,'NO_AUTHORED_ASSERTION')
    return _resolve_live(kernel,request)


def _resolve_live(k,r):
    bindings={(consumer,concept):selector for consumer,concept,selector in k.boundary_manifest.source_resolver_bindings}
    selector=bindings.get((r.consumer_id,r.concept))
    if selector is None:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
    if selector=='AGENT_STATE':
        if r.subject_id!=r.consumer_id or r.perspective!='AGENT':return _outcome(k,r,FactState.BLOCKED,'BLOCKED_PERSPECTIVE')
        a=k.agents[r.consumer_id];acct=k.state.accounts.get(a.account_id)
        if acct is None:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        value=canonical((acct,a))
        return _value(k,r,value,kind='AGENT_VISIBLE_STATE',mode='ADMITTED_INFORMATION',source='agent:'+a.id)
    if selector in ('BELIEF','PRIOR'):
        if r.subject_id!=r.consumer_id:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        key=dict(k.boundary_manifest.parameters).get('belief_key.'+r.consumer_id)
        if key is None:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_PARAMETER')
        values=getattr(k.agents[r.consumer_id],'beliefs' if selector=='BELIEF' else 'priors')
        if key not in values:return _outcome(k,r,FactState.UNKNOWN,'MISSING_'+selector)
        return _value(k,r,str(values[key]),kind='BELIEF' if selector=='BELIEF' else 'AGENT_PRIOR',mode='BELIEF' if selector=='BELIEF' else 'AUTHORED_AGENT_PRIOR',source=selector+':'+r.consumer_id+':'+key)
    if selector=='OBSERVATION':
        obs=k.observations.get(r.subject_id)
        if obs is None:return _outcome(k,r,FactState.UNKNOWN,'MISSING_OBSERVATION')
        if obs.resource_id!=k.boundary_manifest.parameter('resource_id'):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SCOPE')
        if D(obs.year)>D(r.knowledge_cutoff):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_TIME')
        if r.perspective=='AGENT' and obs.id not in k.agents[r.consumer_id].information:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        return _value(k,r,obs.signal,kind='OBSERVATION',mode='OBSERVATION',source='observation:'+obs.id,available=str(obs.year),source_time=str(obs.year))
    if selector=='PUBLIC_INFORMATION':
        artifact=k.public_information.get(r.subject_id)
        if artifact is None:return _outcome(k,r,FactState.UNKNOWN,'MISSING_INFORMATION_ARTIFACT')
        if r.perspective=='AGENT' and (artifact.id not in k.agents[r.consumer_id].information or artifact.source_observation_id not in k.agents[r.consumer_id].information):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        if D(artifact.year)>D(r.knowledge_cutoff):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_TIME')
        return _value(k,r,canonical(artifact),kind='INFORMATION_ARTIFACT',mode='INFORMATION_ARTIFACT',source='publication:'+artifact.id,available=str(artifact.year))
    if selector=='RESOURCE':
        if r.perspective=='AGENT':return _outcome(k,r,FactState.BLOCKED,'BLOCKED_PERSPECTIVE')
        res=k.resources.get(r.subject_id)
        if res is None:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        if r.concept=='R_RESERVE':return _outcome(k,r,FactState.UNKNOWN,'NO_GOVERNED_RESERVE_CONVERSION')
        depletion=res.recoverable-res.remaining
        value={'R_IN_SITU':res.in_situ-depletion,'R_ACCESSIBLE':res.accessible-depletion,'R_RECOVERABLE':res.remaining}[r.concept]
        return _value(k,r,str(value),kind='PHYSICAL_STATE',mode='SIMULATION_RESULT',source=f'resource:{res.id}:{r.concept}')
    # Fixed field adapters. Binding strings are never eval/getattr traversal paths.
    parts=selector.split(':');tag=parts[0]
    if tag=='PROJECT' and len(parts)==3:
        p=k.state.projects.get(parts[1])
        if p is None or r.subject_id!=p.id:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SCOPE')
        if r.perspective=='AGENT' and r.consumer_id not in p.owners:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        if parts[2]=='STATUS':value=p.status
        elif parts[2]=='CASH':value=str(k.state.accounts[p.cash_account_id].balance)
        else:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        return _value(k,r,value,kind='PHYSICAL_STATE' if parts[2]=='STATUS' else 'FINANCIAL_STATE',mode='SIMULATION_RESULT',source=selector)
    if tag=='ASSET' and len(parts)==3 and parts[2]=='CAPACITY':
        a=k.state.assets.get(parts[1])
        if a is None:return _outcome(k,r,FactState.UNKNOWN,'MISSING_ASSET')
        if r.subject_id!=a.project_id or (r.perspective=='AGENT' and r.consumer_id not in k.state.projects[a.project_id].owners):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        return _value(k,r,str(a.capacity),kind='PHYSICAL_STATE',mode='SIMULATION_RESULT',source=selector)
    if tag=='COLONY' and len(parts)==2:
        colony=k.colonies.get(r.subject_id)
        if colony is None:return _outcome(k,r,FactState.BLOCKED,'MISSING_DECLARED_COLONY')
        key=parts[1]
        if key=='STAGE':value=colony.stage
        elif key=='HEADROOM':value=str(max(0,colony.habitat_capacity-colony.population))
        elif key=='INVENTORY':value=str(colony.resource_inventory)
        else:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        return _value(k,r,value,kind='PHYSICAL_STATE',mode='SIMULATION_RESULT',source=selector+':'+r.subject_id)
    if selector=='POPULATION':
        if k.population is None:return _outcome(k,r,FactState.BLOCKED,'MISSING_COHORT')
        return _value(k,r,str(k.population.earth),kind='PHYSICAL_STATE',mode='SIMULATION_RESULT',source='population:EARTH_COHORT')
    if selector=='CLAIM':
        claim=k.financing_return_claims.get(r.subject_id)
        if claim is None:return _outcome(k,r,FactState.BLOCKED,'MISSING_CLAIM')
        return _value(k,r,str(k.financing_return_remaining(claim.id)),kind='FINANCIAL_STATE',mode='SIMULATION_RESULT',source='claim:'+claim.id)
    if selector in ('EXTRACTION_PLANNED','EXTRACTION_ACTUAL'):
        rec=next((x for x in k.extraction_resolution_records if x.extraction_event_id==r.subject_id),None)
        if rec is None:return _outcome(k,r,FactState.UNKNOWN,'MISSING_REALIZED_EVENT')
        if D(rec.year)>D(r.knowledge_cutoff):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_TIME')
        if r.perspective=='AGENT' and (r.consumer_id not in k.state.projects[rec.project_id].owners or rec.extraction_event_id not in k.agents[r.consumer_id].history):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_POSSESSION')
        value=rec.planned_quantity if selector=='EXTRACTION_PLANNED' else rec.actual_extracted
        return _value(k,r,str(value),kind='REALIZED_EVENT',mode='ADMITTED_INFORMATION',source='extraction:'+rec.extraction_event_id,available=str(rec.year))
    if selector.startswith('MARKET:'):
        env=k.market_envelopes.get(r.subject_id)
        if env is None or D(env.year)>D(r.effective_time):return _outcome(k,r,FactState.BLOCKED,'BLOCKED_TIME')
        if selector=='MARKET:PRICE':value=str(env.unit_price)
        elif selector=='MARKET:DEMAND':value=str(k.market_remaining_demand(env.id))
        else:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        return _value(k,r,value,kind='EXOGENOUS_MARKET_INPUT',mode='AUTHORED_SCENARIO',source='market:'+env.id,available='0',source_time='0')
    if selector.startswith('TRANSPORT:'):
        rel=k.transport_relationships.get(k.boundary_manifest.parameter('transport_relationship_id'))
        tech=k.technology_capability_states.get(k.boundary_manifest.parameter('technology_state_id'))
        if rel is None or tech is None:return _outcome(k,r,FactState.UNKNOWN,'MISSING_TRANSPORT_INPUT')
        key=selector.split(':')[1]
        q=k.transport_qualification(tech.id,rel.id,D(r.effective_time))
        values={'AVAILABLE':'TRUE' if q.available else 'FALSE','RELATIONSHIP_ID':rel.id,'STATE_ID':tech.id,
                'CAPACITY':str(rel.capacity),'COST_PER_PASSENGER':str(rel.cost_per_passenger),'TRAVEL_TIME':str(rel.travel_time),
                'ENERGY_PER_PASSENGER':str(rel.energy_per_passenger),'LOSS_RISK':str(rel.loss_risk)}
        if key not in values:return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')
        return _value(k,r,values[key],kind='EXOGENOUS_CAPABILITY_INPUT',mode='AUTHORED_SCENARIO',source='transport:'+rel.id+':'+tech.id,available=str(rel.effective_from),source_time=str(rel.effective_from))
    return _outcome(k,r,FactState.BLOCKED,'BLOCKED_SOURCE_BINDING')


def admit_for_use(kernel,request):
    v=query_context(kernel,request)
    receipt=AdmissionReceipt('',request,((v.assertion_id,v.fingerprint()),),
        ((v.transformation_ref,content_hash((v.transformation_ref,v.transformation_version))),) if v.transformation_ref else (),
        '',v.fingerprint(),v.value_state,v.reason_code,(),CONTRACT,CONTRACT,'ADMISSION_RECEIPT_V1')
    return v,replace(receipt,receipt_id='receipt:'+receipt.digest())


def verify_receipt(kernel,receipt):
    if receipt.receipt_id!='receipt:'+receipt.digest():raise InvariantError('BLOCKED_LINEAGE: forged receipt')
    v,expected=admit_for_use(kernel,receipt.consumption_request)
    if expected!=receipt:raise InvariantError('BLOCKED_LINEAGE: stale/forged receipt binding')
    return v


def snapshot_facts(kernel,receipts):
    facts=[]
    for receipt in receipts:
        v=verify_receipt(kernel,receipt)
        if v.value_state==FactState.BLOCKED:raise InvariantError('BLOCKED_ADMISSION:'+v.reason_code)
        if receipt.consumption_request.use!='POLICY':raise InvariantError('BLOCKED_USE: receipt is not a policy input')
        if v.concept not in ('agent.STATE','agent.BELIEF','agent.PRIOR','observation.SIGNAL','information.ARTIFACT'):
            # Worker receives a stable minimal key, never a world/source digest.
            facts.append(SnapshotFact(v.concept,v.value_state,v.value,'admitted:'+v.concept))
    return tuple(facts)


def validate_snapshot(kernel,agent_id,period,effective_time,facts,receipts):
    if not receipts:raise InvariantError('BLOCKED_DECLARATION: strict snapshot receipts missing')
    required={'agent.STATE','agent.BELIEF','agent.PRIOR'}
    concepts=set()
    for r in receipts:
        q=r.consumption_request
        if q.consumer_id!=agent_id or q.perspective!='AGENT' or q.effective_time!=str(effective_time):raise InvariantError('BLOCKED_CONTEXT_TIME: snapshot receipt mismatch')
        concepts.add(q.concept);verify_receipt(kernel,r)
    if not required<=concepts:raise InvariantError('BLOCKED_DECLARATION: Agent state/prior/belief receipts missing')
    resolved=snapshot_facts(kernel,receipts)
    if tuple(sorted(facts,key=lambda f:f.key))!=tuple(sorted(resolved,key=lambda f:f.key)):raise InvariantError('BLOCKED_LINEAGE: unverified raw fact')


def validate_opening(kernel):
    m=kernel.boundary_manifest
    if kernel.run_identity.code_contract!=CONTRACT or kernel.run_identity.input_snapshot_id!=m.input_snapshot_id:
        raise InvariantError('BLOCKED_CONTRACT: run identity/manifest mismatch')
    if kernel.observations or kernel.state.transactions or kernel.events or kernel.public_information:
        raise InvariantError('BLOCKED_GENESIS: pre-epoch causal activity')
    for selector,expected in m.opening_bindings:
        actual=kernel._boundary_opening_value(selector)
        if canonical(actual)!=expected:raise InvariantError('BLOCKED_GENESIS: opening binding '+selector)
    if content_hash(kernel._boundary_projection())!=m.opening_state_hash:raise InvariantError('BLOCKED_GENESIS: opening state hash')
    if D(m.parameter('S'))<=0 or not D('0')<=D(m.parameter('f'))<=D('1') or D(m.parameter('lambda'))<0:
        raise InvariantError('BLOCKED_PARAMETER: bridge domain')
    if kernel.lambda_displacement!=D(m.parameter('lambda')):raise InvariantError('BLOCKED_PARAMETER: displacement mismatch')
    for a in kernel.agents.values():
        key=m.parameter('belief_key.'+a.id)
        if key not in a.beliefs or key not in a.priors:raise InvariantError('BLOCKED_PARAMETER: opening prior/belief missing')
    for resource in kernel.resources.values():
        if not D('0')<=resource.remaining<=resource.recoverable<=resource.accessible<=resource.in_situ:raise InvariantError('BLOCKED_RESOURCE_HIERARCHY')
    if kernel.population is None:raise InvariantError('BLOCKED_GENESIS: finite cohort missing')
    if kernel.population.earth>D(m.parameter('reference_population_bound')):raise InvariantError('BLOCKED_GENESIS: source population bound')


def load_earth_assertions(path, *, parent_root, verify_parents=True):
    """One selected, offline, byte-pinned source format; no Earth engine coupling."""
    raw=Path(path).read_bytes();doc=json.loads(raw,parse_float=D)
    if doc['schema']!='BUILD6D_EARTH_REFERENCE_SLICE_V1' or doc['iso3']!='USA':raise InvariantError('BLOCKED_REFERENCE: slice schema/economy')
    if doc['adoption_manifest_sha256']!='9934d0ac9f6cbb43d1da91a777ef462a6ae63c9a262bf10592685a8830d20aa2':raise InvariantError('BLOCKED_REFERENCE: adopted parent')
    source_lines={}
    for source in doc['sources']:
        if verify_parents:
            b=(Path(parent_root)/source['artifact']).read_bytes()
            if len(b)!=source['byte_size'] or sha256(b).hexdigest()!=source['sha256']:raise InvariantError('BLOCKED_REFERENCE: whole-source hash')
            source_lines[source['artifact']]=b.splitlines()
        elif not doc.get('extraction_attestation_sha256'):
            raise InvariantError('BLOCKED_REFERENCE: offline extraction attestation absent')
    seen=set();values=[]
    for row in doc['rows']:
        year=row['year'];artifact=row['artifact'];expected_stage='stage_2026_2031/' if year<=2030 else 'stage_2031_2060/'
        if year in seen or year not in range(2026,2047) or not artifact.startswith(expected_stage):raise InvariantError('BLOCKED_REFERENCE: duplicate/temporal source')
        seen.add(year)
        if verify_parents:
            line=source_lines[artifact][row['line_number']-1]
            if sha256(line).hexdigest()!=row['row_sha256']:raise InvariantError('BLOCKED_REFERENCE: row membership hash')
            parent=json.loads(line,parse_float=D)
            if parent['iso3']!='USA' or parent['year']!=year:raise InvariantError('BLOCKED_REFERENCE: row selector')
            for concept in ('investment','population'):
                match=re.search(r'"'+concept+r'"\s*:\s*([-+0-9.eE]+)',line.decode())
                if match is None or match.group(1)!=row['scalar_lexemes'][concept] or D(row[concept])!=parent[concept]:raise InvariantError('BLOCKED_REFERENCE: scalar/source mismatch')
        source=next(x for x in doc['sources'] if x['artifact']==artifact)
        for concept,unit in (('investment','EARTH_REAL_PROXY_INVESTMENT_PER_YEAR'),('population','PERSON')):
            values.append(ContextValue(f'USA:{year}:{concept}','USA',concept,'COUNTRY:USA','REAL','','GOVERNANCE','',FactState.KNOWN,row[concept],unit,'ADMITTED',
                'MODEL_PROJECTION','EARTH_REFERENCE','MODEL_PROJECTION','ADMITTED','UNCHARACTERIZED','NOT_SUPPLIED',str(year),str(year),'CALENDAR_YEAR','2026',
                (artifact,f'row:{row["line_number"]}',doc['reference_snapshot_id']),(source['sha256'],row['row_sha256'],doc['adoption_manifest_sha256']),
                ('ADOPTED_EARTH_REFERENCE',),(),(),'','',AUTHORIZATION,'ADOPTED_REFERENCE',tuple(sorted(row['exception_flags'].items())),'CONTEXT_VALUE_V1',str(year)))
    if seen!=set(range(2026,2047)):raise InvariantError('BLOCKED_REFERENCE: missing coverage row')
    return tuple(values),sha256(raw).hexdigest()
