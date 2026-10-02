"""Gate-H closed-loop causal propagation qualification.

NON-CANON / NON-PREDICTIVE / V0.3 UNPROMOTED.
Consumes committed Gate-G future events, reads mutated state, and emits only
state-justified descendants. This is a qualification loop, not production runtime.
"""
from __future__ import annotations
from dataclasses import dataclass
import copy,hashlib,heapq,json
from typing import Mapping,Sequence

@dataclass(frozen=True)
class ClosedLoopEventV03:
    event_id:str; year:int; event_type:str; status:str; parent_ids:tuple[str,...]
    project_id:str|None; actor_ids:tuple[str,...]; provenance_refs:tuple[str,...]
    reason_codes:tuple[str,...]

@dataclass(frozen=True)
class GateHResultV03:
    qualification_class:str; events:tuple[ClosedLoopEventV03,...]
    processed_years:tuple[int,...]; final_state:Mapping[str,object]
    final_state_sha256:str; canonical_sha256:str

def _state_sha(s):
    return hashlib.sha256(json.dumps(s,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def _eid(kind,year,parent,project):
    return "gateh-"+hashlib.sha256(json.dumps([kind,year,parent,project],separators=(",",":")).encode()).hexdigest()[:20]

def run_closed_loop(*,committed_state:Mapping[str,object],start_year:int,end_year:int,
                    review_to_activation_lag_years:int=1) -> GateHResultV03:
    state=copy.deepcopy(committed_state); queue=[]; serial=0; events=[]; years=[]
    def push(raw):
        nonlocal serial
        y=int(raw["year"])
        if start_year<=y<=end_year:
            serial+=1; heapq.heappush(queue,(y,serial,dict(raw)))
    for raw in state.get("future_events",[]): push(raw)
    state["future_events"]=[]

    while queue:
        year,_,raw=heapq.heappop(queue)
        if not years or years[-1]!=year: years.append(year)
        kind=str(raw["event_type"]); project=str(raw.get("project_id") or "") or None
        parent=str(raw.get("event_id") or raw.get("parent_transaction_id") or "ROOT")
        refs=tuple(raw.get("provenance_refs",()))
        if not refs:
            events.append(ClosedLoopEventV03(_eid(kind,year,parent,project),year,kind,"BLOCKED",
                (parent,),project,(),refs,("MISSING_PROVENANCE",))); continue
        p=state.get("projects",{}).get(project) if project else None

        if kind=="PROJECT_REVIEW":
            eid=_eid(kind,year,parent,project)
            if p is None:
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent,),project,(),refs,("PROJECT_ABSENT",))); continue
            if p.get("status")!="COMMITTED":
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent,),project,(),refs,("PROJECT_NOT_COMMITTED",))); continue
            tid=str(p.get("transaction_id") or "")
            reservation=state.get("reservations",{}).get(tid)
            if reservation is None:
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent,),project,(),refs,("RESERVATION_ABSENT",))); continue
            provider=str(p["provider_actor_id"]); customer=str(p["customer_actor_id"])
            events.append(ClosedLoopEventV03(eid,year,kind,"PASSED",(parent,),project,(customer,provider),refs,()))
            # State change caused by this event: review authorizes activation.
            state["projects"][project]["status"]="ACTIVATION_AUTHORIZED"
            child={"event_id":_eid("PROJECT_ACTIVATION",year+review_to_activation_lag_years,eid,project),
                   "year":year+review_to_activation_lag_years,"event_type":"PROJECT_ACTIVATION",
                   "project_id":project,"parent_event_id":eid,"provenance_refs":list(refs)}
            push(child); continue

        if kind=="PROJECT_ACTIVATION":
            eid=str(raw.get("event_id") or _eid(kind,year,parent,project))
            p=state.get("projects",{}).get(project) if project else None
            parent_id=str(raw.get("parent_event_id") or parent)
            if p is None:
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent_id,),project,(),refs,("PROJECT_ABSENT",))); continue
            if p.get("status")!="ACTIVATION_AUTHORIZED":
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent_id,),project,(),refs,("ACTIVATION_NOT_AUTHORIZED",))); continue
            tid=str(p.get("transaction_id") or "")
            if tid not in state.get("reservations",{}):
                events.append(ClosedLoopEventV03(eid,year,kind,"BLOCKED",(parent_id,),project,(),refs,("RESERVATION_ABSENT",))); continue
            p["status"]="ACTIVE"
            events.append(ClosedLoopEventV03(eid,year,kind,"STATE_CHANGED",(parent_id,),project,
                (str(p["customer_actor_id"]),str(p["provider_actor_id"])),refs,()))
            continue
        raise ValueError("unregistered closed-loop event type: "+kind)

    final_sha=_state_sha(state)
    plain={"events":[x.__dict__ for x in events],"processed_years":years,"final_state":state}
    sha=hashlib.sha256(json.dumps(plain,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return GateHResultV03("GATE_H_QUALIFICATION_CONTROL_NOT_FORECAST",tuple(events),tuple(years),state,final_sha,sha)
