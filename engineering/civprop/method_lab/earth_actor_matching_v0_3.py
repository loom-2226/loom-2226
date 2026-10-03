"""Bounded actor-neighborhood selection for Earth sector opportunities."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping,Sequence

@dataclass(frozen=True)
class OpportunityMatchV03:
 context_id:str; iso3:str; sector:str; actor_ids:tuple[str,...]
 domestic_actor_ids:tuple[str,...]; global_actor_ids:tuple[str,...]; cross_border_actor_ids:tuple[str,...]
 semantics:str="RELEVANCE_ONLY_NO_TRANSACTION_AUTHORITY"

def match_opportunity(*,trigger,registry,jurisdiction_links:Sequence[Mapping[str,object]],max_domestic_per_category:int=5,max_global_per_category:int=3,max_cross_border_per_category:int=3):
 links={}
 global_ids=set()
 for x in jurisdiction_links:
  aid=str(x["actor_id"]); iso=str(x["iso3"])
  if iso=="GLOBAL":global_ids.add(aid)
  else:links.setdefault(iso,set()).add(aid)
 domestic=links.get(trigger.iso3,set())
 selected=set(); ds=set(); gs=set(); cs=set()
 states={x.identity.actor_id:x for x in registry.states()}
 for cat in trigger.relevant_categories:
  eligible=[x.identity for x in states.values() if x.identity.category==cat and x.identity.functional_2026 and x.identity.autonomous_eligible]
  d=[x for x in eligible if x.actor_id in domestic]
  g=[x for x in eligible if x.actor_id in global_ids]
  d.sort(key=lambda x:(-(x.financial_capacity_estimate or 0.0),x.actor_id))
  g.sort(key=lambda x:(-(x.financial_capacity_estimate or 0.0),x.actor_id))
  d=d[:max_domestic_per_category]; g=g[:max_global_per_category]
  # Cross-border fallback preserves opportunity access for all 80 economies.
  # Capacity only bounds neighborhood size; it does not prove affordability/capability.
  others=[x for x in eligible if x.actor_id not in domestic and x.actor_id not in global_ids]
  others.sort(key=lambda x:(-(x.financial_capacity_estimate or 0.0),x.actor_id))
  for x in d:selected.add(x.actor_id);ds.add(x.actor_id)
  for x in g:selected.add(x.actor_id);gs.add(x.actor_id)
  for x in others[:max_cross_border_per_category]:selected.add(x.actor_id);cs.add(x.actor_id)
 return OpportunityMatchV03(trigger.context_id,trigger.iso3,trigger.sector,tuple(sorted(selected)),tuple(sorted(ds)),tuple(sorted(gs)),tuple(sorted(cs)))

def activate_opportunity(*,trigger,registry,jurisdiction_links,max_cross_border_per_category=3):
 m=match_opportunity(trigger=trigger,registry=registry,jurisdiction_links=jurisdiction_links,max_cross_border_per_category=max_cross_border_per_category)
 registry.mark_relevant_actor_ids(context_id=trigger.context_id,actor_ids=m.actor_ids,provenance_refs=trigger.provenance_refs)
 return m
