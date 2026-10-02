"""Gate-E typed causal event scheduler qualification.

NON-CANON / NON-PREDICTIVE / V0.3 UNPROMOTED.
No annual heartbeat exists. Time advances only to queued event timestamps.
Independent branches survive failures in other branches.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, heapq, json
from typing import Mapping, Sequence

from .gate_c_named_lunar_service_v0_3 import assess_named_service
from .gate_c_named_service_traffic_v0_3 import realize_named_service

ENGINE_ID="TYPED_CAUSAL_EVENT_SCHEDULER_V0_3"
ENGINE_VERSION="0.3.0"
PHASE={"FRONTIER":10,"OPPORTUNITY":20,"ASSESS":30,"REALIZE":40,"CONSEQUENCE":50,"FOLLOWUP":60,"DEMOTE":90}

@dataclass(frozen=True)
class ScheduledEventV03:
    event_id:str; year:int; phase:int; event_type:str; family:str; status:str
    actor_ids:tuple[str,...]; location_ids:tuple[str,...]; parent_event_ids:tuple[str,...]
    provenance_refs:tuple[str,...]; payload:Mapping[str,object]

@dataclass(frozen=True)
class SchedulerConsequenceV03:
    consequence_id:str; year:int; consequence_type:str; location_id:str
    amount:float; unit:str; parent_event_id:str

@dataclass(frozen=True)
class GateERunV03:
    engine_id:str; engine_version:str; qualification_class:str
    events:tuple[ScheduledEventV03,...]
    consequences:tuple[SchedulerConsequenceV03,...]
    activated_actor_ids:tuple[str,...]; dormant_actor_ids:tuple[str,...]
    final_active_actor_ids:tuple[str,...]; processed_years:tuple[int,...]
    annual_heartbeat_count:int; canonical_sha256:str

def _id(kind,year,parents,payload):
    raw=json.dumps([kind,year,list(parents),payload],sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    return "gatee-"+hashlib.sha256(raw).hexdigest()[:20]

def run_typed_scheduler(*, start_year:int, end_year:int, seed_events:Sequence[Mapping[str,object]],
                        actor_universe:Sequence[str],
                        actor_capabilities:Mapping[str,Mapping[str,str]],
                        service_evidence:Mapping[str,Mapping[str,object]]) -> GateERunV03:
    universe=tuple(sorted(set(map(str,actor_universe))))
    queue=[]; serial=0; out=[]; cons=[]; active=set(); ever=set(); processed=[]
    def push(year,phase,kind,family,actors=(),locs=(),parents=(),refs=(),payload=None):
        nonlocal serial
        if year < start_year or year > end_year: return
        serial+=1; p={} if payload is None else dict(payload)
        heapq.heappush(queue,(year,phase,serial,kind,family,tuple(actors),tuple(locs),tuple(parents),tuple(refs),p))
    for s in seed_events:
        push(int(s["year"]),int(s.get("phase",PHASE["FRONTIER"])),str(s["event_type"]),
             str(s["family"]),s.get("actor_ids",()),s.get("location_ids",()),
             (),s.get("provenance_refs",()),s.get("payload",{}))

    while queue:
        year,phase,_,kind,family,actors,locs,parents,refs,payload=heapq.heappop(queue)
        if not processed or processed[-1]!=year: processed.append(year)
        eid=_id(kind,year,parents,payload)

        if kind=="TECHNOLOGY_FRONTIER_REACHED":
            # Frontier is a consideration anchor only. It creates no actor capability.
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"CONSIDERATION_ANCHOR",actors,locs,parents,refs,payload))
            continue

        if kind=="NAMED_SERVICE_OPPORTUNITY":
            key=str(payload["service_key"]); evidence=service_evidence[key]
            customer=str(evidence["customer_actor_id"]); provider=str(evidence["provider_actor_id"])
            neighborhood=tuple(evidence["causal_neighborhood_actor_ids"])
            if set(neighborhood)!={customer,provider}: raise ValueError("invalid service causal neighborhood")
            if not set(neighborhood)<=set(universe): raise ValueError("service actor outside universe")
            active.update(neighborhood); ever.update(neighborhood)
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"OBSERVED",neighborhood,locs,parents,refs,payload))
            push(year,PHASE["ASSESS"],"NAMED_SERVICE_ASSESSMENT",family,neighborhood,locs,(eid,),refs,{"service_key":key})
            continue

        if kind=="NAMED_SERVICE_ASSESSMENT":
            key=str(payload["service_key"]); evidence=service_evidence[key]
            customer=str(evidence["customer_actor_id"])
            a=assess_named_service(actor_id=customer,year=year,
                actor_capabilities=actor_capabilities.get(customer,{}),evidence=evidence)
            out.append(ScheduledEventV03(eid,year,phase,kind,family,a.status,actors,locs,parents,refs,
                {"service_key":key,"limiting_constraints":list(a.limiting_constraints)}))
            if a.status=="FEASIBLE_NAMED_SERVICE":
                push(year,PHASE["REALIZE"],"NAMED_SERVICE_REALIZATION",family,actors,locs,(eid,),refs,{"service_key":key})
            else:
                push(year,PHASE["DEMOTE"],"BRANCH_DEMOTION",family,actors,(),(eid,),refs,{"reason":"SERVICE_NOT_FEASIBLE"})
            continue

        if kind=="NAMED_SERVICE_REALIZATION":
            key=str(payload["service_key"]); evidence=service_evidence[key]
            customer=str(evidence["customer_actor_id"])
            a=assess_named_service(actor_id=customer,year=year,
                actor_capabilities=actor_capabilities.get(customer,{}),evidence=evidence)
            r=realize_named_service(assessment=a,year=year)
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"REALIZED",actors,locs,parents,refs,
                {"service_key":key,"cargo_tonnes":r.voyage.cargo_tonnes}))
            push(year,PHASE["CONSEQUENCE"],"TRANSPORT_CONSEQUENCE",family,actors,
                 ("LUNA_FAR_SIDE",),(eid,),refs,{"cargo_tonnes":r.voyage.cargo_tonnes})
            continue

        if kind=="TRANSPORT_CONSEQUENCE":
            amount=float(payload["cargo_tonnes"])
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"WRITTEN",actors,locs,parents,refs,payload))
            cons.append(SchedulerConsequenceV03("gatee-cargo-"+eid,year,"NAMED_CARGO_DELIVERY",
                                                "LUNA_FAR_SIDE",amount,"tonne",eid))
            # Child/future event: delayed post-delivery review. It has no invented
            # substantive consequence; it proves future scheduling and ancestry.
            push(year+2,PHASE["FOLLOWUP"],"POST_DELIVERY_REVIEW",family,actors,
                 ("LUNA_FAR_SIDE",),(eid,),refs,{"source_delivery_event_id":eid})
            push(year,PHASE["DEMOTE"],"BRANCH_DEMOTION",family,actors,(),(eid,),refs,{"reason":"DELIVERY_RESOLVED"})
            continue

        if kind=="POST_DELIVERY_REVIEW":
            active.update(actors); ever.update(actors)
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"REVIEW_DUE",actors,locs,parents,refs,payload))
            push(year,PHASE["DEMOTE"],"BRANCH_DEMOTION",family,actors,(),(eid,),refs,{"reason":"REVIEW_RECORDED"})
            continue

        if kind=="BRANCH_DEMOTION":
            out.append(ScheduledEventV03(eid,year,phase,kind,family,"DEMOTED",actors,locs,parents,refs,payload))
            for a in actors: active.discard(a)
            continue

        raise ValueError("unregistered event type: "+kind)

    dormant=tuple(a for a in universe if a not in ever)
    plain={"events":[x.__dict__ for x in out],"consequences":[x.__dict__ for x in cons],
           "activated_actor_ids":tuple(sorted(ever)),"dormant_actor_ids":dormant,
           "final_active_actor_ids":tuple(sorted(active)),"processed_years":tuple(processed),
           "annual_heartbeat_count":0}
    sha=hashlib.sha256(json.dumps(plain,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return GateERunV03(ENGINE_ID,ENGINE_VERSION,"GATE_E_QUALIFICATION_CONTROL_NOT_FORECAST",
        tuple(out),tuple(cons),tuple(sorted(ever)),dormant,tuple(sorted(active)),tuple(processed),0,sha)
