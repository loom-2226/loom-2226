"""Step 8.A counterparty recruitment for exploratory propositions.

NON_CANON / UNPROMOTED. Requests and responses are exploratory only.
They cannot create contracts, commitments, projects, capability, access or physical effects.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping,Sequence
from .actor_activation_v0_3 import TRIGGER_CATEGORIES
from .bounded_proposition_v0_3 import EXPLORATION_COST,exploration_slots,PropositionDecisionV03,PropositionDisposition

# What an originating role must investigate before a proposition could later become feasible.
# These are dependency-discovery requests, not assertions that the dependency is required in every
# eventual transaction. Step B will determine required gates from the concrete proposition.
DEPENDENCY_REQUESTS={
 "PROSPECTOR":("OFFTAKE_REQUEST","TRANSPORT_REQUIREMENT","FINANCING_REQUEST","UNDERWRITING_REQUEST",
               "SUPPLIER_REQUEST","CERTIFICATION_REQUEST","REGISTRY_REQUEST","INFORMATION_REQUEST"),
 "INCUMBENT_INDUSTRY":("OFFTAKE_REQUEST","TRANSPORT_REQUIREMENT","FINANCING_REQUEST","UNDERWRITING_REQUEST",
                       "SUPPLIER_REQUEST","CERTIFICATION_REQUEST","REGISTRY_REQUEST"),
 "OFFTAKER":("SUPPLIER_REQUEST","TRANSPORT_REQUIREMENT","FINANCING_REQUEST","UNDERWRITING_REQUEST","CERTIFICATION_REQUEST"),
 "CARRIER":("OFFTAKE_REQUEST","FINANCING_REQUEST","UNDERWRITING_REQUEST","SUPPLIER_REQUEST","CERTIFICATION_REQUEST"),
 "SUPPLIER_PRIME":("OFFTAKE_REQUEST","TRANSPORT_REQUIREMENT","FINANCING_REQUEST","UNDERWRITING_REQUEST","CERTIFICATION_REQUEST"),
 "INFRASTRUCTURE":("OFFTAKE_REQUEST","TRANSPORT_REQUIREMENT","FINANCING_REQUEST","UNDERWRITING_REQUEST","SUPPLIER_REQUEST","CERTIFICATION_REQUEST"),
 "CAPITAL":("UNDERWRITING_REQUEST","INFORMATION_REQUEST","CERTIFICATION_REQUEST"),
 "INSURER":("INFORMATION_REQUEST","CERTIFICATION_REQUEST"),
 "INFORMATION":("OFFTAKE_REQUEST",),
 "SOFT_POWER":("INFORMATION_REQUEST",),
 "CERTIFICATION":("REGISTRY_REQUEST","INFORMATION_REQUEST"),
 "REGISTRY":("INFORMATION_REQUEST",),
 "SETTLEMENT_LABOR":("SUPPLIER_REQUEST","TRANSPORT_REQUIREMENT","INFORMATION_REQUEST"),
}

class RecruitmentDisposition(str,Enum):
 ACCEPT_EXPLORATION="ACCEPT_EXPLORATION"
 DEFER="DEFER"
 DECLINE="DECLINE"
 COUNTER="COUNTER"

@dataclass(frozen=True)
class CounterpartyRequestV03:
 request_id:str; proposition_id:str; origin_actor_id:str; context_id:str
 request_type:str; target_category:str; iso3:str; sector:str
 candidate_actor_ids:tuple[str,...]; provenance_refs:tuple[str,...]
 semantics:str="EXPLORATORY_REQUEST_ONLY_NO_TRANSACTION_AUTHORITY"

@dataclass(frozen=True)
class CounterpartyResponseV03:
 request_id:str; proposition_id:str; responder_actor_id:str; target_category:str
 disposition:RecruitmentDisposition; reason:str; response_rank:int|None
 provenance_refs:tuple[str,...]
 semantics:str="EXPLORATORY_RESPONSE_ONLY_NO_CONTRACT_OR_PROJECT_AUTHORITY"

def _geo_sets(jurisdiction_links:Sequence[Mapping[str,object]],iso3:str):
 domestic=set(); global_ids=set()
 for x in jurisdiction_links:
  aid=str(x["actor_id"]); loc=str(x["iso3"])
  if loc=="GLOBAL":global_ids.add(aid)
  elif loc==iso3:domestic.add(aid)
 return domestic,global_ids

def _bounded_candidates(*,registry,category:str,iso3:str,jurisdiction_links,
                        origin_actor_id:str,max_domestic:int=2,max_global:int=1,max_cross_border:int=1):
 domestic,global_ids=_geo_sets(jurisdiction_links,iso3)
 ids=registry.relevant_candidates(
   next(k for k,v in TRIGGER_CATEGORIES.items() if category in v),
   eligible_actor_ids=[s.identity.actor_id for s in registry.states() if s.identity.category==category])
 ids=[x for x in ids if x!=origin_actor_id]
 states={x.identity.actor_id:x.identity for x in registry.states()}
 key=lambda aid:(-(states[aid].financial_capacity_estimate or 0.0),aid)
 d=sorted((x for x in ids if x in domestic),key=key)[:max_domestic]
 g=sorted((x for x in ids if x in global_ids),key=key)[:max_global]
 used=set(d+g)
 o=sorted((x for x in ids if x not in domestic and x not in global_ids),key=key)[:max_cross_border]
 return tuple(d+g+[x for x in o if x not in used])

def decompose_and_recruit(*,decision:PropositionDecisionV03,registry,jurisdiction_links,
                          proposition_category:str,iso3:str,sector:str,provenance_refs:Sequence[str]=()):
 if decision.disposition!=PropositionDisposition.EXPLORE:return ()
 requests=[]
 for request_type in DEPENDENCY_REQUESTS.get(proposition_category,()):
  for category in TRIGGER_CATEGORIES[request_type]:
   candidates=_bounded_candidates(registry=registry,category=category,iso3=iso3,
       jurisdiction_links=jurisdiction_links,origin_actor_id=decision.actor_id)
   if not candidates:continue
   rid=f"REQ:{decision.proposition_id}:{request_type}:{category}"
   prov=tuple(sorted(set(tuple(provenance_refs)+(decision.proposition_id,decision.context_id))))
   registry.mark_relevant_actor_ids(context_id=rid,actor_ids=candidates,provenance_refs=prov)
   requests.append(CounterpartyRequestV03(rid,decision.proposition_id,decision.actor_id,decision.context_id,
       request_type,category,iso3,sector,candidates,prov))
 return tuple(sorted(requests,key=lambda x:x.request_id))

def respond_to_requests(*,registry,requests:Sequence[CounterpartyRequestV03]):
 """Bounded exploratory response portfolio. Acceptance creates no relationship/contract."""
 by_actor={}
 for req in requests:
  for aid in req.candidate_actor_ids:by_actor.setdefault(aid,[]).append(req)
 out=[]
 for aid in sorted(by_actor):
  ident=registry.state(aid).identity
  viable=[]; declined=[]
  for req in by_actor[aid]:
   cost=EXPLORATION_COST.get(ident.category,50_000.0)
   if (ident.financial_capacity_estimate or 0.0)>=cost:viable.append(req)
   else:declined.append(req)
  # Prefer originating proposition attractiveness implicitly through proposition selection;
  # within this exploratory batch use stable request identity, avoiding invented psychology.
  viable=sorted(viable,key=lambda x:(x.proposition_id,x.request_id))
  slots=exploration_slots(ident.scale_score)
  for rank,req in enumerate(viable,1):
   disp=RecruitmentDisposition.ACCEPT_EXPLORATION if rank<=slots else RecruitmentDisposition.DEFER
   reason="RESPONSE_PORTFOLIO_SELECTED" if rank<=slots else "RESPONSE_ATTENTION_CONSTRAINT"
   out.append(CounterpartyResponseV03(req.request_id,req.proposition_id,aid,req.target_category,
       disp,reason,rank,req.provenance_refs))
  for req in sorted(declined,key=lambda x:x.request_id):
   out.append(CounterpartyResponseV03(req.request_id,req.proposition_id,aid,req.target_category,
       RecruitmentDisposition.DECLINE,"EXPLORATORY_AFFORDABILITY_BLOCK",None,req.provenance_refs))
 return tuple(sorted(out,key=lambda x:(x.responder_actor_id,x.request_id)))
