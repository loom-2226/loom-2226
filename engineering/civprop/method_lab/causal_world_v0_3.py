"""CIVPROP V0.3 causal world runtime without HybridEngineV1.

NON-CANON / UNPROMOTED migration runtime.  Reuses qualified domain lanes, but
the causal conductor owns time and lane ordering.  No Hybrid import or call.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib, json
from typing import Mapping, Sequence

from .causal_conductor_v0_3 import run_conductor
from .current_state_index_v0_3 import CurrentStateIndexV03
from .demographic_lane_v1 import DemographicRuntimeV1
from .mission_lane_v1 import MissionLaneV1
from .resource_lane_v1 import ResourceLaneV1
from .power_lane_v1 import PowerLaneV1
from .traffic_lane_v1 import TrafficLaneV1
from .production_lane_v1 import ProductionLaneV1
from .prototypes.common import (
    Recorder, actor_budget, apply_actor_budget_events, commission_due,
    initial_state, pending_input_requirements, snapshot, PendingProject,
)
from .contracts import FacilityRecord
from ..contracts.gate_c_named_lunar_service_v0_3 import assess_named_service
from ..contracts.gate_c_named_service_traffic_v0_3 import realize_named_service
from ..contracts.causal_migration_demography_v0_3 import realize_migration,apply_migration_and_create_cohort
from ..contracts.demand_pressure_v1 import DemandPressureRuntime
from ..contracts.causal_economic_feedback_v0_3 import observe_constraint,advance_pressure,opportunity_from_pressure
from ..contracts.legacy_authority_purge_v0_3 import purge_legacy_authority

ENGINE_ID="CAUSAL_WORLD_V0_3"
ENGINE_VERSION="0.3.0-migration-step4"


@dataclass(frozen=True)
class CausalWorldRunV03:
    engine_id: str
    engine_version: str
    qualification_class: str
    conductor_sha256: str
    event_count: int
    annual_lane_invocations: Mapping[str,int]
    annual_states: tuple
    facilities: tuple
    flows: tuple
    offworld_migrant_cohorts: tuple
    missions: tuple
    observations: tuple
    knowledge_states: tuple
    mission_decisions: tuple
    mission_opportunity_dispositions: tuple
    mission_opportunity_disposition_summaries: tuple
    resource_states: tuple
    resource_flows: tuple
    power_states: tuple
    power_flows: tuple
    traffic_demand_states: tuple
    traffic_service_states: tuple
    fleet_states: tuple
    voyage_states: tuple
    route_traffic_states: tuple
    location_traffic_states: tuple
    facility_production_states: tuple
    sector_production_states: tuple
    location_production_states: tuple
    body_production_states: tuple
    economic_constraints: tuple
    economic_pressures: tuple
    economic_opportunities: tuple
    legacy_authority_inventory: tuple
    final_state_digest: str


class _WorldContext:
    def __init__(self,bundle,seed):
        self.bundle=bundle; self.seed=seed
        self.states=initial_state(bundle)
        self.budgets=actor_budget(bundle)
        self.pending=[]
        self.recorder=Recorder()
        self.current_index=CurrentStateIndexV03()
        self.recorder.compact_mission_opportunity_dispositions=True
        self.annual_states=[]
        self.demand=(DemandPressureRuntime(bundle.scenario.demand_pressure_v1)
                     if bundle.scenario.demand_pressure_v1 else None)
        self.pressure={}
        self.economic_constraints=[]; self.economic_pressures=[]; self.economic_opportunities=[]
        self.demography=(DemographicRuntimeV1(bundle.scenario.demographic_authority_v1,
                         bundle.scenario.migration_demand_v1)
                         if bundle.scenario.demographic_authority_v1 else None)
        self.mission=(MissionLaneV1(bundle,seed,self.recorder)
                      if bundle.scenario.mission_knowledge_v1 else None)
        self.resource=(ResourceLaneV1(bundle,self.recorder,self.current_index)
                       if bundle.scenario.resource_mass_balance_v1 else None)
        self.power=(PowerLaneV1(bundle,self.recorder,self.current_index)
                    if bundle.scenario.power_balance_v1 else None)
        self.traffic=(TrafficLaneV1(bundle,self.recorder)
                      if bundle.scenario.traffic_fleet_v1 else None)
        self.production=(ProductionLaneV1(bundle,self.recorder,self.current_index)
                         if bundle.scenario.production_accounting_v1 else None)


def apply_causal_publication_semantics(payload:dict,bundle)->dict:
    """Fail closed at the causal-world publication boundary.

    GAP-014 owns Earth biological population, not workforce or habitat. Internal
    fixture values may remain available to legacy mechanics, but published causal
    state must not present stale 2026 fixture values as governed future facts.
    """
    if bundle.scenario.demographic_authority_v1 is None:
        return payload
    for row in payload.get("annual_states",[]):
        if row.get("location_id") != "EARTH_SURFACE": continue
        row["workforce"]=None
        row.setdefault("capacities",{})["habitat"]=None
        row["state_authority"]={
            "biological_population":"EARTH_PROMOTED_DEMOGRAPHIC_AUTHORITY",
            "workforce":"UNKNOWN_NOT_GOVERNED_BY_DEMOGRAPHIC_AUTHORITY",
            "habitat":"UNKNOWN_NOT_GOVERNED_BY_DEMOGRAPHIC_AUTHORITY",
        }
    return payload


def run_causal_world(*,bundle,seed:int,start_year:int|None=None,end_year:int|None=None,
                     extra_seed_events:Sequence[Mapping[str,object]]=(),
                     extra_lanes:Mapping[str,object]|None=None,
                     causal_facility_commissions:Sequence[Mapping[str,object]]=(),
                     named_transport_services:Sequence[Mapping[str,object]]=(),
                     migration_controls:Sequence[Mapping[str,object]]=())->CausalWorldRunV03:
    """Run migrated world lanes under one event queue, never HybridEngineV1.

    Step-4 scope intentionally excludes the embedded Hybrid actor/project pressure
    selector; projects enter through the qualified transactional causal path.
    """
    start=bundle.scenario.start_year if start_year is None else int(start_year)
    end=bundle.scenario.end_year if end_year is None else int(end_year)
    purged=purge_legacy_authority(bundle)
    bundle=purged.bundle
    ctx=_WorldContext(bundle,seed)

    project_by_id={x.project_archetype_id:x for x in bundle.scenario.project_archetypes}

    def facility_commission_lane(year,state,payload):
        pid=str(payload["project_archetype_id"]); loc=str(payload["location_id"]); owner=str(payload["owner_actor_id"])
        project=project_by_id.get(pid)
        if project is None: raise ValueError("UNKNOWN_PROJECT_ARCHETYPE")
        if loc not in ctx.states: raise ValueError("UNKNOWN_FACILITY_LOCATION")
        if str(payload.get("project_status"))!="ACTIVE": raise ValueError("FACILITY_REQUIRES_ACTIVE_CAUSAL_PROJECT")
        fid=str(payload["facility_id"])
        ctx.states[loc].capital += project.capital_cost
        ctx.states[loc].add_capacities(project.output_capacities)
        ctx.recorder.facilities.append(FacilityRecord(fid,pid,loc,owner,int(payload["committed_year"]),year,"ACTIVE",project.capital_cost,project.output_capacities))
        return {"last_causal_facility_commissioned":fid},()

    def named_transport_lane(year,state,payload):
        evidence=dict(payload["evidence"]); actor_id=str(payload["actor_id"])
        assessment=assess_named_service(actor_id=actor_id,year=year,
            actor_capabilities=dict(payload.get("actor_capabilities",{})),evidence=evidence)
        if assessment.status!="FEASIBLE_NAMED_SERVICE":
            return {"last_transport_service_status":assessment.status,
                    "last_transport_constraints":list(assessment.limiting_constraints)},()
        realized=realize_named_service(assessment=assessment,year=year)
        ctx.recorder.voyage_states.append(realized.voyage)
        ctx.recorder.location_traffic_states.extend(realized.location_states)
        return {"last_transport_service_status":"REALIZED",
                "last_transport_service_id":assessment.service_id,
                "last_transport_cargo_tonnes":assessment.cargo_mass_tonnes},()

    def migration_control_lane(year,state,payload):
        from types import SimpleNamespace
        origin=str(payload["origin_location_id"]); dest=str(payload["destination_location_id"])
        route=SimpleNamespace(year=year,origin_location_id=origin,destination_location_id=dest,realized_passenger_movements=payload.get("realized_passenger_movements"))
        mr=realize_migration(year=year,origin_location_id=origin,destination_location_id=dest,requested_migrants=payload.get("requested_migrants"),demand_provenance_refs=tuple(payload.get("demand_provenance_refs",())),route_traffic_state=route,origin_population=ctx.states[origin].biological_population)
        pops={k:v.biological_population for k,v in ctx.states.items()}
        out,cohort=apply_migration_and_create_cohort(populations=pops,realization=mr)
        if cohort is None: return {"last_migration_status":mr.status},()
        for k,v in out.items(): ctx.states[k].biological_population=v
        if origin=="EARTH_SURFACE" and ctx.demography: ctx.demography.earth_migration_delta-=mr.realized_migrants
        if dest=="EARTH_SURFACE" and ctx.demography: ctx.demography.earth_migration_delta+=mr.realized_migrants
        ctx.recorder.migration(year,origin,dest,mr.realized_migrants)
        cohorts=list(state.get("offworld_migrant_cohorts",()))+[{"cohort_id":cohort.cohort_id,"location_id":cohort.location_id,"population":cohort.population,"year":cohort.year,"provenance_refs":list(cohort.provenance_refs)}]
        return {"last_migration_status":mr.status,"last_realized_migrants":mr.realized_migrants,"offworld_migrant_cohorts":cohorts},()

    def annual_world_lane(year,state,payload):
        apply_actor_budget_events(bundle,ctx.budgets,year,ctx.recorder)
        if ctx.demography: ctx.demography.apply_earth_baseline(year=year,states=ctx.states)
        commission_due(year,ctx.pending,ctx.states,ctx.recorder)
        if ctx.mission: ctx.mission.execute_due(year=year,recorder=ctx.recorder)
        if ctx.resource: ctx.resource.step(year=year)
        if ctx.power: ctx.power.step(year=year,states=ctx.states)
        if ctx.traffic:
            ctx.traffic.step(year=year,states=ctx.states,
                additional_requirements=pending_input_requirements(ctx.pending))
        if ctx.production: ctx.production.step(year=year)
        if ctx.demand:
            observations=ctx.demand.derive(ctx.states,year=year,additional_requirements=pending_input_requirements(ctx.pending))
            if ctx.traffic: observations=ctx.traffic.apply_pressure_overrides(year=year,observations=observations)
            previous=dict(ctx.pressure); ctx.pressure=ctx.demand.advance_pressure(ctx.pressure,observations)
            channels=ctx.demand.channels
            for o in observations:
                c=observe_constraint(year=year,location_id=o.location_id,channel_id=o.channel_id,required=o.required,available=o.available,provenance_refs=("DEMAND_PRESSURE_V1_STATE_DERIVATION",))
                ctx.economic_constraints.append(c)
                ch=channels[o.channel_id]
                p=advance_pressure(constraint=c,previous_pressure=previous.get((o.location_id,o.channel_id),0.0),decay=ch.decay,gain=ch.gain)
                ctx.economic_pressures.append(p)
                # Threshold authority is not yet earned in production; preserve explicit blocked opportunity.
                ctx.economic_opportunities.append(opportunity_from_pressure(pressure=p,threshold=None))
        if ctx.mission:
            ctx.mission.evaluate_and_commit(year=year,budgets=ctx.budgets,recorder=ctx.recorder)
        if ctx.demography:
            ctx.demography.migrate(year=year,states=ctx.states,
                route_traffic_states=ctx.recorder.route_traffic_states,recorder=ctx.recorder)
        ctx.annual_states.extend(snapshot(year,ctx.states))
        children=[]
        if year<end:
            children.append({"year":year+1,"phase":20,"event_type":"ANNUAL_LANE_BOUNDARY",
                             "lane_id":"WORLD_ANNUAL_ACCOUNTING","provenance_refs":("CAUSAL_WORLD_V0_3",),
                             "payload":{}})
        return {"last_world_accounting_year":year},children

    lanes={"WORLD_ANNUAL_ACCOUNTING":annual_world_lane,"FACILITY_COMMISSION":facility_commission_lane,
           "NAMED_PHYSICAL_TRANSPORT":named_transport_lane,"MIGRATION_CONTROL":migration_control_lane}
    if extra_lanes: lanes.update(extra_lanes)
    seeds=[{"year":start,"phase":20,"event_type":"ANNUAL_LANE_BOUNDARY",
            "lane_id":"WORLD_ANNUAL_ACCOUNTING","provenance_refs":("CAUSAL_WORLD_V0_3",),"payload":{}}]
    for x in causal_facility_commissions:
        seeds.append({"year":int(x["commissioned_year"]),"phase":15,"event_type":"FACILITY_COMMISSIONED","lane_id":"FACILITY_COMMISSION","provenance_refs":tuple(x.get("provenance_refs",())),"payload":dict(x)})
    for x in named_transport_services:
        ev=dict(x["evidence"])
        seeds.append({"year":int(x["year"]),"phase":12,"event_type":"NAMED_PHYSICAL_TRANSPORT_SERVICE",
                      "lane_id":"NAMED_PHYSICAL_TRANSPORT","provenance_refs":tuple(ev.get("provenance_refs",())),"payload":dict(x)})
    for x in migration_controls:
        seeds.append({"year":int(x["year"]),"phase":14,"event_type":"MIGRATION_CONTROL","lane_id":"MIGRATION_CONTROL","provenance_refs":tuple(x.get("demand_provenance_refs",())),"payload":dict(x)})
    seeds.extend(dict(x) for x in extra_seed_events)
    conductor=run_conductor(start_year=start,end_year=end,initial_state={},
                            seed_events=seeds,lanes=lanes)
    digest=hashlib.sha256(json.dumps({
        "annual_states":[str(x) for x in ctx.annual_states],
        "facilities":[str(x) for x in ctx.recorder.facilities],
        "missions":[str(x) for x in ctx.recorder.missions],
        "power_states":[str(x) for x in ctx.recorder.power_states],
        "traffic_states":[str(x) for x in ctx.recorder.location_traffic_states],
        "production_states":[str(x) for x in ctx.recorder.facility_production_states],
    },sort_keys=True,separators=(",",":")).encode()).hexdigest()
    r=ctx.recorder
    return CausalWorldRunV03(ENGINE_ID,ENGINE_VERSION,
      "STEP4_CAUSAL_WORLD_NO_HYBRID_UNPROMOTED",conductor.canonical_sha256,
      len(conductor.events),dict(conductor.annual_lane_invocations),tuple(ctx.annual_states),
      tuple(r.facilities),tuple(r.flows),tuple(conductor.final_state.get("offworld_migrant_cohorts",())),tuple(r.missions),tuple(r.observations),tuple(r.knowledge_states),
      tuple(r.mission_decisions),tuple(r.mission_opportunity_dispositions),
      tuple(r.mission_opportunity_disposition_summaries),tuple(r.resource_states),tuple(r.resource_flows),tuple(r.power_states),tuple(r.power_flows),
      tuple(r.traffic_demand_states),tuple(r.traffic_service_states),tuple(r.fleet_states),
      tuple(r.voyage_states),tuple(r.route_traffic_states),tuple(r.location_traffic_states),
      tuple(r.facility_production_states),tuple(r.sector_production_states),
      tuple(r.location_production_states),tuple(r.body_production_states),
      tuple(ctx.economic_constraints),tuple(ctx.economic_pressures),tuple(ctx.economic_opportunities),
      tuple(purged.inventory),digest)
