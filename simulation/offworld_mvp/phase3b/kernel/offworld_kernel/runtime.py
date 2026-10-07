from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Tuple
from .kernel import InvariantError
from .methodology import MethodologyHardenedBuild4Kernel
from .scheduler import ScheduledEvent, Phase
from .policy import DecisionSnapshot, PolicyContext, build_decision_snapshot, comparison_decision_key
from .provenance import ReplayProvenance

@lru_cache(maxsize=16)
def _verified_git_object(commit, code_hash):
    # Git objects are content addressed. Executable bytes are still rehashed on
    # every runtime construction; only the immutable object comparison is cached.
    from .provenance import verify_commit_code_linkage
    return verify_commit_code_linkage(commit, code_hash)

@dataclass(frozen=True)
class ScheduledRunResult:
    run_mode: str
    scheduler_contract_version: str
    plan_fingerprint: str
    initial_fingerprint: str
    final_fingerprint: str
    execution_log: Tuple[str,...]
    event_results: Tuple[Tuple[str,str],...]
    verification_status: str
    validation_status: str
    repository: str
    git_commit: str
    code_tree_sha256: str
    input_snapshot_ids: Tuple[str,...]
    parameter_manifest_ids: Tuple[str,...]
    table_manifest_ids: Tuple[str,...]
    policy_manifest_ids: Tuple[str,...]
    commit_code_linkage: str
    provenance_fingerprint: str
    execution_fingerprint: str
    result_fingerprint: str

class ScheduledSimulationRuntime:
    """Only supported execution entrypoint for sealed MVP simulation runs.

    Initialization/build fixtures may mutate the kernel before seal(). After seal(),
    all guarded kernel mutations require this runtime's private scheduled-event token.
    """
    runtime_version='PHASE3B_SCHEDULED_RUNTIME_0_1'

    def __init__(self,kernel:MethodologyHardenedBuild4Kernel,provenance:ReplayProvenance|None=None):
        if kernel.strict_scheduled_execution:
            raise InvariantError('kernel already sealed by another scheduled runtime')
        self.kernel=kernel
        self.provenance=(provenance or ReplayProvenance.from_kernel(kernel)).validate()
        if kernel.boundary_manifest is not None:
            from .provenance import source_tree_hash,verify_commit_code_linkage
            actual=source_tree_hash()
            if self.provenance.code_tree_sha256!=actual:raise InvariantError('BLOCKED_PROVENANCE: executable source mismatch')
            _verified_git_object(self.provenance.git_commit,actual)
        self._handlers: Dict[str,Callable[[MethodologyHardenedBuild4Kernel,ScheduledEvent],Any]]={}
        self._policy_bindings: Dict[str,tuple[str,DecisionSnapshot,str,Callable[[PolicyContext],Any]]]={}
        self._sealed=False
        self._ran=False
        self._initial_fingerprint=None
        self._plan_fingerprint=None
        self._execution_token=None
        self._strict_system_bindings={}
        self._strict_policy_bindings={}
        self._strict_emitted_decisions={}

    def register_handler(self,process_id,handler,*,admission_receipts=(),decision_refs=(),transition_methods=()):
        if self._sealed: raise InvariantError('cannot register handler after runtime seal')
        if process_id in self._handlers: raise InvariantError('duplicate runtime handler')
        if process_id not in self.kernel.scheduler.process_ids:
            raise InvariantError('handler process not registered in scheduler')
        if self.kernel.scheduler.coupling(process_id).phase==Phase.DECISION_WINDOW:
            raise InvariantError('DECISION_WINDOW requires policy handler; kernel-bearing handler forbidden')
        if self.kernel.boundary_manifest is not None:
            from .boundary import verify_receipt
            spec=self.kernel.scheduler.coupling(process_id)
            owner=self.kernel.systems.get(process_id)
            allowed=dict(self.kernel.boundary_manifest.allowed_transitions).get(process_id,())
            if owner is None or not set(spec.owned_state)<=set(owner.owned_state_refs) or not set(spec.write_set)<=set(owner.owned_state_refs):
                raise InvariantError('BLOCKED_AUTHORIZATION: SYSTEM state ownership')
            if not admission_receipts or tuple(transition_methods)!=tuple(allowed):
                raise InvariantError('BLOCKED_DECLARATION: SYSTEM consumption/transitions missing')
            required={concept for consumer,concept,_ in self.kernel.boundary_manifest.source_resolver_bindings if consumer==process_id}
            if not required<={r.consumption_request.concept for r in admission_receipts}:raise InvariantError('BLOCKED_DECLARATION: SYSTEM scoped inputs missing')
            for r in admission_receipts:
                q=r.consumption_request
                if q.concept not in spec.read_set:raise InvariantError('BLOCKED_AUTHORIZATION: input absent from coupling read set')
                if q.consumer_id!=process_id or q.perspective!='WORLD_SIM' or q.use!='SYSTEM_TRANSITION':
                    raise InvariantError('BLOCKED_PERSPECTIVE: SYSTEM receipt')
                if verify_receipt(self.kernel,r).value_state.value!='KNOWN':
                    raise InvariantError('BLOCKED_ADMISSION: SYSTEM requires KNOWN inputs')
            event_ids={e.event_id for e in self.kernel.scheduler.ordered_events() if e.phase==Phase.DECISION_WINDOW}
            if any(r not in self.kernel.causal_artifacts and r not in event_ids for r in decision_refs):raise InvariantError('BLOCKED_LINEAGE: decision missing')
            self._strict_system_bindings[process_id]=(tuple(admission_receipts),tuple(decision_refs),spec)
        self._handlers[process_id]=handler

    def register_policy_handler(self,event_id,agent_id,snapshot:DecisionSnapshot,decision_key,policy,*,request=None,admission_receipts=(),expected_policy_version=None):
        if self._sealed: raise InvariantError('cannot register policy after runtime seal')
        if event_id in self._policy_bindings: raise InvariantError('duplicate policy event binding')
        events={e.event_id:e for e in self.kernel.scheduler.ordered_events()}
        if event_id not in events: raise InvariantError('policy event not scheduled')
        event=events[event_id]
        if event.phase!=Phase.DECISION_WINDOW:
            raise InvariantError('policy handler may bind only DECISION_WINDOW event')
        if agent_id not in self.kernel.agents or snapshot.agent_id!=agent_id:
            raise InvariantError('policy snapshot agent mismatch')
        blocked=bool(self.kernel.boundary_manifest is not None and any(r.state.value=='BLOCKED' for r in admission_receipts))
        if blocked:
            from .boundary import verify_receipt
            for r in admission_receipts:verify_receipt(self.kernel,r)
            expected=snapshot  # unconsumed claim; never reaches an Agent worker
        else:
            expected=build_decision_snapshot(
                self.kernel,agent_id,snapshot.period_key,snapshot.effective_time,snapshot.admitted_facts,admission_receipts=admission_receipts)
        if expected.fingerprint()!=snapshot.fingerprint():
            raise InvariantError('policy snapshot does not match current admitted agent-visible state')
        expected_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
        if event.snapshot_ref!=expected_ref:
            raise InvariantError('scheduled decision snapshot reference mismatch')
        if self.kernel.scheduler.decision_snapshots.get(snapshot.period_key)!=snapshot.fingerprint():
            raise InvariantError('scheduler decision snapshot not pinned')
        if str(event.effective_time)!=snapshot.effective_time:
            raise InvariantError('policy snapshot effective time mismatch')
        if self.kernel.boundary_manifest is not None:
            from .causal_trace import canonical
            if request is None or not expected_policy_version:raise InvariantError('BLOCKED_DECLARATION: policy request/version missing')
            request.validate_protocol();canonical(request)
            self._strict_policy_bindings[event_id]=(request,tuple(admission_receipts),expected_policy_version)
        self._policy_bindings[event_id]=(agent_id,snapshot,str(decision_key),policy)

    def seal(self):
        if self._sealed: raise InvariantError('runtime already sealed')
        missing=[]
        for e in self.kernel.scheduler.ordered_events():
            if e.phase==Phase.DECISION_WINDOW:
                if e.event_id not in self._policy_bindings: missing.append(f'policy:{e.event_id}')
            elif e.process_id not in self._handlers:
                missing.append(f'handler:{e.process_id}')
        if missing: raise InvariantError(f'missing scheduled handlers: {sorted(set(missing))}')
        if self.kernel.boundary_manifest is not None and not self.kernel._boundary_opening_validated:
            from .boundary import validate_opening
            validate_opening(self.kernel)
            self.kernel._boundary_opening_validated=True
        if self.kernel.boundary_manifest is not None and self.kernel.boundary_manifest.contract_version=='BUILD6E_NAMED_WORLD_V1':
            from decimal import Decimal
            opening=Decimal(self.kernel.boundary_manifest.parameter('opening_effective_time'))
            for assertion in self.kernel.boundary_manifest.assertions:
                if assertion.time_basis=='SIM_TIME':
                    available=Decimal(assertion.available_from)
                elif assertion.time_basis=='CALENDAR_YEAR' and self.kernel.boundary_manifest.clock_mapping_ref=='SIM_YEAR_PLUS_2025_V1':
                    available=Decimal(assertion.available_from)-Decimal('2025')
                else:
                    raise InvariantError('BLOCKED_TIME: opening input clock basis is unmapped')
                if available>opening:
                    raise InvariantError('BLOCKED_TIME: opening input unavailable at GENESIS')
            if any(Decimal(str(e.effective_time))<opening for e in self.kernel.scheduler.ordered_events()):
                raise InvariantError('BLOCKED_TIME: event precedes 6E opening')
        if self.kernel.boundary_manifest is not None:self._validate_boundary_provenance()
        self._plan_fingerprint=self.kernel.scheduler.plan_fingerprint()
        self._initial_fingerprint=self.kernel.methodology_fingerprint()
        self._execution_token=self.kernel.seal_for_scheduled_execution(
            self._initial_fingerprint,self._plan_fingerprint)
        self._sealed=True
        return self._initial_fingerprint,self._plan_fingerprint

    def _dispatch(self,event):
        if event.phase==Phase.DECISION_WINDOW:
            binding=self._policy_bindings.get(event.event_id)
            if binding is None: raise InvariantError(f'no policy binding for event {event.event_id}')
            agent_id,snapshot,decision_key,policy=binding
            if event.snapshot_ref!=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}':
                raise InvariantError('decision event snapshot drift')
            if self.kernel.boundary_manifest is None:
                return policy(PolicyContext(snapshot,event.snapshot_ref,decision_key))
            from .boundary import validate_snapshot,verify_receipt
            from .causal_trace import archive
            from .policy_runner import PolicyExecutionResult
            request,receipts,version=self._strict_policy_bindings[event.event_id]
            prior=self.kernel._boundary_projection()
            inputs=tuple(verify_receipt(self.kernel,r) for r in receipts)
            if any(v.value_state.value=='BLOCKED' for v in inputs):
                qref=archive(self.kernel.causal_artifacts,'REQUEST',request)
                self.kernel._boundary_emit(event,'POLICY_ATTEMPT',prior,prior,'BLOCKED_ADMISSION',receipts=receipts,request_refs=(qref,),artifacts=(('UNCONSUMED_SNAPSHOT_CLAIM',snapshot),),decision_time=str(event.effective_time),reason_code='BLOCKED_ADMISSION')
                return 'BLOCKED_ADMISSION'
            validate_snapshot(self.kernel,agent_id,snapshot.period_key,snapshot.effective_time,snapshot.admitted_facts,receipts)
            opaque_key=comparison_decision_key(self.kernel.boundary_manifest.comparison_parameters,agent_id,snapshot.period_key,decision_key)
            self.kernel._boundary_random_keys.append(json.dumps(['LOOM_COMPARISON_RANDOM_V1','POLICY',opaque_key],separators=(',',':')))
            result=policy(PolicyContext(snapshot,event.snapshot_ref,opaque_key))
            if self.kernel._boundary_projection()!=prior:
                self.kernel._boundary_invalid=True
                raise InvariantError('INVALID_RUN: policy changed domain state')
            if not isinstance(result,PolicyExecutionResult) or result.policy_version!=version:
                raise InvariantError('BLOCKED_LINEAGE: typed policy result/version')
            d=result.decision;d.validate_protocol(request)
            actual_actor=getattr(d,'actor_id',getattr(d,'financier_id',None))
            if actual_actor!=agent_id or d.request_id!=request.id or getattr(d,'snapshot_ref',getattr(d,'input_snapshot_ref',None))!=event.snapshot_ref or d.policy_version!=version:
                raise InvariantError('BLOCKED_LINEAGE: decision/snapshot/request/actor')
            qref=archive(self.kernel.causal_artifacts,'REQUEST',request)
            dref=archive(self.kernel.causal_artifacts,'DECISION',result)
            # These existing typed outcomes sanction their associated action.
            # A later scheduled realization keeps this authorization coordinate;
            # it does not infer authorization from the consequence timestamp.
            sanctions_action=d.outcome.value in ('AUTHORIZE','APPROVE','PUBLISH','REQUEST_FINANCE','DEVELOP','ABANDON','OPERATE','OFFER','DISTRIBUTE','CONTINUE','CLOSE')
            self.kernel._boundary_decisions[dref]=(str(event.effective_time),d.id,str(event.effective_time) if sanctions_action else None)
            self._strict_emitted_decisions[event.event_id]=dref
            self.kernel._boundary_emit(event,'POLICY_EVALUATION',prior,prior,d.outcome.value,receipts=receipts,request_refs=(qref,),decision_refs=(dref,),artifacts=(('DECISION_STATE',snapshot),('INFORMATION_STATE',inputs)),decision_time=str(event.effective_time),rule_refs=('POLICY_RULE:'+version,),reason_code=d.reason_code.value)
            return result

        handler=self._handlers.get(event.process_id)
        if handler is None: raise InvariantError(f'no handler for process {event.process_id}')
        if self.kernel.boundary_manifest is None:
            with self.kernel.scheduled_event_context(event.event_id,self._execution_token):
                return handler(self.kernel,event)
        from .boundary import verify_receipt
        from .causal_trace import state_delta
        receipts,decisions,spec=self._strict_system_bindings[event.process_id]
        if spec!=self.kernel.scheduler.coupling(event.process_id):raise InvariantError('BLOCKED_AUTHORIZATION: coupling drift')
        decisions=tuple(self._strict_emitted_decisions.get(ref,ref) for ref in decisions)
        if any(ref not in self.kernel.causal_artifacts for ref in decisions):raise InvariantError('BLOCKED_LINEAGE: decision not realized')
        values=tuple(verify_receipt(self.kernel,r) for r in receipts)
        if any(v.value_state.value!='KNOWN' for v in values):raise InvariantError('BLOCKED_ADMISSION: SYSTEM input')
        if any(r.consumption_request.effective_time!=str(event.effective_time) for r in receipts):raise InvariantError('BLOCKED_TIME: SYSTEM receipt')
        prior=self.kernel._boundary_projection();self.kernel._boundary_event_deltas=[]
        self.kernel._boundary_event_context=(event,receipts,decisions)
        self.kernel._boundary_consumed_values=values
        try:
            with self.kernel.scheduled_event_context(event.event_id,self._execution_token):
                result=handler(self.kernel,event)
        finally:
            self.kernel._boundary_event_context=None
            self.kernel._boundary_consumed_values=()
        following=self.kernel._boundary_projection()
        # Apply only recorded outer deltas to the audit projection. Any raw write
        # or read-method side effect makes this exact reconciliation fail.
        projected={(d,p):v for d,p,v in prior}
        for delta in self.kernel._boundary_event_deltas:
            for domain,path,before,after in delta:
                root=path.split('.')[1] if path.startswith('state.') else path.split('.')[0]
                root={'fcf_events':'fcf','event_log':'events'}.get(root,root)
                if root!='_seq' and root not in spec.write_set:
                    self.kernel._boundary_invalid=True
                    raise InvariantError('INVALID_RUN: transition changed undeclared owned state '+root)
                if projected.get((domain,path))!=before:raise InvariantError('INVALID_RUN: uncovered prior state')
                if after is None:projected.pop((domain,path),None)
                else:projected[(domain,path)]=after
        if tuple(sorted((d,p,v) for (d,p),v in projected.items()))!=following or self.kernel._boundary_invalid:
            self.kernel._boundary_invalid=True
            raise InvariantError('INVALID_RUN: untraced raw domain mutation')
        self.kernel._boundary_emit(event,'SYSTEM_TRANSITION',following,following,result,decision_refs=decisions,artifacts=(('ADMITTED_INFORMATION',receipts),('INFORMATION_ARTIFACT',values)),source_values=values,authorization_time=self.kernel._boundary_decisions[decisions[0]][2] if decisions else None,decision_time=self.kernel._boundary_decisions[decisions[0]][0] if decisions else None)
        return result

    def run(self):
        if not self._sealed: raise InvariantError('scheduled runtime must be sealed before run')
        if self._ran: raise InvariantError('scheduled runtime is single-use')
        if self.kernel.methodology_fingerprint()!=self._initial_fingerprint:
            raise InvariantError('sealed kernel state changed before scheduled run')
        if self.kernel.scheduler.plan_fingerprint()!=self._plan_fingerprint:
            raise InvariantError('sealed scheduler plan changed before scheduled run')

        raw=self.kernel.scheduler.run(self._dispatch)

        if self.kernel.scheduler.plan_fingerprint()!=self._plan_fingerprint:
            raise InvariantError('scheduler plan mutated during scheduled run')
        self.kernel.assert_methodology_invariants()
        self._ran=True
        final_fp=self.kernel.methodology_fingerprint()
        event_results=tuple((eid,str(result)) for eid,result in zip(self.kernel.scheduler.execution_log,raw))
        execution_payload={
          'execution_log':tuple(self.kernel.scheduler.execution_log),
          'event_results':event_results,
          'final_fingerprint':final_fp}
        execution_fp=sha256(json.dumps(execution_payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        provenance_fp=self.provenance.fingerprint()
        payload={
          'runtime_version':self.runtime_version,
          'run_mode':'SCHEDULED_MVP',
          'scheduler_contract_version':self.kernel.scheduler.contract_version,
          'plan_fingerprint':self._plan_fingerprint,
          'initial_fingerprint':self._initial_fingerprint,
          'final_fingerprint':final_fp,
          'execution_fingerprint':execution_fp,
          'repository':self.provenance.repository,
          'git_commit':self.provenance.git_commit,
          'code_tree_sha256':self.provenance.code_tree_sha256,
          'input_snapshot_ids':self.provenance.input_snapshot_ids,
          'parameter_manifest_ids':self.provenance.parameter_manifest_ids,
          'table_manifest_ids':self.provenance.table_manifest_ids,
          'policy_manifest_ids':self.provenance.policy_manifest_ids,
          'commit_code_linkage':self.provenance.commit_code_linkage,
          'provenance_fingerprint':provenance_fp,
          'verification_status':'SCHEDULED_EXECUTION_VERIFIED',
          'validation_status':'NOT_EMPIRICALLY_VALIDATED'}
        result_fp=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        result=ScheduledRunResult(
            'SCHEDULED_MVP',self.kernel.scheduler.contract_version,self._plan_fingerprint,
            self._initial_fingerprint,final_fp,tuple(self.kernel.scheduler.execution_log),
            event_results,'SCHEDULED_EXECUTION_VERIFIED','NOT_EMPIRICALLY_VALIDATED',
            self.provenance.repository,self.provenance.git_commit,self.provenance.code_tree_sha256,
            self.provenance.input_snapshot_ids,self.provenance.parameter_manifest_ids,
            self.provenance.table_manifest_ids,self.provenance.policy_manifest_ids,
            self.provenance.commit_code_linkage,provenance_fp,execution_fp,result_fp)
        if self.kernel.active_decision_epoch_id is not None:
            self.kernel.complete_decision_epoch(self._execution_token,result)
        return result


    def _validate_boundary_provenance(self):
        from pathlib import Path
        from .boundary import BUILD6E_AUTHORIZATION, BUILD6E_CONTRACT, AUTHORIZATION, CONTRACT
        m=self.kernel.boundary_manifest;root=Path(__file__).resolve().parents[5]
        is6e=(m.contract_version,m.authorization_ref)==(BUILD6E_CONTRACT,BUILD6E_AUTHORIZATION)
        if (m.contract_version,m.authorization_ref) not in ((CONTRACT,AUTHORIZATION),(BUILD6E_CONTRACT,BUILD6E_AUTHORIZATION)):
            raise InvariantError('BLOCKED_PROVENANCE: unknown closed contract')
        required={'BOUNDARY_SHA256':m.fingerprint(),'EARTH_SLICE_SHA256':m.earth_slice_ref[1],
                  'COMPARISON_CONFIG_SHA256':m.comparison_spec_ref[1],'QUALIFICATION_PROTOCOL_SHA256':m.qualification_protocol_ref[1]}
        build7_profile=is6e and dict(m.parameters).get('build7.profile')=='BUILD7_GENERATED_CAMPAIGN_V1'
        seen_harness=set()
        for ref,digest in m.harness_refs:
            path=(root/ref).resolve()
            if not path.is_relative_to(root) or sha256(path.read_bytes()).hexdigest()!=digest:
                raise InvariantError('BLOCKED_PROVENANCE: qualification harness bytes')
            if is6e:
                expected={
                    'simulation/offworld_mvp/build6e/qualification/build6e_fixture.py':'QUALIFICATION_FIXTURE_SHA256',
                    'simulation/offworld_mvp/build6e/named_world.py':'NAMED_WORLD_COMPILER_SHA256',
                    'src/loom_world_authority/store.py':'WORLD_AUTHORITY_STORE_SHA256',
                }
                if build7_profile:
                    expected['simulation/offworld_mvp/build7/generated_campaign.py']='BUILD7_CAMPAIGN_SHA256'
                else:
                    expected['simulation/offworld_mvp/build6e/qualification/qualify_build6e.py']='QUALIFICATION_DRIVER_SHA256'
                rel=path.relative_to(root).as_posix()
                if rel not in expected or rel in seen_harness:raise InvariantError('BLOCKED_PROVENANCE: undeclared 6E harness/module')
                seen_harness.add(rel);required[expected[rel]]=digest
            elif path.name=='qualify_build6d.py':required['QUALIFICATION_DRIVER_SHA256']=digest
            elif path.name=='build6d_fixture.py':required['QUALIFICATION_FIXTURE_SHA256']=digest
            else:raise InvariantError('BLOCKED_PROVENANCE: undeclared harness kind')
        if is6e and len(seen_harness)!=4:raise InvariantError('BLOCKED_PROVENANCE: incomplete 6E module inventory')
        if not is6e and len(required)!=6:raise InvariantError('BLOCKED_PROVENANCE: harness descriptors absent')
        labels={}
        for entry in self.provenance.table_manifest_ids:
            key,_,value=entry.partition(':')
            if key in labels:raise InvariantError('BLOCKED_PROVENANCE: duplicate identity label')
            labels[key]=value
        if any(labels.get(key)!=value for key,value in required.items()):raise InvariantError('BLOCKED_PROVENANCE: strict manifest labels')
        if build7_profile:
            build7_inputs=root/'simulation/offworld_mvp/build7/inputs'
            build6e_inputs=root/'simulation/offworld_mvp/build6e/inputs'
            refs=tuple((build7_inputs,ref,digest) for ref,digest in (*m.scenario_definition_refs,m.qualification_protocol_ref)) + ((build6e_inputs,m.earth_slice_ref[0],m.earth_slice_ref[1]),)
            for inputs,ref,digest in refs:
                path=(inputs/ref).resolve()
                if not path.is_relative_to(inputs) or sha256(path.read_bytes()).hexdigest()!=digest:
                    raise InvariantError('BLOCKED_PROVENANCE: input/protocol bytes')
        else:
            inputs=root/('simulation/offworld_mvp/build6e/inputs' if is6e else 'simulation/offworld_mvp/build6/inputs')
            for ref,digest in (*m.scenario_definition_refs,m.earth_slice_ref,m.qualification_protocol_ref):
                path=(inputs/ref).resolve()
                if not path.is_relative_to(inputs) or sha256(path.read_bytes()).hexdigest()!=digest:
                    raise InvariantError('BLOCKED_PROVENANCE: input/protocol bytes')
