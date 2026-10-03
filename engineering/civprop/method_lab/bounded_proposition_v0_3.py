"""Bounded proposition formation + portfolio competition for CIVPROP V0.3.

NON_CANON / UNPROMOTED.  This layer may create exploratory propositions only.
It cannot authorize transactions, project capital, capability, access, facilities
or physical-state mutation.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from math import log1p
from typing import Mapping,Sequence

class PropositionDisposition(str,Enum):
    IGNORE="IGNORE"; WATCH="WATCH"; EXPLORE="EXPLORE"; DEFER="DEFER"; REJECT="REJECT"

@dataclass(frozen=True)
class GateResultV03:
    gate:str; passed:bool; reason:str

@dataclass(frozen=True)
class PropositionCandidateV03:
    proposition_id:str; actor_id:str; context_id:str; iso3:str; sector:str
    category:str; attractiveness:float; exploration_cost:float
    gates:tuple[GateResultV03,...]
    provenance_refs:tuple[str,...]

@dataclass(frozen=True)
class PropositionDecisionV03:
    proposition_id:str; actor_id:str; context_id:str
    disposition:PropositionDisposition; attractiveness:float
    reason:str; portfolio_rank:int|None
    semantics:str="EXPLORATORY_INTENT_ONLY_NO_TRANSACTION_OR_PROJECT_AUTHORITY"

# Role-specific relevance.  Values are model parameters, not empirical actor psychology.
# Every term consumes a named Earth dimension; the old generic opportunity_signal is forbidden.
ROLE_WEIGHTS={
"CARRIER":{"scale_share":.35,"investment_intensity":.20,"transport_asset_share":.30,"labor_depth":.15},
"PROSPECTOR":{"investment_intensity":.35,"scale_share":.20,"productive_asset_share":.20,"labor_depth":.25},
"SUPPLIER_PRIME":{"scale_share":.30,"investment_intensity":.20,"productive_asset_share":.30,"labor_depth":.20},
"INFRASTRUCTURE":{"scale_share":.20,"investment_intensity":.25,"transport_asset_share":.25,"productive_asset_share":.30},
"OFFTAKER":{"scale_share":.40,"investment_intensity":.15,"capital_intensity":.20,"demographic_support":.25},
"INCUMBENT_INDUSTRY":{"scale_share":.30,"investment_intensity":.25,"productive_asset_share":.30,"labor_depth":.15},
"CAPITAL":{"scale_share":.25,"investment_intensity":.40,"capital_intensity":.25,"labor_depth":.10},
"INSURER":{"scale_share":.30,"capital_intensity":.30,"investment_intensity":.20,"demographic_support":.20},
"INFORMATION":{"scale_share":.25,"investment_intensity":.25,"labor_depth":.30,"demographic_support":.20},
"SOFT_POWER":{"scale_share":.20,"labor_depth":.35,"demographic_support":.30,"investment_intensity":.15},
"CERTIFICATION":{"scale_share":.20,"investment_intensity":.20,"labor_depth":.35,"productive_asset_share":.25},
"REGISTRY":{"scale_share":.20,"investment_intensity":.15,"labor_depth":.25,"demographic_support":.40},
"SETTLEMENT_LABOR":{"labor_depth":.30,"demographic_support":.45,"scale_share":.15,"investment_intensity":.10},
}

# Cheap investigation, not project finance. Explicit best-estimate initialization parameters.
EXPLORATION_COST={
"CARRIER":250_000.0,"PROSPECTOR":100_000.0,"SUPPLIER_PRIME":150_000.0,"INFRASTRUCTURE":150_000.0,
"OFFTAKER":75_000.0,"INCUMBENT_INDUSTRY":100_000.0,"CAPITAL":50_000.0,"INSURER":50_000.0,
"INFORMATION":25_000.0,"SOFT_POWER":10_000.0,"CERTIFICATION":25_000.0,"REGISTRY":25_000.0,
"SETTLEMENT_LABOR":10_000.0,
}
# Minimum vector attractiveness to justify investigation. Deliberately low: portfolio competition
# should decide among plausible opportunities rather than a single global cutoff.
INTEREST_FLOOR=.03

def _bounded(field:str,value:float|None)->float:
    if value is None:return 0.0
    v=max(0.0,float(value))
    if field in ("capital_intensity",): return v/(1.0+v)
    if field in ("investment_intensity",): return min(1.0,v)
    if field in ("labor_depth",): return min(1.0,20.0*v)
    if field in ("scale_share",): return min(1.0,20.0*v)
    return min(1.0,v)

def attractiveness(category:str,row:Mapping[str,object])->float:
    weights=ROLE_WEIGHTS.get(category)
    if weights is None:return 0.0
    return sum(w*_bounded(k,row.get(k)) for k,w in weights.items())

def exploration_slots(scale_score:float)->int:
    # Organizational attention grows sub-linearly with actor scale.
    return max(1,min(4,1+int(log1p(max(0.0,scale_score))/1.4)))

def form_candidate(*,actor_state,trigger,row:Mapping[str,object])->PropositionCandidateV03|None:
    ident=actor_state.identity
    if ident.actor_id is None:return None
    gates=[]
    aware=trigger.context_id in actor_state.causal_context_ids
    gates.append(GateResultV03("P0_AWARENESS",aware,"MATCHED_RELEVANCE_CONTEXT" if aware else "NOT_AWARE"))
    mandate=ident.category in trigger.relevant_categories
    gates.append(GateResultV03("P1_MANDATE",mandate,"CATEGORY_ROLE_MATCH" if mandate else "OUTSIDE_ROLE"))
    score=attractiveness(ident.category,row)
    material=score>=INTEREST_FLOOR
    gates.append(GateResultV03("P2_MATERIALITY",material,f"ROLE_VECTOR_ATTRACTIVENESS={score:.9f}"))
    plausible=any(float(row.get(k) or 0)>0 for k in ("scale_share","investment_intensity","labor_depth"))
    gates.append(GateResultV03("P3_PLAUSIBILITY",plausible,"EARTH_VECTOR_NONZERO" if plausible else "NO_POSITIVE_CONTEXT"))
    cost=EXPLORATION_COST.get(ident.category,50_000.0)
    capacity=ident.financial_capacity_estimate or 0.0
    affordable=capacity>=cost
    gates.append(GateResultV03("P4_EXPLORATORY_AFFORDABILITY",affordable,
                               f"ESTIMATED_CAPACITY={capacity:.3f};EXPLORATION_COST={cost:.3f}"))
    interest=material and plausible
    gates.append(GateResultV03("P5_ROLE_INTEREST",interest,"ROLE_SCREEN_PASS" if interest else "ROLE_SCREEN_FAIL"))
    if not all(x.passed for x in gates):return None
    return PropositionCandidateV03(
      f"PROP:{ident.actor_id}:{trigger.context_id}",ident.actor_id,trigger.context_id,trigger.iso3,trigger.sector,
      ident.category,score,cost,tuple(gates),tuple(trigger.provenance_refs)+tuple(actor_state.provenance_refs))

def compete_portfolio(actor_state,candidates:Sequence[PropositionCandidateV03])->tuple[PropositionDecisionV03,...]:
    rows=sorted(candidates,key=lambda x:(-x.attractiveness,x.context_id,x.proposition_id))
    slots=exploration_slots(actor_state.identity.scale_score)
    out=[]
    for rank,c in enumerate(rows,1):
      if rank<=slots:
       out.append(PropositionDecisionV03(c.proposition_id,c.actor_id,c.context_id,PropositionDisposition.EXPLORE,
                                         c.attractiveness,"PORTFOLIO_SELECTED",rank))
      else:
       out.append(PropositionDecisionV03(c.proposition_id,c.actor_id,c.context_id,PropositionDisposition.DEFER,
                                         c.attractiveness,"PORTFOLIO_ATTENTION_CONSTRAINT",rank))
    return tuple(out)

def run_proposition_cycle(*,registry,triggers_by_id:Mapping[str,object],rows_by_context:Mapping[str,Mapping[str,object]]):
    by_actor={}
    for st in registry.states():
      if st.level.value!="RELEVANT":continue
      for cid in st.causal_context_ids:
       t=triggers_by_id.get(cid); row=rows_by_context.get(cid)
       if t is None or row is None:continue
       c=form_candidate(actor_state=st,trigger=t,row=row)
       if c is not None:by_actor.setdefault(st.identity.actor_id,[]).append(c)
    decisions=[]
    for aid in sorted(by_actor):
      decisions.extend(compete_portfolio(registry.state(aid),by_actor[aid]))
    return tuple(decisions)
