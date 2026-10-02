"""Gate-D selective causal event engine qualification.

NON-CANON / NON-PREDICTIVE / V0.3 UNPROMOTED.

This is deliberately not the Method Lab's annual all-actor scheduler.  A seed
event identifies a bounded causal neighborhood; only those actors wake.  Child
events are emitted only from successful parents and retain explicit parent IDs.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, heapq, json
from typing import Mapping, Sequence

from .gate_c_named_lunar_service_v0_3 import assess_named_service
from .gate_c_named_service_traffic_v0_3 import realize_named_service

ENGINE_ID="SELECTIVE_CAUSAL_EVENT_ENGINE_V0_3"
ENGINE_VERSION="0.3.0"

@dataclass(frozen=True)
class CausalEventV03:
    event_id: str
    year: int
    phase: int
    event_type: str
    status: str
    actor_ids: tuple[str,...]
    location_ids: tuple[str,...]
    parent_event_ids: tuple[str,...]
    provenance_refs: tuple[str,...]
    payload: Mapping[str,object]

@dataclass(frozen=True)
class ActivationRecordV03:
    actor_id: str
    year: int
    status: str
    cause_event_id: str

@dataclass(frozen=True)
class ConsequenceRecordV03:
    consequence_id: str
    year: int
    consequence_type: str
    location_id: str
    amount: float
    unit: str
    parent_event_id: str
    provenance_refs: tuple[str,...]

@dataclass(frozen=True)
class GateDRunV03:
    engine_id: str
    engine_version: str
    qualification_class: str
    events: tuple[CausalEventV03,...]
    activations: tuple[ActivationRecordV03,...]
    consequences: tuple[ConsequenceRecordV03,...]
    dormant_actor_ids: tuple[str,...]
    final_active_actor_ids: tuple[str,...]
    canonical_sha256: str


def _eid(kind: str, year: int, parents: Sequence[str], payload: Mapping[str,object]) -> str:
    raw=json.dumps([kind,year,list(parents),payload],sort_keys=True,separators=(",",":"),
                   allow_nan=False).encode()
    return "gated-"+hashlib.sha256(raw).hexdigest()[:20]


def run_named_service_event(*, year: int, evidence: Mapping[str,object],
        actor_capabilities: Mapping[str,Mapping[str,str]],
        actor_universe: Sequence[str]) -> GateDRunV03:
    refs=tuple(str(x) for x in evidence.get("provenance_refs",()))
    customer=str(evidence.get("customer_actor_id",""))
    provider=str(evidence.get("provider_actor_id",""))
    neighborhood=tuple(str(x) for x in evidence.get("causal_neighborhood_actor_ids",()))
    if not customer or not provider or set(neighborhood)!={customer,provider}:
        raise ValueError("named-service evidence must define exact customer/provider causal neighborhood")
    universe=tuple(sorted(set(str(x) for x in actor_universe)))
    if not set(neighborhood)<=set(universe):
        raise ValueError("causal neighborhood contains actor outside supplied universe")

    queue=[]; serial=0; events=[]; activations=[]; consequences=[]; active=set()
    def push(phase,kind,parents=(),payload=None):
        nonlocal serial
        serial+=1; payload={} if payload is None else dict(payload)
        heapq.heappush(queue,(phase,serial,kind,tuple(parents),payload))
    push(10,"NAMED_SERVICE_OPPORTUNITY",payload={"service_id":evidence.get("service_id")})

    while queue:
        phase,_,kind,parents,payload=heapq.heappop(queue)
        eid=_eid(kind,year,parents,payload)

        if kind=="NAMED_SERVICE_OPPORTUNITY":
            events.append(CausalEventV03(eid,year,phase,kind,"OBSERVED",neighborhood,
                ("EARTH_SURFACE","LUNA_FAR_SIDE"),parents,refs,payload))
            for aid in sorted(neighborhood):
                active.add(aid)
                activations.append(ActivationRecordV03(aid,year,"ACTIVATED",eid))
            push(20,"PHYSICAL_SERVICE_ASSESSMENT",(eid,),{"actor_id":customer})

        elif kind=="PHYSICAL_SERVICE_ASSESSMENT":
            assessment=assess_named_service(actor_id=customer,year=year,
                actor_capabilities=actor_capabilities.get(customer,{}),evidence=evidence)
            events.append(CausalEventV03(eid,year,phase,kind,assessment.status,neighborhood,
                ("EARTH_SURFACE","LUNA_FAR_SIDE"),parents,refs,
                {"service_id":assessment.service_id,
                 "limiting_constraints":list(assessment.limiting_constraints)}))
            if assessment.status=="FEASIBLE_NAMED_SERVICE":
                push(30,"TRAFFIC_FLEET_REALIZATION",(eid,),
                     {"service_id":assessment.service_id,
                      "cargo_mass_tonnes":assessment.cargo_mass_tonnes})
            else:
                push(90,"CAUSAL_NEIGHBORHOOD_DEMOTION",(eid,),
                     {"reason":"SERVICE_NOT_FEASIBLE"})

        elif kind=="TRAFFIC_FLEET_REALIZATION":
            assessment=assess_named_service(actor_id=customer,year=year,
                actor_capabilities=actor_capabilities.get(customer,{}),evidence=evidence)
            realized=realize_named_service(assessment=assessment,year=year)
            events.append(CausalEventV03(eid,year,phase,kind,"REALIZED",neighborhood,
                ("EARTH_SURFACE","LUNA_FAR_SIDE"),parents,refs,
                {"voyage_id":realized.voyage.voyage_id,
                 "cargo_tonnes":realized.voyage.cargo_tonnes,
                 "passenger_movements":realized.voyage.passenger_movements}))
            push(40,"CIVPROP_TRANSPORT_CONSEQUENCE",(eid,),
                 {"location_id":"LUNA_FAR_SIDE",
                  "cargo_inbound_tonnes":realized.voyage.cargo_tonnes,
                  "arrival_calls":1})

        elif kind=="CIVPROP_TRANSPORT_CONSEQUENCE":
            events.append(CausalEventV03(eid,year,phase,kind,"WRITTEN",neighborhood,
                ("LUNA_FAR_SIDE",),parents,refs,payload))
            consequences.append(ConsequenceRecordV03(
                "gate-d-lunar-inbound-"+str(year),year,"NAMED_CARGO_DELIVERY",
                "LUNA_FAR_SIDE",float(payload["cargo_inbound_tonnes"]),"tonne",
                eid,refs))
            # Explicitly no population consequence: passenger movement is zero
            # and transport movement would not imply migration even if nonzero.
            push(90,"CAUSAL_NEIGHBORHOOD_DEMOTION",(eid,),{"reason":"EVENT_RESOLVED"})

        elif kind=="CAUSAL_NEIGHBORHOOD_DEMOTION":
            events.append(CausalEventV03(eid,year,phase,kind,"DEMOTED",neighborhood,(),
                parents,refs,payload))
            for aid in sorted(tuple(active)):
                active.remove(aid)
                activations.append(ActivationRecordV03(aid,year,"DEMOTED",eid))

    dormant=tuple(a for a in universe if a not in set(neighborhood))
    plain={
      "engine_id":ENGINE_ID,"engine_version":ENGINE_VERSION,
      "qualification_class":"GATE_D_QUALIFICATION_CONTROL_NOT_FORECAST",
      "events":[e.__dict__ for e in events],
      "activations":[a.__dict__ for a in activations],
      "consequences":[c.__dict__ for c in consequences],
      "dormant_actor_ids":dormant,"final_active_actor_ids":tuple(sorted(active)),
    }
    sha=hashlib.sha256(json.dumps(plain,sort_keys=True,separators=(",",":"),
                                  allow_nan=False).encode()).hexdigest()
    return GateDRunV03(ENGINE_ID,ENGINE_VERSION,
        "GATE_D_QUALIFICATION_CONTROL_NOT_FORECAST",tuple(events),tuple(activations),
        tuple(consequences),dormant,tuple(sorted(active)),sha)
