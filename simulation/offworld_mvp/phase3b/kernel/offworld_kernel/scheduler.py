from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import IntEnum
from hashlib import sha256
import json
from typing import Any, Callable, Dict, Iterable, List, Tuple
from .kernel import InvariantError
from .mvp_state import RuntimeObjectClass

D=Decimal

class Phase(IntEnum):
    OPEN_PERIOD=10
    EXOGENOUS_INPUTS=20
    OBSERVATION=30
    INFORMATION_UPDATE=40
    DECISION_WINDOW=50
    ACTION_VALIDATION=60
    COMMITMENT_DISBURSEMENT=70
    OPERATIONS=80
    MARKET_CLEARING=90
    ACCOUNTING_CLOSE=100
    DEPRECIATION_AMORTIZATION=110
    CONSERVATION_CHECK=120
    SNAPSHOT_CLOSE=130

@dataclass(frozen=True)
class ScheduledEvent:
    event_id: str
    effective_time: D
    phase: Phase
    priority: int
    stable_key: str
    process_id: str
    payload: Tuple[Tuple[str,str],...]=()
    parent_ids: Tuple[str,...]=()

    @property
    def order_key(self):
        return (self.effective_time,int(self.phase),self.priority,self.stable_key,self.event_id)

@dataclass(frozen=True)
class CouplingSpec:
    process_id: str
    version: str
    runtime_class: RuntimeObjectClass
    owned_state: Tuple[str,...]
    read_set: Tuple[str,...]
    write_set: Tuple[str,...]
    cadence_or_trigger: str
    phase: Phase
    unit_basis: Tuple[Tuple[str,str],...]=()
    world_context: str='REALIZED'
    perspective: str='WORLD_SIM'
    direction: str='ONE_WAY'
    transition_interfaces: Tuple[str,...]=()

    def validate(self):
        if self.runtime_class==RuntimeObjectClass.AGENT:
            raise InvariantError('scheduler process contract must represent SYSTEM/AGGREGATE mechanism, not autonomous agent policy')
        if self.direction not in {'ONE_WAY','TWO_WAY'}:
            raise InvariantError('invalid coupling direction')
        unauthorized=set(self.write_set)-set(self.owned_state)-set(self.transition_interfaces)
        if unauthorized:
            raise InvariantError(f'coupling writes unowned state: {sorted(unauthorized)}')

@dataclass
class DeterministicScheduler:
    contract_version: str='PHASE3B_SCHEDULER_0_1'
    _events: Dict[str,ScheduledEvent]=field(default_factory=dict)
    _couplings: Dict[str,CouplingSpec]=field(default_factory=dict)
    execution_log: List[str]=field(default_factory=list)

    def register_coupling(self,spec:CouplingSpec):
        spec.validate()
        if spec.process_id in self._couplings:
            raise InvariantError('duplicate coupling process')
        self._couplings[spec.process_id]=spec

    def schedule(self,event:ScheduledEvent):
        if event.event_id in self._events:
            raise InvariantError('duplicate scheduled event')
        if event.process_id not in self._couplings:
            raise InvariantError('unregistered scheduler process')
        if event.phase!=self._couplings[event.process_id].phase:
            raise InvariantError('event phase differs from coupling contract')
        self._events[event.event_id]=event

    def ordered_events(self)->List[ScheduledEvent]:
        return sorted(self._events.values(),key=lambda e:e.order_key)

    def run(self,handler:Callable[[ScheduledEvent],Any])->List[Any]:
        out=[]
        self.execution_log=[]
        for e in self.ordered_events():
            out.append(handler(e))
            self.execution_log.append(e.event_id)
        return out

    def fingerprint(self)->str:
        payload={
          'contract_version':self.contract_version,
          'couplings':sorted((s.process_id,s.version,s.runtime_class.value,s.owned_state,s.read_set,s.write_set,s.cadence_or_trigger,int(s.phase),s.unit_basis,s.world_context,s.perspective,s.direction,s.transition_interfaces) for s in self._couplings.values()),
          'events':[(e.event_id,str(e.effective_time),int(e.phase),e.priority,e.stable_key,e.process_id,e.payload,e.parent_ids) for e in self.ordered_events()],
          'execution_log':tuple(self.execution_log)}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
