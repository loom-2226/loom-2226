"""Gate-G atomic simulation-state transaction qualification.

NON-CANON / NON-PREDICTIVE / V0.3 UNPROMOTED.
A committed opportunity changes all required ledgers together or none at all.
"""
from __future__ import annotations
from dataclasses import dataclass
import copy,hashlib,json
from typing import Mapping,Sequence

@dataclass(frozen=True)
class TransactionRequestV03:
    transaction_id:str; opportunity_id:str; customer_actor_id:str; provider_actor_id:str
    required_budget:float; provider_capacity_units:float; project_id:str
    future_event_year:int; future_event_type:str; provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class TransactionResultV03:
    transaction_id:str; status:str; reason_codes:tuple[str,...]
    pre_state_sha256:str; post_state_sha256:str; emitted_event_ids:tuple[str,...]

def _plain(state):
    return json.loads(json.dumps(state,sort_keys=True,allow_nan=False))
def state_sha256(state):
    return hashlib.sha256(json.dumps(_plain(state),sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def commit_transaction(*,state:Mapping[str,object],request:TransactionRequestV03,
                       inject_failure_at:str|None=None):
    before=_plain(state); pre=state_sha256(before)
    if not request.provenance_refs:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("MISSING_PROVENANCE",),pre,pre,())
    if request.required_budget<0 or request.provider_capacity_units<=0:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("INVALID_REQUIREMENT",),pre,pre,())
    if request.transaction_id in before.get("committed_transaction_ids",[]):
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("DUPLICATE_TRANSACTION",),pre,pre,())
    budgets=before.get("budgets",{}); capacities=before.get("provider_capacity",{})
    if request.customer_actor_id not in budgets:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("BUDGET_UNKNOWN",),pre,pre,())
    if request.provider_actor_id not in capacities:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("PROVIDER_CAPACITY_UNKNOWN",),pre,pre,())
    if float(budgets[request.customer_actor_id]) < request.required_budget:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("INSUFFICIENT_BUDGET",),pre,pre,())
    if float(capacities[request.provider_actor_id]) < request.provider_capacity_units:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",("INSUFFICIENT_PROVIDER_CAPACITY",),pre,pre,())

    work=copy.deepcopy(before)
    try:
        work["budgets"][request.customer_actor_id]=float(work["budgets"][request.customer_actor_id])-request.required_budget
        if inject_failure_at=="AFTER_BUDGET": raise RuntimeError("INJECTED_AFTER_BUDGET")
        work["provider_capacity"][request.provider_actor_id]=float(work["provider_capacity"][request.provider_actor_id])-request.provider_capacity_units
        work.setdefault("reservations",{})[request.transaction_id]={
            "provider_actor_id":request.provider_actor_id,"capacity_units":request.provider_capacity_units,
            "opportunity_id":request.opportunity_id}
        if inject_failure_at=="AFTER_RESERVATION": raise RuntimeError("INJECTED_AFTER_RESERVATION")
        if request.project_id in work.setdefault("projects",{}): raise RuntimeError("PROJECT_ALREADY_EXISTS")
        work["projects"][request.project_id]={
            "status":"COMMITTED","opportunity_id":request.opportunity_id,
            "customer_actor_id":request.customer_actor_id,"provider_actor_id":request.provider_actor_id,
            "transaction_id":request.transaction_id,"provenance_refs":list(request.provenance_refs)}
        if inject_failure_at=="AFTER_PROJECT": raise RuntimeError("INJECTED_AFTER_PROJECT")
        raw=[request.transaction_id,request.future_event_year,request.future_event_type,request.project_id]
        eid="gateg-"+hashlib.sha256(json.dumps(raw,separators=(",",":")).encode()).hexdigest()[:20]
        work.setdefault("future_events",[]).append({
            "event_id":eid,"year":request.future_event_year,"event_type":request.future_event_type,
            "project_id":request.project_id,"parent_transaction_id":request.transaction_id,
            "provenance_refs":list(request.provenance_refs)})
        if inject_failure_at=="AFTER_EVENT": raise RuntimeError("INJECTED_AFTER_EVENT")
        work.setdefault("provenance_ledger",[]).append({
            "transaction_id":request.transaction_id,"opportunity_id":request.opportunity_id,
            "project_id":request.project_id,"event_id":eid,"provenance_refs":list(request.provenance_refs)})
        if inject_failure_at=="AFTER_PROVENANCE": raise RuntimeError("INJECTED_AFTER_PROVENANCE")
        work.setdefault("committed_transaction_ids",[]).append(request.transaction_id)
    except Exception as exc:
        return before,TransactionResultV03(request.transaction_id,"ROLLED_BACK",(str(exc),),pre,pre,())

    post=state_sha256(work)
    return work,TransactionResultV03(request.transaction_id,"COMMITTED",("ATOMIC_COMMIT",),pre,post,(eid,))

def commit_winning_branches(*,state:Mapping[str,object],branches:Sequence[Mapping[str,object]],
                            request_by_opportunity:Mapping[str,TransactionRequestV03]):
    current=_plain(state); results=[]
    for b in sorted(branches,key=lambda x:str(x["opportunity_id"])):
        if str(b["action"])!="COMMIT": continue
        oid=str(b["opportunity_id"])
        if oid not in request_by_opportunity: raise ValueError("winning branch missing transaction request")
        current,res=commit_transaction(state=current,request=request_by_opportunity[oid])
        results.append(res)
    return current,tuple(results)
