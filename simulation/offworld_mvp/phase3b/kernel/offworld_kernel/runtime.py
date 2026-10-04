from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Tuple
from .kernel import InvariantError
from .methodology import MethodologyHardenedBuild4Kernel
from .scheduler import ScheduledEvent, Phase
from .policy import DecisionSnapshot, PolicyContext, build_decision_snapshot
from .provenance import ReplayProvenance

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
        self._handlers: Dict[str,Callable[[MethodologyHardenedBuild4Kernel,ScheduledEvent],Any]]={}
        self._policy_bindings: Dict[str,tuple[str,DecisionSnapshot,str,Callable[[PolicyContext],Any]]]={}
        self._sealed=False
        self._ran=False
        self._initial_fingerprint=None
        self._plan_fingerprint=None
        self._execution_token=None

    def register_handler(self,process_id,handler):
        if self._sealed: raise InvariantError('cannot register handler after runtime seal')
        if process_id in self._handlers: raise InvariantError('duplicate runtime handler')
        if process_id not in self.kernel.scheduler.process_ids:
            raise InvariantError('handler process not registered in scheduler')
        if self.kernel.scheduler.coupling(process_id).phase==Phase.DECISION_WINDOW:
            raise InvariantError('DECISION_WINDOW requires policy handler; kernel-bearing handler forbidden')
        self._handlers[process_id]=handler

    def register_policy_handler(self,event_id,agent_id,snapshot:DecisionSnapshot,decision_key,policy):
        if self._sealed: raise InvariantError('cannot register policy after runtime seal')
        if event_id in self._policy_bindings: raise InvariantError('duplicate policy event binding')
        events={e.event_id:e for e in self.kernel.scheduler.ordered_events()}
        if event_id not in events: raise InvariantError('policy event not scheduled')
        event=events[event_id]
        if event.phase!=Phase.DECISION_WINDOW:
            raise InvariantError('policy handler may bind only DECISION_WINDOW event')
        if agent_id not in self.kernel.agents or snapshot.agent_id!=agent_id:
            raise InvariantError('policy snapshot agent mismatch')
        expected=build_decision_snapshot(
            self.kernel,agent_id,snapshot.period_key,snapshot.effective_time,snapshot.admitted_facts)
        if expected.fingerprint()!=snapshot.fingerprint():
            raise InvariantError('policy snapshot does not match current admitted agent-visible state')
        expected_ref=f'decision-snapshot:{snapshot.period_key}:{snapshot.fingerprint()}'
        if event.snapshot_ref!=expected_ref:
            raise InvariantError('scheduled decision snapshot reference mismatch')
        if self.kernel.scheduler.decision_snapshots.get(snapshot.period_key)!=snapshot.fingerprint():
            raise InvariantError('scheduler decision snapshot not pinned')
        if str(event.effective_time)!=snapshot.effective_time:
            raise InvariantError('policy snapshot effective time mismatch')
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
            context=PolicyContext(snapshot,event.snapshot_ref,decision_key)
            return policy(context)

        handler=self._handlers.get(event.process_id)
        if handler is None: raise InvariantError(f'no handler for process {event.process_id}')
        with self.kernel.scheduled_event_context(event.event_id,self._execution_token):
            result=handler(self.kernel,event)
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
