from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Tuple
from .kernel import InvariantError
from .methodology import MethodologyHardenedBuild4Kernel
from .scheduler import ScheduledEvent

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
    result_fingerprint: str

class ScheduledSimulationRuntime:
    """Only supported execution entrypoint for sealed MVP simulation runs.

    Initialization/build fixtures may mutate the kernel before seal(). After seal(),
    all guarded kernel mutations require this runtime's private scheduled-event token.
    """
    runtime_version='PHASE3B_SCHEDULED_RUNTIME_0_1'

    def __init__(self,kernel:MethodologyHardenedBuild4Kernel):
        if kernel.strict_scheduled_execution:
            raise InvariantError('kernel already sealed by another scheduled runtime')
        self.kernel=kernel
        self._handlers: Dict[str,Callable[[MethodologyHardenedBuild4Kernel,ScheduledEvent],Any]]={}
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
        self._handlers[process_id]=handler

    def seal(self):
        if self._sealed: raise InvariantError('runtime already sealed')
        event_processes={e.process_id for e in self.kernel.scheduler.ordered_events()}
        missing=sorted(event_processes-set(self._handlers))
        if missing: raise InvariantError(f'missing scheduled handlers: {missing}')
        self._plan_fingerprint=self.kernel.scheduler.plan_fingerprint()
        self._initial_fingerprint=self.kernel.methodology_fingerprint()
        self._execution_token=self.kernel.seal_for_scheduled_execution(
            self._initial_fingerprint,self._plan_fingerprint)
        self._sealed=True
        return self._initial_fingerprint,self._plan_fingerprint

    def _dispatch(self,event):
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
        payload={
          'runtime_version':self.runtime_version,
          'run_mode':'SCHEDULED_MVP',
          'scheduler_contract_version':self.kernel.scheduler.contract_version,
          'plan_fingerprint':self._plan_fingerprint,
          'initial_fingerprint':self._initial_fingerprint,
          'final_fingerprint':final_fp,
          'execution_log':tuple(self.kernel.scheduler.execution_log),
          'event_results':event_results,
          'verification_status':'SCHEDULED_EXECUTION_VERIFIED',
          'validation_status':'NOT_EMPIRICALLY_VALIDATED'}
        result_fp=sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return ScheduledRunResult(
            'SCHEDULED_MVP',self.kernel.scheduler.contract_version,self._plan_fingerprint,
            self._initial_fingerprint,final_fp,tuple(self.kernel.scheduler.execution_log),
            event_results,'SCHEDULED_EXECUTION_VERIFIED','NOT_EMPIRICALLY_VALIDATED',result_fp)
