"""Immutable causal composition; no domain executor, reducer, clock or ledger.

Domain adapters supply typed state rows. The envelope never assumes a project,
price, account, resource, or particular decision/transition implementation.
"""
from __future__ import annotations
from dataclasses import dataclass, fields, is_dataclass, replace
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from .kernel import InvariantError


def typed(value):
    """Lossless type tags keep original records and scalar domains distinguishable."""
    if isinstance(value, Enum):
        return {'type': type(value).__name__, 'value': value.value}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise InvariantError('non-finite trace scalar')
        return {'type': 'Decimal', 'value': str(value)}
    if is_dataclass(value):
        return {'type': type(value).__name__, 'fields': {f.name: typed(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, dict):
        return {'type': 'mapping', 'entries': sorted(((canonical(k), typed(v)) for k, v in value.items()), key=lambda x: x[0])}
    if isinstance(value, (set, frozenset)):
        return {'type': 'set', 'items': sorted((typed(x) for x in value), key=lambda x: json.dumps(x, sort_keys=True))}
    if isinstance(value, (tuple, list)):
        return {'type': 'tuple' if isinstance(value, tuple) else 'list', 'items': [typed(x) for x in value]}
    if value is None or type(value) in (str, int, bool):
        return {'type': type(value).__name__, 'value': value}
    raise InvariantError(f'unsupported trace type: {type(value).__name__}')


def canonical(value):
    return json.dumps(typed(value), sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def content_hash(value):
    return sha256(canonical(value).encode('utf-8')).hexdigest()


def state_delta(prior, following):
    """Rows are (state domain, source path, canonical typed payload)."""
    a={(d,p):v for d,p,v in prior}; b={(d,p):v for d,p,v in following}
    if len(a)!=len(prior) or len(b)!=len(following):
        raise InvariantError('duplicate typed state path')
    # None is record absence, never a numerical zero or an epistemic UNKNOWN.
    return tuple((d,p,a.get((d,p)),b.get((d,p))) for d,p in sorted(a.keys()|b.keys()) if a.get((d,p))!=b.get((d,p)))


@dataclass(frozen=True, slots=True)
class CausalEnvelope:
    envelope_id: str
    record_version: str
    run_id: str
    scheduled_event_id: str
    epoch_id: str
    effective_time: str
    time_basis: str
    actor_id: str
    process_id: str
    action: str
    world_context: str
    context_id: str
    perspective: str
    request_refs: tuple[str,...]
    decision_refs: tuple[str,...]
    information_refs: tuple[str,...]
    input_receipt_refs: tuple[str,...]
    prior_state: tuple[tuple[str,str,str|None],...]
    result: str
    new_state: tuple[tuple[str,str,str|None],...]
    reason_code: str
    reason: str
    rule_refs: tuple[str,...]
    parameter_manifest_refs: tuple[tuple[str,str],...]
    scenario_ref: tuple[str,str,str]
    random_stream_refs: tuple[str,...]
    source_artifact_refs: tuple[tuple[str,str],...]
    lineage_refs: tuple[str,...]
    parent_envelope_refs: tuple[str,...]
    pre_domain_hash: str
    post_domain_hash: str
    previous_trace_hash: str
    envelope_hash: str
    # All use the declared existing axis. An absent decision time is not inferred
    # from event time (physical/system and genesis origins need no Agent choice).
    decision_time: str|None
    authorization_time: str|None
    realized_time: str
    source_times: tuple[tuple[str,str,str],...]
    artifact_refs: tuple[tuple[str,str],...]

    def __post_init__(self):
        def immutable(value):
            if value is None or type(value) in (str,int,bool):return
            if isinstance(value,tuple):
                for child in value:immutable(child)
                return
            raise InvariantError('mutable/unsupported causal envelope payload')
        for f in fields(self):immutable(getattr(self,f.name))
        for name in ('envelope_id','record_version','run_id','scheduled_event_id','time_basis','process_id','action','world_context','context_id','perspective','pre_domain_hash','post_domain_hash'):
            if not getattr(self,name):
                raise InvariantError(f'causal envelope field missing: {name}')
        if self.time_basis!='SIM_TIME' or self.world_context!='REALIZED':
            raise InvariantError('unsupported trace time/context')
        for t in (self.effective_time,self.realized_time,self.decision_time,self.authorization_time):
            if t is not None and (not Decimal(t).is_finite() or Decimal(t)<0):
                raise InvariantError('invalid causal time')
        if self.decision_time is not None and Decimal(self.decision_time)>Decimal(self.realized_time):
            raise InvariantError('decision occurs after realized transition')
        if self.authorization_time is not None and Decimal(self.authorization_time)>Decimal(self.realized_time):
            raise InvariantError('authorization occurs after realized transition')
        if tuple((d,p) for d,p,_ in self.prior_state)!=tuple((d,p) for d,p,_ in self.new_state):
            raise InvariantError('causal delta paths differ')
        if not self.rule_refs or not self.source_artifact_refs:
            raise InvariantError('causal origin/rules incomplete')

    def digest(self):
        return content_hash(tuple((f.name,getattr(self,f.name)) for f in fields(self) if f.name!='envelope_hash'))

    def finalized(self):
        return replace(self,envelope_hash=self.digest())


def archive(artifacts, kind, value):
    """Audit store contains immutable original payloads, not replacement state."""
    payload=canonical(value); ref=f'{kind}:{sha256(payload.encode()).hexdigest()}'
    if ref in artifacts and artifacts[ref]!=(kind,payload):
        raise InvariantError('causal artifact collision')
    artifacts[ref]=(kind,payload)
    return ref


def validate_trace(envelopes, artifacts):
    previous='';seen=set();post=None;realized=None
    for e in envelopes:
        if realized is not None and Decimal(e.realized_time)<realized:
            raise InvariantError('TRACE_INCOMPLETE: realization time moved backwards')
        if post is not None and e.pre_domain_hash!=post:
            raise InvariantError('TRACE_INCOMPLETE: uncovered state transition')
        if e.envelope_id in seen or e.envelope_hash!=e.digest() or e.previous_trace_hash!=previous:
            raise InvariantError('TRACE_INCOMPLETE: invalid envelope/hash chain')
        if any(p not in seen for p in e.parent_envelope_refs):
            raise InvariantError('TRACE_INCOMPLETE: missing/forward/cyclic parent')
        refs=(*e.request_refs,*e.decision_refs,*e.information_refs,*e.input_receipt_refs,*e.lineage_refs,*(r for _,r in e.artifact_refs))
        if any(r not in artifacts for r in refs):
            raise InvariantError('TRACE_INCOMPLETE: missing original artifact')
        for r in refs:
            kind,payload=artifacts[r]
            if r!=f'{kind}:{sha256(payload.encode()).hexdigest()}':
                raise InvariantError('TRACE_INCOMPLETE: artifact hash mismatch')
        source_hashes={digest for _,digest in e.source_artifact_refs}
        if any('#' not in rule or rule.rsplit('#',1)[1] not in source_hashes for rule in e.rule_refs):
            raise InvariantError('TRACE_INCOMPLETE: unbound rule source/version')
        if not e.decision_refs and not any(r.startswith(('SYSTEM_RULE:','GENESIS_RULE:')) for r in e.rule_refs):
            raise InvariantError('TRACE_INCOMPLETE: no decision or explicit system/genesis origin')
        if e.pre_domain_hash==e.post_domain_hash and e.prior_state!=e.new_state:
            raise InvariantError('TRACE_INCOMPLETE: inconsistent domain delta')
        seen.add(e.envelope_id);previous=e.envelope_hash;post=e.post_domain_hash;realized=Decimal(e.realized_time)
    return previous


def reconstruct(envelopes, artifacts, envelope_id, *, perspective, actor_id):
    """No implicit promotion of world audit material into Agent knowledge."""
    validate_trace(envelopes,artifacts)
    by_id={e.envelope_id:e for e in envelopes}
    if envelope_id not in by_id:
        return {'status':'TRACE_INCOMPLETE','envelopes':(),'artifacts':()}
    if perspective=='AGENT':
        # Original worker snapshots/decisions are separately retrievable through
        # admitted-information use. Never return a world delta with hidden state.
        return {'status':'BLOCKED_PERSPECTIVE','envelopes':(),'artifacts':()}
    if perspective not in ('WORLD_SIM','GOVERNANCE') or not actor_id:
        raise InvariantError('trace audit perspective/consumer required')
    pending=[envelope_id];selected=set()
    while pending:
        eid=pending.pop()
        if eid in selected:continue
        selected.add(eid);pending.extend(by_id[eid].parent_envelope_refs)
    ordered=tuple(e for e in envelopes if e.envelope_id in selected)
    refs={r for e in ordered for r in (*e.request_refs,*e.decision_refs,*e.information_refs,*e.input_receipt_refs,*e.lineage_refs,*(r for _,r in e.artifact_refs))}
    return {'status':'COMPLETE','envelopes':ordered,'artifacts':tuple((r,*artifacts[r]) for r in sorted(refs))}


def legacy_event_view(event):
    return {'status':'LEGACY_TRACE_INCOMPLETE','original_record':canonical(event),'missing':('prior_state','consumption_receipts','complete_input_rule_lineage')}
