from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable, Tuple
from .kernel import InvariantError
from .mvp_state import AgentState

D=Decimal

class FactState(str,Enum):
    KNOWN='KNOWN'
    UNKNOWN='UNKNOWN'
    BLOCKED='BLOCKED'

@dataclass(frozen=True, slots=True)
class SnapshotFact:
    key: str
    state: FactState
    value: str|None=None
    source_ref: str=''

    def __post_init__(self):
        if self.state!=FactState.KNOWN and self.value is not None:
            raise InvariantError('UNKNOWN/BLOCKED snapshot fact may not carry value')
        if self.state==FactState.KNOWN and self.value is None:
            raise InvariantError('KNOWN snapshot fact requires value')

@dataclass(frozen=True, slots=True)
class DecisionSnapshot:
    agent_id: str
    agent_kind: str
    node_id: str
    period_key: str
    effective_time: str
    account_balance: D
    capabilities: Tuple[str,...]
    objectives: Tuple[str,...]
    information_refs: Tuple[str,...]
    beliefs: Tuple[Tuple[str,D],...]
    priors: Tuple[Tuple[str,D],...]
    asset_refs: Tuple[str,...]
    resource_holdings: Tuple[Tuple[str,D],...]
    claim_holdings: Tuple[Tuple[str,D],...]
    admitted_facts: Tuple[SnapshotFact,...]=()

    def fingerprint(self)->str:
        payload={
          'agent_id':self.agent_id,'agent_kind':self.agent_kind,'node_id':self.node_id,
          'period_key':self.period_key,'effective_time':self.effective_time,
          'account_balance':str(self.account_balance),
          'capabilities':self.capabilities,'objectives':self.objectives,
          'information_refs':self.information_refs,
          'beliefs':tuple((k,str(v)) for k,v in self.beliefs),
          'priors':tuple((k,str(v)) for k,v in self.priors),
          'asset_refs':self.asset_refs,
          'resource_holdings':tuple((k,str(v)) for k,v in self.resource_holdings),
          'claim_holdings':tuple((k,str(v)) for k,v in self.claim_holdings),
          'admitted_facts':tuple((f.key,f.state.value,f.value,f.source_ref) for f in self.admitted_facts)}
        return sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def _comparison_draw(coordinates):
    """Shared strict conversion; coordinates are framed, not delimiter joined."""
    from decimal import getcontext
    ctx=getcontext()
    if ctx.prec!=28 or str(ctx.rounding)!='ROUND_HALF_EVEN':
        raise InvariantError('BLOCKED_PARAMETER: decimal replay environment')
    raw=json.dumps(coordinates,separators=(',',':'),ensure_ascii=True)
    return D(int.from_bytes(sha256(raw.encode()).digest()[:8],'big'))/D(2**64)

@dataclass(frozen=True, slots=True)
class PolicyContext:
    snapshot: DecisionSnapshot
    snapshot_ref: str
    decision_key: str

    def deterministic_draw(self,label:str)->D:
        if self.decision_key.startswith('LOOM_COMPARISON_RANDOM_V1:'):
            return _comparison_draw(['LOOM_COMPARISON_RANDOM_V1','POLICY',self.decision_key,str(label)])
        else:
            raw='|'.join((self.decision_key,self.snapshot.fingerprint(),str(label)))
        n=int.from_bytes(sha256(raw.encode()).digest()[:8],'big')
        return D(n)/D(2**64)

def build_decision_snapshot(kernel,agent_id,period_key,effective_time,admitted_facts:Iterable[SnapshotFact]=(),*,admission_receipts=()):
    """World-side snapshot builder. Copies only explicitly admitted agent-visible state.

    The returned object contains no kernel reference, scenario-resource registry,
    world seed, universe id/version, scheduler object or mutable state container.
    """
    if agent_id not in kernel.agents:
        raise InvariantError('decision snapshot agent missing')
    admitted_facts=tuple(admitted_facts)
    if getattr(kernel,'boundary_manifest',None) is not None:
        from .boundary import validate_snapshot
        validate_snapshot(kernel,agent_id,period_key,effective_time,admitted_facts,admission_receipts)
    a:AgentState=kernel.agents[agent_id]
    account=kernel.state.accounts[a.account_id]
    facts=tuple(sorted(tuple(admitted_facts),key=lambda f:(f.key,f.state.value,f.source_ref,f.value or '')))
    keys=[f.key for f in facts]
    if len(keys)!=len(set(keys)):
        raise InvariantError('duplicate admitted snapshot fact key')
    return DecisionSnapshot(
        agent_id=a.id,
        agent_kind=a.kind.value,
        node_id=a.node_id,
        period_key=str(period_key),
        effective_time=str(effective_time),
        account_balance=D(account.balance),
        capabilities=tuple(sorted(a.capabilities)),
        objectives=tuple(a.objectives),
        information_refs=tuple(sorted(a.information)),
        beliefs=tuple(sorted((str(k),D(v)) for k,v in a.beliefs.items())),
        priors=tuple(sorted((str(k),D(v)) for k,v in a.priors.items())),
        asset_refs=tuple(sorted(a.asset_refs)),
        resource_holdings=tuple(sorted((str(k),D(v)) for k,v in a.resource_holdings.items())),
        claim_holdings=tuple(sorted((str(k),D(v)) for k,v in a.claim_holdings.items())),
        admitted_facts=facts)


def comparison_decision_key(comparison,actor_id,period_key,slot):
    """World-side framed derivation. Only the opaque result enters PolicyContext."""
    c=dict(comparison)
    if c['key_schema']!='LOOM_COMPARISON_RANDOM_V1' or c['algorithm']!='SHA256_FIRST64_DECIMAL_V1':
        raise InvariantError('BLOCKED_PARAMETER: comparison key contract')
    raw=json.dumps([c['key_schema'],'POLICY',c['policy_seed'],c['comparison_group'],str(actor_id),str(period_key),str(slot)],separators=(',',':'),ensure_ascii=True)
    return c['key_schema']+':'+sha256(raw.encode()).hexdigest()
