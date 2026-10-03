"""Adaptive actor registry/activation boundary for CIVPROP V0.3.

NON-CANON / PRE-ACTOR infrastructure. Identity and relevance are not authority.
This module schedules no annual actor heartbeat and grants no budget, capability,
access, relationship authority, or consequential action.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping, Sequence

class ActivationLevel(str, Enum):
    DORMANT_CANDIDATE="DORMANT_CANDIDATE"
    RELEVANT="RELEVANT"
    ACTIVE_LIGHT="ACTIVE_LIGHT"
    ACTIVE_TRANSACTIONAL="ACTIVE_TRANSACTIONAL"

TRIGGER_CATEGORIES={
    "ECONOMIC_OPPORTUNITY":("PROSPECTOR","INCUMBENT_INDUSTRY","OFFTAKER"),
    "PROCUREMENT_DEMAND":("OFFTAKER","SUPPLIER_PRIME","INFRASTRUCTURE"),
    "TRANSPORT_REQUIREMENT":("CARRIER",),
    "FINANCING_REQUEST":("CAPITAL",),
    "UNDERWRITING_REQUEST":("INSURER",),
    "PROJECT_BID":("SUPPLIER_PRIME","INFRASTRUCTURE","INCUMBENT_INDUSTRY"),
    "CERTIFICATION_REQUEST":("CERTIFICATION",),
    "REGISTRY_REQUEST":("REGISTRY",),
    "POLICY_EVENT":("STATE","REGISTRY"),
    "INFORMATION_EVENT":("INFORMATION","SOFT_POWER"),
    "LABOR_SETTLEMENT_EVENT":("SETTLEMENT_LABOR",),
}

@dataclass(frozen=True)
class ActorIdentityV03:
    actor_id:str
    name:str
    category:str
    candidate_status:str="NON_CANON_2026_ACTOR_CANDIDATE"
    budget_status:str="UNKNOWN"
    lifecycle_status:str="ACTIVE_OR_OPERATING"
    functional_2026:bool=True
    financial_capacity_estimate:float|None=None
    financial_capacity_low:float|None=None
    financial_capacity_high:float|None=None
    capacity_semantics:str|None=None
    estimate_status:str="UNKNOWN"
    execution_ontology:str="AUTONOMOUS_ACTOR"
    autonomous_eligible:bool=True

@dataclass(frozen=True)
class ActorActivationStateV03:
    identity:ActorIdentityV03
    level:ActivationLevel=ActivationLevel.DORMANT_CANDIDATE
    causal_context_ids:tuple[str,...]=()
    provenance_refs:tuple[str,...]=()

@dataclass(frozen=True)
class ActivationResultV03:
    trigger_type:str
    context_id:str
    actor_ids:tuple[str,...]
    reason:str

class ActorRegistryV03:
    def __init__(self, identities:Iterable[ActorIdentityV03]):
        rows=tuple(identities)
        ids=[x.actor_id for x in rows]
        if len(ids)!=len(set(ids)): raise ValueError("DUPLICATE_ACTOR_ID")
        self._states={x.actor_id:ActorActivationStateV03(x) for x in rows}

    @classmethod
    def from_candidate_seed(cls,seed:Mapping[str,object]):
        return cls(ActorIdentityV03(
            actor_id=str(a["id"]),name=str(a["name"]),category=str(a["category"]))
            for a in seed["actors"])

    @classmethod
    def from_actor_baseline(cls,baseline:Mapping[str,object],roster_audit:Mapping[str,object]|None=None):
        audit_by={} if roster_audit is None else {x["actor_id"]:x for x in roster_audit["nodes"]}
        return cls(ActorIdentityV03(
            actor_id=str(a["actor_id"]),name=str(a["name"]),category=str(a["category"]),
            candidate_status="NON_CANON_DERIVED_ESTIMATED_2026_INITIALIZATION",
            budget_status="ESTIMATED_INITIAL_CAPACITY" if a["functional_2026"] else "INACTIVE",
            lifecycle_status=str(a["lifecycle_status"]),functional_2026=bool(a["functional_2026"]),
            financial_capacity_estimate=float(a["financial_capacity_estimate"]),
            financial_capacity_low=float(a["financial_capacity_low"]),
            financial_capacity_high=float(a["financial_capacity_high"]),
            capacity_semantics=str(a["capacity_semantics"]),estimate_status=str(a["evidence_status"]),
            execution_ontology=str(audit_by.get(a["actor_id"],{}).get("ontology","AUTONOMOUS_ACTOR")),
            autonomous_eligible=bool(audit_by.get(a["actor_id"],{}).get("autonomous_eligible",True)))
            for a in baseline["actors"])

    def state(self,actor_id:str)->ActorActivationStateV03:
        return self._states[actor_id]

    def states(self)->tuple[ActorActivationStateV03,...]:
        return tuple(self._states[k] for k in sorted(self._states))

    def relevant_candidates(self,trigger_type:str,*,eligible_actor_ids:Sequence[str]|None=None)->tuple[str,...]:
        cats=TRIGGER_CATEGORIES.get(trigger_type)
        if cats is None: raise ValueError("UNKNOWN_ACTIVATION_TRIGGER")
        eligible=None if eligible_actor_ids is None else set(eligible_actor_ids)
        return tuple(k for k in sorted(self._states)
                     if self._states[k].identity.category in cats
                     and self._states[k].identity.functional_2026
                     and self._states[k].identity.autonomous_eligible
                     and (eligible is None or k in eligible))

    def mark_relevant(self,*,trigger_type:str,context_id:str,
                      eligible_actor_ids:Sequence[str]|None=None,
                      provenance_refs:Sequence[str]=())->ActivationResultV03:
        ids=self.relevant_candidates(trigger_type,eligible_actor_ids=eligible_actor_ids)
        for actor_id in ids:
            old=self._states[actor_id]
            contexts=tuple(sorted(set(old.causal_context_ids+(context_id,))))
            prov=tuple(sorted(set(old.provenance_refs+tuple(provenance_refs))))
            # Relevance is discovery only. It grants no transactional authority.
            level=old.level if old.level in (ActivationLevel.ACTIVE_LIGHT,ActivationLevel.ACTIVE_TRANSACTIONAL) else ActivationLevel.RELEVANT
            self._states[actor_id]=replace(old,level=level,causal_context_ids=contexts,provenance_refs=prov)
        return ActivationResultV03(trigger_type,context_id,ids,"CATEGORY_RELEVANCE_ONLY_NO_ACTION_AUTHORITY")

    def promote(self,actor_id:str,*,level:ActivationLevel,context_id:str,
                provenance_refs:Sequence[str])->ActorActivationStateV03:
        if level not in (ActivationLevel.ACTIVE_LIGHT,ActivationLevel.ACTIVE_TRANSACTIONAL):
            raise ValueError("PROMOTION_REQUIRES_ACTIVE_LEVEL")
        old=self._states[actor_id]
        if old.level==ActivationLevel.DORMANT_CANDIDATE:
            raise ValueError("DORMANT_ACTOR_MUST_FIRST_BE_RELEVANT")
        if not provenance_refs: raise ValueError("PROMOTION_REQUIRES_PROVENANCE")
        self._states[actor_id]=replace(old,level=level,
            causal_context_ids=tuple(sorted(set(old.causal_context_ids+(context_id,)))),
            provenance_refs=tuple(sorted(set(old.provenance_refs+tuple(provenance_refs)))))
        return self._states[actor_id]

    def demote_context(self,context_id:str)->None:
        for actor_id,old in tuple(self._states.items()):
            if context_id not in old.causal_context_ids: continue
            remaining=tuple(x for x in old.causal_context_ids if x!=context_id)
            level=ActivationLevel.RELEVANT if remaining else ActivationLevel.DORMANT_CANDIDATE
            self._states[actor_id]=replace(old,level=level,causal_context_ids=remaining)

    def may_emit_consequential_action(self,actor_id:str)->bool:
        # Activation is necessary but intentionally not sufficient. Step 8 role
        # adapters must additionally prove budget/capability/access/role authority.
        return self._states[actor_id].level==ActivationLevel.ACTIVE_TRANSACTIONAL

__all__=["ActivationLevel","ActorIdentityV03","ActorActivationStateV03",
         "ActivationResultV03","ActorRegistryV03","TRIGGER_CATEGORIES"]
