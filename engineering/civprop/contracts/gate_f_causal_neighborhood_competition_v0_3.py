"""Gate-F derived causal-neighborhood and shared-scarcity qualification.

NON-CANON / NON-PREDICTIVE / V0.3 UNPROMOTED.
Neighborhoods are derived from scoped actor edges. Competition delegates to the
existing shared portfolio allocator; this contract does not invent a new budget model.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json
from typing import Mapping,Sequence
from .shared_portfolio_competition_v0_3 import PortfolioOpportunityV03, allocate_shared_portfolio

VERSION="0.3.0"

@dataclass(frozen=True)
class DerivedNeighborhoodV03:
    trigger_actor_id:str
    required_scope_token:str
    actor_ids:tuple[str,...]
    supporting_edges:tuple[Mapping[str,object],...]
    excluded_edge_count:int

@dataclass(frozen=True)
class CompetitionBranchV03:
    opportunity_id:str; provider_actor_id:str; priority:float; required_budget:float
    action:str; reason_codes:tuple[str,...]; neighborhood_actor_ids:tuple[str,...]

@dataclass(frozen=True)
class GateFResultV03:
    qualification_class:str
    neighborhood:DerivedNeighborhoodV03
    branches:tuple[CompetitionBranchV03,...]
    committed_budget:float
    ending_budget:float
    winning_opportunity_ids:tuple[str,...]
    losing_opportunity_ids:tuple[str,...]
    activated_actor_ids:tuple[str,...]
    dormant_actor_ids:tuple[str,...]
    canonical_sha256:str

def derive_scoped_neighborhood(*,trigger_actor_id:str,scope_token:str,seed_edges:Sequence[Mapping[str,object]],
                               actor_universe:Sequence[str]) -> DerivedNeighborhoodV03:
    universe=set(map(str,actor_universe)); token=scope_token.lower().strip()
    if trigger_actor_id not in universe: raise ValueError("trigger actor outside universe")
    if not token: raise ValueError("scope token required")
    support=[]
    for e in seed_edges:
        if str(e.get("from"))!=trigger_actor_id: continue
        if token not in str(e.get("scope","")).lower(): continue
        if str(e.get("to")) not in universe: raise ValueError("edge actor outside universe")
        support.append(dict(e))
    if not support:
        return DerivedNeighborhoodV03(trigger_actor_id,scope_token,(trigger_actor_id,),(),len(seed_edges))
    actors={trigger_actor_id}
    for e in support: actors.add(str(e["to"]))
    return DerivedNeighborhoodV03(trigger_actor_id,scope_token,tuple(sorted(actors)),
        tuple(sorted(support,key=lambda e:(str(e["from"]),str(e["to"]),str(e["scope"])))),
        len(seed_edges)-len(support))

def arbitrate_scoped_competition(*,trigger_actor_id:str,scope_token:str,
        seed_edges:Sequence[Mapping[str,object]],actor_universe:Sequence[str],
        opportunities:Sequence[Mapping[str,object]],budget_status:str,budget_value:float|None) -> GateFResultV03:
    n=derive_scoped_neighborhood(trigger_actor_id=trigger_actor_id,scope_token=scope_token,
        seed_edges=seed_edges,actor_universe=actor_universe)
    providers=set(n.actor_ids)-{trigger_actor_id}
    seen=set(); opps=[]
    provider_by={}
    for raw in opportunities:
        oid=str(raw["opportunity_id"]); provider=str(raw["provider_actor_id"])
        if oid in seen: raise ValueError("duplicate opportunity id")
        seen.add(oid)
        if provider not in providers: raise ValueError("opportunity provider outside derived neighborhood")
        provider_by[oid]=provider
        opps.append(PortfolioOpportunityV03(oid,str(raw.get("kind","PROJECT")),
            float(raw["required_budget"]),bool(raw.get("eligible",True)),
            float(raw["priority"]),tuple(raw["provenance_refs"])))
    alloc=allocate_shared_portfolio(actor_id=trigger_actor_id,opportunities=tuple(opps),
        budget_status=budget_status,budget_value=budget_value)
    branches=[]
    for d in alloc.decisions:
        branches.append(CompetitionBranchV03(d.opportunity_id,provider_by[d.opportunity_id],
            next(o.priority for o in opps if o.opportunity_id==d.opportunity_id),
            d.required_budget,d.action,d.reason_codes,n.actor_ids))
    winners=tuple(sorted(x.opportunity_id for x in branches if x.action=="COMMIT"))
    losers=tuple(sorted(x.opportunity_id for x in branches if x.action!="COMMIT"))
    committed=sum(x.required_budget for x in branches if x.action=="COMMIT")
    universe=tuple(sorted(set(map(str,actor_universe))))
    activated=tuple(sorted(set(n.actor_ids)))
    dormant=tuple(a for a in universe if a not in set(activated))
    ending=alloc.ending_budget
    plain={"neighborhood":n.__dict__,"branches":[x.__dict__ for x in branches],
      "committed_budget":committed,"ending_budget":ending,"winners":winners,"losers":losers,
      "activated":activated,"dormant":dormant}
    sha=hashlib.sha256(json.dumps(plain,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return GateFResultV03("GATE_F_QUALIFICATION_CONTROL_NOT_FORECAST",n,tuple(branches),
        committed,ending,winners,losers,activated,dormant,sha)
